# Runs on the Pico. tilt_control.py (on the laptop) starts it and sends
# "servo1_deg servo2_deg" lines about 50 times a second.
#   Servo 1 = outer board, pin 21 (GP16)   Servo 2 = inner board, pin 22 (GP17)
from machine import Pin, PWM
import sys

servo1 = PWM(Pin(16))
servo2 = PWM(Pin(17))
servo1.freq(50)
servo2.freq(50)
LIMIT = 25          # never go further than this from the servo's 0


def write(servo, deg):
    deg = max(-LIMIT, min(LIMIT, deg))
    servo.duty_ns(int((1500 + deg * 7.4) * 1000))


while True:
    try:
        a, b = sys.stdin.readline().split()
        write(servo1, float(a))
        write(servo2, float(b))
    except ValueError:
        pass
