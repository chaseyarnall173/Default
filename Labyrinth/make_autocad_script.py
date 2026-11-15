"""Write Labyrinth_3D.scr: an AutoCAD script that builds the whole game as a
3D model. In a NEW drawing (acad3d.dwt) type SCRIPT and pick the file.

Units are inches. The floor's front-left corner is at 0,0 and its top at
Z = 0. The player stands at the front (-Y side).

Board, as built (numbers in as_built.py, traced from the team's laser
drawing): red floor with 9 holes (all 7/8 in) and the trapdoor opening,
yellow rim, 34 blue maze walls (2 in tall), labels, the ball at START.
The trapdoor's SG90 lies flat against the underside of the floor next to
the opening, its shaft in line with the flap's hinge.

Under the board, moving with it: the collection tray - a box whose walls
carry the rim on down 2.375 in, with a floor under them. The left and
front walls have a 3 x 1.625 in corner cut out at the START corner, so
the ball rolls to that corner when the button tilts the board there.

Mounting, as built: the outer box (4 red walls) hangs between two posts
and the board hangs inside the outer box. Both pivots sit AXLE_UP above
the bottom of the outer box's walls.
  inner servo (board tips left/right, axis 1 runs front-back): its body
      sits in a cutout in the outer box's FRONT wall and its horn screws to
      the board's front rim. At the back a dowel glued in the board's back
      rim turns in a bearing glued to the INSIDE of the outer box's back
      wall - both sit in the gap, nothing goes through that wall.
  outer servo (outer box + board tip front/back, axis 2 runs left-right):
      its body is fixed to the RIGHT post and its horn screws to the outer
      box's right wall. On the left a dowel in the left post turns in a
      bearing in the outer box's left wall.

Servo size is the listing's 40 x 20 x 40.5 mm. Tab span, tab hole spacing
and tab height are typical 25 kg servo values - measure yours and change
the SERVO_* / TAB_* numbers.

Every part with holes is built on its own layer and cut with SUBTRACT
while every finished layer is frozen, so a cut never touches another part.
"""
import os
import sys

import as_built as ab

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else HERE
B, T = ab.BOARD, ab.T
C = B / 2                     # board centre, x and y
FR_Z0, FR_Z1 = -1.2, ab.WALL_H   # outer box walls: top level with the rim
AXLE_UP = 1.875               # both axles, above the outer box walls' bottom
AXIS_Z = FR_Z0 + AXLE_UP      # = height above the floor top
TRAP_GAP = 1 / 32             # trapdoor flap clearance, three free sides
TRAP_HINGE_GAP = 1 / 16       # flap clearance, hinge side
SG90_L, SG90_W, SG90_H = 0.90, 0.48, 0.89   # 22.8 x 12.2 x 22.7 mm body
SG90_SHAFT = 0.23             # shaft centre from the body's end
PIN_R, PIN_HOLE_R = 0.125, 0.13          # 1/4 in dowel, hole a bit bigger
BEAR_R, BEAR_T = 0.433, 0.276            # 608 bearing: 22 mm OD, 7 mm wide

# servo, local frame: shaft along +z at x = y = 0, top face at z = 0
SERVO_LEN, SERVO_W, SERVO_BODY_H = 1.58, 0.79, 1.48
SHAFT_FROM_END = 0.39         # shaft centre from the near end of the body
SERVO_TAB_SPAN = 2.15         # tab tip to tab tip
SERVO_TAB_FROM_TOP, SERVO_TAB_T = 0.49, 0.1
TAB_HOLE_DX, TAB_HOLE_DY, TAB_HOLE_R = 1.95, 0.39, 0.09
BOSS_R, BOSS_H = 0.24, 0.12
HORN_R, HORN_T = 0.34, 0.1
HORN_SCREW_R, HORN_SCREW_DX, HORN_HUB_R = 0.05, 0.3, 0.1
WINDOW_CLEAR = 0.01           # servo cutout is this much bigger all round
TAB_Z = -SERVO_TAB_FROM_TOP - SERVO_TAB_T   # tab underside, local z
HORN_UP = BOSS_H + HORN_T     # horn face, above the servo's top face

