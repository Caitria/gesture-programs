# Moon Flowers

Two RGB LEDs, each in a tissue/paper diffuser on a gooseneck stem —
flowers, on stems, on my desk. (This project started life under the
name "Breathing Mushroom"; the build guide still uses that name.
The flowers were renamed once they were built, because that's what
they are.)

**Left alone**, the Uno runs the show: a slow colour journey —
cyan → azure → violet → magenta — over about 18 seconds, the two
flowers half a cycle apart.

**Raise both hands** and you conduct them, theremin-style:

- One hand is the **anchor**: raised, roughly still.
- The other hand **conducts**: left–right steers the colour across
  the spectrum, up–down sets the pulse speed.
- How far apart the two hands are sets the pulse **intensity**.
- **One hand up** = pause: both flowers freeze exactly as they are.
- **Hands away** = the breathing show resumes by itself.

Honest caveat: the tracking can drop a hand in low light. When it
does, the flowers freeze or resume on their own — they improvise,
and the show survives it.

## Files

- `GUIDE.md` — the full build guide: the resistor maths proven from
  the LED's datasheet numbers, wiring, stages. (Written under the
  old name.)
- `BreathingMushroom/BreathingMushroom.ino` — the autonomous
  breathing sketch (no camera, no serial).
- `BreathingMushroomHand/BreathingMushroomHand_v2.ino` — the
  hand-control Uno sketch: the same breathing show plus a serial
  ear. Commands at 9600 baud: `G <colour 0..1000> <intensity
  0..255> <period ms>`, `P` pause, `A` autonomous. If commands stop
  arriving, the show resumes after ~3.5 s.
- `code/mushroom_hand_v5.py` — the current Mac-side program
  (MediaPipe → the commands above). It's the finger-LED build grown
  up: same stack, two-hand map.

## Wiring, in one breath

Common-anode RGB LEDs: common leg to 5V, each colour leg through a
220 Ω resistor to a PWM pin — flower 1 on ~3/~5/~6, flower 2 on
~9/~10/~11. The pins sink current to ground inside the chip, so
there's no ground wire in the finished build. The full proof and
the hole-by-hole version are in `GUIDE.md`.
