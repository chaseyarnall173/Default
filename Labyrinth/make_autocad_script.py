"""Write Labyrinth_3D.scr: an AutoCAD script that builds the whole game as a
3D model. In a NEW drawing (acad3d.dwt) type SCRIPT and pick the file.

Units are inches. The floor's front-left corner is at 0,0 and its top at
Z = 0. The player stands at the front (-Y side).

Board: floor with 8 holes and the trapdoor opening, the flap in the
opening, the 3 in rim and 34 maze walls (2 in tall) standing on top of the
floor, two brackets under the floor for axis 1, labels, the ball at START.

Under the board, moving with it: a collection tray. Its floor is two
flat 45-45-90 triangles that meet on the diagonal from the back-left
corner down to the front-right corner (the corner in line with START's
row and the 5 hole's column), so any ball that drops through a hole
rolls into that corner and out a notch in the tray's front wall, into a
cup on the base. A triangle is always flat, so stiff wood works.

Outside, direct drive (servos on the stands, no pushrods). Both pivot axes
sit AXIS_Z below the floor and cross under the board's centre:
  axis 1 (front/back tilt): servo 1 sits in a cutout in the frame's LEFT
      plate; its horn screws to the LEFT BRACKET under the board. A 1/4 in
      pin goes through the RIGHT BRACKET and the frame's right strip.
  axis 2 (left/right tilt): servo 2 sits in a cutout in the FRONT post; its
      horn screws to the frame's front strip. A 1/4 in pin goes through
      holes in the frame's back strip and the back post.

Servo size is the listing's 40 x 20 x 40.5 mm. Tab span, tab hole spacing
and tab height are typical 25 kg servo values - measure yours and change
the SERVO_* / TAB_* numbers.

Every part with holes is built on its own layer and cut with SUBTRACT
while every finished layer is frozen, so a cut never touches another part.
"""
import os
import sys

import make_labyrinth as ml

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else HERE
B, T = ml.BOARD, ml.T
C = B / 2                     # board centre, x and y
AXIS_Z = -0.6                 # both pivot axes, below the floor (top = 0)
PIN_R, PIN_HOLE_R = 0.125, 0.13          # 1/4 in pin, hole a bit bigger

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

FR_GAP = 0.5                  # gap between board and frame (3 sides)
FR_Z0, FR_Z1 = -1.2, ml.RIM_H # frame strips: top level with the board's rim
BAY_CLEAR = 0.25              # servo bay: room behind servo 1's body
BAY_Z1 = AXIS_Z + SERVO_W / 2 + 0.3   # servo bay walls stop just above it
LP_Z0 = -1.45                 # the frame's left plate goes a bit lower
# brackets under the floor for axis 1 (left: servo horn, right: pin)
BRK_W, BRK_T, BRK_Z0 = 1.5, 0.25, -1.1   # drop plate: width, thick, bottom
BRK_FLANGE = 1.0              # flange glued under the floor
BASE_Z0, BASE_Z1 = -6.0, -5.5   # low enough for the tray to swing
# collection tray under the floor (moves with the board)
TRAY_IN = BRK_T               # side walls start just inside the brackets
TRAY_TOP = -2 * T             # wall tops, just under the bracket flanges
TRAY_Z = {"FR": -3.4, "BL": -1.6, "BR": -2.1, "FL": -2.1}   # floor top
EXIT_W, EXIT_H = 1.0, 0.9     # ball exit notch, front wall, right end
CUP_H = 0.5                   # cup on the base under the exit
GAME_TILT = 6.0               # tilt the clearance checks allow for
POST_T = 0.5                  # posts: 1/2 in thick (4 layers of 1/8 ply)
TAB_Z = -SERVO_TAB_FROM_TOP - SERVO_TAB_T   # tab underside, local z


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

    def tri_plate(self, a, b, c, t):
        """Flat triangle a-b-c (top face) made t thick downwards: set a
        UCS in the triangle's plane, draw it, extrude, back to World."""
        import numpy as np
        a, b, c = (np.array(v, float) for v in (a, b, c))
        u = (b - a) / np.linalg.norm(b - a)
        w = c - a
        v = w - (w @ u) * u
        v /= np.linalg.norm(v)
        if np.cross(u, v)[2] < 0:              # keep the top face up
            return self.tri_plate(a, c, b, t)
        nrm = np.cross(u, v)
        bx, cx, cy = (b - a) @ u, w @ u, w @ v
        self.lines += ["UCS", pt(*a), pt(*b), pt(*c),
                       "PLINE", "0,0", "%s,0" % n(bx),
                       "%s,%s" % (n(cx), n(cy)), "C",
                       "EXTRUDE", "L", "", n(-t), "UCS", "W"]
        self.solids.append((self.layer, "prism",
                            (tuple(a), tuple(b), tuple(c), t, tuple(nrm))))

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


