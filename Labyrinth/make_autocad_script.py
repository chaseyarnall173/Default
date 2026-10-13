"""Write Labyrinth_3D.scr: an AutoCAD script that builds the whole game as a
3D model. In a NEW drawing (acad3d.dwt) type SCRIPT and pick the file.

Units are inches. The floor's front-left corner is at 0,0 and its top at
Z = 0. The player stands at the front (-Y side).

Board: floor with 8 holes and the trapdoor opening, the flap in the
opening, the rim and 34 maze walls standing on top of the floor, labels,
the ball at START.

Outside, direct drive (servos on the stands, no pushrods). Both pivot axes
are 3/8 in above the floor (half the rim height) and cross at the board's
centre:
  axis 1 (front/back tilt): servo 1 sits in a cutout in the frame's LEFT
      plate; its horn screws to the board's left rim. A 1/4 in pin goes
      through holes in the right rim and the frame's right strip.
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
PIN_Z = 0.375                 # both pivot axes: half the 3/4 in rim height
PIN_R, PIN_HOLE_R = 0.125, 0.13          # 1/4 in pin, hole a bit bigger

# servo, local frame: shaft along +z at x = y = 0, top face at z = 0
SERVO_LEN, SERVO_W, SERVO_BODY_H = 1.58, 0.79, 1.48
SHAFT_FROM_END = 0.39         # shaft centre from the near end of the body
SERVO_TAB_SPAN = 2.15         # tab tip to tab tip
SERVO_TAB_FROM_TOP, SERVO_TAB_T = 0.49, 0.1
TAB_HOLE_DX, TAB_HOLE_DY, TAB_HOLE_R = 1.95, 0.39, 0.09
BOSS_R, BOSS_H = 0.24, 0.12
HORN_R, HORN_T = 0.36, 0.1
HORN_SCREW_R, HORN_SCREW_DX, HORN_HUB_R = 0.05, 0.3, 0.1
WINDOW_CLEAR = 0.01           # servo cutout is this much bigger all round

FR_GAP = 0.25                 # gap between board and frame (3 sides)
FR_Z0, FR_Z1 = -0.125, 0.875  # frame strips: 1/8 thick, 1 in tall
BASE_Z0, BASE_Z1 = -5.0, -4.5
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
def servo(m, to_world, layer, color):
    """Servo body, mounting tabs, output boss and round horn."""
    x0, x1 = -SHAFT_FROM_END, SERVO_LEN - SHAFT_FROM_END
    xm, hy = (x0 + x1) / 2, SERVO_W / 2
    m.use(layer, color)
    m.box(*to_world(x0, -hy, -SERVO_BODY_H), *to_world(x1, hy, 0))
    m.box(*to_world(xm - SERVO_TAB_SPAN / 2, -hy, TAB_Z),
          *to_world(xm + SERVO_TAB_SPAN / 2, hy, -SERVO_TAB_FROM_TOP))
    m.cyl(to_world(0, 0, 0), to_world(0, 0, BOSS_H), BOSS_R)
    m.use("HORNS", 9)
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
    return (z - (BOSS_H + HORN_T), C + x, PIN_Z + y)


FR_FRONT_OUT = -FR_GAP - T


def s2(x, y, z):
    """Servo 2: shaft along +y into the frame's front strip, body down."""
    return (C + y, z - (BOSS_H + HORN_T) + FR_FRONT_OUT, PIN_Z - x)


