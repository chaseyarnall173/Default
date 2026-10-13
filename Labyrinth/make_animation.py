"""Animate the two-axis tilting mechanism as an MP4 so the team can see how
the board and the outer frame move.

Maze geometry comes from make_labyrinth.py. The frame, posts, servos and
pushrods use the starting numbers from the README (3D steps): board pins on
the left/right rims (axis 1), frame pins into front/back posts (axis 2).

    python3 make_animation.py              -> Labyrinth_two_axis.mp4
    python3 make_animation.py --check DIR  -> a few still frames as PNG
"""
import math
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter
from matplotlib.patches import Circle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

import make_labyrinth as ml

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 20
TILT = 6.0                       # real design tilt, degrees

B = ml.BOARD
C = B / 2                        # board centre (x and y)
PIN_Z = 0.375                    # both pivot axes sit at mid-rim height
P_LOCAL = np.array([C, C - 3.4, -0.125])     # board pushrod point (axis 1)
Q_LOCAL = np.array([11.875, C, -0.125])      # frame pushrod point (axis 2)
HORN1_R, HORN2_R = 0.5, 0.9
HORN1_C = np.array([C, P_LOCAL[1] + HORN1_R, -2.6])
HORN2_C = np.array([Q_LOCAL[0] + HORN2_R, C, -2.6])

WOOD, WALL, FRAME, POST = "#e3c08d", "#8a5a2b", "#6f87a3", "#c9a46c"
BASE, SERVO, METAL = "#6d6259", "#c2335c", "#b9bec6"
PIN1, PIN2 = "#d62728", "#1f5fbf"


# ------------------------------------------------------------- primitives
def box(p0, p1, color, seg=1.4, bottom=False):
    """Box split into small faces so the painter's sort draws it right."""
    def grid(a, b):
        return np.linspace(a, b, max(1, math.ceil((b - a) / seg)) + 1)
    (x0, y0, z0), (x1, y1, z1) = p0, p1
    X, Y, Z = grid(x0, x1), grid(y0, y1), grid(z0, z1)
    out = []
    for zc in ((z1, z0) if bottom else (z1,)):
        for i in range(len(X) - 1):
            for j in range(len(Y) - 1):
                out.append(([(X[i], Y[j], zc), (X[i + 1], Y[j], zc),
                             (X[i + 1], Y[j + 1], zc), (X[i], Y[j + 1], zc)],
                            color))
    for xc in (x0, x1):
        for j in range(len(Y) - 1):
            for k in range(len(Z) - 1):
                out.append(([(xc, Y[j], Z[k]), (xc, Y[j + 1], Z[k]),
                             (xc, Y[j + 1], Z[k + 1]), (xc, Y[j], Z[k + 1])],
                            color))
    for yc in (y0, y1):
        for i in range(len(X) - 1):
            for k in range(len(Z) - 1):
                out.append(([(X[i], yc, Z[k]), (X[i + 1], yc, Z[k]),
                             (X[i + 1], yc, Z[k + 1]), (X[i], yc, Z[k + 1])],
                            color))
    return out


def disc(cx, cy, z, r, color, n=20):
    return [([(cx + r * math.cos(2 * math.pi * k / n),
               cy + r * math.sin(2 * math.pi * k / n), z) for k in range(n)],
             color)]


