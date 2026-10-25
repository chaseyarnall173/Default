# Wiring: joystick GND -> pin 33   +5V -> pin 36   VRx -> pin 32
#         VRy -> pin 34   SW -> pin 29
#         outer servo white -> pin 21   inner servo white -> pin 22
#         both servo red -> pin 40      both servo black -> pin 38
from machine import ADC, Pin, PWM
import time


class Servo:
    """Works like Arduino's Servo: write(0..180), same pulses as Arduino."""

    def __init__(self, pin):
        self.pwm = PWM(Pin(pin))
        self.pwm.freq(50)

    def write(self, angle):
        angle = max(0, min(180, angle))
        us = 544 + angle * (2400 - 544) / 180
        self.pwm.duty_ns(int(us * 1000))


servo_x = Servo(16)                    # outer board, pin 21
servo_y = Servo(17)                    # inner board, pin 22
vrx = ADC(27)                          # pin 32
vry = ADC(28)                          # pin 34
button = Pin(22, Pin.IN, Pin.PULL_UP)  # pin 29, press = level

LEVEL_X = 89.5    # brother's level angles
LEVEL_Y = 87.5
RANGE = 3.6       # 3.6 Arduino degrees = 5 real degrees each way


def read(adc):
    """Middle of 15 readings, 0..1. One bad reading can't move the servo."""
    r = sorted(adc.read_u16() for _ in range(15))
    return r[7] / 65535


time.sleep(0.5)                        # don't touch the stick
mid_x = read(vrx)
mid_y = read(vry)

while True:
    x = read(vrx) - mid_x              # -0.5 .. +0.5
    y = read(vry) - mid_y
    if abs(x) < 0.08 or button.value() == 0:
        x = 0
    if abs(y) < 0.08 or button.value() == 0:
        y = 0
    servo_x.write(LEVEL_X + x * 2 * RANGE)
    servo_y.write(LEVEL_Y + y * 2 * RANGE)
    time.sleep_ms(20)
