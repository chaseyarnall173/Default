"""Show how the two tilt axes move, using the exact 3D model in
Labyrinth_3D.scr (the mounting as built).

    python3 make_axis_views.py          -> Labyrinth_axes_explained.png
    python3 make_axis_views.py --video  -> also Labyrinth_two_axis.mp4

Parts are coloured by what they move with:
  grey   never moves             base, posts, outer servo's body, joystick
  blue   turned by the outer servo   outer box, inner servo's body
  orange turned by the inner servo too   board, walls, rim, tray, ball
The outer servo (right post) turns the blue outer box on AXIS 2, which
runs left-right (right servo shaft + left dowel and bearing); the board
rides along. The inner servo is fixed in the outer box's front wall, so
it turns only the orange board, on AXIS 1, which runs front-back (front
servo shaft + back dowel and bearing).
"""
import math
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

import make_autocad_script as cad

HERE = os.path.dirname(os.path.abspath(__file__))
C, PIN_Z, B = cad.C, cad.AXIS_Z, cad.B
SHOW_TILT = 10.0          # pictures exaggerate the tilt so it is visible
REAL_TILT = 6.0

FIXED = {"BASE", "POST-LEFT", "POST-RIGHT", "SERVO-OUTER", "CONTROLS",
         "JOYSTICK", "PIN-AXIS2"}
FRAME = {"FRAME-LEFT", "FRAME-RIGHT", "FRAME-FRONT", "FRAME-BACK",
         "HORN-OUTER", "SERVO-INNER", "BEARING-1", "BEARING-2"}
GROUP_COLOR = {"fixed": "#8f9399", "frame": "#3f7fd0", "board": "#e39b45"}
SHADE = {"WALLS": 0.78, "RIM-FRONT": 0.66, "RIM-BACK": 0.66,
         "RIM-LEFT": 0.66, "RIM-RIGHT": 0.66, "BALL": 1.25, "BASE": 0.72,
         "SERVO-INNER": 0.8, "SERVO-OUTER": 0.8, "CONTROLS": 0.5,
         "TRAY-FLOOR": 0.9}


# ------------------------------------------------------- read the model
def parse(path):
    """Solids from the AutoCAD script: (group, layer, kind, data, is_hole).

    Cutters (layer TMP) are kept as dark 'holes' in the part they cut."""
    lines = open(path).read().split("\n")
    lines = [s.strip("\r") for s in lines]
    P = lambda s: tuple(float(v) for v in s.split(","))
    out, pending, layer, i = [], [], "0", 0
    while i < len(lines):
        t = lines[i]
        if t == "-LAYER" and lines[i + 1] == "M":
            layer = lines[i + 2]
            i += 3
            continue
        if t in ("BOX", "CYLINDER", "SPHERE"):
            if t == "BOX" and lines[i + 3] == "SLICE":   # tray triangle:
                top = [np.array(P(lines[i + 3 + 8 + k])) for k in (4, 5, 6)]
                low = np.array(P(lines[i + 3 + 16 + 4]))  # box cut by 3 planes
                nrm = np.cross(top[1] - top[0], top[2] - top[0])
                nrm /= np.linalg.norm(nrm)
                if nrm[2] < 0:
                    nrm = -nrm
                th = (top[0][2] - low[2]) * nrm[2]
                data, i = ("prism", (*top, th, nrm)), i + 3 + 24
            elif t == "BOX":
                data, i = ("box", (P(lines[i + 1]), P(lines[i + 2]))), i + 3
            elif t == "CYLINDER":
                data = ("cyl", (P(lines[i + 1]), P(lines[i + 4]),
                                float(lines[i + 2])))
                i += 5
            else:
                data, i = ("sphere", (P(lines[i + 1]),
                                      float(lines[i + 2]))), i + 3
            if layer == "TMP":
                if data[0] == "cyl":
                    pending.append(data)
                continue
            if layer in FIXED:
                group = "fixed"
            elif layer in FRAME:
                group = "frame"
            else:
                group = "board"
            out.append((group, layer, data[0], data[1], False))
            for kind, d in pending:      # the holes cut into this part
                out.append((group, layer, kind, d, True))
            pending = []
            continue
        i += 1
    return out


