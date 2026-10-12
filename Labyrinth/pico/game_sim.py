"""Labyrinth test run with fake input.

A pretend player steers a simulated ball from START to the 5-coin hole.
Its "joystick" goes through exactly the same control steps as
joystick_servos.py (deadzone, expo, smoothing, swing), and the real
servos move just as they would in the game.

Runs two ways
  Pico (Thonny, F5): the servos on GP16 (X) and GP17 (Y) move in real time
      while the Shell tells you what the player and the ball are doing.
  Computer (python3 game_sim.py [careful|reckless]): no servos, finishes
      instantly, prints the same story - handy for checking timings.

Wiring: same as servo_test.py, USB power only. Servo 2's white wire goes to
GP17 (pin 22); its red and black share pins 40 and 38. One servo is fine too.
The ball is simulated from the board tilt - nothing is actually rolling.
"""
import math
import random
import sys
import time

try:
    from machine import Pin, PWM
    ON_PICO = True
except ImportError:
    ON_PICO = False

# ---- the maze: a copy of MAZE in ../make_labyrinth.py (keep them the same)
MAZE = """
+---+---+---+---+---+---+---+---+---+
|       |               | 3 | X | 5 |
+   +   +   +---+   +---+   +   +   +
|   |       |   |   | 1 |       |   |
+   +   +---+   +   +   +   +   +   +
|   |           |           |       |
+   +---+---+---+---+---+---+---+---+
|   |       |                       |
+   +   +---+---+---+---+   +---+   +
|   |             T         | X     |
+   +---+   +---+---+---+   +---+   +
|           | X                 |   |
+---+---+---+---+---+---+---+---+   +
| X                 |           |   |
+---+   +---+   +---+   +---+   +   +
|       |   |   | X |   |   |   |   |
+---+   +   +   +   +   +   +   +   +
| S         |               |       |
+---+---+---+---+---+---+---+---+---+
"""
BOARD, T, N = 11.5, 0.125, 9         # inches, same as make_labyrinth.py
PITCH = (BOARD - T) / N
R = 0.3125                           # ball radius (5/8 in ball)
HOLE_D = {"5": 0.75, "3": 0.875, "1": 1.0, "X": 0.875}
COINS = {"5": 5, "3": 3, "1": 1, "X": 0}
TRAP_HALF = 0.5                      # trapdoor opening is 1 in square
BRIDGE_UP_S, BRIDGE_DOWN_S = 3.0, 2.0

# ---- control settings: the same numbers as joystick_servos.py
SWING, DEADZONE, EXPO, SMOOTH, LOOP_MS = 45.0, 0.06, 0.5, 0.4, 15
TRIM_X = TRIM_Y = 0.0
MIN_US, MAX_US, RANGE_DEG = 500, 2500, 270

# ---- mechanism and physics guesses
HORN_R, ARM_L = 0.5, 3.4      # pushrod on the 1/2 in horn hole, 3.4 in from pivot
SERVO_DEG_S = 400.0           # how fast the servo turns
G = 386.1                     # gravity, in/s^2
ROLL_DRAG = 3.0               # rolling resistance, in/s^2
BOUNCE = 0.3                  # share of speed kept after hitting a wall

# ---- the pretend player: top speed (in/s), reaction time (s), shakiness
PLAYERS = {"careful": (4.0, 0.25, 0.04), "reckless": (11.0, 0.15, 0.08)}
PLAYER = "reckless"
TIME_LIMIT_S = 180


# --------------------------------------------------------------- the maze
def parse(text):
    rows = text.strip("\n").split("\n")
    hw, vw, feat = set(), set(), {}
    for i in range(N + 1):
        for j in range(N):
            if rows[2 * i][4 * j + 1:4 * j + 4] == "---":
                hw.add((i, j))
    for i in range(N):
        for j in range(N + 1):
            if rows[2 * i + 1][4 * j] == "|":
                vw.add((i, j))
        for j in range(N):
            c = rows[2 * i + 1][4 * j + 2]
            if c != " ":
                feat[(i, j)] = c
    return hw, vw, feat


HW, VW, FEAT = parse(MAZE)


def gx(j):
    return T / 2 + j * PITCH


def gy(i):
    return BOARD - T / 2 - i * PITCH


def centre(cell):
    return gx(cell[1]) + PITCH / 2, gy(cell[0]) - PITCH / 2


def cell_of(x, y):
    j = int((x - T / 2) / PITCH)
    i = int((BOARD - T / 2 - y) / PITCH)
    return min(max(i, 0), N - 1), min(max(j, 0), N - 1)


def neighbours(cell):
    i, j = cell
    out = []
    if i > 0 and (i, j) not in HW:
        out.append((i - 1, j))
    if i < N - 1 and (i + 1, j) not in HW:
        out.append((i + 1, j))
    if j > 0 and (i, j) not in VW:
        out.append((i, j - 1))
    if j < N - 1 and (i, j + 1) not in VW:
        out.append((i, j + 1))
    return out


