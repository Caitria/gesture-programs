#!/bin/bash
# Demo sequencer — runs the three gesture programs one after another.
#   bash ~/demo.sh        (uses camera 1)
#   bash ~/demo.sh 2      (uses camera 2 — your real camera's number)
# In every act: Q quits that program and the script offers the next.
# Control+C stops the whole sequence at any point.

CAM="${1:-1}"

source ~/hand-controlled-led/code/.venv/bin/activate

echo ""
echo "=================================================="
echo "  ACT 1 of 3 — HAND-CONTROLLED LEDS (Arduino Uno)"
echo "  Plug the Uno in now if it isn't. When the window"
echo "  opens: fist = all off, open hand = all five on,"
echo "  hold up 1-5 fingers for counts in between."
echo "  Press Return to start, Q in the window to finish."
echo "=================================================="
read -r -p "Return to begin Act 1... "
python3 ~/hand-controlled-led/code/hand_led.py --camera "$CAM"

echo ""
echo "=================================================="
echo "  ACT 2 of 3 — PORTAL (the effect-changing frame)"
echo "  Both hands up: thumb and pinky tips make the frame."
echo "  Keys 1-9,0 jump to an effect; fingertips together"
echo "  steps to the next; F = full screen; Q = finish."
echo "=================================================="
read -r -p "Return to begin Act 2... "
python3 ~/portal/portal.py --camera "$CAM"

echo ""
echo "=================================================="
echo "  ACT 3 of 3 — MAC CONDUCTOR (your real desktop)"
echo "  Index finger = cursor. Quick pinch = click."
echo "  Pinch + hold = drag a window. Open palm with the"
echo "  second hand = command mode (fist hold = close,"
echo "  thumbs = zoom/minimize, spread = fullscreen)."
echo "  Q quits. Top-left corner hold = emergency stop."
echo "=================================================="
read -r -p "Return to begin Act 3... "
python3 ~/mac-conductor/mac_conductor.py --camera "$CAM"

echo ""
echo "Demo complete — all three acts closed."
