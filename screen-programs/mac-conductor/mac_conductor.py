#!/usr/bin/env python3
"""
Mac Conductor v5 -- fingertip cursor + element-aware clicks + a gated
gesture vocabulary for window control. Windows like cards, clicks that
know what they're clicking.

v5 changes (from Caitria's field queue F1-F5, Oct 25 2026):
- Rock hand (app switcher) works standalone, no gate needed, holds
  Cmd and re-taps Tab every ~0.9 s to cycle; poses are "sticky" for
  0.25 s so a flickered frame can't drop it mid-switch.
- Toggle commands (Mission Control, Spaces) fire ONCE per arming and
  exit command mode on firing, so the cursor is live to select.
- Fullscreen logic reads the window's actual AXFullScreen state at
  arming; exit is judged against the widest spread seen while armed.
- Minimize from fullscreen un-fullscreens first, then minimizes.
- Swipes are measured from pose start (not a rolling window).
- Window-command failures print to the Terminal instead of vanishing.

POINTING (as v3):
    Index finger                        -> cursor (One Euro filtered)
    Quick pinch (< 0.3 s, still)        -> click, position-locked
    Pinch + hold / move                 -> drag, live, drops at hand
    BOTH hands up (not a palm)          -> PAUSED
    Hand to the screen's top-left       -> emergency stop (hold 0.6 s)
    corner
    Q                                   -> quits

ELEMENT-AWARE CLICKS (new in v4):
    At the moment a pinch starts, the program asks macOS's
    Accessibility tree what real element sits at the aim point. If
    the point is within ~14 px of a small element's frame, the click
    locks onto that element's CENTRE instead -- the Bubble Cursor
    (Grossman & Balakrishnan, CHI 2005) over the real UI map.
    Queries happen only at pinch time (never per frame), carry a
    0.15 s timeout, and quietly fall back to the raw point when an
    app exposes a poor tree. (Research: PLAN.md.)

COMMAND MODE (new in v4) -- show an OPEN PALM with your second hand
to arm it for 3 s. The cursor freezes; commands act on the window
under the cursor. Every command needs the hold shown (flickering
poses can't fire); destructive ones hold longest.

    Two hands SPREAD apart (hold)       -> fullscreen that window
    Two hands PINCH TOGETHER (hold)     -> exit fullscreen
    FIST (hold 0.6 s)                   -> close the window (presses
                                           its real close button via
                                           Accessibility, not Cmd+W)
    THUMB DOWN (hold)                   -> minimize
    THUMB UP (hold)                     -> zoom / maximize
    VICTORY + move hand up/down         -> scroll (while posed)
    VICTORY + fast swipe left / right   -> previous / next Space
    Open palm SWIPE UP (pointing hand)  -> Mission Control
    I-LOVE-YOU pose (rock hand)         -> app switcher: Cmd+Tab held
                                           while posed, release commits
    POINT (index only) + move up/down   -> volume up / down

Needs: pynput and pyobjc-framework-ApplicationServices inside the
venv; macOS Accessibility permission for Terminal. Without the
Accessibility layer the conductor still points, clicks and drags --
snapping and window commands switch themselves off with a notice.

Run it:  python3 ~/mac-conductor/mac_conductor.py --camera 1
"""

import argparse
import math
import re
import sys
import time
import urllib.request
from pathlib import Path

import cv2

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)

PINCH_ON = 0.38
PINCH_OFF = 0.55
REGION = 0.18
CLICK_HOLD_S = 0.30
CLICK_MOVE_PX = 14
PARK_PX = 3
CORNER_STOP_S = 0.6

SNAP_PAD_PX = 14        # snap if aim is within this of an element frame
SNAP_MAX_AREA = 160000  # ...and the element is at most this big (px^2)
AX_TIMEOUT_S = 0.15

GATE_SECONDS = 3.0      # command mode stays armed this long per palm
POSE_HOLDS = {"CLOSE": 0.6, "FULLSCREEN": 0.4, "UNFULLSCREEN": 0.4,
              "MINIMIZE": 0.4, "ZOOM": 0.3}
