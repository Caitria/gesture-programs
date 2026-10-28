# Breathing Mushroom — detailed build guide for your setup (v2)

Source plan: `breathing_mushroom_agent_plan.json` (uploaded Oct 25, 2026)
Adapted for: your Uno (working today), your CHANZON RGB LED bag, your
220 Ω resistors, your 400-point breadboard. Terminal-only, one action per
step, a "You should see" check after steps that change something.

---

# Part 1 — Is 220 Ω right? The proof, not just the claim

## The three numbers this depends on (all checked)

1. **Your LED** (CHANZON 5 mm RGB, common anode — from the bag you
   photographed today, matching the maker's published specs):
   - Red uses up **2.0–2.2 V**
   - Green and blue each use up **3.0–3.2 V**
   - Each colour is rated for **20 mA** of current. More than that,
     for a long time, damages the colour inside the LED.
2. **Your Uno:** each pin is rated for **20 mA** as its normal working
   value (40 mA is the never-exceed line, not a working value).
3. **Your power:** the Uno runs at **5 V**.

## The one formula

An LED does not limit its own current. The resistor does. The resistor
gets whatever voltage the LED does not use up, and that sets the current:

```
current = (5 V − LED's volts) ÷ resistor ohms
```

The dangerous case is always the LED's **lowest** voltage (2.0 V for red,
3.0 V for green/blue), because that leaves the most voltage across the
resistor and pushes the most current. So we check the worst case, not the
average case.

## What 220 Ω actually gives

| Colour | Worst case (lowest LED volts) | Other end of its range |
|---|---|---|
| Red | (5 − 2.0) ÷ 220 = **13.6 mA** | (5 − 2.2) ÷ 220 = 12.7 mA |
| Green | (5 − 3.0) ÷ 220 = **9.1 mA** | (5 − 3.2) ÷ 220 = 8.2 mA |
| Blue | (5 − 3.0) ÷ 220 = **9.1 mA** | (5 − 3.2) ÷ 220 = 8.2 mA |

Every number is **under both limits** — under the LED's 20 mA and under
the Uno pin's 20 mA — with room to spare. These are also slight
over-estimates: a real Uno pin drops a little voltage itself when it is
sinking current, so the real current is a touch lower, never higher.

Two more safety margins on top of that, in the code as written:

- The sketch caps brightness at 0.45 and the colour values below full,
  so at the brightest moment of the breath the pins are only on about
  16 % (red), 27 % (green), 34 % (blue) of the time. Average current is
  well below the peak numbers above.
- The resistor itself only has to shed about 41 mW of heat at worst,
  and your resistors are 1/4 W (250 mW) parts. Not close.

## Why not the other values?