def route(start, goal):
    prev, todo = {start: None}, [start]
    while todo:
        c = todo.pop(0)
        if c == goal:
            break
        for nb in neighbours(c):
            if nb not in prev:
                prev[nb] = c
                todo.append(nb)
    path, c = [], goal
    while c is not None:
        path.append(c)
        c = prev[c]
    path.reverse()
    return path


def find(f):
    for c in FEAT:
        if FEAT[c] == f:
            return c
    return None


START, GOAL, TRAP = find("S"), find("5"), find("T")
PATH = route(START, GOAL)
ON_PATH = {c: k for k, c in enumerate(PATH)}
HOLES = [(centre(c)[0], centre(c)[1], HOLE_D[f] / 2, f)
         for c, f in FEAT.items() if f in HOLE_D]


def run_end(k):
    """Index of the last cell of the straight run that starts at PATH[k]."""
    if k >= len(PATH) - 1:
        return len(PATH) - 1
    di, dj = PATH[k + 1][0] - PATH[k][0], PATH[k + 1][1] - PATH[k][1]
    m = k + 1
    while (m + 1 < len(PATH) and PATH[m + 1][0] - PATH[m][0] == di
           and PATH[m + 1][1] - PATH[m][1] == dj):
        m += 1
    return m


# ------------------------------------------------- controls and mechanism
def shape(v):
    """Deadzone + expo, exactly as in joystick_servos.py."""
    if abs(v) < DEADZONE:
        return 0.0
    sign = 1 if v > 0 else -1
    v = (abs(v) - DEADZONE) / (1 - DEADZONE)
    return sign * ((1 - EXPO) * v + EXPO * v ** 3)


def board_tilt(servo_deg):
    """Servo angle -> board tilt (degrees) through the pushrod linkage."""
    s = HORN_R / ARM_L * math.sin(servo_deg * math.pi / 180)
    return math.asin(s) * 180 / math.pi


def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


if ON_PICO:
    servos = [PWM(Pin(16)), PWM(Pin(17))]
    for s in servos:
        s.freq(50)


def go(axis, angle):
    if ON_PICO:
        us = (MIN_US + MAX_US) / 2 + angle * (MAX_US - MIN_US) / RANGE_DEG
        servos[axis].duty_ns(int(clamp(us, MIN_US, MAX_US) * 1000))


# ---------------------------------------------------------------- physics
def collide(x, y, vx, vy):
    i, j = cell_of(x, y)
    if (i, j + 1) in VW and x > gx(j + 1) - T / 2 - R:
        x, vx = gx(j + 1) - T / 2 - R, -vx * BOUNCE
    if (i, j) in VW and x < gx(j) + T / 2 + R:
        x, vx = gx(j) + T / 2 + R, -vx * BOUNCE
    i, j = cell_of(x, y)
    if (i, j) in HW and y > gy(i) - T / 2 - R:
        y, vy = gy(i) - T / 2 - R, -vy * BOUNCE
    if (i + 1, j) in HW and y < gy(i + 1) + T / 2 + R:
        y, vy = gy(i + 1) + T / 2 + R, -vy * BOUNCE
    return x, y, vx, vy


def roll(x, y, vx, vy, tilt_x, tilt_y, dt):
    ax = 5 / 7 * G * math.sin(tilt_x * math.pi / 180)
    ay = 5 / 7 * G * math.sin(tilt_y * math.pi / 180)
    speed = math.sqrt(vx * vx + vy * vy)
    if speed > ROLL_DRAG * dt:
        ax -= ROLL_DRAG * vx / speed
        ay -= ROLL_DRAG * vy / speed
    elif abs(ax) < ROLL_DRAG and abs(ay) < ROLL_DRAG:
        return x, y, 0.0, 0.0                 # too flat to start rolling
    vx += ax * dt
    vy += ay * dt
    return collide(x + vx * dt, y + vy * dt, vx, vy)


def fell_in(x, y, speed, t):
    for hx, hy, hr, f in HOLES:
        dx, dy = x - hx, y - hy
        if dx * dx + dy * dy < (hr - 0.03) ** 2 and speed < 25:
            return f
    if TRAP is not None:
        tx, ty = centre(TRAP)
        if (abs(x - tx) < TRAP_HALF - 0.05 and abs(y - ty) < TRAP_HALF - 0.05
                and not bridge_up(t)):
            return "T"
    return None


def bridge_up(t):
    return t % (BRIDGE_UP_S + BRIDGE_DOWN_S) < BRIDGE_UP_S


def bridge_left(t):
    return BRIDGE_UP_S - t % (BRIDGE_UP_S + BRIDGE_DOWN_S)


