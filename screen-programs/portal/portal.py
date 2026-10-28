#!/usr/bin/env python3
"""
Portal mode -- a live filter window held between your two hands.

Hold up BOTH hands, palms to the camera. Four fingertips become the
corners of a floating frame:

    left hand:  thumb tip (landmark 4) and pinky tip (landmark 20)
    right hand: thumb tip (landmark 4) and pinky tip (landmark 20)

The patch of camera image inside that frame is perspective-warped,
run through the current filter, and pasted back -- so the frame tilts
and stretches as your hands move, exactly like the TikTok demo this
mode copies (@byte0880, "RETROLENS").

CHANGE THE FILTER, three ways:
    Touch-and-release: bring ANY fingertip of one hand (thumb, index
    or pinky) close to ANY fingertip of the other hand -- that click
    moves to the next filter. The frame's corner dots turn cyan as
    your fingers get close, so you can see it charging.
    Keyboard: N = next, P = previous, and the number keys JUMP
    straight to an effect: 1 NORMAL, 2 NEON, 3 THERMAL, 4 MONO,
    5 DUAL-TONE, 6 PIXELATE, 7 SKETCH, 8 INVERT, 9 BLUR, 0 GLITCH.

FILTERS: NORMAL, NEON, THERMAL, MONO, DUAL-TONE, PIXELATE, SKETCH,
INVERT, BLUR, GLITCH.

Keys: Q quit - F full screen - N/P next/previous filter.

Run it (same environment as the air desktop; the venv from the LED
project, and the camera number that shows YOU):
    python3 ~/portal/portal.py --camera 1

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

WARP_W, WARP_H = 480, 360   # the patch size filters run on
SWITCH_GAP = 0.50           # any-fingertip to any-fingertip, hand-size units
NEAR_GAP = 0.95             # "getting close" -- corner dots turn cyan
COOLDOWN_S = 0.9            # min seconds between filter switches
SWITCH_FINGERS = (4, 8, 20)  # thumb tip, index tip, pinky tip


def get_model() -> Path:
    here = Path(__file__).with_name("hand_landmarker.task")
    if here.exists():
        return here
    led_copy = Path.home() / "hand-controlled-led" / "code" / "hand_landmarker.task"
    if led_copy.exists():
        return led_copy
    air_copy = Path.home() / "air-desktop" / "code" / "hand_landmarker.task"
    if air_copy.exists():
        return air_copy
    print(f"Downloading the hand model once ({MODEL_URL}) ...")
    urllib.request.urlretrieve(MODEL_URL, here)
    return here


def d(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


# ---------------------------------------------------------------- filters
def f_normal(img):
    return img


def f_neon(img):
    edges = cv2.Canny(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 60, 160)
    out = np.zeros_like(img)
    out[edges > 0] = (255, 220, 60)
    return out


def f_thermal(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.applyColorMap(gray, cv2.COLORMAP_INFERNO)


def f_mono(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)


def f_dualtone(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    lut = np.zeros((1, 256, 3), dtype=np.uint8)
    for i in range(256):
        t = i / 255.0
        lut[0, i] = (int(30 + 200 * t * t), int(20 + 60 * t),
                     int(90 + 165 * t))
    return cv2.LUT(cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR), lut)


def f_pixelate(img):
    h, w = img.shape[:2]
    small = cv2.resize(img, (w // 16, h // 16), interpolation=cv2.INTER_LINEAR)
    return cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)


def f_sketch(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    inv = 255 - gray
    blur = cv2.GaussianBlur(inv, (21, 21), 0)
    sketch = cv2.divide(gray, 255 - blur, scale=256)
    return cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)


def f_invert(img):
    return 255 - img


def f_blur(img):
    return cv2.GaussianBlur(img, (31, 31), 0)


def f_glitch(img):
    out = img.copy()
    h, w = img.shape[:2]
    out[:, :, 0] = np.roll(img[:, :, 0], 12, axis=1)
    out[:, :, 2] = np.roll(img[:, :, 2], -12, axis=1)
    for _ in range(6):
        y = np.random.randint(0, h - 12)
        shift = np.random.randint(-28, 28)
        out[y:y + 10] = np.roll(out[y:y + 10], shift, axis=1)
    return out


FILTERS = [
    ("NORMAL", f_normal),
    ("NEON", f_neon),
    ("THERMAL", f_thermal),
    ("MONO", f_mono),
    ("DUAL-TONE", f_dualtone),
    ("PIXELATE", f_pixelate),
    ("SKETCH", f_sketch),
    ("INVERT", f_invert),
    ("BLUR", f_blur),
    ("GLITCH", f_glitch),
]


def order_quad(points):
    """Sort 4 corner points into a proper quad: take them in angle
    order around their centre so the frame never crosses itself."""
    pts = np.array(points, dtype=np.float32)
    centre = pts.mean(axis=0)
    angles = np.arctan2(pts[:, 1] - centre[1], pts[:, 0] - centre[0])
    return pts[np.argsort(angles)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--camera", type=int, default=1,
                    help="which camera to use (default 1). Use the number "
                         "that showed YOU in the LED project.")
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

    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print(f"Camera {args.camera} did not open. Try --camera 1 or "
              f"--camera 2 (0 is often a virtual camera from another app).")
        sys.exit(1)
    print(f"Using camera {args.camera}. Both hands up = portal. "
          f"Thumb to the other hand's pinky = next filter. Q quits.")

    win = "Portal -- Q quit, F full screen, N/P filters"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    fullscreen = False

    start = time.monotonic()
    filter_idx = 0
    last_switch = 0.0
    touch_was_closed = False
    smooth_quad = None
    toast = ""
    toast_until = 0.0

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)  # mirror view
        frame_h, frame_w, _ = frame.shape

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        timestamp_ms = int((time.monotonic() - start) * 1000)
        result = detector.detect_for_video(mp_image, timestamp_ms)

        hands = []
        if result.hand_landmarks:
            for lm in result.hand_landmarks[:2]:
                def px(i):
                    return (lm[i].x * frame_w, lm[i].y * frame_h)
                hand_size = d((lm[0].x, lm[0].y), (lm[9].x, lm[9].y)) or 1e-6
                hands.append({"thumb": px(4), "pinky": px(20),
                              "size": hand_size, "lm": lm,
                              "tips": {i: px(i) for i in SWITCH_FINGERS}})

        portal_on = len(hands) == 2
        switch_gap = None
        if portal_on:
            a, b = hands
            corners = [a["thumb"], a["pinky"], b["thumb"], b["pinky"]]
            quad = order_quad(corners)
            if smooth_quad is None:
                smooth_quad = quad
            else:
                smooth_quad = 0.55 * smooth_quad + 0.45 * quad

            # Filter switching (v2, loosened at Caitria's report): ANY
            # fingertip of one hand coming near ANY fingertip of the
            # other fires the switch -- v1 demanded one specific
            # thumb-to-other-pinky pairing at a tight distance and in
            # practice never engaged.
            avg_size_px = (a["size"] + b["size"]) / 2 * frame_w
            switch_gap = min(
                d(a["tips"][i], b["tips"][j])
                for i in SWITCH_FINGERS for j in SWITCH_FINGERS
            ) / avg_size_px
            touching = switch_gap < SWITCH_GAP
            now = time.monotonic()
            if touching and not touch_was_closed and now - last_switch > COOLDOWN_S:
                filter_idx = (filter_idx + 1) % len(FILTERS)
                last_switch = now
                toast = f"{filter_idx + 1}  {FILTERS[filter_idx][0]}"
                toast_until = now + 1.1
            touch_was_closed = touching

            # warp the patch out, filter it, warp it back
            src = smooth_quad.astype(np.float32)
            dst = np.array([[0, 0], [WARP_W - 1, 0],
                            [WARP_W - 1, WARP_H - 1], [0, WARP_H - 1]],
                           dtype=np.float32)
            # order_quad gives angle order (either direction); match dst by
            # aligning the topmost point first for a stable patch
            m_out = cv2.getPerspectiveTransform(src, dst)
            patch = cv2.warpPerspective(frame, m_out, (WARP_W, WARP_H))
            name, fn = FILTERS[filter_idx]
            patch = fn(patch)
            m_back = cv2.getPerspectiveTransform(dst, src)
            warped = cv2.warpPerspective(patch, m_back, (frame_w, frame_h))
            blank = np.zeros((WARP_H, WARP_W), dtype=np.uint8)
            mask = cv2.warpPerspective(
                cv2.rectangle(blank, (0, 0), (WARP_W - 1, WARP_H - 1), 255, -1),
                m_back, (frame_w, frame_h))
            frame[mask > 0] = warped[mask > 0]

            # the frame itself; corner dots turn solid cyan as a switch
            # gesture gets close, white when it is not near
            near = switch_gap is not None and switch_gap < NEAR_GAP
            dot = (0, 255, 255) if near else (255, 255, 255)
            ring = (255, 255, 255) if near else (0, 255, 255)
            poly = smooth_quad.astype(np.int32).reshape(-1, 1, 2)
            cv2.polylines(frame, [poly], True, (255, 255, 255), 2)
            for (x, y) in smooth_quad:
                cv2.circle(frame, (int(x), int(y)), 7, dot, -1)
                cv2.circle(frame, (int(x), int(y)), 10, ring, 2)
            top = smooth_quad[np.argmin(smooth_quad[:, 1])]
            cv2.putText(frame, name, (int(top[0]) - 40, int(top[1]) - 16),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        else:
            smooth_quad = None
            cv2.putText(frame, "hold up BOTH hands to open the portal",
                        (12, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        (255, 255, 255), 2)

        if time.monotonic() < toast_until:
            cv2.putText(frame, toast, (frame_w // 2 - 90, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 255), 3)
        cv2.putText(frame, "fingertips together = next effect - "
                           "keys 1-9,0 jump to one",
                    (12, frame_h - 14), cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                    (230, 230, 230), 1)

        cv2.imshow(win, frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key == ord("n"):
            filter_idx = (filter_idx + 1) % len(FILTERS)
            toast = f"{filter_idx + 1}  {FILTERS[filter_idx][0]}"
            toast_until = time.monotonic() + 1.1
        if key == ord("p"):
            filter_idx = (filter_idx - 1) % len(FILTERS)
            toast = f"{filter_idx + 1}  {FILTERS[filter_idx][0]}"
            toast_until = time.monotonic() + 1.1
        if ord("1") <= key <= ord("9") or key == ord("0"):
            picked = 9 if key == ord("0") else key - ord("1")
            if picked < len(FILTERS):
                filter_idx = picked
                toast = f"{filter_idx + 1}  {FILTERS[filter_idx][0]}"
                toast_until = time.monotonic() + 1.1
        if key == ord("f"):
            fullscreen = not fullscreen
            cv2.setWindowProperty(
                win, cv2.WND_PROP_FULLSCREEN,
                cv2.WINDOW_FULLSCREEN if fullscreen else cv2.WINDOW_NORMAL)

    cap.release()
    cv2.destroyAllWindows()
    detector.close()


if __name__ == "__main__":
    main()