# ---------------------------------------------------------- geometry
def box_faces(lo, hi, seg=1.0, zseg=0.5):
    def grid(a, b, step):
        return np.linspace(a, b, max(1, math.ceil((b - a) / step)) + 1)
    X, Y = grid(lo[0], hi[0], seg), grid(lo[1], hi[1], seg)
    Z = grid(lo[2], hi[2], zseg)
    f = []
    for zc in (lo[2], hi[2]):
        for i in range(len(X) - 1):
            for j in range(len(Y) - 1):
                f.append([(X[i], Y[j], zc), (X[i + 1], Y[j], zc),
                          (X[i + 1], Y[j + 1], zc), (X[i], Y[j + 1], zc)])
    for xc in (lo[0], hi[0]):
        for j in range(len(Y) - 1):
            for k in range(len(Z) - 1):
                f.append([(xc, Y[j], Z[k]), (xc, Y[j + 1], Z[k]),
                          (xc, Y[j + 1], Z[k + 1]), (xc, Y[j], Z[k + 1])])
    for yc in (lo[1], hi[1]):
        for i in range(len(X) - 1):
            for k in range(len(Z) - 1):
                f.append([(X[i], yc, Z[k]), (X[i + 1], yc, Z[k]),
                          (X[i + 1], yc, Z[k + 1]), (X[i], yc, Z[k + 1])])
    return f


def cyl_faces(p0, p1, r, n=16):
    p0, p1 = np.array(p0, float), np.array(p1, float)
    d = p1 - p0
    d /= np.linalg.norm(d)
    u = np.cross(d, [0, 0, 1.0] if abs(d[2]) < 0.9 else [1.0, 0, 0])
    u /= np.linalg.norm(u)
    v = np.cross(d, u)
    ring = [r * (math.cos(2 * math.pi * k / n) * u
                 + math.sin(2 * math.pi * k / n) * v) for k in range(n)]
    f = [[p0 + c for c in ring], [p1 + c for c in ring]]
    for k in range(n):
        a, b = ring[k], ring[(k + 1) % n]
        f.append([p0 + a, p0 + b, p1 + b, p1 + a])
    return f


def sphere_faces(c, r, nu=12, nv=8):
    f = []
    for i in range(nu):
        for j in range(nv):
            q = []
            for di, dj in ((0, 0), (1, 0), (1, 1), (0, 1)):
                th = 2 * math.pi * (i + di) / nu
                ph = math.pi * (j + dj) / nv - math.pi / 2
                q.append((c[0] + r * math.cos(ph) * math.cos(th),
                          c[1] + r * math.cos(ph) * math.sin(th),
                          c[2] + r * math.sin(ph)))
            f.append(q)
    return f


def prism_faces(a, b, c, th, nrm):
    top = [np.asarray(p, float) for p in (a, b, c)]
    bot = [p - th * nrm for p in top]
    f = [top, bot]
    for k in range(3):
        j = (k + 1) % 3
        f.append([top[k], top[j], bot[j], bot[k]])
    return f


def faces_of(kind, data):
    if kind == "prism":
        return prism_faces(*data)
    if kind == "box":
        return box_faces(*data)
    if kind == "cyl":
        return cyl_faces(*data)
    return sphere_faces(*data)


def prepare(solids):
    """Faces as arrays, grouped, with a base colour each."""
    prepared = {"fixed": [], "frame": [], "board": []}
    for group, layer, kind, data, hole in solids:
        rgb = np.array(matplotlib.colors.to_rgb(GROUP_COLOR[group]))
        rgb = (np.array([0.08, 0.08, 0.08]) if hole
               else np.clip(rgb * SHADE.get(layer, 1.0), 0, 1))
        for f in faces_of(kind, data):
            prepared[group].append((np.asarray(f, float), rgb))
    return prepared


# --------------------------------------------------------------- motion
def rot1(pts, a):
    """Axis 1 (inner servo): about the y-direction line x = C, z = PIN_Z."""
    x, z = pts[..., 0] - C, pts[..., 2] - PIN_Z
    out = pts.copy()
    out[..., 0] = C + x * math.cos(a) + z * math.sin(a)
    out[..., 2] = PIN_Z - x * math.sin(a) + z * math.cos(a)
    return out


def rot2(pts, b):
    """Axis 2 (outer servo): about the x-direction line y = C, z = PIN_Z."""
    y, z = pts[..., 1] - C, pts[..., 2] - PIN_Z
    out = pts.copy()
    out[..., 1] = C + y * math.cos(b) - z * math.sin(b)
    out[..., 2] = PIN_Z + y * math.sin(b) + z * math.cos(b)
    return out


