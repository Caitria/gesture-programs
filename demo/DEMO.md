# The Three-Act Demo — runbook

One sitting, three programs, in story order: **the hand lights real LEDs → the hand bends the camera image → the hand drives the real Mac.** Each act is the previous one's idea with the training wheels off a little further.

You run **one command** (`bash ~/demo.sh`) and the sequencer walks you through all three, pausing between acts so you can move the LED rig, breathe, and narrate. `Q` ends each act's program; **Control+C** in the Terminal stops the whole show.

---

## Pre-flight (do this before the audience, ~5 minutes)

1. **Uno plugged in.** USB cable from the Mac to the Uno. When it powers up, the five LEDs do their chase-blink — that's the rig telling you it's alive before you've run anything.
2. **Breadboard in the camera's view.** Rig positioned so the camera sees your hand *and* the LEDs without you leaning. Do the whole demo from one chair position if you can.
3. **Camera is free.** Quit Zoom/FaceTime/Photo Booth and anything else that holds the camera. The Immersed app doesn't need quitting, but remember: **camera 0 is its fake camera** — your real one is the nonzero number you've been using (1, or 2 if 1 showed the Immersed card).
4. **Windows staged for Act 3.** Two Finder windows and one browser window open, somewhere visible. One Finder window is the designated sacrifice for the close-window gesture.
5. **Accessibility permission still on** (Act 3's clicks need it): System Settings → Privacy & Security → Accessibility → Terminal = on. You set this during the build; just confirm it hasn't been toggled off.
6. **Optional — the TV.** If you're casting: start the mirror *before* the demo (Control Center → Screen Mirroring, or the HDMI cable), laptop below the TV facing you. Test pointing once on the big screen; AirPlay lag is normal.
7. **Quick smoke test (optional but wise).** Run `bash ~/demo.sh`, step through each act for ten seconds, Q out. Better to find a loose jumper wire now than in front of people.

## Running it

1. Download `demo.sh` (and this runbook, if you want it beside you).
2. In Terminal:
   ```
   cp "$(ls -t ~/Downloads/demo*.sh | head -1)" ~/demo.sh
   ```
3. ```
   bash ~/demo.sh
   ```
   That runs camera 1. If your real camera is number 2, it's `bash ~/demo.sh 2`. The script activates the project Python environment itself — you don't need `(.venv)` first.

## Act by act — what to show

**Act 1 — Hand-controlled LEDs.** Fist: all five off. Open hand: all five on. Then count 1–2–3–4–5 slowly. *Say:* the camera watches the hand, the computer counts fingers, the signal crosses USB to an Arduino, and physical lights answer. **Stick to counts** — the pinch-to-dim mode exists in code but was never field-tested; don't debut it live.

**Act 2 — Portal.** Both hands up, frame on your thumbs and pinkies. Start on NORMAL (just the frame), then jump the keyboard tour: **6** PIXELATE, **2** NEON, **3** THERMAL, **0** GLITCH — then do one switch hands-only: fingertips together, next effect. Finish with **F** for fullscreen. *Say:* the frame is a piece of the camera image, warped flat, filtered, and pasted back — sixty times a second it isn't, but at demo speed "live" is honest.

**Act 3 — Mac Conductor.** Point and sweep (the cursor is really the Mac's). Quick-pinch click on an icon. Pinch-and-hold drag of a Finder window — slow, visible, lands where you let go. Then the second-hand palm: command mode — thumb up (zoom), spread (fullscreen), squeeze (back), fist-hold on the sacrifice window (close; let them watch the HOLD counter climb). *Demo around the known rough edges:* scroll, Space-switching, and the app switcher are mid-fix in the queue (F6/F7) — they're not in the show until the next iteration proves them.

## Recovery card — if something stalls mid-demo

- **Window shows the Immersed "Please Launch" card** → wrong camera number. Q, and rerun the whole script with the other number (`bash ~/demo.sh 2`). 
- **Act 1 can't find the Uno** → cable first (unplug, replug, watch for the chase-blink), then rerun.
- **Act 3 cursor frozen** → you probably have both hands up: that's PAUSE by design. Drop to one hand. Or the corner-stop got held — just relaunch the act with `python3 ~/air-desktop/code/mac_conductor.py --camera 1`.
- **Anything else misbehaves** → Q, breathe, rerun that act alone:
  - Act 1: `python3 ~/hand-controlled-led/code/hand_led.py --camera 1`
  - Act 2: `python3 ~/air-desktop/code/portal.py --camera 1`
  - Act 3: `python3 ~/air-desktop/code/mac_conductor.py --camera 1`
  (These three need `(.venv)` active: `cd ~/hand-controlled-led/code` then `source .venv/bin/activate` first.)

## After the demo
The known-rough edges (scroll/Spaces/switcher, F6–F8) are in `air-desktop/FEEDBACK-QUEUE.md` awaiting the next iteration. Gesture cheat-sheet for Act 3 patter: `air-desktop/GESTURES.md`.
