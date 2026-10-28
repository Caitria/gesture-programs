# Air Desktop — gesture-controlled cards (Minority Report style)

**What this is:** a second program that grows out of the hand-controlled LED build. Same camera, same hand tracker (MediaPipe), same Python — but now it watches **both hands**, and the screen holds three floating cards. The control is the **pinch** (thumb tip touching index tip):

- **Pinch a card, move your hand** → the card follows. You've grabbed it.
- **Let go mid-move** → the card glides on its own. A toss.
- **Pinch the same card with both hands, spread your hands** → the card grows. Hands together → it shrinks.
- Keys while it runs: **Q** quit · **R** reset the cards · **F** full screen on/off.

No new parts, no new installs. Your existing Python setup from the LED project runs this as-is — the program even reuses the hand-model file that project already downloaded.

Three stages, each with its own pass test. Do them in order; each stage uses the last.

---

## Getting the files onto your Mac

You already know this dance from the LED project — same shape:

1. Download the file **`air-desktop-project.zip`** (attached in chat) to your Mac. It lands in **Downloads**.
2. Open **Terminal** (⌘+Space, type `Terminal`, Return).
3. Make the project folder and step into it. Type each line, Return after each:

```
mkdir -p ~/air-desktop/code
cd ~/air-desktop
```

4. Unzip the download into place:

```
unzip -o ~/Downloads/air-desktop-project.zip -d ~/air-desktop
```

*You should see:* a short list of files being extracted, including `PLAN.md` and `code/air_desktop.py`.

5. Check the layout:

```
ls ~/air-desktop
ls ~/air-desktop/code
```

*You should see:* `PLAN.md` in the first list, `air_desktop.py` in the second. If the zip extracted into a nested `air-desktop` folder instead (so you see a folder where the file should be), tell Maude — it's a one-line fix.

6. Turn on the LED project's Python environment — this program borrows it (nothing new to install). Two lines:

```
cd ~/hand-controlled-led/code
source .venv/bin/activate
```

*You should see:* your prompt gains the `(.venv)` tag, same as during the LED build. **Every run of the air desktop starts with these two lines** if you've opened a fresh Terminal.

**About the camera number:** every command below ends with `--camera 1` as the example. Use **the number that showed you** in the LED project, if yours was different. (Camera 0 is the Immersed placeholder — not you.)

---

## Stage A — Hands and pinches (no cards yet)

**Goal:** prove the program sees both hands and knows a pinch from not-a-pinch.

Run:

```
python3 ~/air-desktop/code/air_desktop.py --camera 1 --track-only
```

**You should see:** the camera window opens, darkened, with your hand drawn as a skeleton — dots on every joint, lines between them — and a **ring** floating between your thumb tip and index tip.

**The test:**
1. Hold up **both hands**. Two skeletons, two rings.
2. **Pinch** with one hand (thumb tip to index tip, like picking up something tiny). *The ring fills in solid yellow while you hold the pinch*, and empties when you open.
3. Same with the other hand. Then pinch both at once.

**Pass:** both hands tracked, rings fill exactly while pinching and empty on release, no flickering in between. Quit with **Q**.

*If a ring flickers:* you're near the pinch boundary — pinch decisively, fingertips actually touching. The program uses two thresholds (pinch starts at a tighter distance than it ends) specifically so a held pinch doesn't strobe.

---

## Stage B — Grab, drag, toss

**Goal:** move the cards.

Run (same command, without the stage flag):

```
python3 ~/air-desktop/code/air_desktop.py --camera 1
```

**You should see:** three cards on the darkened camera view — **PHOTO — the coast**, **NOTES**, **CHART — fingers** — and your skeleton hands with rings.

**The tests, in order:**
1. **Hover:** put your ring (fingertips open, no pinch) over a card. Nothing should happen — hovering is not grabbing.
2. **Grab:** pinch *on* a card. Its border thickens — that's the grab registering. Move your hand: the card follows, staying where your fingers hold it.
3. **Drop:** open your fingers while holding still. The card stays where you left it.
4. **Staying put (tuning update, Oct 25):** cards no longer glide or drift — a card stays exactly where you release it, anywhere, at any speed. While you carry one, its movement is smoothed so tracker jitter doesn't turn into wobble, and grabbing has a forgiving margin: a pinch within about a thumb's width of a card's edge still picks it up (pinching the *sides* of cards was finicky before this).
5. **Stacking:** drag one card over another, drop it. Now pinch the overlap: you grab the one **on top** (grabbing a card also brings it to the front).
6. Press **R**: all three cards jump back to their starting spots.

