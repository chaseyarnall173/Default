# Joystick -> both servos, 5 degrees max each way.
# Wiring: joystick GND -> pin 33   +5V -> pin 36 (3V3)   VRx -> pin 32
#         VRy -> pin 34   SW -> pin 29
#         outer servo white -> pin 21   inner servo white -> pin 22
#         both servo red -> pin 40      both servo black -> pin 38
from machine import ADC, Pin, PWM
import time

vrx = ADC(27)
vry = ADC(28)
button = Pin(22, Pin.IN, Pin.PULL_UP)
servo_x = PWM(Pin(16))
servo_y = PWM(Pin(17))
servo_x.freq(50)
servo_y.freq(50)

LEVEL_X = 1467    # pulse (us) where the board is level (brother's centres)
LEVEL_Y = 1446
LIMIT = 5         # degrees each way
DEADZONE = 0.15   # stick has to move this far before anything happens
SPEED = 40        # max degrees per second, so a glitch can't jerk the board
FLIP_X = False
FLIP_Y = False


def read(adc):
    """Middle value of 15 readings: one bad reading can't move the servo."""
    r = sorted(adc.read_u16() for _ in range(15))
    return r[7]


def stick(adc, mid):
    v = (read(adc) - mid) / 32768
    if abs(v) < DEADZONE:
        return 0.0
    v = (abs(v) - DEADZONE) / (1 - DEADZONE) * (1 if v > 0 else -1)
    return max(-1.0, min(1.0, v))


time.sleep(0.5)                       # don't touch the stick
mid_x = sum(read(vrx) for _ in range(10)) / 10
mid_y = sum(read(vry) for _ in range(10)) / 10

x = y = 0.0                           # current tilt in degrees
step = SPEED * 0.02
while True:
    if button.value() == 0:
        want_x = want_y = 0.0
    else:
        want_x = stick(vrx, mid_x) * LIMIT
        want_y = stick(vry, mid_y) * LIMIT
    x += max(-step, min(step, want_x - x))
    y += max(-step, min(step, want_y - y))
    servo_x.duty_ns(int((LEVEL_X + (-x if FLIP_X else x) * 7.4) * 1000))
    servo_y.duty_ns(int((LEVEL_Y + (-y if FLIP_Y else y) * 7.4) * 1000))
    time.sleep_ms(20)
