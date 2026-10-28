# Start Each Program — the shortlist

Updated Oct 26, 2026 (after the project-folder reorganization).
All four programs are on Caitria's Mac. Ask Maude to "pull up the
programs map" and this comes back.

## The one thing to know first

You **always cd to the same folder** — the LED project's code folder.
It holds the shared environment (`.venv`) and the hand model that all
four programs borrow:

```
cd ~/hand-controlled-led/code
source .venv/bin/activate
```

You should see the prompt start with `(.venv)`. Do those two lines
first, every time, then the launch line for the program you want.
One program at a time — the camera has a single tenant. To switch:
press **Q** in the program's window (click the window first), wait
for the `%` prompt to come back, then run the next launch line.

---

## 1 · Hand-controlled LED — hand lights the real LEDs (Uno)

- Program file: `~/hand-controlled-led/code/hand_led.py`
- Needs: the Uno plugged in by USB.
- If you're not sure of the Uno's port, check first:
  ```
  arduino-cli board list
  ```
  You should see the Uno listed with a port like `/dev/cu.usbmodem1401`
  (the number can change if you use a different USB socket — use the
  port the list shows).
- Launch (from the two lines above):
  ```
  python3 ~/hand-controlled-led/code/hand_led.py --port /dev/cu.usbmodem1401 --camera 1
  ```
- Quit: **Q**.

## 2 · Air Desktop — the cards and decisions desk

- Program file: `~/air-desktop/code/air_desktop.py` (v7.3)
- Launch:
  ```
  python3 ~/air-desktop/code/air_desktop.py --camera 1
  ```
- Quit: **Q**.

## 3 · Portal — the two-hand filter frame

- Program file: `~/portal/portal.py`
- Launch:
  ```
  python3 ~/portal/portal.py --camera 1
  ```
- Switch effects: touch the two hands' fingertips together, or keys
  1–9, 0. Quit: **Q**.

## 4 · Mac Conductor — gestures drive your real Mac

- Program file: `~/mac-conductor/mac_conductor.py`
- Needs: Terminal's Accessibility permission (already granted).
- Launch:
  ```
  python3 ~/mac-conductor/mac_conductor.py --camera 1
  ```
- Quit: **Q**, or hold your hand in the top-left corner (the failsafe).

---

## If the camera shows the wrong picture

Camera 0 is a virtual camera from another app. Quit with **Q** and
run the same launch line with `--camera 2` instead of `--camera 1`.

## Where things live (your Mac)

- `~/hand-controlled-led/` — LED project + the shared toolbox
- `~/air-desktop/` — Air Desktop program, `notes.txt`, `audio/`,
  and the queue/answers shortcuts into the Drive "Air Desk" folder
- `~/portal/` — Portal
- `~/mac-conductor/` — Mac Conductor
- Pictures for photo cards: `~/Pictures/air-desk/`