def s1(x, y, z):
    """Servo 1: shaft along +x into the left rim, body lying along y."""
    return (z - (BOSS_H + HORN_T), C + x, AXIS_Z + y)


FR_FRONT_OUT = -FR_GAP - T


def s2(x, y, z):
    """Servo 2: shaft along +y into the frame's front strip, body down."""
    return (C + y, z - (BOSS_H + HORN_T) + FR_FRONT_OUT, AXIS_Z - x)


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
def tray_corners():
    """Top of the tray floor at its 4 inside corners."""
    x0, x1 = TRAY_IN + T, B - TRAY_IN - T
    y0, y1 = T, B - T
    return {"FL": (x0, y0, TRAY_Z["FL"]), "FR": (x1, y0, TRAY_Z["FR"]),
            "BR": (x1, y1, TRAY_Z["BR"]), "BL": (x0, y1, TRAY_Z["BL"])}


def tray_z(x, y):
    """Height of the tray floor's top at x, y (two flat triangles)."""
    import numpy as np
    tc = tray_corners()
    x0, x1, y0, y1 = tc["FL"][0], tc["FR"][0], tc["FL"][1], tc["BL"][1]
    u, v = (x - x0) / (x1 - x0), (y - y0) / (y1 - y0)   # 0..1, BL->FR is u+v=1
    tri = ("FR", "BR", "BL") if u + v >= 1 else ("FR", "BL", "FL")
    p = [np.array(tc[k]) for k in tri]
    nrm = np.cross(p[1] - p[0], p[2] - p[0])
    return p[0][2] - (nrm[0] * (x - p[0][0]) + nrm[1] * (y - p[0][1])) / nrm[2]


def tray_check(m, info):
    """Every hole drops into the tray, the floor drains to the front-right
    corner, nothing hits the trapdoor, and the tray clears the cup and
    base at GAME_TILT on both axes."""
    import math
    import numpy as np
    tc = tray_corners()
    x0, x1, y0, y1 = tc["FL"][0], tc["FR"][0], tc["FL"][1], tc["BL"][1]
    r = ml.BALL_D / 2
    for _, hx, hy, _ in info["holes"] + [("T",) + info["trap"]]:
        assert x0 + r <= hx <= x1 - r and y0 + r <= hy <= y1 - r, \
            "hole at %.2f,%.2f misses the tray" % (hx, hy)
    # drains: heights above FR along the diagonal (h1) and at the side
    # corners (h2); each triangle slopes toward the diagonal if h2 > h1/2
    h1 = TRAY_Z["BL"] - TRAY_Z["FR"]
    for k in ("BR", "FL"):
        assert TRAY_Z[k] - TRAY_Z["FR"] > h1 / 2, "tray would trap balls"
    diag = math.hypot(x1 - x0, y1 - y0)
    valley = math.degrees(math.atan(h1 / diag))
    edge = math.degrees(math.atan((TRAY_Z["FL"] - TRAY_Z["FR"]) / (x1 - x0)))
    # trapdoor: flap (TRAP wide, hinged) and its servo stay above the tray
    tx, ty, th = info["trap"]
    lowest = min(-T - 2 * th, -1.3)            # flap swung open / servo
    room = lowest - max(tray_z(x, y) for x in (tx - th, tx + th)
                        for y in (ty - th - 0.55, ty + th))
    assert room > 0.1, "trapdoor flap would hit the tray"
    # swing: lowest tray point at +/- GAME_TILT on both axes
    pts = np.array([p for layer, kind, d in m.solids if layer in TRAY_LAYERS
                    for p in corners(kind, d)])
    low = 1e9
    for a in (-GAME_TILT, GAME_TILT):
        for b in (-GAME_TILT, GAME_TILT):
            q = pts.copy()
            ra, rb = math.radians(a), math.radians(b)
            yy, zz = q[:, 1] - C, q[:, 2] - AXIS_Z
            q[:, 1] = C + yy * math.cos(ra) - zz * math.sin(ra)
            q[:, 2] = AXIS_Z + yy * math.sin(ra) + zz * math.cos(ra)
            xx, zz = q[:, 0] - C, q[:, 2] - AXIS_Z
            q[:, 2] = AXIS_Z - xx * math.sin(rb) + zz * math.cos(rb)
            low = min(low, q[:, 2].min())
    gap = low - (BASE_Z1 + CUP_H)
    assert gap > 0.1, "tray hits the cup at %.0f deg" % GAME_TILT
    print("tray: catches all %d holes + trapdoor; floor drains to the "
          "front-right corner (valley %.1f deg, front edge %.1f deg); "
          "clears the trapdoor by %.2f in and the cup by %.2f in at "
          "%.0f deg tilt" % (len(info["holes"]), valley, edge, room, gap,
                             GAME_TILT))