GESTURE_COOLDOWN_S = 0.8
SPREAD_ON = 1.35        # two-hand distance x baseline -> fullscreen
SPREAD_OFF = 0.65       # two-hand distance x baseline -> restore


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


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


class OneEuro:
    """Casiez, Roussel & Vogel, CHI 2012. Defaults: 1.0 / 0.007 / 1.0."""

    def __init__(self, min_cutoff=1.0, beta=0.007, d_cutoff=1.0):
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        self.x_prev = None
        self.dx_prev = 0.0
        self.t_prev = None

    @staticmethod
    def _alpha(cutoff, dt):
        tau = 1.0 / (2 * math.pi * cutoff)
        return 1.0 / (1.0 + tau / dt)

    def __call__(self, x, t):
        if self.x_prev is None:
            self.x_prev = x
            self.t_prev = t
            return x
        dt = max(t - self.t_prev, 1e-3)
        dx = (x - self.x_prev) / dt
        a_d = self._alpha(self.d_cutoff, dt)
        dx_hat = a_d * dx + (1 - a_d) * self.dx_prev
        cutoff = self.min_cutoff + self.beta * abs(dx_hat)
        a = self._alpha(cutoff, dt)
        x_hat = a * x + (1 - a) * self.x_prev
        self.x_prev = x_hat
        self.dx_prev = dx_hat
        self.t_prev = t
        return x_hat


# ------------------------------------------------------------- poses
def _extended(lm, tip, pip):
    return dist((lm[tip].x, lm[tip].y), (lm[0].x, lm[0].y)) > \
        1.15 * dist((lm[pip].x, lm[pip].y), (lm[0].x, lm[0].y))


def classify_pose(lm):
    """One of OPEN_PALM, FIST, THUMB_UP, THUMB_DOWN, VICTORY,
    ILOVEYOU, POINT, OTHER -- from landmarks, geometry only."""
    idx = _extended(lm, 8, 6)
    mid = _extended(lm, 12, 10)
    rng = _extended(lm, 16, 14)
    pky = _extended(lm, 20, 18)
    thumb_out = dist((lm[4].x, lm[4].y), (lm[17].x, lm[17].y)) > \
        0.95 * dist((lm[2].x, lm[2].y), (lm[17].x, lm[17].y))
    fingers = (idx, mid, rng, pky)
    if all(fingers) and thumb_out:
        return "OPEN_PALM"
    if idx and pky and not mid and not rng and thumb_out:
        return "ILOVEYOU"
    if idx and mid and not rng and not pky:
        return "VICTORY"
    if idx and not mid and not rng and not pky:
        return "POINT"
    if not any(fingers):
        if thumb_out and lm[4].y < lm[2].y - 0.02:
            return "THUMB_UP"
        if thumb_out and lm[4].y > lm[2].y + 0.02:
            return "THUMB_DOWN"
        return "FIST"
    return "OTHER"


