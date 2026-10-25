# Mac Conductor v5 — Gestures & Behaviours

The complete list, as built (Oct 25, 2026). "Hold" times are how long a pose must be held before it fires — the overlay counts them up as a percentage.

## Pointing — always on, one hand
- **Index finger** — moves the real cursor. One Euro filtered: steady when your hand is still, fast when it sweeps.
- **Quick pinch** (thumb to index, released within ~0.3 s, hand fairly still) — a **click**. The position locks the instant the pinch starts, so the click can't smear.
- **Element snap** — at pinch start, the program asks macOS what real element is at your aim point. Within ~14 px of a small element's frame, the click locks onto its **centre** instead. The overlay says `(snapped)`.
- **Pinch + hold (~0.3 s), or pinch and move off the lock** — becomes a **drag**. Real dragged events: windows follow live, and the drop lands where your hand is at release.
- **Parking** — movements under ~3 px are ignored while aiming, so the cursor plants on narrow targets instead of trembling off them.

## Rock hand — standalone, any time (no gate needed)
- **Rock pose** (thumb + index + pinky out, middle and ring folded) — opens the **app switcher** (Cmd+Tab held). Keep holding: it steps to the next app about every **0.9 s**. **Open your hand** to land on the highlighted app.

## Command mode — window commands
**Arm it:** show an **open palm with your second hand**. Command mode lasts **3 s** per palm (re-show the palm to extend). The cursor freezes; commands act on the **window under the cursor**. One window command per arming; 0.8 s cooldown after. Every command below must be **held** — the overlay shows `HOLD: <name> <percent>`.

- **Two hands spread apart** (past ~1.4× the narrowest distance seen this arming), hold **0.4 s** — **fullscreen** the window.
- **Two hands squeeze together** (below ~0.7× the widest distance seen this arming), hold **0.4 s** — **exit fullscreen**. (Only offered when the window actually is fullscreen — the program reads its state.)
- **Fist**, hold **0.6 s** — **close the window**, by pressing its real close button (not Cmd+W). The longest hold in the set, on purpose.
- **Thumb down**, hold **0.4 s** — **minimize**. If the window is fullscreen, it un-fullscreens first, pauses ~0.45 s, then minimizes.
- **Thumb up**, hold **0.3 s** — **zoom / maximize** (fills the screen; not fullscreen).
- **Victory** (index + middle), hand moves up/down — **scroll**, only while the pose is held. Hand down = page down.
- **Victory + fast sideways swipe** — **switch Space** (Desktop) in the swipe direction. Fires once, then command mode ends so your cursor is live.
- **Open palm (command hand) flicked up fast** — **Mission Control**. Fires once, then command mode ends so you can click a window — the view stays open.
- **Point (index only)**, hand moves up/down — **volume up / down**, in small steps about every 0.12 s while you move.

If a window refuses a command, the Terminal prints the refusal — commands never fail silently.

## Poses — how they're read
Poses are measured geometrically from hand landmarks (no extra model). A pose is **sticky for ~0.25 s**, so a flickery frame mid-motion doesn't cancel a held pose. The bottom of the conductor window shows each hand's current pose label — if a gesture misbehaves, that label says what the program thought you did.

## Pauses & exits
- **Both hands up (neither a palm)** — **paused**: cursor frozen until you go back to one hand.
- **Hand lost mid-drag** — the drag lets go safely instead of dragging into the void.
- **Drive your hand to the screen's top-left corner and hold (~0.6 s)** — emergency stop: the program quits.
- **Q** in the conductor window — quits.
- Closing the Terminal window also ends it.
