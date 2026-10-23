# Arrow keys tilt the maze.
#   LEFT / RIGHT -> Servo 1, outer board (pin 21, GP16)
#   UP / DOWN    -> Servo 2, inner board (pin 22, GP17)
#   SPACE        -> back to level
# W A S D work too. Each press (or holding the key) tilts 2 degrees more.
# Both red -> pin 40 (VBUS), both black -> pin 38 (GND).
#
# Thonny's shell does NOT send arrow keys, so run this from a terminal:
#   1. In Thonny: save this file onto the Pico as arrow_keys.py, then close Thonny
#   2. In a terminal:   py -m pip install mpremote      (only the first time)
#                       mpremote repl
#   3. Type:  import arrow_keys   and press Enter, then use the arrows
#   Ctrl+C stops it, Ctrl+] leaves mpremote.
from machine import Pin, PWM
import sys
import select
import time

servo1 = PWM(Pin(16))   # outer board, left/right
servo2 = PWM(Pin(17))   # inner board, front/back
servo1.freq(50)
servo2.freq(50)

OUTER_TRIM = 5      # same as auto_solve.py: use the number that makes it level
INNER_TRIM = 0
FLIP_OUTER = False  # True if RIGHT arrow makes the ball go left
FLIP_INNER = True   # True if UP arrow makes the ball come toward you
STEP = 2            # degrees per key press
MAX_TILT = 15       # never tilt more than this (board hits frame at ~16)
SPEED = 90          # degrees per second the board moves


def write(servo, deg, trim, flip):
    if flip:
        deg = -deg
    servo.duty_ns(int((1500 + (deg + trim) * 7.4) * 1000))


def clamp(x):
    return max(-MAX_TILT, min(MAX_TILT, x))


target = [0, 0]      # [left/right, front/back], + = right / away from you
now = [0.0, 0.0]
keys = select.poll()
keys.register(sys.stdin, select.POLLIN)
esc = ""

print("Arrows tilt, SPACE = level, Ctrl+C = stop")
try:
    while True:
        while keys.poll(0):
            c = sys.stdin.read(1)
            if esc == "" and c == "\x1b":
                esc = c
                continue
            if esc == "\x1b" and c in "[O":
                esc += c
                continue
            if esc:                       # arrow key: ESC [ A/B/C/D
                c = {"A": "w", "B": "s", "C": "d", "D": "a"}.get(c, "")
                esc = ""
            c = c.lower()
            if c == "d":
                target[0] = clamp(target[0] + STEP)
            elif c == "a":
                target[0] = clamp(target[0] - STEP)
            elif c == "w":
                target[1] = clamp(target[1] + STEP)
            elif c == "s":
                target[1] = clamp(target[1] - STEP)
            elif c == " ":
                target = [0, 0]
            else:
                continue
            print("left/right %+3d   front/back %+3d" % (target[0], target[1]))

        step = SPEED * 0.01
        for k in (0, 1):
            now[k] += max(-step, min(step, target[k] - now[k]))
        write(servo1, now[0], OUTER_TRIM, FLIP_OUTER)
        write(servo2, now[1], INNER_TRIM, FLIP_INNER)
        time.sleep(0.01)
except KeyboardInterrupt:
    write(servo1, 0, OUTER_TRIM, FLIP_OUTER)
    write(servo2, 0, INNER_TRIM, FLIP_INNER)
    print("stopped, board level")
