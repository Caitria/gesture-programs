#!/usr/bin/env python3
"""
Air Desktop -- move virtual cards around the screen with your hands.

A webcam watches BOTH hands (MediaPipe Hand Landmarker, Google AI Edge
Tasks API, same tracker as the hand-controlled LED project). Floating
cards live on top of the camera picture. Your control is the PINCH:
thumb tip touching index tip.

    Pinch a card and move your hand      -> the card follows (grab/drag)
    Let go                               -> the card stays exactly there
    Pinch the SAME card with BOTH hands
    and spread your hands apart           -> the card grows
    Bring your hands together             -> the card shrinks

Keys in the camera window:
    Q   quit
    R   reset the cards to their starting places
    F   toggle full screen

Run it:
    python3 air_desktop.py --camera 1
    (use the camera number that showed YOU in the LED project;
     0 is often a virtual camera from another app)

Optional, if your Uno is plugged in from the LED project: add
    --port /dev/cu.usbmodem1401
and the finger count of your first hand keeps driving the five LEDs
while you move cards with the other.

Stage flags:
    --track-only   Stage A: just hands + pinch rings, no cards yet.

The camera feed is processed on this computer only. Nothing is uploaded.
"""

import argparse
import math
import sys
import time
import urllib.request
from pathlib import Path

import cv2
import numpy as np

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)


def get_model() -> Path:
    """Find the hand model: next to this script, else reuse the one the
    LED project already downloaded, else download it once."""
    here = Path(__file__).with_name("hand_landmarker.task")
    if here.exists():
        return here
    led_copy = Path.home() / "hand-controlled-led" / "code" / "hand_landmarker.task"
    if led_copy.exists():
        return led_copy
    print(f"Downloading the hand model once ({MODEL_URL}) ...")
    urllib.request.urlretrieve(MODEL_URL, here)
    return here


def dist2d(ax, ay, bx, by) -> float:
    return math.hypot(ax - bx, ay - by)


# The skeleton lines between the 21 landmarks (MediaPipe numbering).
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17),
]

PINCH_ON = 0.38   # thumb-index distance (scaled by hand size): pinch starts
PINCH_OFF = 0.55  # ... and ends only above this (a gap = no flicker)


class Card:
    """One floating panel. Position is its CENTRE, in screen pixels."""

    def __init__(self, title, cx, cy, w, h, colour, lines):
        self.title = title
        self.cx, self.cy = float(cx), float(cy)
        self.base_w, self.base_h = float(w), float(h)
        self.scale = 1.0
        self.colour = colour          # BGR border/glow colour
        self.lines = lines            # fake body text lines
        self.vx = self.vy = 0.0       # glide velocity after a toss
        self.grabbed_by = None        # hand id (0/1) or "both"

    @property
    def w(self):
        return self.base_w * self.scale

    @property
    def h(self):
        return self.base_h * self.scale

    def contains(self, x, y, pad=0):
        return (abs(x - self.cx) <= self.w / 2 + pad
                and abs(y - self.cy) <= self.h / 2 + pad)

    def step_physics(self, frame_w, frame_h):
        # No gliding (Caitria's ruling, Oct 25): a card stays exactly
        # where it was put. This only keeps cards inside the frame.
        self.vx = self.vy = 0.0
        hw, hh = self.w / 2, self.h / 2
        self.cx = min(max(self.cx, hw), frame_w - hw)
        self.cy = min(max(self.cy, hh), frame_h - hh)

    def draw(self, img, active):
        x0, y0 = int(self.cx - self.w / 2), int(self.cy - self.h / 2)
        x1, y1 = int(self.cx + self.w / 2), int(self.cy + self.h / 2)
        overlay = img.copy()
        cv2.rectangle(overlay, (x0, y0), (x1, y1), (28, 30, 38), -1)
        cv2.addWeighted(overlay, 0.82, img, 0.18, 0, img)
        border = 3 if active else 1
        cv2.rectangle(img, (x0, y0), (x1, y1), self.colour, border)
        # title bar
        cv2.rectangle(img, (x0, y0), (x1, y0 + 30), self.colour, -1)
        cv2.putText(img, self.title, (x0 + 10, y0 + 21),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (10, 10, 10), 2)
        # a simple "photo" gradient block
        gx0, gy0 = x0 + 12, y0 + 42
        gx1, gy1 = x1 - 12, y0 + 42 + int((self.h - 90) * 0.55)
        if gy1 > gy0 + 8:
            grad = np.linspace(0, 1, max(2, gy1 - gy0), dtype=np.float32)
            block = np.zeros((gy1 - gy0, gx1 - gx0, 3), dtype=np.uint8)
            c = np.array(self.colour, dtype=np.float32)
            for i, t in enumerate(grad):
                block[i, :, :] = (c * (0.35 + 0.65 * t)).astype(np.uint8)
            img[gy0:gy1, gx0:gx1] = block
        # fake text lines under the block
        ty = gy1 + 22
        for line in self.lines:
            if ty > y1 - 10:
                break
            cv2.putText(img, line, (x0 + 12, ty),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (210, 215, 225), 1)
            ty += 18


