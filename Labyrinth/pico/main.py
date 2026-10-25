# Starts one of your files when the Pico powers up.
# Normal power-up            -> runs FILE
# Hold the joystick button
# down while plugging in     -> runs BUTTON_FILE
# Change the names to any file saved on the Pico (without the .py).
from machine import Pin

FILE = "joystick_simple"
BUTTON_FILE = "joystick_servos"

button = Pin(22, Pin.IN, Pin.PULL_UP)       # joystick SW, pin 29
name = BUTTON_FILE if button.value() == 0 else FILE
print("running", name)
__import__(name)