FR_GAP = 0.5                  # board to outer box: left, right, back
POST_GAP = 0.25               # outer box to the left post
POST_T = 0.75                 # posts: 3/4 in thick
POST_W = 1.5
BASE_Z0, BASE_Z1 = -5.0, -4.5
# collection tray under the board (moves with the board)
TRAY_Z1 = -T                  # tray walls start under the floor plate
TRAY_Z0 = TRAY_Z1 - ab.TRAY_H # bottom of the walls = top of the tray floor
GAME_TILT = 6.0               # tilt the clearance checks allow for


def n(v):
    s = "%.4f" % v
    s = s.rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


def pt(x, y, z):
    return "%s,%s,%s" % (n(x), n(y), n(z))


# ---------------------------------------------------------------- recording
class Model:
    """Collects script lines and remembers every solid for the checks."""

    def __init__(self):
        self.lines = ["DYNMODE", "0", "OSMODE", "0", "INSUNITS", "1",
                      "LUPREC", "4"]
        self.built = []           # finished layers, frozen during cuts
        self.solids = []          # (layer, kind, data)
        self.layer = None

    def use(self, name, color, freeze=False):
        self.lines += ["-LAYER", "M", name, "C", str(color), name]
        if freeze and self.built:
            self.lines += ["F", ",".join(self.built)]
        self.lines.append("")
        self.layer = name

    def box(self, x0, y0, z0, x1, y1, z1):
        lo = (min(x0, x1), min(y0, y1), min(z0, z1))
        hi = (max(x0, x1), max(y0, y1), max(z0, z1))
        self.lines += ["BOX", pt(*lo), pt(*hi)]
        self.solids.append((self.layer, "box", (lo, hi)))

    def cyl(self, p0, p1, r):
        """Cylinder of radius r from point p0 to point p1."""
        self.lines += ["CYLINDER", pt(*p0), n(r), "A", pt(*p1)]
        self.solids.append((self.layer, "cyl", (p0, p1, r)))

    def sphere(self, c, r):
        self.lines += ["SPHERE", pt(*c), n(r)]
        self.solids.append((self.layer, "sphere", (c, r)))

    def text(self, s, x, y, z, h):
        self.lines += ["TEXT", "J", "MC", pt(x, y, z), n(h), "0", s, ""]

    def cut_part(self, name, color, target, cutters):
        """One part with holes: cutters, then the part, then SUBTRACT."""
        self.use("TMP", 1, freeze=True)
        for cut in cutters:
            cut()
        self.use(name, color)
        target()
        self.lines += ["SUBTRACT", "L", "", "ALL", "R", "L", ""]
        self.built.append(name)

    def finish(self):
        self.lines += ["-LAYER", "T", "*", "S", "0", "",
                       "-VIEW", "SEISO", "VSCURRENT", "S", "ZOOM", "E",
                       "OSMODE", "4133"]


# -------------------------------------------------------------- the servo
def servo(m, to_world, layer, color, horn_layer):
    """Servo body, mounting tabs, output boss and round horn."""
    x0, x1 = -SHAFT_FROM_END, SERVO_LEN - SHAFT_FROM_END
    xm, hy = (x0 + x1) / 2, SERVO_W / 2
    m.use(layer, color)
    m.box(*to_world(x0, -hy, -SERVO_BODY_H), *to_world(x1, hy, 0))
    m.box(*to_world(xm - SERVO_TAB_SPAN / 2, -hy, TAB_Z),
          *to_world(xm + SERVO_TAB_SPAN / 2, hy, -SERVO_TAB_FROM_TOP))
    m.cyl(to_world(0, 0, 0), to_world(0, 0, BOSS_H), BOSS_R)
    m.use(horn_layer, 9)
    m.cyl(to_world(0, 0, BOSS_H), to_world(0, 0, BOSS_H + HORN_T), HORN_R)


def mount_cuts(m, to_world, plate_t):
    """Cutters for a servo mount plate: body cutout + 4 tab screw holes.
    The plate sits right under the tabs and is plate_t thick."""
    x0, x1 = -SHAFT_FROM_END, SERVO_LEN - SHAFT_FROM_END
    xm, hy, c = (x0 + x1) / 2, SERVO_W / 2, WINDOW_CLEAR
    lo, hi = TAB_Z - plate_t - 0.05, TAB_Z + 0.05
    cuts = [lambda: m.box(*to_world(x0 - c, -hy - c, lo),
                          *to_world(x1 + c, hy + c, hi))]
    for sx in (-1, 1):
        for sy in (-1, 1):
            hx, hy2 = xm + sx * TAB_HOLE_DX / 2, sy * TAB_HOLE_DY / 2
            cuts.append(lambda hx=hx, hy2=hy2: m.cyl(
                to_world(hx, hy2, lo), to_world(hx, hy2, hi), TAB_HOLE_R))
    return cuts


