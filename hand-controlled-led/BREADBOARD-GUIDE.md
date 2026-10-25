# Breadboard Guide — Stage 2 of the Hand-Controlled LED, in pictures

*This guide goes with Stage 2 of `PLAN.md`. It covers only the wiring: five lights on a breadboard, connected to the Uno. It assumes nothing — every new word is explained the first time it appears, one small action per step, and after each step it says what you should see. The computer parts (Stage 0 and Stage 1) are already done; the only computer use here is typing test commands in Terminal at the end of a wiring step.*

---

## First, the answer to the big question: where does everything actually go?

**The LEDs do NOT plug into the Arduino.** Nothing with bare legs plugs into the Arduino at all. Here is the whole arrangement, in one picture:

```
   your Mac ──USB cable──► ┌─────────────┐
                           │    UNO      │   the board with the program on it.
                           │  (Arduino)  │   Its edge is a row of little
                           └─────────────┘   sockets (holes) with numbers.
                                  ▲
                    jumper wires  │  A jumper wire has a stiff metal pin
                    (the ONLY     │  on each end. One pin pushes into an
                     thing that   │  Uno socket, the other pin pushes
                     touches the  │  into a breadboard hole.
                     Uno)         │
                                  ▼
   ┌───────────────────────────────────────────────────┐
   │                  BREADBOARD                        │
   │  a flat plastic board full of holes. Under the     │
   │  plastic, hidden metal strips connect some holes   │
   │  to each other (that is the whole trick of it —      │
   │  see the map in Part 2).                           │
   │                                                    │
   │   LEDs plug in here ──►  ║  ║  ║  ║  ║             │
   │   resistors plug in ──►  ∿  ∿  ∿  ∿  ∿   here too   │
   └───────────────────────────────────────────────────┘
```

Three facts that make everything else make sense:

1. **The breadboard is reusable.** Nothing is soldered, nothing is permanent. Legs and wire pins just push into the holes and pull back out. A mistake costs nothing — pull it out and move it. You cannot really break the breadboard by putting something in the wrong hole at these voltages.
2. **The breadboard's job is to be a meeting place.** The Uno sends power out of one numbered socket. A jumper wire carries it to the breadboard. On the breadboard, hidden strips carry it from hole to hole, through a resistor, through an LED, and back out another wire to the Uno. The LED lights because electricity made a full round trip.
3. **The path for every LED is the same loop.** Say it once and you know all five:

> **Uno pin → jumper wire → resistor → LED long leg → LED short leg → ground rail → one wire back to Uno GND.**

The resistor's job: an LED on its own would take more current than is good for it and burn out. The resistor is a narrow place in the path that holds the flow down to a safe amount. That is why every LED gets its **own** resistor — five LEDs, five resistors.

A few words used everywhere below:

- **Socket / hole** — both mean "a place a pin or leg pushes into". On the Uno they're called sockets; on the breadboard, holes. Same idea.
- **Leg** — the stiff metal wire sticking out of a part (an LED has two legs; a resistor has two legs).
- **Jumper wire** — a short coloured wire with a metal pin on each end, made for exactly this plugging-in work. Yours are the rainbow set. The colour of a jumper wire means nothing electrically — pick colours you like. (Using the same colour every time for the same job, e.g. black or blue for anything ground-related, is a kindness to your future self, but it is a habit, not a rule.)
- **GND** — short for "ground". Here it just means the return path: the way electricity gets back to the Uno to complete the loop. The Uno has sockets labelled GND; the breadboard rail we use for returning is called the **ground rail**.
- **Rail** — a long row of connected holes running along the edge of the breadboard. Explained properly in Part 2.

**Safety and framing, before anything is plugged in:**

- Everything in this stage is **5 volts from a USB cable** — the same power as a phone charger. It cannot shock you. Nothing here touches mains electricity, wall outlets, the relay board, or the EL wire. Those are different projects and are **not** part of this stage.
- **Unplug the Uno's USB cable before you plug in or move any wire or leg, every time.** Wiring while powered is how pins get accidentally shorted (two things touching that should not). The rule for the whole stage: *change wires with USB out, test with USB in.*
- If anything ever feels hot or smells odd (it should not), unplug the USB and stop. That has not happened in this build; the sentence exists so you never have to wonder what the rule is.

---

## Your actual board — notes from your photo (Oct 25)

You photographed the breadboard, and it is the one from the Pi plank rig. Four facts about *this specific board*, which adjust the generic guide below:

1. **It is a 30-number board** (numbers 1–30, letters a–e on one half, f–j on the other). Every address in this guide runs from 2 to 29 — **all of them exist on your board, exactly as printed.** Copy them as written.
2. **The black board plugged into it is a Pi Cobbler** (labelled NULSOM, with Raspberry Pi pin names like 3V3, SDA, G17, TXD). It is an adapter that brings a Raspberry Pi's pins onto the breadboard, and it arrives by the wide grey ribbon cable. It belongs to the Pi rig — **this project does not use it, and its pins occupy holes this build needs.** Before wiring: grip it at both ends and **pull it straight up and out of the breadboard**, gently, keeping it level so its pins come out straight rather than bent. It is plug-in like everything else here — removing it harms nothing, and it can be pushed back in later for Pi work. Leave the ribbon cable attached to the Cobbler; set the pair aside together.
3. **Check YOUR board's rail split with your eyes first:** in your photo, the red printed line along the f–j edge stops partway down (around numbers 25–26) — boards of this size often split their rails there. The guide's Part 2 explains the check and the fix; on this board it matters concretely, because LED 5's ground jumper lands near number 29 and the ground return wire was described near number 1. If the blue − rail is also split, those two would be on different rail pieces. **The simple, always-works arrangement for your board:** put the Uno GND return wire into the − rail near **number 15** (the middle), and add one short jumper wire in the − rail bridging the split (one end in a rail hole just above the break in the printed blue line, the other just below it). Do both, and every ground jumper from 5 to 29 has a path home.
   - **Your close-up photo (later, Oct 25) settles most of this:** Cobbler removed, board bare, both printed lines run the visible length of the f–j edge — but printed lines are paint, not proof: on this board size the hidden rail metal can still be in two pieces under unbroken paint. The 30-second proof is the **Fluke continuity check**: dial to the continuity setting (the sound-wave symbol), touch the two probes together first (you should hear a beep — that is the meter saying "these are connected"), then put one probe in a **− rail hole near number 1** and the other in a **− rail hole near number 29** (the − rail is the outer column of holes on the f–j edge, the one the blue line runs beside). **Beep = one unbroken rail, and the bridge jumper is not needed.** Silence = split rail; the middle return (near 15) plus the bridge jumper covers you either way, so if the check is annoying you may skip it and just use that arrangement.
4. **Unrelated neighbours in the photo, leave them alone:** the wide grey ribbon and black StarTech box are other projects' cabling, and the blue board at the bottom-right corner is the relay module — the do-not-energise one. None of them is part of this build, and nothing in this stage goes near them.

---

## Part 1 — Find and check your parts (before any wiring)

You need, laid out where you can see them:

| Part | How many | Notes |
|---|---|---|
| Breadboard | 1 | From your parts photos. Any size works with this guide — Part 2 teaches you to read yours. |
| LEDs | 5 | **Confirmed (Oct 25 photo): you have a whole box of them** — see step 1.2. |
| Resistors, all the **same value**: 220 Ω, 330 Ω, or 1 kΩ | 5 | **Warning in step 1.3 — the one readable bag you own is the wrong value.** |
| Jumper wires (rainbow Dupont set) | 11 | 5 from Uno pins, 5 short ones from LED legs to the rail, 1 from the rail back to the Uno. |
| Arduino Uno + its USB A–B cable | 1 | Already programmed in Stage 1. |
| Fluke 106 multimeter | 1 | Only for checking resistors in step 1.3. |

### 1.1 The breadboard
Pick it up. **You should see:** a plastic board covered in a grid of small square holes, with **numbers** and **letters** printed beside the holes, and long printed lines (usually one red, one blue) running along one or both long edges. The exact size and the highest number do not matter. Part 2 explains how to read it.

### 1.2 The LEDs — and the fork if you have none
An **LED** is the light itself: a small coloured or clear plastic dome (about 5 mm across, roughly a match-head) with **two metal legs** coming out of the bottom.

Look at one closely. **You should see three differences between its two legs/sides:**

```
        side view of one LED

             _______
            /       \      <- plastic dome (the coloured part)
           |         |
           |         |\
           |         | \   <- look at the rim at the bottom of the
            \_______/  |      dome: one side of the rim is FLAT,
             |     |   |      the other side is round
             |     |
          LONG    SHORT
          leg     leg
           (+)     (-)
```

1. **One leg is longer than the other.** The **long leg is the + side** (where power arrives). The **short leg is the − side** (where power leaves, toward ground). This is the single most important fact about an LED: **it only lights one way round.** In backwards, it does nothing — it does not break, it just stays dark, and turning it round fixes it.
2. **The rim at the bottom of the dome has a flat side.** The flat side is on the **short leg (−) side**. If an LED's legs were ever trimmed to the same length, the flat side is how you still tell which side is −.
3. Inside the dome you may be able to see two metal shapes; the bigger one is on the − side. You do not need this — legs and flat side are enough.