# --------------------------------------------------------------- the model
def build():
    m = Model()
    runs = ml.wall_runs()
    rim = {r["name"]: r["rect"] for r in runs if r["rim"]}
    walls = [r for r in runs if not r["rim"]]
    holes, trap, start = [], None, None
    for cell, f in sorted(ml.FEATURES.items()):
        cx, cy = ml.centre(cell)
        if f in ml.HOLE_D:
            holes.append((f, cx, cy, ml.HOLE_D[f] / 2))
        elif f == "T":
            trap = (cx, cy, ml.TRAP / 2)
        elif f == "S":
            start = (cx, cy + 0.12)
    tx, ty, th = trap

    # ---- floor: 8 holes + trapdoor opening
    cuts = [lambda h=h: m.cyl((h[1], h[2], -0.2), (h[1], h[2], 0.1), h[3])
            for h in holes]
    cuts.append(lambda: m.box(tx - th, ty - th, -0.2, tx + th, ty + th, 0.1))
    m.cut_part("FLOOR", 42, lambda: m.box(0, 0, -T, B, B, 0), cuts)

    # ---- brackets under the floor: drop plates with the axis-1 holes
    y0b, y1b = C - BRK_W / 2, C + BRK_W / 2
    m.cut_part("BRACKET-LEFT", 40,
               lambda: m.box(0, y0b, BRK_Z0, BRK_T, y1b, -T - T),
               horn_hole_cuts(m, "x", -0.05, BRK_T + 0.05, C))
    m.cut_part("BRACKET-RIGHT", 40,
               lambda: m.box(B - BRK_T, y0b, BRK_Z0, B, y1b, -T - T),
               [lambda: m.cyl((B - BRK_T - 0.05, C, AXIS_Z),
                              (B + 0.05, C, AXIS_Z), PIN_HOLE_R)])

    # ---- outer frame
    fi0, fi1 = -FR_GAP, B + FR_GAP                 # inside faces
    lp1 = s1(0, 0, TAB_Z)[0]                       # left plate, under tabs
    lp0 = lp1 - T
    bay1 = s1(0, 0, -SERVO_BODY_H)[0] - BAY_CLEAR   # servo bay outer wall
    bay0 = bay1 - T
    fx0, fx1 = bay0, fi1 + T                       # frame outside, x
    fy0, fy1 = fi0 - T, fi1 + T                    # frame outside, y
    m.cut_part("FRAME-LEFT", 150,
               lambda: m.box(lp0, fi0, LP_Z0, lp1, fi1, FR_Z1),
               mount_cuts(m, s1, T))
    m.cut_part("FRAME-RIGHT", 150,
               lambda: m.box(fi1, fi0, FR_Z0, fx1, fi1, FR_Z1),
               [lambda: m.cyl((fi1 - 0.05, C, AXIS_Z), (fx1 + 0.05, C, AXIS_Z),
                              PIN_HOLE_R)])
    m.cut_part("FRAME-FRONT", 150,
               lambda: m.box(lp0, fy0, FR_Z0, fx1, fi0, FR_Z1),
               horn_hole_cuts(m, "y", fy0 - 0.05, fi0 + 0.05, C))
    m.cut_part("FRAME-BACK", 150,
               lambda: m.box(lp0, fi1, FR_Z0, fx1, fy1, FR_Z1),
               [lambda: m.cyl((C, fi1 - 0.05, AXIS_Z), (C, fy1 + 0.05, AXIS_Z),
                              PIN_HOLE_R)])

    # ---- posts
    pf1 = s2(0, 0, TAB_Z)[1]                       # front post, under tabs
    pf0 = pf1 - POST_T
    m.cut_part("POST-FRONT", 33,
               lambda: m.box(C - 0.75, pf0, BASE_Z1, C + 0.75, pf1, 0.5),
               mount_cuts(m, s2, POST_T))
    pb0, pb1 = fy1 + 0.125, fy1 + 0.125 + POST_T
    m.cut_part("POST-BACK", 33,
               lambda: m.box(C - 0.5, pb0, BASE_Z1, C + 0.5, pb1, 0.2),
               [lambda: m.cyl((C, pb0 - 0.05, AXIS_Z), (C, pb1 + 0.05, AXIS_Z),
                              PIN_HOLE_R)])

    # ---- collection tray: front wall has the exit notch
    tc = tray_corners()
    zfr = TRAY_Z["FR"]
    m.cut_part("TRAY-FRONT", 30,
               lambda: m.box(TRAY_IN, 0, zfr - T, B - TRAY_IN, T, TRAY_TOP),
               [lambda: m.box(tc["FR"][0] - EXIT_W, -0.05, zfr - 0.02,
                              tc["FR"][0] + 0.01, T + 0.05, zfr + EXIT_H)])

    # ---- parts without holes
    m.lines += ["-LAYER", "T", "*", ""]
    m.use("FRAME-BAY", 150)                        # low servo bay, left
    m.box(bay0, fi0, FR_Z0, bay1, fi1, BAY_Z1)     # outer wall
    m.box(bay0, fy0, FR_Z0, lp0, fi0, BAY_Z1)      # front side
    m.box(bay0, fi1, FR_Z0, lp0, fy1, BAY_Z1)      # back side
    for name in ("RIM-FRONT", "RIM-BACK", "RIM-LEFT", "RIM-RIGHT"):
        m.use(name, 22)
        m.box(*rim[name][:2], 0, *rim[name][2:], ml.RIM_H)
    m.use("BRACKET-LEFT", 40)                      # flanges under the floor
    m.box(0, y0b, -T - T, BRK_FLANGE, y1b, -T)
    m.use("BRACKET-RIGHT", 40)
    m.box(B - BRK_FLANGE, y0b, -T - T, B, y1b, -T)
    m.use("WALLS", 32)
    for r in walls:
        x0, y0, x1, y1 = r["rect"]
        m.box(x0, y0, 0, x1, y1, r["height"])
    m.use("TRAY-BACK", 30)
    m.box(TRAY_IN, B - T, min(TRAY_Z["BL"], TRAY_Z["BR"]) - T,
          B - TRAY_IN, B, TRAY_TOP)
    m.use("TRAY-LEFT", 30)
    m.box(TRAY_IN, T, min(TRAY_Z["FL"], TRAY_Z["BL"]) - T,
          TRAY_IN + T, B - T, TRAY_TOP)
    m.use("TRAY-RIGHT", 30)
    m.box(B - TRAY_IN - T, T, TRAY_Z["FR"] - T, B - TRAY_IN, B - T, TRAY_TOP)
    m.use("TRAY-FLOOR", 31)                    # two flat triangles
    m.tri_plate(tc["FR"], tc["BR"], tc["BL"], T)
    m.tri_plate(tc["FR"], tc["BL"], tc["FL"], T)
    m.use("TRAPDOOR-FLAP", 40)
    m.box(tx - th + ml.TRAP_GAP, ty - th + ml.TRAP_HINGE_GAP, -T,
          tx + th - ml.TRAP_GAP, ty + th - ml.TRAP_GAP, 0)
    m.use("TRAPDOOR-SERVO", 140)                   # micro servo under floor
    m.box(tx - 0.45, ty - th - 0.55, -1.3, tx + 0.45, ty - th - 0.07, -T)
    m.use("PIN-AXIS1", 1)
    m.cyl((B - BRK_T, C, AXIS_Z), (fx1 + 0.1, C, AXIS_Z), PIN_R)
    m.use("PIN-AXIS2", 5)
    m.cyl((C, fi1, AXIS_Z), (C, pb1 + 0.1, AXIS_Z), PIN_R)
    servo(m, s1, "SERVO-1", 240, "HORN-1")
    servo(m, s2, "SERVO-2", 240, "HORN-2")
    bx0 = fx0 - 0.5
    by0 = s2(0, 0, -SERVO_BODY_H)[1] - 0.5
    bx1, by1 = fx1 + 1.0, pb1 + 0.5
    m.use("BASE", 251)
    m.box(bx0, by0, BASE_Z0, bx1, by1, BASE_Z1)
    m.use("TRAY-CUP", 251)                     # catches balls from the exit
    cx0, cx1 = tc["FR"][0] - EXIT_W - 0.6, tc["FR"][0] + 0.6
    cy0, cy1 = -1.4, 0.8
    for x0_, y0_, x1_, y1_ in ((cx0, cy0, cx1, cy0 + T), (cx0, cy1 - T, cx1, cy1),
                               (cx0, cy0, cx0 + T, cy1), (cx1 - T, cy0, cx1, cy1)):
        m.box(x0_, y0_, BASE_Z1, x1_, y1_, BASE_Z1 + CUP_H)
    m.use("CONTROLS", 250)                         # joystick box, front left
    m.box(0.6, by0 + 0.2, BASE_Z1, 3.6, by0 + 1.4, BASE_Z1 + 0.9)
    m.use("JOYSTICK", 7)
    jx, jy, jz = 2.1, by0 + 0.8, BASE_Z1 + 0.9
    m.cyl((jx, jy, jz), (jx, jy, jz + 0.5), 0.1)
    m.sphere((jx, jy, jz + 0.62), 0.22)
    m.use("BALL", 8)
    m.sphere((start[0], start[1], ml.BALL_D / 2), ml.BALL_D / 2)
    m.use("LABELS", 7)
    m.text("START", start[0], start[1] - 0.52, 0.002, 0.12)
    for cell, f in sorted(ml.FEATURES.items()):
        if f in "135":
            mouth = ml.neighbours(cell)[0]
            mx, my = ml.centre(mouth)
            ux, uy = cell[1] - mouth[1], mouth[0] - cell[0]
            m.text(f, mx + 0.3 * ux, my + 0.3 * uy, 0.002, 0.26)
    m.finish()
    info = dict(base=(bx1 - bx0, by1 - by0), holes=holes, trap=trap, left_plate=(lp0, lp1),
                front_post=(pf0, pf1), frame=(fx0, fx1, fy0, fy1),
                frame_inside=(fi0, fi1))
    return m, info


