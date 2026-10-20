# Two-servo test: outer servo (axis 2, left/right) + inner servo (axis 1, front/back)
# both black -> pin 38 (GND)   both red -> pin 40 (VBUS)
# outer white -> pin 21 (GP16)   inner white -> pin 22 (GP17)
from machine import Pin, PWM
import time
import math

outer = PWM(Pin(16))
inner = PWM(Pin(17))
outer.freq(50)
inner.freq(50)

OUTER_TILT = 10   # degrees each way, outer (frame + maze)
INNER_TILT = 10   # degrees each way, inner (maze only) - keep under 16
STEP = 1          # degrees per step
WAIT = 0.015      # seconds per step


def angle(servo, deg):             # 0 = level
    servo.duty_ns(int((1500 + deg * 7.4) * 1000))


def glide(servo, start, end):
    step = STEP if end > start else -STEP
    a = start
    while (a < end) if step > 0 else (a > end):
        angle(servo, a)
        time.sleep(WAIT)
        a += step
    angle(servo, end)


def swing(servo, tilt):
    glide(servo, 0, tilt)
    glide(servo, tilt, -tilt)
    glide(servo, -tilt, 0)


angle(outer, 0)                    # both level
angle(inner, 0)
time.sleep(1)
while True:
    print("1) outer only: frame + maze tip left/right")
    swing(outer, OUTER_TILT)
    time.sleep(0.5)
    print("2) inner only: maze tips front/back inside the frame")
    swing(inner, INNER_TILT)
    time.sleep(0.5)
    print("3) both: maze leans in a circle")
    glide(inner, 0, INNER_TILT)    # start the circle at front/back = +tilt
    for i in range(0, 361, 5):
        a = math.radians(i)
        angle(outer, OUTER_TILT * math.sin(a))
        angle(inner, INNER_TILT * math.cos(a))
        time.sleep(0.02)
    glide(inner, INNER_TILT, 0)    # circle ends at front/back = +tilt
    angle(outer, 0)
    time.sleep(1)
