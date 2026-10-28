# Gestural control — research shortlist (Oct 25, 2026)

What's out there, and what Caitria could add to her four gesture programs
(Air Desktop, Portal, Mac Conductor, hand-controlled LED). Constraints
honoured throughout: no static poses needing independent finger control
(pinch / open palm / fist / whole-hand motion only); runs on her Mac with
the existing Python + MediaPipe setup or the Uno; no purchases (the EMG
wristband class — Meta Neural Band, Mudra — is $199+ and locked to other
ecosystems: a trend to mine for patterns, not a shopping suggestion).

## Trends

1. **Input is moving from camera to wrist, and the winning gestures are
   tiny.** Meta's sEMG Neural Band (CTRL-labs) shipped Sep 30, 2025 with
   the Ray-Ban Display glasses: pinches select, thumb slides scroll,
   pinch-and-twist changes volume — from a hand resting in a lap. The 2025
   *Nature* work: generic models pass 90% gesture categorization with no
   per-user calibration. Known failure mode: accidental activation.
   Lesson: design for small motions from a resting hand; make every
   command easy to cancel.
   Sources: https://smartwearguide.com/guides/emg-wristband-smart-glasses-input/ · https://www.nature.com/articles/s41593-025-02057-3
2. **Platforms converged on pinch as the universal trigger** (visionOS
   look + pinch; Meta's porting guidance maps thumbstick scroll to
   "a swipe or a pinch-and-drag" — the exact Conductor scroll binding
   Caitria ruled tonight). Palm-summons-menu is the other recurring
   pattern. Her vocabulary is already the industry vocabulary; gains are
   in feedback and error-proofing.
   Sources: https://graspable.dev/blog/build-for-meta-vr-glasses-on-the-web · https://nullstud.io/blog/apple-vision-pro-app-development/
3. **Makers are shifting from pose catalogues to motion and continuous
   control** — trajectory recognition (a 2025 system reports >99% on
   eight dynamic gestures), two-hand instruments, fist-trace drawing.
   Poses become the clutch; the information is in the movement.
   Sources: https://WWW.MDPI.COM/2673-4591/108/1/22 · https://github.com/Ekmand/gesture-synth · https://www.hackster.io/steffen-brown/me461-final-project-computer-vision-control-4d5582

## Ideas

1. **Drawn-shape commands** — pinch and trace a shape (check = YES,
   X = NO on a decision card, circle = gather cards); classified from the
   pinch point's path over ~1 s (the "point history classifier" pattern).
   Fits Air Desktop, then Conductor (circle = Mission Control). *Medium.*
   Sources: https://deepwiki.com/Kazuhito00/hand-gesture-recognition-using-mediapipe/4.1-mediapipe-integration · MDPI above.
2. **Fist-trace sketching** — fist = pen down, fist centre draws, open
   palm = pen up. Annotate a snap, or draw into Portal's warped view.
   *Medium.* Source: https://www.hackster.io/steffen-brown/me461-final-project-computer-vision-control-4d5582
3. **Two-hand theremin / gesture synth** — one hand's height = pitch,
   other hand's pinch = volume, fist = mute; sounddevice is already
   installed. Could also drive the LED strip. New sibling to Portal.
   *Medium.* Sources: https://github.com/Ekmand/gesture-synth · https://dev.to/lluisestape/creating-sound-with-gestural-harmony-aethericgeometry-2dlh
4. **Pinch-and-twist knob** — while pinching, wrist rotation (landmark
   axis angle) = a continuous dial: Conductor volume/zoom, rotate/scale
   a held Air Desktop card (cards can't rotate today), LED brightness.
   *Small–medium.* Source: smartwearguide above.
5. **Head as a second channel** — Face Landmarker's head pose +
   blendshapes: nod = confirm, shake = cancel, long blink = third
   option. Answers decisions while both hands are holding cards.
   *Medium* (second model, run at reduced rate; decisive amplitude).
   Sources: https://deepwiki.com/gaofc/NeuroSync/5.1-biometric-monitoring · https://deepwiki.com/jays0606/mediapipe-facelandmark-demo/5.1-mediapipe-face-landmarker
6. **A real clutch (quasimode)** — commands only count while the other
   hand holds an open palm. The anti-accidental-activation pattern from
   Neural Band reviews and XR research; her Conductor already arms
   command mode this way — extend to Air Desktop answers. *Small.*
   Sources: smartwearguide above · https://arxiv.org/html/2311.15372v1
7. **Bimanual split roles** ("Objestures") — one hand anchors/holds,
   the other hand's pinch then means act (duplicate / stamp / file)
   instead of grab. Portal variant: left holds frame, right pinch
   cycles filters. *Medium.* Source: https://arxiv.org/html/2503.02973v1
8. **Push-to-press (Z axis)** — hand size growth toward the camera =
   press, for big targets (decision zones, Conductor confirm). Needs a
   short personal calibration; honestly slower than pinch — best for
   chunky targets only. *Small–medium.* Source: http://www.yorku.ca/mack/iss2022.html
9. **Train her own motions** — record motions her hand likes (wrist
   flick, scoop, wave-off) + a "background" class of fidgets, retrain
   with MediaPipe Model Maker. The sanctioned fix for "that pose
   hurts." *Large — a weekend project; highest payoff.*
   Sources: http://developers.googleblog.com/introducing-mediapipe-solutions-for-on-device-machine-learning/ · https://reetinav.quarto.pub/my-blog/posts/hand-gesture-tutorial/index.html
10. **LED strip as the desk's status light** — run the Uno backwards:
    decision waiting = slow gold pulse, mic recording = red, answer
    recorded = green flash, trash-dwell = filling bar. Ambient "did it
    record?" confirmation without looking at the screen — speaks
    directly to tonight's DEFER/notes uncertainty. *Small.*
    Source: https://www.hackster.io/jobinjjose03/gesture-controlled-led-system-abfae7

## Feasibility, honestly

Ideas 4, 6, 8, 10 are incremental on code she already has. Ideas 1, 2,
3, 5, 7 are real builds, each one mechanism. Idea 9 is the only large
one. Nothing needs hardware she doesn't own.

## Addendum (Oct 26) — hardware watch: Raspberry Pi AI Camera (IMX500)

Caitria asked whether this type of camera could eventually replace her
computer camera. The part: Sony IMX500 sensor with the neural network
running inside the sensor itself; $70; works with any Pi that has a CSI
connector (inference is on-sensor, so the host Pi does almost nothing);
preloaded detection + pose-estimation models; sends gesture *events*
(MQTT/webhooks) to Home Assistant instead of streaming video anywhere —
private and always-on by design. Hard limits: ~8 MB shared on-sensor
memory and 640×640 INT8 inputs, so models are tiny and quantized; the
pose model is body keypoints, not 21-point hand landmarks.

Verdict: not a swap-in replacement for the laptop camera — Air Desktop /
Conductor / Portal need the Mac's screen and precise two-hand fingertip
tracking, which this sensor can't match. It IS the right shape for a
fixed room node: coarse gestures (open palm, swipe, point, thumbs-up —
never Victory) → Home Assistant actions (lights, dimming by hold,
scenes), with the desk setup staying on the Mac. Eventual architecture
is both: Mac camera at the desk, AI-camera nodes in rooms. Host note:
her Pi 3 B+ could drive one (on-sensor inference), but that board is
pencilled in for Pi-hole.
