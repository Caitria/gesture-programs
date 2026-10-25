# Hand-Controlled LED — Computer + Uno Version
### A step-by-step plan, written to teach as you go

**What you end up with:** You hold your hand up to your computer's camera. Hold up three fingers, three lights turn on. Make a fist, they all go out. Later: pinch your fingers apart and a light gets brighter.

**Time:** Part 0 first (Terminal from zero — about 30 minutes, done once). Then one evening for Stages 0–2 (about 2 hours at a careful beginner pace). Stage 3 is 20 extra minutes another night. Stage 4 is a separate session.

**Prepared for you (in this folder):**
- `START-HERE.md` — a one-page copy of Part 0 + Stage 0, for keeping open beside Terminal
- `code/hand_led_uno/hand_led_uno.ino` — the program that goes on the Uno
- `code/hand_led.py` — the program that runs on your computer
- `hand-controlled-led-project.zip` (attached in chat, separate from this folder) — the one download that carries all of the above onto your Mac; Part 0, step 0.4 walks through it

You do not have to write either program. Your job is the wiring, the installing, and the testing. Reading the programs afterwards is where some of the learning is, and both have plain comments.

---

## How it works, in one picture

```
  your hand
     │
     ▼
  WEBCAM ──► COMPUTER ──► a number ──► UNO ──► LEDs
             (Python)     over USB     (sketch)
             sees 21 dots  "C3"        lights 3
             on your hand
```

**The one idea to take away:** the computer and the Uno each do the job they are good at. Seeing a hand takes a lot of computing — the computer does that. Turning lights on is simple and instant — the Uno does that. The two talk over the USB cable in short text messages. That split, *a smart thing sending simple commands to a simple thing*, is how most real gadgets are built.

## Words used in this plan

- **Landmark** — one of the 21 points the software finds on a hand: fingertips, knuckles, wrist. It does not know what a "gesture" is. It only reports where the points are. *We* decide that "five tips higher than their joints" means an open hand.
- **Serial** — text sent one character at a time over the USB cable. The Uno's USB cable is also its serial cable; there is no second cable.
- **Baud rate (9600)** — how fast the serial text goes. Both ends must be set to the same number, or the text arrives garbled. Ours is 9600 at both ends.
- **Sketch** — Arduino's word for a program that lives on the Uno.
- **Pin** — one numbered metal connector on the Uno. A pin set to OUTPUT can be switched to 5 volts (on) or 0 volts (off) by the sketch.
- **PWM pin** — a pin that can fake "half on" by switching on and off thousands of times a second. On an Uno these are marked with a ~ sign: pins 3, 5, 6, 9, 10, 11. Only PWM pins can dim an LED.
- **Breadboard** — the white board with holes for temporary circuits. Holes in each numbered row of 5 are connected to each other underneath. The two long rails down the sides (marked + and −) are connected along their whole length, and are used as shared power and ground.
- **GND (ground)** — the 0-volt return side of the circuit. Every LED's short leg eventually connects back to a GND pin.
- **Resistor, for an LED** — a part that limits how much current reaches the LED so it does not burn out. For this build: **220 Ω or 330 Ω, one per LED.** Ω (ohm) is the unit; bigger number = less current = dimmer.

---

# PART 0 — Terminal from zero
### Read this part slowly. Every step is one small action. Do not skip the "you should see" checks — they are how you know the step worked before you build the next one on top of it.

## 0.1 What Terminal is, and how to open it

**Terminal** is an app on your Mac where you type instructions as text instead of clicking. One typed line is called a **command**. You type a command, press the **Return** key, the Mac does it, and then it waits for the next command. That is all Terminal is — there is nothing else happening behind it.

How to open it:

1. Press **Command (⌘) and Space together**. A search box appears in the middle of the screen. This search is called Spotlight.
2. Type the word **Terminal**.
3. Press **Return**. The Terminal app opens.
4. **You should see:** a plain window, mostly empty, with one line of text at the top. That line ends in a **%** sign, and there is a small blinking block after it. Something like:
   ```
   caitria@MacBook-Air ~ %
   ```
   Your name and the machine's name will differ. That does not matter.
5. The blinking block is the **cursor** — it marks where your typing will appear. The **%** (or a $ on some systems) is called the **prompt**. It means "I am ready, type here."

**Three rules for every command in this whole plan:**
- **Never type the % sign.** It is already on screen. You type only the words after it.
- **Press Return at the end of each command, once.** Nothing happens until you do. A command just sitting typed on the line has not run yet.
- **Spelling, spaces, and capital letters count.** `hand-led` and `Hand-Led` are different names to the Mac. If a command answers with "no such file or directory", the cause is a typo or a wrong folder about 9 times out of 10. Check the typing first, not last.

If a command ever seems stuck and you want it to stop: hold **Control** and press **C**. That cancels whatever is running in Terminal. It harms nothing. (It is Control, not Command — a common mix-up.)

## 0.2 Your first four commands — looking around

Terminal always sits *inside* one folder at a time, the way Finder shows one folder at a time. That folder is called your **working directory**. Four commands run your whole life in Terminal:

| Command | What it stands for | What it does |
|---|---|---|
| `pwd` | **p**rint **w**orking **d**irectory | Tells you which folder you are in |
| `ls` | **l**i**s**t | Lists what is in that folder |
| `mkdir hand-led` | **m**a**k**e **dir**ectory | Creates a new folder called hand-led |
| `cd hand-led` | **c**hange **d**irectory | Moves you into the folder called hand-led |

(Terminal people say "directory" where Finder says "folder". They are the same thing.)

Try them, one at a time:

1. Type `pwd` and press Return.
   - **You should see:** one line like `/Users/caitria`. That is your **home folder** — your personal folder on this Mac, the one with your name on it. Terminal normally starts there.
   - The `/` marks separate folders inside folders, like an address: `Users` is a folder, and inside it is the folder named after you.
2. Type `ls` and press Return.
   - **You should see:** a list of the folders you already know — `Desktop`, `Documents`, `Downloads`, `Pictures`, and others. This is the same home folder, in text instead of icons. If Terminal and Finder disagree about what is in a folder, something else is wrong; they normally never disagree.
