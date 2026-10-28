#!/usr/bin/env python3
"""
Air Desktop v7 -- move virtual cards around the screen with your hands.

A webcam watches BOTH hands (MediaPipe Hand Landmarker, Google AI Edge
Tasks API, same tracker as the hand-controlled LED project). Floating
cards live on top of the camera picture. Your control is the PINCH:
thumb tip touching index tip.

    Pinch a card and move your hand      -> the card follows (grab/drag)
    Let go                               -> the card stays exactly there
    Pinch the SAME card with BOTH hands
    and spread / bring hands together    -> the card grows / shrinks
    Quick pinch on a PHOTO card (a tap)  -> next photo
    Quick pinch on a NOTES card (a tap)  -> reload the notes file

New in v3 (Caitria's picks, Oct 25):
    CAPTURE -- hold both hands up so the thumb/pinky frame shows, then
               pinch BOTH hands in the air (not on a card): the framed
               piece of the camera picture becomes a new card.
    NOTES   -- the notes card shows a real text file on this computer
               (~/air-desktop-notes.txt unless --notes says otherwise).
               Edit the file; the card follows. It is created with
               starter text the first time.
    PHOTOS  -- photo cards show real pictures from a folder
               (~/Pictures/air-desk unless --photos says otherwise).
    SPAWN   -- pinch the + NEW pad (top left): a new card of the kind
               named on the pad appears in your hand; the pad rotates
               PHOTO -> NOTES -> BLANK.
    TRASH   -- drag a card onto the TRASH pad and let go: deleted.

New in v4 (Caitria's idea, Oct 25):
New in v7 (her call after the v6 field test, Oct 25):
    VOICE-TYPE -- hold a NOTES card with one hand and dictate with
    the thumbs gestures: the words are appended to the notes file
    and appear on the card, instead of going to the answers file.
    STATUS  -- the chart card is gone; in its place a STATUS card
    shows the time, fingers up, mic state, decisions done/waiting,
    and the photo count, refreshed every second.
    ORGANIZED -- the desk's files live in the project folder now
    (~/air-desktop/: notes.txt, the queue/answers pair, audio/).
    Startup migrates or falls back to the old home-folder paths, so
    the move can happen in any order.
    TRASH IS BACK, as a dwell: the throw/swipe delete did not work
    in her hands (the swipe never fired, and fast dragging lost the
    card), so throws are OUT entirely. The TRASH pad sits at the
    bottom centre again: hold ANY part of a held card on it for
    half a second and the card is deleted (U undoes). A card merely
    resting on the pad is safe -- it must be HELD there. Decision
    cards: zones and keys only (throws no longer answer), and a
    decision card held on TRASH counts as DEFER, as before.
    v7.2: the zones are ALSO judged while the card is held (0.35 s
    dwell, one hand or two) -- release-only judging lost DEFER at
    the top of the frame, where the hand exits the camera view.
    v7.3: dictation routing no longer depends on pinching a notes
    card at the exact moment the mic starts (her test dictations
    landed in the answers file instead). TAP a notes card to arm
    it as the dictation target for a minute (red dot in its title
    bar); holding one at mic start arms it too.

New in v6 (her field-test fixes, Oct 25):
    BIGGER  -- every card is larger and the text much larger (F9).
    SNAP    -- hold a two-hand frame STEADY for a second to capture;
               the both-hands double-pinch is gone (F10).
    (THROW -- added in v6, removed in v7: it never fired for her.)
    ANSWERS -- the decision zones moved off the bottom edge (F13):
               drop the decision card in a lit side/top zone.
    PHOTOS  -- the photos folder is re-scanned every couple of
               seconds and unreadable files are skipped (F12).

New in v5 (Caitria's idea, Oct 25):
    MIC     -- thumbs UP held half a second = microphone on; thumbs
               DOWN held half a second = off. While a decision card
               is up, the note attaches to it; otherwise it is a
               general note. Recording is transcribed ON THIS MAC by
               Apple's speech recognition (audio never leaves the
               machine) and appended to the answers file as a NOTE
               line. If recognition is unavailable, the audio is kept
               in ~/air-desktop-audio and the note is marked
               untranscribed. M key toggles the mic too.

    DECISIONS -- Maude can deal you decision cards. A queue file
               (~/air-desktop-queue.txt unless --queue says otherwise)
               holds decisions in plain text blocks; the desk shows
               ONE at a time on a big gold card. Answer by dragging
               the decision card into a lit zone (sides / top)
               (or press Y / X / D). Answers are appended to an answers
               file (~/air-desktop-answers.txt). Dragging a decision
               thrown decision card answers by its exit side.

Keys in the camera window:
    Q   quit        R   reset the cards     F   full screen
    U   undo last delete                    N   spawn a card (pad kind)
    C   capture, if the two-hand frame is showing
    Y   answer the decision card: YES     X   NO     D   DEFER
    M   microphone on/off (same as the thumbs gestures)

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
import threading
import time
import wave
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

FONT = cv2.FONT_HERSHEY_SIMPLEX


def overlap_area(a, b):
    """Intersection area (px^2) of two (x0, y0, x1, y1) rects."""
    w = min(a[2], b[2]) - max(a[0], b[0])
    hh = min(a[3], b[3]) - max(a[1], b[1])
    return max(0, w) * max(0, hh)


def blit_fit(img, src, x0, y0, x1, y1):
    """Draw src into the box (x0,y0)-(x1,y1), scaled to COVER it and
    centre-cropped, so pictures fill their card without distortion.
    The box is clipped to the image first: a card hanging off the
    frame edge must never feed numpy a mismatched slice (that was
    the v6 crash: (195,316,3) into (195,294,3))."""
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(img.shape[1], x1), min(img.shape[0], y1)
    bw, bh = x1 - x0, y1 - y0
    if bw <= 4 or bh <= 4 or src is None:
        return
    sh, sw = src.shape[:2]
    scale = max(bw / sw, bh / sh)
    nw, nh = max(bw, int(sw * scale + 0.5)), max(bh, int(sh * scale + 0.5))
    resized = cv2.resize(src, (nw, nh), interpolation=cv2.INTER_AREA)
    ox = min(max(0, (nw - bw) // 2), nw - bw)
    oy = min(max(0, (nh - bh) // 2), nh - bh)
    crop = resized[oy:oy + bh, ox:ox + bw]
    if crop.shape[:2] != (bh, bw):
        crop = cv2.resize(crop, (bw, bh), interpolation=cv2.INTER_AREA)
    img[y0:y1, x0:x1] = crop


def wrap_line(text, max_px, scale=0.5, thick=1):
    """Word-wrap one line of text to fit max_px of card width."""
    words, out, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if cv2.getTextSize(trial, FONT, scale, thick)[0][0] <= max_px or not cur:
            cur = trial
        else:
            out.append(cur)
            cur = w
    if cur:
        out.append(cur)
    return out or [""]


# ---------------------------------------------------------------- cards

class Card:
    """One floating panel. Position is its CENTRE, in screen pixels.
    kind is one of: photo, notes, snap, blank, status."""

    def __init__(self, title, cx, cy, w, h, colour, kind="blank", lines=None):
        self.title = title
        self.cx, self.cy = float(cx), float(cy)
        self.base_w, self.base_h = float(w), float(h)
        self.scale = 1.0
        self.colour = colour          # BGR border / title colour
        self.kind = kind
        self.lines = lines or []       # notes/status body lines (raw)
        self.img = None                # snap: the captured picture
        self.photo_paths = []          # photo: candidate image files
        self.photo_idx = 0
        self.photo_cache = None        # photo: decoded current picture
        self.dec_title = None          # decision: the question itself
        self.dec_body = []             # decision: grounding/ask lines
        self.grabbed_by = None         # hand id (0/1) or "both"
        self.grab_dx = self.grab_dy = 0.0
        self.grab_t0 = 0.0             # when the current grab started
        self.grab_cx = self.grab_cy = 0.0   # centre when the grab started
        self.photo_bad = set()         # photo files that failed to decode
        self.flash_until = 0.0         # notes: border flash after an update
        self.armed_until = 0.0         # notes: dictation target (red dot)

    @property
    def w(self):
        return self.base_w * self.scale

    @property
    def h(self):
        return self.base_h * self.scale

    def contains(self, x, y, pad=0):
        return (abs(x - self.cx) <= self.w / 2 + pad
                and abs(y - self.cy) <= self.h / 2 + pad)

    def clamp(self, frame_w, frame_h):
        hw, hh = self.w / 2, self.h / 2
        self.cx = min(max(self.cx, hw), frame_w - hw)
        self.cy = min(max(self.cy, hh), frame_h - hh)

    def step_physics(self, frame_w, frame_h):
        # No gliding (Caitria's ruling, Oct 25): a card stays exactly
        # where it was put. This only keeps cards inside the frame.
        self.clamp(frame_w, frame_h)

    # -- photo helpers --------------------------------------------------
    def current_photo(self):
        if not self.photo_paths:
            return None
        if self.photo_cache is not None:
            return self.photo_cache
        for _ in range(len(self.photo_paths)):
            path = self.photo_paths[self.photo_idx]
            if path in self.photo_bad:
                self.photo_idx = (self.photo_idx + 1) % len(self.photo_paths)
                continue
            img = cv2.imread(path)
            if img is None:
                self.photo_bad.add(path)
                self.photo_idx = (self.photo_idx + 1) % len(self.photo_paths)
                continue
            self.photo_cache = img
            self.title = "PHOTO -- " + Path(path).stem
            return img
        return None

    def next_photo(self):
        if len(self.photo_paths) > 1:
            self.photo_idx = (self.photo_idx + 1) % len(self.photo_paths)
            self.photo_cache = None

    # -- drawing ---------------------------------------------------------
    def draw(self, img, active):
        x0, y0 = int(self.cx - self.w / 2), int(self.cy - self.h / 2)
        x1, y1 = int(self.cx + self.w / 2), int(self.cy + self.h / 2)
        overlay = img.copy()
        cv2.rectangle(overlay, (x0, y0), (x1, y1), (28, 30, 38), -1)
        cv2.addWeighted(overlay, 0.82, img, 0.18, 0, img)
        flashing = (self.kind == "notes"
                    and time.monotonic() < self.flash_until)
        cv2.rectangle(img, (x0, y0), (x1, y1),
                      (255, 255, 255) if flashing else self.colour,
                      5 if flashing else (3 if active else 1))
        # title bar (title clipped to the bar's width); everything
        # scales with the card so bigger cards mean bigger text (F9)
        ts = self.w / 340.0
        title_scale = min(1.05, max(0.62, 0.8 * ts))
        bar_h = int(30 * title_scale / 0.55)
        cv2.rectangle(img, (x0, y0), (x1, y0 + bar_h), self.colour, -1)
        title = self.title
        while title and cv2.getTextSize(title, FONT, title_scale, 2)[0][0] > self.w - 16:
            title = title[:-1]
        cv2.putText(img, title, (x0 + 10, y0 + bar_h - 9), FONT,
                    title_scale, (10, 10, 10), 2)
        if self.kind == "notes" and time.monotonic() < self.armed_until:
            # armed as the dictation target: red dot in the title bar
            cv2.circle(img, (x1 - 18, y0 + bar_h // 2), 8, (0, 0, 255), -1)
            cv2.circle(img, (x1 - 18, y0 + bar_h // 2), 8,
                       (255, 255, 255), 2)
        bx0, by0, bx1, by1 = x0 + 12, y0 + bar_h + 10, x1 - 12, y1 - 12
        if by1 <= by0:
            return
        if self.kind == "photo":
            pic = self.current_photo()
            if pic is not None:
                blit_fit(img, pic, bx0, by0, bx1, by1)
            else:
                self._placeholder(img, bx0, by0, bx1, by1,
                                  ["NO PHOTOS YET", "",
                                   "put JPG or PNG pictures in",
                                   "~/Pictures/air-desk", "",
                                   "they appear here on their own"])
        elif self.kind == "snap":
            if self.img is not None:
                blit_fit(img, self.img, bx0, by0, bx1, by1)
        elif self.kind == "decision":
            self._decision_body(img, bx0, by0, bx1, by1)
        elif self.kind == "notes":
            self._text_body(img, bx0, by0, bx1, by1)
        elif self.kind == "status":
            self._text_body(img, bx0, by0, bx1, by1)
        else:  # blank
            self._text_body(img, bx0, by0, bx1, by1)

    def _decision_body(self, img, x0, y0, x1, y1):
        ty = y0 + 30
        for line in wrap_line(self.dec_title or "", x1 - x0 - 6,
                              scale=0.92, thick=2):
            if ty > y1 - 44:
                break
            cv2.putText(img, line, (x0 + 3, ty), FONT, 0.92,
                        (255, 240, 200), 2)
            ty += 36
        ty += 10
        for raw in self.dec_body:
            for line in wrap_line(raw, x1 - x0 - 6, scale=0.66):
                if ty > y1 - 40:
                    break
                cv2.putText(img, line, (x0 + 3, ty), FONT, 0.66,
                            (215, 220, 230), 1)
                ty += 28
        for line in wrap_line("hold in a lit zone: YES right, NO left,"
                              " DEFER top -- keys Y / X / D",
                              x1 - x0 - 6, scale=0.52):
            cv2.putText(img, line, (x0 + 3, y1 - 30), FONT, 0.52,
                        (170, 175, 190), 1)
            y1 -= 22

    def _placeholder(self, img, x0, y0, x1, y1, lines, gradient=False):
        if gradient:
            gh = max(2, (y1 - y0) // 2)
            gx1 = min(x1, img.shape[1])
            gy1 = min(y0 + gh, img.shape[0])
            grad = np.linspace(0, 1, max(2, gy1 - y0), dtype=np.float32)
            block = np.zeros((gy1 - y0, gx1 - x0, 3), dtype=np.uint8)
            c = np.array(self.colour, dtype=np.float32)
            for i, t in enumerate(grad[:gy1 - y0]):
                block[i, :, :] = (c * (0.35 + 0.65 * t)).astype(np.uint8)
            if block.size:
                img[y0:gy1, x0:gx1] = block
            y0 += gh + 6
        ty = y0 + 24
        for line in lines:
            if ty > y1 - 4:
                break
            cv2.putText(img, line, (x0 + 2, ty), FONT, 0.62, (210, 215, 225), 1)
            ty += 27

    def _text_body(self, img, x0, y0, x1, y1):
        wrapped = []
        for raw in self.lines:
            wrapped.extend(wrap_line(raw, x1 - x0 - 6, scale=0.66))
        max_lines = max(1, int(((y1 - 6) - (y0 + 24)) // 28) + 1)
        if self.kind == "notes":
            visible = wrapped[-max_lines:]
        else:
            visible = wrapped[:max_lines]
        flashing = (self.kind == "notes"
                    and time.monotonic() < self.flash_until)
        ty = y0 + 24
        for i, line in enumerate(visible):
            last = flashing and i == len(visible) - 1
            cv2.putText(img, line, (x0 + 3, ty), FONT, 0.66,
                        (140, 255, 255) if last else (215, 220, 230),
                        2 if last else 1)
            ty += 28


PHOTO_COLOUR = (255, 190, 80)
NOTES_COLOUR = (120, 255, 170)
STATUS_COLOUR = (170, 200, 255)
SNAP_COLOUR = (255, 255, 120)
BLANK_COLOUR = (200, 200, 210)


def load_photo_paths(folder: Path):
    if not folder.is_dir():
        return []
    files = []
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.JPG", "*.PNG",
                "*.webp", "*.bmp", "*.WEBP", "*.JPEG"):
        files.extend(folder.glob(ext))
    return [str(p) for p in sorted(set(files))]


def make_card(kind, cx, cy, photo_paths):
    if kind == "photo":
        card = Card("PHOTO", cx, cy, 340, 260, PHOTO_COLOUR, kind="photo")
        card.photo_paths = photo_paths
        if photo_paths:
            card.title = "PHOTO -- " + Path(photo_paths[0]).stem
        return card
    if kind == "notes":
        return Card("NOTES", cx, cy, 320, 240, NOTES_COLOUR, kind="notes")
    if kind == "status":
        return Card("STATUS", cx, cy, 320, 240, STATUS_COLOUR,
                    kind="status")
    return Card("BLANK", cx, cy, 300, 220, BLANK_COLOUR, kind="blank")


def default_cards(frame_w, frame_h, photo_paths):
    return [
        make_card("photo", int(frame_w * 0.24), int(frame_h * 0.40), photo_paths),
        make_card("notes", int(frame_w * 0.52), int(frame_h * 0.60), photo_paths),
        make_card("status", int(frame_w * 0.80), int(frame_h * 0.34), photo_paths),
    ]


# ---------------------------------------------------------------- hands

class HandState:
    def __init__(self):
        self.present = False
        self.pinching = False
        self.px = self.py = 0.0       # pinch point (mid thumb/index tip)
        self.landmarks = None
        self.pinch_started_at = 0.0   # last pinch-start time (edges)
        self.grabbed_this_pinch = False

    def update(self, lm, frame_w, frame_h):
        self.present = True
        self.landmarks = lm
        thumb, index = lm[4], lm[8]
        self.px = (thumb.x + index.x) / 2 * frame_w
        self.py = (thumb.y + index.y) / 2 * frame_h
        hand_size = dist2d(lm[0].x, lm[0].y, lm[9].x, lm[9].y) or 1e-6
        ratio = dist2d(thumb.x, thumb.y, index.x, index.y) / hand_size
        if not self.pinching and ratio < PINCH_ON:
            self.pinching = True
            self.pinch_started_at = time.monotonic()
            self.grabbed_this_pinch = False
        elif self.pinching and ratio > PINCH_OFF:
            self.pinching = False

    def gone(self):
        self.present = False
        self.pinching = False
        self.landmarks = None


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


def frame_quad(hands, frame_w, frame_h):
    """The two-hand Portal frame: both hands' thumb tips + pinky tips,
    ordered around their centroid. None unless both hands are up."""
    if not (hands[0].present and hands[1].present):
        return None
    pts = []
    for hand in hands:
        lm = hand.landmarks
        pts.append((lm[4].x * frame_w, lm[4].y * frame_h))
        pts.append((lm[20].x * frame_w, lm[20].y * frame_h))
    cx = sum(p[0] for p in pts) / 4
    cy = sum(p[1] for p in pts) / 4
    pts.sort(key=lambda p: math.atan2(p[1] - cy, p[0] - cx))
    return np.array(pts, dtype=np.float32), (cx, cy)


def warp_quad(clean, quad):
    """Perspective-warp the framed region of the clean camera frame
    into a straight picture, sized by the quad's own edges."""
    (tl, tr, br, bl) = quad[0], quad[1], quad[2], quad[3]
    w = int(max(dist2d(*tl, *tr), dist2d(*bl, *br)))
    h = int(max(dist2d(*tl, *bl), dist2d(*tr, *br)))
    if w < 60 or h < 40:
        return None
    w = min(w, 520)
    h = min(h, 400)
    dst = np.array([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]],
                   dtype=np.float32)
    m = cv2.getPerspectiveTransform(quad, dst)
    return cv2.warpPerspective(clean, m, (w, h))


