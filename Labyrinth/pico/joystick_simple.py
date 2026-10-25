# Your brother's Arduino code, on the Pico.
# Needs the servo library: Thonny > Tools > Manage packages > micropython-servo
from machine import ADC
from servo import Servo
import time

servo_x = Servo(pin_id=16)    # outer servo, pin 21
servo_y = Servo(pin_id=17)    # inner servo, pin 22
vrx = ADC(27)                 # joystick VRx, pin 32
vry = ADC(28)                 # joystick VRy, pin 34

x = 89.5                      # level (brother's centre)
y = 87.5

while True:
    want_x = 86 + (vrx.read_u16() / 65535) * 7    # 86..93 = 5 deg each way
    want_y = 84 + (vry.read_u16() / 65535) * 7    # 84..91
    x += (want_x - x) * 0.1   # glide there instead of snapping
    y += (want_y - y) * 0.1
    servo_x.write(x)
    servo_y.write(y)
    time.sleep_ms(20)
