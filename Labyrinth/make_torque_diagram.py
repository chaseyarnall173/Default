"""Picture of what '25 kg-cm' means on a servo, and on the Labyrinth board.

    python3 make_torque_diagram.py  ->  Labyrinth_servo_torque.png
"""
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle, Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
RED, DARK, HORN, BLUE = "#c0392b", "#2b2b2b", "#e8e8e8", "#1f5fae"


def servo(ax, x, y, scale=1.0):
    """Servo seen from the front: body, mounting tabs, output shaft."""
    w, h = 2.0 * scale, 4.0 * scale
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h + 0.4 * scale), w, h,
                                boxstyle="round,pad=0.05", fc="#b3123f",
                                ec="k", lw=1.5))
    ax.add_patch(Rectangle((x - 1.6 * scale, y - 0.7 * scale), 3.2 * scale,
                           0.35 * scale, fc="#222", ec="k"))
    ax.add_patch(Circle((x, y), 0.45 * scale, fc="#999", ec="k", lw=1.5))


def weight(ax, x, y, label, size=1.0):
    ax.plot([x, x], [y, y - 1.2], color="k", lw=1.5)
    ax.add_patch(Polygon([[x - 0.7 * size, y - 1.2], [x + 0.7 * size, y - 1.2],
                          [x + 0.9 * size, y - 2.4 * size],
                          [x - 0.9 * size, y - 2.4 * size]],
                         fc="#555", ec="k"))
    ax.text(x, y - 1.2 - 0.65 * size, label, ha="center", va="center",
            color="w", weight="bold", fontsize=12)


def dim(ax, x0, x1, y, text, color=RED):
    ax.annotate("", (x1, y), (x0, y), arrowprops=dict(arrowstyle="<->",
                color=color, lw=2))
    ax.text((x0 + x1) / 2, y + 0.3, text, ha="center", color=color,
            weight="bold", fontsize=13)


def panel_servo(ax, arm, kg, title):
    sx, sy = 2.0, 6.0
    servo(ax, sx, sy)
    ax.add_patch(FancyBboxPatch((sx - 0.5, sy - 0.25), arm + 1.0, 0.5,
                                boxstyle="round,pad=0.1", fc=HORN, ec="k",
                                lw=1.5, zorder=3))
    ax.add_patch(Circle((sx, sy), 0.18, fc="k", zorder=4))
    for k in range(1, int(arm) + 1):
        ax.add_patch(Circle((sx + k, sy), 0.08, fc="#777", zorder=4))
    ax.add_patch(Circle((sx + arm, sy), 0.12, fc="k", zorder=4))
    dim(ax, sx, sx + arm, sy + 1.0, "%g cm" % arm)
    ax.plot([sx, sx], [sy, sy + 1.3], ls=":", color=RED)
    ax.plot([sx + arm, sx + arm], [sy, sy + 1.3], ls=":", color=RED)
    weight(ax, sx + arm, sy - 0.1, "%g kg" % kg, 1.0)
    ax.annotate("shaft centre\n(measure from here)", (sx, sy), (sx - 1.2, sy + 2.8),
                ha="center", fontsize=10.5, weight="bold",
                arrowprops=dict(arrowstyle="->", lw=1.3))
    ax.annotate("horn", (sx + arm * 0.55, sy + 0.25), (sx + arm * 0.55 + 1.2,
                sy + 2.6), fontsize=10.5, weight="bold",
                arrowprops=dict(arrowstyle="->", lw=1.3))
    ax.text(sx, sy - 4.4, "SERVO", ha="center", color="w", weight="bold")
    ax.text(6.5, 0.4, "%g kg x %g cm = 25 kg-cm" % (kg, arm), ha="center",
            fontsize=13, weight="bold", color=BLUE)
    ax.set_title(title, fontsize=14, weight="bold")
    ax.set_xlim(-1, 14)
    ax.set_ylim(0, 10)
    ax.set_aspect("equal")
    ax.axis("off")


