# air-desktop/ — the screen programs (2–4)

Three programs built as one suite on the same machinery: two-hand
tracking, pinch grab with hysteresis, and a smoothed follow so tracker
jitter doesn't become drift. They were rehearsed here first because a
virtual desk can't break anything real.

| Program | File | One line |
|---------|------|----------|
| Portal | `code/portal.py` | Two hands hold a frame; the picture inside it is warped and filtered live (10 effects). |
| Air Desktop | `code/air_desktop.py` | A desk of movable cards that became a decision desk and a dictation surface. |
| Mac Conductor | `code/mac_conductor.py` | The same gestures driving the real Mac — cursor, clicks, window drags, palm-gated window commands. |

## Air Desktop, the decision desk

The desk shows ordinary cards (a photo card reading a folder of
pictures, notes cards backed by a real text file, a status card) and
one gold **decision card** at a time. Decisions come from a plain-text
queue file; answers are appended to an answers file. On my setup both
files live in a synced cloud folder, so my assistant stocks the queue
and reads the verdicts — the desk is a two-way channel, not a toy.

- **Answer** by holding the decision card in a lit zone — YES (right),
  NO (left), DEFER (top) — for a short beat, or release it there, or
  press Y / X / D. Holding it on the TRASH pad also counts as DEFER.
- **Delete a card** by holding it on the TRASH pad for half a second.
  A card merely resting there is safe. U undoes a deletion.
- **Dictate** with thumbs-up (start) and thumbs-down (stop). Tap a
  notes card first to arm it (a red dot shows in its title bar) and
  the words land in the notes file and appear on the card; dictate
  unarmed and the note goes to the answers file instead, aimed at the
  current decision. Transcription is on-device (macOS Speech).
- **Capture** a card from the camera by holding a two-hand frame
  steady for about a second.

The versions moved fast (v3–v7.3 in two days) because every field
failure became a numbered item in `FEEDBACK-QUEUE.md` and a fix in the
next build. `PLAN.md` is the full build record; `GESTURE-RESEARCH.md`
is the survey of what the rest of the gestural-control world is doing
and what might get added next.

## The Conductor

Gesture reference: `GESTURES.md` (every gesture and its hold time).
Known state, honestly: it works, and a fix round is approved and
queued — pinch-and-drag scrolling (the Victory pose it used before is
one of the least ergonomic poses a hand can make), open-palm-flick
Space switching, and an app switcher that steps one app per gesture.
Details in `FEEDBACK-QUEUE.md`, items F6–F8.
