# gesture-programs

One idea, two families: a webcam finds 21 landmarks on each of my hands, and the programs answer "now what?" — some on a screen, some in the physical world. Built on a MacBook Air and an Arduino Uno, with parts I already owned.

## The screen programs — `screen-programs/`

| Program | Folder | What it does |
|---------|--------|--------------|
| **Portal** | `screen-programs/portal/` | Two hands hold a frame (thumb + pinky tips); the camera image inside it is perspective-warped and filtered live — 10 effects. |
| **Air Desktop** | `screen-programs/air-desktop/` | A desk of virtual cards: pinch to grab and drag, two-hand stretch to resize. It grew into my decision desk — question cards answered by holding them in YES / NO / DEFER zones, and notes cards I dictate into. |
| **Mac Conductor** | `screen-programs/mac-conductor/` | The same gestures driving the real Mac: fingertip cursor, element-aware clicks, live window drags, and a palm-gated command mode. |

Shared by the three: `screen-programs/README.md` (how the suite fits together), `PLAN.md` (the build record), `FEEDBACK-QUEUE.md` (the honest list of what doesn't work yet), and `GESTURE-RESEARCH.md` (what the wider gestural-control world is doing).

## The LED control projects — `led-control/`

| Project | Folder | What it does |
|---------|--------|--------------|
| **Finger LEDs** | `led-control/finger-leds/` | The camera counts my fingers; the count crosses USB to an Arduino Uno; five real LEDs on a breadboard obey. Where this repo started. |
| **Moon Flowers** | `led-control/moon-flowers/` | Two RGB LEDs in tissue diffusers on gooseneck stems, breathing through a cyan → azure → violet → magenta cycle on the Uno — and, when I raise both hands, conducted live: one hand anchors, the other steers colour and pulse like a theremin. |

## Also here

- `demo/` — `PROGRAMS.md` (the one-page map: how to start each program), the demo runbook, and a sequencer script.

The story: [I taught my laptop to watch my hands](https://caitriaoneill.com/blog/watching-my-hands) (blog post, Oct 25 2026).

## Running them

You need: Python 3.12 (MediaPipe's prebuilt wheels stop at 3.12), a webcam, and for the LED projects an Arduino Uno + the rigs in their guides. The shared Python environment lives with the finger-LED project on my machine; `demo/PROGRAMS.md` has the exact start routine for every program, including the one folder you always start from.

```sh
python3.12 -m venv .venv && source .venv/bin/activate
pip install mediapipe opencv-python pyserial pyautogui pynput sounddevice pyobjc-framework-ApplicationServices pyobjc-framework-Speech
```

The hand model (`hand_landmarker.task`, ~8 MB) is **not** in this repo — each program downloads it once from Google on first run, or drop the file beside the script:
https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task

Camera numbering: 0 is often a *virtual* camera (in my case, the Immersed app's); the real camera is usually 1 or 2. **Q** quits every program. The conductor additionally needs macOS Accessibility permission for your terminal (System Settings → Privacy & Security → Accessibility). Air Desktop's dictation uses macOS Speech recognition, on-device. Everything runs locally; camera frames never leave the machine.

## Stack & sources

Python 3.12 · MediaPipe Hand Landmarker · OpenCV · pySerial · arduino-cli · pynput (honest `LeftMouseDragged` events — see the conductor notes in `screen-programs/PLAN.md`) · macOS Accessibility and Speech frameworks via PyObjC.

Tools and ideas borrowed, with thanks: [OpenCV](https://docs.opencv.org/4.13.0/d1/dfb/intro.html) (camera capture and the Portal's perspective warping), [pynput](https://pynput.readthedocs.io/en/latest/mouse.html) (mouse events macOS accepts as real drags), and the Portal's concept, which follows @byte0880's "RETROLENS" demo on TikTok.

Ideas borrowed, with thanks: the One Euro filter (Casiez, Roussel & Vogel, CHI 2012), the Bubble Cursor (Grossman & Balakrishnan, CHI 2005), Steady Clicks (Trewin, Keates & Moffatt, ASSETS 2006). MediaPipe docs: https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker

## Status

Air Desktop is at v7.3 and in daily use as a decision desk. The Conductor works, with a fix round approved and queued (pinch-and-drag scrolling, open-palm-flick Space switching, a step-at-a-time app switcher — the Victory pose it used turned out to be one of the least ergonomic poses a hand can make, and it's being designed out). The Moon Flowers' gesture control works, with one honest caveat recorded in its README: tracking can drop a hand in low light, and when it does, the flowers improvise. The full queue is `screen-programs/FEEDBACK-QUEUE.md`.

— Caitria O'Neill · [caitriaoneill.com](https://caitriaoneill.com)
