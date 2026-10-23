# Runs on the LAPTOP (not the Pico). Opens a window:
#   HOLD an arrow (or W A S D) = board keeps tilting slowly that way
#   LET GO = board stays where it is
#   hold two keys = diagonal, hold SHIFT too = extra slow (fine control)
#   SPACE = glide back to level
#   ENTER = "the board is level right now" (saves it as the new level)
# It sends its own little program to the Pico, so nothing needs copying.
# Close Thonny first, then in PowerShell:   python tilt_control.py
import json
import os
import time
import tkinter as tk

import serial
import serial.tools.list_ports

OUTER_TRIM = -5     # servo angle that makes the board level (ENTER sets it)
INNER_TRIM = 0
FLIP_OUTER = False  # True if RIGHT makes the ball go left
FLIP_INNER = True   # True if UP makes the ball come toward you
RATE = 12           # degrees per second while holding a key
SLOW_RATE = 4       # degrees per second while holding SHIFT + key
MAX_TILT = 15       # furthest from level (board hits the frame at ~16)
SMOOTH = 0.15       # seconds the board takes to catch up (bigger = calmer)
RATE_MS = 20        # send to the Pico every 20 ms (50 times a second)

TRIM_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "tilt_trim.json")
if os.path.exists(TRIM_FILE):
    OUTER_TRIM, INNER_TRIM = json.load(open(TRIM_FILE))

# the program that runs on the Pico: reads "servo1 servo2" lines
PICO_CODE = b"""
from machine import Pin, PWM
import sys
s1 = PWM(Pin(16))
s2 = PWM(Pin(17))
s1.freq(50)
s2.freq(50)
def w(s, d):
    d = max(-30, min(30, d))
    s.duty_ns(int((1500 + d * 7.4) * 1000))
while True:
    try:
        a, b = sys.stdin.readline().split()
        w(s1, float(a))
        w(s2, float(b))
    except ValueError:
        pass
"""


def find_pico():
    for p in serial.tools.list_ports.comports():
        if p.vid == 0x2E8A:             # Raspberry Pi's USB id
            return p.device
    raise SystemExit("Pico not found - plug it in and close Thonny")


port = find_pico()
pico = serial.Serial(port, 115200, timeout=0)
pico.write(b"\r\x03\x03")               # stop whatever is running
time.sleep(0.2)
pico.write(b"\r\x01")                   # raw mode, for sending code
time.sleep(0.3)
pico.reset_input_buffer()
for i in range(0, len(PICO_CODE), 256):
    pico.write(PICO_CODE[i:i + 256])
    time.sleep(0.01)
pico.write(b"\x04")                     # run it
time.sleep(0.3)
if b"OK" not in pico.read(100):
    print("Pico didn't answer - unplug it, plug it back in, try again")

held = set()
target = [0.0, 0.0]                     # where you've steered to
now = [0.0, 0.0]                        # where the board is (smoothed)
trim = [OUTER_TRIM, INNER_TRIM]

win = tk.Tk()
win.title("Labyrinth tilt")
canvas = tk.Canvas(win, width=300, height=300, bg="white")
canvas.pack()
canvas.create_rectangle(20, 20, 280, 280, width=3)
canvas.create_line(150, 20, 150, 280, fill="#ccc")
canvas.create_line(20, 150, 280, 150, fill="#ccc")
dot = canvas.create_oval(140, 140, 160, 160, fill="red")
label = tk.Label(win, font=("Arial", 12))
label.pack()
tk.Label(win, text="hold arrows = tilt   SHIFT = slow   SPACE = level\n"
                   "ENTER = save this as level",
         font=("Arial", 10)).pack()

WASD = {"w": "Up", "a": "Left", "s": "Down", "d": "Right"}


def press(e):
    key = WASD.get(e.keysym.lower(), e.keysym)
    held.add(key)
    if key == "Return":                 # this position is level
        for k in (0, 1):
            trim[k] = servo_deg(k)
            target[k] = now[k] = 0.0
        json.dump(trim, open(TRIM_FILE, "w"))
        print("saved level: OUTER_TRIM = %.1f  INNER_TRIM = %.1f" % tuple(trim))


def release(e):
    held.discard(WASD.get(e.keysym.lower(), e.keysym))


def servo_deg(k):
    flip = FLIP_OUTER if k == 0 else FLIP_INNER
    return (-now[k] if flip else now[k]) + trim[k]


def tick():
    dt = RATE_MS / 1000
    slow = "Shift_L" in held or "Shift_R" in held
    rate = (SLOW_RATE if slow else RATE) * dt
    push = [("Right" in held) - ("Left" in held),
            ("Up" in held) - ("Down" in held)]
    for k in (0, 1):
        if "space" in held:
            target[k] = 0.0
        target[k] = max(-MAX_TILT, min(MAX_TILT, target[k] + push[k] * rate))
        now[k] += (target[k] - now[k]) * min(1.0, dt / SMOOTH)
    pico.write(b"%.2f %.2f\n" % (servo_deg(0), servo_deg(1)))
    extra = pico.read(pico.in_waiting or 1)
    if extra.strip():
        print(extra.decode(errors="replace"), end="")   # Pico errors
    x, y = 150 + now[0] * 130 / MAX_TILT, 150 - now[1] * 130 / MAX_TILT
    canvas.coords(dot, x - 10, y - 10, x + 10, y + 10)
    label.config(text="left/right %+5.1f   front/back %+5.1f   (level trim %+.1f, %+.1f)"
                 % (now[0], now[1], trim[0], trim[1]))
    win.after(RATE_MS, tick)


def close():
    pico.write(b"%.2f %.2f\n" % (trim[0], trim[1]))   # level
    time.sleep(0.1)
    pico.write(b"\x03\x02")             # stop the Pico code, normal mode
    pico.close()
    win.destroy()


win.bind("<KeyPress>", press)
win.bind("<KeyRelease>", release)
win.protocol("WM_DELETE_WINDOW", close)
win.focus_force()
tick()
win.mainloop()