# ---------------------------------------------------------------- mic

MIC_RATE = 16000


def classify_pose(lm):
    """'thumb_up', 'thumb_down', or None, from the 21 landmarks.
    Requires all four fingers folded and the thumb extended clear of
    the palm; whether the thumb tip sits above or below its own base
    joint decides up vs down. Poses with any finger extended (point,
    pinch, Victory, open hand) never match, by design."""
    def d(a, b):
        return math.hypot(lm[a].x - lm[b].x, lm[a].y - lm[b].y)
    for tip, pip in ((8, 6), (12, 10), (16, 14), (20, 18)):
        if d(tip, 0) > d(pip, 0) * 1.05:
            return None
    if d(4, 17) < d(2, 17) * 1.05:
        return None
    if lm[4].y < lm[2].y - 0.015:
        return "thumb_up"
    if lm[4].y > lm[2].y + 0.015:
        return "thumb_down"
    return None


class HoldGesture:
    """Fires exactly once when `active` has been true continuously
    for hold_secs; re-arms only after the pose is released."""

    def __init__(self, hold_secs=0.5):
        self.hold_secs = hold_secs
        self.since = None
        self.fired = False

    def update(self, active, now):
        if not active:
            self.since = None
            self.fired = False
            return False
        if self.since is None:
            self.since = now
        if not self.fired and now - self.since >= self.hold_secs:
            self.fired = True
            return True
        return False


