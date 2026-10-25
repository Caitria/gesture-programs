# The Programs — one map

Everything from the October 25 build day, untangled. **Four programs, two folders, one shared toolbox.** Ask Maude to "pull up the programs map" any time and this card comes back.

## The shared toolbox (not a program — the thing all four stand on)
Lives inside the LED project, which is why it gets mentioned everywhere:
- **The environment** — `~/hand-controlled-led/code/.venv` (Python 3.12 + the libraries). Every program runs inside it. Activate with the two lines:
  ```
  cd ~/hand-controlled-led/code
  source .venv/bin/activate
  ```
  Prompt shows `(.venv)` = toolbox open. A new Terminal or tab starts with it closed.
- **The hand model** — one downloaded file (`hand_landmarker.task`) that all four programs share.

## The four programs

### 1 · Hand-Controlled LED — the physical one
- **What:** your hand, counted by the camera, lights real LEDs on the breadboard via the Arduino Uno.
- **Lives:** its own folder — `~/hand-controlled-led/` (plan, breadboard guide, code, the Uno sketch). The toolbox lives here too.
- **Launch:** `python3 ~/hand-controlled-led/code/hand_led.py --camera 1`
- **Needs:** Uno plugged in USB. **Quit:** Q.

### 2 · Portal — the effect frame
- **What:** both hands make a frame; the image inside it is filtered live (10 effects).
- **Lives:** `~/air-desktop/code/portal.py`
- **Launch:** `python3 ~/air-desktop/code/portal.py --camera 1`
- **Switch effects:** fingertips of both hands together, or keys 1–9, 0. **Quit:** Q.

### 3 · Air Desktop — the cards
- **What:** virtual cards on screen that you pinch-grab, drag, and two-hand stretch. The rehearsal space where the gestures were proven.
- **Lives:** `~/air-desktop/code/air_desktop.py`
- **Launch:** `python3 ~/air-desktop/code/air_desktop.py --camera 1`
- **Quit:** Q.

### 4 · Mac Conductor — the real desktop
- **What:** the same gestures, driving your actual Mac — cursor, clicks (with element snapping), window drags, and the palm-gated window commands.
- **Lives:** `~/air-desktop/code/mac_conductor.py`
- **Launch:** `python3 ~/air-desktop/code/mac_conductor.py --camera 1`
- **Reference:** `~/air-desktop/GESTURES.md` (every gesture + hold time). **Feedback queue:** `~/air-desktop/FEEDBACK-QUEUE.md` (F1–F8). **Quit:** Q (or top-left corner hold).

## Switching — the only rule
One program at a time: the camera has a single tenant, and a running program owns its Terminal. So every switch is the same three beats:

**Q** (quit; prompt returns) → **launch line for the next** → done.

Prompt visible = nothing running. No prompt + a camera window open = that program is running (its window title says which). Control+C is the universal stop if Q doesn't answer. **↑** at the prompt walks back through launch lines you've already used — after one lap, your history is the switchboard.

## The paperwork, in its places
- `~/hand-controlled-led/PLAN.md` + `BREADBOARD-GUIDE.md` — Program 1's build record.
- `~/air-desktop/PLAN.md` — Programs 2–4 build record, including the research and v3–v5 changes.
- `~/air-desktop/GESTURES.md` — Conductor gesture cheat-sheet.
- `~/air-desktop/FEEDBACK-QUEUE.md` — the fix queue (F1–F8) for the next iteration.
- `~/demo/` — extras: this map, the demo runbook, and the auto-sequencer script (manual switching is Caitria's stated preference; the script is a spare).