- **330 Ω (the uploaded plan's value):** also safe — red 9.1 mA,
  green/blue 6.1 mA worst case — just dimmer. 220 Ω is safe *and*
  brighter, and it is the value you actually own.
- **150 Ω for red / 100 Ω for green and blue:** those are the exact
  minimums that would land precisely on 20.0 mA in the worst case.
  "Exactly at the limit" is not a design target — a slightly-off LED
  or supply puts you over it. We don't build there.
- **The 10 MΩ bag:** (5 − 2.0) ÷ 10,000,000 = 0.0003 mA. The LED would
  be dark. That bag stays out of this build.

## Check a resistor yourself before you trust it

Your 220 Ω resistors, two ways — do both once, on the first one:

**By its coloured bands:** hold it so the gold band is on the right.
Reading left to right: **red = 2, red = 2, brown = "× 10"**.
2, then 2, then ×10 = **220**. Gold means ±5 %, so a true value anywhere
from 209 Ω to 231 Ω is normal for this part.

**With your Fluke 106:** the resistor must be out of the breadboard,
not connected to anything.

1. Turn the Fluke's dial to **Ω** (the resistance symbol).
2. Black probe in the **COM** socket, red probe in the **VΩ** socket.
3. Touch one probe tip to one resistor leg and the other probe tip to
   the other leg. It does not matter which probe goes to which leg.
4. Squeeze the probe tips against the legs with your fingers on the
   *probe handles* — if your fingers touch both bare legs at once, your
   body becomes part of the measurement and the number wanders.
   *You should see:* a reading near **220** (roughly 200–240 counts as
   right for this check; the 209–231 range is the exact spec).
   If it shows a number in the millions, or "OL", you picked up a
   10 MΩ resistor — set it back in its bag.

---

# Part 2 — Your breadboard, in plain words

Everything in this build is placed by **hole address**: a letter and a
number printed on the board, like `d13`. Here is how your board works.

- Turn the board so the numbers read **1 on the left to 30 on the
  right**, the right way up, with letters **a–e on the top half** and
  **f–j on the bottom half**. A groove runs left-to-right down the
  middle, between e and f.
- For one number, the five top holes are joined together inside the
  board. Example: `a12`, `b12`, `c12`, `d12`, `e12` are all the **same
  electrical point**. That row of five is called a **strip**.
- The five bottom holes for that number are also joined: `f12` to `j12`
  are one point — a **different** point from the top strip.
- The groove is a wall: the top strip and the bottom strip of the same
  number are **not** connected — unless you put a part across the groove
  yourself. In this build, **each resistor is that bridge**.
- Different numbers are never connected to each other. `d12` and `d13`
  are separate points. That is why each LED leg must get its **own
  number**.
- The long **+ / − rails** along the edges: **this build does not use
  them at all.** (Your rails may be split partway along — that caused
  trouble earlier today. Bypassing them removes that whole problem.)

### The map this build will follow

```
              top half                 ‖  bottom half
           a    b    c    d    e       ‖   f    g    h    i    j
 row 12     .    .    .   LEG   R ──────‖── R    .    .    .   wire
 row 13     W5V  .    .   LEG   .       ‖   .    .    .    .    .
 row 14     .    .    .   LEG   R ──────‖── R    .    .    .   wire
 row 15     .    .    .   LEG   R ──────‖── R    .    .    .   wire
```

Read one row like this, using row 12 as the example:

- `d12` = one LED leg.
- `e12` and `f12` = the two ends of one resistor, bridging the groove.
- `j12` = a jumper wire heading to the Uno.
- Row 13 is special in this example: it is the common leg's row, so
  `a13` gets a jumper wire straight to the Uno's 5V — and **no resistor**.

That is the whole pattern. Every colour row is identical:
**leg in d, resistor from e to f of the same number, wire out of j of
the same number.**

---

# Part 3 — Get ready

**Step 1.** Unplug the Uno's USB cable from the Mac.
*You should see:* all lights on the Uno are off. Nothing gets plugged
or unplugged on the breadboard while power is on, for the whole build.

**Step 2.** Empty the breadboard from today's hand-LED build.
Pull each LED, resistor, and jumper wire straight up, one at a time,
and set them aside in a pile.
*You should see:* a completely empty board — every hole open.

**Step 3.** Turn the board to the Part 2 position: numbers 1 (left) to
30 (right) reading the right way up, a–e on top, f–j at the bottom.
*You should see:* the centre groove running left-to-right.

**Step 4.** Cut 3 resistors off your taped "220" strip.
Cut the paper tape beside each resistor with scissors. Do **not** cut
the metal legs short — leave them as long as they come.
*You should see:* 3 loose resistors with long legs, bands red-red-brown
with a gold band at one end.

**Step 5.** Check the first resistor with the Fluke, exactly as in
Part 1 ("Check a resistor yourself").
*You should see:* a reading near 220.
If it is wrong, check another one from the strip and tell me what you
got before going on.

**Step 6.** Get out 4 jumper wires, all different colours if you can.
Write down which colour wire you will use for each job — this matters
when something doesn't light later:
- 5V wire (suggest red): ______ colour
- Red-channel wire: ______ colour
- Green-channel wire: ______ colour
- Blue-channel wire: ______ colour

**Step 7.** Take one RGB LED from the CHANZON bag and look at its legs
before it goes anywhere near the board.
*You should see:* 4 legs in a row under the dome. **One leg is longer
than the other three. That longest leg is the common (+) leg.** The
other three are the red, green, and blue legs, one per colour.

---

# Part 4 — Put the LED in the board

The LED's 4 legs are close together — closer than the breadboard's hole
spacing. You will gently spread them apart. This is normal for this part.

**Step 8.** Hold the LED by its dome, legs pointing down.
Gently bend the legs apart like a tiny fan: the two outside legs bend
out the most, the two inside legs bend out a little.
*You should see:* the 4 leg tips now land roughly one hole-number apart
from each other, and **no leg touches any other leg anywhere**. If two
legs touch, bend them apart again — touching legs are a short circuit
and that colour will not behave.

**Step 9.** Line the leg tips up over holes **d12, d13, d14, d15**.
Left to right: first leg over `d12`, second over `d13`, third over
`d14`, fourth over `d15`.

**Step 10.** Push all four legs in together, gently, until the dome
sits a little above the board.
*You should see:* one leg in each of d12, d13, d14, d15 — four
different numbers, no leg bent flat, no legs touching.

**Step 11.** Find the longest leg again, now that it's in the board.
It will be in `d13` or `d14` — the second leg in from one end.
Write it down: **"Longest leg is in hole ______."**
That row number is your **common row**. Everything else in this guide
hangs off that one fact.

**Step 12.** Look at the two possible maps below and find yours.

**Map A — longest leg in d13:**

| Hole | What this leg is |
|---|---|
| d12 | Red leg |
| **d13** | **Common (+) leg — longest** |
| d14 | Green leg |
| d15 | Blue leg |

**Map B — longest leg in d14** (the LED went in the other way round):

| Hole | What this leg is |
|---|---|
| d15 | Red leg |
| **d14** | **Common (+) leg — longest** |
| d13 | Green leg |
| d12 | Blue leg |

These maps are the maker's standard leg order (red, common, green, blue
in a row). Part 5 tests them before anything is final — if your LED
disagrees with its map, the test catches it and we swap two wires,
nothing is harmed.
*You should see / write down:* "I have Map ___ (A or B)."

