"""Write Labyrinth_3D.scr: an AutoCAD script that builds the maze board as a
3D model, so nothing has to be typed by hand.

In a NEW drawing (acad3d.dwt), type SCRIPT and pick Labyrinth_3D.scr.

Model (inches): floor 11.5 x 11.5 x 1/8 with its front-left corner at 0,0
and its top at Z = 0, holes and trapdoor cut through it, rim and maze walls
standing ON TOP of the floor (rim flush with the outside edge).

Before writing, the geometry is checked: every hole and the trapdoor must
sit fully inside the floor and must not touch the rim or any wall.
"""
import os
import sys

import make_labyrinth as ml

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE,
                                                         "Labyrinth_3D.scr")
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


def write():
    L = ["DYNMODE", "0", "OSMODE", "0", "INSUNITS", "1", "LUPREC", "4"]
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
    L += ["-VIEW", "SEISO", "VSCURRENT", "S", "ZOOM", "E", "OSMODE", "4133"]
    with open(OUT, "w", newline="\r\n") as fh:
        fh.write("\n".join(L) + "\n")
    print("wrote", OUT, "(%d lines)" % len(L))


if __name__ == "__main__":
    check()
    write()
