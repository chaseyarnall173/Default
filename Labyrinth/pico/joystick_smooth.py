from machine import ADC, PWM, Pin
import time
import _thread

xPin = 27
yPin = 26
switchPin = 13

switch = Pin(switchPin, Pin.IN, Pin.PULL_UP)
servoPinX = 15
servoX = PWM(Pin(servoPinX))
servoX.freq(50)

servoPinY = 14
servoY = PWM(Pin(servoPinY))
servoY.freq(50)

trapdoorServo = PWM(Pin(12))
trapdoorServo.freq(50)

max_duty = 7864
min_duty = 1802
half_duty = int((max_duty+min_duty)/2)

trapdoorServo.duty_u16(min_duty+1200)

xJoy = ADC(xPin)
yJoy = ADC(yPin)

# ---- tune these ------------------------------------------------------
LEVEL_X, LEVEL_Y = 88, 88    # angle where the board is flat (83 + 5 in your code)
RANGE = 5                    # how far it tilts each way at full stick
DEADZONE = 0.08              # stick ignored near the middle (0-1)
CURVE = 0.6                  # 0 = straight, 1 = very gentle near the middle
GLIDE = 0.12                 # smoothing: smaller = smoother, slower
MAX_SPEED = 40               # fastest the board may move, degrees per second
CORNER_X, CORNER_Y = 95, 95  # where the button sends the board
# -----------------------------------------------------------------------

LOOP = 0.02                  # 50 times a second (the servo's own rate)
STEP = MAX_SPEED * LOOP      # most it may move in one loop


def read(joy):
    """Average 8 readings so noise can't shake the board."""
    total = 0
    for i in range(8):
        total += joy.read_u16()
    return total / 8


def stick(value, mid):
    """Stick -> -1 .. +1 with a dead zone and a gentle middle."""
    span = mid if value < mid else 65535 - mid
    v = (value - mid) / max(span, 1)
    v = max(-1.0, min(1.0, v))
    if abs(v) < DEADZONE:
        return 0.0
    sign = 1 if v > 0 else -1
    v = (abs(v) - DEADZONE) / (1 - DEADZONE)      # restart from 0 after it
    return sign * ((1 - CURVE) * v + CURVE * v ** 3)


def to_duty(angle):
    return int((6553 / 180) * angle + 1638)


def trapdoor_loop():
    trapdoorServo.duty_u16(min_duty + 1200)
    while True:
        for i in range(min_duty + 1200, half_duty + 1700):
            time.sleep(0.001)
            trapdoorServo.duty_u16(i)
        for i in range(half_duty + 1700, min_duty + 1200, -1):
            time.sleep(0.0025)
            trapdoorServo.duty_u16(i)
        time.sleep(3)


time.sleep(0.5)                       # don't touch the stick
xMid = read(xJoy)
yMid = read(yJoy)

x, y = float(LEVEL_X), float(LEVEL_Y)   # where the board is now
sent_x = sent_y = 0                     # last duty sent to each servo
button_until = 0

_thread.start_new_thread(trapdoor_loop, ())

while True:
    # 1. where the stick says to go
    want_x = LEVEL_X + stick(read(xJoy), xMid) * RANGE
    want_y = LEVEL_Y + stick(read(yJoy), yMid) * RANGE

    # 2. button: glide to the corner and hold it there for 8 seconds
    if switch.value() == 0:
        button_until = time.ticks_add(time.ticks_ms(), 8000)
    if time.ticks_diff(button_until, time.ticks_ms()) > 0:
        want_x, want_y = CORNER_X, CORNER_Y

    # 3. glide part of the way there, but never faster than MAX_SPEED
    dx = (want_x - x) * GLIDE
    dy = (want_y - y) * GLIDE
    x += max(-STEP, min(STEP, dx))
    y += max(-STEP, min(STEP, dy))

    # 4. send it - only when it changed enough to matter (no jitter)
    dux, duy = to_duty(x), to_duty(y)
    if abs(dux - sent_x) >= 2:
        servoX.duty_u16(dux)
        sent_x = dux
    if abs(duy - sent_y) >= 2:
        servoY.duty_u16(duy)
        sent_y = duy

    time.sleep(LOOP)
