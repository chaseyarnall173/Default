"""Show how the two tilt axes move, using the exact 3D model in
Labyrinth_3D.scr (servos on the stands).

    python3 make_axis_views.py          -> Labyrinth_axes_explained.png
    python3 make_axis_views.py --video  -> also Labyrinth_two_axis.mp4

Parts are coloured by what they move with:
  grey   never moves             base, posts, servo 2's body, joystick
  blue   turned by servo 2       outer frame, servo 1's body, servo 2's horn
  orange turned by servo 1 too   board, walls, rim, ball, servo 1's horn
Servo 2 turns the blue group on the AXIS 2 line (front servo shaft + back
pin); the orange board rides along because it hangs in the frame. Servo 1
is bolted to the frame, so it turns only the orange board, on the AXIS 1
line (left servo shaft + right pin).
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
SHOW_TILT = 15.0          # pictures exaggerate the tilt so it is visible
REAL_TILT = 6.0

FIXED = {"BASE", "POST-FRONT", "POST-BACK", "SERVO-2", "CONTROLS",
         "JOYSTICK", "PIN-AXIS2", "TRAY-CUP"}
FRAME = {"FRAME-LEFT", "FRAME-RIGHT", "FRAME-FRONT", "FRAME-BACK", "FRAME-BAY",
         "HORN-2",
         "SERVO-1", "PIN-AXIS1"}
GROUP_COLOR = {"fixed": "#8f9399", "frame": "#3f7fd0", "board": "#e39b45"}
SHADE = {"WALLS": 0.78, "RIM-FRONT": 0.66, "RIM-BACK": 0.66,
         "RIM-LEFT": 0.66, "RIM-RIGHT": 0.66, "BALL": 1.25, "BASE": 0.72,
         "SERVO-1": 0.8, "SERVO-2": 0.8, "CONTROLS": 0.5}


# ------------------------------------------------------- read the model
def parse(path):
    """Solids from the AutoCAD script: (group, layer, kind, data, is_hole).

    Cutters (layer TMP) are kept as dark 'holes' in the part they cut."""
    lines = open(path).read().split("\n")
    lines = [s.strip("\r") for s in lines]
    P = lambda s: tuple(float(v) for v in s.split(","))
    out, pending, layer, last_servo, i = [], [], "0", None, 0
    while i < len(lines):
        t = lines[i]
        if t == "-LAYER" and lines[i + 1] == "M":
            layer = lines[i + 2]
            if layer.startswith("SERVO"):
                last_servo = layer
            i += 3
            continue
        if t == "UCS" and lines[i + 1] != "W":    # tray triangle
            a, b, c = (np.array(P(lines[i + k])) for k in (1, 2, 3))
            th = -float(lines[i + 12])
            nrm = np.cross(b - a, c - a)
            nrm /= np.linalg.norm(nrm)
            if nrm[2] < 0:
                nrm = -nrm
            out.append(("board", layer, "prism", (a, b, c, th, nrm), False))
            i += 15
            continue
        if t in ("BOX", "CYLINDER", "SPHERE"):
            if t == "BOX":
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
            elif layer == "HORNS":       # each horn moves with what it's on
                group = "board" if last_servo == "SERVO-1" else "frame"
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
    """Axis 1: about the x-direction line y = C, z = PIN_Z."""
    y, z = pts[..., 1] - C, pts[..., 2] - PIN_Z
    out = pts.copy()
    out[..., 1] = C + y * math.cos(a) - z * math.sin(a)
    out[..., 2] = PIN_Z + y * math.sin(a) + z * math.cos(a)
    return out


def rot2(pts, b):
    """Axis 2: about the y-direction line x = C, z = PIN_Z."""
    x, z = pts[..., 0] - C, pts[..., 2] - PIN_Z
    out = pts.copy()
    out[..., 0] = C + x * math.cos(b) + z * math.sin(b)
    out[..., 2] = PIN_Z - x * math.sin(b) + z * math.cos(b)
    return out


LIGHT = np.array([-0.35, -0.55, 0.76]) / np.linalg.norm([-0.35, -0.55, 0.76])


def draw(ax, prepared, servo1_deg, servo2_deg, labels=False, axes=True):
    a = math.radians(servo1_deg)        # + = back of the board goes up
    b = math.radians(servo2_deg)        # + = right side goes down
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
    # pivot lines: axis 2 never moves, axis 1 rides on the frame
    ax2 = np.array([[C, -3.0, PIN_Z], [C, B + 2.6, PIN_Z]])
    ax1 = rot2(np.array([[-2.6, C, PIN_Z], [B + 1.6, C, PIN_Z]]), b)
    ax.plot(*ax1.T, ls="--", lw=2.2, color="#c0392b", zorder=5)
    if axes:
        ax.plot(*ax2.T, ls="--", lw=2.2, color="#1450a0", zorder=5)
        ax.text(*ax2[1] + [0, 0.4, 0.3], "AXIS 2", color="#1450a0",
                fontsize=10, weight="bold", zorder=6)
        ax.text(*ax1[0] + [-0.6, 0, 0.3], "AXIS 1", color="#c0392b",
                fontsize=10, weight="bold", zorder=6)
    if labels:
        for p, s, col in (
                ((C + 3.4, -2.6, -2.9), "SERVO 2\nbolted to the post\n"
                 "(never moves)", "#333"),
                ((-1.4, C + 2.6, 0.9), "SERVO 1\nbolted to the frame",
                 "#1450a0"),
                ((B + 1.0, -0.6, 1.1), "OUTER FRAME", "#1450a0"),
                ((C + 1.5, C + 1.5, 3.6), "BOARD", "#a85a10"),
                ((-0.4, C - 2.6, -1.9), "bracket under\nthe board", "#a85a10")):
            ax.text(*p, s, color=col, fontsize=9, weight="bold",
                    ha="center", zorder=6)
    ax.set_xlim(-2.8, B + 1.5)
    ax.set_ylim(-2.7, B + 1.6)
    ax.set_zlim(-6.1, 3.4)
    ax.set_box_aspect((B + 4.3, B + 4.3, 9.5), zoom=1.3)
    ax.view_init(elev=38, azim=-58)
    ax.set_axis_off()


# ------------------------------------------------------------ outputs
PANELS = [
    ("1  Level", "Grey never moves. Blue is turned by servo 2. Orange is "
     "turned by servo 1\n(and also gets carried by servo 2).", 0, 0, True),
    ("2  Servo 2 turns -> frame AND board tip left / right",
     "Servo 2 is bolted to the front post and its horn is screwed to the "
     "frame.\nThe frame swings on AXIS 2 (front servo shaft + back pin). "
     "The board hangs\nin the frame, so it goes with it - and so does "
     "servo 1, bolted to the frame.", 0, SHOW_TILT, False),
    ("3  Servo 1 turns -> ONLY the board tips front / back",
     "Servo 1 is bolted to the frame and its horn is screwed to the "
     "bracket under the board.\nThe board swings on AXIS 1 (left servo "
     "shaft + pin in the right bracket). The frame does\nnot move, "
     "because servo 1 pushes against the frame it is bolted to.",
     SHOW_TILT, 0, False),
    ("4  Both at once -> the board leans any direction",
     "Servo 2 sets left/right, servo 1 sets front/back. AXIS 1 is carried "
     "around by the\nframe, so servo 1 always tips the board relative to "
     "the frame - that is why each\nservo only ever controls its own "
     "direction.", SHOW_TILT, SHOW_TILT, False),
]


def picture(prepared, path):
    fig = plt.figure(figsize=(16, 14.5), dpi=110)
    fig.suptitle("The Labyrinth - how the two axes move (servos on the "
                 "stands)", fontsize=19, weight="bold", y=0.99)
    fig.text(0.5, 0.962, "tilt drawn at %d deg so you can see it - the "
             "real game uses about +/-%d deg" % (SHOW_TILT, REAL_TILT),
             ha="center", fontsize=11, color="#555")
    fig.legend(handles=[
        Patch(color=GROUP_COLOR["fixed"], label="never moves: base, posts, "
              "servo 2 body, joystick"),
        Patch(color=GROUP_COLOR["frame"], label="turned by servo 2: outer "
              "frame + servo 1 (bolted to it)"),
        Patch(color=GROUP_COLOR["board"], label="turned by servo 1, and "
              "carried by servo 2: the board")],
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
        (2.0, "Level", "grey never moves - blue: servo 2 - orange: servo 1",
         lambda u: (0, 0)),
        (6.0, "Servo 2 turns: frame AND board tip left / right",
         "servo 2 is on the post; the board and servo 1 ride in the frame",
         lambda u: (0, REAL_TILT * 1.6 * math.sin(2 * math.pi * u / 3))),
        (6.0, "Servo 1 turns: ONLY the board tips front / back",
         "servo 1 is bolted to the frame, so the frame stays still",
         lambda u: (REAL_TILT * 1.6 * math.sin(2 * math.pi * u / 3), 0)),
        (6.0, "Both: the board leans any direction",
         "servo 2 = left/right, servo 1 = front/back",
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
                t3.set_text("servo 1 (axis 1) %+5.1f deg     servo 2 "
                            "(axis 2) %+5.1f deg     (shown 1.6x the real "
                            "+/-6 deg)" % (s1 * ease, s2 * ease))
                writer.grab_frame()
    plt.close(fig)
    print("wrote", path)


HIDE_IN_CLOSEUP = {"FRAME-FRONT", "POST-FRONT", "SERVO-2", "RIM-FRONT",
                   "CONTROLS", "JOYSTICK", "BASE", "BALL", "LABELS",
                   "TRAPDOOR-SERVO", "TRAPDOOR-FLAP"}


def crop(prepared, lo, hi):
    """Keep only faces whose centre lies inside the box lo..hi."""
    out = {}
    for group, items in prepared.items():
        out[group] = [(f, c) for f, c in items
                      if np.all(f.mean(axis=0) >= lo)
                      and np.all(f.mean(axis=0) <= hi)]
    return out


def closeup(solids, path):
    """Looking up from the front at each end of axis 1: brackets glued
    under the floor, servo 1 + horn on the left, the pin on the right."""
    keep = [s for s in solids if s[1] not in HIDE_IN_CLOSEUP]
    prepared = prepare(keep)
    fig = plt.figure(figsize=(16, 7.5), dpi=110)
    for k, (x0, x1, title, notes) in enumerate((
            (-2.6, 2.4, "LEFT end: servo 1 turns the board",
             "servo 1 sits in the frame's left plate; its horn is screwed "
             "to the left bracket"),
            (B - 2.4, B + 0.6, "RIGHT end: plain pin",
             "1/4 in pin through the right bracket and the frame's right "
             "strip"))):
        lo = np.array([x0, C - 2.2, -2.0])
        hi = np.array([x1, C + 2.2, 0.6])
        ax = fig.add_axes([0.5 * k, 0.06, 0.5, 0.8], projection="3d")
        draw(ax, crop(prepared, lo, hi), 0, 0, axes=False)
        ax.set_xlim(x0, x1)
        ax.set_ylim(C - 2.2, C + 2.2)
        ax.set_zlim(-2.0, 0.6)
        ax.set_box_aspect((x1 - x0, 4.4, 2.6), zoom=1.0)
        ax.view_init(elev=-14, azim=-75)
        fig.text(0.25 + 0.5 * k, 0.9, title, ha="center", fontsize=14,
                 weight="bold")
        fig.text(0.25 + 0.5 * k, 0.865, notes, ha="center", fontsize=10.5,
                 color="#333")
    fig.suptitle("Axis 1 seen from below the board (front parts and base "
                 "hidden)", fontsize=16, weight="bold", y=0.985)
    fig.text(0.5, 0.025, "orange = board, floor and the two brackets glued "
             "under it   blue = frame + servo 1   dark dots = axle / screw "
             "holes   red line = axis 1, %.2f in below the floor top"
             % -PIN_Z, ha="center", fontsize=10.5, color="#333")
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    print("wrote", path)


def main():
    solids = parse(os.path.join(HERE, "Labyrinth_3D.scr"))
    prepared = prepare(solids)
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv \
        else HERE
    picture(prepared, os.path.join(out, "Labyrinth_axes_explained.png"))
    closeup(solids, os.path.join(out, "Labyrinth_axis1_bracket.png"))
    if "--video" in sys.argv:
        video(prepared, os.path.join(out, "Labyrinth_two_axis.mp4"))


if __name__ == "__main__":
    main()
