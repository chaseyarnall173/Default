You are helping me (Chase, GE 1501 Group 1, Northeastern) finish the electronics and code for
our carnival game, "The Labyrinth". You run on my Windows laptop, so you can talk to the
Raspberry Pi Pico over USB with `mpremote` (already installed; the Pico is on COM3). Thonny is
what I normally use, so I will close it while you are using the Pico.

## How I want you to work
- MicroPython on a Raspberry Pi Pico (RP2040), MicroPython v1.29.
- Keep the code simple and in the same plain style as my code below (camelCase names like
  `xValJoy`, short comments, no classes unless needed). Don't rewrite parts that already work.
- When you give me code, give me the COMPLETE file, never snippets.
- When you mention wiring, always give BOTH the physical pin number and the GP number
  (e.g. "physical pin 14 (GP10)"). I have confused these before.
- Change one thing at a time and tell me exactly what to watch for on the real board.
- First thing: run `mpremote ls` and `mpremote cat main.py` (and any other .py on the Pico),
  copy everything on the Pico into this folder as a backup, then tell me what you found.

## The game
A 2-axis tilting ball maze (11.5 x 11.5 in plywood board, 2 in walls). The player tilts it
with a joystick and rolls an 18 mm ball from START (front-left) to prize holes 1, 3 and 5
coins (back-right). Other holes and a moving trapdoor in the middle lose.
- Outer servo (X, 25 kg) on a post tips the outer box + board one way.
- Inner servo (Y, 25 kg) in the outer box tips only the board the other way.
- SG90 micro servo sweeps the trapdoor back and forth every few seconds (runs on core 1).
- An HC-SR04 ultrasonic sensor under the board points at a wall about 11.6 cm away. A ball
  falling through the 1, 3 or 5 hole passes in front of it at a different distance, so the
  distance tells which hole: 1 coin = 4-5.5 cm, 3 coins = 6.25-8 cm, 5 coins = 8.5-11.2 cm,
  wall/baseline = 11.6 cm.
- A 16x2 I2C LCD (PCF8574 backpack, address 0x27) shows "THE LABYRINTH / Get to the 5!" and
  "YOU WIN! / 3 COINS" etc.
- A push button tilts the board to the START corner (cornerX/cornerY) for 8 s so the ball
  rolls into the collection tray corner to be returned.

## What I want (all must work together, reliably, at the same time)
1. Joystick tilts the board smoothly: moving out at moveSpeed, gliding back to level at the
   slower returnSpeed, max tilt +/- tiltX / tiltY around levelX / levelY. No twitching when
   nobody touches it.
2. Trapdoor sweeps the whole time.
3. Sensor catches a ball falling through 1/3/5 quickly (ball is only in the beam briefly) and
   the LCD shows the right prize every time, with no fake wins.
4. Button reliably tilts to the corner; noise must never trigger it.
5. Eventually save as main.py so it runs on power-up without the laptop.

## Wiring (current)
- Servo power: 5 V 6 A wall adapter. Adapter + -> breadboard + rail -> red wires of all 3
  servos. Adapter - -> - rail -> brown wires. ONE wire from the - rail -> physical pin 38 (GND).
  Nothing from adapter + goes to the Pico.
- Servo X signal: physical pin 20 (GP15). Servo Y signal: pin 19 (GP14). Trapdoor SG90 signal:
  pin 16 (GP12).
- Joystick (KY-023): + -> pin 36 (3V3), GND -> pin 33 (AGND), VRx -> pin 32 (GP27),
  VRy -> pin 31 (GP26). Its SW click is worn out and NOT used.
- Corner button: separate push button, diagonal legs, one leg -> pin 14 (GP10), other -> pin 13 (GND).
- HC-SR04: VCC -> pin 40 (VBUS 5 V), GND -> pin 23, Trig -> pin 24 (GP18),
  Echo -> 1 kOhm -> pin 25 (GP19), plus 2 kOhm from pin 25 to GND (voltage divider).
- LCD: VCC -> pin 40, GND -> pin 8, SDA -> pin 6 (GP4), SCL -> pin 7 (GP5).
- Pins 1 and 2 (GP0/GP1) are probably damaged (an earlier short when a ground wire was one pin
  off at pins 38/39/40). Don't use them.

## History / known problems (what we already learned)
- Joystick jitter was fixed earlier by powering it from 3V3 (not 5 V) and putting its GND on
  pin 33, NOT on the servo ground rail. Shared servo ground = jitter.
- Servos were weak on laptop USB power; the 5 V 6 A adapter fixed that.
- One-wheel-off wiring once shorted the Pico (it got hot). After that GP0/GP1 stopped working
  for the LCD (scan returned []); on GP4/GP5 it is found at 0x27.
- Hardware I2C gave ETIMEDOUT writing to the LCD; SoftI2C at 50 kHz plus retries works.
  The LCD loses sync from servo noise, so screen() restarts the LCD before every message.
  The win message still sometimes doesn't show.