# ------------------------------------------------- Accessibility layer
class AXLayer:
    """Best-effort macOS Accessibility bridge. Every call is wrapped:
    if anything is unavailable or errors, the layer disables itself
    and the conductor keeps working without snapping/commands."""

    def __init__(self):
        self.ok = False
        try:
            import ApplicationServices as AS
            self.AS = AS
            self.sys = AS.AXUIElementCreateSystemWide()
            try:
                AS.AXUIElementSetMessagingTimeout(self.sys, AX_TIMEOUT_S)
            except Exception:
                pass
            self.ok = True
            print("Accessibility layer: ON (element snapping + window "
                  "commands available).")
        except Exception as e:
            print(f"Accessibility layer: OFF ({e}). Pointing/click/drag "
                  f"still work; snapping and window commands disabled. "
                  f"Install with: pip install "
                  f"pyobjc-framework-ApplicationServices")

    def _attr(self, elem, name):
        try:
            err, val = self.AS.AXUIElementCopyAttributeValue(elem, name, None)
            return val if err == 0 else None
        except Exception:
            return None

    def element_at(self, x, y):
        if not self.ok:
            return None
        try:
            err, elem = self.AS.AXUIElementCopyElementAtPosition(
                self.sys, float(x), float(y), None)
            return elem if err == 0 else None
        except Exception:
            return None

    def window_of(self, elem):
        if elem is None:
            return None
        win = self._attr(elem, "AXWindow")
        if win is not None:
            return win
        if self._attr(elem, "AXRole") == "AXWindow":
            return elem
        return None

    def frontmost_window(self):
        app = self._attr(self.sys, "AXFocusedApplication")
        if app is None:
            return None
        return self._attr(app, "AXFocusedWindow")

    def window_at(self, x, y):
        win = self.window_of(self.element_at(x, y))
        return win if win is not None else self.frontmost_window()

    def _value_nums(self, v, want):
        """Pull numbers out of an AXValue: struct route first, string
        parse as a fallback. Returns a list or None."""
        try:
            from Quartz import CGPoint, CGSize, CGRect
            from ApplicationServices import AXValueGetValue
            if want == "point":
                p = CGPoint()
                if AXValueGetValue(v, 0, p):
                    return [p.x, p.y]
            elif want == "size":
                s = CGSize()
                if AXValueGetValue(v, 1, s):
                    return [s.width, s.height]
            elif want == "rect":
                r = CGRect()
                if AXValueGetValue(v, 3, r):
                    return [r.origin.x, r.origin.y, r.size.width,
                            r.size.height]
        except Exception:
            pass
        try:
            nums = re.findall(r"-?\d+\.?\d*", str(v))
            need = {"point": 2, "size": 2, "rect": 4}[want]
            if len(nums) >= need:
                return [float(n) for n in nums[:need]]
        except Exception:
            pass
        return None

    def frame_of(self, elem):
        """(x, y, w, h) of an element, or None."""
        rect = self._attr(elem, "AXFrame")
        if rect is not None:
            nums = self._value_nums(rect, "rect")
            if nums:
                return tuple(nums)
        pos = self._attr(elem, "AXPosition")
        size = self._attr(elem, "AXSize")
        if pos is not None and size is not None:
            p = self._value_nums(pos, "point")
            s = self._value_nums(size, "size")
            if p and s:
                return (p[0], p[1], s[0], s[1])
        return None

    def snap_point(self, x, y):
        """Bubble-cursor snap: if (x, y) is within SNAP_PAD of a small
        element's frame, return the element's centre; else (x, y)."""
        elem = self.element_at(x, y)
        if elem is None:
            return (x, y), False
        frame = self.frame_of(elem)
        if frame is None:
            return (x, y), False
        fx, fy, fw, fh = frame
        if fw <= 0 or fh <= 0 or fw * fh > SNAP_MAX_AREA:
            return (x, y), False
        if (fx - SNAP_PAD_PX <= x <= fx + fw + SNAP_PAD_PX
                and fy - SNAP_PAD_PX <= y <= fy + fh + SNAP_PAD_PX):
            return (fx + fw / 2, fy + fh / 2), True
        return (x, y), False

    def perform(self, elem, action):
        try:
            return self.AS.AXUIElementPerformAction(elem, action) == 0
        except Exception:
            return False

    def set_attr(self, elem, name, value):
        try:
            return self.AS.AXUIElementSetAttributeValue(elem, name, value) == 0
        except Exception:
            return False

    def button_of(self, win, name):
        return self._attr(win, name)


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--camera", type=int, default=1,
                    help="which camera to use (default 1). Use the number "
                         "that showed YOU in the LED project.")
    args = ap.parse_args()

    import pyautogui   # screen size only
    from pynput.mouse import Controller as MouseCtl, Button
    from pynput.keyboard import Controller as KbCtl, Key
    mouse = MouseCtl()
    kb = KbCtl()
    screen_w, screen_h = pyautogui.size()
    print(f"Screen is {screen_w} x {screen_h}.")

    ax = AXLayer()

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
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    print(f"Using camera {args.camera}. Q quits.")

    win = "Mac Conductor v4 -- Q quit"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)

    start = time.monotonic()
    fx, fy = OneEuro(), OneEuro()
    pinching = False
    dragging = False
    lock_pos = None
    pinch_t0 = 0.0
    corner_since = None
    fps = 0.0
    posted = None
    snapped = False

    cmd_until = 0.0          # command mode armed until this time
    cmd_seen_min = None      # two-hand distances seen during this arming
    cmd_seen_max = None
    cmd_win_fs = None        # target window's fullscreen state at arming
    pending = None           # (action_name, since_time)
    cooldown_until = 0.0
    toast = ""
    toast_until = 0.0
    switcher_held = False
    switcher_next_tab = 0.0
    scroll_acc = 0.0
    last_vol_t = 0.0
    swipe_hist = []          # recent (t, x, y) of cmd hand tip (scroll/vol)
    traj = None              # (pose, t0, x0, y0): current command gesture
    swipe_fired = False      # one toggle-swipe per arming (F2)
    scheduled = []           # (due_time, callable) delayed actions (F4)
    prev_poses = []          # pose stickiness (F1/F5)
    prev_pose_t = []

    def post(x, y):
        nonlocal posted
        mouse.position = (int(x), int(y))
        posted = (int(x), int(y))

    def release_all():
        nonlocal pinching, dragging
        if dragging:
            try:
                mouse.release(Button.left)
            except Exception:
                pass
        pinching = False
        dragging = False

    def fire(action, win_elem):
        """Run a window command. Returns True if it did something.
        Failures print to the Terminal (v5: no silent refusals)."""
        if win_elem is None:
            print(f"command {action}: no target window found.")
            return False
        ok = False
        if action == "FULLSCREEN":
            ok = ax.set_attr(win_elem, "AXFullScreen", True)
        elif action == "UNFULLSCREEN":
            ok = ax.set_attr(win_elem, "AXFullScreen", False)
        elif action == "MINIMIZE":
            # F4: a fullscreen window ignores minimize. Un-fullscreen
            # first, then minimize once it has settled (0.45 s later).
            if ax._attr(win_elem, "AXFullScreen"):
                ok = ax.set_attr(win_elem, "AXFullScreen", False)
                w = win_elem
                scheduled.append((time.monotonic() + 0.45,
                                  lambda: ax.set_attr(w, "AXMinimized", True)))
            else:
                ok = ax.set_attr(win_elem, "AXMinimized", True)
        elif action == "CLOSE":
            btn = ax.button_of(win_elem, "AXCloseButton")
            ok = btn is not None and ax.perform(btn, "AXPress")
        elif action == "ZOOM":
            btn = ax.button_of(win_elem, "AXZoomButton")
            ok = btn is not None and ax.perform(btn, "AXPress")
        if not ok:
            print(f"command {action}: the window refused or the "
                  f"Accessibility call failed.")
        return ok

    try:
        while True:
            loop_t0 = time.monotonic()
            ok, frame = cap.read()
            if not ok:
                break
            frame = cv2.flip(frame, 1)
            frame_h, frame_w, _ = frame.shape

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            timestamp_ms = int((loop_t0 - start) * 1000)
            result = detector.detect_for_video(mp_image, timestamp_ms)
            now = time.monotonic()

            hands = []
            if result.hand_landmarks:
                for lm in result.hand_landmarks[:2]:
                    hands.append({
                        "lm": lm,
                        "pose": classify_pose(lm),
                        "wrist": (lm[0].x * frame_w, lm[0].y * frame_h),
                        "tip": (lm[8].x * frame_w, lm[8].y * frame_h),
                    })
            # Pose stickiness (v5): a real pose survives 0.25 s of
            # OTHER misreads, so motion flicker can't drop a held pose
            # (this was killing the app switcher and fast swipes).
            for i, h in enumerate(hands):
                if h["pose"] != "OTHER":
                    while len(prev_poses) <= i:
                        prev_poses.append("OTHER")
                        prev_pose_t.append(0.0)
                    prev_poses[i] = h["pose"]
                    prev_pose_t[i] = now
                elif (i < len(prev_poses) and prev_poses[i] != "OTHER"
                        and now - prev_pose_t[i] < 0.25):
                    h["pose"] = prev_poses[i]
            n_hands = len(hands)
            if switcher_held and not any(h["pose"] == "ILOVEYOU" for h in hands):
                kb.release(Key.cmd)
                switcher_held = False

            # ---------------- app switcher (v5: standalone, F1)
            rock_now = any(h["pose"] == "ILOVEYOU" for h in hands)
            if rock_now and not switcher_held:
                kb.press(Key.cmd)
                kb.press(Key.tab)
                kb.release(Key.tab)
                switcher_held = True
                switcher_next_tab = now + 0.9
                toast = "APP SWITCHER (hold to cycle, open hand to choose)"
                toast_until = now + 1.2
            elif rock_now and switcher_held and now >= switcher_next_tab:
                kb.press(Key.tab)
                kb.release(Key.tab)
                switcher_next_tab = now + 0.9

            # ---------------- command mode gate
            gate_now = n_hands == 2 and any(
                h["pose"] == "OPEN_PALM" for h in hands)
            if gate_now:
                if now > cmd_until:      # fresh entry (v5 bookkeeping)
                    d0 = dist(hands[0]["wrist"], hands[1]["wrist"])
                    cmd_seen_min = cmd_seen_max = d0
                    pending = None
                    traj = None
                    swipe_fired = False
                    cpt = posted if posted else (screen_w // 2, screen_h // 2)
                    w0 = ax.window_at(*cpt) if ax.ok else None
                    cmd_win_fs = ax._attr(w0, "AXFullScreen") if w0 else None
                cmd_until = now + GATE_SECONDS
            in_cmd = now < cmd_until and n_hands >= 1

            # delayed actions (F4's minimize-after-unfullscreen)
            due = [s for s in scheduled if now >= s[0]]
            scheduled = [s for s in scheduled if now < s[0]]
            for _, fn in due:
                fn()

            if switcher_held:
                release_all()
                state = "APP SWITCHER"
            elif in_cmd and ax.ok:
                release_all()
                state = "COMMAND"
                cursor_pt = posted if posted else (screen_w // 2, screen_h // 2)
                target_win = ax.window_at(*cursor_pt)

                # two-hand spread / squeeze (v5, F3): judge against
                # the widest/narrowest distances seen during THIS
                # arming and the window's real fullscreen state --
                # not a single snapshot taken at arming.
                spread_action = None
                if n_hands == 2:
                    d_now = dist(hands[0]["wrist"], hands[1]["wrist"])
                    if cmd_seen_min is None:
                        cmd_seen_min = cmd_seen_max = d_now
                    cmd_seen_min = min(cmd_seen_min, d_now)
                    cmd_seen_max = max(cmd_seen_max, d_now)
                    if cmd_win_fs:
                        if d_now < 0.70 * cmd_seen_max:
                            spread_action = "UNFULLSCREEN"
                    else:
                        if d_now > 1.40 * cmd_seen_min:
                            spread_action = "FULLSCREEN"

                # pose from the non-gate hand first, else either hand
                cmd_pose = None
                cmd_hand = None
                for h in hands:
                    if h["pose"] != "OPEN_PALM":
                        cmd_pose, cmd_hand = h["pose"], h
                        break
                if cmd_pose is None and hands:
                    cmd_pose, cmd_hand = hands[0]["pose"], hands[0]

                desired = spread_action
                if desired is None and cmd_pose in (
                        "FIST", "THUMB_DOWN", "THUMB_UP"):
                    desired = {"FIST": "CLOSE", "THUMB_DOWN": "MINIMIZE",
                               "THUMB_UP": "ZOOM"}[cmd_pose]

                if desired is not None and now >= cooldown_until:
                    if pending is None or pending[0] != desired:
                        pending = (desired, now)
                    elif now - pending[1] >= POSE_HOLDS[desired]:
                        if fire(desired, target_win):
                            toast = desired
                            toast_until = now + 1.2
                        pending = None
                        cooldown_until = now + GESTURE_COOLDOWN_S
                        cmd_until = 0.0     # one command per arming
                elif desired is None and cmd_pose not in ("VICTORY",
                                                          "ILOVEYOU",
                                                          "POINT"):
                    pending = None

                # continuous + swipe gestures (v5: swipes measured
                # from where the pose STARTED, not a rolling window --
                # F5; toggles fire once per arming and exit command
                # mode so the cursor is live to select -- F2)
                if cmd_hand is not None:
                    if traj is None or traj[0] != cmd_pose:
                        traj = (cmd_pose, now, cmd_hand["tip"][0],
                                cmd_hand["tip"][1])
                    swipe_hist.append((now, cmd_hand["tip"][0],
                                       cmd_hand["tip"][1]))
                    swipe_hist = [s for s in swipe_hist if now - s[0] < 0.45]
                    if cmd_pose == "VICTORY":
                        # scroll by vertical wrist motion
                        if len(swipe_hist) >= 2:
                            dy = swipe_hist[-1][2] - swipe_hist[-2][2]
                            scroll_acc += dy
                            clicks = int(scroll_acc / 28)
                            if clicks:
                                mouse.scroll(0, -clicks)
                                scroll_acc -= clicks * 28
                        # sideways swipe from pose start -> switch Space
                        if not swipe_fired and now - traj[1] < 1.2:
                            dx = cmd_hand["tip"][0] - traj[2]
                            dyy = cmd_hand["tip"][1] - traj[3]
                            if abs(dx) > 0.15 * frame_w and \
                                    abs(dx) > 1.5 * abs(dyy):
                                key = Key.right if dx > 0 else Key.left
                                kb.press(Key.ctrl)
                                kb.press(key)
                                kb.release(key)
                                kb.release(Key.ctrl)
                                toast = "SPACE >" if dx > 0 else "< SPACE"
                                toast_until = now + 1.0
                                swipe_fired = True
                                cmd_until = 0.0
                    elif cmd_pose == "POINT":
                        if len(swipe_hist) >= 2 and now - last_vol_t > 0.12:
                            dy = swipe_hist[-1][2] - swipe_hist[-2][2]
                            if dy < -6:
                                kb.press(Key.media_volume_up)
                                kb.release(Key.media_volume_up)
                                last_vol_t = now
                            elif dy > 6:
                                kb.press(Key.media_volume_down)
                                kb.release(Key.media_volume_down)
                                last_vol_t = now
                    elif cmd_pose == "OPEN_PALM" and not swipe_fired \
                            and now - traj[1] < 1.2:
                        dyy = cmd_hand["tip"][1] - traj[3]
                        dx = cmd_hand["tip"][0] - traj[2]
                        if dyy < -0.15 * frame_h and abs(dyy) > 1.5 * abs(dx):
                            kb.press(Key.ctrl)
                            kb.press(Key.up)
                            kb.release(Key.up)
                            kb.release(Key.ctrl)
                            toast = "MISSION CONTROL"
                            toast_until = now + 1.0
                            swipe_fired = True
                            cmd_until = 0.0     # cursor live to select

                if pending is not None:
                    need = POSE_HOLDS[pending[0]]
                    frac = min((now - pending[1]) / need, 1.0)
                    cv2.putText(frame, f"HOLD: {pending[0]} {frac:.0%}",
                                (12, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                                (0, 255, 255), 2)
            # ---------------- normal pointing (v3 behaviour)
            elif n_hands >= 1 and n_hands < 2:
                lm = hands[0]["lm"]
                tip = (lm[8].x, lm[8].y)
                thumb = (lm[4].x, lm[4].y)
                hand_size = dist((lm[0].x, lm[0].y), (lm[9].x, lm[9].y)) or 1e-6
                gap = dist(tip, thumb) / hand_size

                was_pinching = pinching
                if not pinching and gap < PINCH_ON:
                    pinching = True
                    pinch_t0 = now
                elif pinching and gap > PINCH_OFF:
                    pinching = False

                if pinching or dragging:
                    ctl = ((tip[0] + thumb[0]) / 2, (tip[1] + thumb[1]) / 2)
                else:
                    ctl = tip
                mx = (ctl[0] - REGION) / (1 - 2 * REGION)
                my = (ctl[1] - REGION) / (1 - 2 * REGION)
                tx = min(max(mx, 0.0), 1.0) * screen_w
                ty = min(max(my, 0.0), 1.0) * screen_h
                gx = fx(tx, now)
                gy = fy(ty, now)

                if tx < 4 and ty < 4:
                    if corner_since is None:
                        corner_since = now
                    elif now - corner_since > CORNER_STOP_S:
                        print("Corner stop. Quitting.")
                        break
                else:
                    corner_since = None

                if pinching and not was_pinching:
                    lock_pos = (gx, gy)
                    snapped = False
                    if ax.ok:
                        lock_pos, snapped = ax.snap_point(gx, gy)
                    post(*lock_pos)
                elif pinching and was_pinching and not dragging:
                    if (now - pinch_t0 > CLICK_HOLD_S
                            or dist((gx, gy), lock_pos) > CLICK_MOVE_PX):
                        dragging = True
                        mouse.press(Button.left)
                elif pinching and dragging:
                    post(gx, gy)
                elif not pinching and was_pinching:
                    if dragging:
                        post(tx, ty)
                        mouse.release(Button.left)
                        dragging = False
                    else:
                        post(*lock_pos)
                        mouse.press(Button.left)
                        mouse.release(Button.left)
                    lock_pos = None
                elif not pinching:
                    vx = fx.dx_prev * 0.016
                    vy = fy.dx_prev * 0.016
                    lead = min(max(vx, -10), 10), min(max(vy, -10), 10)
                    goal = (gx + lead[0], gy + lead[1])
                    if posted is None or dist(goal, posted) > PARK_PX:
                        post(*goal)

                state = ("DRAG" if dragging else
                         "CLICK?" if pinching else "MOVE")
                if snapped and pinching:
                    state += " (snapped)"
                txp, typ = hands[0]["tip"]
                colour = (0, 0, 255) if pinching else (0, 255, 0)
                cv2.circle(frame, (int(txp), int(typ)), 12, colour, 2)
                cv2.drawMarker(frame, (int(txp), int(typ)), colour,
                               cv2.MARKER_CROSS, 22, 2)
            else:
                if pinching or dragging:
                    release_all()
                state = "PAUSED (both hands)" if n_hands == 2 else "NO HAND"

            cv2.putText(frame, f"{state}   {fps:.0f} fps", (12, 34),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            if now < toast_until:
                cv2.putText(frame, toast, (12, 108),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
            poses_txt = "  ".join(h["pose"] for h in hands)
            cv2.putText(frame, poses_txt, (12, frame_h - 38),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 255), 1)
            cv2.putText(frame, "palm (2nd hand) = commands - quick pinch = "
                               "click - pinch+hold = drag",
                        (12, frame_h - 14), cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                        (230, 230, 230), 1)
            cv2.imshow(win, frame)
            spent = time.monotonic() - loop_t0
            if spent > 0:
                inst = 1.0 / max(spent, 1e-6)
                fps = inst if fps == 0 else 0.9 * fps + 0.1 * inst
            wait_ms = max(1, int((1 / 30 - spent) * 1000))
            if (cv2.waitKey(wait_ms) & 0xFF) == ord("q"):
                break
    finally:
        if switcher_held:
            try:
                kb.release(Key.cmd)
            except Exception:
                pass
        release_all()
        cap.release()
        cv2.destroyAllWindows()
        detector.close()


if __name__ == "__main__":
    main()