**Your box (confirmed by your Oct 25 photo):** you have a whole translucent box of loose LEDs — dozens, in red, green, yellow, orange, clear and frosted white, in round and rectangular shapes. No purchase is needed; that question is closed. Picking five: **round ones are easiest** (the legs-and-flat-side checks above are easiest to see on them); colours may match or mix — different colours glow at slightly different brightnesses on the same resistor, which is normal physics, not a fault. Two cautions about that box: it is a *mixed* parts box, not a pure LED box — the black three-legged parts are transistors and the black many-legged rectangles are chips; leave those in the box, they are not part of this build. And there is a clear plastic **pushpin** in it — an actual thumbtack, sharp end up in the photo. Fish it out carefully by its head and put it somewhere else; it does not belong among electronics.

### 1.3 The resistors — read this one carefully, it contains the trap
A **resistor** is a small cylinder (usually beige or blue) with a wire leg out of each end and **coloured bands** printed around it. The bands are a code for how much it resists. The value is measured in **ohms**, written **Ω**. Bigger number = more resistance = less current gets through = dimmer LED.

For LEDs you need a *small* resistance: **220 Ω, 330 Ω, or 1 kΩ** (1 kΩ = 1,000 Ω). Any one of those three values works; **use the same value for all five LEDs** so they match in brightness.

**Your resistors — confirmed (Oct 25 photo):** you found a taped strip hand-labelled **220**, ten or more resistors on it, and the visible bands (red-red-brown) match 220 Ω exactly. **Those are the ones — this build uses five of them.** They are on a paper tape strip, the way resistors are sold: free one by cutting its two leads with scissors, leaving each lead long (about a centimetre or more on each side of the body is plenty to work with; the leads arrive much longer than this build needs).

**The trap:** the one resistor bag readable in your parts photos is labelled **100 × 10 MΩ**. **MΩ means *millions* of ohms.** 10 MΩ = 10,000,000 Ω. That is roughly forty-five thousand times more resistance than a 220 Ω resistor. An LED wired through a 10 MΩ resistor gets so little current that **it looks completely dead — indistinguishable from broken.** It is the most misleading part in your drawer for this project. Do not use the 10 MΩ bag for LEDs, and if an LED later "does nothing at all", a 10 MΩ resistor in its path is a prime suspect.

**How to tell which resistors you actually have — two ways, use either (or both):**

**Way 1: read the colour bands.** Turn the resistor so any gold or silver band is on the **right**. Read the first three bands from the left. The first two bands are digits; the third is "how many zeros follow".

| Value you want | Band 1 | Band 2 | Band 3 | Reads as |
|---|---|---|---|---|
| **220 Ω** | red | red | brown | 2, 2, one zero → 220 |
| **330 Ω** | orange | orange | brown | 3, 3, one zero → 330 |
| **1 kΩ (1,000 Ω)** | brown | black | red | 1, 0, two zeros → 1,000 |
| 10 MΩ (the trap — do not use) | brown | black | blue | 1, 0, six zeros → 10,000,000 |

**Way 2: measure with the Fluke 106.** This is the surest way, and it works even if the band colours are hard to see.

1. The resistor must **not** be plugged into anything powered. A loose resistor on the table is perfect. (Measuring resistance on a live circuit gives nonsense numbers.)
2. Turn the Fluke's dial to **Ω** (the ohms symbol). The screen wakes up.
3. Touch one probe tip to one resistor leg and the other probe tip to the other leg. It does not matter which probe goes to which leg — resistors work both ways round, unlike LEDs. Hold your fingers on the *insulated* parts of the probes, not squeezing the resistor legs themselves, or your body can bend the reading.
4. **You should see** a steady number on the screen:
   - Around **218–222** → that is a 220 Ω resistor. ✔
   - Around **325–335** → 330 Ω. ✔
   - Around **980–1,020**, or the screen shows **0.99 kΩ / 1.00 kΩ** → 1 kΩ. ✔
   - The screen shows a number in the **millions**, or **MΩ** on the display → that is the 10 MΩ trap value. Put it back in its bag. ✘
   - Small wobbles in the last digit are normal. Numbers never sit perfectly still on a multimeter; close is correct.
5. Check five resistors the same way and set the five good ones aside in a little pile of their own.

**If you only have 10 MΩ resistors:** same fork as the LEDs — the resistor part of this stage pauses until you have five of 220 Ω / 330 Ω / 1 kΩ. (Resistors are sold in assortment packs too, and an assortment covers this.) There is no wiring trick that makes 10 MΩ work for an LED; wiring five of them still leaves millions of ohms. Naming that plainly now saves a very confusing evening later.

**Checkpoint before Part 2 — you should have, in front of you:** breadboard, 5 LEDs (legs identified), 5 resistors all of one good value, a handful of jumper wires. If any of the three forks stopped you (no LEDs / only 10 MΩ resistors), the rest of the guide will keep; come back to this checkpoint when the parts exist.

