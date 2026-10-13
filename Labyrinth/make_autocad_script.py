"""Write AutoCAD scripts that build the game as a 3D model, so nothing has
to be typed by hand. Type SCRIPT in AutoCAD and pick the file.

  Labyrinth_3D.scr        everything, in a NEW drawing (acad3d.dwt)
  Labyrinth_3D_frame.scr  only the outside (frame, pins, servos, posts,
                          base) - run it in the drawing that already has
                          the board from an earlier Labyrinth_3D.scr

Model (inches): floor 11.5 x 11.5 x 1/8 with its front-left corner at 0,0
and its top at Z = 0, holes and trapdoor cut through it, rim and maze walls
standing ON TOP of the floor (rim flush with the outside edge).

Outside, direct drive (servos on the stands): servo 1 is bolted to the
outer frame and turns the board (axis 1, front/back); servo 2 is bolted to
the front post and turns the frame (axis 2, left/right). Plain pins on the
opposite sides. Servo size is the listing's 1.58 x 0.79 x 1.60 in.

Before writing, the geometry is checked: every hole and the trapdoor must
sit fully inside the floor and must not touch the rim or any wall.
"""
import os
import sys

import make_labyrinth as ml

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else HERE
B, T = ml.BOARD, ml.T


def n(v):
    s = "%.4f" % v
    s = s.rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


def pt(x, y, z):
    return "%s,%s,%s" % (n(x), n(y), n(z))


# ------------------------------------------------------------- geometry
runs = ml.wall_runs()
rims = [r for r in runs if r["rim"]]
walls = [r for r in runs if not r["rim"]]
holes = []
for cell, f in sorted(ml.FEATURES.items()):
    cx, cy = ml.centre(cell)
    if f in ml.HOLE_D:
        holes.append((f, cx, cy, ml.HOLE_D[f] / 2))
    elif f == "T":
        trap = (cx, cy, ml.TRAP / 2)
    elif f == "S":
        start = (cx, cy + 0.12)


def check():
    problems = []
    solids = [r["rect"] for r in runs]
    for f, cx, cy, r in holes:
        if not (r < cx < B - r and r < cy < B - r):
            problems.append("hole %s at %.3f,%.3f leaves the floor" % (f, cx,
                                                                      cy))
        for x0, y0, x1, y1 in solids:
            nx, ny = min(max(cx, x0), x1), min(max(cy, y0), y1)
            if (nx - cx) ** 2 + (ny - cy) ** 2 < r * r:
                problems.append("hole %s at %.3f,%.3f hits a wall" % (f, cx,
                                                                     cy))
    tx, ty, h = trap
    for x0, y0, x1, y1 in solids:
        if x0 < tx + h and x1 > tx - h and y0 < ty + h and y1 > ty - h:
            problems.append("trapdoor hits a wall")
    for x0, y0, x1, y1 in solids:
        if x0 < -1e-9 or y0 < -1e-9 or x1 > B + 1e-9 or y1 > B + 1e-9:
            problems.append("wall off the floor")
    if problems:
        raise SystemExit("\n".join(problems))
    clear = min(min(cx - r, cy - r, B - cx - r, B - cy - r) - T
                for _, cx, cy, r in holes)
    print("checked: %d holes + trapdoor inside the floor, clear of the rim "
          "and all %d walls (closest hole is %.3f in from the rim)"
          % (len(holes), len(walls), clear))


# --------------------------------------------------------------- script
def layer(lines, name, color):
    lines += ["-LAYER", "M", name, "C", str(color), name, ""]


def box(lines, x0, y0, z0, x1, y1, z1):
    lines += ["BOX", pt(x0, y0, z0), pt(x1, y1, z1)]


# Outside structure, direct drive (servos on the stands, no pushrods).
# Both pivot axes sit at mid-rim height and cross at the board centre.
PIN_Z = 0.375
C = B / 2
FR_GAP, FR_T, FR_Z0, FR_Z1 = 0.25, T, -T, 0.875   # outer frame strips
PIN_R = 0.125                                      # 1/4 in pins
SERVO_LEN, SERVO_W, SERVO_H, SHAFT_FROM_END = 1.58, 0.79, 1.60, 0.39
HORN_R, HORN_T = 0.45, 0.1
BASE_Z0, BASE_Z1 = -5.0, -4.5


def cyl_axis(lines, p0, p1, r):
    """Cylinder lying along the line p0 -> p1."""
    lines += ["CYLINDER", pt(*p0), n(r), "A", pt(*p1)]