LIGHT = np.array([-0.35, -0.55, 0.76]) / np.linalg.norm([-0.35, -0.55, 0.76])


def draw(ax, prepared, servo1_deg, servo2_deg, labels=False, axes=True):
    a = math.radians(servo1_deg)        # inner servo: + = left side down
    b = math.radians(servo2_deg)        # outer servo: + = back goes up
    polys, cols = [], []
    for group, items in prepared.items():
        for f, rgb in items:
            if group == "board":
                f = rot2(rot1(f, a), b)
            elif group == "frame":
                f = rot2(f, b)
            nrm = np.cross(f[1] - f[0], f[2] - f[0])
            ln = np.linalg.norm(nrm)
            k = 0.55 + 0.45 * (abs(nrm @ LIGHT) / ln if ln > 1e-9 else 0.5)
            polys.append(f)
            cols.append(np.clip(rgb * k, 0, 1))
    ax.computed_zorder = False
    coll = Poly3DCollection(polys, facecolors=cols, edgecolors=cols,
                            linewidths=0.25, zsort="average")
    coll.set_zorder(1)
    ax.add_collection3d(coll, autolim=False)   # limits are set below
    # pivot lines: axis 2 never moves, axis 1 rides on the outer box
    ax2 = np.array([[-3.0, C, PIN_Z], [B + 3.4, C, PIN_Z]])
    ax1 = rot2(np.array([[C, -3.0, PIN_Z], [C, B + 1.8, PIN_Z]]), b)
    ax.plot(*ax1.T, ls="--", lw=2.2, color="#c0392b", zorder=5)
    if axes:
        ax.plot(*ax2.T, ls="--", lw=2.2, color="#1450a0", zorder=5)
        ax.text(*ax2[1] + [0.3, 0, 0.3], "AXIS 2", color="#1450a0",
                fontsize=10, weight="bold", zorder=6)
        ax.text(*ax1[0] + [0, -0.4, 0.3], "AXIS 1", color="#c0392b",
                fontsize=10, weight="bold", zorder=6)
    if labels:
        for p, s_, col in (
                ((B + 3.0, C - 2.4, -2.6), "OUTER SERVO\non the right post\n"
                 "(never moves)", "#333"),
                ((C + 2.2, -3.2, -1.6), "INNER SERVO\nin the outer box's\n"
                 "front wall", "#1450a0"),
                ((-1.8, -1.6, 2.6), "OUTER BOX", "#1450a0"),
                ((C + 1.5, C + 1.5, 3.4), "BOARD", "#a85a10"),
                ((-2.6, C + 2.0, -1.4), "dowel +\nbearing", "#333")):
            ax.text(*p, s_, color=col, fontsize=9, weight="bold",
                    ha="center", zorder=6)
    ax.set_xlim(-3.0, B + 3.2)
    ax.set_ylim(-3.6, B + 1.6)
    ax.set_zlim(-6.1, 3.4)
    ax.set_box_aspect((B + 6.2, B + 5.2, 9.5), zoom=1.3)
    ax.view_init(elev=38, azim=-58)
    ax.set_axis_off()


# ------------------------------------------------------------ outputs
PANELS = [
    ("1  Level", "Grey never moves. Blue is turned by the outer servo. "
     "Orange is turned by the inner servo\n(and also gets carried by the "
     "outer servo).", 0, 0, True),
    ("2  Outer servo turns -> outer box AND board tip front / back",
     "The outer servo is fixed to the right post and its horn is screwed to "
     "the outer box.\nThe outer box swings on AXIS 2 (right servo shaft + "
     "left dowel in a bearing). The board\nhangs in the outer box, so it "
     "goes with it - and so does the inner servo.", 0, SHOW_TILT, False),
    ("3  Inner servo turns -> ONLY the board tips left / right",
     "The inner servo sits in the outer box's front wall and its horn is "
     "screwed to the board's\nfront rim. The board swings on AXIS 1 (front "
     "servo shaft + back dowel in a bearing).\nThe outer box does not move, "
     "because the inner servo pushes against it.", SHOW_TILT, 0, False),
    ("4  Both at once -> the board leans any direction",
     "The outer servo sets front/back, the inner servo sets left/right. "
     "AXIS 1 is carried\nby the outer box, so the inner servo always tips "
     "the board relative to the outer box.", SHOW_TILT, SHOW_TILT, False),
]