---

# Part 5 — Test one colour at a time

You will light each colour on its own, using **one** resistor and
**two** jumper wires, moved from row to row. USB is unplugged before
every move. Do not skip ahead to Part 6 until all three colours have
lit, one at a time.

First, the wire that stays put for the whole of Part 5:

**Step 13.** Take your 5V wire. Push one end into hole **a** of your
common row — that is `a13` if you have Map A, or `a14` if you have
Map B. (It must be the letter-a hole of the **same number** as the
longest leg, because a and d of one number are the same strip.)
Push the other end into the Uno socket labelled **5V** (on the power
header along the side of the Uno).
*You should see:* a wire running from the common row's a-hole to 5V.

Now the test loop. You will do steps 14–19 **three times** — once for
each colour row. A "colour row" means the number of a colour leg:
Map A → test rows **12, 14, 15**. Map B → test rows **15, 13, 12**.

**Step 14.** Pick the first colour row to test. Write its number here
before you wire it: ______

**Step 15.** Take resistor #1. Push one leg into hole **e** of that
row's number (e.g. testing row 12 → `e12`). Bend it across the centre
groove and push the other leg into hole **f** of the **same number**
(e.g. `f12`).
*You should see:* the resistor lying across the groove, one end in the
top half, one end in the bottom half, both ends in the same number.
This resistor is what makes the test safe — the colour leg is never
connected to anything without it in between.

**Step 16.** Take a jumper wire (any colour — this one is temporary;
call it the test wire). Push one end into hole **j** of the same number
(e.g. `j12`). Push the other end into a Uno socket labelled **GND**
(use the GND socket on the power header, near the 5V socket).
*You should see:* for the row you're testing — leg in d, resistor
e→f, test wire in j, common wire still in place on its own row.