def panel_board(ax):
    px, py = 6.5, 7.0                    # pivot (servo shaft)
    t = math.radians(7)
    L, d = 5.8, 1.2                      # half board width, com below pivot
    def rot(x, y):
        return (px + x * math.cos(t) - y * math.sin(t),
                py + x * math.sin(t) + y * math.cos(t))
    floor = [rot(-L, -1.0), rot(L, -1.0), rot(L, -1.3), rot(-L, -1.3)]
    ax.add_patch(Polygon(floor, fc="#d9a066", ec="k"))
    for xx in (-L, L):
        ax.add_patch(Polygon([rot(xx - 0.15 * (xx > 0), -1.0),
                              rot(xx + 0.15 * (xx < 0), -1.0),
                              rot(xx + 0.15 * (xx < 0), 1.0),
                              rot(xx - 0.15 * (xx > 0), 1.0)],
                             fc="#b07a40", ec="k"))
    tray = [rot(-L, -1.4), rot(L, -1.4), rot(0, -2.6)]
    ax.add_patch(Polygon(tray, fc="#e8c48a", ec="k", alpha=0.9))
    ax.add_patch(Circle((px, py), 0.35, fc="#999", ec="k", lw=1.5, zorder=5))
    ax.add_patch(Circle((px, py), 0.12, fc="k", zorder=6))
    cx, cy = rot(0.9, -d)                # centre of mass, off-centre (drawn bigger)
    ax.add_patch(Circle((cx, cy), 0.28, fc=RED, ec="k", zorder=6))
    ax.annotate("", (cx, 2.0), (cx, cy - 0.3), arrowprops=dict(
                arrowstyle="-|>", color="k", lw=2.2))
    ax.text(cx + 0.25, 2.6, "weight\n0.7 kg", fontsize=10.5, weight="bold")
    ax.plot([px, px], [py, 2.0], ls="--", color=BLUE)
    ax.text(px - 0.25, 2.3, "straight\ndown from\nthe pivot", ha="right",
            fontsize=9.5, color=BLUE)
    dim(ax, px, cx, 3.6, "", color=RED)
    ax.annotate("lever arm ~0.7 cm", ((px + cx) / 2, 3.6), (px - 4.3, 4.6),
                color=RED, weight="bold", fontsize=12,
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.3))
    ax.annotate("servo shaft = pivot", (px, py), (px - 3.5, py + 2.0),
                fontsize=10.5, weight="bold",
                arrowprops=dict(arrowstyle="->", lw=1.3))
    ax.annotate("centre of mass\n(where all the\nweight acts)", (cx, cy),
                (cx + 2.2, cy - 2.6),
                fontsize=10.5, weight="bold", color=RED,
                arrowprops=dict(arrowstyle="->", lw=1.3, color=RED))
    ax.text(6.5, 0.2, "0.7 kg x 0.7 cm = 0.5 kg-cm   (servo can do 25)",
            ha="center", fontsize=13, weight="bold", color=BLUE)
    ax.set_title("Your board, tilted 7 deg (front view, offset drawn bigger)", fontsize=13,
                 weight="bold")
    ax.set_xlim(-1, 14)
    ax.set_ylim(0, 10.5)
    ax.set_aspect("equal")
    ax.axis("off")


def main():
    fig, axs = plt.subplots(1, 3, figsize=(19, 6.2), dpi=110)
    panel_servo(axs[0], 1, 25, "25 kg hung 1 cm from the shaft")
    panel_servo(axs[1], 10, 2.5, "2.5 kg hung 10 cm from the shaft")
    panel_board(axs[2])
    fig.suptitle("What '25 kg-cm' means: weight x distance from the shaft "
                 "centre (measured straight across)", fontsize=16,
                 weight="bold")
    fig.text(0.5, 0.02, "Same twist on the shaft both times: further out = "
             "less weight it can hold.  On the board, only the sideways "
             "distance from the pivot to the centre of mass counts - keep it "
             "small by balancing the board.", ha="center", fontsize=11.5)
    path = os.path.join(HERE, "Labyrinth_servo_torque.png")
    fig.savefig(path, facecolor="white", bbox_inches="tight")
    print("wrote", path)


if __name__ == "__main__":
    main()