- Sensor: worked (baseline 10.5/11.9, then 11.6), then read -1 (no echo) in the game even after
  swapping sensors and moving pins; a standalone test with a 60 ms gap works fine in the hand.
  Then the baseline read 4.3 cm in the game (suspected ghost echoes inside the closed tray when
  pinging fast, or something in the beam). Needs to be made reliable.
- The joystick's SW button failed intermittently on several pins -> switched to a separate
  push button on GP10.
- Servos twitch/snap with no input. Suspects in the code: the deadzone edge jump (inside the
  deadzone the value becomes 32768 but just outside it uses the raw reading, so ~1.5 deg jump),
  round() to whole degrees flipping at x.5, the glide step getting huge after a blocking call
  (LCD write ~150 ms, 8 s corner sleep) -> add ms = min(ms, 30), plus possible electrical causes
  (trapdoor current surge, grounds). No real race condition: core 1 only touches the trapdoor
  PWM (GP12), core 0 only touches GP14/GP15.
- Level drifts over time: probably the horn or horn-to-wall joint slipping (we turned servos by
  hand while unplugged). Mechanical, not code.
- Running from Thonny has a startup delay because Thonny pastes the file; saving as main.py fixes it.

## Suggested plan
1. Back up everything on the Pico (see top).
2. Test each part ALONE with a tiny script and have me confirm on the real hardware:
   button (GP10), joystick raw values, sensor (GP18/GP19, 60 ms gap first, then faster),
   LCD (SoftI2C GP4/GP5), each servo.
3. Fix the twitch sources in the code (smooth deadzone without round(), cap ms, only
   write servo duty when it really changes).
4. Combine into one program, test, then save as main.py.

