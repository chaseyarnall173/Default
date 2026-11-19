# Outer servo (axis 2) test - tilts the frame + maze slowly left and right
# black -> pin 38 (GND)   red -> pin 40 (VBUS)   white -> pin 21 (GP16)
from machine import Pin, PWM
import time

servo = PWM(Pin(16))
servo.freq(50)

TILT = 6       # degrees each way (the game uses about 6)
STEP = 0.25    # degrees per step - small steps = smooth
WAIT = 0.03    # seconds per step - bigger = slower


def angle(deg):                    # 0 = level
    servo.duty_ns(int((1500 + deg * 7.4) * 1000))


def glide(start, end):
    n = int(abs(end - start) / STEP)
    for i in range(n + 1):
        angle(start + (end - start) * i / n)
        time.sleep(WAIT)


angle(0)                           # level
time.sleep(2)
while True:
    glide(0, TILT)
    time.sleep(1)
    glide(TILT, -TILT)
    time.sleep(1)
    glide(-TILT, 0)
    time.sleep(2)
