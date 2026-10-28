# gesture-programs

Four small programs, one idea: a webcam finds 21 landmarks on each of my hands, and each program answers "now what?" differently. Built on a MacBook Air with parts I already owned — the first three in one day (October 25, 2026), the fourth by iterating on what my hands taught me.

| # | Program | What it does |
|---|---------|--------------|
| 1 | **Hand-Controlled LED** (`hand-controlled-led/`) | The camera counts my fingers; the count crosses USB to an Arduino Uno; five real LEDs on a breadboard obey. |
| 2 | **Portal** (`air-desktop/code/portal.py`) | Two hands hold a frame (thumb + pinky tips); the camera image inside it is perspective-warped and filtered live — 10 effects, switched by touching fingertips together or by number keys. |
| 3 | **Air Desktop** (`air-desktop/code/air_desktop.py`) | A desk of virtual cards: pinch to grab and drag, two-hand stretch to resize. It grew into my decision desk — question cards I answer by holding them in YES / NO / DEFER zones, and notes cards I dictate into. |
| 4 | **Mac Conductor** (`air-desktop/code/mac_conductor.py`) | The same gestures driving the real Mac: fingertip cursor, element-aware clicks (they snap to the real UI element via the Accessibility tree), live window drags, and a palm-gated command mode for fullscreen / minimize / zoom / close. |

The story: [I taught my laptop to watch my hands](https://caitriaoneill.com/blog/watching-my-hands) (blog post, Oct 25 2026).

## Layout

- `hand-controlled-led/` — Program 1. Start with its `README.md`; the build plan (`PLAN.md`), the illustrated `BREADBOARD-GUIDE.md`, and `START-HERE.md` are the full record. Code in `code/` (`hand_led.py`, the `uno_send.py` test sender, and the Uno sketch `hand_led_uno/`).
- `air-desktop/` — Programs 2–4, which were built as one suite. Its `README.md` explains the decision desk and the notes system. Also here: `PLAN.md` (the build record), `GESTURES.md` (the conductor cheat-sheet), `FEEDBACK-QUEUE.md` (the honest list of what doesn't work yet), and `GESTURE-RESEARCH.md` (what the wider gestural-control world is doing, and what might get added).
- `demo/` — `PROGRAMS.md` (the one-page map: how to start each program), the demo runbook, and a sequencer script.

One layout note: on my own Mac, Portal and the Conductor live in their own folders (`~/portal/`, `~/mac-conductor/`) because that's how I run them day to day. In this repo they sit together under `air-desktop/code/`, where they were built. The programs themselves don't care which folder they launch from.

## Running them

You need: Python 3.12 (MediaPipe's prebuilt wheels stop at 3.12), a webcam, and for Program 1 an Arduino Uno + the breadboard rig in the guide. Everything below assumes the shared environment is active — the map in `demo/PROGRAMS.md` has the exact per-program routine, including the one folder you always start from.

```sh
python3.12 -m venv .venv && source .venv/bin/activate
pip install mediapipe opencv-python pyserial pyautogui pynput sounddevice pyobjc-framework-ApplicationServices pyobjc-framework-Speech
```

The hand model (`hand_landmarker.task`, ~8 MB) is **not** in this repo — each program downloads it once from Google on first run, or drop the file beside the script:
https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task

```sh
python3 hand-controlled-led/code/hand_led.py --camera 1        # Program 1 (Uno plugged in; see its README for the port)
python3 air-desktop/code/portal.py --camera 1                  # Program 2
python3 air-desktop/code/air_desktop.py --camera 1             # Program 3
python3 air-desktop/code/mac_conductor.py --camera 1           # Program 4
```

Camera numbering: 0 is often a *virtual* camera (in my case, the Immersed app's); the real camera is usually 1 or 2. **Q** quits every program. The conductor additionally needs macOS Accessibility permission for your terminal (System Settings → Privacy & Security → Accessibility) or its clicks won't land. Air Desktop's dictation uses macOS Speech recognition, on-device. Everything runs locally; camera frames never leave the machine.

## Parts (Program 1)

Arduino Uno R3 · 400-point breadboard · 5× LEDs (5 mm) · 5× 220 Ω resistors · jumper wires · USB A–B cable. The full illustrated wiring — every hole address — is in `hand-controlled-led/BREADBOARD-GUIDE.md`.

## Stack & sources

Python 3.12 · MediaPipe Hand Landmarker · OpenCV · pySerial · arduino-cli · pynput (honest `LeftMouseDragged` events — see the conductor notes in `air-desktop/PLAN.md` for why that matters) · macOS Accessibility and Speech frameworks via PyObjC.

Tools and ideas borrowed, with thanks: [OpenCV](https://docs.opencv.org/4.13.0/d1/dfb/intro.html) (camera capture and the Portal's perspective warping), [pynput](https://pynput.readthedocs.io/en/latest/mouse.html) (mouse events macOS accepts as real drags), and the Portal's concept, which follows @byte0880's "RETROLENS" demo on TikTok.

Ideas borrowed, with thanks: the One Euro filter (Casiez, Roussel & Vogel, CHI 2012), the Bubble Cursor (Grossman & Balakrishnan, CHI 2005), Steady Clicks (Trewin, Keates & Moffatt, ASSETS 2006). MediaPipe docs: https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker

## Status

Air Desktop is the live one — currently v7.3 (decision zones judged by dwell as well as release, a trash pad you hold a card on to delete, a status card, and tap-to-arm dictation into notes cards). The Conductor works, with a fix round approved and queued: scrolling moves to pinch-and-drag, Spaces to an open-palm flick, and the app switcher will step one app per gesture instead of overshooting. The Victory pose turned out to be one of the least ergonomic static poses a hand can make (the ergonomics literature is extensive; my ring finger concurs) — it's being designed out. The full, honest list is `air-desktop/FEEDBACK-QUEUE.md`.

— Caitria O'Neill · [caitriaoneill.com](https://caitriaoneill.com)