## My current full program
```python
from machine import ADC, PWM, Pin, SoftI2C, time_pulse_us
import time
import _thread

# ---------------- settings ----------------
levelX = 83          # outer servo flat
levelY = 98          # inner servo flat
tiltX = 5.5          # degrees each way
tiltY = 5
moveSpeed = 0.03     # moving out (bigger = faster)
returnSpeed = 0.01   # coming back to level (smaller = gentler)
DEADZONE = 6000

cornerX = 75         # button: tilt to return the ball
cornerY = 115
cornerTime = 8

oneMin, oneMax = 3.5, 5.9        # hole distances in cm (wall about 11.6)
threeMin, threeMax = 5.9, 8.25
fiveMin, fiveMax = 8.25, 11.4

pingTime = 10        # ms between sensor readings
confirmNeeded = 2    # readings in a row to count a win
showTime = 5000
lockTime = 3000

printChecks = True   # prints what each part is doing

# ---------------- lcd ----------------
i2c = SoftI2C(sda=Pin(4), scl=Pin(5), freq=50000)
lcdAddr = 0
lcdWorks = False

def lcdWrite(b):
    for i in range(10):
        try:
            i2c.writeto(lcdAddr, bytes([(b | 0x08) & 0xFF]))
            return
        except OSError:
            time.sleep_ms(2)
    raise OSError("lcd")

def lcdNibble(b):
    lcdWrite(b | 0x04)
    lcdWrite(b & 0xFB)

def lcdSend(value, mode):
    lcdNibble((value & 0xF0) | mode)
    lcdNibble(((value << 4) & 0xF0) | mode)

def lcdStart():
    lcdWrite(0)
    time.sleep_ms(50)
    for v in (0x30, 0x30, 0x30, 0x20):
        lcdNibble(v)
        time.sleep_ms(5)
    for c in (0x28, 0x08, 0x01, 0x06, 0x0C):
        lcdSend(c, 0)
        time.sleep_ms(3)

def lcdLine(row, text):
    lcdSend(0x80 | (0x40 * row), 0)
    for letter in (text + "                ")[:16]:
        lcdSend(ord(letter), 1)

def screen(top, bottom=""):
    if lcdWorks:
        for i in range(3):
            try:
                lcdStart()
                lcdLine(0, top)
                lcdLine(1, bottom)
                return
            except OSError:
                time.sleep_ms(5)

def startScreen():
    screen("THE LABYRINTH", "Get to the 5!")

found = i2c.scan()
if len(found) > 0:
    lcdAddr = found[0]
    try:
        lcdStart()
        lcdWorks = True
    except OSError:
        pass
print("LCD:", "ok" if lcdWorks else "NOT WORKING - check pins 6, 7, 8, 40")
startScreen()

# ---------------- distance sensor ----------------
trig = Pin(18, Pin.OUT)
echo = Pin(19, Pin.IN)
trig.value(0)

def getDistance():
    if echo.value() == 1:
        return -1
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)
    pulse = time_pulse_us(echo, 1, 2000)
    if pulse < 0:
        return -1
    return pulse * 0.0343 / 2

def checkHole(dist):
    if oneMin <= dist < oneMax:
        return 1
    if threeMin <= dist < threeMax:
        return 3
    if fiveMin <= dist < fiveMax:
        return 5
    return 0

time.sleep_ms(50)
test = getDistance()
print("SENSOR:", "ok, wall at %.1f cm" % test if test > 0 else "NO READING - check pins 23, 24, 25, 40")

# ---------------- button ----------------
button = Pin(10, Pin.IN, Pin.PULL_UP)
print("BUTTON:", "ok" if button.value() == 1 else "READS PRESSED - use diagonal legs")

# ---------------- joystick (4 readings averaged = less noise) ----------------
xJoy = ADC(27)
yJoy = ADC(26)

def readJoy(joy):
    total = 0
    for i in range(4):
        total = total + joy.read_u16()
    return total // 4

xMid = readJoy(xJoy)
yMid = readJoy(yJoy)
print("JOYSTICK: middle", xMid, yMid, "(should be 25000-40000)")

# ---------------- servos ----------------
servoX = PWM(Pin(15))
servoY = PWM(Pin(14))
trapdoorServo = PWM(Pin(12))
servoX.freq(50)
servoY.freq(50)
trapdoorServo.freq(50)

min_duty = 1802
max_duty = 7864
half_duty = int((max_duty + min_duty) / 2)

def moveServos(angleX, angleY):
    servoX.duty_u16(int((6553 / 180) * angleX + 1638))
    servoY.duty_u16(int((6553 / 180) * angleY + 1638))

def trapdoor_loop():
    while True:
        for i in range(min_duty + 1400, half_duty + 1700):
            time.sleep(0.001)
            trapdoorServo.duty_u16(i)
        for i in range(half_duty + 1700, min_duty + 1400, -1):
            time.sleep(0.0025)
            trapdoorServo.duty_u16(i)
        time.sleep(3)

def glide(now, target, level, ms):
    if abs(target - level) < abs(now - level):
        step = ms * returnSpeed
    else:
        step = ms * moveSpeed
    if now > target:
        return max(target, now - step)
    return min(target, now + step)

# ---------------- start ----------------
nowX = levelX
nowY = levelY
last = time.ticks_ms()
lastPing = last
lockUntil = last
showUntil = 0
showing = False
armed = True
lastHole = 0
holeCount = 0
pressedSince = 0

trapdoorServo.duty_u16(min_duty + 1400)
moveServos(nowX, nowY)
_thread.start_new_thread(trapdoor_loop, ())
print("RUNNING")

while True:
    t = time.ticks_ms()
    ms = time.ticks_diff(t, last)
    last = t

    # joystick -> board
    xValJoy = readJoy(xJoy)
    yValJoy = readJoy(yJoy)
    if abs(xValJoy - xMid) < DEADZONE:
        xValJoy = 32768
    if abs(yValJoy - yMid) < DEADZONE:
        yValJoy = 32768
    angleX = round(levelX - tiltX + (xValJoy / 65535) * 2 * tiltX)
    angleY = round(levelY - tiltY + (yValJoy / 65535) * 2 * tiltY)
    nowX = glide(nowX, angleX, levelX, ms)
    nowY = glide(nowY, angleY, levelY, ms)
    moveServos(nowX, nowY)

    # sensor -> win
    if time.ticks_diff(t, lastPing) >= pingTime:
        lastPing = t
        dist = getDistance()
        if dist >= fiveMax:
            armed = True
        if dist > 0:
            hole = checkHole(dist)
            if hole > 0 and hole == lastHole:
                holeCount = holeCount + 1
            elif hole > 0:
                holeCount = 1
            else:
                holeCount = 0
            lastHole = hole
            if armed and holeCount >= confirmNeeded and time.ticks_diff(t, lockUntil) >= 0:
                if printChecks:
                    print("WIN", hole, "at %.1f cm" % dist)
                if hole == 1:
                    screen("YOU WIN!", "1 COIN")
                else:
                    screen("YOU WIN!", "%d COINS" % hole)
                armed = False
                holeCount = 0
                showing = True
                showUntil = time.ticks_add(t, showTime)
                lockUntil = time.ticks_add(t, lockTime)

    if showing and time.ticks_diff(t, showUntil) >= 0:
        startScreen()
        showing = False

    # button -> corner (must be held 50 ms, so noise can't trigger it)
    if button.value() == 0:
        if pressedSince == 0:
            pressedSince = t
        elif time.ticks_diff(t, pressedSince) >= 50:
            if printChecks:
                print("BUTTON pressed - returning ball")
            screen("Returning ball")
            moveServos(cornerX, cornerY)
            time.sleep(cornerTime)
            nowX = cornerX
            nowY = cornerY
            last = time.ticks_ms()
            lockUntil = time.ticks_add(last, 1000)
            pressedSince = 0
            startScreen()
            showing = False
    else:
        pressedSince = 0
```
