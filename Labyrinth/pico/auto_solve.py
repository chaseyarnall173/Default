# Auto-solve: tilts the board through the whole maze, START -> 5 hole.
# No sensors: it's a timed plan, so it needs tuning on the real board.
# both black -> pin 38 (GND)   both red -> pin 40 (VBUS)
# outer white -> pin 21 (GP16, left/right)   inner white -> pin 22 (GP17, front/back)
# Board seen with START in the BOTTOM-LEFT corner (you stand at the bottom).
from machine import Pin, PWM
import time

outer = PWM(Pin(16))
inner = PWM(Pin(17))
outer.freq(50)
inner.freq(50)

OUTER_TRIM = 5      # outer servo's 0 is 5 deg off level; flip to -5 if worse
INNER_TRIM = 0      # change if the board isn't level front/back
FLIP_OUTER = False  # True if "RIGHT" moves make the ball go LEFT
FLIP_INNER = True   # True if "BACK" moves make the ball come toward you
TIME_SCALE = 1.0    # all push times x this (ball too slow: 1.2, too fast: 0.8)
STEP_MODE = False   # True: press Enter before every move (for tuning)
SETTLE_S = 0.6      # level pause after each move so the ball stops
RAMP_DEG_S = 120    # how fast the board changes angle

# each move: list of (left/right deg, front/back deg, seconds)
# + = right / back (away from you), - = left / front (toward you)
MOVES = [
    (" 1 RIGHT", [(+5, +0, 0.25), (-5, +0, 0.25)]),
    (" 2 BACK ", [(+0, +5, 0.35), (+0, -5, 0.30)]),
    (" 3 RIGHT", [(+5, +0, 0.30), (-2, +0, 0.40)]),
    (" 4 FRONT", [(+0, -5, 0.35), (+0, +5, 0.30)]),
    (" 5 RIGHT", [(+5, +0, 0.35), (-5, +0, 0.30)]),
    (" 6 BACK ", [(+0, +5, 0.35), (+0, -5, 0.30)]),
    (" 7 RIGHT", [(+5, +0, 0.35), (-2, +0, 0.25)]),
    (" 8 FRONT", [(+0, -5, 0.35), (+0, +5, 0.30)]),
    (" 9 RIGHT", [(+5, +0, 0.65), (-5, +0, 0.10)]),
    ("10 BACK ", [(+0, +5, 1.30), (+0, -5, 0.10)]),
    ("11 LEFT ", [(-5, +0, 0.35), (+5, +0, 0.30)]),
    ("12 FRONT", [(+0, -5, 0.20), (+0, +2, 0.25)]),
    ("13 LEFT ", [(-5, +0, 0.50), (+5, +0, 0.40)]),
    ("14 FRONT", [(+0, -5, 0.25), (+0, +5, 0.25)]),
    ("15 LEFT ", [(-5, +0, 0.80), (+5, +0, 0.10)]),
    ("16 BACK ", [(+0, +5, 1.30), (+0, -5, 0.10)]),
    ("17 RIGHT", [(+5, +0, 0.65), (-5, +0, 0.10)]),
    ("18 FRONT", [(+0, -5, 0.20), (+0, +2, 0.25)]),
    ("19 RIGHT", [(+5, +0, 0.25), (-2, +0, 0.30)]),
    ("20 BACK ", [(+0, +5, 0.45), (+0, -2, 0.10)]),
    ("21 RIGHT", [(+5, +0, 0.35), (-5, +0, 0.30)]),
    ("22 FRONT", [(+0, -5, 0.35), (+0, +5, 0.30)]),
    ("23 RIGHT", [(+5, +0, 0.35), (-5, +0, 0.30)]),
    ("24 BACK ", [(+0, +5, 0.25), (+0, -5, 0.25)]),
    ("25 RIGHT", [(+5, +0, 0.25), (-2, +0, 0.10)]),
    ("26 FRONT", [(+0, -5, 0.25), (+0, +5, 0.25)]),
    ("27 RIGHT", [(+5, +0, 0.45), (-2, +0, 0.10)]),
    ("28 BACK ", [(+0, +5, 0.20)]),
]

now = [0.0, 0.0]


def set_tilt(lr, fb):
    o = -lr if FLIP_OUTER else lr
    i = -fb if FLIP_INNER else fb
    outer.duty_ns(int((1500 + (o + OUTER_TRIM) * 7.4) * 1000))
    inner.duty_ns(int((1500 + (i + INNER_TRIM) * 7.4) * 1000))


def go(lr, fb, seconds):
    """Ramp to the tilt, then hold it for the rest of the time."""
    start = time.ticks_ms()
    dt = 0.01
    while time.ticks_diff(time.ticks_ms(), start) < seconds * 1000:
        step = RAMP_DEG_S * dt
        now[0] += max(-step, min(step, lr - now[0]))
        now[1] += max(-step, min(step, fb - now[1]))
        set_tilt(now[0], now[1])
        time.sleep(dt)


print("LEVEL CHECK: the board should be flat for 5 s.")
print("If it leans left/right, change OUTER_TRIM; front/back, INNER_TRIM.")
go(0, 0, 5)
input("Put the ball on START, then press Enter to run the maze ")

for name, steps in MOVES:
    if STEP_MODE:
        input("next: %s  (Enter) " % name)
    else:
        print(name)
    for lr, fb, s in steps:
        go(lr, fb, s * TIME_SCALE)
    go(0, 0, SETTLE_S)

print("Done - the ball should be in the 5 hole!")
go(0, 0, 1)