def s_in(x, y, z):
    """Inner servo: shaft along +y into the board's front rim (horn face
    at y = 0), body hanging down, outside the outer box's front wall."""
    return (C + y, z - HORN_UP, AXIS_Z - x)


FRONT_IN = s_in(0, 0, TAB_Z)[1]     # outer box front wall: inside face
FRONT_OUT = FRONT_IN - T
LEFT_IN, RIGHT_IN, BACK_IN = -FR_GAP, B + FR_GAP, B + FR_GAP
LEFT_OUT, RIGHT_OUT, BACK_OUT = LEFT_IN - T, RIGHT_IN + T, BACK_IN + T


def s_out(x, y, z):
    """Outer servo: shaft along -x into the outer box's right wall (horn
    face on its outside), body hanging down, fixed to the right post."""
    return (RIGHT_OUT + HORN_UP - z, C + y, AXIS_Z - x)


def horn_hole_cuts(m, along, a0, a1, centre):
    """Hub hole + 2 screw holes for a horn, drilled along x or y."""
    cuts = []
    for d, r in ((0, HORN_HUB_R), (-HORN_SCREW_DX, HORN_SCREW_R),
                 (HORN_SCREW_DX, HORN_SCREW_R)):
        if along == "x":
            p0, p1 = (a0, centre + d, AXIS_Z), (a1, centre + d, AXIS_Z)
        else:
            p0, p1 = (centre + d, a0, AXIS_Z), (centre + d, a1, AXIS_Z)
        cuts.append(lambda p0=p0, p1=p1, r=r: m.cyl(p0, p1, r))
    return cuts


# ------------------------------------------------------- collection tray
def tray_parts():
    """Tray walls and floor as boxes: (layer, lo, hi). The left and front
    walls are split in two where the START-corner cut-out is."""
    z0, z1 = TRAY_Z0, TRAY_Z1
    cut, lip = ab.TRAY_CUT_LEN, ab.TRAY_LIP
    if ab.TRAY_LIP_AT_FLOOR:
        lz0, lz1 = z0, z0 + lip          # strip on the tray floor
    else:
        lz0, lz1 = z1 - lip, z1          # strip under the board
    return [
        ("TRAY-LEFT", (0, cut, z0), (T, B, z1)),
        ("TRAY-LEFT", (0, 0, lz0), (T, cut, lz1)),
        ("TRAY-FRONT", (T + cut, 0, z0), (B - T, T, z1)),
        ("TRAY-FRONT", (T, 0, lz0), (T + cut, T, lz1)),
        ("TRAY-RIGHT", (B - T, 0, z0), (B, B, z1)),
        ("TRAY-BACK", (T, B - T, z0), (B - T, B, z1)),
        ("TRAY-FLOOR", (0, 0, z0 - T), (B, B, z0)),
    ]


def trap_servo_box(tx, ty, th):
    """SG90 lying flat on the floor's underside, right of the opening,
    shaft pointing at the opening along the hinge line (front edge)."""
    x0 = tx + th + 0.12
    hy = ty - th                           # hinge line
    return ((x0, hy - SG90_SHAFT, -T - SG90_W),
            (x0 + SG90_H, hy - SG90_SHAFT + SG90_L, -T))