3. **Practice run (safe, reversible):** type `mkdir practice-folder`, Return. Then `ls`, Return.
   - **You should see:** `practice-folder` now appears in the list. You just made a folder, from text.
4. Type `cd practice-folder`, Return. Then `pwd`, Return.
   - **You should see:** `/Users/caitria/practice-folder` — you are now *inside* the new, empty folder. Run `ls` — nothing is listed, because the folder is empty. An empty answer is a correct answer here.
5. Type `cd ..`, Return. Then `pwd`, Return.
   - The two dots, `..`, mean "the folder one level up". **You should see:** `/Users/caitria` again.
   - `cd` with a name goes down *into* a folder. `cd ..` comes back up. `cd` on its own, with nothing after it, always takes you straight home from anywhere — a useful rescue if you ever feel lost.
6. Remove the practice folder: type `rmdir practice-folder`, Return. Then `ls`.
   - **You should see:** `practice-folder` is gone. `rmdir` removes an *empty* folder only, which is why it is the safe practice command.

## 0.3 Create the real project folder

We will keep this whole project inside one folder in your home folder, so it is easy to find and easy to delete later if you want rid of it.

1. First check that you are home: type `pwd`, Return. It should say `/Users/<your name>`. If it says anything else, type `cd`, Return, then `pwd` again.
2. Type `mkdir hand-controlled-led`, Return.
   - No message appears. **Silence means success** — Terminal only speaks up when something goes wrong. That takes getting used to.
   - If instead it answers `mkdir: hand-controlled-led: File exists`, that is not a failure: the folder is already there (you made it earlier, or re-ran the step). Carry on to step 3.
3. Check it exists: type `ls`, Return. `hand-controlled-led` should be in the list.
4. Go into it: type `cd hand-controlled-led`, Return, then `pwd`.
   - **You should see:** `/Users/caitria/hand-controlled-led` (with your own name).
5. Look at it in Finder too, to fix the connection between the two views: open **Finder**, click your home folder in the sidebar (or press ⌘+Shift+H). There is `hand-controlled-led`, the folder you just made from text. Same folder, two windows onto it.

**From now on, this plan assumes you are inside `hand-controlled-led` in Terminal.** Every time you open a new Terminal window, it starts at home, so each work session starts with these two commands:
```
cd hand-controlled-led
pwd
```
and the `pwd` check that you landed in the right place.

## 0.4 Get this project's files into that folder

The two programs were written for you by Maude. They live in a file package called `hand-controlled-led-project.zip` that Maude attached in chat. A zip file is just a bag containing other files; we take the files out of the bag, then throw the bag away (or keep it as a spare copy).

1. In the chat, **download `hand-controlled-led-project.zip`**. Downloads from a browser land in the `Downloads` folder — no exceptions unless you changed a setting.
2. In Terminal, go back home first. Note the `~` in these commands: it is a typed shortcut that means "my home folder", so `~/Downloads` means "the Downloads folder inside my home folder", from anywhere.
   ```
   cd
   ls ~/Downloads
   ```
   - **You should see:** `hand-controlled-led-project.zip` in the Downloads list that prints. If it is not there, the download went somewhere else — look in the browser's downloads list for where it put it, and tell Maude that folder name instead of guessing.
3. Take the files out of the zip bag, right where you are standing (home). The zip contains a folder with the *same name* as the project folder you made in 0.3, so the files land inside that folder — the empty folder you made and the folder in the zip simply become one folder:
   ```
   unzip ~/Downloads/hand-controlled-led-project.zip
   ```
   - **You should see:** a few lines naming the files as they come out, ending with names like `hand-controlled-led/code/hand_led.py` and `hand-controlled-led/code/hand_led_uno/hand_led_uno.ino`.
   - If Terminal asks a question ending in `replace?` — you have unzipped this once before. Type `n`, Return, and stop: the files are already there from the first time, and step 4 will prove it.
4. Go to your project folder and check the final layout:
   ```
   cd ~/hand-controlled-led
   ls
   ls code
   ls code/hand_led_uno
   ```
   - **You should see, in order:** `PLAN.md`, `START-HERE.md`, and `code` — then inside `code`: `hand_led.py` and `hand_led_uno` — and inside that: `hand_led_uno.ino`.
   - That nested check is the whole point: if those three `ls` commands show those names, the files are exactly where every later command in this plan expects them to be. If a name is missing, stop and re-do 0.4 — do not press on with a missing file, because later steps will fail with confusing errors that all trace back to this one.

The folder should look like this:

```
hand-controlled-led/            ← you are here (pwd says so)
├── PLAN.md                     ← this plan
├── START-HERE.md               ← a one-page copy of Part 0 + Stage 0
└── code/
    ├── hand_led.py             ← runs on the Mac
    └── hand_led_uno/
        └── hand_led_uno.ino    ← goes on the Uno, using the Arduino app
```

## 0.5 Check Python — and which Python (3.14 is too new for this project)

There can be several Pythons on one Mac at once. They do not interfere with each other. This project needs **one specific one: Python 3.12**, named in commands as `python3.12`. Here is why, in plain words: the hand-seeing package (MediaPipe) is handed out in ready-made bundles, called wheels, made per Python version — and its bundles stop at Python 3.12. **Your Mac's Python is 3.14 (reported Oct 25).** With 3.14, the venv step works, but the MediaPipe install later fails with an error that blames everything except the real cause. Do not debug that failure — it is expected. Use 3.12 for this project and leave 3.14 alone for everything else.

1. Staying inside `hand-controlled-led`, check whether 3.12 is already on your Mac:
   ```
   python3.12 --version
   ```
   - **You should see (the good case):** a line like `Python 3.12.7`. Move on to step 3.
   - **If you see `command not found`:** 3.12 is not installed yet. Do step 2.
   - (For contrast, `python3 --version` on your Mac says 3.14 — that is the too-new one. Both answers can be true at once, because they are different programs with similar names.)
