# Two-axis show: the maze moves through cool patterns, nonstop
# both black -> pin 38 (GND)   both red -> pin 40 (VBUS)
# outer white -> pin 21 (GP16)   inner white -> pin 22 (GP17)
from machine import Pin, PWM
import time
import math

outer = PWM(Pin(16))
inner = PWM(Pin(17))
outer.freq(50)
inner.freq(50)

TILT = 10         # biggest lean on either axis (inner: keep under 16)
PATTERN_S = 6     # seconds per pattern
WAIT = 0.015      # seconds per step


def angle(servo, deg):
    deg = max(-TILT, min(TILT, deg))
    servo.duty_ns(int((1500 + deg * 7.4) * 1000))


def wave(t, period):
    return math.sin(2 * math.pi * t / period)


def cwave(t, period):
    return math.cos(2 * math.pi * t / period)


# each pattern gives (outer, inner) as -1..1 at time t
def spin(t):                 # fast circle
    return wave(t, 0.8), cwave(t, 0.8)


def figure8(t):              # infinity sign
    return wave(t, 1.6), wave(t, 0.8)


def spiral(t):               # circle that grows and shrinks
    s = 0.25 + 0.75 * abs(wave(t, 3.0))
    return s * wave(t, 0.7), s * cwave(t, 0.7)


def rock(t):                 # big diagonal see-saw
    d = wave(t, 1.2)
    return d, d


def flower(t):               # 4-petal flower
    s = abs(cwave(t, 2.4))
    return s * wave(t, 1.2), s * cwave(t, 1.2)


def quake(t):                # shimmy that builds up and dies down
    s = 0.5 - 0.5 * cwave(t, 2.0)
    return s * wave(t, 0.25), s * wave(t, 0.31)


PATTERNS = [("spin", spin), ("figure 8", figure8), ("spiral", spiral),
            ("rock", rock), ("flower", flower), ("quake", quake)]

angle(outer, 0)
angle(inner, 0)
time.sleep(1)
while True:
    for name, pattern in PATTERNS:
        print("~", name)
        start = time.ticks_ms()
        while True:
            t = time.ticks_diff(time.ticks_ms(), start) / 1000
            if t >= PATTERN_S:
                break
            fade = min(1.0, t / 0.6, (PATTERN_S - t) / 0.6)
            o, i = pattern(t)
            angle(outer, TILT * fade * o)
            angle(inner, TILT * fade * i)
            time.sleep(WAIT)
        angle(outer, 0)
        angle(inner, 0)
        time.sleep(0.3)