def tray_check(m, info):
    """Every hole and the trapdoor drop into the tray, nothing under the
    floor hits the tray, the ball can't roll over the lip, and the tray
    clears the base at GAME_TILT on both axes."""
    import math
    import numpy as np
    r = ab.BALL_D / 2
    for name, hx, hy, _ in info["holes"] + [("T",) + info["trap"]]:
        assert T + r <= hx <= B - T - r and T + r <= hy <= B - T - r, \
            "hole %s misses the tray" % name
    tx, ty, th = info["trap"]
    flap_low = -T - 2 * th                  # flap hanging straight down
    servo_low = trap_servo_box(tx, ty, th)[0][2]
    room = min(flap_low, servo_low) - TRAY_Z0
    assert room > ab.BALL_D, "trapdoor flap / servo too close to the tray"
    pts = np.array([p for layer, kind, d in m.solids if layer in TRAY_LAYERS
                    for p in corners(kind, d)])
    low = 1e9
    for a in (-GAME_TILT, GAME_TILT):
        for b in (-GAME_TILT, GAME_TILT):
            q = pts.copy()
            ra, rb = math.radians(a), math.radians(b)
            xx, zz = q[:, 0] - C, q[:, 2] - AXIS_Z     # inner servo
            q[:, 0] = C + xx * math.cos(ra) + zz * math.sin(ra)
            q[:, 2] = AXIS_Z - xx * math.sin(ra) + zz * math.cos(ra)
            yy, zz = q[:, 1] - C, q[:, 2] - AXIS_Z     # outer servo
            q[:, 2] = AXIS_Z + yy * math.sin(rb) + zz * math.cos(rb)
            low = min(low, q[:, 2].min())
    gap = low - BASE_Z1
    assert gap > 0.1, "tray hits the base at %.0f deg" % GAME_TILT
    where = ("on the tray floor (opening above it)" if ab.TRAY_LIP_AT_FLOOR
             else "under the board (opening at the tray floor)")
    print("tray: %.3f in deep, catches all %d holes + trapdoor; corner "
          "cut-out %.3f x %.3f in at START, %.2f in strip %s; %.2f in "
          "between the open flap and the tray floor; clears the base by "
          "%.2f in at %.0f deg tilt"
          % (ab.TRAY_H, len(info["holes"]), ab.TRAY_CUT_LEN, ab.TRAY_CUT_H,
             ab.TRAY_LIP, where, room, gap, GAME_TILT))