**Step 17.** Double-check before power: USB out; the resistor is
really in e and f of the **same** number; no bare legs touching.
*You should see:* exactly the three connections from step 16's check.

**Step 18.** Plug the USB cable into the Mac.
*You should see:* **one colour of the LED lights** — red, green, or
blue, at a comfortable brightness, and nothing gets warm.

**Step 19.** Write down what you saw, in this form:
"Row ______ lit ______ (colour)."
Then **unplug the USB cable** and wait for the LED to go out.

**Step 20.** Pull the resistor out (both ends) and pull the test wire's
board end out of its j hole. Leave the 5V wire exactly where it is.
Repeat steps 14–19 for the second colour row, then the third.
*You should see at the end:* three written lines, three different
colours, one per row.

**Step 21.** Compare your three lines with your map from Step 12.
- **They match the map:** good — Part 6 will use your map as written.
- **Two colours are swapped versus the map:** also fine, and exactly
  why we tested. Cross out the map and write the true one from your
  three lines. Part 6 follows your written lines, not the printed map.
- **A colour never lit, or the LED lit with no test wire connected:**
  stop here and tell me which row and what happened. Do not go to
  Part 6. Nothing is harmed; we sort it from your notes and a photo.

---

# Part 6 — Final wiring (only after Part 5 passes)

Everything stays in the same holes you just tested. Now all three
resistors and all three channel wires go in at once. **USB unplugged**
for all of Part 6.

**About ground in this build — read this, it is different from this
morning's build:** in the final wiring there is **no wire to a GND
socket, and that is correct, not a missing wire.** This morning's LEDs
ran pin → LED → ground rail → GND wire. This LED runs the other way:
5V → common leg → colour leg → resistor → pin (`~3`/`~5`/`~6`). When a
pin is switched on in this design, it connects *internally* to the
Uno's ground inside the chip — the pin itself is the road to ground.
The loop completes inside the Uno and back through the USB cable.
The only GND wire in this whole project was the temporary test wire in
Part 5, which stood in for a pin so you could light one colour
directly. In Part 6 the pins take that job over, so the test wire
comes out and stays out.

**Step 22.** Leave the 5V wire where it is (a-hole of the common row →
Uno 5V). Do not move it.

**Step 23.** Wire the **red** channel, using your written map's red row:
1. Resistor: one leg in **e** of the red row's number, other leg in
   **f** of the same number, across the groove.
2. Take your red-channel wire. Board end in **j** of the red row's
   number.
3. Other end of that wire into the Uno socket labelled **3** — the one
   with the `~` mark beside it, printed `~3`.

**Step 24.** Wire the **green** channel the same way, on the green
row's number:
1. Resistor: **e** of green's number → **f** of green's number.
2. Green-channel wire: board end in **j** of green's number.
3. Uno end in the socket labelled **`~5`**.

**Step 25.** Wire the **blue** channel the same way, on the blue row's
number:
1. Resistor: **e** of blue's number → **f** of blue's number.
2. Blue-channel wire: board end in **j** of blue's number.
3. Uno end in the socket labelled **`~6`**.

Worked example, if you have Map A, your board now holds:

| Wire / part | Board hole | Uno socket |
|---|---|---|
| 5V wire | a13 | 5V |
| Red resistor | e12 ↔ f12 | — |
| Red wire | j12 | ~3 |
| Green resistor | e14 ↔ f14 | — |
| Green wire | j14 | ~5 |
| Blue resistor | e15 ↔ f15 | — |
| Blue wire | j15 | ~6 |
| LED legs | d12 (R), d13 (common), d14 (G), d15 (B) | — |

**Step 26.** The full check, before any power. Read each line out loud
against the board:
- [ ] 3 resistors in the board, each bridging the groove on its own
      colour's number (e→f, same number both ends).