# ----------------------------------------------------------------- checks
def first(m, layer, kind):
    return [s[2] for s in m.solids if s[0] == layer and s[1] == kind][0]


def check(m, info):
    """Servo bodies must pass through their cutouts, horns must sit on
    their faces, pins must be on the pivot axes and fit their holes."""
    lo, hi = first(m, "SERVO-1", "box")
    lp0, lp1 = info["left_plate"]
    assert lo[0] < lp0 and hi[0] > lp1, "servo 1 must pass the left plate"
    lo, hi = first(m, "SERVO-2", "box")
    pf0, pf1 = info["front_post"]
    assert lo[1] < pf0 and hi[1] > pf1, "servo 2 must pass the front post"
    horns = [first(m, "HORN-1", "cyl"), first(m, "HORN-2", "cyl")]
    assert abs(max(horns[0][0][0], horns[0][1][0]) - 0.0) < 1e-6, \
        "servo 1 horn must sit on the left bracket"
    assert abs(max(horns[1][0][1], horns[1][1][1]) - FR_FRONT_OUT) < 1e-6, \
        "servo 2 horn must sit on the frame's front strip"
    for name in ("PIN-AXIS1", "PIN-AXIS2"):
        p0, p1, r = first(m, name, "cyl")
        assert abs(p0[2] - AXIS_Z) < 1e-9 and abs(p1[2] - AXIS_Z) < 1e-9
        assert r < PIN_HOLE_R
    fx0, fx1, fy0, fy1 = info["frame"]
    print("checked: servos pass through their cutouts, horns sit on the "
          "bracket / frame, pins sit on the pivot axes")
    print("frame %.3f x %.3f in outside, base %.2f x %.2f in"
          % (fx1 - fx0, fy1 - fy0, *info["base"]))