**Pass:** grab only on pinch, card follows smoothly, drop stays exactly put, R resets. Quit with **Q**.

*Too twitchy or too sluggish?* Both are feel settings in the code (pinch thresholds, glide friction). Report which way it feels and Maude can tune the numbers — that's a code edit, not a rebuild.

---

## Stage C — Two hands stretch a card

**Goal:** the full Minority Report move.

Run the same Stage B command again.

**The test:**
1. Put one hand's ring over the **left half** of a card, the other hand's ring over the **right half** of the *same* card.
2. **Pinch with both hands at once.** The card's border thickens.
3. **Spread your hands apart** slowly. The card grows, following the distance between your hands.
4. **Bring your hands together.** It shrinks. (It won't go below about half size or above about triple — those limits are deliberate.)
5. While stretched, move both hands together sideways: the card travels, still stretched.
6. Release one hand: stretch mode ends, the card keeps its new size, and the still-pinching hand is now just holding it — drag it somewhere and drop it.

**Pass:** one card, two pinches, size follows hand distance smoothly, position follows the midpoint between your hands.

**Full-screen for the real effect:** press **F** and the window fills the screen. If the Mac is showing on a TV, this is the version that reads as the movie prop. **F** again to come back, **Q** to quit.

---

## Optional — run the LEDs at the same time

If the Uno is plugged in from the LED project, add the port to the command:

```
python3 ~/air-desktop/code/air_desktop.py --camera 1 --port /dev/cu.usbmodem1401
```

Now your **first hand's finger count also drives the five LEDs** while you move cards. (The count reads best from an open, upright hand — same limits as the LED project.) This is a garnish, not a stage: skip it freely.

---

## Troubleshooting

- **Window shows the Immersed placeholder card.** Wrong camera number. Q, re-run with the next `--camera` number (your LED-project number is the right one).
- **"Camera did not open."** Another program is holding the camera (the LED program still running counts — one camera, one program), or the number is wrong. Close the other window first.
- **`ModuleNotFoundError` (mediapipe / cv2 / numpy).** The `(.venv)` tag is missing from your prompt — the environment isn't on. Run the two lines from step 6 of setup.
- **Cards grab when I don't mean it.** Your fingertips are drifting together below the pinch threshold while you hover. Pinch is judged by the *gap* between thumb and index tips relative to your hand's size — keeping fingers visibly apart while moving prevents accidental grabs. If it still happens, tell Maude; the ON threshold can be tightened.
- **A card got lost off-screen.** It can't — the physics keeps cards inside the frame. But a fully-shrunk card behind a big one can hide. **R** resets everything visibly.
- **Hand tracking drops a hand at the screen edges.** Normal for webcams — the tracker needs most of the hand in frame. Play in the middle two-thirds of the view.

---

## Portal mode — BUILT (second program in the same folder)

`code/portal.py` — the first TikTok's effect. Hold up **both hands**: the frame between the two hands' thumb tips and pinky tips becomes a live filter window (perspective-warped patch, filtered, pasted back). Ten filters: NORMAL, NEON, THERMAL, MONO, DUAL-TONE, PIXELATE, SKETCH, INVERT, BLUR, GLITCH.

- Run (same setup lines, same camera number): `python3 ~/air-desktop/code/portal.py --camera 1`
- **Change filter (v2, loosened Oct 25 after v1's gesture never engaged in her run):** bring **any fingertip of one hand near any fingertip of the other** (thumb/index/pinky, either hand) and separate again — the corner dots turn **cyan** as you get close, so the gesture visibly charges. Keyboard: **N** next, **P** previous, and **number keys jump straight to an effect**: 1 NORMAL, 2 NEON, 3 THERMAL, 4 MONO, 5 DUAL-TONE, 6 PIXELATE, 7 SKETCH, 8 INVERT, 9 BLUR, 0 GLITCH. Note: **NORMAL showing "no distortion" is correct** — it warps the patch out and straight back invisibly; the warp becomes visible once a real filter makes the patch differ from its surroundings.
- **F** full screen, **Q** quit.
- **Stage A test:** both hands up → white frame appears and follows your hands, contents = NORMAL (unchanged image, just the frame).
- **Stage B test:** cycle through all ten filters with the corner-touch; each name flashes on screen and the patch visibly changes; the frame should track tilts and stretches without tearing.

---

## Mac Conductor — BUILT (third program, Oct 25, after Portal passed)

`code/mac_conductor.py` — the graduation step: fingertip drives the **real** Mac cursor (Portal Working!!! → Caitria green-lit it the same minute). Index tip mapped from the central region of the camera view to the full screen (smoothed), pinch = mouse-down (drag real windows; a quick pinch is a click), **both hands up = pause**, lost-hand = safe release, pyautogui FAILSAFE on (top-left corner stops it), Q quits. **New install needed: `pip install pyautogui` inside the venv. New permission needed: macOS Accessibility for Terminal** (System Settings → Privacy & Security → Accessibility) or clicks won't land. Test order given: point-move first, then pinch-drag a Finder window by its title bar, then a quick-pinch click on an icon, then the pause and failsafe so exits are proven before free use. File size for the copy-verify: **7228 bytes**.

---

## Mac Conductor v3 — researched rebuild (Oct 25, after v2 field report)

v2 verdict: "slightly less laggy" — drag still invisible until drop, drop overshoots, tap targets too small. Research pass (web, Oct 25) **confirmed the root causes with sources**:

- **Invisible drag = wrong event type (source-verified).** PyAutoGUI's macOS backend posts `kCGEventMouseMoved` unconditionally, even between its own mouseDown/mouseUp (pyautogui `_pyautogui_osx.py` lines 824–828); macOS window drag tracking waits for `NSLeftMouseDragged` events and macOS does **not** auto-convert. **pynput's darwin backend posts `kCGEventLeftMouseDragged` automatically while a button is held** (`pynput/mouse/_darwin.py` lines 135–154) — drop-in fix, now the conductor's event layer (needs `pip install pynput`).
- **Lag stacks:** PyAutoGUI PAUSE defaults to 0.1s per call (we had zeroed it) plus an internal macOS catch-up sleep; fixed-divisor EMA trades lag uniformly; synchronous pipeline. Replaced by a **One Euro filter** (Casiez, Roussel & Vogel, CHI 2012, doi:10.1145/2207676.2208639; published defaults min_cutoff 1.0 Hz, beta 0.007, d_cutoff 1.0) + a small clamped velocity lead on free pointing only.
- **Overshoot on drop:** pending smoothing steps flushing after release. v3 posts a **final move to the current hand target before mouseUp** — the window lands where the hand is at release, like a card.
- **Micro-drag clicks:** pinch onset jitters the control point. v3 uses **Steady Clicks–style locking** (Trewin, Keates & Moffatt, ASSETS 2006): position locks at pinch start; release within **0.30 s and 14 px** = click at the lock; hold longer or move further = drag (press fires at the lock, then live dragged events). Plus a **3 px parking deadband** while aiming.
- Pipeline stays 640×480 @ ~30 fps paced (camera-mouse literature floor ≈25 fps). Emergency stop changed with the event layer: Q, both-hands pause, hand-lost safe release, and **hold the target in the screen's top-left corner 0.6 s = quit** (PyAutoGUI's failsafe no longer applies — it isn't posting events anymore).

**Behaviour change to learn:** drag now starts with a deliberate **pinch-and-hold beat (~⅓ second)** — quick pinch = click, held pinch = drag. File size for the copy-verify: **12416 bytes**.

---

## Mac Conductor v4 — snapping + gesture pack (Oct 25, built on research #2, Caitria: "let's do it all!")

- **Element-aware clicks:** at pinch start only, an AX hit-test (`AXUIElementCopyElementAtPosition`, system-wide element, 0.15s messaging timeout) finds the real element at the aim point; if the point sits within **14px** of a small element's frame (area ≤ 160,000 px²), the click **locks to the element's centre** — Bubble Cursor (Grossman & Balakrishnan, CHI 2005) over the real macOS tree. HUD shows "(snapped)" when it engages. All AX calls are wrapped — any failure disables the layer, never crashes the conductor. Frame extraction is the one best-effort piece (AXValue struct conversion with a string-parse fallback; if both fail, no snap, raw point used).
- **Command mode:** **Open Palm on the second hand arms commands for 3s** (cursor freezes; pause still applies to two non-palm hands). Window acted on = window under the cursor (element's AXWindow, frontmost fallback). Hold-to-fire: CLOSE 0.6s / FULLSCREEN & UNFULLSCREEN & MINIMIZE 0.4s / ZOOM 0.3s; one command per arming; 0.8s cooldown; on-screen "HOLD: ACTION %" progress + toast.
- **Bindings (as ruled):** two-hand spread >1.35× baseline = fullscreen (set AXFullScreen=true), squeeze <0.65× = exit fullscreen; FIST = close via **AXPress on the real AXCloseButton** (not Cmd+W); THUMB_DOWN = minimize (AXMinimized); THUMB_UP = zoom (AXPress AXZoomButton). Extras included since "do it all": VICTORY + vertical move = scroll (pynput scroll; hand down = page down — sign is one flip if it feels backwards), VICTORY + fast horizontal swipe = Ctrl+←/→ Space switch, palm swipe up = Ctrl+↑ Mission Control, ILOVEYOU = Cmd+Tab held while posed (release commits), POINT + vertical move = volume keys (0.12s throttle).
- **Poses are geometric** (landmark extension ratios), not the Gesture Recognizer model — no new download; the bottom HUD line shows each hand's live pose label so misreads are visible and reportable.
- **New install:** `pip install pyobjc-framework-ApplicationServices` (pynput already in from v3). Startup prints whether the Accessibility layer is ON or OFF. File size for the copy-verify: **27167 bytes**.

---

## Mac Conductor v5 — the F1–F5 fix iteration (Oct 25, queue called by Caitria)

Built from `FEEDBACK-QUEUE.md`. **Rock hand freed from the gate** (standalone app switcher: Cmd held, Tab re-tapped every 0.9s to cycle, release commits) and **poses made sticky for 0.25s** against motion flicker. **Toggle commands fire once per arming and exit command mode on firing** (Mission Control / Spaces — the cursor is immediately live for selecting; the F2 re-fire toggle is structurally impossible now). **Fullscreen judged by state, not snapshot:** at arming the program reads the target window's AXFullScreen; if fullscreen, only exit is offered, triggered by squeezing below 0.70× the **widest** spread seen while armed; if not, spread above 1.40× the **narrowest** enters it. **Minimize is two-step from fullscreen** (un-fullscreen, scheduled minimize 0.45s later). **Swipes measured from pose start** (trajectory anchor on pose change; 15% of frame; 1.2s window). **AX command failures print to Terminal.** No new installs. File size for the copy-verify: **31462 bytes**.

---

## Where this goes next (not built, just mapped)

- **Your own photos on the cards** (drop image files in a folder; cards become a real photo wall).
- **Rotation:** two hands don't just stretch — twist, and the card turns. Same machinery, one more measurement (the angle between your hands).
- **Portal mode:** the first TikTok — the rectangle between both hands' thumb+pinky tips becomes a live filter window (NEON / THERMAL / PIXELATE…). Shares this program's two-hand tracking wholesale.
- **Conducting the real Mac:** fingertip drives the actual cursor, pinch drags real windows. Needs a macOS Accessibility permission — a deliberate step, taken with eyes open, after the gestures feel good here.

## v3 — Caitria's picks (Oct 25, evening): capture, real notes, spawn, trash

Built same evening in `code/air_desktop.py` (v3). All v2 feel rules kept
(cards stay where put, smoothed drag, 26px grab pad, two-hand stretch).

- **Capture card:** both hands up shows the thumb/pinky frame (Portal
  machinery). Pinch BOTH hands in the air (neither holding a card,
  starts within 0.35s of each other) -> the framed region is warped
  straight and becomes a SNAP card at that spot. C key does the same
  while the frame shows. 1.2s cooldown.
- **Notes card (real):** reads ~/air-desktop-notes.txt (created with
  starter text on first run; --notes overrides). The program polls the
  file's mtime ~1/s, so edits appear on their own; a tap (quick pinch)
  on the card reloads immediately.
- **Photo cards (real):** images from ~/Pictures/air-desk (--photos
  overrides); the folder is created on first run. A tap on a photo
  card shows the next picture. Empty folder -> placeholder text, and
  spawning a PHOTO yields a blank card with a toast explaining.
- **Spawn pad** (top left, "+ NEW: <kind>"): pinch-start on the pad
  spawns that kind in the pinching hand; the pad rotates
  PHOTO -> NOTES -> BLANK. N key spawns at centre.
- **Trash pad** (bottom right): release a dragged card with its centre
  on the pad to delete it (pad lights up while a dragged card is over
  it). U restores the last deleted card (stack of 5). R still resets
  to the default three cards.
- Tap = grab released within 0.35s with the card moved < 14px.

Field-test order: notes first (edit the file while it runs), then
spawn/trash, then capture (the double-pinch timing is the new risk).

## v4 — decision cards (Oct 25, evening; Caitria's idea)

Maude deals decisions onto the desk. Queue file ~/air-desktop-queue.txt
(--queue), plain-text blocks split by a line of only ---, first line =
the decision's name, # lines are comments. One gold DECISION n OF m
card at a time (370x265), body wrapped from the block. Answers: drag
the card onto the YES / DEFER / NO strip along the bottom (the strip
only shows while a decision card is up), or keys Y / X / D; dragging a
decision card onto TRASH also counts as DEFER. Each answer appends
"YYYY-MM-DD hh:mm AM - VERDICT - <title>" to ~/air-desktop-answers.txt
(--answers) and deals the next decision. The queue file is polled with
the notes file (~1s): new blocks Maude adds appear mid-run; titles
answered this session are skipped on reload. R re-deals the current
decision. Stage 1 transport is manual (files move by hand); a synced
folder is the designed Stage 2, gated on the household access rules.
Shipped queue v1 carries two real decisions: Conductor scroll binding
and the matrix-watch co-dream restriction.

## v5 — mic on/off gestures + voice notes (Oct 25, evening)

Thumbs UP held 0.5s = mic on; thumbs DOWN held 0.5s = mic off
(HoldGesture latch; pose = classify_pose: all four fingers folded +
thumb extended clear, tip above/below its base joint; point, pinch,
victory, open hand and tucked fist all tested NOT to match). Either
hand, but not while that hand pinches or holds a card. Recording via
sounddevice (16 kHz mono) to ~/air-desktop-audio/note-<time>.wav;
transcription on-device via PyObjC Speech (SFSpeechRecognizer,
requiresOnDeviceRecognition, 45s cap, worker thread + runloop pump;
auth status 3 required). Results append to the answers file as
"stamp - NOTE - <decision title or General> - <text>"; failures
append an untranscribed line carrying the error + wav path, so audio
is never silently lost. Notes attach to the decision card currently
up. M key toggles. 120s auto-stop; <0.4s clips discarded. Transcript
shown on screen ~12s (LAST NOTE panel) for an eyes-on check.
New installs: sounddevice, pyobjc-framework-Speech. First run raises
two macOS permission prompts for Terminal (Speech Recognition at
startup, Microphone at first record). Verified here: py_compile;
classify_pose against 7 synthetic hands; HoldGesture timeline;
write_wav roundtrip (16k frames/16 kHz/16-bit); queue regression.
NOT verifiable here: the Speech framework calls themselves (macOS
only) — written defensively, every failure degrades to audio-only.

## Stage 2 — Drive pipe LIVE (Oct 25, evening, Caitria's Route A pick)

Drive folder "Air Desk" created at Drive root (id
18vwommUeCPOmaGYJ-QD4MJVm7NnodCBZ, verified empty by listing). Her
Mac runs Drive for Desktop, so the design is links, not uploaders:
she moves ~/air-desktop-answers.txt and ~/air-desktop-queue.txt
into the synced "Air Desk" folder and symlinks them back to the
paths the program already uses — zero code change. From then on:
the program appends answers/notes -> Drive syncs up -> Maude reads
via the Drive connector. Queue direction: Maude edits the DRIVE
copy (canonical now; the workspace copy is stale once her move
lands) -> Drive syncs down -> the program's 1s mtime poll deals
the new decisions live. Single-writer rule each way. Setup steps
delivered Oct 25 ~8:10 PM; end-to-end verification = she runs one
answer/note, then Maude reads the Drive copies back.

## v6 — the F9–F13 fix round (Oct 25, evening; she called it: "fix it all")

F9: cards bigger across the board (photo 340x260, notes/chart
320x240, blank 300x220, decision 500x360); all card text scales
with card width (title bar + bodies), decision title at 0.92,
bodies at 0.66. F10: snap = hold the two-hand frame STEADY 0.8s
(centroid drift <34px), with a progress bar and a size gate
(>220x120 px) so resting hands and thumbs-up poses can't trigger
it; double-pinch capture removed; C key kept. F11: trash pad
DELETED. Throw-to-delete: drag samples feed release_velocity;
a release faster than 950 px/s aimed sideways (or 1100 up) starts
a fling, as does carrying a card's centre out of the frame; exits
resolve in finish_exit. Slow releases still park the card exactly
where put (clamp on release only). F13: answer zones = YES right
side / NO left side (tall, 120 wide) / DEFER top centre; judged by
overlap_area > 1500 (helper, unit-tested); thrown decision card:
right=YES, left=NO, top=DEFER. F12: photos folder rescanned on the
1s poll and pushed into live photo cards; decode failures are
blacklisted per session and skipped; placeholder now says where
to put pictures, in large text. Verified here: py_compile;
overlap_area 4/4; release_velocity + throw classification 8/8
(incl. bottom-is-never-a-throw); photo bad-file skipping; pose +
queue regressions. 62.5 KB. Awaiting field test.

---

## v7 (Oct 25, evening — built after the v6 field test)

Her live instructions during the build: the chart goes ("remove it - or it should show something more useful"), voice-typing into Note cards, files reorganized by project. Plus the v6 fallout: throws failed in the field, and a crash to fix.

- THROWS REMOVED entirely (release velocity, fling physics, decision-by-throw): her verdict "the swipe away doesn't work, fast dragging loses card." Cards are always clamped on screen again; a fast drag can no longer lose a card.
- TRASH is back as a DWELL (her spec): pad bottom-centre; while a card is HELD and any part overlaps the pad, a 0.5 s dwell deletes it (decision card = DEFER, same as trash before); a card merely resting on the pad never deletes; the pad fills red with dwell progress; U undo unchanged.
- STATUS card replaces the chart: time, fingers up per hand, mic state, decisions done/waiting, photo count — refreshed in the 1 s poll.
- VOICE-TYPING: hold a NOTES card with one hand, thumbs-up with the other; the transcript is appended to the notes file and appears on the card within a second, instead of going to the answers file. Untranscribed audio still falls back to an answers-file NOTE.
- CRASH FIXED: ValueError (195,316,3) into (195,294,3) — a held photo card could hang 22 px off the frame edge (v6 exempted grabbed cards from clamping); blit_fit's raw slice then mismatched. v7 clamps always + blit_fit clips its box to the image and forces exact crop shape; the placeholder gradient is clipped the same way. The crash shape is reproduced in the test battery and passes.
- ORGANIZED PATHS: defaults now live in the project folder — ~/air-desktop/notes.txt, ~/air-desktop/air-desktop-queue.txt, ~/air-desktop/air-desktop-answers.txt, ~/air-desktop/audio/. Startup resolves new-vs-legacy per file (prefer new if it exists, else fall back + print), migrates the notes file and legacy WAVs automatically, and never auto-creates a starter queue at the new path while a legacy queue exists (keeps the Drive symlink step clean).
- BUILD SLIP, caught pre-ship: the throws-removal edit sliced out blit_fit and wrap_line with the removed code; py_compile passed (runtime-only failure). Caught by a function-inventory diff against the shipped v6 copy; both restored (blit_fit in its hardened form) and the inventory check is now part of the battery.
- Queue restocked the same night (4 decisions) after the desk ran empty — her rule: answering one should surface the next.
- v7.1 (same night, her field note "the transcription should visually update a Note when added to the file"): root cause — notes cards drew the TOP of the notes file and stopped when full; dictated lines append at the BOTTOM, so they were saved but below the fold, invisible. Fix: notes cards now render the newest lines (the tail); a voice-typed append refreshes every notes card in the same frame (not via the 1 s poll) and flashes the card border white for 3 s with the new line highlighted. Status cards still read top-down. Drive: air_desktop_v7_1.py, 66,418 B.
- v7.2 (same night, her field note "defer option is not working"): the zones were judged ONLY at pinch-release. DEFER is the top zone — exactly where the hand leaves the camera view before a clean release registers, so the release (and the verdict) never landed; two-hand holds had the same hole (their release path never ran the zone check at all). Fix: zones are now ALSO judged continuously while a decision card is held (one hand or two): 0.35 s of overlap with a lit zone records the answer, no release needed; release-in-zone still answers instantly; a hand that answers mid-pinch cannot re-grab until it opens once (spent_hands). Geometry + dwell tests pass (centre = no verdict, top = DEFER incl. at scale 1.4, sides unchanged). Drive: air_desktop_v7_2.py, 69,112 B.
- v7.3 (same night, her field note "Notes is still only showing the text it starts with after transcribing"): the Drive answers file proved the real fault — her test dictations ("Testing testing testing does this update the notes", 9:15 PM) landed in the ANSWERS file, targeted at the decision card. Transcription and the card display were both fine; the ROUTING missed, because v7 routed to notes only if a notes card was being pinched at the exact instant the mic started. Fix: TAP a notes card to arm it as dictation target for 60 s (red dot in the title bar; tap again disarms); holding one at mic start arms it too, so letting go to speak is safe. Notes tail rendering (v7.1) unchanged. Drive: air_desktop_v7_3.py, 71,454 B.