---

## Part 2 — How to read your breadboard (the map)

A breadboard looks like hundreds of identical holes. Under the plastic it is not identical at all: **hidden metal strips connect groups of holes together.** Plugging two legs into the same group is the same as soldering them together — electricity treats them as one point. Plugging into different groups means "not connected" until a wire or a part bridges them.

Hold your board so the printed numbers read the right way up. (If your board is a different size from the picture, that is fine — the *pattern* of the printing is the same on all of them.)

### The map

```
        THE BREADBOARD, TOP VIEW  (drawing is a map, not to scale)

   along the top edge:  TWO LONG RAILS
        red  line +  ┌───────────────────────────────────────┐
        blue line −  └───────────────────────────────────────┘
                     every hole on one rail is connected to
                     every other hole on the SAME rail —
                     one long strip, running the board's length

         numbers →    1     2     3     4     5   ...   30
                     ┌─────┬─────┬─────┬─────┬─────┐
   top half    a     │  •     •     •     •     •  │   ┐
   (letters    b     │  •     •     •     •     •  │   │
    a to e)    c     │  •     •     •     •     •  │   ├─ the 5 holes in ONE
               d     │  •     •     •     •     •  │   │  numbered column
               e     │  •     •     •     •     •  │   ┘  (a,b,c,d,e) are ALL
                     └─────┴─────┴─────┴─────┴─────┘      connected together
        CENTRE GAP   ══════════════════════════════   <- a groove down the
                     ┌─────┬─────┬─────┬─────┬─────┐      middle. Holes ABOVE
   bottom half f     │  •     •     •     •     •  │   ┐  it are NEVER
   (letters    g     │  •     •     •     •     •  │   │  connected to holes
    f to j)    h     │  •     •     •     •     •  │   │  BELOW it.
               i     │  •     •     •     •     •  │   │
               j     │  •     •     •     •     •  │   ┘
                     └─────┴─────┴─────┴─────┴─────┘

   along the bottom edge:  TWO MORE RAILS
        red  line +  ┌───────────────────────────────────────┐
        blue line −  └───────────────────────────────────────┘   <- WE USE THIS ONE
                                                                (see below)
```

### The five rules of the map — these are the whole game

1. **Holes are named by letter + number.** Your board prints letters (a–j) down the side and numbers along the top. A hole's name is like a street address: **`f2`** = letter f, number 2. This guide will tell you exact addresses. On your own board the printing may run in the other direction — addresses still work the same way; find the letter row and the number column and read off the hole where they meet.
2. **The 5 holes in one numbered column, on one side of the gap, are connected.** `a2, b2, c2, d2, e2` are one connected group (call it a **strip**). A leg in `a2` and a leg in `e2` are touching, electrically. Same for `f2`–`j2` below the gap.
3. **Different numbers are NOT connected.** Strip 2 and strip 3 are strangers. Nothing flows between them until you plug in a wire or a part (like a resistor) with one leg in each.
4. **The centre gap is a wall.** `e2` and `f2` sit right next to each other, either side of the groove — and are **not** connected. The gap exists so chips can straddle it; for us it just means: top half and bottom half are separate worlds.
5. **Each rail is one very long strip.** Every hole along the blue `−` line at the bottom edge is connected to every other hole on that same line. That makes a rail perfect for something all five LEDs share: the way back to ground. (The red `+` rails exist too — this project does not use them. Leave them empty.)

**One warning about rails:** on *some* boards, each rail is secretly **two halves** — the long strip is split in the middle, so the left half of the rail is not connected to the right half. **How to check yours:** look at the printed blue line along the bottom edge. If the blue line (and usually the numbers beside it) has a visible **gap or break about halfway along**, your rail is split there. If the line runs unbroken from end to end, your rail is whole.

- **Rail whole** → nothing special to do.
- **Rail split** → the ground-return wire from the Uno (Part 5) must land on the **same half** as the LED ground wires — or add one extra jumper wire *along the rail*, one end in a rail hole just before the break and the other end just after it, to bridge the two halves into one. The bridge does nothing else; it just makes the rail whole.

This guide's layout puts all five LEDs' ground wires on the bottom `−` rail, spread along its length (near numbers 5, 11, 17, 23 and 29). If your rail is split around the middle, bridge it as described above, or move the Uno's return wire onto the same half as the furthest LED — the rule that matters is: **every LED's ground jumper, the rail, and the Uno's GND wire must all be one connected chain, with no break in it.**

### The pattern, in one sentence

> **Each LED gets its own little group of numbered strips; every short leg hops to the shared ground rail; the rail has one wire back to the Uno's GND.**