TRAY_LAYERS = ("TRAY-FRONT", "TRAY-BACK", "TRAY-LEFT", "TRAY-RIGHT",
               "TRAY-FLOOR")
BOARD_LAYERS = ("FLOOR", "RIM-FRONT", "RIM-BACK", "RIM-LEFT", "RIM-RIGHT",
                "WALLS", "BRACKET-LEFT", "BRACKET-RIGHT", "TRAPDOOR-FLAP",
                "TRAPDOOR-SERVO", "BALL", "HORN-1") + TRAY_LAYERS
FRAME_LAYERS = ("FRAME-LEFT", "FRAME-RIGHT", "FRAME-FRONT", "FRAME-BACK",
                "FRAME-BAY", "SERVO-1", "PIN-AXIS1", "HORN-2")


def corners(kind, d):
    if kind == "box":
        (x0, y0, z0), (x1, y1, z1) = d
        return [(x, y, z) for x in (x0, x1) for y in (y0, y1)
                for z in (z0, z1)]
    if kind == "cyl":
        (p0, p1, r) = d
        return [(p[0] + dx, p[1] + dy, p[2] + dz) for p in (p0, p1)
                for dx in (-r, r) for dy in (-r, r) for dz in (-r, r)]
    if kind == "prism":
        a, b, c, t, nrm = d
        return [tuple(p[i] - k * t * nrm[i] for i in range(3))
                for p in (a, b, c) for k in (0, 1)]
    (c, r) = d
    return [(c[0] + dx, c[1] + dy, c[2] + dz) for dx in (-r, r)
            for dy in (-r, r) for dz in (-r, r)]


