# Runs on the LAPTOP (not the Pico). Opens a window:
#   HOLD an arrow (or W A S D) = tilt that way, LET GO = back to level
#   hold two keys = diagonal, hold SHIFT too = gentle tilt, SPACE = level
# It sends its own little program to the Pico, so nothing needs copying.
# Close Thonny first, then in PowerShell:   python tilt_control.py
import time
import tkinter as tk

import serial
import serial.tools.list_ports

OUTER_TRIM = 5      # the number that makes the board level
INNER_TRIM = 0
FLIP_OUTER = False  # True if RIGHT makes the ball go left
FLIP_INNER = True   # True if UP makes the ball come toward you
TILT = 8            # degrees when holding an arrow
GENTLE = 3          # degrees when holding SHIFT + arrow
SPEED = 250         # degrees per second the board moves (higher = snappier)
RATE_MS = 20        # send to the Pico every 20 ms (50 times a second)

# the program that runs on the Pico: reads "servo1 servo2" lines
PICO_CODE = b"""
from machine import Pin, PWM
import sys
s1 = PWM(Pin(16))
s2 = PWM(Pin(17))
s1.freq(50)
s2.freq(50)
def w(s, d):
    d = max(-25, min(25, d))
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
now = [0.0, 0.0]                        # [left/right, front/back]

win = tk.Tk()
win.title("Labyrinth tilt")
canvas = tk.Canvas(win, width=300, height=300, bg="white")
canvas.pack()
canvas.create_rectangle(20, 20, 280, 280, width=3)
dot = canvas.create_oval(140, 140, 160, 160, fill="red")
label = tk.Label(win, text="connected on " + port, font=("Arial", 12))
label.pack()


WASD = {"w": "Up", "a": "Left", "s": "Down", "d": "Right"}


def press(e):
    held.add(WASD.get(e.keysym.lower(), e.keysym))


def release(e):
    held.discard(WASD.get(e.keysym.lower(), e.keysym))


def tick():
    size = GENTLE if ("Shift_L" in held or "Shift_R" in held) else TILT
    want = [size * (("Right" in held) - ("Left" in held)),
            size * (("Up" in held) - ("Down" in held))]
    if "space" in held:
        want = [0, 0]
    step = SPEED * RATE_MS / 1000
    for k in (0, 1):
        now[k] += max(-step, min(step, want[k] - now[k]))
    s1 = (-now[0] if FLIP_OUTER else now[0]) + OUTER_TRIM
    s2 = (-now[1] if FLIP_INNER else now[1]) + INNER_TRIM
    pico.write(b"%.1f %.1f\n" % (s1, s2))
    extra = pico.read(pico.in_waiting or 1)
    if extra.strip():
        print(extra.decode(errors="replace"), end="")   # Pico errors
    x, y = 150 + now[0] * 120 / 15, 150 - now[1] * 120 / 15
    canvas.coords(dot, x - 10, y - 10, x + 10, y + 10)
    label.config(text="left/right %+5.1f   front/back %+5.1f"
                 % (now[0], now[1]))
    win.after(RATE_MS, tick)


def close():
    pico.write(b"%.1f %.1f\n" % (OUTER_TRIM, INNER_TRIM))   # level
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
