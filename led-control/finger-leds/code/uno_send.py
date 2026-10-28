#!/usr/bin/env python3
"""Send ONE command to the Uno and print EVERYTHING the board answers.

Usage (Terminal, from the code folder, with the .venv active):
    python3 uno_send.py C5
    python3 uno_send.py C0
    python3 uno_send.py B128        (pin 9 brightness, Stage 3)
    python3 uno_send.py C5 --hold   keep the port open until Control+C

How it works, and why (lessons from Oct 25, live):
1. SYNC, DON'T GUESS. Opening the port restarts the Uno; startup time
   varies. Instead of sleeping a fixed time, this sender READS until
   the board itself says 'uno-ready', and only then sends.
2. SHOW, DON'T FILTER. Earlier versions summarised what the board
   said, which hid evidence when a command landed wrong (a sent C5
   kept producing count=0 for a reason not visible from outside).
   Sketch v3 reports every byte it receives ('rx 67 'C''), and this
   sender prints the board's output raw, so one run shows exactly
   what crossed the wire.
3. NOTHING ELSE ON THE WIRE. Typing into a serial monitor forwards
   every keystroke — including shell commands — to the board. This
   sender puts exactly the command's bytes on the wire.

About staying on: an Uno restarts when its USB connection opens, and
on most setups also when it closes; a restart clears the pins, so a
send-and-exit tool can only flash a light. --hold keeps the connection
open so state persists — like the Stage 2 camera program does.

Port defaults to Caitria's Uno; override with --port.
"""

import argparse
import sys
import time

try:
    import serial
except ModuleNotFoundError:
    print("This needs pySerial, which lives in the project's .venv. "
          "Run:  source .venv/bin/activate   first, from the code folder.")
    sys.exit(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", help="e.g. C0..C5 or B0..B255")
    ap.add_argument("--port", default="/dev/cu.usbmodem1401")
    ap.add_argument("--hold", action="store_true",
                    help="keep the port open until Control+C, so the "
                         "commanded state persists (the board restarts "
                         "when the port closes, clearing the pins)")
    args = ap.parse_args()

    cmd = args.command.strip().upper()
    if len(cmd) < 2 or cmd[0] not in "CB" or not cmd[1:].isdigit():
        print("Command should look like C5 or B128 — a letter, then a number.")
        sys.exit(1)

    ser = serial.Serial(args.port, 9600, timeout=0.25)

    # 1) Wait until the board itself says it is listening.
    heard_ready = False
    deadline = time.time() + 8
    while time.time() < deadline:
        raw = ser.readline()
        if raw and b"uno-ready" in raw:
            heard_ready = True
            break
    print("(board said uno-ready — sending now)" if heard_ready
          else "(did not hear uno-ready within 8s — sending anyway)")

    # 2) Send exactly the command's bytes, then print the board raw.
    ser.reset_input_buffer()
    ser.write((cmd + "\n").encode())
    ser.flush()
    deadline = time.time() + 3
    while time.time() < deadline:
        raw = ser.readline()
        if raw:
            print(raw.decode(errors="replace").rstrip())

    # 3) Optionally hold the connection open so the state persists.
    if args.hold:
        print("Holding the port open — the commanded state should "
              "persist now. Control+C to release; the board restarts "
              "when the port closes, so the light goes out then. "
              "That part is expected.")
        try:
            while True:
                raw = ser.readline()
                if raw:
                    print(raw.decode(errors="replace").rstrip())
        except KeyboardInterrupt:
            pass
    ser.close()


if __name__ == "__main__":
    main()