def write_wav(path, chunks, rate=MIC_RATE):
    """chunks: list of float32 mono arrays, as delivered by the mic
    callback. Writes a 16-bit PCM WAV; returns the duration in secs."""
    if chunks:
        data = np.concatenate(chunks)
    else:
        data = np.zeros(0, dtype=np.float32)
    pcm = (np.clip(data, -1.0, 1.0) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm.tobytes())
    return len(data) / rate


class SpeechTranscriber:
    """Apple speech recognition (on-device) via PyObjC. Every failure
    lands in self.error and self.ok stays False; nothing raises."""

    def __init__(self):
        self.ok = False
        self.error = ""
        self._rec = None
        self._Speech = None
        self._Foundation = None
        try:
            import Speech
            import Foundation
            self._Speech = Speech
            self._Foundation = Foundation
        except Exception as e:
            self.error = f"speech framework missing ({e})"
            return
        Speech, Foundation = self._Speech, self._Foundation
        status_box = {}
        done = threading.Event()

        def handler(status):
            status_box["status"] = int(status)
            done.set()
        try:
            Speech.SFSpeechRecognizer.requestAuthorization_(handler)
            deadline = time.monotonic() + 12
            while not done.is_set() and time.monotonic() < deadline:
                Foundation.NSRunLoop.currentRunLoop().runUntilDate_(
                    Foundation.NSDate.dateWithTimeIntervalSinceNow_(0.1))
        except Exception as e:
            self.error = f"authorization request failed ({e})"
            return
        if status_box.get("status") != 3:   # 3 = authorized
            self.error = ("speech recognition not authorized "
                          f"(status {status_box.get('status')})")
            return
        try:
            locale = Foundation.NSLocale.localeWithLocaleIdentifier_("en-US")
            self._rec = Speech.SFSpeechRecognizer.alloc().initWithLocale_(locale)
            if self._rec is None or not self._rec.isAvailable():
                self.error = "speech recognizer unavailable"
                return
        except Exception as e:
            self.error = f"recognizer setup failed ({e})"
            return
        self.ok = True

    def transcribe(self, wav_path):
        """Blocking — call from a worker thread. Returns (text, err)."""
        Speech, Foundation = self._Speech, self._Foundation
        try:
            import objc
            pool = objc.autorelease_pool()
        except Exception:
            import contextlib
            pool = contextlib.nullcontext()
        with pool:
            try:
                url = Foundation.NSURL.fileURLWithPath_(str(wav_path))
                req = Speech.SFSpeechURLRecognitionRequest.alloc().initWithURL_(url)
                try:
                    if self._rec.supportsOnDeviceRecognition():
                        req.setRequiresOnDeviceRecognition_(True)
                except Exception:
                    pass
                req.setShouldReportPartialResults_(False)
                box = {}
                done = threading.Event()

                def handler(result, error):
                    if error is not None:
                        try:
                            box["error"] = str(error.localizedDescription())
                        except Exception:
                            box["error"] = "recognition error"
                        done.set()
                        return
                    if result is not None and result.isFinal():
                        box["text"] = str(
                            result.bestTranscription().formattedString())
                        done.set()
                task = self._rec.recognitionTaskWithRequest_resultHandler_(
                    req, handler)
                deadline = time.monotonic() + 45
                while not done.is_set() and time.monotonic() < deadline:
                    Foundation.NSRunLoop.currentRunLoop().runUntilDate_(
                        Foundation.NSDate.dateWithTimeIntervalSinceNow_(0.1))
                if not done.is_set():
                    try:
                        task.cancel()
                    except Exception:
                        pass
                    return None, "transcription timed out"
                if "error" in box:
                    return None, box["error"]
                return box.get("text", ""), None
            except Exception as e:
                return None, f"transcription failed ({e})"


