from machine import ADC, Pin, PWM
import time

x_stick = ADC(27)                     # VRx -> pin 32
y_stick = ADC(28)                     # VRy -> pin 34
outer = PWM(Pin(16))                  # Servo 1, outer board -> pin 21
inner = PWM(Pin(17))                  # Servo 2, inner board -> pin 22
outer.freq(50)
inner.freq(50)

OUTER_TRIM = -5
INNER_TRIM = -10
MAX_TILT = 10


def servo(s, deg):
    s.duty_ns(int((1500 + deg * 7.4) * 1000))


def stick(adc, mid):
    v = (adc.read_u16() - mid) / 30000
    v = max(-1, min(1, v))
    return 0 if abs(v) < 0.1 else v


time.sleep(0.5)                       # don't touch the stick
x_mid = x_stick.read_u16()
y_mid = y_stick.read_u16()

n = 0
while True:
    x = stick(x_stick, x_mid)
    y = stick(y_stick, y_mid)
    servo(outer, OUTER_TRIM + x * MAX_TILT)
    servo(inner, INNER_TRIM - y * MAX_TILT)
    n += 1
    if n % 10 == 0:
        print("X", x_stick.read_u16(), "  Y", y_stick.read_u16())
    time.sleep(0.02)