# --------------------------------------------------------------- the model
def build():
    m = Model()
    col = ab.COLOR
    rim = ab.RIMS
    holes = [(f, x, y, ab.HOLE_D / 2) for f, x, y in ab.HOLES]
    tx, ty, size = ab.TRAP
    th = size / 2
    trap = (tx, ty, th)
    start = ab.START

    # ---- floor: 9 holes + trapdoor opening
    cuts = [lambda h=h: m.cyl((h[1], h[2], -0.2), (h[1], h[2], 0.1), h[3])
            for h in holes]
    cuts.append(lambda: m.box(tx - th, ty - th, -0.2, tx + th, ty + th, 0.1))
    m.cut_part("FLOOR", col["FLOOR"], lambda: m.box(0, 0, -T, B, B, 0), cuts)

    # ---- board rim: front takes the inner horn, back takes the dowel
    m.cut_part("RIM-FRONT", col["RIM"],
               lambda: m.box(*rim["RIM-FRONT"][:2], 0,
                             *rim["RIM-FRONT"][2:], ab.WALL_H),
               horn_hole_cuts(m, "y", -0.05, T + 0.05, C))
    m.cut_part("RIM-BACK", col["RIM"],
               lambda: m.box(*rim["RIM-BACK"][:2], 0,
                             *rim["RIM-BACK"][2:], ab.WALL_H),
               [lambda: m.cyl((C, B - T - 0.05, AXIS_Z), (C, B + 0.05, AXIS_Z),
                              PIN_HOLE_R)])

    # ---- outer box: 4 walls
    m.cut_part("FRAME-FRONT", col["OUTER-BOX"],
               lambda: m.box(LEFT_OUT, FRONT_OUT, FR_Z0, RIGHT_OUT, FRONT_IN,
                             FR_Z1),
               mount_cuts(m, s_in, T))
    m.cut_part("FRAME-LEFT", col["OUTER-BOX"],
               lambda: m.box(LEFT_OUT, FRONT_IN, FR_Z0, LEFT_IN, BACK_IN,
                             FR_Z1),
               [lambda: m.cyl((LEFT_OUT - 0.05, C, AXIS_Z),
                              (LEFT_IN + 0.05, C, AXIS_Z), BEAR_R + 0.005)])
    m.cut_part("FRAME-RIGHT", col["OUTER-BOX"],
               lambda: m.box(RIGHT_IN, FRONT_IN, FR_Z0, RIGHT_OUT, BACK_IN,
                             FR_Z1),
               horn_hole_cuts(m, "x", RIGHT_IN - 0.05, RIGHT_OUT + 0.05, C))

    # ---- posts: right holds the outer servo, left holds the dowel
    pr0 = s_out(0, 0, TAB_Z)[0]                    # right post, under tabs
    pr1 = pr0 + POST_T
    post_top = AXIS_Z + SERVO_LEN - SHAFT_FROM_END + 0.3
    m.cut_part("POST-RIGHT", 33,
               lambda: m.box(pr0, C - POST_W / 2, BASE_Z1, pr1, C + POST_W / 2,
                             post_top),
               mount_cuts(m, s_out, POST_T))
    pl1 = LEFT_OUT - POST_GAP
    pl0 = pl1 - POST_T
    m.cut_part("POST-LEFT", 33,
               lambda: m.box(pl0, C - POST_W / 2, BASE_Z1, pl1, C + POST_W / 2,
                             AXIS_Z + 1.0),
               [lambda: m.cyl((pl0 - 0.05, C, AXIS_Z), (pl1 + 0.05, C, AXIS_Z),
                              PIN_HOLE_R)])

    # ---- parts without holes
    m.lines += ["-LAYER", "T", "*", ""]
    m.use("FRAME-BACK", col["OUTER-BOX"])      # bearing sits on its inside
    m.box(LEFT_OUT, BACK_IN, FR_Z0, RIGHT_OUT, BACK_OUT, FR_Z1)
    for name in ("RIM-LEFT", "RIM-RIGHT"):
        m.use(name, col["RIM"])
        m.box(*rim[name][:2], 0, *rim[name][2:], ab.WALL_H)
    m.use("WALLS", col["WALLS"])
    for x0, y0, x1, y1 in ab.WALLS:
        m.box(x0, y0, 0, x1, y1, ab.WALL_H)
    for layer, lo, hi in tray_parts():
        m.use(layer, col["TRAY-FLOOR" if layer == "TRAY-FLOOR"
                         else "TRAY-WALLS"])
        m.box(*lo, *hi)
    m.use("TRAPDOOR-FLAP", 14)                 # red too; darker to see it
    m.box(tx - th + TRAP_GAP, ty - th + TRAP_HINGE_GAP, -T,
          tx + th - TRAP_GAP, ty + th - TRAP_GAP, 0)
    m.use("TRAPDOOR-SERVO", 150)               # SG90 lying flat
    lo, hi = trap_servo_box(tx, ty, th)
    m.box(*lo, *hi)
    sz = (lo[2] + hi[2]) / 2                   # shaft: along the hinge line
    m.cyl((lo[0], ty - th, sz), (tx + th - 0.02, ty - th, sz), 0.08)
    m.use("BEARING-1", 8)                      # on the back wall's inside
    m.cyl((C, BACK_IN - BEAR_T, AXIS_Z), (C, BACK_IN, AXIS_Z), BEAR_R)
    m.use("BEARING-2", 8)                      # left wall bearing
    m.cyl((LEFT_IN, C, AXIS_Z), (LEFT_IN - BEAR_T, C, AXIS_Z), BEAR_R)
    m.use("PIN-AXIS1", 1)                      # dowel: board back rim
    m.cyl((C, B - T, AXIS_Z), (C, BACK_IN - 0.02, AXIS_Z), PIN_R)
    m.use("PIN-AXIS2", 5)                      # dowel: left post
    m.cyl((pl0 - 0.1, C, AXIS_Z), (LEFT_IN, C, AXIS_Z), PIN_R)
    servo(m, s_in, "SERVO-INNER", 240, "HORN-INNER")
    servo(m, s_out, "SERVO-OUTER", 240, "HORN-OUTER")
    bx0 = pl0 - 0.5
    by0 = s_in(0, 0, -SERVO_BODY_H)[1] - 1.8      # room for the controls
    bx1 = s_out(0, 0, -SERVO_BODY_H)[0] + 0.5
    by1 = BACK_OUT + 0.6
    m.use("BASE", 251)
    m.box(bx0, by0, BASE_Z0, bx1, by1, BASE_Z1)
    m.use("CONTROLS", 250)                         # joystick box, front left
    m.box(0.6, by0 + 0.2, BASE_Z1, 3.6, by0 + 1.4, BASE_Z1 + 0.9)
    m.use("JOYSTICK", 7)
    jx, jy, jz = 2.1, by0 + 0.8, BASE_Z1 + 0.9
    m.cyl((jx, jy, jz), (jx, jy, jz + 0.5), 0.1)
    m.sphere((jx, jy, jz + 0.62), 0.22)
    m.use("BALL", 8)
    m.sphere((start[0], start[1], ab.BALL_D / 2), ab.BALL_D / 2)
    m.use("LABELS", 7)
    for text, x, y, h in ab.LABELS:
        m.text(text, x, y, 0.002, h)
    m.finish()
    info = dict(base=(bx1 - bx0, by1 - by0), holes=holes, trap=trap,
                right_post=(pr0, pr1),
                frame=(LEFT_OUT, RIGHT_OUT, FRONT_OUT, BACK_OUT))
    return m, info