def default_cards(frame_w, frame_h):
    return [
        Card("PHOTO -- the coast", int(frame_w * 0.28), int(frame_h * 0.42),
             240, 190, (255, 190, 80), ["salt air, low tide", "october light"]),
        Card("NOTES", int(frame_w * 0.55), int(frame_h * 0.55),
             210, 160, (120, 255, 170), ["pinch = grab", "two hands = stretch"]),
        Card("CHART -- fingers", int(frame_w * 0.76), int(frame_h * 0.38),
             230, 175, (255, 130, 200), ["21 landmarks", "per hand, live"]),
    ]


class HandState:
    def __init__(self):
        self.present = False
        self.pinching = False
        self.px = self.py = 0.0       # pinch point (mid thumb/index tip)
        self.vx = self.vy = 0.0       # pinch point velocity, px/frame
        self.landmarks = None

    def update(self, lm, frame_w, frame_h):
        self.present = True
        self.landmarks = lm
        thumb, index = lm[4], lm[8]
        nx = (thumb.x + index.x) / 2 * frame_w
        ny = (thumb.y + index.y) / 2 * frame_h
        self.vx = 0.65 * self.vx + 0.35 * (nx - self.px)
        self.vy = 0.65 * self.vy + 0.35 * (ny - self.py)
        self.px, self.py = nx, ny
        hand_size = dist2d(lm[0].x, lm[0].y, lm[9].x, lm[9].y) or 1e-6
        ratio = dist2d(thumb.x, thumb.y, index.x, index.y) / hand_size
        if not self.pinching and ratio < PINCH_ON:
            self.pinching = True
        elif self.pinching and ratio > PINCH_OFF:
            self.pinching = False

    def gone(self):
        self.present = False
        self.pinching = False
        self.landmarks = None
        self.vx = self.vy = 0.0