def max_tilt(m, info):
    """Largest axis-1 tilt (degrees) before the board touches the frame.
    Axis 2 never moves the board against the frame - they turn together."""
    import math
    fi0, fi1 = info["frame_inside"]
    pts = [p for layer, kind, d in m.solids if layer in BOARD_LAYERS
           for p in corners(kind, d)]
    a = 0.0
    while a < 30:
        a += 0.1
        for sgn in (1, -1):
            r = math.radians(a * sgn)
            for x, y, z in pts:
                yy = C + (y - C) * math.cos(r) - (z - AXIS_Z) * math.sin(r)
                zz = AXIS_Z + (y - C) * math.sin(r) + (z - AXIS_Z) * math.cos(r)
                if FR_Z0 <= zz <= FR_Z1 and not fi0 < yy < fi1:
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

;; axis 1 runs left-right under the board; it rides on the frame, so after
;; the frame has turned b degrees on axis 2 its end points move too
(defun lab:axis1 (b / r)
  (setq r (* pi (/ b 180.0)))
  (list (list (+ lab:C (* (- 0 lab:C) (cos r))) lab:C
              (- lab:AZ (* (- 0 lab:C) (sin r))))
        (list (+ lab:C (* (- lab:B lab:C) (cos r))) lab:C
              (- lab:AZ (* (- lab:B lab:C) (sin r))))))

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
  (setq a2a (list lab:C 0.0 lab:AZ) a2b (list lab:C 1.0 lab:AZ))
  (princ "\n1) servo 1 only: the board tips front/back, the frame stays still")
  (setq ax1 (lab:axis1 0))
  (lab:swing (list board) (car ax1) (cadr ax1))
  (princ "\n2) servo 2 only: the frame tips left/right and carries the board")
  (lab:swing (list board frame) a2a a2b)
  (princ "\n3) both: frame tipped, then the board tips inside it")
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
    assert tilt >= 8.0, "board hits the frame at %.1f deg" % tilt
    print("board can tip %.1f deg on axis 1 before touching the frame "
          "(game uses 6)" % tilt)
    tray_check(m, info)
    write_lsp(os.path.join(OUT_DIR, "Labyrinth_animate.lsp"))
    path = os.path.join(OUT_DIR, "Labyrinth_3D.scr")
    with open(path, "w", newline="\r\n") as fh:
        fh.write("\n".join(m.lines) + "\n")
    print("wrote", path, "(%d lines, %d solids)" % (len(m.lines),
                                                    len(m.solids)))


if __name__ == "__main__":
    main()
