"""Joystick drives both servos: the starting point for the real control loop.

Wiring
  joystick GND  -> Pico GND (pin 38)
  joystick +5V  -> Pico 3V3(OUT) (pin 36)   NOT 5 V: the ADC pins max at 3.3 V
  joystick VRx  -> GP26 (pin 31)       VRy -> GP27 (pin 32)
  joystick SW   -> GP22 (pin 29)       hold the button = board goes level
  servo X signal -> GP16 (pin 21)      servo Y signal -> GP17 (pin 22)
  both servos red -> VBUS (pin 40, USB 5 V)   brown/black -> GND (pin 38)
  Get one servo working on its own first. Two servos moving fast at the
  same time can draw more than a laptop USB port gives.

Leave the stick alone for the first second while it calibrates its centre.
Save it on the Pico as main.py to make it run whenever the Pico powers up.
"""
import time
from machine import ADC, Pin, PWM

# ---- tune these during playtesting -----------------------------------
SWING = 45.0      # servo degrees at full stick (the linkage turns this into
                  # about 6 deg of board tilt - lower it if the board tilts
                  # more than that)
DEADZONE = 0.06   # part of the stick travel ignored around centre
EXPO = 0.5        # 0 = straight line, 1 = very soft near centre (finer)
SMOOTH = 0.4      # 1 = no smoothing; lower is smoother but adds lag
TRIM_X, TRIM_Y = 0.0, 0.0       # servo degrees that make the board level
INVERT_X, INVERT_Y = False, False
LOOP_MS = 15      # keep this short - long loops ARE the input delay
# -----------------------------------------------------------------------

MIN_US, MAX_US, RANGE_DEG = 500, 2500, 270   # 270 degree servo

stick_x, stick_y = ADC(26), ADC(27)
button = Pin(22, Pin.IN, Pin.PULL_UP)
servo_x, servo_y = PWM(Pin(16)), PWM(Pin(17))
for s in (servo_x, servo_y):
    s.freq(50)


def go(servo, angle):
    us = (MIN_US + MAX_US) / 2 + angle * (MAX_US - MIN_US) / RANGE_DEG
    servo.duty_ns(int(max(MIN_US, min(MAX_US, us)) * 1000))


def centre_of(adc):
    total = 0
    for _ in range(50):
        total += adc.read_u16()
        time.sleep_ms(10)
    return total // 50


def normalise(raw, mid):
    """Stick reading -> -1 .. +1, using each half's own range."""
    span = mid if raw < mid else 65535 - mid
    return max(-1.0, min(1.0, (raw - mid) / max(span, 1)))


def shape(v):
    """Deadzone, then expo so small stick moves give very small tilts."""
    if abs(v) < DEADZONE:
        return 0.0
    sign = 1 if v > 0 else -1
    v = (abs(v) - DEADZONE) / (1 - DEADZONE)
    return sign * ((1 - EXPO) * v + EXPO * v ** 3)


go(servo_x, TRIM_X)
go(servo_y, TRIM_Y)
print("calibrating - don't touch the stick")
mid_x, mid_y = centre_of(stick_x), centre_of(stick_y)
print("centre x=%d y=%d - go!" % (mid_x, mid_y))

fx = fy = 0.0
n = 0
while True:
    t0 = time.ticks_ms()
    if button.value() == 0:                 # pressed: level the board
        x = y = 0.0
    else:
        x = shape(normalise(stick_x.read_u16(), mid_x))
        y = shape(normalise(stick_y.read_u16(), mid_y))
    fx += SMOOTH * (x - fx)
    fy += SMOOTH * (y - fy)
    ax = TRIM_X + SWING * (-fx if INVERT_X else fx)
    ay = TRIM_Y + SWING * (-fy if INVERT_Y else fy)
    go(servo_x, ax)
    go(servo_y, ay)
    n += 1
    if n % 13 == 0:                         # print about 5 times a second
        print("x %+6.1f deg   y %+6.1f deg   loop %d ms"
              % (ax, ay, time.ticks_diff(time.ticks_ms(), t0)))
    time.sleep_ms(max(0, LOOP_MS - time.ticks_diff(time.ticks_ms(), t0)))