- [ ] No resistor on the common row.
- [ ] 4 jumper wires: one to 5V (from the common row's a-hole),
      three to `~3`, `~5`, `~6` (from the j-holes of the colour rows).
- [ ] Each Uno-end wire is in the socket whose **printed label** matches
      — chosen by the label, not by its position in the row.
- [ ] No LED legs touching each other; no bare wire ends touching.
*You should see:* every box ticked. If one isn't, fix it now, unplugged.

---

# Part 7 — Put the code on the Uno (Terminal only)

**Step 27.** Open Terminal: press **Command + Space**, type
`Terminal`, press **Return**.
*You should see:* a window with a prompt (a line ending in `%` or `$`,
waiting for typing).

**Step 28.** Type this line and press **Return**:
```
mkdir -p ~/ArduinoProjects/BreathingMushroom
```
Then type this line and press **Return**:
```
cd ~/ArduinoProjects/BreathingMushroom
```
*You should see:* the prompt comes back both times, with no error text.

**Step 29.** Type this line and press **Return**:
```
nano BreathingMushroom.ino
```
*You should see:* the window turns into a mostly empty text editor.
`nano` is an editor that lives inside Terminal.

**Step 30.** Paste the whole sketch (the `BreathingMushroom.ino` file
sent with this guide) with **Command + V**.
*You should see:* code filling the screen; the first line starts
with `//`.

**Step 31.** Save: hold **Control** and press **O**, then press
**Return** once (that confirms the file name).
Then quit: hold **Control** and press **X**.
*You should see:* you are back at the Terminal prompt.

**Step 32.** Check the file really saved. Type this and press
**Return**:
```
head -3 BreathingMushroom.ino
```
*You should see:* the first 3 lines of the sketch printed back at you,
starting with `// Breathing Mushroom`.

**Step 33.** Plug the USB cable in (if it isn't) and type this, then
press **Return**:
```
arduino-cli board list
```
*You should see:* a row that says **Arduino UNO**. Note the port it
shows — it looks like `/dev/cu.usbmodem1401` if the Uno is in the same
Mac socket as today. If the ending number differs, that new number is
your port for Step 35. Write it down: ______

**Step 34.** Compile. Type this one line and press **Return**:
```
arduino-cli compile --fqbn arduino:avr:uno .
```
*You should see:* several lines, ending with a memory summary
("Sketch uses … bytes") and **no** line containing `error`.
If you do see `error`: stop, copy the whole output, and send it to me.
Do not do Step 35.

**Step 35.** Upload. Type this one line — with **your** port from
Step 33 in place of the example — and press **Return**:
```
arduino-cli upload -p /dev/cu.usbmodem1401 --fqbn arduino:avr:uno .
```
*You should see:* a few lines about uploading, then the prompt returns.

**Step 36.** Look at the LED.
*You should see, first:* the new sketch's own **flash test** — red
alone for a quarter second, then green alone, then blue alone, then
off. That flash is the proof each colour's full loop works
(pin → wire → resistor → leg → 5V). A colour that does not flash here
has a wiring fault on that colour's row — the code has done its part.
*Then you should see:* it breathes — slowly brightening and dimming,
one full breath about every 4 seconds — while its colour drifts:
cyan → blue → violet → back to cyan, about every 12 seconds.
Nothing hot, nothing buzzing, the Uno is not restarting (its small
lights stay steady).

Note: the **old** flash test from today's hand-LED build (the chase
across pins 8–12) belonged to the old sketch and the old wiring. It
stops the moment this sketch uploads, and it can never flash this LED
anyway — this LED is on pins 3, 5, 6, which the old sketch never
touches. From now on, the red-green-blue flash above is your
flash test.

---

# If it does not do that

- **Completely dark:** the usual suspects, in order — 5V wire not in
  the common row's a-hole or not in the 5V socket; a resistor end in
  the wrong number (e and f must match); `COMMON_ANODE` in the code
  changed away from `true`. Check all of it unplugged.
- **One colour missing:** that colour's resistor (e→f of its number)
  or its j-wire; or that row's leg was misread in Part 5.
- **Two colours swapped:** your Part 5 notes beat the printed map —
  swap those two wires at the **Uno end** (unplugged): e.g. red showing
  where green should be means the `~3` and `~5` wires trade sockets.
- **One colour on full blast, never fading:** that colour's wire is
  landing on GND or 5V somewhere instead of its `~` pin — check the
  Uno-end socket by its printed label.
- **Anything hot, the Uno restarting, or hard flicker:** unplug the
  USB now, leave it unplugged, and send me a photo of the board.

---

# Part 8 — Getting the LED away from the breadboard

Yes — connectors just work. The circuit does not care whether a path
is a solid LED leg in a hole or a leg plus a wire plus a connector,
as long as each of the 4 paths stays **separate, continuous, and in
the same order**. Distance is a non-issue at this size: even 1 metre
of thin jumper wire each way adds under 0.5 Ω of resistance against
your 220 Ω resistors (~0.2 %) — brightness does not change.

**Method A — plug-on connectors, no soldering (for tonight).**
Uses **male-to-female jumper wires**: one end is a pin (male, goes in
the breadboard), the other end is a socket (female, slides onto a
leg). Check your rainbow jumper set: if some wires have a socket end
instead of a pin, those are the ones.

1. USB unplugged.
2. Work **one leg at a time** — never have two legs loose at once,
   so the order cannot get lost.
3. Pull one LED leg out of its d-hole. Slide the socket end of a
   jumper fully onto that leg, until the plastic housing is up near
   the dome.
4. Push that jumper's pin end into the **same d-hole** the leg just
   came out of.
5. Write it down: "______ colour wire = ______ LED leg (row ______)".
6. Repeat for the other three legs.

The plastic housings also insulate the legs from each other — keep
the short bare stretch between dome and housing fanned out so bare
legs don't touch. The grip of a socket on a flat LED leg is looser
than on a round pin: it works, but it's wobbly, so don't let the LED
dangle by its wires — rest it where it will sit (in the mushroom cap
is ideal). A tiny wrap of tape over housing + leg helps if one keeps
slipping. This gets you about **20 cm** from the board (standard
jumper length).

**Method B — soldered extensions (for as far as you like, and for
the permanent mushroom).** Solder one wire to each LED leg; solder
the other end of each wire to a pin snapped off your breakaway male
header strip (confirmed in your parts); that pin plugs solidly into
the same d-hole. Insulate each solder joint (tape, or heat-shrink if
you have it) so bare joints can never touch. This is a good first
soldering job — Hakko, helping hands, and solder are all confirmed
in your kit — and worth doing as its own guided step when the
prototype becomes the mushroom, not as a rush job tonight.

**Not this:** the black 4-prong plug from your LED tape is made for
the tape's pads. It is not a connector for this LED.

# Part 9 — Second RGB LED on the same Uno (v4 sketch)

Same pattern as LED 1, new rows, plus one new idea: a **5V hub**.

**Why a hub:** the Uno has only ONE 5V socket, and now two common
legs need 5V. So one empty board strip becomes the meeting point:
row **24** top strip (`a24`–`e24` are one point).
- `a24` → wire → Uno **5V** (the only wire in the 5V socket now)
- `c24` → wire → LED 1's common row a-hole (LED 1's old 5V wire,
  moved at the Uno end only — its board end does not move)