# ----------------------------------------------------------------- checks
def first(m, layer, kind):
    return [s[2] for s in m.solids if s[0] == layer and s[1] == kind][0]


def check(m, info):
    """Servo bodies must pass through their cutouts, horns must sit on
    their faces, dowels must be on the pivot axes and fit their holes."""
    lo, hi = first(m, "SERVO-INNER", "box")
    assert lo[1] < FRONT_OUT and hi[1] > FRONT_IN, \
        "inner servo must pass the outer box's front wall"
    lo, hi = first(m, "SERVO-OUTER", "box")
    pr0, pr1 = info["right_post"]
    assert lo[0] < pr0 and hi[0] > pr1, "outer servo must pass the right post"
    p0, p1, _ = first(m, "HORN-INNER", "cyl")
    assert abs(max(p0[1], p1[1])) < 1e-6, "inner horn must sit on the rim"
    p0, p1, _ = first(m, "HORN-OUTER", "cyl")
    assert abs(min(p0[0], p1[0]) - RIGHT_OUT) < 1e-6, \
        "outer horn must sit on the outer box's right wall"
    for name in ("PIN-AXIS1", "PIN-AXIS2"):
        p0, p1, r = first(m, name, "cyl")
        assert abs(p0[2] - AXIS_Z) < 1e-9 and abs(p1[2] - AXIS_Z) < 1e-9
        assert r < PIN_HOLE_R
    x0, x1, y0, y1 = info["frame"]
    print("checked: servos pass through their cutouts, horns sit on the "
          "rim / outer box, dowels sit on the pivot axes")
    print("outer box %.3f x %.3f in outside, base %.2f x %.2f in"
          % (x1 - x0, y1 - y0, *info["base"]))


TRAY_LAYERS = ("TRAY-LEFT", "TRAY-FRONT", "TRAY-RIGHT", "TRAY-BACK",
               "TRAY-FLOOR")
BOARD_LAYERS = ("FLOOR", "RIM-FRONT", "RIM-BACK", "RIM-LEFT", "RIM-RIGHT",
                "WALLS", "TRAPDOOR-FLAP", "TRAPDOOR-SERVO", "BALL",
                "HORN-INNER", "PIN-AXIS1") + TRAY_LAYERS
FRAME_LAYERS = ("FRAME-LEFT", "FRAME-RIGHT", "FRAME-FRONT", "FRAME-BACK",
                "SERVO-INNER", "HORN-OUTER", "BEARING-1", "BEARING-2")


def corners(kind, d):
    if kind == "box":
        (x0, y0, z0), (x1, y1, z1) = d
        return [(x, y, z) for x in (x0, x1) for y in (y0, y1)
                for z in (z0, z1)]
    if kind == "cyl":
        (p0, p1, r) = d
        return [(p[0] + dx, p[1] + dy, p[2] + dz) for p in (p0, p1)
                for dx in (-r, r) for dy in (-r, r) for dz in (-r, r)]
    (c, r) = d
    return [(c[0] + dx, c[1] + dy, c[2] + dz) for dx in (-r, r)
            for dy in (-r, r) for dz in (-r, r)]


def max_tilt(m, info):
    """Largest inner-servo tilt (degrees) before the board touches the
    outer box. The outer servo turns both together, so it can't."""
    import math
    pts = [p for layer, kind, d in m.solids if layer in BOARD_LAYERS
           for p in corners(kind, d)]
    a = 0.0
    while a < 30:
        a += 0.1
        for sgn in (1, -1):
            r = math.radians(a * sgn)
            for x, y, z in pts:
                xx = C + (x - C) * math.cos(r) + (z - AXIS_Z) * math.sin(r)
                zz = AXIS_Z - (x - C) * math.sin(r) + (z - AXIS_Z) * math.cos(r)
                if FR_Z0 <= zz <= FR_Z1 and not LEFT_IN < xx < RIGHT_IN:
                    return a - 0.1
    return a


