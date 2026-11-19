"""Picture of the collection tray under the board, from Labyrinth_3D.scr.

    python3 make_tray_views.py   ->  Labyrinth_tray.png

Left: board + tray from below, the START corner nearest, so the corner
cut-out shows. Right: the five tray pieces flat, with their sizes.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import as_built as ab
import make_autocad_script as cad
import make_axis_views as views

HERE = os.path.dirname(os.path.abspath(__file__))
B, T = ab.BOARD, ab.T


def piece(ax, x, y, length, height, title, cut=False):
    """One wall piece drawn flat at x, y: notch at its left end if cut.
    The strip under the notch is at the bottom, the way it is glued."""
    h, lip, cl = height, ab.TRAY_LIP, ab.TRAY_CUT_LEN
    if cut:
        xs = [0, length, length, cl, cl, 0, 0]
        ys = [0, 0, h, h, lip, lip, 0]
    else:
        xs = [0, length, length, 0, 0]
        ys = [0, 0, h, h, 0]
    ax.fill([x + v for v in xs], [y + v for v in ys], color="#e3c03a",
            ec="k", lw=1.2)
    ax.text(x + length / 2, y + h + 0.25, title, ha="center",
            fontsize=10.5, weight="bold")
    ax.text(x + length / 2, y - 0.3, "%.3f" % length, ha="center",
            va="top", fontsize=9)
    ax.text(x + length + 0.15, y + h / 2, "%.3f" % h, va="center",
            fontsize=9)
    if cut:
        ax.text(x + cl / 2, y + lip + 0.15, "%.3f x %.3f\ncut out"
                % (cl, ab.TRAY_CUT_H), ha="center", fontsize=8.5,
                color="#a0281e")


def main():
    solids = views.parse(os.path.join(HERE, "Labyrinth_3D.scr"))
    keep = views.BOARD_ONLY
    fig = plt.figure(figsize=(17, 8.6), dpi=110)
    fig.suptitle("Collection tray - a box under the board, corner cut out "
                 "at START", fontsize=17, weight="bold", y=0.985)
    ax = fig.add_axes([0.0, 0.05, 0.5, 0.82], projection="3d")
    views.draw(ax, views.prepare([s for s in solids if s[1].startswith(keep)],
                                 real=True), 0, 0, pivots=False)
    ax.set_xlim(-0.5, B + 0.5)
    ax.set_ylim(-0.5, B + 0.5)
    ax.set_zlim(-3.0, 2.2)
    ax.set_box_aspect((B + 1, B + 1, 5.2), zoom=1.25)
    ax.view_init(elev=-20, azim=-125)
    fig.text(0.25, 0.9, "From below, START corner nearest you", ha="center",
             fontsize=12)

    ax = fig.add_axes([0.52, 0.06, 0.46, 0.84])
    h = ab.TRAY_H
    piece(ax, 0, 11.4, B, h, "LEFT (x1)", cut=True)
    piece(ax, 0, 7.4, B - 2 * T, h, "FRONT (x1)", cut=True)
    piece(ax, 0, 3.4, B - 2 * T, h, "BACK (x1)")
    piece(ax, 0, -0.6, B, h, "RIGHT (x1)")
    ax.text(0, -2.2, "FLOOR (x1): %.3f x %.3f   - the four walls stand on "
            "it, in line with the rim above" % (B, B), fontsize=10.5,
            weight="bold")
    ax.text(0, -3.0, "The %.2f in strip under each cut-out sits on the tray "
            "floor, so the %.0f mm ball stops in the corner\nand you reach "
            "in through the opening to take it." % (ab.TRAY_LIP,
                                                     ab.BALL_D * 25.4),
            fontsize=10, color="#333", va="top")
    ax.set_xlim(-0.5, B + 1.5)
    ax.set_ylim(-4.2, 14.6)
    ax.set_aspect("equal")
    ax.axis("off")
    path = os.path.join(HERE, "Labyrinth_tray.png")
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    print("wrote", path)


if __name__ == "__main__":
    cad.main()
    main()
