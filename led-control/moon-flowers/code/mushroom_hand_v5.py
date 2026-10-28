#!/usr/bin/env python3
"""
Mushroom hand control v3 -- TWO-HAND conducting (Oct 26).

The pinch-twist dial is retired: it was not a good movement for
Caitria's wrists. This map uses two hands and big, plain motions:

    TWO HANDS UP = conducting.
        One hand is the ANCHOR: raised, held up, roughly still.
        The other hand CONDUCTS, like a theremin / XY pad:
            move it LEFT-RIGHT ... colour spectrum
                                   (left = cyan, right = magenta)
            move it UP-DOWN ...... pulse speed
                                   (up = fast, down = slow)
        How far apart the two hands are sets pulse INTENSITY:
            spread wide = strong, hands close = gentle.
        Roles latch when the second hand enters: whichever hand is
        HIGHER at that moment is the anchor until a hand leaves.

    ONE HAND UP = PAUSE. Both mushrooms freeze exactly as they are.
        (This script sends P, with a keepalive, while one hand shows.)

    NO HANDS = RESUME. Hide both hands and the autonomous breathing
        show resumes by itself (~3.5 s later, via the Uno's timeout).

Commands to the Uno (9600 baud):  G <color 0..1000> <intensity
0..255> <period ms>  /  P = pause  /  A = autonomous.

Run:  python mushroom_hand.py --port /dev/cu.usbmodem11301 --camera 1
      (--dry-run = camera only. Camera 0 on this Mac is the Immersed
      virtual camera; use the real camera's number.)
Press Q in the camera window to quit; quitting sends A first.
Camera feed is processed on this computer only. Nothing is uploaded.
"""

import argparse
import math
import sys
import time
import urllib.request
from pathlib import Path

import cv2

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)
MODEL_PATH = Path(__file__).with_name("hand_landmarker.task")

HEARTBEAT_S = 1.0  # resend current values at least this often in
# two-hand mode. Without a heartbeat the Uno only hears from us when
# a value changes bucket, decides after 3.5 s of stillness that the
# hands are gone, and drops back to the autonomous show — which is
# why a held pose used to stop affecting the mushrooms' tone.


