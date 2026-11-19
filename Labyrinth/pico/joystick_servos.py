"""Joystick tilts the maze. Runs on the Pico by itself - no laptop needed.

Wiring
  joystick GND  -> Pico GND (pin 38)
  joystick +5V  -> Pico 3V3(OUT) (pin 36)   NOT 5 V: the ADC pins max at 3.3 V
  joystick VRx  -> GP27 (pin 32)       VRy -> GP28 (pin 34)
  (pin 33 is a GND pin, not an input - don't put VRx there)
  joystick SW   -> GP22 (pin 29)       hold the button = board goes level
  Servo 1 (outer board, left/right) white -> GP16 (pin 21)
  Servo 2 (inner board, front/back) white -> GP17 (pin 22)
  both servos red -> VBUS (pin 40)     both servos black -> GND (pin 38)

The stick works like the knobs on a real labyrinth: push it halfway and
the board tilts halfway, let go and the board goes back to level.
Leave the stick alone for the first second while it finds its centre.
Save it on the Pico as main.py and it runs whenever the Pico gets power,
so you can run the game off a USB wall charger (stronger than a laptop).
"""
import time
from machine import ADC, Pin, PWM

# ---- tune these during playtesting -----------------------------------
MAX_TILT = 10     # board tilt (degrees) at full stick - never more than 15
DEADZONE = 0.08   # part of the stick travel ignored around centre
EXPO = 0.5        # 0 = straight line, 1 = very soft near centre (finer)
SPEED = 120       # fastest the board may move, degrees per second
OUTER_TRIM = -5   # servo angle that levels the board (same numbers as
INNER_TRIM = -10  # tilt_control.py - use what ENTER saved there)
FLIP_OUTER = False  # True if stick right makes the ball go left
FLIP_INNER = True   # True if stick up makes the ball come toward you
SWAP_AXES = False   # True if left/right on the stick moves front/back
LOOP_MS = 10
# -----------------------------------------------------------------------

stick_x, stick_y = ADC(27), ADC(28)
button = Pin(22, Pin.IN, Pin.PULL_UP)
servo1, servo2 = PWM(Pin(16)), PWM(Pin(17))
servo1.freq(50)
servo2.freq(50)


def write(servo, deg):
    deg = max(-30, min(30, deg))
    servo.duty_ns(int((1500 + deg * 7.4) * 1000))


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


write(servo1, OUTER_TRIM)
write(servo2, INNER_TRIM)
print("finding the stick centre - don't touch it")
mid_x, mid_y = centre_of(stick_x), centre_of(stick_y)
print("centre x=%d y=%d - go!" % (mid_x, mid_y))

now = [0.0, 0.0]                  # [left/right, front/back] board tilt
step = SPEED * LOOP_MS / 1000
n = 0
while True:
    t0 = time.ticks_ms()
    if button.value() == 0:       # pressed: level the board
        want = [0.0, 0.0]
    else:
        x = shape(normalise(stick_x.read_u16(), mid_x))
        y = shape(normalise(stick_y.read_u16(), mid_y))
        if SWAP_AXES:
            x, y = y, x
        want = [x * MAX_TILT, y * MAX_TILT]
    for k in (0, 1):              # glide, so a flick can't jerk the board
        now[k] += max(-step, min(step, want[k] - now[k]))
    write(servo1, (-now[0] if FLIP_OUTER else now[0]) + OUTER_TRIM)
    write(servo2, (-now[1] if FLIP_INNER else now[1]) + INNER_TRIM)
    n += 1
    if n % 20 == 0:               # print about 5 times a second
        print("left/right %+5.1f   front/back %+5.1f" % (now[0], now[1]))
    time.sleep_ms(max(0, LOOP_MS - time.ticks_diff(time.ticks_ms(), t0)))
