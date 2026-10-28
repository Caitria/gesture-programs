# hand-controlled-led/ — Program 1

The camera watches my hand and counts fingers (0–5). The count is
sent over USB serial to an Arduino Uno, which lights that many LEDs
on a breadboard. Fist = all off, open hand = all five on. A second
mode maps pinch distance to brightness.

It's the simplest program here and the foundation for the rest: the
shared Python environment and the hand model live in this project,
and every other program in the repo borrows them.

## Files

- `START-HERE.md` — the one-page version: wiring summary + how to run.
- `PLAN.md` — the full build plan, written from zero (Terminal basics
  included), with every stage and what "working" looked like.
- `BREADBOARD-GUIDE.md` — the wiring, hole by hole.
- `code/hand_led.py` — the program (camera → count → serial).
- `code/uno_send.py` — a tiny test sender for checking the Uno end
  without the camera.
- `code/hand_led_uno/hand_led_uno.ino` — the Uno sketch. It parses
  commands one byte at a time (`C0`–`C5` counts, `B0`–`B255`
  brightness) and echoes what it received, which is how the link was
  debugged.

## Run it

With the shared environment active and the Uno plugged in:

```sh
arduino-cli board list   # find the Uno's port, e.g. /dev/cu.usbmodem1401
python3 code/hand_led.py --port /dev/cu.usbmodem1401 --camera 1
```

The port name can change with the USB socket; the board list is the
source of truth. `--dry-run` runs the camera half with no Uno.
**Q** quits.