def get_model() -> Path:
    if not MODEL_PATH.exists():
        print(f"Downloading the hand model once ({MODEL_URL}) ...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    return MODEL_PATH


def dist_xy(ax, ay, bx, by) -> float:
    return math.hypot(ax - bx, ay - by)


def open_serial(port_arg):
    import serial
    from serial.tools import list_ports

    if port_arg:
        port = port_arg
    else:
        candidates = [p.device for p in list_ports.comports()
                      if "arduino" in (p.description or "").lower()
                      or "usbmodem" in p.device or "ttyACM" in p.device
                      or "wch" in (p.description or "").lower()]
        if not candidates:
            print("Could not auto-find an Arduino. Ports I can see:")
            for p in list_ports.comports():
                print(f"  {p.device}  {p.description}")
            print("Re-run with --port <that port>, or use --dry-run.")
            sys.exit(1)
        port = candidates[0]
    print(f"Opening {port} at 9600 baud ...")
    ser = serial.Serial(port, 9600, timeout=1)
    time.sleep(2)  # opening the port resets the Uno; flash test runs
    print("Uno is running its flash test; hand control starts after.")
    return ser


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", help="serial port of the Uno")
    ap.add_argument("--dry-run", action="store_true",
                    help="camera and tracking only; send nothing")
    ap.add_argument("--camera", type=int, default=0,
                    help="which camera (0 here is the Immersed virtual "
                         "camera; use the real camera's number)")
    args = ap.parse_args()

    import mediapipe as mp
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision

    options = vision.HandLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=str(get_model())),
        running_mode=vision.RunningMode.VIDEO,
        num_hands=2,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    detector = vision.HandLandmarker.create_from_options(options)

    ser = None if args.dry_run else open_serial(args.port)

    def send(cmd: str):
        print(cmd)
        if ser is not None:
            ser.write((cmd + "\n").encode())

    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print(f"Camera {args.camera} did not open. Check the camera "
              "permission for Terminal/Python and try another --camera.")
        sys.exit(1)

    hand_count_prev = 0
    anchor_idx = None        # which detected hand is the anchor (latched)
    smooth_color = 0.0
    smooth_intensity = 180.0
    smooth_period = 4200.0
    last_bucket = None
    last_send_time = 0.0
    last_pause_send = 0.0
    start = time.monotonic()
    print("Two hands: higher hand anchors, other hand conducts "
          "(left-right colour, up-down speed, spread intensity). "
          "One hand = pause. No hands = resume. Q quits.")

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)  # mirror view
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        timestamp_ms = int((time.monotonic() - start) * 1000)
        result = detector.detect_for_video(mp_image, timestamp_ms)
        now = time.monotonic()

        hands = result.hand_landmarks or []
        n = len(hands)
        h, w, _ = frame.shape
        for lm in hands:
            for point in lm:
                cv2.circle(frame, (int(point.x * w), int(point.y * h)),
                           3, (0, 255, 0), -1)

        status = "AUTO (no hands - resumed)"
        if n == 1:
            # One hand up = pause both. P once, then keepalive so the
            # Uno's 3.5 s timeout does not mistake this for "hidden".
            if hand_count_prev != 1 or now - last_pause_send > 0.5:
                send("P")
                last_pause_send = now
            status = "PAUSED (one hand)"
        elif n >= 2:
            # Latch roles when arriving at two hands: the HIGHER hand
            # (smaller wrist y) becomes the anchor.
            if hand_count_prev < 2 or anchor_idx is None:
                anchor_idx = 0 if hands[0][0].y < hands[1][0].y else 1
                last_bucket = None  # force an immediate send on entry
            control_idx = 1 - anchor_idx
            anchor = hands[anchor_idx][0]    # wrist of anchor hand
            ctrl = hands[control_idx][0]     # wrist of conducting hand

            # Show the spread between the wrists.
            cv2.line(frame,
                     (int(anchor.x * w), int(anchor.y * h)),
                     (int(ctrl.x * w), int(ctrl.y * h)),
                     (0, 255, 255), 2)

            # Colour: control hand left-right across the frame.
            cx = max(0.10, min(0.90, ctrl.x))
            target_color = (cx - 0.10) / 0.80 * 1000
            smooth_color += (target_color - smooth_color) * 0.35

            # Pulse speed: control hand up = fast, down = slow.
            cy = max(0.15, min(0.85, ctrl.y))
            target_period = 1500 + (cy - 0.15) / 0.70 * 6500
            smooth_period += (target_period - smooth_period) * 0.30

            # Intensity: spread between the two wrists.
            sep = dist_xy(anchor.x, anchor.y, ctrl.x, ctrl.y)
            sep = max(0.15, min(0.85, sep))
            target_int = 50 + (sep - 0.15) / 0.70 * 205
            smooth_intensity += (target_int - smooth_intensity) * 0.30

            bucket = (int(smooth_color) // 20,
                      int(smooth_intensity) // 10,
                      int(smooth_period) // 200)
            heartbeat_due = now - last_send_time > HEARTBEAT_S
            if (bucket != last_bucket and now - last_send_time > 0.10) \
                    or heartbeat_due:
                last_bucket = bucket
                last_send_time = now
                send(f"G {int(smooth_color)} {int(smooth_intensity)} "
                     f"{int(smooth_period)}")
            status = (f"TWO-HAND  colour {int(smooth_color) // 10}%  "
                      f"pulse {int(smooth_intensity) * 100 // 255}%  "
                      f"cadence {smooth_period / 1000:.1f}s")
        else:
            anchor_idx = None  # roles re-latch next time two hands enter

        hand_count_prev = n
        cv2.putText(frame, status, (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.imshow("Mushroom two-hand control -- Q to quit", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    send("A")  # leave the mushrooms on their autonomous show
    cap.release()
    cv2.destroyAllWindows()
    detector.close()
    if ser is not None:
        ser.close()


if __name__ == "__main__":
    main()