def horn_hole_cuts(m, along, a0, a1, centre):
    """Hub hole + 2 screw holes for a horn, drilled along x or y."""
    cuts = []
    for d, r in ((0, HORN_HUB_R), (-HORN_SCREW_DX, HORN_SCREW_R),
                 (HORN_SCREW_DX, HORN_SCREW_R)):
        if along == "x":
            p0, p1 = (a0, centre + d, PIN_Z), (a1, centre + d, PIN_Z)
        else:
            p0, p1 = (centre + d, a0, PIN_Z), (centre + d, a1, PIN_Z)
        cuts.append(lambda p0=p0, p1=p1, r=r: m.cyl(p0, p1, r))
    return cuts


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

    # ---- right rim: axis-1 pin hole
    rx0, ry0, rx1, ry1 = rim["RIM-RIGHT"]
    m.cut_part("RIM-RIGHT", 22,
               lambda: m.box(rx0, ry0, 0, rx1, ry1, ml.RIM_H),
               [lambda: m.cyl((rx0 - 0.05, C, PIN_Z), (rx1 + 0.05, C, PIN_Z),
                              PIN_HOLE_R)])

    # ---- left rim: holes for servo 1's horn
    lx0, ly0, lx1, ly1 = rim["RIM-LEFT"]
    m.cut_part("RIM-LEFT", 22,
               lambda: m.box(lx0, ly0, 0, lx1, ly1, ml.RIM_H),
               horn_hole_cuts(m, "x", lx0 - 0.05, lx1 + 0.05, C))

    # ---- outer frame
    fi0, fi1 = -FR_GAP, B + FR_GAP                 # inside faces
    lp1 = s1(0, 0, TAB_Z)[0]                       # left plate, under tabs
    lp0 = lp1 - T
    fx0, fx1 = lp0, fi1 + T                        # frame outside, x
    fy0, fy1 = fi0 - T, fi1 + T                    # frame outside, y
    m.cut_part("FRAME-LEFT", 150,
               lambda: m.box(lp0, fi0, -0.45, lp1, fi1, 1.2),
               mount_cuts(m, s1, T))
    m.cut_part("FRAME-RIGHT", 150,
               lambda: m.box(fi1, fi0, FR_Z0, fx1, fi1, FR_Z1),
               [lambda: m.cyl((fi1 - 0.05, C, PIN_Z), (fx1 + 0.05, C, PIN_Z),
                              PIN_HOLE_R)])
    m.cut_part("FRAME-FRONT", 150,
               lambda: m.box(fx0, fy0, FR_Z0, fx1, fi0, FR_Z1),
               horn_hole_cuts(m, "y", fy0 - 0.05, fi0 + 0.05, C))
    m.cut_part("FRAME-BACK", 150,
               lambda: m.box(fx0, fi1, FR_Z0, fx1, fy1, FR_Z1),
               [lambda: m.cyl((C, fi1 - 0.05, PIN_Z), (C, fy1 + 0.05, PIN_Z),
                              PIN_HOLE_R)])

    # ---- posts
    pf1 = s2(0, 0, TAB_Z)[1]                       # front post, under tabs
    pf0 = pf1 - POST_T
    m.cut_part("POST-FRONT", 33,
               lambda: m.box(C - 0.75, pf0, BASE_Z1, C + 0.75, pf1, 1.4),
               mount_cuts(m, s2, POST_T))
    pb0, pb1 = fy1 + 0.125, fy1 + 0.125 + POST_T
    m.cut_part("POST-BACK", 33,
               lambda: m.box(C - 0.5, pb0, BASE_Z1, C + 0.5, pb1, 1.0),
               [lambda: m.cyl((C, pb0 - 0.05, PIN_Z), (C, pb1 + 0.05, PIN_Z),
                              PIN_HOLE_R)])

    # ---- parts without holes
    m.lines += ["-LAYER", "T", "*", ""]
    m.use("RIM-FRONT", 22)
    m.box(*rim["RIM-FRONT"][:2], 0, *rim["RIM-FRONT"][2:], ml.RIM_H)
    m.use("RIM-BACK", 22)
    m.box(*rim["RIM-BACK"][:2], 0, *rim["RIM-BACK"][2:], ml.RIM_H)
    m.use("WALLS", 32)
    for r in walls:
        x0, y0, x1, y1 = r["rect"]
        m.box(x0, y0, 0, x1, y1, r["height"])
    m.use("TRAPDOOR-FLAP", 40)
    m.box(tx - th + ml.TRAP_GAP, ty - th + ml.TRAP_HINGE_GAP, -T,
          tx + th - ml.TRAP_GAP, ty + th - ml.TRAP_GAP, 0)
    m.use("TRAPDOOR-SERVO", 140)                   # micro servo under floor
    m.box(tx - 0.45, ty - th - 0.55, -1.3, tx + 0.45, ty - th - 0.07, -T)
    m.use("PIN-AXIS1", 1)
    m.cyl((rx0, C, PIN_Z), (fx1 + 0.1, C, PIN_Z), PIN_R)
    m.use("PIN-AXIS2", 5)
    m.cyl((C, fi1, PIN_Z), (C, pb1 + 0.1, PIN_Z), PIN_R)
    servo(m, s1, "SERVO-1", 240)
    servo(m, s2, "SERVO-2", 240)
    bx0 = s1(0, 0, -SERVO_BODY_H)[0] - 0.5
    by0 = s2(0, 0, -SERVO_BODY_H)[1] - 0.5
    bx1, by1 = fx1 + 1.0, pb1 + 0.5
    m.use("BASE", 251)
    m.box(bx0, by0, BASE_Z0, bx1, by1, BASE_Z1)
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
    info = dict(base=(bx1 - bx0, by1 - by0), left_plate=(lp0, lp1),
                front_post=(pf0, pf1), frame=(fx0, fx1, fy0, fy1))
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
    horns = [s[2] for s in m.solids if s[0] == "HORNS"]
    assert abs(max(horns[0][0][0], horns[0][1][0]) - 0.0) < 1e-6, \
        "servo 1 horn must sit on the left rim"
    assert abs(max(horns[1][0][1], horns[1][1][1]) - FR_FRONT_OUT) < 1e-6, \
        "servo 2 horn must sit on the frame's front strip"
    for name in ("PIN-AXIS1", "PIN-AXIS2"):
        p0, p1, r = first(m, name, "cyl")
        assert abs(p0[2] - PIN_Z) < 1e-9 and abs(p1[2] - PIN_Z) < 1e-9
        assert r < PIN_HOLE_R
    fx0, fx1, fy0, fy1 = info["frame"]
    print("checked: servos pass through their cutouts, horns sit on the "
          "rim / frame, pins sit on the pivot axes")
    print("frame %.3f x %.3f in outside, base %.2f x %.2f in"
          % (fx1 - fx0, fy1 - fy0, *info["base"]))


def main():
    m, info = build()
    check(m, info)
    path = os.path.join(OUT_DIR, "Labyrinth_3D.scr")
    with open(path, "w", newline="\r\n") as fh:
        fh.write("\n".join(m.lines) + "\n")
    print("wrote", path, "(%d lines, %d solids)" % (len(m.lines),
                                                    len(m.solids)))


if __name__ == "__main__":
    main()