- `e24` → wire → LED 2's common row a-hole

**Order of work** (full micro-steps were given in chat, Oct 25):
1. USB unplugged. Build the hub; move LED 1's 5V wire's Uno end to
   `c24`; plug in and confirm LED 1 still flashes and breathes
   exactly as before. Unplug. (Hub proven before anything new is added.)
2. LED 2 legs splayed into **d18, d19, d20, d21**. Longest leg will be
   in d19 (Map A) or d20 (Map B), same leg order as LED 1's maps.
   Common wire: a-hole of LED 2's common row → `e24`.
3. Test LED 2's colours one at a time, exactly like Part 5:
   resistor **e→f of the row being tested**, temporary wire from
   **j of that row → GND**. Record three lines, one colour per row.
4. Final wiring for LED 2, same pattern as LED 1:
   resistors e→f on each colour row; j-wires to the Uno —
   red row → **`~9`**, green row → **`~10`**, blue row → **`~11`**.
5. Full read-out-loud check (Part 6 style, both LEDs + hub), then
   upload sketch **v4**: flash test is now LED 1 red/green/blue,
   then LED 2 red/green/blue (600 ms each). In the show, LED 2 runs
   the same journey and breathing offset by half a cycle.

Parts for LED 2: 1 more RGB LED, 3 more 220 Ω resistors, 5 jumper
wires (common, three channels, hub feed). Totals for the pair:
6 resistors, 9 wires + LED 1's original common wire.

