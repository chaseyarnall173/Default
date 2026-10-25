"""Picture of the collection tray under the board, from Labyrinth_3D.scr.

    python3 make_tray_views.py   ->  Labyrinth_tray.png

Left: the model seen from below the front-right corner (base, posts and
the frame's front strip hidden). Right: the tray floor from above with
its heights and which way a dropped ball rolls, plus the cut list.
"""
import math
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import make_autocad_script as cad
import make_axis_views as views
import make_labyrinth as ml

HERE = os.path.dirname(os.path.abspath(__file__))
B, T = cad.B, cad.T
HIDE = {"BASE", "POST-FRONT", "POST-BACK", "SERVO-2", "CONTROLS", "JOYSTICK",
        "FRAME-FRONT", "FRAME-BACK", "FRAME-LEFT", "FRAME-RIGHT", "FRAME-BAY",
        "HORN-2", "PIN-AXIS2", "PIN-AXIS1", "SERVO-1", "HORN-1", "TRAY-CUP"}


def length(p, q):
    return math.dist(p, q)


def cut_list():
    tc = cad.tray_corners()
    rows = []
    for name, k in (("right triangle", "BR"), ("left triangle", "FL")):
        a, b, c = tc["FR"], tc[k], tc["BL"]
        rows.append((name, "sides %.3f (FR-%s), %.3f (%s-BL), %.3f "
                     "(diagonal)" % (length(a, b), k, length(b, c), k,
                                     length(a, c))))
    return rows


def model_view(ax, solids):
    keep = [s for s in solids if s[1] not in HIDE]
    views.draw(ax, views.prepare(keep), 0, 0, axes=False)
    ax.set_xlim(-1.5, B + 1.5)
    ax.set_ylim(-1.5, B + 1.5)
    ax.set_zlim(-4.5, 2.5)
    ax.set_box_aspect((B + 3, B + 3, 7), zoom=1.25)
    ax.view_init(elev=-24, azim=-52)


def drain_map(ax):
    tc = cad.tray_corners()
    x0, x1, y0, y1 = tc["FL"][0], tc["FR"][0], tc["FL"][1], tc["BL"][1]
    xs, ys = np.linspace(x0, x1, 120), np.linspace(y0, y1, 120)
    Z = np.array([[cad.tray_z(x, y) for x in xs] for y in ys])
    im = ax.contourf(xs, ys, Z, levels=14, cmap="YlOrBr_r")
    ax.contour(xs, ys, Z, levels=14, colors="k", linewidths=0.3, alpha=0.4)
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.03,
                 label="tray floor height (in, floor top = 0)")
    gx, gy = np.meshgrid(np.linspace(x0 + 0.8, x1 - 0.8, 9),
                         np.linspace(y0 + 0.8, y1 - 0.8, 9))
    e = 0.05
    for x, y in zip(gx.ravel(), gy.ravel()):
        dx = (cad.tray_z(x + e, y) - cad.tray_z(x - e, y)) / (2 * e)
        dy = (cad.tray_z(x, y + e) - cad.tray_z(x, y - e)) / (2 * e)
        n = math.hypot(dx, dy)
        ax.annotate("", (x - 0.55 * dx / n, y - 0.55 * dy / n), (x, y),
                    arrowprops=dict(arrowstyle="->", color="#1f4e8c", lw=1))
    ax.plot([x0, x1], [y1, y0], "--", color="#c0392b", lw=2)
    ax.text(3.4, 8.4, "valley: the two\ntriangles meet here", rotation=-45,
            color="#c0392b", fontsize=9, ha="center", weight="bold")
    for cell, f in sorted(ml.FEATURES.items()):
        cx, cy = ml.centre(cell)
        if f in ml.HOLE_D:
            ax.add_patch(plt.Circle((cx, cy), ml.HOLE_D[f] / 2, fill=False,
                                    lw=1.5, color="k"))
            ax.text(cx, cy, f if f in "135" else "", ha="center",
                    va="center", fontsize=9, weight="bold")
        elif f == "T":
            ax.add_patch(plt.Rectangle((cx - ml.TRAP / 2, cy - ml.TRAP / 2),
                                       ml.TRAP, ml.TRAP, fill=False, lw=1.5,
                                       ls=":", color="k"))
        elif f == "S":
            ax.text(cx, cy, "START", ha="center", va="center", fontsize=8,
                    weight="bold", color="#2e7d32")
    ax.annotate("balls collect here", (x1 - 0.2, y0 + 0.2), (x1 - 4.2, -0.8),
                color="#2e7d32", weight="bold", fontsize=9,
                arrowprops=dict(arrowstyle="->", color="#2e7d32", lw=1.5))
    for k, (dx, dy) in {"FL": (-0.2, -0.5), "FR": (0.2, 0.35),
                        "BR": (0.2, 0.3), "BL": (-0.2, 0.3)}.items():
        x, y, z = tc[k]
        ax.text(x + dx, y + dy, "%s  %.1f" % (k, z), fontsize=9,
                ha="right" if dx < 0 else "left", weight="bold")
    ax.set_xlim(-1.2, B + 1.6)
    ax.set_ylim(-1.1, B + 0.8)
    ax.set_aspect("equal")
    ax.set_xlabel("x (in)   - front edge at the bottom, where the player "
                  "stands -")
    ax.set_title("Tray floor from above: arrows = way a dropped ball rolls",
                 fontsize=12, weight="bold")


def main():
    solids = views.parse(os.path.join(HERE, "Labyrinth_3D.scr"))
    fig = plt.figure(figsize=(17, 9.2), dpi=110)
    fig.suptitle("Collection tray under the board - slopes to the "
                 "front-right corner", fontsize=17, weight="bold", y=0.985)
    ax = fig.add_axes([0.0, 0.2, 0.5, 0.72], projection="3d")
    model_view(ax, solids)
    fig.text(0.25, 0.92, "Board + tray seen from below, front-right corner "
             "nearest you (frame, servos, base hidden)", ha="center", fontsize=11)
    drain_map(fig.add_axes([0.53, 0.2, 0.42, 0.7]))
    rows = cut_list()
    fig.text(0.04, 0.165, "Cut list (inches) - just the two floor triangles "
             "(walls not in this version)",
             fontsize=11, weight="bold")
    for k, (name, size) in enumerate(rows):
        fig.text(0.04, 0.13 - 0.032 * k,
                 "%-15s %s" % (name, size), fontsize=10,
                 family="DejaVu Sans Mono")
    fig.text(0.04, 0.02, "Lowest point %.1f in under the floor top; the "
             "tray swings with the board and clears the base at %d deg. "
             "Valley slope %.1f deg - tilt the board toward the "
             "front-right corner to empty it." % (
                 -cad.TRAY_Z["FR"], cad.GAME_TILT, math.degrees(math.atan(
                     (cad.TRAY_Z["BL"] - cad.TRAY_Z["FR"]) / math.dist(
                         cad.tray_corners()["BL"][:2],
                         cad.tray_corners()["FR"][:2])))),
             fontsize=10, color="#333")
    path = os.path.join(HERE, "Labyrinth_tray.png")
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    print("wrote", path)
    for name, size in rows:
        print("  %-15s %s" % (name, size))


if __name__ == "__main__":
    main()
