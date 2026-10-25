from machine import ADC, Pin, PWM
import time

vrx = ADC(27)                         # VRx -> pin 32
vry = ADC(28)                         # VRy -> pin 34
button = Pin(22, Pin.IN, Pin.PULL_UP)  # SW -> pin 29 (press = level)
servo_x = PWM(Pin(16))                # outer board -> pin 21
servo_y = PWM(Pin(17))                # inner board -> pin 22
servo_x.freq(50)
servo_y.freq(50)

LEVEL_X = 1467    # pulse (microseconds) where the board is level. These are
LEVEL_Y = 1446    # your brother's centres (89.5 and 87.5 in his Arduino code)
LIMIT = 5         # degrees each way
FLIP_X = False
FLIP_Y = False


def read(adc):
    """Average 20 readings so the noise can't make the servo jitter."""
    total = 0
    for _ in range(20):
        total += adc.read_u16()
    return total / 20


def pulse(raw, mid, level, flip):
    v = (raw - mid) / 32768           # stick: -1 .. +1
    if abs(v) < 0.08:                 # stick at rest = exactly level
        v = 0
    v = max(-1, min(1, v))
    if flip:
        v = -v
    return level + v * LIMIT * 7.4    # 7.4 us = 1 degree


time.sleep(0.5)                       # don't touch the stick
mid_x = read(vrx)
mid_y = read(vry)
last_x = last_y = 0

while True:
    if button.value() == 0:
        px, py = LEVEL_X, LEVEL_Y
    else:
        px = pulse(read(vrx), mid_x, LEVEL_X, FLIP_X)
        py = pulse(read(vry), mid_y, LEVEL_Y, FLIP_Y)
    if abs(px - last_x) >= 2:         # ignore tiny changes = no jitter
        servo_x.duty_ns(int(px * 1000))
        last_x = px
    if abs(py - last_y) >= 2:
        servo_y.duty_ns(int(py * 1000))
        last_y = py
    time.sleep_ms(20)