def rod(a, b, w, color):
    """Square rod from point a to point b."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = b - a
    d /= np.linalg.norm(d)
    u = np.cross(d, [0, 0, 1.0] if abs(d[2]) < 0.9 else [1.0, 0, 0])
    u = u / np.linalg.norm(u) * w / 2
    v = np.cross(d, u)
    v = v / np.linalg.norm(v) * w / 2
    corners = [u + v, -u + v, -u - v, u - v]
    out = []
    for k in range(4):
        c0, c1 = corners[k], corners[(k + 1) % 4]
        out.append(([a + c0, b + c0, b + c1, a + c1], color))
    return out


def sphere(c, r, color, nu=10, nv=6):
    out = []
    for i in range(nu):
        for j in range(nv):
            pts = []
            for di, dj in ((0, 0), (1, 0), (1, 1), (0, 1)):
                th = 2 * math.pi * (i + di) / nu
                ph = math.pi * (j + dj) / nv - math.pi / 2
                pts.append((c[0] + r * math.cos(ph) * math.cos(th),
                            c[1] + r * math.cos(ph) * math.sin(th),
                            c[2] + r * math.sin(ph)))
            out.append((pts, color))
    return out


# ------------------------------------------------------------ the model
def board_parts():
    parts = box((0, 0, -0.125), (B, B, 0), WOOD, seg=ml.PITCH)
    for r in ml.wall_runs():
        x0, y0, x1, y1 = r["rect"]
        parts += box((x0, y0, 0), (x1, y1, r["height"]), WALL)
    for cell, f in ml.FEATURES.items():
        cx, cy = ml.centre(cell)
        if f in ml.HOLE_D:
            parts += disc(cx, cy, 0.012, ml.HOLE_D[f] / 2,
                          "#4a0f12" if f == "X" else "#111111")
        elif f == "T":
            h = ml.TRAP / 2
            parts.append(([(cx - h, cy - h, 0.012), (cx + h, cy - h, 0.012),
                           (cx + h, cy + h, 0.012), (cx - h, cy + h, 0.012)],
                          "#f2b134"))
    for x0, x1 in ((-0.375, 0), (B, B + 0.375)):          # axis-1 pins
        parts += box((x0, C - 0.125, PIN_Z - 0.125),
                     (x1, C + 0.125, PIN_Z + 0.125), PIN1)
    return parts


def frame_parts():
    o0, o1, i0, i1 = -0.375, B + 0.375, -0.25, B + 0.25
    z0, z1 = -0.125, 0.875
    parts = box((o0, o0, z0), (o1, i0, z1), FRAME)            # front
    parts += box((o0, i1, z0), (o1, o1, z1), FRAME)           # back
    parts += box((o0, i0, z0), (i0, i1, z1), FRAME)           # left
    parts += box((i1, i0, z0), (o1, i1, z1), FRAME)           # right
    parts += box((Q_LOCAL[0] - 0.125, C - 0.2, -0.5),         # pushrod tab
                 (Q_LOCAL[0], C + 0.2, z0), FRAME)
    for y0, y1 in ((-1.0, -0.375), (B + 0.375, B + 1.0)):     # axis-2 pins
        parts += box((C - 0.125, y0, PIN_Z - 0.125),
                     (C + 0.125, y1, PIN_Z + 0.125), PIN2)
    return parts


def fixed_parts():
    parts = box((-1.75, -1.75, -5.0), (B + 1.75, B + 1.75, -4.5), BASE,
                seg=1.6)
    parts += box((C - 0.5, -1.0, -4.5), (C + 0.5, -0.5, 1.0), POST, seg=1.0)
    parts += box((C - 0.5, B + 0.5, -4.5), (C + 0.5, B + 1.0, 1.0), POST,
                 seg=1.0)
    # servo 1: on its side, shaft pointing -x, horn swings in the y-z plane
    h = HORN1_C
    parts += box((h[0] + 0.1, h[1] - 0.4, h[2] - 0.4),
                 (h[0] + 1.7, h[1] + 1.18, h[2] + 0.4), SERVO, seg=0.8)
    parts += box((h[0] + 0.3, h[1] - 0.3, -4.5),
                 (h[0] + 1.5, h[1] + 1.08, h[2] - 0.4), POST, seg=0.8)
    # servo 2: shaft pointing -y, horn swings in the x-z plane
    h = HORN2_C
    parts += box((h[0] - 1.18, h[1] + 0.1, h[2] - 0.4),
                 (h[0] + 0.4, h[1] + 1.7, h[2] + 0.4), SERVO, seg=0.8)
    parts += box((h[0] - 1.08, h[1] + 0.3, -4.5),
                 (h[0] + 0.3, h[1] + 1.5, h[2] - 0.4), POST, seg=0.8)
    # joystick box at the front
    parts += box((1.0, -1.6, -4.5), (3.4, -0.4, -3.6), "#2b2b2b", seg=0.8)
    return parts


BOARD_PARTS, FRAME_PARTS, FIXED_PARTS = board_parts(), frame_parts(), \
    fixed_parts()


# ------------------------------------------------------------ kinematics
def rot1(pts, a):
    """Axis 1: rotate about the x-direction line y = C, z = PIN_Z."""
    y, z = pts[:, 1] - C, pts[:, 2] - PIN_Z
    out = pts.copy()
    out[:, 1] = C + y * math.cos(a) - z * math.sin(a)
    out[:, 2] = PIN_Z + y * math.sin(a) + z * math.cos(a)
    return out


def rot2(pts, b):
    """Axis 2: rotate about the y-direction line x = C, z = PIN_Z."""
    x, z = pts[:, 0] - C, pts[:, 2] - PIN_Z
    out = pts.copy()
    out[:, 0] = C + x * math.cos(b) + z * math.sin(b)
    out[:, 2] = PIN_Z - x * math.sin(b) + z * math.cos(b)
    return out


def pose(tilt_x, tilt_y):
    """tilt_x > 0: right side down (ball rolls right).
    tilt_y > 0: back side down (ball rolls away from the player)."""
    a = -math.radians(tilt_y)
    b = math.radians(tilt_x)
    return (lambda p: rot2(rot1(p, a), b)), (lambda p: rot2(p, b))


def horn(centre, r, swing_plane, target_z):
    rise = max(-0.98 * r, min(0.98 * r, target_z - centre[2]))
    phi = math.asin(rise / r)
    tip = centre.copy()
    if swing_plane == "yz":
        tip[1] -= r * math.cos(phi)
    else:
        tip[0] -= r * math.cos(phi)
    tip[2] += r * math.sin(phi)
    return tip, math.degrees(phi)


# ------------------------------------------------------------ timeline
SCENES = [
    (1.5, "level", "THE LABYRINTH - two-axis tilting maze",
     "Board sits inside an outer frame. Frame sits on two posts."),
    (5.5, "axis1", "AXIS 1 - servo 1 tips the BOARD front / back",
     "The board turns on the RED pins in the frame. The frame stays still."),
    (5.5, "axis2", "AXIS 2 - servo 2 tips the FRAME left / right",
     "Frame + board turn together on the BLUE pins in the posts."),
    (5.5, "both", "BOTH AT ONCE - the board can lean any direction",
     "Joystick left/right -> servo 2.   Joystick forward/back -> servo 1."),
    (8.0, "play", "PLAYING - lean the board toward where the ball should go",
     "Ball rolls downhill. Level the board to stop it at a turn."),
    (1.5, "level", "THE LABYRINTH", "tilt shown at the real design value: "
     "+/-6 degrees"),
]
ROUTE = [(8, 0), (8, 1), (7, 1), (6, 1), (6, 2), (6, 3), (7, 3), (8, 3),
         (8, 4), (8, 5)]


def scene_at(t):
    t0 = 0.0
    for dur, kind, title, sub in SCENES:
        if t < t0 + dur:
            return kind, t - t0, dur, title, sub
        t0 += dur
    dur, kind, title, sub = SCENES[-1]
    return kind, dur, dur, title, sub


def state(t):
    """Board tilts and ball position (board coords) at time t."""
    kind, u, dur, title, sub = scene_at(t)
    ease = min(1.0, u / 0.6, (dur - u) / 0.6)
    tx = ty = 0.0
    ball = np.array(ml.centre(ROUTE[0]) + (ml.BALL_D / 2,))
    if kind == "axis1":
        ty = TILT * math.sin(2 * math.pi * u / 2.6) * ease
    elif kind == "axis2":
        tx = TILT * math.sin(2 * math.pi * u / 2.6) * ease
    elif kind == "both":
        tx = TILT * math.cos(2 * math.pi * u / 2.6) * ease
        ty = TILT * math.sin(2 * math.pi * u / 2.6) * ease
    elif kind == "play":
        seg_t = dur / (len(ROUTE) - 1)
        k = min(int(u / seg_t), len(ROUTE) - 2)
        f = (u - k * seg_t) / seg_t
        a, b = ROUTE[k], ROUTE[k + 1]
        dx, dy = b[1] - a[1], a[0] - b[0]
        s = f * f * (3 - 2 * f)
        (ax, ay), (bx, by) = ml.centre(a), ml.centre(b)
        ball = np.array([ax + (bx - ax) * s, ay + (by - ay) * s,
                         ml.BALL_D / 2])
        lean = TILT * 0.8 * math.sin(math.pi * f)
        tx, ty = dx * lean, dy * lean
    elif kind == "level" and t > 10:
        ball = np.array(ml.centre(ROUTE[-1]) + (ml.BALL_D / 2,))
    return tx, ty, ball, title, sub


# --------------------------------------------------------------- render
LIGHT = np.array([-0.35, -0.55, 0.76])
LIGHT /= np.linalg.norm(LIGHT)


def shade(verts, color):
    v = np.asarray(verts)
    n = np.cross(v[1] - v[0], v[2] - v[0])
    norm = np.linalg.norm(n)
    k = 0.5 + 0.5 * (abs(n @ LIGHT) / norm if norm > 1e-9 else 0.5)
    rgb = np.array(matplotlib.colors.to_rgb(color)) * k
    return np.clip(rgb, 0, 1)


def transform(parts, fn):
    out = []
    for verts, color in parts:
        out.append((fn(np.asarray(verts, float)), color))
    return out


def draw(fig, ax, joy_ax, texts, t):
    tx, ty, ball, title, sub = state(t)
    fb, ff = pose(tx, ty)
    polys = transform(BOARD_PARTS + sphere(ball, ml.BALL_D / 2, "#c8ccd4"),
                      fb)
    polys += transform(FRAME_PARTS, ff)
    polys += [(np.asarray(v, float), c) for v, c in FIXED_PARTS]

    p = fb(P_LOCAL[None, :])[0]
    q = ff(Q_LOCAL[None, :])[0]
    tip1, a1 = horn(HORN1_C.copy(), HORN1_R, "yz", HORN1_C[2] + (p[2] - P_LOCAL[2]))
    tip2, a2 = horn(HORN2_C.copy(), HORN2_R, "xz", HORN2_C[2] + (q[2] - Q_LOCAL[2]))
    for c, tip in ((HORN1_C, tip1), (HORN2_C, tip2)):
        polys += [(np.asarray(v, float), col)
                  for v, col in rod(c, tip, 0.16, METAL)]
    polys += [(np.asarray(v, float), col) for v, col in rod(tip1, p, 0.07,
                                                            "#3d3d3d")]
    polys += [(np.asarray(v, float), col) for v, col in rod(tip2, q, 0.07,
                                                            "#3d3d3d")]

    ax.cla()
    ax.set_axis_off()
    ax.computed_zorder = False
    coll = Poly3DCollection([v for v, _ in polys],
                            facecolors=[shade(v, c) for v, c in polys],
                            edgecolors=[shade(v, c) for v, c in polys],
                            linewidths=0.25, zsort="average")
    coll.set_zorder(1)
    ax.add_collection3d(coll)

    # pivot axes as dashed lines (axis 1 rides on the frame)
    a1_line = ff(np.array([[-1.4, C, PIN_Z], [B + 1.4, C, PIN_Z]]))
    ax.plot(a1_line[:, 0], a1_line[:, 1], a1_line[:, 2], ls="--", lw=1.6,
            color=PIN1, zorder=5)
    ax.plot([C, C], [-1.8, B + 1.8], [PIN_Z, PIN_Z], ls="--", lw=1.6,
            color=PIN2, zorder=5)
    for x, y, z, s, col in (
            (HORN1_C[0] + 3.0, HORN1_C[1], -4.0, "SERVO 1\n(axis 1)", PIN1),
            (B + 2.6, HORN2_C[1] + 1.0, -3.4, "SERVO 2\n(axis 2)", PIN2),
            (C, -1.6, 1.6, "POST", "#333"),
            (B + 0.9, -0.6, 1.3, "OUTER FRAME", "#333"),
            (2.2, -2.6, -3.4, "JOYSTICK", "#333"),
            (C, -3.4, -5.2, "FRONT (player)", "#555")):
        ax.text(x, y, z, s, color=col, fontsize=9, ha="center",
                weight="bold", zorder=6)
    ax.set_xlim(-2.2, B + 2.2)
    ax.set_ylim(-2.2, B + 2.2)
    ax.set_zlim(-5.2, 2.2)
    ax.set_box_aspect((B + 4.4, B + 4.4, 7.4), zoom=1.22)
    ax.view_init(elev=30, azim=-62)

    texts[0].set_text(title)
    texts[1].set_text(sub)
    texts[2].set_text("board tilt: left/right %+.1f deg   front/back %+.1f "
                      "deg      servo 1 %+.0f deg   servo 2 %+.0f deg"
                      % (tx, ty, a1, a2))
    joy_ax.cla()
    joy_ax.set_xlim(-1.3, 1.3)
    joy_ax.set_ylim(-1.3, 1.3)
    joy_ax.set_aspect("equal")
    joy_ax.axis("off")
    joy_ax.add_patch(Circle((0, 0), 1, fc="#f2f2f2", ec="#888"))
    joy_ax.plot([-1, 1], [0, 0], color="#bbb", lw=0.8)
    joy_ax.plot([0, 0], [-1, 1], color="#bbb", lw=0.8)
    joy_ax.add_patch(Circle((tx / TILT, ty / TILT), 0.22, fc="#222"))
    joy_ax.set_title("joystick", fontsize=9)


def make_figure():
    fig = plt.figure(figsize=(12.8, 8.0), dpi=100)
    ax = fig.add_axes([0.0, 0.0, 1.0, 0.84], projection="3d")
    joy = fig.add_axes([0.83, 0.08, 0.14, 0.2])
    texts = [fig.text(0.5, 0.955, "", ha="center", fontsize=17,
                      weight="bold"),
             fig.text(0.5, 0.915, "", ha="center", fontsize=12.5,
                      color="#333"),
             fig.text(0.5, 0.875, "", ha="center", fontsize=9.5,
                      color="#555", family="DejaVu Sans Mono")]
    return fig, ax, joy, texts


def main():
    total = sum(s[0] for s in SCENES)
    fig, ax, joy, texts = make_figure()
    if "--check" in sys.argv:              # stills: --check OUT_DIR
        out_dir = sys.argv[sys.argv.index("--check") + 1]
        for t in (0.5, 3.0, 8.5, 13.0, 21.0):
            draw(fig, ax, joy, texts, t)
            fig.savefig(os.path.join(out_dir, "check_%04.1f.png" % t))
        return
    out = os.path.join(HERE, "Labyrinth_two_axis.mp4")
    writer = FFMpegWriter(fps=FPS, bitrate=2500,
                          extra_args=["-pix_fmt", "yuv420p"])
    with writer.saving(fig, out, dpi=100):
        n = int(total * FPS)
        for i in range(n):
            draw(fig, ax, joy, texts, i / FPS)
            writer.grab_frame()
    print("wrote", out, "(%d frames, %.1f s)" % (n, total))


if __name__ == "__main__":
    main()
