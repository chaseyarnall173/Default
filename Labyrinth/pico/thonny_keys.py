# Keyboard control that works in Thonny's shell.
# Thonny only sends what you type when you press Enter, so:
#   a + Enter = tilt left      d + Enter = tilt right    (Servo 1, outer, GP16)
#   w + Enter = tilt away      s + Enter = tilt toward   (Servo 2, inner, GP17)
#   0 + Enter = level
#   just Enter = do the last move again (hold Enter to keep tilting)
#   ddd + Enter = 3 steps at once, wd + Enter = both at once
# Both red -> pin 40 (VBUS), both black -> pin 38 (GND).
from machine import Pin, PWM
import time

servo1 = PWM(Pin(16))   # outer board, left/right
servo2 = PWM(Pin(17))   # inner board, front/back
servo1.freq(50)
servo2.freq(50)

OUTER_TRIM = 5      # use the number that makes the board level
INNER_TRIM = 0
FLIP_OUTER = False  # True if d makes the ball go left
FLIP_INNER = False  # True if w makes the ball come toward you
STEP = 2            # degrees per letter
MAX_TILT = 15       # board hits the frame at about 16


def write(servo, deg, trim, flip):
    if flip:
        deg = -deg
    servo.duty_ns(int((1500 + (deg + trim) * 7.4) * 1000))


def clamp(x):
    return max(-MAX_TILT, min(MAX_TILT, x))


def move_to(lr, fb):
    """Glide smoothly from the current tilt to the new one."""
    for k in range(1, 21):
        write(servo1, now[0] + (lr - now[0]) * k / 20, OUTER_TRIM, FLIP_OUTER)
        write(servo2, now[1] + (fb - now[1]) * k / 20, INNER_TRIM, FLIP_INNER)
        time.sleep(0.01)
    now[0], now[1] = lr, fb


now = [0, 0]          # [left/right, front/back], + = right / away from you
move_to(0, 0)
last = ""
print("a d = left/right   w s = away/toward   0 = level   Enter = repeat")

while True:
    keys = input("> ").strip().lower() or last
    last = keys
    lr, fb = now
    for c in keys:
        if c == "d":
            lr += STEP
        elif c == "a":
            lr -= STEP
        elif c == "w":
            fb += STEP
        elif c == "s":
            fb -= STEP
        elif c == "0":
            lr, fb = 0, 0
    move_to(clamp(lr), clamp(fb))
    print("left/right %+3d   front/back %+3d" % (now[0], now[1]))
