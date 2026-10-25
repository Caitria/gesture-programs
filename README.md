# gesture-programs

Four small programs, one idea: a webcam finds 21 landmarks on each of my hands, and each program answers "now what?" differently. All built in one day (October 25, 2026), on a MacBook Air, with parts I already owned.

| # | Program | What it does |
|---|---------|--------------|
| 1 | **Hand-Controlled LED** (`hand-controlled-led/`) | The camera counts my fingers; the count crosses USB to an Arduino Uno; five real LEDs on a breadboard obey. |
| 2 | **Portal** (`air-desktop/code/portal.py`) | Two hands hold a frame (thumb + pinky tips); the camera image inside it is perspective-warped and filtered live — 10 effects, switched by touching fingertips together or by number keys. |
| 3 | **Air Desktop** (`air-desktop/code/air_desktop.py`) | Virtual cards on screen: pinch to grab, drag, two-hand stretch to resize. The rehearsal space where the gestures were proven safe. |
| 4 | **Mac Conductor** (`air-desktop/code/mac_conductor.py`) | The same gestures driving the real Mac: fingertip cursor, element-aware clicks (they snap to the real UI element via the Accessibility tree), live window drags, and a palm-gated command mode for fullscreen / minimize / zoom / close. |

The story: [I taught my laptop to watch my hands](https://caitriaoneill.com) (blog post, Oct 25 2026).

## Layout

- `hand-controlled-led/` — Program 1: build plan (`PLAN.md`), the illustrated `BREADBOARD-GUIDE.md`, `START-HERE.md`, and `code/` (`hand_led.py`, the `uno_send.py` test sender, and the Uno sketch `hand_led_uno/`).
- `air-desktop/` — Programs 2–4: `PLAN.md` (build record incl. the research behind v3–v5), `GESTURES.md` (the conductor cheat-sheet), `FEEDBACK-QUEUE.md` (the honest list of what still doesn't work), and `code/`.
- `demo/` — `PROGRAMS.md` (the one-page map of everything), the demo runbook, and a sequencer script.

## Running them

You need: Python 3.12 (MediaPipe's prebuilt wheels stop at 3.12), a webcam, and for Program 1 an Arduino Uno + the breadboard rig in the guide.

```sh
python3.12 -m venv .venv && source .venv/bin/activate
pip install mediapipe opencv-python pyserial pyautogui pynput pyobjc-framework-ApplicationServices
```

The hand model (`hand_landmarker.task`, ~8 MB) is **not** in this repo — each program downloads it once from Google on first run, or drop the file beside the script:
https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task

```sh
python3 hand-controlled-led/code/hand_led.py --camera 1        # Program 1 (Uno plugged in)
python3 air-desktop/code/portal.py --camera 1                  # Program 2
python3 air-desktop/code/air_desktop.py --camera 1             # Program 3
python3 air-desktop/code/mac_conductor.py --camera 1           # Program 4
```

Camera numbering: 0 is often a *virtual* camera (in my case, the Immersed app's); the real camera is usually 1 or 2. **Q** quits every program. The conductor additionally needs macOS Accessibility permission for your terminal (System Settings → Privacy & Security → Accessibility) or its clicks won't land. Everything runs locally; camera frames never leave the machine.

## Parts (Program 1)

Arduino Uno R3 · 400-point breadboard · 5× LEDs (5 mm) · 5× 220 Ω resistors · jumper wires · USB A–B cable. The full illustrated wiring — every hole address — is in `hand-controlled-led/BREADBOARD-GUIDE.md`.

## Stack & sources

Python 3.12 · MediaPipe Hand Landmarker · OpenCV · pySerial · arduino-cli · pynput (honest `LeftMouseDragged` events — see the conductor notes in `air-desktop/PLAN.md` for why that matters) · macOS Accessibility framework via PyObjC.

Ideas borrowed, with thanks: the One Euro filter (Casiez, Roussel & Vogel, CHI 2012), the Bubble Cursor (Grossman & Balakrishnan, CHI 2005), Steady Clicks (Trewin, Keates & Moffatt, ASSETS 2006). MediaPipe docs: https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker

## Status

Working, with an honest queue. Scrolling and Space-switching are unreliable, the app switcher overshoots, and the Victory pose turned out to be one of the least ergonomic static poses a hand can make (the ergonomics literature is extensive; my ring finger concurs). The full list is `air-desktop/FEEDBACK-QUEUE.md`, items F1–F8.

— Caitria O'Neill · [caitriaoneill.com](https://caitriaoneill.com)