# ---------------------------------------------------------------- notes

STARTER_NOTES = (
    "Air Desktop notes.\n"
    "This card reads a real file:\n"
    "    ~/air-desktop/notes.txt\n"
    "Edit that file and this card\n"
    "updates on its own.\n"
    "A quick pinch on the card\n"
    "also reloads it.\n"
)


def read_notes(path: Path):
    try:
        text = path.read_text(errors="replace")
        return text.splitlines(), path.stat().st_mtime
    except OSError:
        return ["(notes file unreadable)"], 0.0


DECISION_COLOUR = (110, 215, 255)


def parse_queue(text):
    """Queue file -> [(title, [body lines]), ...]. Blocks are split by
    a line containing only --- ; lines starting with # are comments;
    the first line of a block is the decision's name."""
    blocks, cur = [], []
    for raw in text.splitlines():
        line = raw.strip()
        if line == "---":
            if cur:
                blocks.append(cur)
            cur = []
        elif line.startswith("#"):
            continue
        elif line:
            cur.append(line)
    if cur:
        blocks.append(cur)
    return [(b[0], b[1:]) for b in blocks if b]


def make_decision_card(title, body, cx, cy, number, total):
    card = Card(f"DECISION {number} OF {total}", cx, cy, 500, 360,
                DECISION_COLOUR, kind="decision")
    card.dec_title = title
    card.dec_body = body
    return card