Everything in Parts 3–5 is just that sentence, done five times.

---

## Part 3 — One complete LED, on the map (read this before touching parts)

Before building, see the finished thing once. This is LED 1, the one driven by **Uno pin 8**, placed with exact hole addresses. **You can copy these addresses exactly.** Later, Part 5 repeats the identical pattern at other numbers.

The five parts of LED 1, and where each leg goes:

| # | Part | From | To | Why |
|---|---|---|---|---|
| 1 | Jumper wire | Uno socket **8** | hole **j2** | Brings power from the Uno to strip 2 |
| 2 | Resistor (your checked value) | hole **f2** | hole **f4** | f2 is on strip 2 (same strip as j2 — connected under the plastic), f4 is on strip 4. The resistor *is* the bridge between strip 2 and strip 4. |
| 3 | LED **long leg (+)** | hole **j4** | — | j4 is on strip 4, so the LED's + side connects to the resistor's far end. |
| 4 | LED **short leg (−)** | hole **j5** | — | Strip 5, one strip along from the long leg. Different strip — if both legs were in one strip, they'd already be touching and the LED would be bypassed entirely. |
| 5 | Jumper wire | hole **f5** | the bottom **− rail**, the rail hole nearest number 5 | f5 is on strip 5 (same strip as the short leg). This carries the LED's return current into the shared ground rail. |

Follow the loop with your finger: **Uno 8 → j2 → (under the plastic of strip 2) → f2 → resistor → f4 → (strip 4) → j4 → through the LED → j5 → (strip 5) → f5 → jumper → ground rail → (in Part 5) one wire → Uno GND.** A full circle. Break any link in that circle and the LED stays dark; that fact becomes the troubleshooting method later.

The same thing as a drawing (only the bottom half of the board, where this build lives; the letters run f at the top of this half, nearest the centre gap, down to j at the bottom, nearest the rail):

```
   LED 1 (Uno pin 8) — strips 2, 4 and 5 of the bottom half

   number:        2             4       5
                  │             │       │
   f (near gap) ──[RESISTOR]──────┤       ├──[jumper]──┐
                  f2            f4│       f5            │
                                  │       │             ▼
   j (near rail)──[wire to       [LED+]  [LED−]    GROUND RAIL
                  Uno pin 8]     j4      j5       (bottom −, blue line)
                  j2          long leg  short leg

   Reading it: the wire from Uno pin 8 lands at j2. Strip 2 connects
   j2 to f2 under the plastic. The resistor bridges f2 to f4 (strip 4).
   The LED's long leg at j4 is on strip 4. Its short leg at j5 is on
   strip 5, and the jumper at f5 (same strip) goes down to the rail.
```

**About copying addresses exactly:** the addresses in this guide are one correct arrangement, chosen so the five LEDs never collide with each other. You could shift *everything* five numbers to the right and it would work identically, because what matters is never the absolute numbers — it is **which holes share a strip, and what bridges one strip to the next.** Copy the addresses as written anyway. Exact addresses are checkable ("is the resistor really in f2 and f4?") in a way that "somewhere over there" is not, and checking by address is how we'll debug if an LED misbehaves.

---

## Part 4 — Build LED 1 only, and test it (the whole method, once)

We build **one** LED first, test it, and only then copy it. One LED has five connections; five LEDs have twenty-five. Finding a mistake among five connections is a two-minute job; among twenty-five, it is an evening. Every build of more than one anything works this way.

**USB cable: OUT.** Confirm it before step 1. You will plug it in only at step 7, when told.

**A note on pushing things in:** legs and pins push into holes with gentle finger pressure and a small amount of wiggle. **You should feel** a slight grip as the hole's hidden clip takes the leg. A leg should stand up straight and stay where you put it. If a leg bends instead of going in, it missed the hole — pull it out, straighten it gently with your fingers, and aim again. Never force; bent legs are normal and unbend fine. Jumper wire pins are sturdier than LED and resistor legs.

1. **The wire from the Uno.** Take one jumper wire. Push one end into hole **j2** on the breadboard. Leave the other end loose for now — it plugs into the Uno at step 6.
   - **You should see:** the wire standing in j2, bottom half of the board (letters f–j), at number 2.
2. **The resistor.** Bend nothing yet — look at the resistor's legs. Resistors arrive with long legs; the two legs need to land in **f2** and **f4**, which are two numbers apart. If the legs are too long and splayed, bend each leg down at a right angle, close to the body, so the resistor lies fairly flat with its legs pointing down, spaced to match f2 and f4. Push one leg into **f2**, the other into **f4**. A resistor works **either way round** — there is no + or − on a resistor, so it does not matter which leg goes in which hole.
   - **You should see:** the resistor lying across strips 2 and 4 in row f, bridging them. Its body sits above the holes, legs down.
   - **Check by address:** is one leg truly in the column numbered **2** and the other in the column numbered **4**? Not 3 and 4, not 2 and 5. Two numbers apart, starting at 2.