### Mapping grid — every part, Map A (common leg in d13 / d19)

Board holes: `·` = empty. Resistor "e ↔ f" = one resistor bridging
the groove on that row. Bottom half of row 24 is all empty.

| Row | a | b | c | d | e | ‖ | f | g | h | i | j |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 12 | · | · | · | LED 1 red leg | 220 Ω | ‖ | 220 Ω | · | · | · | wire → Uno ~3 |
| 13 | wire → hub c24 | · | · | LED 1 common leg | · | ‖ | · | · | · | · | · |
| 14 | · | · | · | LED 1 green leg | 220 Ω | ‖ | 220 Ω | · | · | · | wire → Uno ~5 |
| 15 | · | · | · | LED 1 blue leg | 220 Ω | ‖ | 220 Ω | · | · | · | wire → Uno ~6 |
| 18 | · | · | · | LED 2 red leg | 220 Ω | ‖ | 220 Ω | · | · | · | wire → Uno ~9 |
| 19 | wire → hub e24 | · | · | LED 2 common leg | · | ‖ | · | · | · | · | · |
| 20 | · | · | · | LED 2 green leg | 220 Ω | ‖ | 220 Ω | · | · | · | wire → Uno ~10 |
| 21 | · | · | · | LED 2 blue leg | 220 Ω | ‖ | 220 Ω | · | · | · | wire → Uno ~11 |
| 24 | hub: → Uno 5V | · | hub: ← LED 1 common | · | hub: ← LED 2 common | ‖ | · | · | · | · | · |

Map B (LED went in the other way round) changes only the leg rows:
LED 1 — d12 blue (j12 → ~6), d13 green (j13 → ~5), d14 common
(a14 → hub c24), d15 red (j15 → ~3). LED 2 — d18 blue (j18 → ~11),
d19 green (j19 → ~10), d20 common (a20 → hub e24), d21 red
(j21 → ~9). Resistors stay e→f on every colour row; common rows
never have one.

### Uno socket grid — what plugs into the Uno

| Uno socket | What is in it |
|---|---|
| 5V | hub feed wire (from a24) — the only wire in this socket |
| ~3 | LED 1 red wire (from j of LED 1's red row) |
| ~5 | LED 1 green wire |
| ~6 | LED 1 blue wire |
| ~9 | LED 2 red wire |
| ~10 | LED 2 green wire |
| ~11 | LED 2 blue wire |
| GND | nothing in the final build (temporary test wire only) |
| all others | nothing |

# Stage D — fabric (later, after the light works)

From the uploaded plan, unchanged except the materials check:
black felt ~12×12 cm, 2–3 organza scraps ~5×5 cm layered into a cap
~4–5 cm wide, a small diffuser scrap between LED and cap, embroidered
stem/mycelium on the felt. LED sits behind the cap, unplugged while you
place it, legs insulated from each other and from the fabric.
Breadboard and Uno stay on the table — nothing gets worn at this stage.

**Open check for Stage D:** do you have felt and organza (or another
translucent fabric) in the house? Not in any parts photo so far.
A scrap of white tissue or baking parchment can stand in as a test
diffuser over the clear LED in the meantime.
