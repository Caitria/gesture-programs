#!/usr/bin/env python3
"""
Hand-controlled LED -- computer side.

A webcam watches your hand. MediaPipe Hand Landmarker (the current
Google AI Edge Tasks API) finds 21 landmarks on the hand. This script
turns them into two simple commands and sends them to an Arduino Uno
over USB serial:

    C0 .. C5    how many fingers are up
    B0 .. B255  pinch brightness (thumb tip to index tip distance)

Run it three ways:
    python hand_led.py --dry-run     camera + tracking only, no Arduino
    python hand_led.py --port COM5   Windows: use your port from `arduino-cli board list`
    python hand_led.py --port /dev/cu.usbmodem101   macOS example
    python hand_led.py               tries to auto-find the Uno

If the camera window shows a placeholder picture instead of you
(for example "Please Launch Immersed App"), the program picked a
virtual camera -- a pretend camera made by another app. Your real
camera is a different number. Quit with Q and add --camera 1, then
--camera 2 if 1 is not you either:
    python hand_led.py --dry-run --camera 1

Press Q in the camera window to quit.
The camera feed is processed on this computer only. Nothing is uploaded.
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

# Landmark indices that matter here (MediaPipe numbers a hand 0-20):
# 0 wrist, 4 thumb tip, 8 index tip, 9 middle-finger base,
# tips 8/12/16/20 with the joint just below them at 6/10/14/18.
FINGER_TIPS_JOINTS = [(8, 6), (12, 10), (16, 14), (20, 18)]


def get_model() -> Path:
    if not MODEL_PATH.exists():
        print(f"Downloading the hand model once ({MODEL_URL}) ...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    return MODEL_PATH


def dist(a, b) -> float:
    return math.hypot(a.x - b.x, a.y - b.y)


def count_fingers(lm) -> int:
    """lm = the 21 landmarks of one hand, palm facing the camera,
    fingers pointing roughly up. Good enough for a bench toy;
    it will miscount a sideways hand, and that is expected in v1."""
    count = 0
    # Thumb: tip farther from the pinky base (17) than its joint (3) is.
    if dist(lm[4], lm[17]) > dist(lm[3], lm[17]):
        count += 1
    # Other fingers: tip above the joint below it (smaller y = higher).
    for tip, joint in FINGER_TIPS_JOINTS:
        if lm[tip].y < lm[joint].y:
            count += 1
    return count


def pinch_brightness(lm) -> int:
    """Map thumb-to-index distance to 0-255, scaled by hand size
    (wrist to middle-finger base) so distance from camera matters less."""
    scale = dist(lm[0], lm[9]) or 1e-6
    ratio = dist(lm[4], lm[8]) / scale  # ~0.2 pinched, ~1.4 open
    ratio = max(0.2, min(1.4, ratio))
    return int((ratio - 0.2) / 1.2 * 255)


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
    time.sleep(2)  # opening the port resets the Uno; give it time to boot
    return ser


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", help="serial port of the Uno, e.g. COM5")
    ap.add_argument("--dry-run", action="store_true",
                    help="camera and tracking only; print commands, send nothing")
    ap.add_argument("--pinch", action="store_true",
                    help="also send pinch brightness (Stage 3)")
    ap.add_argument("--camera", type=int, default=0,
                    help="which camera to use (default 0). If the window "
                         "shows a placeholder from another app (a virtual "
                         "camera), quit and try --camera 1, then 2.")
    args = ap.parse_args()

    import mediapipe as mp
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision

    options = vision.HandLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=str(get_model())),
        running_mode=vision.RunningMode.VIDEO,
        num_hands=1,
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
              "permission for your terminal / Python, that no other app "
              "is holding it, and try --camera 1 or --camera 2: different "
              "numbers are different cameras, and number 0 is sometimes "
              "a virtual camera belonging to another app.")
        sys.exit(1)
    print(f"Using camera {args.camera}. If the window shows a "
          "placeholder picture from another app instead of you, quit "
          "with Q and re-run with the next --camera number.")

    last_count = None
    last_bright_bucket = None
    last_send = 0.0
    start = time.monotonic()
    print("Show your hand to the camera, palm facing it. Q quits.")

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)  # mirror view: moving right moves right
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        timestamp_ms = int((time.monotonic() - start) * 1000)
        result = detector.detect_for_video(mp_image, timestamp_ms)

        count = 0
        if result.hand_landmarks:
            lm = result.hand_landmarks[0]
            h, w, _ = frame.shape
            for point in lm:
                cv2.circle(frame, (int(point.x * w), int(point.y * h)),
                           3, (0, 255, 0), -1)
            count = count_fingers(lm)

            if args.pinch:
                bright = pinch_brightness(lm)
                bucket = bright // 16  # only send on a real change
                if bucket != last_bright_bucket:
                    last_bright_bucket = bucket
                    send(f"B{bright}")
        cv2.putText(frame, f"fingers: {count}", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

        # Send the count when it changes, at most every 50 ms.
        now = time.monotonic()
        if count != last_count and now - last_send > 0.05:
            last_count = count
            last_send = now
            send(f"C{count}")

        cv2.imshow("Hand-controlled LED -- Q to quit", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    send("C0")
    cap.release()
    cv2.destroyAllWindows()
    detector.close()
    if ser is not None:
        ser.close()


if __name__ == "__main__":
    main()
