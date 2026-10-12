"""Bench test for ONE 25 kg servo (DS3225-style, 270 degree) on a Pico.

Wiring - the servo gets its OWN 5-6 V supply, never the Pico's 3V3 pin:
  servo brown/black wire          -> supply (-)  AND  Pico GND (pin 38)
  servo red wire                  -> supply (+)  4x AA pack (6 V) or a
                                     5-6 V adapter rated 3 A or more
  servo orange/yellow/white wire  -> Pico GP16 (pin 21)
The two grounds MUST be joined or the servo will twitch randomly.

Run in Thonny (F5). Tape a straw or ruler to the horn so small moves are
easy to see, and watch the printed angles.
"""
import time
from machine import Pin, PWM

PIN = 16
MIN_US, MAX_US, RANGE_DEG = 500, 2500, 270   # 270 degree servo
SWEEP_DEG = 20      # how far either side of centre the sweep goes

servo = PWM(Pin(PIN))
servo.freq(50)


def pulse_us(angle):
    """Pulse width for `angle` degrees from centre (+ one way, - the other)."""
    us = (MIN_US + MAX_US) / 2 + angle * (MAX_US - MIN_US) / RANGE_DEG
    return max(MIN_US, min(MAX_US, us))


def go(angle):
    servo.duty_ns(int(pulse_us(angle) * 1000))


print("1) CENTRE. Push the horn on now, pointing straight out.")
go(0)
time.sleep(3)

print("2) slow sweep +/-%d deg - should be smooth, no grinding" % SWEEP_DEG)
angles = (list(range(0, SWEEP_DEG + 1))
          + list(range(SWEEP_DEG, -SWEEP_DEG - 1, -1))
          + list(range(-SWEEP_DEG, 1)))
for a in angles:
    go(a)
    time.sleep_ms(30)

print("3) step test: jump to +10 and back x5 - does it lag or overshoot?")
for _ in range(5):
    go(10)
    time.sleep_ms(400)
    go(0)
    time.sleep_ms(400)

print("4) fine steps of 0.25 deg - write down the first step you can SEE")
a = 0.0
while a <= 3.0:
    go(a)
    print("   %.2f deg  (%.1f us)" % (a, pulse_us(a)))
    time.sleep_ms(800)
    a += 0.25

go(0)
print("done - servo is holding centre")
