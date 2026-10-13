# Simple servo test
# black -> pin 38 (GND)   red -> pin 39 (VSYS)   white -> pin 21 (GP16)
from machine import Pin, PWM
import time

servo = PWM(Pin(16))
servo.freq(50)


def angle(deg):              # 0 = middle, + one way, - the other way
    servo.duty_ns(int((1500 + deg * 7.4) * 1000))


while True:
    angle(0)
    time.sleep(1)
    angle(30)
    time.sleep(1)
    angle(0)
    time.sleep(1)
    angle(-30)
    time.sleep(1)