def frame_lines():
    i0, i1 = -FR_GAP, B + FR_GAP                  # frame inside faces
    o0, o1 = i0 - FR_T, i1 + FR_T                 # frame outside faces
    L = []
    layer(L, "FRAME", 150)
    box(L, o0, o0, FR_Z0, o1, i0, FR_Z1)          # front strip
    box(L, o0, i1, FR_Z0, o1, o1, FR_Z1)          # back strip
    box(L, o0, i0, FR_Z0, i0, i1, FR_Z1)          # left strip
    box(L, i1, i0, FR_Z0, o1, i1, FR_Z1)          # right strip

    # axis 1 (board turns in the frame, front/back tilt)
    layer(L, "PINS-AXIS1", 1)
    cyl_axis(L, (B, C, PIN_Z), (o1 + 0.1, C, PIN_Z), PIN_R)   # plain pin
    layer(L, "SERVOS", 240)                       # servo 1 rides on the frame
    box(L, o0 - SERVO_H, C - SHAFT_FROM_END, PIN_Z - SERVO_W / 2,
        o0, C - SHAFT_FROM_END + SERVO_LEN, PIN_Z + SERVO_W / 2)
    layer(L, "HORNS", 9)
    cyl_axis(L, (o0, C, PIN_Z), (-HORN_T, C, PIN_Z), 0.12)    # shaft
    cyl_axis(L, (-HORN_T, C, PIN_Z), (0, C, PIN_Z), HORN_R)   # horn on rim

    # axis 2 (frame turns on the posts, left/right tilt)
    layer(L, "PINS-AXIS2", 5)
    cyl_axis(L, (C, o1 - FR_T, PIN_Z), (C, o1 + 0.725, PIN_Z), PIN_R)
    layer(L, "SERVOS", 240)                       # servo 2 on the front post
    s_y1 = o0 - HORN_T
    s_y0 = s_y1 - SERVO_H
    box(L, C - SERVO_W / 2, s_y0, PIN_Z + SHAFT_FROM_END - SERVO_LEN,
        C + SERVO_W / 2, s_y1, PIN_Z + SHAFT_FROM_END)
    layer(L, "HORNS", 9)
    cyl_axis(L, (C, s_y1, PIN_Z), (C, o0, PIN_Z), HORN_R)     # horn on frame

    # posts and base
    layer(L, "POSTS", 33)
    post_t = 0.5
    box(L, C - 0.5, s_y0 - post_t, BASE_Z1, C + 0.5, s_y0, 1.0)   # front
    box(L, C - 0.5, o1 + 0.125, BASE_Z1, C + 0.5, o1 + 0.625, 1.0)  # back
    layer(L, "BASE", 251)
    bx0, bx1 = o0 - SERVO_H - 0.5, o1 + 1.0
    by0, by1 = s_y0 - post_t - 0.5, o1 + 1.125
    box(L, bx0, by0, BASE_Z0, bx1, by1, BASE_Z1)
    return L, (bx1 - bx0, by1 - by0)


def board_lines():
    L = []
    # cutters first, floor last, so SUBTRACT can pick the floor as "Last"
    layer(L, "CUTTERS", 1)
    for f, cx, cy, r in holes:
        L += ["CYLINDER", pt(cx, cy, -0.2), n(r), "0.3"]
    tx, ty, h = trap
    box(L, tx - h, ty - h, -0.2, tx + h, ty + h, 0.1)
    layer(L, "FLOOR", 42)
    box(L, 0, 0, -T, B, B, 0)
    L += ["SUBTRACT", "L", "", "ALL", "R", "L", ""]
    layer(L, "RIM", 22)
    for r in rims:
        x0, y0, x1, y1 = r["rect"]
        box(L, x0, y0, 0, x1, y1, r["height"])
    layer(L, "WALLS", 32)
    for r in walls:
        x0, y0, x1, y1 = r["rect"]
        box(L, x0, y0, 0, x1, y1, r["height"])
    layer(L, "BALL", 8)
    L += ["SPHERE", pt(start[0], start[1], ml.BALL_D / 2), n(ml.BALL_D / 2)]
    return L


SETUP = ["DYNMODE", "0", "OSMODE", "0", "INSUNITS", "1", "LUPREC", "4"]
FINISH = ["-VIEW", "SEISO", "VSCURRENT", "S", "ZOOM", "E", "OSMODE", "4133"]


def save(path, lines):
    with open(path, "w", newline="\r\n") as fh:
        fh.write("\n".join(lines) + "\n")
    print("wrote", path, "(%d lines)" % len(lines))


def write():
    frame, base_size = frame_lines()
    save(os.path.join(OUT_DIR, "Labyrinth_3D.scr"),
         SETUP + board_lines() + frame + FINISH)
    save(os.path.join(OUT_DIR, "Labyrinth_3D_frame.scr"),
         SETUP + frame + FINISH)
    print("base %.2f x %.2f in" % base_size)


if __name__ == "__main__":
    check()
    write()
