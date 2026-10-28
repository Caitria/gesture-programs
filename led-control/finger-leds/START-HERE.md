# START HERE — the short version
## Hand-Controlled LED — MacBook Air or Mac mini, macOS 14.3.1

This is a one-page copy of Part 0 and Stage 0 of PLAN.md. If anything here is unclear, PLAN.md explains the same step in more words.

## A. Open Terminal
1. Press ⌘+Space. Type **Terminal**. Press Return.
2. You should see a window with a line ending in **%**. That means it is ready.
3. Never type the %. Press Return after each command. Control+C stops a stuck command.

## B. Make the project folder (skip if you already did it)
```
pwd
```
Should say `/Users/<your name>`. If not, type `cd` and Return, then `pwd` again.
```
mkdir hand-controlled-led
ls
cd hand-controlled-led
pwd
```
`pwd` should now end with `hand-controlled-led`. `ls` = list, `mkdir` = make folder, `cd` = go into a folder, `cd ..` = go back up one level.

## C. Unzip the project package into it
Download `hand-controlled-led-project.zip` from the chat first (it lands in Downloads). The zip holds a folder with the same name as the one you just made, so unzipping at home fills your folder.
```
cd
ls ~/Downloads
unzip ~/Downloads/hand-controlled-led-project.zip
cd ~/hand-controlled-led
ls
ls code
```
You should see `PLAN.md`, `START-HERE.md`, `code` — and inside `code`: `hand_led.py` and `hand_led_uno`. If `unzip` asks "replace?", type `n` — you already unzipped it once, and the files are there.

## D. Check Python — you need 3.12 specifically
Your Mac's Python is **3.14, which is too new for this project**: the hand-seeing package's ready-made bundles stop at 3.12, so a 3.14 install fails later with a misleading error. Leave 3.14 alone; several Pythons can share one Mac.
```
python3.12 --version
```
Good answer: `Python 3.12.x`. If it says "command not found", install **Python 3.12** from python.org (Downloads → the 3.12 macOS installer, `.pkg`), quit and reopen Terminal, then `cd ~/hand-controlled-led` and check again.

## E. Make a private box for this project's packages, and fill it
A **venv** (virtual environment) is a private box inside the project folder where this project's add-on packages live, so they cannot break, or be broken by, other projects. The box's folder is named `.venv` — the dot makes it **hidden: plain `ls` will not show it. Always check with `ls -a`** (the `-a` means "all, including hidden").
```
cd ~/hand-controlled-led/code
ls -a
```
If `.venv` is already listed, check its Python: `.venv/bin/python --version`. If that says 3.14, delete just that box (check `pwd` ends with `hand-controlled-led/code` first) with `rm -rf .venv`, then make the right one:
```
python3.12 -m venv .venv
ls -a
source .venv/bin/activate
python --version
```
You should see, in order: `.venv` in the `ls -a` list, then your prompt gaining `(.venv)` at the front (that is how you know the box is open), then `Python 3.12.x`.
```
pip install --upgrade pip
pip install mediapipe opencv-python pyserial
```
This takes a few minutes and prints a lot. Success ends with "Successfully installed" and a list of names.

**Every new Terminal session:** the box starts closed. Before running the program in any later session, reopen it with exactly these two lines:
```
cd ~/hand-controlled-led/code
source .venv/bin/activate
```

## F. First run — camera only
Test the camera first in **Photo Booth** (Air: built-in camera. Mac mini: only works if a USB webcam is plugged in).
```
python3 hand_led.py --dry-run
```
Say yes when macOS asks whether Terminal may use the camera. Hold your hand up, palm to the camera, fingers up. Green dots + a finger count in the corner = Stage 0 passed. Press **Q** to quit.

After that, go back to PLAN.md at **Stage 1** (the Uno's built-in light).