2. **Install Python 3.12** (only if step 1 said "command not found") — either route works; pick one:
   - **Homebrew route (the one Caitria used, Oct 25):** in Terminal, `brew install python@3.12`. When it finishes, run `python3.12 --version` to check. If that still says "command not found" right after a Homebrew install, quit Terminal (⌘+Q), reopen it, go back to the project folder, and check again — a Terminal window only picks up some newly installed programs when it starts. Homebrew puts its programs in `/opt/homebrew/bin` on Apple-silicon Macs and `/usr/local/bin` on Intel Macs; the full-path check, if the short name fails twice, is `/opt/homebrew/bin/python3.12 --version` (or `/usr/local/bin/python3.12 --version` on Intel).
   - **python.org route:** in your browser, go to **python.org**, then **Downloads**, then the **Python 3.12** release for macOS. You want the file called a **macOS installer** (it ends in `.pkg`). Pick 3.12 even though the site will push the newest version at you — scroll to the 3.12 releases if you land on the 3.14 page.
   2. Double-click the downloaded `.pkg` file in Downloads. Follow the installer: Continue, agree, Install, enter your Mac password when asked.
   3. Quit Terminal completely (⌘+Q with Terminal focused) and reopen it. A Terminal window only learns about newly installed programs when it starts.
   4. Get back to your project folder: `cd ~/hand-controlled-led`, then `pwd` to check.
   5. Run `python3.12 --version` again. **You should see:** `Python 3.12.x`.
3. **If you already made a `.venv` with Python 3.14** (you ran the earlier version of Stage 0), delete that one box and remake it in Stage 0 — Stage 0 now uses `python3.12 -m venv .venv`. Deleting a venv harms nothing else: it is a self-contained folder of copies. Stage 0 step 2 includes the exact, checked delete command for this; do not improvise a delete command from memory — deletes are the one Terminal operation that cannot be undone.
4. That is the end of Part 0. You can now open Terminal, find your folder, and know what you are looking at. Everything after this is just more commands of the same kind, one at a time.

---

## Parts check — do this before anything else

### You already own (confirmed from your photos, Oct 24)
- Arduino Uno R3 and its grey USB A–B cable
- Breadboard, rainbow jumper wires
- A resistor assortment — **with one trap, see below**
- A computer with (probably) a webcam — *not confirmed, Stage 0 tests this*
- Fluke multimeter (only needed if an LED does not light)

### The one thing to check in the drawer
Your photos showed a readable bag of **100 × 10 MΩ resistors. Those will not work for LEDs** — 10 million ohms lets through almost no current; an LED on one would look dead. That bag is for other jobs.

Look for **220 Ω, 330 Ω, or 1 kΩ** resistors instead. How to tell: the coloured bands. 220 Ω = red-red-brown. 330 Ω = orange-orange-brown. 1 kΩ = brown-black-red (works, a bit dimmer). You need **5** of roughly the same value.

### Possibly to buy — one small item, nothing else
If LEDs or the right resistors are not in the drawer: **one basic LED assortment pack** (loose 5 mm LEDs in a few colours, usually sold with 220 Ω resistors included). That is the only purchase this plan needs. Do not buy a camera, a sensor, or a different board for this build.

> No purchase is made by this plan. If the pack is needed, that is your call, at your usual electronics source.

---

## Your computer — macOS 14.3.1, Mac mini or MacBook Air (added Oct 25)

You have two machines that could run this, both on macOS 14.3.1 (Sonoma). They are *not* equal for this project, and the difference is the camera:

- **MacBook Air — recommended for this build.** It has a built-in camera at the top of the screen, it is portable to wherever the breadboard is, and there is nothing extra to plug in or buy. Stage 0 works as written.
- **Mac mini — works, but needs a camera first.** A Mac mini has **no built-in camera** (same for Mac Pro and Mac Studio — notebooks and iMacs have one, those desktops do not). On the mini you would need a USB webcam plugged in, or a monitor with a camera in it. If you do have a webcam on the mini already, the mini is fine too — test it in step 2 below and it becomes an equal choice.

**Mac-specific setup, whichever machine you pick:**
1. **Test the camera before any code.** Open **Photo Booth** (in Applications). If you see yourself, the camera works. On the Air that is the end of this test. On the mini, no picture = no camera connected = stop and use the Air, or plug a webcam in.
2. **Camera permission.** The first time the Python program tries the camera, macOS will ask whether **Terminal** may use it. Say yes. If you said no by reflex: **System Settings → Privacy & Security → Camera**, turn Terminal on, then quit and reopen Terminal. The program cannot see around this setting, and "camera opens black / no camera found" on a Mac is this permission about half the time.
3. **Use `python3`, not `python`.** On a current Mac there may be no plain `python` command at all — `python3` is the correct name, not a typo. The three commands you will actually run, all explained step by step in Part 0 and Stage 0, are:
   ```
   python3 hand_led.py --dry-run
   python3 hand_led.py --port /dev/cu.usbmodem101
   ```
   plus the one-time package install, which Stage 0 does inside a private box (a venv) so it cannot disturb anything else on the Mac. If Python itself is not installed, install Python 3.12 from python.org first (Part 0, step 0.5 covers how to check).
4. **The Uno's port name on a Mac** looks like `/dev/cu.usbmodem101` or `/dev/cu.usbmodem1101` — the number varies. You do not have to guess it: in Terminal, `arduino-cli board list` (Stage 1, part 1C) prints the exact name when the Uno is plugged in, and plain `python3 hand_led.py` (no `--port`) tries to find it automatically.
5. **Which chip?** About This Mac (Apple menu → About This Mac) says "Chip: Apple M…" or "Processor: Intel…". You do not need this to start — the install commands are the same — but if the Stage 0 package install fails, the chip line is the first thing I will ask for, so it is worth glancing at.

Everything else in the plan is the same on macOS as elsewhere.

---

## Stage 0 — Computer only: watch it see your hand (30–45 min)
*No Arduino yet. This stage answers: does the camera + software part work at all?*