3. **The LED, long leg.** Push the LED's **long leg (+)** into hole **j4**.
   - **You should see:** the long leg in the bottom row (j), at number 4 — the same strip as the resistor's f4 end.
4. **The LED, short leg.** Push the LED's **short leg (−)** into hole **j5**.
   - **You should see:** the LED standing over numbers 4 and 5, dome up, both legs in row j, one number apart. Its flat rim side faces the number-5 side (the short leg side). If the two legs ended up in the **same** number — both in 4, say — pull the LED out and redo steps 3–4; same-strip legs would bypass the LED completely.
   - LED legs are short and a bit springy; the LED may sit slightly proud or lean a little. That is fine.
5. **The ground jumper for this LED.** Take another jumper wire. Push one end into hole **f5** (strip 5 — the same strip as the short leg, row f at the other end of the strip from j5). Push the other end into the **bottom − rail**: the rail hole nearest number 5, on the blue-line side.
   - **You should see:** a wire from f5 dropping down to the blue `−` line along the bottom edge.
6. **Connect the Uno.** Take the loose end of the wire from step 1 and push it into the Uno socket labelled **8**. (The Uno's digital sockets are the row of holes along one edge of the board, each with its number printed beside it — find the one marked **8**.)
   - Also — the **ground return wire**, the last link of the loop: take one more jumper wire, push one end into **any hole of the same bottom − rail** (pick one near the left end, near number 1, out of the way) and the other end into an Uno socket labelled **GND**. *Without this one wire, the rail goes nowhere and no LED can ever light.* It is the most-forgotten wire in beginner builds, so it gets its own step here instead of at the end.
   - **You should see, before power:** exactly four things plugged in around LED 1 — wire at j2 (running to Uno 8), resistor f2–f4, LED at j4/j5, wire at f5 (running to the rail) — plus the rail's return wire running to Uno GND.
7. **First power test — the built-in chase.** Plug the Uno's USB cable into the Mac.
   - **You should see:** the program already on the Uno (from Stage 1) runs its power-on test: it switches pins 8, 9, 10, 11, 12 on and off in order, once. Only pin 8 has an LED so far, so **you should see your one LED light up once, briefly,** as the chase passes pin 8, then go out. (The later pins chase invisibly — their LEDs don't exist yet.)
   - **If you saw the single blink: the whole loop for LED 1 is physically correct.** Go to step 8.
   - **If you saw nothing:** do not add more parts. Go to the fault checks right after step 9 — with one LED, there are only six suspects.
8. **Command test, from Terminal.** On the Mac: open Terminal, go to the project code folder, and enter the project's Python environment:
   ```
   cd ~/hand-controlled-led/code
   source .venv/bin/activate
   ```
   (Your prompt gains `(.venv)` at the front — that is the sign you're in.) Then send the command that lights exactly one LED:
   ```
   python3 uno_send.py C1
   ```
   - **You should see:** the sender prints the board's receipt, **`count=1`** — and **LED 1 lights and stays lit** while the sender is connected, going out when the command finishes and the connection closes (the board restarts as the port closes; that on-then-off across separate commands is normal, as Stage 1 established).
   - The opposite command:
   ```
   python3 uno_send.py C0
   ```
   - **You should see:** receipt **`count=0`**, and the LED is **off**.
   - (The same test works in the monitor instead: `arduino-cli monitor -p /dev/cu.usbmodem1401 --config baudrate=9600`, type `C1`, Return — LED on; `C0`, Return — off; leave with **Control+C**. Use one method or the other, not both at once: only one program can hold the port.)
9. **LED 1 passes when all three are true:** it blinked once in the power-on chase → `C1` lights it (receipt `count=1`) → `C0` puts it out (receipt `count=0`).

### If LED 1 did not light — the six suspects, in order

Unplug the USB before changing anything, plug back in to re-test. Change **one thing at a time**; changing two things at once destroys the evidence of which one it was.

1. **The LED is in backwards.** The most common beginner fault of all, and harmless. Pull the LED out and put it back with the legs swapped: long leg where the short leg was (long in j5's strip is wrong for our addresses though — instead, rotate the LED so the **long leg is in j4** and the **short leg in j5**, re-checking against step 3–4). Flat rim side toward the short-leg side. Retest.
2. **The ground return wire is missing or on the wrong rail.** Is there really a wire from the bottom `−` rail to an Uno **GND** socket? Is LED 1's f5 jumper in the `−` (blue) rail and not the `+` (red) one right beside it? The two rails sit a hair apart and this mix-up is easy and invisible. Check by eye, hole by hole.
3. **A wire is in the wrong strip.** Read the addresses off your board out loud: resistor **f2 and f4**; LED **j4 and j5**; jumpers **j2** and **f5**. Being off by one number is the second most common fault — a leg in strip 3 instead of 4 connects to nothing at all.
4. **The resistor is a 10 MΩ.** If you skipped the Part 1 check, do it now: power off, pull the resistor out, measure it with the Fluke on Ω. Millions = that's the fault; the LED was never going to show anything through it.
5. **A leg is not actually in its hole.** A leg can slide down *beside* the board's edge of a strip or bend under the board instead of entering. Each leg should stand straight and resist a *gentle* tug. Reseat anything wobbly.
6. **The split rail.** Only if your board's blue line has that middle gap from Part 2: LED 1's ground jumper and the Uno return wire must be on the **same half** of the rail, or bridged. If one is left of the break and the other right of it, the loop is open exactly as if the return wire were missing.

Once LED 1 passes, leave it exactly as it is. It is now your reference copy — the other four are photocopies of it.

---

## Part 5 — Copy the pattern four more times (LEDs 2–5)

**USB cable: OUT again** while you wire. Same rule as before: wire unpowered, test powered.

LEDs 2–5 are LED 1 repeated exactly, shifted along the board and aimed at the next Uno pin each time. Each LED uses strips **M**, **M+2** and **M+3**, where M is its starting number. Here is the complete layout for all five — this table is the whole build:

| LED | Uno pin | Starts at M | Pin wire lands at | Resistor from → to | LED long leg (+) | LED short leg (−) | Ground jumper from |
|---|---|---|---|---|---|---|---|
| 1 | 8 | 2 | **j2** | **f2 → f4** | **j4** | **j5** | **f5** → − rail |
| 2 | 9 | 8 | **j8** | **f8 → f10** | **j10** | **j11** | **f11** → − rail |
| 3 | 10 | 14 | **j14** | **f14 → f16** | **j16** | **j17** | **f17** → − rail |
| 4 | 11 | 20 | **j20** | **f20 → f22** | **j22** | **j23** | **f23** → − rail |
| 5 | 12 | 26 | **j26** | **f26 → f28** | **j28** | **j29** | **f29** → − rail |

The recipe for each new LED, word for word the same as Part 4:

1. Pin wire: one end in **jM**, other end in the Uno socket with that LED's pin number.
2. Resistor: legs in **fM** and **f(M+2)** (either way round).
3. LED long leg (+) in **j(M+2)**; LED short leg (−) in **j(M+3)** — **different numbers, always.**
4. Ground jumper: **f(M+3)** down to the nearest hole of the same bottom **− rail**.

Build **one LED at a time**, and after each one, do the ten-second check before starting the next: read its four addresses off the board and compare with the table row. Then plug the USB in briefly and watch the power-on chase — **each new LED you finish adds one more blink to the chase sequence**, in pin order. Two LEDs built = two blinks in a row at the start of the chase. That running count is your progress meter: if the chase ever shows fewer blinks than LEDs built, the newest one is the suspect, and you know exactly which row of the table to re-check.

The finished board, as a picture:

```
   THE FINISHED BOARD (bottom half shown; top half and + rails unused)

   Uno pins:        8          9          10         11         12
                    │          │          │          │          │
   pin wires →      j2         j8         j14        j20        j26
                    │          │          │          │          │
   resistors →   f2∿∿f4     f8∿∿f10    f14∿∿f16   f20∿∿f22   f26∿∿f28
                          │          │          │          │
   LEDs (+ leg) →        j4         j10        j16        j22        j28
   LEDs (− leg) →        j5         j11        j17        j23        j29
                          │          │          │          │
   ground jumpers →      f5         f11        f17        f23        f29
                          └──────────┴─────┬────┴──────────┘
                                           ▼
                          GROUND RAIL (bottom −, blue line, all one strip)
                                           │
                          return wire ─────┘──► Uno GND socket
```

**One more look at the rail before the final test:** trace the ground chain with your finger — from any LED's short leg, to its f-row jumper, into the rail, along the rail, out the return wire, into GND. If your board has the **split rail** (Part 2), this is the moment it matters most: LEDs 4 and 5's ground jumpers (f23, f29) may sit on the far half of the rail from the return wire. Bridge the break with one extra jumper along the rail, or move the return wire — the chain must be unbroken end to end.

**Checkpoint — you should have plugged in, in total:** 5 pin wires (Uno 8–12), 5 resistors, 5 LEDs (10 legs), 5 ground jumpers, 1 return wire = **21 things** in breadboard holes, plus the 6 Uno-end connections. If your count is short by one wire, history says it will be a ground jumper or the return wire.

---

## Part 6 — The full test (still no camera — commands only)

Plug the USB in and start from the power-on chase.

1. **The chase.** On plugging in, **you should see all 5 LEDs chase in order, once** — 1, 2, 3, 4, 5, like a tiny wave. Five blinks means five complete loops. Fewer blinks = go back to that LED's row in the Part 5 table.
2. **The command table.** In Terminal, in the `code` folder with the venv active, run each command and compare. The LEDs light **in order, from LED 1** — "count" always fills from the left of your row:

   ```
   python3 uno_send.py C0
   python3 uno_send.py C1
   python3 uno_send.py C2
   python3 uno_send.py C3
   python3 uno_send.py C4
   python3 uno_send.py C5
   ```

   | Command | Receipt to expect | LEDs lit |
   |---|---|---|
   | `C0` | `count=0` | none |
   | `C1` | `count=1` | LED 1 |
   | `C2` | `count=2` | LEDs 1–2 |
   | `C3` | `count=3` | LEDs 1–3 |
   | `C4` | `count=4` | LEDs 1–4 |
   | `C5` | `count=5` | all five |

   Each command's light goes out when the sender disconnects, as before — that is the port closing and restarting the board, not a fault. To watch a state *stay*, use the sender's hold mode, e.g. `python3 uno_send.py C3 --hold`, and leave it running while you look; **Control+C** releases it.
   (In the monitor — `arduino-cli monitor -p /dev/cu.usbmodem1401 --config baudrate=9600` — the same table applies: type the command, Return, read the receipt, watch the LEDs; Control+C to leave.)
3. **Pass:** chase shows 5 → every row of the table matches what the board does → the wiring stage is done. What remains in Stage 2 of the plan is only joining the camera program to this same setup — no more wiring.

### Troubleshooting — breadboard edition

Unplug before changing wires; change one thing at a time; re-check by address, not by memory.

| What you see | Most likely cause | Check, in order |
|---|---|---|
| **All five dark, even in the chase** | The loop's shared link is open: usually the **return wire** (rail → GND) missing, in the + rail by mistake, or the split rail unbridged. Or the Uno itself has no power. | Return wire first (both ends, right rail). Then: does the Uno's green ON light show with USB in? Then the rail bridge if yours is split. |
| **One LED dark, others fine** | That LED is backwards, or one of its parts is off by one strip, or its resistor is a 10 MΩ. | Swap that LED's legs round. Read its four addresses against the table. Measure its resistor with the Fluke (Ω, power off). |
| **One LED much dimmer than the rest** | Its resistor is a bigger value than the others (they must all match), or one of its legs is barely seated. | Measure that resistor and compare with a neighbour's. Reseat its legs with a gentle push. |
| **Two LEDs always light together, as a pair** | Two legs that should be on different strips are **sharing one strip** — e.g. LED 2's long leg landed in the same numbered column as LED 1's short leg, or an LED's own two legs share a strip. Electricity cannot tell them apart, so they act as one. | Compare every leg's address against the Part 5 table, pair by pair. The shared number is the error; move the leg that doesn't belong there. |
| **An LED is on when its count says it should be off** | Its pin wire is in the wrong Uno socket (it is hearing another pin's commands), or its long leg shares a strip with a neighbour's long leg. | Check the Uno end: sockets 8, 9, 10, 11, 12 in order, one wire each. Then check for a shared strip on the board. |
| **LEDs light, but in the wrong order** | The pin wires are in the right sockets but in the wrong sequence (e.g. pin 9's wire went to LED 1's position). | Nothing is broken — decide whether you care. To fix: swap the wires **at the Uno sockets only** until chase order matches LED order. |
| **Chase works, but Terminal commands do nothing** | Not a wiring fault — the chase proves the wiring. This is the port: another program (a leftover monitor session) is holding it, or the sender is talking to the wrong port. | Control+C any monitor in any Terminal window; re-run the sender; confirm the port is `/dev/cu.usbmodem1401`. |
| **An LED flickers when the board is touched** | A leg or wire is half-seated and making intermittent contact. | With USB out, reseat that LED's four connections firmly, one at a time. |

*What you just learned:* the breadboard is not a part of the circuit so much as the place where the circuit's connections are *declared* — every strip you chose either joined two things or kept them apart, and the LED row is just the loop from Part 3, declared five times. When the camera program joins in Stage 2, it sends the identical `C0`–`C5` commands you typed here. The lights will not know the difference — and now, neither does your hand: hold up three fingers, and exactly three of the lights you wired will answer.

---

*End of guide. Companion files: `PLAN.md` (the whole project, Stage 2 especially), `code/hand_led_uno/hand_led_uno.ino` (the program on the Uno), `code/uno_send.py` (the command sender used in the tests above).*