def picture(prepared, path):
    fig = plt.figure(figsize=(16, 14.5), dpi=110)
    fig.suptitle("The Labyrinth - how the two axes move (as built)",
                 fontsize=19, weight="bold", y=0.99)
    fig.text(0.5, 0.962, "tilt drawn at %d deg so you can see it - the "
             "real game uses about +/-%d deg" % (SHOW_TILT, REAL_TILT),
             ha="center", fontsize=11, color="#555")
    fig.legend(handles=[
        Patch(color=GROUP_COLOR["fixed"], label="never moves: base, posts, "
              "outer servo, joystick"),
        Patch(color=GROUP_COLOR["frame"], label="turned by the outer servo: "
              "outer box + inner servo"),
        Patch(color=GROUP_COLOR["board"], label="turned by the inner servo, "
              "carried by the outer servo: board + tray")],
        loc="upper center", ncol=3, fontsize=10.5, frameon=False,
        bbox_to_anchor=(0.5, 0.955))
    for k, (title, text, s1, s2, labels) in enumerate(PANELS):
        r, c = divmod(k, 2)
        y_t = (0.89, 0.435)[r]
        ax = fig.add_axes([0.01 + 0.495 * c, y_t - 0.37, 0.48, 0.355],
                          projection="3d")
        draw(ax, prepared, s1, s2, labels)
        fig.text(0.25 + 0.495 * c, y_t, title, ha="center", fontsize=14,
                 weight="bold")
        fig.text(0.25 + 0.495 * c, y_t - 0.372, text, ha="center",
                 va="top", fontsize=10, color="#222", linespacing=1.35)
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    print("wrote", path)


def video(prepared, path, fps=20):
    from matplotlib.animation import FFMpegWriter
    scenes = [
        (2.0, "Level", "grey never moves - blue: outer servo - orange: "
         "inner servo", lambda u: (0, 0)),
        (6.0, "Outer servo turns: outer box AND board tip front / back",
         "the outer servo is on the right post; the board rides in the box",
         lambda u: (0, REAL_TILT * 1.6 * math.sin(2 * math.pi * u / 3))),
        (6.0, "Inner servo turns: ONLY the board tips left / right",
         "the inner servo is in the outer box, so the box stays still",
         lambda u: (REAL_TILT * 1.6 * math.sin(2 * math.pi * u / 3), 0)),
        (6.0, "Both: the board leans any direction",
         "outer servo = front/back, inner servo = left/right",
         lambda u: (REAL_TILT * 1.6 * math.sin(2 * math.pi * u / 3),
                    REAL_TILT * 1.6 * math.cos(2 * math.pi * u / 3))),
    ]
    fig = plt.figure(figsize=(12.8, 8.0), dpi=100)
    ax = fig.add_axes([0, 0, 1, 0.86], projection="3d")
    t1 = fig.text(0.5, 0.95, "", ha="center", fontsize=18, weight="bold")
    t2 = fig.text(0.5, 0.905, "", ha="center", fontsize=12.5, color="#333")
    t3 = fig.text(0.5, 0.03, "", ha="center", fontsize=10.5, color="#555",
                  family="DejaVu Sans Mono")
    writer = FFMpegWriter(fps=fps, bitrate=2500,
                          extra_args=["-pix_fmt", "yuv420p"])
    with writer.saving(fig, path, dpi=100):
        for dur, title, sub, fn in scenes:
            for i in range(int(dur * fps)):
                u = i / fps
                ease = min(1.0, u / 0.5, (dur - u) / 0.5)
                s1, s2 = fn(u)
                ax.cla()
                draw(ax, prepared, s1 * ease, s2 * ease, labels=True)
                t1.set_text(title)
                t2.set_text(sub)
                t3.set_text("inner servo (axis 1) %+5.1f deg     outer "
                            "servo (axis 2) %+5.1f deg     (shown 1.6x the "
                            "real +/-6 deg)" % (s1 * ease, s2 * ease))
                writer.grab_frame()
    plt.close(fig)
    print("wrote", path)


def main():
    solids = parse(os.path.join(HERE, "Labyrinth_3D.scr"))
    prepared = prepare(solids)
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv \
        else HERE
    picture(prepared, os.path.join(out, "Labyrinth_axes_explained.png"))
    if "--video" in sys.argv:
        video(prepared, os.path.join(out, "Labyrinth_two_axis.mp4"))


if __name__ == "__main__":
    main()
