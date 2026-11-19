# Both servos at once: the maze leans around in a circle, nonstop
# both black -> pin 38 (GND)   both red -> pin 40 (VBUS)
# outer white -> pin 21 (GP16)   inner white -> pin 22 (GP17)
from machine import Pin, PWM
import time
import math

outer = PWM(Pin(16))
inner = PWM(Pin(17))
outer.freq(50)
inner.freq(50)

TILT = 10         # degrees each way on both axes (inner: keep under 16)
SPEED = 4         # degrees around the circle per step (bigger = faster)
WAIT = 0.02       # seconds per step


def angle(servo, deg):             # 0 = level
    servo.duty_ns(int((1500 + deg * 7.4) * 1000))


angle(outer, 0)                    # start level
angle(inner, 0)
time.sleep(1)

size = 0.0                         # grow the circle slowly at the start
a = 0
while True:
    size = min(1.0, size + 0.02)
    r = math.radians(a)
    angle(outer, TILT * size * math.sin(r))
    angle(inner, TILT * size * math.cos(r))
    time.sleep(WAIT)
    a = (a + SPEED) % 360
