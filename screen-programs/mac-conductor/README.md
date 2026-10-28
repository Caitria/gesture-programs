# Mac Conductor

The Air Desktop gestures, driving the real Mac.

- **Index fingertip** is the cursor (smoothed with a One Euro filter;
  clicks snap to the real UI element under the point, via the
  Accessibility tree).
- **Quick pinch** clicks; **pinch and hold** drags real windows —
  sent as honest `LeftMouseDragged` events via pynput, because the
  more obvious library posts events macOS doesn't treat as drags.
- **Second hand, open palm** arms command mode for three seconds:
  fist hold = close window, thumbs-down hold = minimize, thumbs-up
  hold = zoom, two-hand spread/squeeze = fullscreen.
- **Q** quits; holding a hand in the **top-left corner** is the
  emergency stop.

Needs macOS Accessibility permission for the terminal app, or the
clicks won't land.

**`GESTURES.md`** is the full reference — every gesture and its hold
time.

Known state, honestly: it works, and a fix round is approved and
queued — scrolling moves to pinch-and-drag (the Victory pose it used
is one of the least ergonomic static poses a hand can make),
Space-switching to an open-palm flick, and the app switcher will
step one app per gesture instead of overshooting. See
`../FEEDBACK-QUEUE.md`, items F6–F8.