# ------------------------------------------------------------- the game
def play(player):
    vmax, react_s, shaky = PLAYERS[player]
    random.seed(1)
    dt = LOOP_MS / 1000
    x, y = centre(START)
    vx = vy = 0.0
    seen = [(x, y, vx, vy)] * max(1, int(react_s / dt))   # reaction delay
    fx = fy = 0.0                    # smoothed stick
    sv = [TRIM_X, TRIM_Y]            # where the servos actually are
    k, t, last_cell, waiting = 0, 0.0, None, False
    swing_seen, tilt_seen = 0.0, 0.0
    go(0, TRIM_X)
    go(1, TRIM_Y)
    print("%s player | top speed %.0f in/s, reaction %.2f s | route %d cells"
          % (player, vmax, react_s, len(PATH)))
    print("  time   cell       stick x/y      servo x/y      board tilt x/y")
    result = None
    while t < TIME_LIMIT_S:
        t0 = time.ticks_ms() if ON_PICO else 0

        # --- the player looks at where the ball was a moment ago
        ox, oy, ovx, ovy = seen.pop(0)
        cell = cell_of(ox, oy)
        if cell in ON_PATH and ON_PATH[cell] >= k - 1:
            k = ON_PATH[cell]
        m = run_end(k)
        if TRAP is not None and TRAP in ON_PATH:
            ti = ON_PATH[TRAP]
            cross_s = 2.5 * PITCH / vmax + 0.4
            if k < ti <= m and not (bridge_up(t) and bridge_left(t) > cross_s):
                m = ti - 1                        # stop before the trapdoor
                if not waiting and k == ti - 1:
                    print("%6.1fs  waiting for the trapdoor bridge..." % t)
                    waiting = True
            elif waiting and k >= ti - 1:
                print("%6.1fs  bridge is up - GO" % t)
                waiting = False
        tx, ty = centre(PATH[m])
        want_vx = clamp(2.0 * (tx - ox), -vmax, vmax)
        want_vy = clamp(2.0 * (ty - oy), -vmax, vmax)
        sx = clamp(0.35 * (want_vx - ovx)
                   + shaky * (random.getrandbits(8) / 127.5 - 1), -1, 1)
        sy = clamp(0.35 * (want_vy - ovy)
                   + shaky * (random.getrandbits(8) / 127.5 - 1), -1, 1)

        # --- same control steps as the real game loop
        fx += SMOOTH * (shape(sx) - fx)
        fy += SMOOTH * (shape(sy) - fy)
        cmd = [TRIM_X + SWING * fx, TRIM_Y + SWING * fy]
        go(0, cmd[0])
        go(1, cmd[1])

        # --- servos turn toward the command, board tilts, ball rolls
        tilt = []
        for a in (0, 1):
            step = SERVO_DEG_S * dt
            sv[a] += clamp(cmd[a] - sv[a], -step, step)
            tilt.append(board_tilt(sv[a]))
            swing_seen = max(swing_seen, abs(sv[a]))
        tilt_seen = max(tilt_seen, abs(tilt[0]), abs(tilt[1]))
        for _ in range(3):
            x, y, vx, vy = roll(x, y, vx, vy, tilt[0], tilt[1], dt / 3)
        seen.append((x, y, vx, vy))
        t += dt

        now = cell_of(x, y)
        if now != last_cell:
            print("%6.1fs  row %d col %d   %+.2f %+.2f   %+6.1f %+6.1f"
                  "   %+5.1f %+5.1f deg"
                  % (t, now[0], now[1], sx, sy, cmd[0], cmd[1],
                     tilt[0], tilt[1]))
            last_cell = now
        result = fell_in(x, y, math.sqrt(vx * vx + vy * vy), t)
        if result:
            break
        if ON_PICO:
            time.sleep_ms(max(0, LOOP_MS - time.ticks_diff(time.ticks_ms(),
                                                            t0)))

    go(0, TRIM_X)
    go(1, TRIM_Y)
    lag_ms = math.ceil(math.log(0.1) / math.log(1 - SMOOTH)) * LOOP_MS
    print("")
    if result in COINS and COINS[result] > 0:
        print("RESULT: WIN - %d COINS after %.1f s" % (COINS[result], t))
    elif result == "X":
        print("RESULT: LOSS hole after %.1f s" % t)
    elif result == "T":
        print("RESULT: fell through the TRAPDOOR after %.1f s" % t)
    else:
        print("RESULT: ran out of time (%d s)" % TIME_LIMIT_S)
    print("servos swung up to %.0f deg, board tilted up to %.1f deg"
          % (swing_seen, tilt_seen))
    print("stick-to-servo delay from smoothing: about %d ms" % lag_ms)
    return result, t


if __name__ == "__main__":
    who = PLAYER
    if not ON_PICO and len(sys.argv) > 1 and sys.argv[1] in PLAYERS:
        who = sys.argv[1]
    play(who)
