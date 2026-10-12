"""Servo wave show: the servo swings through smooth wave patterns forever.

Same wiring as servo_test.py:
  black -> GND (pin 38)   red -> VBUS (pin 40)   white -> GP16 (pin 21)
Press Stop in Thonny to end. Keep the horn clear of anything it can hit.
If the Pico resets during the big swings, lower LIMIT (USB power limit).
"""
import math
import time
from machine import Pin, PWM

PIN = 16
MIN_US, MAX_US, RANGE_DEG = 500, 2500, 270   # 270 degree servo
LIMIT = 70          # never swing further than this from centre (degrees)
PATTERN_S = 10      # seconds each pattern plays
FADE_S = 0.6        # ease in/out so patterns join without a jump

servo = PWM(Pin(PIN))
servo.freq(50)


def go(angle):
    angle = max(-LIMIT, min(LIMIT, angle))
    us = (MIN_US + MAX_US) / 2 + angle * (MAX_US - MIN_US) / RANGE_DEG
    servo.duty_ns(int(us * 1000))


def wave(t, period):
    return math.sin(2 * math.pi * t / period)


def swell(t):           # slow, even back and forth
    return 40 * wave(t, 3.0)


def growing(t):         # same wave, getting bigger the whole time
    return 60 * (t / PATTERN_S) * wave(t, 1.2)


def ripples(t):         # big slow wave with small fast ripples on top
    return 35 * wave(t, 2.0) + 12 * wave(t, 0.3)


def heartbeat(t):       # lub-dub ... lub-dub
    beat = t % 1.2
    if beat < 0.2:
        return 22 * math.sin(math.pi * beat / 0.2)
    if 0.3 < beat < 0.5:
        return 15 * math.sin(math.pi * (beat - 0.3) / 0.2)
    return 0


def ocean(t):           # three waves that never line up, so it looks random
    return 25 * wave(t, 2.3) + 18 * wave(t, 3.7) + 12 * wave(t, 5.9)


def pendulum(t):        # big swing that dies down like a real pendulum
    return 65 * math.exp(-t / 3.5) * math.cos(2 * math.pi * t / 1.6)


PATTERNS = [("gentle swell", swell), ("growing wave", growing),
            ("ripples", ripples), ("heartbeat", heartbeat),
            ("ocean", ocean), ("pendulum", pendulum)]

go(0)
time.sleep(1)
while True:
    for name, pattern in PATTERNS:
        print("~", name)
        start = time.ticks_ms()
        while True:
            t = time.ticks_diff(time.ticks_ms(), start) / 1000
            if t >= PATTERN_S:
                break
            fade = min(1.0, t / FADE_S, (PATTERN_S - t) / FADE_S)
            go(pattern(t) * fade)
            time.sleep_ms(20)
        go(0)
        time.sleep_ms(300)