def write_lsp(path):
    """AutoLISP: TILTDEMO swings the model in AutoCAD, servo by servo."""
    lsp = r""";; The Labyrinth - tilt animation for the 3D model built by Labyrinth_3D.scr
;; Load:  Manage tab > Applications > Load Application (APPLOAD), pick this
;;        file, Load (or drag the file onto the drawing).
;; Run:   type TILTDEMO   (TILTSPEED changes how fast it moves)
;; The model always ends back level.

(setq lab:C %(C)s  lab:AZ %(AZ)s  lab:B %(B)s  lab:tilt %(TILT)s  lab:ms 40)

(defun lab:board () (ssget "_X" '((8 . "%(BOARD)s"))))
(defun lab:frame () (ssget "_X" '((8 . "%(FRAME)s"))))

;; axis 1 (inner servo) runs front-back through the board's centre; it
;; rides on the outer box, so after the outer servo has turned b degrees
;; (about axis 2, left-right) its end points move too
(defun lab:axis1 (b / r)
  (setq r (* pi (/ b 180.0)))
  (list (list lab:C (+ lab:C (* (- 0 lab:C) (cos r)))
              (+ lab:AZ (* (- 0 lab:C) (sin r))))
        (list lab:C (+ lab:C (* (- lab:B lab:C) (cos r)))
              (+ lab:AZ (* (- lab:B lab:C) (sin r))))))

(defun lab:turn (sets p1 p2 ang)
  (command "_.ROTATE3D")
  (foreach s sets (if s (command s)))
  (command "" p1 p2 ang "_.DELAY" lab:ms))

;; swing one axis 0 -> +tilt -> -tilt -> 0, one degree per step
(defun lab:swing (sets p1 p2)
  (repeat (fix lab:tilt) (lab:turn sets p1 p2 1))
  (repeat (fix (* 2 lab:tilt)) (lab:turn sets p1 p2 -1))
  (repeat (fix lab:tilt) (lab:turn sets p1 p2 1)))

(defun c:TILTDEMO (/ echo snap board frame a2a a2b ax1)
  (setq echo (getvar "CMDECHO") snap (getvar "OSMODE"))
  (setvar "CMDECHO" 0) (setvar "OSMODE" 0)   ; snaps would move the axis points
  (setq board (lab:board) frame (lab:frame))
  (setq a2a (list 0.0 lab:C lab:AZ) a2b (list 1.0 lab:C lab:AZ))
  (princ "\n1) inner servo only: the board tips left/right, the outer box stays still")
  (setq ax1 (lab:axis1 0))
  (lab:swing (list board) (car ax1) (cadr ax1))
  (princ "\n2) outer servo only: the outer box tips front/back and carries the board")
  (lab:swing (list board frame) a2a a2b)
  (princ "\n3) both: outer box tipped, then the board tips inside it")
  (repeat (fix lab:tilt) (lab:turn (list board frame) a2a a2b 1))
  (setq ax1 (lab:axis1 lab:tilt))
  (lab:swing (list board) (car ax1) (cadr ax1))
  (repeat (fix lab:tilt) (lab:turn (list board frame) a2a a2b -1))
  (setvar "CMDECHO" echo) (setvar "OSMODE" snap)
  (princ "\nDone - back to level.")
  (princ))

(defun c:TILTSPEED (/ v)
  (setq v (getint (strcat "\nPause per step in ms <" (itoa lab:ms) ">: ")))
  (if v (setq lab:ms v))
  (princ))

(princ "\nLabyrinth animation loaded - type TILTDEMO.")
(princ)
""" % dict(C=n(C), AZ=n(AXIS_Z), B=n(B), TILT="6",
           BOARD=",".join(BOARD_LAYERS + ("LABELS",)),
           FRAME=",".join(FRAME_LAYERS))
    with open(path, "w", newline="\r\n") as fh:
        fh.write(lsp)
    print("wrote", path)


def main():
    m, info = build()
    check(m, info)
    tilt = max_tilt(m, info)
    assert tilt >= 8.0, "board hits the outer box at %.1f deg" % tilt
    print("board can tip %.1f deg on the inner servo before touching the "
          "outer box (game uses 6)" % tilt)
    tray_check(m, info)
    write_lsp(os.path.join(OUT_DIR, "Labyrinth_animate.lsp"))
    path = os.path.join(OUT_DIR, "Labyrinth_3D.scr")
    with open(path, "w", newline="\r\n") as fh:
        fh.write("\n".join(m.lines) + "\n")
    print("wrote", path, "(%d lines, %d solids)" % (len(m.lines),
                                                    len(m.solids)))


if __name__ == "__main__":
    main()