# ---------------------------------------------------------------- main

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
    ap.add_argument("--photos", default=str(Path.home() / "Pictures" / "air-desk"),
                    help="folder of pictures for photo cards "
                         "(default ~/Pictures/air-desk)")
    ap.add_argument("--notes", default=str(Path.home() / "air-desktop" / "notes.txt"),
                    help="text file the notes cards read "
                         "(default ~/air-desktop-notes.txt)")
    ap.add_argument("--queue", default=str(Path.home() / "air-desktop" / "air-desktop-queue.txt"),
                    help="decision queue file Maude writes "
                         "(default ~/air-desktop-queue.txt)")
    ap.add_argument("--answers", default=str(Path.home() / "air-desktop" / "air-desktop-answers.txt"),
                    help="file your card answers are appended to "
                         "(default ~/air-desktop-answers.txt)")
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

    # photos folder + notes file: create on first run so they just work
    photos_dir = Path(args.photos).expanduser()
    photos_dir.mkdir(parents=True, exist_ok=True)
    photo_paths = load_photo_paths(photos_dir)
    notes_path = Path(args.notes).expanduser()
    notes_path.parent.mkdir(parents=True, exist_ok=True)
    if not notes_path.exists():
        legacy_notes = Path.home() / "air-desktop-notes.txt"
        if legacy_notes.exists():
            notes_path.write_bytes(legacy_notes.read_bytes())
            print(f"Migrated your notes file to {notes_path}")
        else:
            notes_path.write_text(STARTER_NOTES)
    notes_lines, notes_mtime = read_notes(notes_path)
    queue_path = Path(args.queue).expanduser()
    if not queue_path.exists() and \
            not (Path.home() / "air-desktop-queue.txt").exists():
        queue_path.parent.mkdir(parents=True, exist_ok=True)
        queue_path.write_text(
            "# Decisions Maude needs from you. One per block,\n"
            "# blocks separated by a line with only ---\n"
            "An example decision\n"
            "This queue file is plain text. Maude writes decisions\n"
            "here; the desk shows one at a time.\n"
            "Drag this card onto YES, DEFER, or NO at the bottom.\n")
    answers_path = Path(args.answers).expanduser()

    def resolve(new, legacy):
        """Project-folder reorganization (v7): prefer the new path
        when it exists (file or Drive symlink); fall back to the
        legacy home-folder path so any order of moving files works
        and the answers pipe can never silently break."""
        if new.exists() or not legacy.exists():
            return new
        print(f"Using {legacy} (new home {new} not set up yet)")
        return legacy

    queue_path = resolve(queue_path, Path.home() / "air-desktop-queue.txt")
    answers_path = resolve(answers_path,
                           Path.home() / "air-desktop-answers.txt")
    # microphone + speech: everything degrades to a printed reason
    audio_dir = Path.home() / "air-desktop" / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    legacy_audio = Path.home() / "air-desktop-audio"
    if legacy_audio.is_dir():
        for wav in legacy_audio.glob("*.wav"):
            dest = audio_dir / wav.name
            if not dest.exists():
                dest.write_bytes(wav.read_bytes())
    sd = None
    try:
        import sounddevice as _sd
        sd = _sd
        print("Microphone: OK")
    except Exception as e:
        print(f"Microphone: unavailable ({e}) -- run: pip install sounddevice")
    transcriber = None
    if sd is not None:
        print("Speech recognition: requesting permission "
              "(click Allow if macOS asks)...")
        transcriber = SpeechTranscriber()
        if transcriber.ok:
            print("Speech recognition: OK (on this Mac)")
        else:
            print(f"Speech recognition: unavailable ({transcriber.error}) "
                  "-- notes will be kept as audio only")
    pending, queue_mtime = [], 0.0
    try:
        pending = parse_queue(queue_path.read_text(errors="replace"))
        queue_mtime = queue_path.stat().st_mtime
    except OSError:
        pending = []

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
    print(f"Using camera {args.camera}.")
    print(f"Photos folder: {photos_dir} ({len(photo_paths)} picture(s) found)")
    print(f"Notes file:    {notes_path}")
    print("Pinch a card to move it. Pinch the + NEW pad to spawn a card.")
    print("Decision card: hold it in a lit zone, or keys Y / X / D.")
    print("Hold a two-hand frame STEADY for a second = capture.")
    print("Hold any part of a held card on TRASH (bottom) 0.5s = delete.")
    print("Hold a NOTES card + thumbs up = voice-type into the card.")
    print("Or TAP a NOTES card to arm it (red dot, 1 minute).")
    print("Q quits, R resets, F full screen.")
    print(f"Decision queue: {queue_path} ({len(pending)} waiting)")
    print(f"Answers file:   {answers_path}")
    print(f"Voice notes:    {audio_dir} (audio kept here)")
    print("Thumbs up (hold) = mic on. Thumbs down (hold) = mic off.")

    win = "Air Desktop v7 -- Q quit, R reset, F full screen"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    fullscreen = False

    hands = [HandState(), HandState()]
    cards = None
    deleted = []                     # undo stack (last deleted on top)
    start = time.monotonic()
    stretch = {"card": None, "d0": 1.0, "s0": 1.0}
    spawn_kinds = ["photo", "notes", "blank"]
    spawn_idx = 0
    snap_count = 0
    last_capture = 0.0
    snap_hold = {"t": 0.0, "anchor": None}
    trash_dwell = {"card": None, "t": 0.0}
    zone_dwell = {"card": None, "v": None, "t": 0.0}
    spent_hands = set()   # hands that answered mid-pinch: they may
                          # not grab again until they open once
    notes_armed = {"card": None, "until": 0.0}   # dictation target
    prev_now = None
    last_notes_poll = 0.0
    toast = {"text": "", "until": 0.0}
    mic = {"state": "off", "stream": None, "chunks": [], "t0": 0.0,
           "target": "General", "result": None, "to_notes": False}
    mic_up = HoldGesture(0.5)
    mic_down = HoldGesture(0.5)
    last_note = {"text": "", "until": 0.0}

    def say(text, secs=2.2):
        toast["text"] = text
        toast["until"] = time.monotonic() + secs

    session_done = set()             # decision titles answered this run
    dec_state = {"dealt": 0, "total": len(pending), "current": None}

    def decision_card():
        if cards:
            for c in cards:
                if c.kind == "decision":
                    return c
        return None

    def deal_decision(frame_w, frame_h):
        if not pending or decision_card() is not None:
            return
        title, body = pending.pop(0)
        dec_state["dealt"] += 1
        dec_state["current"] = (title, body)
        cards.append(make_decision_card(
            title, body, frame_w // 2, frame_h // 2 - 30,
            dec_state["dealt"],
            max(dec_state["total"], dec_state["dealt"])))
        say(f"Decision: {title}", 3.0)

    def record_answer(card, verdict, frame_w, frame_h):
        stamp = time.strftime("%Y-%m-%d %I:%M %p")
        try:
            with open(answers_path, "a") as f:
                f.write(f"{stamp} - {verdict} - {card.dec_title}\n")
        except OSError:
            pass
        session_done.add(card.dec_title)
        dec_state["current"] = None
        if card in cards:
            cards.remove(card)
        say(f"Recorded: {verdict}", 2.6)
        deal_decision(frame_w, frame_h)

    def mic_start():
        if sd is None or mic["state"] != "off":
            return
        mic["chunks"] = []

        def cb(indata, frames, tinfo, status):
            mic["chunks"].append(indata.copy())
        try:
            stream = sd.InputStream(samplerate=MIC_RATE, channels=1,
                                    dtype="float32", callback=cb)
            stream.start()
        except Exception as e:
            print(f"Could not start the microphone: {e}")
            say("Microphone would not start -- see Terminal", 3.5)
            return
        mic["stream"] = stream
        mic["state"] = "recording"
        mic["t0"] = time.monotonic()
        mic["to_notes"] = False
        if cards:
            held_notes = next((c for c in cards if c.kind == "notes"
                               and c.grabbed_by in (0, 1)), None)
            armed_notes = None
            if notes_armed["card"] is not None and \
                    notes_armed["card"] in cards and \
                    time.monotonic() < notes_armed["until"]:
                armed_notes = notes_armed["card"]
            if held_notes is not None:
                # Holding a notes card arms it for a minute, so the
                # routing survives letting go of the card to speak.
                held_notes.armed_until = time.monotonic() + 60
                notes_armed["card"] = held_notes
                notes_armed["until"] = held_notes.armed_until
                mic["to_notes"] = True
            elif armed_notes is not None:
                mic["to_notes"] = True
        dc = decision_card()
        mic["target"] = ("Notes card" if mic["to_notes"]
                         else dc.dec_title if dc is not None else "General")
        say("Listening -- into your notes card" if mic["to_notes"]
            else "Listening -- thumbs down stops", 2.6)

    def mic_stop():
        if mic["state"] != "recording":
            return
        stream, mic["stream"] = mic["stream"], None
        try:
            stream.stop()
            stream.close()
        except Exception:
            pass
        wav_path = audio_dir / f"note-{time.strftime('%Y%m%d-%H%M%S')}.wav"
        secs = write_wav(wav_path, mic["chunks"])
        mic["chunks"] = []
        if secs < 0.4:
            mic["state"] = "off"
            say("Too short -- nothing saved")
            return
        mic["state"] = "transcribing"
        target = mic["target"]
        to_notes = mic["to_notes"]

        def work():
            if transcriber is not None and transcriber.ok:
                text, err = transcriber.transcribe(wav_path)
            else:
                text, err = None, (transcriber.error if transcriber
                                   else "no recognizer")
            mic["result"] = (text, err, wav_path, target, to_notes)
        threading.Thread(target=work, daemon=True).start()
        say("Transcribing...", 2.0)

    def spawn(kind, cx, cy):
        nonlocal spawn_idx
        card = make_card(kind, cx, cy, photo_paths)
        if kind == "photo" and not photo_paths:
            card = make_card("blank", cx, cy, photo_paths)
            say("No photos in the photos folder -- blank card instead", 3.0)
        if card.kind == "notes":
            card.lines = list(notes_lines)
        cards.append(card)
        return card

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)  # mirror: moving right moves right
        clean = frame.copy()        # undarkened copy, for captures
        frame_h, frame_w, _ = frame.shape
        if cards is None and not args.track_only:
            cards = default_cards(frame_w, frame_h, photo_paths)
            for c in cards:
                if c.kind == "notes":
                    c.lines = list(notes_lines)
            deal_decision(frame_w, frame_h)

        now = time.monotonic()
        frame_dt = min(0.05, now - prev_now) if prev_now else 1 / 30
        prev_now = now
        # notes file: follow edits, checked about once a second
        if cards and now - last_notes_poll > 1.0:
            last_notes_poll = now
            _, mtime = read_notes(notes_path)
            if mtime != notes_mtime:
                notes_lines, notes_mtime = read_notes(notes_path)
                for c in cards:
                    if c.kind == "notes":
                        c.lines = list(notes_lines)
            try:
                qm = queue_path.stat().st_mtime
            except OSError:
                qm = queue_mtime
            if qm != queue_mtime:
                queue_mtime = qm
                try:
                    fresh = parse_queue(queue_path.read_text(errors="replace"))
                except OSError:
                    fresh = []
                held = {dec_state["current"][0]} if dec_state["current"] else set()
                pending[:] = [b for b in fresh
                              if b[0] not in session_done and b[0] not in held]
                dec_state["total"] = (len(session_done) + len(pending)
                                      + (1 if dec_state["current"] else 0))
                deal_decision(frame_w, frame_h)
            for c in cards:
                if c.kind == "status":
                    counts = [count_fingers(hd.landmarks) if hd.present
                              else 0 for hd in hands]
                    waiting = len(pending) + \
                        (1 if dec_state["current"] else 0)
                    c.lines = [
                        f"time  {time.strftime('%I:%M %p')}",
                        f"fingers up: {counts[0]} + {counts[1]}",
                        f"mic: {mic['state']}",
                        f"decisions done: {len(session_done)}",
                        f"decisions waiting: {waiting}",
                        f"photos in folder: {len(photo_paths)}",
                    ]
            fresh_photos = load_photo_paths(photos_dir)
            if fresh_photos != photo_paths:
                photo_paths = fresh_photos
                print(f"Photos folder: {len(photo_paths)} picture(s) now")
                for c in cards:
                    if c.kind == "photo":
                        c.photo_paths = photo_paths
                        c.photo_idx = min(c.photo_idx,
                                          max(0, len(photo_paths) - 1))
                        c.photo_cache = None

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        timestamp_ms = int((now - start) * 1000)
        result = detector.detect_for_video(mp_image, timestamp_ms)

        seen = [False, False]
        if result.hand_landmarks:
            for i, lm in enumerate(result.hand_landmarks[:2]):
                hands[i].update(lm, frame_w, frame_h)
                seen[i] = True
        for i in range(2):
            if not seen[i]:
                if cards:
                    for card in cards:
                        if card.grabbed_by in (i, "both"):
                            card.grabbed_by = None
                    if stretch["card"] is not None:
                        stretch["card"] = None
                hands[i].gone()

        # --- microphone: gestures, results, limits --------------------
        if cards:
            up_ok = down_ok = False
            for i, hand in enumerate(hands):
                if not hand.present or hand.pinching:
                    continue
                if stretch["card"] is not None or \
                        any(c.grabbed_by in (i, "both") for c in cards):
                    continue
                pose = classify_pose(hand.landmarks)
                if pose == "thumb_up":
                    up_ok = True
                elif pose == "thumb_down":
                    down_ok = True
            if mic_up.update(up_ok, now) and mic["state"] == "off":
                mic_start()
            if mic_down.update(down_ok, now) and mic["state"] == "recording":
                mic_stop()
            if mic["state"] == "recording" and now - mic["t0"] > 120:
                mic_stop()
                say("Note stopped at 2 minutes", 3.0)
        if mic["result"] is not None:
            text, err, wav_path, target, to_notes = mic["result"]
            mic["result"] = None
            mic["state"] = "off"
            stamp = time.strftime("%Y-%m-%d %I:%M %p")
            if text and to_notes:
                # voice-typing: the words go into the notes file, and
                # every notes card reloads it within a second
                try:
                    with open(notes_path, "a") as f:
                        f.write(text.strip() + "\n")
                    said = "Added to your notes card"
                    try:
                        notes_lines, notes_mtime = read_notes(notes_path)
                        if cards:
                            for c in cards:
                                if c.kind == "notes":
                                    c.lines = list(notes_lines)
                                    c.flash_until = now + 3.0
                    except Exception:
                        pass  # the poll refreshes within a second anyway
                except OSError:
                    said = "Could not write the notes file"
                shown = text
            else:
                if text:
                    line = f"{stamp} - NOTE - {target} - {text}"
                    shown = text
                else:
                    line = (f"{stamp} - NOTE (untranscribed: {err}; "
                            f"audio: {wav_path}) - {target}")
                    shown = f"(saved as audio only: {err})"
                try:
                    with open(answers_path, "a") as f:
                        f.write(line + "\n")
                except OSError:
                    pass
                said = "Note saved to the answers file"
            last_note["text"] = shown
            last_note["until"] = now + 12
            say(said, 3.0)

        quad = frame_quad(hands, frame_w, frame_h) if cards else None

        # pads (fixed UI): spawn top-left. No trash pad in v6 --
        # cards are thrown off the sides instead (F11).
        spawn_rect = (12, 48, 222, 102)
        # TRASH pad (v7): bottom centre, dwell-to-delete
        trash_rect = (frame_w // 2 - 170, frame_h - 84,
                      frame_w // 2 + 170, frame_h - 14)
        # decision answer zones, off the bottom edge (F13): two tall
        # side zones + a top zone, judged by overlap, not centre
        yes_rect = (frame_w - 128, 92, frame_w - 8, frame_h - 16)
        no_rect = (8, 92, 128, frame_h - 16)
        defer_rect = (frame_w // 2 - 190, 8, frame_w // 2 + 190, 92)

        def in_rect(x, y, r):
            return r[0] <= x <= r[2] and r[1] <= y <= r[3]

        # --- interactions -------------------------------------------------
        if cards:
            h0, h1 = hands

            # SPAWN: a pinch that STARTS on the + pad (checked on the
            # edge, before normal grabbing, so the new card lands in
            # the hand that asked for it)
            for hand in hands:
                if hand.present and hand.pinching and \
                        now - hand.pinch_started_at < 0.05 and \
                        in_rect(hand.px, hand.py, spawn_rect):
                    kind = spawn_kinds[spawn_idx]
                    spawn_idx = (spawn_idx + 1) % len(spawn_kinds)
                    spawn(kind, hand.px + 60, hand.py + 66)

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
                        h0.grabbed_this_pinch = h1.grabbed_this_pinch = True
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
                        if held is None and i not in spent_hands:
                            for card in reversed(cards):
                                if card.grabbed_by is None and \
                                        card.contains(hand.px, hand.py, pad=26):
                                    card.grabbed_by = i
                                    card.grab_dx = card.cx - hand.px
                                    card.grab_dy = card.cy - hand.py
                                    card.grab_t0 = now
                                    card.grab_cx, card.grab_cy = card.cx, card.cy
                                    hand.grabbed_this_pinch = True
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
                        spent_hands.discard(i)
                        if held is not None:
                            held.grabbed_by = None
                            moved = dist2d(held.cx, held.cy,
                                           held.grab_cx, held.grab_cy)
                            if held.kind == "decision":
                                rect = (held.cx - held.w / 2,
                                        held.cy - held.h / 2,
                                        held.cx + held.w / 2,
                                        held.cy + held.h / 2)
                                verdict = None
                                if overlap_area(rect, yes_rect) > 1500:
                                    verdict = "YES"
                                elif overlap_area(rect, no_rect) > 1500:
                                    verdict = "NO"
                                elif overlap_area(rect, defer_rect) > 1500:
                                    verdict = "DEFER"
                                if verdict:
                                    record_answer(held, verdict,
                                                  frame_w, frame_h)
                                    continue
                            if now - held.grab_t0 < 0.35 and moved < 14:
                                # a TAP: quick pinch, card barely moved
                                if held.kind == "photo":
                                    held.next_photo()
                                    say("Next photo")
                                elif held.kind == "notes":
                                    lines, _m = read_notes(notes_path)
                                    held.lines = list(lines)
                                    if time.monotonic() < held.armed_until:
                                        held.armed_until = 0.0
                                        if notes_armed["card"] is held:
                                            notes_armed["card"] = None
                                            notes_armed["until"] = 0.0
                                        say("Notes card disarmed")
                                    else:
                                        held.armed_until = \
                                            time.monotonic() + 60
                                        notes_armed["card"] = held
                                        notes_armed["until"] = \
                                            held.armed_until
                                        say("Notes armed -- dictation "
                                            "goes here (red dot)")
                            held.clamp(frame_w, frame_h)

            # TRASH DWELL (v7): any part of a HELD card overlapping
            # the pad accumulates time; half a second deletes. A card
            # merely resting on the pad is never touched.
            held_any = next((c for c in cards
                             if c.grabbed_by in (0, 1)), None)
            if held_any is not None and overlap_area(
                    (held_any.cx - held_any.w / 2,
                     held_any.cy - held_any.h / 2,
                     held_any.cx + held_any.w / 2,
                     held_any.cy + held_any.h / 2), trash_rect) > 0:
                if trash_dwell["card"] is held_any:
                    trash_dwell["t"] += frame_dt
                else:
                    trash_dwell = {"card": held_any, "t": frame_dt}
                if trash_dwell["t"] >= 0.5:
                    _hand = held_any.grabbed_by
                    trash_dwell = {"card": None, "t": 0.0}
                    if isinstance(_hand, int):
                        hands[_hand].grabbed_this_pinch = True
                        spent_hands.add(_hand)
                    if held_any.kind == "decision":
                        record_answer(held_any, "DEFER",
                                      frame_w, frame_h)
                    else:
                        held_any.grabbed_by = None
                        cards.remove(held_any)
                        deleted.append(held_any)
                        if len(deleted) > 5:
                            deleted.pop(0)
                        say("Card deleted -- U brings it back")
            else:
                trash_dwell = {"card": None, "t": 0.0}

            # DECISION ZONES (v7.2): also judged CONTINUOUSLY while
            # a decision card is held -- one hand or two -- with a
            # short dwell. Release-only judging failed at the top
            # zone: the hand leaves the camera view there before a
            # clean release registers. Holding the card in a lit zone
            # for a beat now answers it; releasing in a zone still
            # answers instantly.
            held_dec = next((c for c in cards
                             if c.kind == "decision"
                             and c.grabbed_by is not None), None)
            if held_dec is not None:
                drect = (held_dec.cx - held_dec.w / 2,
                         held_dec.cy - held_dec.h / 2,
                         held_dec.cx + held_dec.w / 2,
                         held_dec.cy + held_dec.h / 2)
                zverdict = None
                if overlap_area(drect, yes_rect) > 1500:
                    zverdict = "YES"
                elif overlap_area(drect, no_rect) > 1500:
                    zverdict = "NO"
                elif overlap_area(drect, defer_rect) > 1500:
                    zverdict = "DEFER"
                if zverdict is None:
                    zone_dwell = {"card": None, "v": None, "t": 0.0}
                else:
                    if zone_dwell["card"] is held_dec and \
                            zone_dwell["v"] == zverdict:
                        zone_dwell["t"] += frame_dt
                    else:
                        zone_dwell = {"card": held_dec, "v": zverdict,
                                      "t": frame_dt}
                    if zone_dwell["t"] >= 0.35:
                        _gb = held_dec.grabbed_by
                        zone_dwell = {"card": None, "v": None, "t": 0.0}
                        if _gb == "both":
                            spent_hands.update((0, 1))
                        elif isinstance(_gb, int):
                            spent_hands.add(_gb)
                        record_answer(held_dec, zverdict,
                                      frame_w, frame_h)
            else:
                zone_dwell = {"card": None, "v": None, "t": 0.0}

            # CAPTURE (F10): hold the two-hand frame STEADY for about
            # a second -- no pinching, no split-second timing.
            quad_big = False
            if quad is not None:
                _xs = [p[0] for p in quad[0]]
                _ys = [p[1] for p in quad[0]]
                quad_big = (max(_xs) - min(_xs) > 220 and
                            max(_ys) - min(_ys) > 120)
            if quad is not None and quad_big and stretch["card"] is None and \
                    not any(c.grabbed_by is not None for c in cards) and \
                    now - last_capture > 1.2:
                qx, qy = quad[1]
                if snap_hold["anchor"] is None or \
                        dist2d(qx, qy, *snap_hold["anchor"]) > 34:
                    snap_hold["anchor"] = (qx, qy)
                    snap_hold["t"] = 0.0
                else:
                    snap_hold["t"] += frame_dt
                if snap_hold["t"] >= 0.8:
                    pic = warp_quad(clean, quad[0])
                    if pic is not None:
                        last_capture = now
                        snap_count += 1
                        ph, pw = pic.shape[:2]
                        card = Card(f"SNAP {snap_count}", qx, qy,
                                    pw, ph, SNAP_COLOUR, kind="snap")
                        card.img = pic
                        while card.w > frame_w * 0.5 or card.h > frame_h * 0.5:
                            card.base_w *= 0.9
                            card.base_h *= 0.9
                        cards.append(card)
                        say(f"Captured -- SNAP {snap_count}")
                    snap_hold["t"] = 0.0
                    snap_hold["anchor"] = None
            else:
                snap_hold["t"] = 0.0
                snap_hold["anchor"] = None

            for card in cards:
                card.step_physics(frame_w, frame_h)

        # --- drawing ------------------------------------------------------
        frame = (frame.astype(np.float32) * 0.72).astype(np.uint8)
        if cards:
            active_ids = {id(c) for c in cards if c.grabbed_by is not None}
            for card in cards:
                card.draw(frame, id(card) in active_ids)
            # the capture frame, when both hands are up and free
            if quad is not None and stretch["card"] is None and \
                    not any(c.grabbed_by is not None for c in cards):
                pts = quad[0].astype(int).reshape(-1, 1, 2)
                prog = min(1.0, snap_hold["t"] / 0.8)
                colour = (0, 255, 255) if prog < 1.0 else (0, 255, 120)
                cv2.polylines(frame, [pts], True, colour, 2)
                cv2.putText(frame, "HOLD STEADY to snap a photo",
                            (int(quad[1][0]) - 170, max(24, int(quad[1][1]) - 14)),
                            FONT, 0.65, colour, 2)
                bx = int(quad[1][0]) - 90
                by = int(quad[1][1]) + 16
                cv2.rectangle(frame, (bx, by), (bx + 180, by + 10),
                              (60, 60, 70), -1)
                cv2.rectangle(frame, (bx, by),
                              (bx + int(180 * prog), by + 10), colour, -1)
            # pads
            sx0, sy0, sx1, sy1 = spawn_rect
            cv2.rectangle(frame, (sx0, sy0), (sx1, sy1), (40, 44, 54), -1)
            cv2.rectangle(frame, (sx0, sy0), (sx1, sy1), (160, 220, 255), 2)
            cv2.putText(frame, f"+ NEW: {spawn_kinds[spawn_idx].upper()}",
                        (sx0 + 14, sy0 + 36), FONT, 0.7, (220, 240, 255), 2)
            # TRASH pad (v7): fills red as the dwell runs
            tx0, ty0, tx1, ty1 = trash_rect
            prog = min(1.0, trash_dwell["t"] / 0.5) \
                if trash_dwell["card"] is not None else 0.0
            cv2.rectangle(frame, (tx0, ty0), (tx1, ty1), (40, 44, 54), -1)
            if prog > 0:
                cv2.rectangle(frame, (tx0, ty0),
                              (tx0 + int((tx1 - tx0) * prog), ty1),
                              (70, 70, 200), -1)
            cv2.rectangle(frame, (tx0, ty0), (tx1, ty1),
                          (120, 120, 235) if prog > 0 else (160, 160, 175), 2)
            _ttl = "TRASH -- hold a card here"
            _ttw = cv2.getTextSize(_ttl, FONT, 0.7, 2)[0][0]
            cv2.putText(frame, _ttl, ((tx0 + tx1 - _ttw) // 2, ty0 + 45),
                        FONT, 0.7, (255, 228, 228), 2)

        if cards and decision_card() is not None:
            dc = decision_card()
            drect = (dc.cx - dc.w / 2, dc.cy - dc.h / 2,
                     dc.cx + dc.w / 2, dc.cy + dc.h / 2)
            for rect, label, base in (
                    (yes_rect, "YES", (60, 170, 80)),
                    (no_rect, "NO", (70, 70, 180)),
                    (defer_rect, "DEFER", (120, 120, 135))):
                over = dc.grabbed_by is not None and \
                    overlap_area(drect, rect) > 1500
                cv2.rectangle(frame, (rect[0], rect[1]), (rect[2], rect[3]),
                              (base[0] + 55, base[1] + 55, base[2] + 55)
                              if over else (34, 36, 44), -1)
                cv2.rectangle(frame, (rect[0], rect[1]), (rect[2], rect[3]),
                              base, 3 if over else 2)
                scale = 0.85 if rect is defer_rect else 1.0
                tw_ = cv2.getTextSize(label, FONT, scale, 2)[0][0]
                th_ = cv2.getTextSize(label, FONT, scale, 2)[0][1]
                cv2.putText(frame, label,
                            ((rect[0] + rect[2] - tw_) // 2,
                             (rect[1] + rect[3] + th_) // 2),
                            FONT, scale, (240, 242, 248), 2)

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
                        (12, 34), FONT, 0.7, (255, 255, 255), 2)
        else:
            cv2.putText(frame, "pinch a card to grab it -- hold it on TRASH to delete",
                        (12, 34), FONT, 0.7, (255, 255, 255), 2)
        if toast["text"] and now < toast["until"]:
            tw = cv2.getTextSize(toast["text"], FONT, 0.7, 2)[0][0]
            cv2.putText(frame, toast["text"],
                        ((frame_w - tw) // 2, 66),
                        FONT, 0.7, (140, 255, 190), 2)

        # microphone state, top right
        if mic["state"] == "recording":
            el = int(now - mic["t0"])
            label = f"LISTENING {el // 60}:{el % 60:02d}"
            tw2 = cv2.getTextSize(label, FONT, 0.7, 2)[0][0]
            pulse = int(127 + 127 * math.sin(now * 6))
            cv2.circle(frame, (frame_w - tw2 - 46, 27), 9,
                       (60, 60, 160 + pulse // 2), -1)
            cv2.putText(frame, label, (frame_w - tw2 - 26, 37),
                        FONT, 0.7, (130, 130, 255), 2)
            cv2.putText(frame, "thumbs down = stop",
                        (frame_w - tw2 - 26, 63), FONT, 0.5,
                        (205, 205, 215), 1)
        elif mic["state"] == "transcribing":
            label = "TRANSCRIBING..."
            tw2 = cv2.getTextSize(label, FONT, 0.7, 2)[0][0]
            cv2.putText(frame, label, (frame_w - tw2 - 12, 37),
                        FONT, 0.7, (120, 210, 255), 2)
        else:
            label = "MIC OFF" if sd is not None else "MIC N/A"
            tw2 = cv2.getTextSize(label, FONT, 0.55, 1)[0][0]
            cv2.putText(frame, label, (frame_w - tw2 - 12, 34),
                        FONT, 0.55, (150, 155, 165), 1)
        if last_note["text"] and now < last_note["until"]:
            lines = wrap_line(last_note["text"], frame_w - 280)[:4]
            cv2.rectangle(frame, (112, 76),
                          (frame_w - 112, 76 + 30 + 20 * len(lines)),
                          (24, 26, 32), -1)
            cv2.rectangle(frame, (112, 76),
                          (frame_w - 112, 76 + 30 + 20 * len(lines)),
                          (90, 160, 110), 1)
            cv2.putText(frame, "LAST NOTE (saved):",
                        (126, 98), FONT, 0.5, (140, 255, 190), 1)
            yy = 98
            for line in lines:
                yy += 20
                cv2.putText(frame, line, (126, yy), FONT, 0.5,
                            (228, 230, 238), 1)

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
            cards = default_cards(frame_w, frame_h, photo_paths)
            for c in cards:
                if c.kind == "notes":
                    c.lines = list(notes_lines)
            stretch["card"] = None
            deleted.clear()
            if dec_state["current"] is not None:
                _t, _b = dec_state["current"]
                cards.append(make_decision_card(
                    _t, _b, frame_w // 2, frame_h // 2 - 30,
                    dec_state["dealt"],
                    max(dec_state["total"], dec_state["dealt"])))
        if key in (ord("y"), ord("x"), ord("d")) and cards is not None:
            dc = decision_card()
            if dc is not None:
                record_answer(dc, {ord("y"): "YES", ord("x"): "NO",
                                   ord("d"): "DEFER"}[key],
                              frame_w, frame_h)
        if key == ord("u") and cards is not None and deleted:
            card = deleted.pop()
            card.grabbed_by = None
            card.step_physics(frame_w, frame_h)
            cards.append(card)
            say("Card restored")
        if key == ord("n") and cards is not None:
            kind = spawn_kinds[spawn_idx]
            spawn_idx = (spawn_idx + 1) % len(spawn_kinds)
            spawn(kind, frame_w // 2, frame_h // 2)
        if key == ord("c") and cards is not None and quad is not None and \
                now - last_capture > 1.2:
            pic = warp_quad(clean, quad[0])
            if pic is not None:
                last_capture = now
                snap_count += 1
                ph, pw = pic.shape[:2]
                card = Card(f"SNAP {snap_count}", quad[1][0], quad[1][1],
                            pw, ph, SNAP_COLOUR, kind="snap")
                card.img = pic
                while card.w > frame_w * 0.5 or card.h > frame_h * 0.5:
                    card.base_w *= 0.9
                    card.base_h *= 0.9
                cards.append(card)
                say(f"Captured -- SNAP {snap_count}")
        if key == ord("m"):
            if mic["state"] == "off":
                mic_start()
            elif mic["state"] == "recording":
                mic_stop()
        if key == ord("f"):
            fullscreen = not fullscreen
            cv2.setWindowProperty(
                win, cv2.WND_PROP_FULLSCREEN,
                cv2.WINDOW_FULLSCREEN if fullscreen else cv2.WINDOW_NORMAL)

    if mic["stream"] is not None:
        try:
            mic["stream"].stop()
            mic["stream"].close()
        except Exception:
            pass
    cap.release()
    cv2.destroyAllWindows()
    detector.close()
    if ser is not None:
        ser.write(b"C0\n")
        ser.close()


if __name__ == "__main__":
    main()