*Starting point: you finished Part 0. Terminal is open, `pwd` ends with `hand-controlled-led`, and `python3.12 --version` gave you a 3.12.x line (Part 0, step 0.5 — your Mac's default Python is 3.14, which this project does not use).*

1. **Go into the `code` folder.** Type each line, Return after each:
   ```
   cd code
   pwd
   ls
   ```
   - **You should see:** `pwd` ends with `hand-controlled-led/code`, and `ls` lists `hand_led.py` and `hand_led_uno`. If `ls` does not list them, the files did not land right — go back to Part 0, step 0.4.
2. **Make a private box for this project's packages (a venv).** A **venv** — short for virtual environment — is a folder that holds add-on packages for *this project only*, so installing them cannot break anything else on your Mac, and deleting the project later deletes them with it.
   - **First, check whether a box already exists here** (you may have made one with Python 3.14 from the earlier plan):
     ```
     ls -a
     ```
     If `.venv` is **not** in that list, skip straight to the create commands below. If `.venv` **is** there, check which Python is inside it:
     ```
     .venv/bin/python --version
     ```
     - It says **3.12.x** → your box is already right. Skip to step 3.
     - It says **3.14.x** → the box holds the too-new Python. Delete just that box and remake it, with these three commands, one at a time, checking as you go. The middle command is the delete: `rm` means remove, `-rf` means "the folder and everything in it, no asking". It cannot be undone, which is why the `pwd` check comes first — you only run it standing in exactly this folder:
       ```
       pwd
       rm -rf .venv
       ls -a
       ```
       `pwd` must end with `hand-controlled-led/code` before you run the delete. After it, `ls -a` should **no longer** list `.venv`. Now create the right box:
   ```
   python3.12 -m venv .venv
   ls -a
   ```
   - In plain words, that first line says: "Python **3.12**, make a venv (the `-m venv` part) and call the folder `.venv`." The version in the command name is deliberate — see the Python 3.14 note in Part 0, step 0.5. Your other Python stays untouched; several Pythons can live on one Mac and never meet.
   - The dot at the front of `.venv` makes the folder **hidden — plain `ls` will NOT show it**, and neither will Finder. That is why the check command is `ls -a`: the `-a` means "all, including hidden things" (any command can have these little switches, called flags, added after a dash).
   - **You should see:** `ls -a` lists `.` and `..` at the start (every folder contains those two — they mean "this folder" and "the folder above"), and `.venv` in the list. Silence from the first command plus `.venv` in that list = it worked. *(Correction, Oct 25: the first version of this plan said plain `ls` would list `.venv`. That was wrong — a plain `ls` hides dot-names. The plan was at fault, not your typing.)*
3. **Open the box (activate the venv):**
   ```
   source .venv/bin/activate
   ```
   - `source` means "run the instructions in this file". The file's job is to switch this Terminal window over to using the box's Python.
   - **You should see:** your prompt gains `(.venv)` at the front, like `(.venv) caitria@MacBook-Air code %`. That tag is the sign the box is open.
   - **Prove the right Python is in charge:** type `python --version` (inside the box, plain `python` is correct — the box gives the short name to *its* Python). **You should see:** `Python 3.12.x`. If it says 3.14, the box is the old one — go back to step 2 and do the checked delete-and-remake. Do not install anything into a 3.14 box for this project. **Every new Terminal window starts with the box closed** — in future sessions, the first two commands are always `cd ~/hand-controlled-led/code` then `source .venv/bin/activate`, and you check for the `(.venv)` tag before going further. To close the box by hand, the command is `deactivate` — you do not need it; closing the window is enough.
4. **Install the three packages into the box:**
   ```
   pip install --upgrade pip
   pip install mediapipe opencv-python pyserial
   ```
   - `pip` is Python's package installer — now that the box is open, plain `pip` (not `pip3`) is correct, because you are talking to the box's pip. In plain words: `mediapipe` = Google's hand-seeing software, `opencv-python` = the camera software, `pyserial` = the talk-to-the-Uno software.
   - This takes a few minutes and prints many lines. That flood is normal. **Pass:** it ends with a line starting `Successfully installed` followed by a list of names. **Fail:** it ends in red text, usually with `ERROR:` in it — copy the last few lines and bring them to Maude; do not re-run it hoping for a different result.
5. **Run the camera-only test:**
   ```
   python3 hand_led.py --dry-run
   ```
   The first run downloads one model file (the "what a hand looks like" file, about 8 MB) from Google, once, and saves it next to the program. After that it works offline.
6. A window opens showing the camera view, mirrored (move right, it moves right). Hold your hand up, palm facing the camera, fingers pointing up.
   - **Pass:** green dots appear on your fingertips and joints, and the number in the corner counts your fingers — 0 for a fist, 5 for an open hand.
   - Move slowly. Look at which finger it miscounts, if any. The thumb is the usual one.
7. Press **Q** to quit. You are back at the prompt, with `(.venv)` still showing.

**If this stage fails, stop here and fix it here** — every later stage depends on it. See Troubleshooting, items 1–3.

*What you just learned:* the software never sees "a fist". It sees 21 points. The counting rule in the program is simple geometry — a finger counts as "up" when its tip is higher in the picture than the joint below it. That is why a sideways hand miscounts: the rule assumes fingers-up. Real gesture systems are mostly better rules, not better cameras.

---

## Stage 1 — Uno only, all in Terminal: one built-in light, no wiring (about 30 min the first time, most of it downloads)
*No camera logic yet. This stage answers: can the computer command the Uno at all? Every step happens in **Terminal** — no Arduino IDE window is used anywhere in this plan (Caitria's ruling, Oct 25: all instructions for terminal). The IDE app, if it is installed, simply stays closed; nothing in this project needs it.*

**The one tool: `arduino-cli`.** Arduino (the company) publishes two front-ends for the same machinery: the IDE *app*, with windows and buttons, and `arduino-cli`, the same machinery driven by typed commands. This plan uses only the typed one. **A sketch** (Arduino's word for a program) does not care which front-end sends it to the board.

### 1A. Install arduino-cli (5–10 minutes, one time only)
1. Open **Terminal** (⌘+Space, type Terminal, Return).
2. **Install the tool** with Homebrew, the same way Python and other tools were installed:
   ```
   brew install arduino-cli
   arduino-cli version
   ```
   - **You should see:** brew working for a bit, then the version check printing a line like `arduino-cli Version: 1.x.x …`. That line is the proof the tool is installed and runnable.
   - If brew answers that it is *already installed*, that is fine — go on to step 3.
3. **Teach it about Uno boards** (one time only):
   ```
   arduino-cli core update-index
   arduino-cli core install arduino:avr
   ```
   - What these are: the first fetches the current catalogue of board-support packages. The second downloads and installs the **Arduino AVR Boards** package — the definitions and compiler for Uno-type boards. Without it, the compile step later has no idea what an Uno is.
   - **You should see:** downloading progress from the first command; the second runs a few minutes, downloads a few hundred MB on a slow connection, and ends reporting `arduino:avr` installed (or "already installed").
   - **You do not need any other package, library, or manager for this project.** A genuine Uno R3 is covered by this one package.

### 1B. Plug in the Uno and check it woke up (5 minutes)
1. **Find the right cable.** Your Uno's cable is a **USB A–B cable**: one end flat and wide (USB-A, goes to the computer), the other chunkier and almost square with two corners cut off (USB-B, goes to the Uno). It is not a phone cable.
2. **Plug the square USB-B end into the Uno.** One matching socket on the board; it fits one way only; gentle pressure, do not force it.
3. **Plug the flat USB-A end into the computer:**
   - **Mac mini:** USB-A sockets on the back — straight in.
   - **MacBook Air:** recent Airs have only oval **USB-C** sockets, which the flat plug does not fit — use a **USB-C to USB-A adapter or hub** if you have one. No adapter = stop here; the mini is the workaround.
4. **Check the board woke up:** a small green light marked **ON**, lit steadily = the Uno has power. An amber light marked **L** blinking about once a second is also normal — new Unos often run a tiny factory program called Blink that only blinks that light. Our program replaces it in part 1E.
   - **No lights at all:** re-seat both cable ends (and the adapter, on the Air); try another socket. Cable/adapter first, settings later — in that order.

### 1C. Find the Uno's port name (2 minutes)
A **port name** is the computer's name for the cable connection — the address every later command sends to. You never guess it; the tool lists it.
1. In Terminal:
   ```
   arduino-cli board list
   ```
2. **You should see:** a small table. One row shows a port like **`/dev/cu.usbmodem1401`**, type "Serial Port (USB)", board name **Arduino UNO**. (Caitria's machine reported exactly that port on Oct 25; the number at the end varies by socket and machine.)
   - **Write the exact port name down.** The upload and monitor commands in this stage use it, and Stage 2's Python program asks for it too. It stays the same while you use the same USB socket.
   - If the board-name column says Unknown but a `/dev/cu.usbmodem…` port row is present, that row is still the Uno — the commands below name the board explicitly, so this does not matter.
   - **No `cu.usbmodem` row at all:** the fault is physical, not a setting — unplug, run `arduino-cli board list` again (note what's there), plug back in, run it once more. The row that *appears* is the Uno. If it never appears: cable or Air adapter (part 1B), in that order.

### 1D. Check the program text — compile (2 minutes)
1. In Terminal, this one line (the sketch *folder* is the argument, not the file):
   ```
   arduino-cli compile --fqbn arduino:avr:uno ~/hand-controlled-led/code/hand_led_uno
   ```
   - New word: **`--fqbn`** is how this tool spells "which board" (Fully Qualified Board Name). `arduino:avr:uno` = Arduino, AVR family, plain Uno. **Compile** means: translate the sketch text into machine code for the Uno, on the computer, *without sending anything yet* — the equivalent of spell-checking a letter before posting it.
   - A fact about the sketch itself, so its address makes sense: the ending **.ino** is Arduino's file type, and a sketch file must sit inside a folder with *exactly the same name* — `hand_led_uno.ino` inside the `hand_led_uno` folder. The zip built it that way on purpose; do not rename or move either one.
2. **You should see:** a line beginning **`Sketch uses … bytes`** of program storage space, and nothing in red. That is "compiles clean".
   - If it ends in error text instead: the problem is in the program text or the folder path — copy the last few lines exactly for Maude; do not edit the sketch by guessing.

### 1E. Send the program to the Uno — upload (2 minutes)
1. In Terminal, using *your* port name from part 1C (the example shows Caitria's):
   ```
   arduino-cli upload -p /dev/cu.usbmodem1401 --fqbn arduino:avr:uno ~/hand-controlled-led/code/hand_led_uno
   ```
2. **You should see:** a few lines of programmer output ending **without errors**, and the Uno's small lights flickering while the data moves. It takes a few seconds. Afterwards the board restarts itself and runs the new program from the top: its first act is switching pins 8–12 on and off in a chase (nothing is wired to them yet, so you see nothing), then it prints its hello (seen in part 1F) and waits for commands.
   - **Why compile and upload are separate steps** even though upload compiles again anyway: they split faults. Compile fails = program text. Compile passes, upload fails = cable, port, or another program holding the port. That split is worth the extra line every time something goes wrong.
   - **If upload ends in red error text:** read the last line. `can't open device` / port wording = the port name is wrong here, the cable moved, or another tool is holding the port (a leftover monitor session is the classic one — find that Terminal window and Control+C out of its monitor first). Fix that one thing and run the upload line once more. Failing twice in a row = bring Maude the exact lines, don't keep re-running.

### 1F. Test it by typing at it — the monitor (5 minutes)
**Monitor** is the Terminal way to hold a two-way text conversation with the Uno over the same cable: what you type goes to the board, what the board prints appears under it.
1. In Terminal, with your port name:
   ```
   arduino-cli monitor -p /dev/cu.usbmodem1401 --config baudrate=9600
   ```
   - **Baud** is the conversation speed; both ends must match, and our sketch speaks 9600. A mismatch shows up as gibberish characters, which is a settings mismatch, not a breakage.
2. **First proof:** opening the monitor restarts the Uno (the connection does that), and our program prints its hello as it starts.
   - **You should see:** the word **`uno-ready`**. That word travelled *from the board to you* — proof the cable carries text board-ward already.
3. **Send command one:** type exactly `C1` and press Return.
   - **You should see two things:** the board prints back **`count=1`** (its receipt — new in sketch v2, it answers every command with what it did), and the small amber LED on the board marked **L** lights up and stays lit.
   - Timing note: a reply may take up to about a second after Return. That is expected, not a hang — see "why v2" below.
4. **Send command two:** type `C0`, Return.
   - **You should see:** the board prints **`count=0`**, and the **L** light goes out.
5. **Send command three:** type `C5`, Return.
   - **You should see:** **`count=5`** printed, and **L** lights again. The rule built into the program: the built-in light stands for "at least one finger", so C1–C5 all light it and only C0 puts it out. The difference between 1 and 5 fingers needs the wired LEDs of Stage 2.
   - Try C3, C2, C0 in any order too — every command gets its printed receipt and the light obeys C0 vs the rest.
6. **Get out of the monitor: Control+C.** You return to the ordinary Terminal prompt.
   - **This exit matters:** while the monitor runs, it *holds the port*. A monitor left running in some Terminal window is the main cause of "port busy" failures in Stage 2. One monitor at a time, and out when done.
7. **If typing into the monitor gives scrambled or missing receipts** (seen live, Oct 25): the cause is built into what a monitor *is* — while it runs, **every keystroke in that window goes to the board**, including shell commands typed there. The board then parses any `C`/`B` letters and following numbers out of those lines as commands (a port name's `1401` becomes `count=5` after the C-rule trims it to range; a `timeout=3` becomes `count=3`; a stray `b` becomes `bright=0`). Receipts arrive late and wrong, and the shell never runs what you typed. Rules that prevent it: **Control+C out of the monitor before typing anything meant for the shell**, and for a clean one-command test use the purpose-built sender in the project instead of typing — it puts exactly the command's bytes on the wire, waits out the board's restart, discards startup noise, and prints the board's answer:
   ```
   cd ~/hand-controlled-led/code
   source .venv/bin/activate
   python3 uno_send.py C5
   ```
   How the sender avoids the restart trap: it does not guess timings — it **listens until the board itself says `uno-ready`**, sends only then, **checks the receipt matches the command**, and resends up to 3 times if it doesn't, saying which attempt landed. (A fixed "wait 2 seconds" version lost bytes across the board's restart and got `count=0` back for a `C5` — seen live Oct 25; a command's letter can reach the still-starting board while its digit is eaten by the bootloader.) **You should see:** `(board said uno-ready — it is listening)` then exactly **`count=5   (attempt 1)`** — attempt 2 or 3 is also a pass; the sender is closing its own loop — and the **L** light on. `python3 uno_send.py C0` → `count=0`, light off. (The sender defaults to Caitria's port `/dev/cu.usbmodem1401`; another port goes in as `python3 uno_send.py C5 --port /dev/cu.usbmodemXXXX`.) One file-handling trap, also seen live: if a command-line option like `--hold` is rejected as "unrecognized arguments", the copy on your machine is an older download — browsers save a second download of the same name as `uno_send (1).py` instead of replacing the first, so a `cp` of the plain name copies the *old* file. `ls -t ~/Downloads/uno_send*.py | head -1` prints the newest one; copy that path instead.

**Why sketch v2 (Oct 25):** v1 waited for a specific "end of line" character after each command before acting. Terminal tools differ in what, if anything, they add when you press Return — so commands could arrive complete yet never be acted on, silently. V2 reads the letter and then the number with a brief wait (`Serial.parseInt()`) and needs no ending character at all; it also prints a receipt (`count=1`) for every command, so a working board *says* so. The Python camera program sends the same `C` commands and is unaffected — it already ended its lines, and v2 accepts those too.

**About a light that flashes but does not stay on (seen live, Oct 25):** an Uno **restarts itself whenever its USB connection opens, and on most setups when it closes too**. A restart clears every pin — so a test tool that opens the port, sends one command, and exits will show the L light come on and then go out as the tool closes the port. That on-then-off is the connection cycling, not the board disobeying. Two related sights, both normal: a few quick L blinks right when a connection opens are the board's bootloader saying hello during the restart; and in the monitor, L stays as commanded only while the monitor stays open. **The persistence check:** use the sender's hold mode, which keeps the port open like the Stage 2 camera program does the whole time it runs —
```
python3 uno_send.py C5 --hold
```
**You should see:** `count=5`, and L lit **steadily, for as long as the sender runs**. Control+C ends it, the board restarts as the port closes, and L goes out — expected, and itself a second proof the light follows the connection's commands.

**Stage 1 pass, all three facts true:** upload ended without errors → the monitor showed `uno-ready` → `C1`/`C0` switch the board's **L** light (and its printed receipts match) on command, with `C5 --hold` keeping L steadily lit while the port is held open.

*What you just learned:* you sent the exact messages the Python program will send later — `C` for count, followed by a number. The Uno does not know or care whether a person or a program typed them.

---

## Stage 2 — Wire 5 LEDs, then join the two halves (your pace — LED 1 is the slow one; LEDs 2–5 are photocopies)

**The wiring steps for this stage live in `BREADBOARD-GUIDE.md`** — the visual companion written for this stage: breadboard map, every leg in a named hole, one LED built and tested first, then the pattern copied four times. What follows here is the short version and the tests; if any line below and the guide ever seem to differ in detail, the guide's hole addresses are the ones to follow.

### Wiring — do this with the Uno UNPLUGGED
Unplug USB first. Wiring while powered is how pins get shorted.

**Nothing plugs into the Uno except jumper wires.** The LEDs and resistors plug into the **breadboard**; the Uno reaches the breadboard through jumper wires (one into each Uno pin socket). Each LED is the same loop:

```
Uno pin 8 ──► 220Ω resistor ──► LED long leg (+)    LED short leg (−) ──► GND rail
Uno pin 9 ──► 220Ω resistor ──► LED long leg (+)    LED short leg (−) ──► GND rail
Uno pin 10 ──► 220Ω resistor ──► LED long leg (+)   LED short leg (−) ──► GND rail
Uno pin 11 ──► 220Ω resistor ──► LED long leg (+)   LED short leg (−) ──► GND rail
Uno pin 12 ──► 220Ω resistor ──► LED long leg (+)   LED short leg (−) ──► GND rail
Uno GND pin ───────────────────────────────────────────────► GND rail (one wire)
```

Vocabulary that matters here (the guide's Part 2 teaches it with the map): a **strip** is the group of 5 connected holes under one number on one side of the breadboard's centre gap. An LED's two legs must land in **different strips** — legs in the same strip are already connected under the plastic, which bypasses the LED entirely. **Long leg = +, short leg = −**; if legs were ever trimmed even, the flat side of the plastic rim is the − side.

The guide's exact layout, in one line per LED (pin wire → resistor → long leg → short leg → ground jumper): **LED 1, pin 8:** j2, f2→f4, j4, j5, f5→rail. **LED 2, pin 9:** j8, f8→f10, j10, j11, f11→rail. **LED 3, pin 10:** j14, f14→f16, j16, j17, f17→rail. **LED 4, pin 11:** j20, f20→f22, j22, j23, f23→rail. **LED 5, pin 12:** j26, f26→f28, j28, j29, f29→rail. Plus the one wire everyone forgets: **the − rail back to a Uno GND socket** — without it, nothing lights.

**Split-rail check (new — older versions of this plan missed it):** some breadboards' long rails are split in the middle (look for a gap in the printed blue line). On such a board, every ground jumper and the GND return wire must sit on the **same half** of the − rail, or be bridged with a short jumper across the split — otherwise some LEDs have no return path and stay dark for no visible reason. The guide's Part 2 shows how to check yours.

### Test the wiring before the camera joins in
6. Plug the Uno back in. It runs its power-on test: **the wired LEDs should chase in order, once** (one blink per finished LED — with only LED 1 built, exactly one blink).
   - One LED dark: turn that LED around (it was probably in backwards) and retest. Still dark: check that LED's resistor is not a 10 MΩ one — measure it with the Fluke on the **Ω setting, power off** (the guide's step 1.3 shows how) — then re-check its strip addresses against the table above, out loud, hole by hole.
7. Test by command from Terminal, either way (one at a time):
   - **Monitor:** `arduino-cli monitor -p /dev/cu.usbmodem1401 --config baudrate=9600`, type `C3` → **exactly 3 LEDs**, board prints `count=3`. `C0` → none. `C5` → all 5. **Control+C** out before the next step, or the port stays held.
   - **Sender:** `python3 uno_send.py C3` from the code folder with the venv active. Add **`--hold`** (`python3 uno_send.py C5 --hold`) to make a state stay on screen-and-board while you look — without it, the LEDs go out when the sender disconnects and the board restarts, which is expected behaviour, not a failure.

### Join the halves
8. In Terminal, in the `code` folder, with the venv active:
   ```
   python3 hand_led.py --port /dev/cu.usbmodem1401
   ```
   That is the port your machine reported in Stage 1; if it ever changes (different USB socket), `arduino-cli board list` shows the current one. (Plain `python3 hand_led.py` with no `--port` also tries to find the Uno by itself.) **Camera:** if Stage 0 needed a `--camera` number on your Mac (it did — camera 0 was the Immersed virtual camera), add the same number here, for example `python3 hand_led.py --port /dev/cu.usbmodem1401 --camera 1` with your number in place of 1.
9. Wait 2 seconds after it connects — opening the port restarts the Uno, and commands sent during those 2 seconds are lost. The program already waits for you.
10. Hold your hand up to the camera.
    - **Pass — you are done with the main build:** fist = all off, 3 fingers = 3 LEDs, open hand = all 5, live as you move.

*What you just learned:* the LED does not care that a camera is involved. The Uno received `C3` exactly as it did when you typed it. Replacing the typer is the whole trick — a button, a timer, or another computer could send the same messages.

---

## Stage 3 — Pinch to dim (20 min, another night is fine)
*One extra idea, using the one LED on a PWM pin.*

1. Run: `python3 hand_led.py --port <your port> --pinch`
2. Hold your hand up. Bring thumb tip and index fingertip together, then slowly apart.
   - **Pass:** the middle LED (pin 9) gets dimmer as you pinch closed, brighter as you open.
   - Pin 9 is used because it is a PWM pin (~ sign). Pin 8 or 12 cannot do this at all — on those, "half brightness" is not a thing the hardware can express.
3. Notice the lag and the steps. The program measures the pinch distance, divides it by the size of your hand in the picture (so moving closer to the camera does not fake a wider pinch), and only sends a new brightness when it changes by a real step.

---

## Stage 4 — Optional finale: hand up, EL sign lights (separate session)
*Do not fold this into the first evening.*

Idea: instead of (or as well as) the 5th LED, the Uno switches one relay channel, and the relay switches the **battery side** of an EL-wire inverter. Hand up → sign glows. Hand down → dark.

Safety rules that do not bend for this stage:
- The relay switches **battery/USB low voltage only — never mains, never a lamp, never the spliced mains cord on the Pi 3 relay rig.**
- Switch the EL inverter's **DC battery input only**. Its output side is high-voltage AC at low current; respect the insulation and reseal any cut EL end.
- Relay coils are powered from the Uno's 5 V, not driven directly by a signal pin alone beyond the module's own input — use the relay module's input pins as designed.
- Build and test this stage with batteries only, on the bench, before anything is mounted.

---

## Gesture cheat sheet (v1, exactly what the program understands)

| You do | Program sends | LEDs do |
|---|---|---|
| No hand in view | C0 | All off |
| Fist | C0 | All off |
| 1 finger up | C1 | 1 on |
| 2, 3, 4 fingers | C2 / C3 / C4 | 2 / 3 / 4 on |
| Open hand | C5 | All 5 on |
| Pinch open/close (Stage 3) | B0–B255 | Middle LED dims/brightens |

Not in v1, on purpose: two hands, sideways hands, signs that need finger *identity* beyond thumb-vs-fingers, anything while the hand is moving fast. Each is a better counting rule, added later if you want it.

---

## Troubleshooting — in the order faults actually happen

1. **"Port busy" / program cannot open the port.** Something else is holding it — almost always a monitor session still running in another Terminal window (or the Python program, if it is running). Find it and end it: **Control+C** in the window running the monitor. Only one program may use the port at a time.
2. **Camera window never opens, or opens black.** Another app (Zoom, a browser tab) is holding the camera, or the operating system has not given your terminal camera permission. Close the other app; check the permission; re-run.
3. **No green dots on your hand.** Lighting. Face a light source so your hand is lit, keep your whole hand in frame, palm to the camera, fingers up, hand not too close. A hand half out of frame will not track.
4. **Count flickers between 2 and 3.** Normal in v1 — a finger on the borderline of the up/down rule. Hold gestures a fraction longer; the program already ignores changes faster than 50 ms. A steadier light helps more than any code change.
5. **Thumb counted when it should not be (or the reverse).** The thumb uses a different rule (distance from the pinky base) because it moves sideways, not up. It is the weakest rule in the program and disagrees with different hands. This is a known v1 limit, not a wiring fault.
6. **No LEDs light, built-in LED does.** The missing GND-rail wire (Stage 2, step 5), or LEDs in backwards, or 10 MΩ resistors in the path. Check in that order.
7. **One LED very dim.** Its resistor is a much bigger value than the others — read its bands, or measure it with the Fluke with the power off.
8. **Commands work from the Terminal monitor but not from Python.** Wrong port in the `--port` argument, or baud mismatch. Both ends are 9600 in the supplied code; if you changed one, change the other.
9. **First command after starting Python is ignored.** The 2-second reset wait was skipped by an edit, or the Uno was mid-restart. Wait, then move your hand — the next change sends again.
10. **`uno-ready` prints in the monitor, but typed commands do nothing — no light, no reply.** Two possible causes, in order. (a) *The board is still running sketch v1* (the Oct 25 fault): v1 waited for a newline character after each command, and Terminal tools differ in what they send for Return, so complete commands could be silently ignored. Fix: make sure the current `hand_led_uno.ino` (v2 — its top comment says "How commands are read (v2, Oct 25)") is the file in your project folder, and re-run Stage 1's compile and upload. V2 needs no line ending and prints a receipt (`count=1`) for every command it acts on. (b) *The monitor isn't forwarding your typing at all:* run the one-line Python sender in Stage 1, part 1F step 7 — if it prints `count=1` and lights L, the board and cable are proven good and only the monitor's typing path is at fault; keep using the sender for this test, or tell Maude. If receipts print but the L light never changes, the board is receiving commands and acting on pin 13 without a visible result — re-check that you are looking at the small LED marked **L** (not the green ON light, which never changes).
11. **The L light (or a wired LED) flashes on a command, then goes out instead of staying on.** The board was restarted by its connection cycling: the Uno restarts when the USB port opens, and usually when it closes, and a restart clears all pins. A send-and-exit tool therefore can only ever produce a flash. It is not a wiring or code fault. Prove persistence with a holder: `python3 uno_send.py C5 --hold` (Stage 1) keeps the port open and L stays lit until Control+C; the Stage 2 camera program holds the port open for its whole run, which is why commanded states persist there. Quick blinks of L right at connect time are the bootloader during that same restart — also normal.
12. **The camera window opens, but shows another app's picture — e.g. an orange logo reading "Please Launch Immersed App" (seen live, Oct 25).** Nothing is broken, and most of Stage 0 has actually passed: the packages installed, the program ran, the window opened, and "fingers: 0" is the correct answer for that picture. What happened: your Mac has more than one "camera" as far as programs are concerned. **Immersed** (a virtual-desktop app) installs a **virtual camera** — a pretend camera that other programs can pick like a real one — and it was camera number 0, the default the program asks for. Because the Immersed app is not running, its pretend camera just shows that "please launch" card, the way a TV shows a test card. Fix: use the updated `hand_led.py` (Oct 25, adds `--camera`), quit with Q, and re-run with the next camera number — `python3 hand_led.py --dry-run --camera 1`, then `--camera 2` if 1 is also not you. Your real camera (the Air's built-in one, or a USB webcam on the mini) is one of those numbers. Note which number is you — every later run in this project should use that same `--camera N`. Do *not* fix this by launching Immersed: that would make the pretend camera show a virtual desktop, which is still not your hand.

---

## Privacy note
The camera feed is processed on your own computer, frame by frame, and is never saved or uploaded by this program. The only download is the one-time hand model file in Stage 0. If the camera being on bothers you later, Stage 4's relay circuit can be driven instead by a $5-class gesture sensor with no camera at all — a different plan, same Uno and LEDs.

## Sources and further reading (checked Oct 25, 2026)
- Google AI Edge — Hand Landmarker Python API (the current Tasks API this plan uses; `detect_for_video` with increasing timestamps): https://ai.google.dev/edge/api/mediapipe/python/mp/tasks/vision/HandLandmarker?authuser=1
- The hand model file the program downloads once: https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
- Controlling an LED with Python (pySerial, the same send-a-character pattern, worked slowly): https://problemsolvingwithpython.com/11-Python-and-External-Hardware/11.03-Controlling-an-LED/
- MediaPipe's own older Hands example (21 landmarks, index fingertip = landmark 8, thumb tip = landmark 4): https://github.com/google-ai-edge/mediapipe/blob/v0.8.4/docs/solutions/hands.md

*Note on versions: older tutorials online mostly use MediaPipe's retired `mp.solutions.hands` shortcut. This plan deliberately uses the current Hand Landmarker Tasks API, so the code should not break the next time the old shortcut is removed from a release. If you follow another tutorial and its first lines look different from `hand_led.py`, that is why.*

---

## What I need from you to run this with you live
1. ~~Which computer / operating system~~ — **answered Oct 25: macOS 14.3.1, Mac mini or MacBook Air.** Recommendation above: the Air, unless the mini already has a webcam on it.
2. The drawer check: do you have 5 LEDs and 5 resistors that are *not* the 10 MΩ bag?
3. If you do use the mini: is a webcam plugged into it? (Photo Booth answers this in 10 seconds.)
4. Optional, only if the install fails: the chip line from About This Mac (Apple M… or Intel…).

Everything else is in this folder, ready to go.
