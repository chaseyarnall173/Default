from machine import Pin, PWM


class Servo:
    """Works like Arduino's Servo: write(0..180), same pulses as Arduino."""

    def __init__(self, pin):
        self.pwm = PWM(Pin(pin))
        self.pwm.freq(50)

    def write(self, angle):
        angle = max(0, min(180, angle))
        us = 544 + angle * (2400 - 544) / 180
        self.pwm.duty_ns(int(us * 1000))
