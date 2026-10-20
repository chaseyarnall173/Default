# Ball paths on the open board (no inner walls yet): the board tilts so the
# ball rolls along the rim walls in a square, then corner to corner.
# both black -> pin 38 (GND)   both red -> pin 40 (VBUS)
# outer white -> pin 21 (GP16, left/right)   inner white -> pin 22 (GP17, front/back)
from machine import Pin, PWM
import time

outer = PWM(Pin(16))
inner = PWM(Pin(17))
outer.freq(50)
inner.freq(50)

TILT = 6           # how far to lean (more = faster ball, more bouncing)
ROLL_S = 2.0       # seconds to wait while the ball rolls one side
RAMP_S = 0.4       # seconds to change the lean (smooth, so it doesn't fling)
FLIP_OUTER = False # if the ball goes LEFT when it should go RIGHT, set True
FLIP_INNER = False # if the ball goes FRONT when it should go BACK, set True

now = [0.0, 0.0]   # current lean: [left/right, front/back]


def angle(servo, deg, flip):
    if flip:
        deg = -deg
    servo.duty_ns(int((1500 + deg * 7.4) * 1000))


def lean(right, back, label):
    """Lean toward right/back (+1), left/front (-1) or level (0)."""
    print(label)
    start = list(now)
    steps = max(1, int(RAMP_S / 0.02))
    for k in range(1, steps + 1):
        f = k / steps
        f = f * f * (3 - 2 * f)            # ease in and out
        now[0] = start[0] + (right * TILT - start[0]) * f
        now[1] = start[1] + (back * TILT - start[1]) * f
        angle(outer, now[0], FLIP_OUTER)
        angle(inner, now[1], FLIP_INNER)
        time.sleep(0.02)
    time.sleep(ROLL_S)


angle(outer, 0, FLIP_OUTER)
angle(inner, 0, FLIP_INNER)
time.sleep(1)

# check the directions once: watch which way the ball goes
lean(+1, 0, "TEST: ball should roll to the RIGHT")
lean(-1, 0, "TEST: ball should roll to the LEFT")
lean(0, +1, "TEST: ball should roll to the BACK (away from you)")
lean(0, -1, "TEST: ball should roll to the FRONT (toward you)")

lean(-1, -1, "go to the front-left corner")
while True:
    # square: change ONE axis at a time, so the ball runs along a rim wall
    lean(+1, -1, "along the front wall  -> front-right corner")
    lean(+1, +1, "along the right wall  -> back-right corner")
    lean(-1, +1, "along the back wall   -> back-left corner")
    lean(-1, -1, "along the left wall   -> front-left corner")
    # diagonal: change BOTH at once, so the ball crosses the middle
    lean(+1, +1, "diagonal through the middle -> back-right corner")
    lean(-1, -1, "diagonal back -> front-left corner")