def count_fingers(lm) -> int:
    def d(a, b):
        return math.hypot(a.x - b.x, a.y - b.y)
    count = 0
    if d(lm[4], lm[17]) > d(lm[3], lm[17]):
        count += 1
    for tip, joint in [(8, 6), (12, 10), (16, 14), (20, 18)]:
        if lm[tip].y < lm[joint].y:
            count += 1
    return count


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--camera", type=int, default=1,
                    help="which camera to use (default 1). Use the number "
                         "that showed YOU in the LED project; 0 is often "
                         "a virtual camera from another app.")
    ap.add_argument("--track-only", action="store_true",
                    help="Stage A: hands and pinch rings only, no cards")
    ap.add_argument("--port",
                    help="optional: Uno serial port, so the first hand's "
                         "finger count also drives the LED project's LEDs")
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

    ser = None
    if args.port:
        import serial
        print(f"Opening {args.port} at 9600 baud for the LEDs ...")
        ser = serial.Serial(args.port, 9600, timeout=1)
        time.sleep(2)
    last_led_count = None

    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print(f"Camera {args.camera} did not open. Try --camera 1 or "
              f"--camera 2: different numbers are different cameras, and "
              f"number 0 is sometimes a virtual camera from another app.")
        sys.exit(1)
    print(f"Using camera {args.camera}. Pinch = thumb tip to index tip. "
          f"Q quits, R resets the cards, F toggles full screen.")

    win = "Air Desktop -- Q quit, R reset, F full screen"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    fullscreen = False

    hands = [HandState(), HandState()]
    cards = None
    start = time.monotonic()

    # two-hand stretch bookkeeping
    stretch = {"card": None, "d0": 1.0, "s0": 1.0}

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)  # mirror: moving right moves right
        frame_h, frame_w, _ = frame.shape
        if cards is None and not args.track_only:
            cards = default_cards(frame_w, frame_h)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        timestamp_ms = int((time.monotonic() - start) * 1000)
        result = detector.detect_for_video(mp_image, timestamp_ms)

        seen = [False, False]
        if result.hand_landmarks:
            for i, lm in enumerate(result.hand_landmarks[:2]):
                hands[i].update(lm, frame_w, frame_h)
                seen[i] = True
        for i in range(2):
            if not seen[i]:
                # hand vanished while holding a card: let go of it
                if cards:
                    for card in cards:
                        if card.grabbed_by in (i, "both"):
                            card.grabbed_by = None
                            card.vx = card.vy = 0.0
                    if stretch["card"] is not None:
                        stretch["card"] = None
                hands[i].gone()

        # --- interactions -------------------------------------------------
        if cards:
            h0, h1 = hands
            # two-hand stretch takes over a card both hands are pinching
            if h0.pinching and h1.pinching:
                target = None
                for card in reversed(cards):
                    if card.contains(h0.px, h0.py, pad=18) and \
                            card.contains(h1.px, h1.py, pad=18):
                        target = card
                        break
                if target is not None:
                    d = dist2d(h0.px, h0.py, h1.px, h1.py)
                    if stretch["card"] is not target:
                        stretch = {"card": target, "d0": max(d, 1.0),
                                   "s0": target.scale}
                        target.grabbed_by = "both"
                        cards.remove(target)
                        cards.append(target)
                    target.scale = max(0.4, min(3.0,
                                         stretch["s0"] * d / stretch["d0"]))
                    target.cx = (h0.px + h1.px) / 2
                    target.cy = (h0.py + h1.py) / 2
                else:
                    stretch["card"] = None
            else:
                stretch["card"] = None

            if stretch["card"] is None:
                for i, hand in enumerate(hands):
                    held = next((c for c in cards if c.grabbed_by == i), None)
                    if hand.pinching:
                        if held is None:
                            for card in reversed(cards):
                                if card.grabbed_by is None and \
                                        card.contains(hand.px, hand.py, pad=26):
                                    card.grabbed_by = i
                                    card.vx = card.vy = 0.0
                                    card.grab_dx = card.cx - hand.px
                                    card.grab_dy = card.cy - hand.py
                                    cards.remove(card)
                                    cards.append(card)  # bring to front
                                    held = card
                                    break
                        if held is not None:
                            # Follow a smoothed target so tracker jitter
                            # does not become card drift.
                            tx = hand.px + held.grab_dx
                            ty = hand.py + held.grab_dy
                            if dist2d(tx, ty, held.cx, held.cy) > 1.5:
                                held.cx += (tx - held.cx) * 0.55
                                held.cy += (ty - held.cy) * 0.55
                    else:
                        if held is not None:
                            held.grabbed_by = None
                            held.vx = held.vy = 0.0  # stays where put

            for card in cards:
                card.step_physics(frame_w, frame_h)

        # --- drawing ------------------------------------------------------
        frame = (frame.astype(np.float32) * 0.72).astype(np.uint8)
        if cards:
            active_ids = {id(c) for c in cards if c.grabbed_by is not None}
            for card in cards:
                card.draw(frame, id(card) in active_ids)

        for hand in hands:
            if not hand.present:
                continue
            lm = hand.landmarks
            pts = [(int(p.x * frame_w), int(p.y * frame_h)) for p in lm]
            for a, b in HAND_CONNECTIONS:
                cv2.line(frame, pts[a], pts[b], (120, 200, 255), 1)
            for (x, y) in pts:
                cv2.circle(frame, (x, y), 3, (0, 255, 170), -1)
            px, py = int(hand.px), int(hand.py)
            if hand.pinching:
                cv2.circle(frame, (px, py), 14, (0, 255, 255), -1)
                cv2.circle(frame, (px, py), 20, (0, 255, 255), 2)
            else:
                cv2.circle(frame, (px, py), 14, (0, 255, 255), 2)

        if args.track_only:
            cv2.putText(frame, "STAGE A -- pinch each hand: ring fills",
                        (12, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        (255, 255, 255), 2)
        else:
            cv2.putText(frame, "pinch a card to grab it -- two hands stretch it",
                        (12, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        (255, 255, 255), 2)

        # optional: keep the LEDs alive with hand 1's finger count
        if ser is not None and hands[0].present:
            c = count_fingers(hands[0].landmarks)
            if c != last_led_count:
                last_led_count = c
                ser.write(f"C{c}\n".encode())

        cv2.imshow(win, frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key == ord("r") and cards is not None:
            cards = default_cards(frame_w, frame_h)
            stretch["card"] = None
        if key == ord("f"):
            fullscreen = not fullscreen
            cv2.setWindowProperty(
                win, cv2.WND_PROP_FULLSCREEN,
                cv2.WINDOW_FULLSCREEN if fullscreen else cv2.WINDOW_NORMAL)

    cap.release()
    cv2.destroyAllWindows()
    detector.close()
    if ser is not None:
        ser.write(b"C0\n")
        ser.close()


if __name__ == "__main__":
    main()
