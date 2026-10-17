"""Build The Labyrinth (GE1501 Group 1) maze board: a laser layout DXF for
AutoCAD plus 1:1 printable templates for the cardboard prototype.

Units are inches. Board coordinates: origin at the front-left corner of the
floor plate (the player stands at the front, y = 0), x to the right, y away
from the player. Row 0 of MAZE is the back edge, row 8 the front edge.

Edit MAZE (or the settings below) and re-run:
    python3 make_labyrinth.py [output_dir]

Outputs
  Labyrinth_Board.dxf              laser layout, one 12 x 16 sheet per panel
  Labyrinth_preview.png            picture of the DXF
  Labyrinth_board_top.png          top view of the assembled playfield
  Labyrinth_Template_Letter.pdf    cardboard template, 4 letter pages at 1:1
  Labyrinth_Template_FullSize.pdf  same template on one 13 x 13 in page
"""
import os
import sys

import ezdxf
from ezdxf.enums import TextEntityAlignment
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Circle, Rectangle

OUT_DIR = (sys.argv[1] if len(sys.argv) > 1
           else os.path.dirname(os.path.abspath(__file__)))

# ------------------------------------------------------------------ settings
BOARD = 11.5        # floor plate (square): 12 in laser bed minus 1/4 border
T = 0.125           # plywood thickness = wall thickness (measure your sheet)
N = 9               # cells per side
PITCH = (BOARD - T) / N          # wall centre to wall centre
CLEAR = PITCH - T                # corridor width between wall faces
WALL_H = 2.0        # maze wall height above the floor
RIM_H = 2.0         # outer rim height above the floor (same as walls)
BALL_D = 0.625      # 5/8 in steel ball

# Hole diameters: all standard drill press (Forstner) bit sizes.
# Smaller hole = harder to sink = more coins.
HOLE_D = {"5": 3 / 4, "3": 7 / 8, "1": 1.0, "X": 7 / 8}
HOLE_NAME = {"5": "5 COINS", "3": "3 COINS", "1": "1 COIN", "X": "LOSS"}
START_RING_D = 0.70
TRAP = 1.0                  # trapdoor opening (square)
TRAP_GAP = 1 / 32           # flap clearance, three free sides
TRAP_HINGE_GAP = 1 / 16     # flap clearance, hinge side

BED_W, BED_H = 16.0, 12.0   # laser bed (2018 FYE guide: 12 x 16) - confirm
BORDER = 0.25               # keep parts this far inside the bed
GAP = 0.125                 # space between parts
MAX_SHEETS = 6              # the class budget is about 2


def sheet_x(s):
    return s * (BED_W + 2.0)

# S start, 1/3/5 prize holes, X loss hole, T trapdoor.
# Walls: '---' between rows, '|' between columns.
MAZE = """
+---+---+---+---+---+---+---+---+---+
|       |               | 3 | X | 5 |
+   +   +   +---+   +---+   +   +   +
|   |       |   |   | 1 |       |   |
+   +   +---+   +   +   +   +   +   +
|   |           |           |       |
+   +---+---+---+---+---+---+---+---+
|   |       |                       |
+   +   +---+---+---+---+   +---+   +
|   |             T         | X     |
+   +---+   +---+---+---+   +---+   +
|           | X                 |   |
+---+---+---+---+---+---+---+---+   +
| X                 |           |   |
+---+   +---+   +---+   +---+   +   +
|       |   |   | X |   |   |   |   |
+---+   +   +   +   +   +   +   +   +
| S         |               |       |
+---+---+---+---+---+---+---+---+---+
"""


# --------------------------------------------------------------- parse maze
def parse(text):
    rows = [ln for ln in text.strip("\n").splitlines()]
    if len(rows) != 2 * N + 1 or any(len(r) < 4 * N + 1 for r in rows):
        raise SystemExit("MAZE must be %d lines of %d characters"
                         % (2 * N + 1, 4 * N + 1))
    hw = {(i, j) for i in range(N + 1) for j in range(N)
          if rows[2 * i][4 * j + 1:4 * j + 4] == "---"}
    vw = {(i, j) for i in range(N) for j in range(N + 1)
          if rows[2 * i + 1][4 * j] == "|"}
    cells = {(i, j): rows[2 * i + 1][4 * j + 2]
             for i in range(N) for j in range(N)}
    for j in range(N):
        if (0, j) not in hw or (N, j) not in hw:
            raise SystemExit("outer rim must be closed (row walls)")
    for i in range(N):
        if (i, 0) not in vw or (i, N) not in vw:
            raise SystemExit("outer rim must be closed (column walls)")
    return hw, vw, {k: v for k, v in cells.items() if v != " "}


HW, VW, FEATURES = parse(MAZE)


def gx(j):
    return T / 2 + j * PITCH


def gy(i):
    return BOARD - T / 2 - i * PITCH


def centre(cell):
    i, j = cell
    return gx(j) + PITCH / 2, gy(i) - PITCH / 2


def neighbours(cell):
    """Cells reachable from `cell` in one step (no wall in between)."""
    i, j = cell
    out = []
    if i > 0 and (i, j) not in HW:
        out.append((i - 1, j))
    if i < N - 1 and (i + 1, j) not in HW:
        out.append((i + 1, j))
    if j > 0 and (i, j) not in VW:
        out.append((i, j - 1))
    if j < N - 1 and (i, j + 1) not in VW:
        out.append((i, j + 1))
    return out


def check_maze():
    start = [c for c, f in FEATURES.items() if f == "S"]
    if len(start) != 1:
        raise SystemExit("MAZE needs exactly one S")
    seen, todo = {start[0]}, [start[0]]
    while todo:
        for nb in neighbours(todo.pop()):
            if nb not in seen:
                seen.add(nb)
                todo.append(nb)
    for c, f in FEATURES.items():
        if f in "135" and c not in seen:
            raise SystemExit("prize hole %s at %s is unreachable" % (f, c))
        if f in HOLE_D and HOLE_D[f] > CLEAR - 0.1:
            print("warning: %s hole is wider than the corridor allows" % f)
    return len(seen)


# ------------------------------------------------------------- wall pieces
def wall_runs():
    """Split the walls into straight pieces that butt together.

    A piece that runs through a junction stays whole and the piece that ends
    there stops at its face. At an L corner the row wall (horizontal) wins.
    Where walls cross, the column wall is split.
    """
    def h_through(i, j):
        return 0 < j < N and (i, j - 1) in HW and (i, j) in HW

    def v_through(i, j):
        return 0 < i < N and (i - 1, j) in VW and (i, j) in VW

    runs = []
    for i in range(N + 1):
        j = 0
        while j < N:
            if (i, j) not in HW:
                j += 1
                continue
            j0 = j
            while j < N and (i, j) in HW:
                j += 1
            ends = []
            for jn in (j0, j):
                ends.append(-1 if v_through(i, jn) else 1)
            x0 = gx(j0) - ends[0] * T / 2
            x1 = gx(j) + ends[1] * T / 2
            y = gy(i)
            runs.append({"dir": "h", "rect": (x0, y - T / 2, x1, y + T / 2),
                         "rim": i in (0, N), "edge": i})
    for j in range(N + 1):
        i = 0
        while i < N:
            if (i, j) not in VW:
                i += 1
                continue
            i0 = i
            i += 1
            while i < N and (i, j) in VW and not h_through(i, j):
                i += 1
            ends = []
            for inode in (i0, i):
                touched = (j > 0 and (inode, j - 1) in HW) or \
                          (j < N and (inode, j) in HW)
                ends.append(-1 if touched else 1)
            y_top = gy(i0) + ends[0] * T / 2
            y_bot = gy(i) - ends[1] * T / 2
            x = gx(j)
            runs.append({"dir": "v",
                         "rect": (x - T / 2, y_bot, x + T / 2, y_top),
                         "rim": j in (0, N), "edge": j})
    for r in runs:
        x0, y0, x1, y1 = r["rect"]
        r["length"] = round(max(x1 - x0, y1 - y0), 4)
        if r["rim"]:
            r["name"] = {("h", 0): "RIM-BACK", ("h", N): "RIM-FRONT",
                         ("v", 0): "RIM-LEFT", ("v", N): "RIM-RIGHT"}[
                (r["dir"], r["edge"])]
            r["height"] = RIM_H
        else:
            r["height"] = WALL_H
    lengths = sorted({r["length"] for r in runs if not r["rim"]},
                     reverse=True)
    letter = {L: chr(ord("A") + k) for k, L in enumerate(lengths)}
    for r in runs:
        if not r["rim"]:
            r["name"] = letter[r["length"]]
    return runs


# ------------------------------------------------------- shared geometry
# Every shape goes into SHAPES once; the DXF and the PDF/PNG are both drawn
# from it.  part = "floor" (floor plate, board coords) or "sheet" (already in
# sheet coords).
SHAPES = []


def add(kind, layer, part, **kw):
    SHAPES.append(dict(kind=kind, layer=layer, part=part, **kw))


def rect(x0, y0, x1, y1, layer, part, **kw):
    add("poly", layer, part, pts=[(x0, y0), (x1, y0), (x1, y1), (x0, y1)],
        closed=True, **kw)


def text(s, x, y, h, layer, part, rot=0.0, **kw):
    add("text", layer, part, s=s, pos=(x, y), h=h, rot=rot, **kw)


def frac(d):
    whole, rest = int(d), round((d - int(d)) * 32)
    if rest == 0:
        return "%d" % whole
    num, den = rest, 32
    while num % 2 == 0:
        num, den = num // 2, den // 2
    return ("%d-%d/%d" % (whole, num, den)) if whole else ("%d/%d" % (num, den))


def build_floor(runs):
    # where each wall strip gets glued (rims sit flush with the edge, so
    # their outline would engrave on top of the cut line - reference only)
    for r in runs:
        x0, y0, x1, y1 = r["rect"]
        rect(x0, y0, x1, y1, "REFERENCE" if r["rim"] else "ENGRAVE", "floor",
             wall=True)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        if not r["rim"]:
            text(r["name"], cx, cy, 0.08, "REFERENCE", "floor",
                 rot=90 if r["dir"] == "v" else 0, wall_label=True)
    for cell, f in sorted(FEATURES.items()):
        cx, cy = centre(cell)
        if f == "S":
            add("circle", "ENGRAVE", "floor", c=(cx, cy + 0.12),
                r=START_RING_D / 2)
            text("START", cx, cy - 0.40, 0.12, "RASTER", "floor")
        elif f == "T":
            build_trapdoor(cell, cx, cy)
        else:
            d = HOLE_D[f]
            # drill guide: ring at the finished size + crosshair for the bit
            add("circle", "ENGRAVE", "floor", c=(cx, cy), r=d / 2, hole=f)
            k = d / 2 * 0.8
            add("line", "ENGRAVE", "floor", p=((cx - k, cy), (cx + k, cy)))
            add("line", "ENGRAVE", "floor", p=((cx, cy - k), (cx, cy + k)))
            text("DRILL " + frac(d), cx, cy + 0.17, 0.065, "REFERENCE",
                 "floor")
            if f in "135":
                mouth = neighbours(cell)[0]
                mx, my = centre(mouth)
                ux, uy = cell[1] - mouth[1], mouth[0] - cell[0]
                text(f, mx + 0.30 * ux, my + 0.30 * uy, 0.26, "RASTER",
                     "floor")
    # drawn last so the cut outline sits on top of the rim footprints
    rect(0, 0, BOARD, BOARD, "CUT", "floor")


def build_trapdoor(cell, cx, cy):
    nbs = neighbours(cell)
    along_x = all(nb[0] == cell[0] for nb in nbs)
    h = TRAP / 2
    rect(cx - h, cy - h, cx + h, cy + h, "CUT", "floor", trap=True)
    # flap outline (it is cut as its own piece) and its hinge edge
    a = TRAP - 2 * TRAP_GAP                     # along the corridor
    b = TRAP - TRAP_GAP - TRAP_HINGE_GAP        # across, hinge on front side
    if along_x:
        fx0, fx1 = cx - a / 2, cx + a / 2
        fy0 = cy - h + TRAP_HINGE_GAP
        fy1 = fy0 + b
        rect(fx0, fy0, fx1, fy1, "REFERENCE", "floor", dashed=True)
        add("line", "REFERENCE", "floor", p=((fx0, fy0), (fx1, fy0)),
            dashed=True)
        text("HINGE", cx, fy0 + 0.08, 0.06, "REFERENCE", "floor")
    else:
        fy0, fy1 = cy - a / 2, cy + a / 2
        fx0 = cx - h + TRAP_HINGE_GAP
        fx1 = fx0 + b
        rect(fx0, fy0, fx1, fy1, "REFERENCE", "floor", dashed=True)
        text("HINGE", fx0 + 0.08, cy, 0.06, "REFERENCE", "floor", rot=90)
    text("TRAPDOOR", cx, cy, 0.09, "REFERENCE", "floor")
    return a, b


# ----------------------------------------------------------- sheet nesting
def nest(runs):
    """Lay the floor plate and every strip out on as few sheets as fit."""
    pieces = [(r["height"], r["length"], r["name"]) for r in runs]
    pieces.sort(key=lambda p: (-p[0], -p[1]))
    flap_a = TRAP - 2 * TRAP_GAP
    flap_b = TRAP - TRAP_GAP - TRAP_HINGE_GAP
    pieces.append((flap_b, flap_a, "FLAP"))     # small, goes in last

    y_lo, y_hi = BORDER, BED_H - BORDER
    regions = [[sheet_x(0) + BORDER + BOARD + GAP, BED_W - BORDER]]
    regions += [[sheet_x(s) + BORDER, sheet_x(s) + BED_W - BORDER]
                for s in range(1, MAX_SHEETS)]
    cols = []   # [sheet, x, width, y_cursor]
    nxt = [reg[0] for reg in regions]
    placed = []
    for w, L, name in pieces:
        spot = None
        for col in cols:
            if col[2] >= w and col[3] + L <= y_hi + 1e-9 and col[2] - w < 0.2:
                spot = col
                break
        if spot is None:
            for s, reg in enumerate(regions):
                if nxt[s] + w <= reg[1] + 1e-9:
                    spot = [s, nxt[s], w, y_lo]
                    cols.append(spot)
                    nxt[s] += w + GAP
                    break
        if spot is None:
            raise SystemExit("parts do not fit on %d sheets" % MAX_SHEETS)
        s, x, _, y = spot
        placed.append((s, x, y, w, L, name))
        spot[3] = y + L + GAP
    used = 1 + max(s for s, *_ in placed)
    return placed, nxt[:used], regions[:used]


def build_sheets(placed, nxt, regions):
    count = len(regions)
    for s in range(count):
        ox = sheet_x(s)
        rect(ox, 0, ox + BED_W, BED_H, "REFERENCE", "sheet")
        rect(ox + BORDER, BORDER, ox + BED_W - BORDER, BED_H - BORDER,
             "REFERENCE", "sheet", dashed=True)
        text("SHEET %d OF %d  -  1/8 PLYWOOD, LASER BED %g x %g IN "
             "(CONFIRM WITH FYELIC)" % (s + 1, count, BED_W, BED_H),
             ox + BED_W / 2, BED_H + 0.35, 0.22, "REFERENCE", "sheet")
    for s, x, y, w, L, name in placed:
        rect(x, y, x + w, y + L, "CUT", "sheet")
        if name == "RIM-FRONT":
            text("THE LABYRINTH", x + w / 2, y + L / 2,
                 min(0.8, 0.5 * w), "RASTER", "sheet", rot=90)
        else:
            text(name, x + w / 2, y + L / 2, min(0.18, w * 0.4),
                 "REFERENCE", "sheet", rot=90)
    free = regions[-1][1] - nxt[-1]
    if free > 1.0:
        x0, x1 = nxt[-1], regions[-1][1]
        rect(x0, BORDER, x1, BED_H - BORDER, "REFERENCE", "sheet",
             dashed=True)
        text("FREE: %.1f x %.1f IN" % (free, BED_H - 2 * BORDER),
             (x0 + x1) / 2, BED_H / 2 + 0.25, 0.22, "REFERENCE", "sheet")
        text("frame / brackets / joystick box", (x0 + x1) / 2,
             BED_H / 2 - 0.15, 0.16, "REFERENCE", "sheet")


def floor_to_sheet(x, y):
    return x + sheet_x(0) + BORDER, y + BORDER


# --------------------------------------------------------------------- DXF
def write_dxf(path, notes):
    doc = ezdxf.new("R2010", setup=True)
    doc.units = ezdxf.units.IN
    doc.header["$INSUNITS"] = 1
    doc.header["$MEASUREMENT"] = 0
    doc.header["$LUNITS"] = 2
    doc.header["$LUPREC"] = 3
    doc.header["$LTSCALE"] = 0.25
    for name, color in (("CUT", 1), ("ENGRAVE", 5), ("RASTER", 7),
                        ("REFERENCE", 8)):
        layer = doc.layers.add(name, color=color, lineweight=0)
        if name == "REFERENCE":
            layer.dxf.plot = 0          # never sent to the laser
    doc.styles.add("LAB", font="arial.ttf")
    msp = doc.modelspace()

    for sh in SHAPES:
        tf = floor_to_sheet if sh["part"] == "floor" else (lambda x, y: (x, y))
        attribs = {"layer": sh["layer"]}
        if sh.get("dashed"):
            attribs["linetype"] = "DASHED"
        if sh["kind"] == "poly":
            msp.add_lwpolyline([tf(*p) for p in sh["pts"]],
                               close=sh["closed"], dxfattribs=attribs)
        elif sh["kind"] == "line":
            msp.add_line(tf(*sh["p"][0]), tf(*sh["p"][1]),
                         dxfattribs=attribs)
        elif sh["kind"] == "circle":
            msp.add_circle(tf(*sh["c"]), sh["r"], dxfattribs=attribs)
        elif sh["kind"] == "text":
            attribs["style"] = "LAB"
            msp.add_text(sh["s"], height=sh["h"], rotation=sh["rot"],
                         dxfattribs=attribs).set_placement(
                tf(*sh["pos"]), align=TextEntityAlignment.MIDDLE_CENTER)
    msp.add_mtext("\\P".join(notes), dxfattribs={
        "layer": "REFERENCE", "style": "LAB", "char_height": 0.16,
        "width": 2 * BED_W + 2, "insert": (0, -0.6)})
    doc.saveas(path)
    return doc


# ------------------------------------------------------- matplotlib output
LAYER_STYLE = {"CUT": ("#d62728", 0.9), "ENGRAVE": ("#1f5fbf", 0.6),
               "RASTER": ("#111111", 0.6), "REFERENCE": ("#8a8a8a", 0.4)}


def draw(ax, shapes, tf, mono=False, font_scale=1.0):
    for sh in shapes:
        color, lw = LAYER_STYLE[sh["layer"]]
        if mono:
            color = "#000000" if sh["layer"] != "REFERENCE" else "#555555"
        ls = (0, (4, 3)) if sh.get("dashed") else "solid"
        if sh["kind"] == "poly":
            pts = [tf(*p) for p in sh["pts"]]
            if sh["closed"]:
                pts.append(pts[0])
            if sh.get("wall"):
                xs, ys = zip(*pts)
                ax.fill(xs, ys, color="#c9c9c9" if mono else "#bcd0ee",
                        lw=0, zorder=1)
            if sh.get("trap"):
                xs, ys = zip(*pts)
                ax.fill(xs, ys, fill=False, hatch="////", color=color, lw=0)
            ax.plot(*zip(*pts), color=color, lw=lw, ls=ls, zorder=2)
        elif sh["kind"] == "line":
            ax.plot(*zip(*[tf(*p) for p in sh["p"]]), color=color, lw=lw,
                    ls=ls, zorder=2)
        elif sh["kind"] == "circle":
            ax.add_patch(Circle(tf(*sh["c"]), sh["r"], fill=False,
                                ec=color, lw=lw, ls=ls, zorder=2))
        elif sh["kind"] == "text":
            # TEXT height is cap height; Arial caps are ~0.716 em
            ax.text(*tf(*sh["pos"]), sh["s"], rotation=sh["rot"],
                    fontsize=sh["h"] * 72 / 0.716 * font_scale,
                    color=color, ha="center", va="center",
                    family="DejaVu Sans", zorder=3, clip_on=True)


def ident(x, y):
    return x, y


def write_preview(dxf_path, png_path, sheets=2):
    """Render the saved DXF itself, so the picture shows what AutoCAD gets."""
    from ezdxf.addons.drawing import Frontend, RenderContext
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
    from ezdxf.addons.drawing.config import Configuration, BackgroundPolicy

    doc = ezdxf.readfile(dxf_path)
    fig = plt.figure(figsize=(7.5 * sheets, 7.2), dpi=120)
    ax = fig.add_axes([0.01, 0.01, 0.98, 0.98])
    cfg = Configuration(background_policy=BackgroundPolicy.WHITE)
    Frontend(RenderContext(doc), MatplotlibBackend(ax), config=cfg) \
        .draw_layout(doc.modelspace())
    ax.set_aspect("equal")
    fig.savefig(png_path, facecolor="white")
    plt.close(fig)


def write_board_top(path):
    """Top view of the playfield as it looks assembled (for slides/report)."""
    fig = plt.figure(figsize=(7, 7.6), dpi=160)
    ax = fig.add_axes([0.04, 0.03, 0.92, 0.86])
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), BOARD, BOARD, fc="#e9d3a8", ec="#7a5a2e",
                           lw=1.5))
    for sh in SHAPES:
        if sh["part"] != "floor":
            continue
        if sh["kind"] == "poly" and sh.get("wall"):
            (x0, y0), _, (x1, y1), _ = sh["pts"]
            ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="#6b4a24",
                                   ec="none", zorder=3))
        elif sh["kind"] == "poly" and sh.get("trap"):
            (x0, y0), _, (x1, y1), _ = sh["pts"]
            ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="#f2b134",
                                   ec="#8a5a00", lw=1, hatch="xx", zorder=2))
        elif sh["kind"] == "circle" and sh.get("hole"):
            f = sh["hole"]
            fc = "#3a0d0d" if f == "X" else "#101010"
            ax.add_patch(Circle(sh["c"], sh["r"], fc=fc, ec="#000000",
                                zorder=2))
        elif sh["kind"] == "circle":
            ax.add_patch(Circle(sh["c"], sh["r"], fill=False, ec="#2a6f2a",
                                lw=1.5, zorder=2))
        elif sh["kind"] == "text" and sh["layer"] == "RASTER":
            ax.text(*sh["pos"], sh["s"], fontsize=sh["h"] * 72 / 0.716 * 0.6,
                    ha="center", va="center", color="#3b2a14",
                    weight="bold", zorder=4)
    s = [c for c, f in FEATURES.items() if f == "S"][0]
    ax.add_patch(Circle((centre(s)[0], centre(s)[1] + 0.12), BALL_D / 2,
                        fc="#b8bcc4", ec="#555", lw=1, zorder=5))
    ax.set_xlim(-0.2, BOARD + 0.2)
    ax.set_ylim(-0.75, BOARD + 0.2)
    ax.text(BOARD / 2, -0.4, "FRONT  (player + joystick)", ha="center",
            fontsize=11, color="#555")
    fig.suptitle("The Labyrinth - maze board, top view (%.1f in square)"
                 % BOARD, fontsize=13, y=0.97)
    fig.text(0.5, 0.915, "black = prize holes (1 / 3 / 5 coins)   dark red "
             "= LOSS   yellow = trapdoor   grey ball = start",
             ha="center", fontsize=8.5, color="#444")
    fig.savefig(path)
    plt.close(fig)


def cut_list(runs):
    groups = {}
    for r in runs:
        key = r["name"]
        g = groups.setdefault(key, [r["length"], r["height"], 0])
        g[2] += 1
    rims = sorted((k for k in groups if k.startswith("RIM")))
    walls = sorted(k for k in groups if not k.startswith("RIM"))
    return [(k,) + tuple(groups[k]) for k in walls + rims]


def template_page_header(fig, title, sub):
    fig.text(0.5, 0.965, title, ha="center", fontsize=13, weight="bold")
    fig.text(0.5, 0.945, sub, ha="center", fontsize=8.5, color="#333")


def write_templates(letter_path, full_path, runs, cl):
    floor = [s for s in SHAPES if s["part"] == "floor"]
    # ----- one big page for a plotter / large-format printer
    side = BOARD + 1.5
    with PdfPages(full_path) as pdf:
        fig = plt.figure(figsize=(side, side))
        ax = fig.add_axes([0.75 / side, 0.75 / side, BOARD / side,
                           BOARD / side])
        ax.set_xlim(0, BOARD)
        ax.set_ylim(0, BOARD)
        ax.axis("off")
        draw(ax, floor, ident, mono=True)
        fig.text(0.5, 1 - 0.35 / side, "THE LABYRINTH - FLOOR TEMPLATE 1:1 "
                 "(print at 100%%, check the 1 in bar)", ha="center",
                 fontsize=11)
        bar = fig.add_axes([0.75 / side, 0.2 / side, 1 / side, 0.2 / side])
        bar.set_xlim(0, 1)
        bar.set_ylim(0, 0.2)
        bar.axis("off")
        bar.add_patch(Rectangle((0, 0), 1, 0.2, fc="#000"))
        fig.text(2.0 / side, 0.25 / side, "= 1.000 in", fontsize=9)
        pdf.savefig(fig)
        plt.close(fig)

    # ----- letter pages: page 1 instructions, then four 1:1 quadrants
    W, H = 8.5, 11.0
    half = BOARD / 2
    ov = 0.5
    with PdfPages(letter_path) as pdf:
        fig = plt.figure(figsize=(W, H))
        template_page_header(fig, "The Labyrinth - cardboard prototype "
                             "template", "GE1501 Group 1  -  inches  -  "
                             "print every page at 100% / Actual size")
        lines = [
            "1. Check scale: the square below must measure exactly 2.000 x "
            "2.000 in.",
            "2. Trim the RIGHT edge of pages A2/B2 and the TOP edge of pages "
            "A1/A2 on the",
            "    dashed line, overlap onto the neighbour page so the lines "
            "match, tape.",
            "3. Glue the sheet to the floor board (glue stick / spray "
            "mount), let it dry flat.",
            "4. Holes: drill press + the bit size printed in each ring, board "
            "clamped on scrap",
            "    wood. Centre the bit point on the crosshair.",
            "5. Trapdoor: cut the hatched square; the flap is a separate "
            "piece (dashed).",
            "6. Walls: cut strips to the lengths below, glue on the shaded "
            "footprints.",
            "",
            "Ball: %s in steel.  Corridor: %.3f in between walls.  "
            "Walls %.3f thick, %s in tall;" % (frac(BALL_D), CLEAR, T,
                                               frac(WALL_H)),
            "rim %s in tall.  Floor: %.2f x %.2f in." % (frac(RIM_H), BOARD,
                                                         BOARD),
        ]
        for k, ln in enumerate(lines):
            fig.text(0.07, 0.905 - k * 0.022, ln, fontsize=9,
                     family="DejaVu Sans")
        # 2 x 2 in check square at 1:1
        sq = fig.add_axes([(W - 2.8) / W, 0.8 / H, 2 / W, 2 / H])
        sq.set_xlim(0, 2)
        sq.set_ylim(0, 2)
        sq.axis("off")
        sq.add_patch(Rectangle((0, 0), 2, 2, fill=False, ec="#000", lw=1))
        sq.text(1, 1, "2.000 in\nsquare", ha="center", va="center",
                fontsize=9)
        # cut list
        y0 = 0.64
        n_rim = sum(c[3] for c in cl if c[0].startswith("RIM"))
        fig.text(0.07, y0, "WALL STRIPS  (%s in thick: %d walls + %d rim "
                 "pieces)" % (frac(T), sum(c[3] for c in cl) - n_rim, n_rim),
                 fontsize=10, weight="bold")
        fig.text(0.07, y0 - 0.025, "piece      length (in)      height (in)"
                 "      qty", fontsize=9, family="DejaVu Sans Mono")
        for k, (name, L, h, q) in enumerate(cl):
            fig.text(0.07, y0 - 0.047 - k * 0.019, "%-9s  %9.3f  %15.3f  %9d"
                     % (name, L, h, q), fontsize=9,
                     family="DejaVu Sans Mono")
        yh = y0 - 0.047 - len(cl) * 0.019 - 0.02
        fig.text(0.07, yh, "HOLES", fontsize=10, weight="bold")
        counts = {}
        for f in FEATURES.values():
            if f in HOLE_D:
                counts[f] = counts.get(f, 0) + 1
        for k, f in enumerate(("5", "3", "1", "X")):
            if f in counts:
                fig.text(0.07, yh - 0.022 - k * 0.019, "%-8s  %d x  drill %s "
                         "in" % (HOLE_NAME[f], counts[f], frac(HOLE_D[f])),
                         fontsize=9, family="DejaVu Sans Mono")
        pdf.savefig(fig)
        plt.close(fig)

        tiles = [("A1", 0, 1), ("A2", 1, 1), ("B1", 0, 0), ("B2", 1, 0)]
        for name, cx, cy in tiles:
            x0 = -0.3 if cx == 0 else half - ov
            x1 = half + ov if cx == 0 else BOARD + 0.3
            y0 = -0.3 if cy == 0 else half - ov
            y1 = half + ov if cy == 0 else BOARD + 0.3
            fig = plt.figure(figsize=(W, H))
            left, bottom = (W - (x1 - x0)) / 2, 1.2
            ax = fig.add_axes([left / W, bottom / H, (x1 - x0) / W,
                               (y1 - y0) / H])
            ax.set_xlim(x0, x1)
            ax.set_ylim(y0, y1)
            ax.axis("off")
            draw(ax, floor, ident, mono=True)
            ax.axvline(half, color="#000", lw=0.5, ls=(0, (6, 4)))
            ax.axhline(half, color="#000", lw=0.5, ls=(0, (6, 4)))
            where = {"A1": "back-left", "A2": "back-right",
                     "B1": "front-left", "B2": "front-right"}[name]
            template_page_header(fig, "Page %s  -  %s quarter of the floor"
                                 % (name, where), "1:1 - dashed lines = "
                                 "board centre lines, overlap pages here")
            bar = fig.add_axes([left / W, 0.6 / H, 1 / W, 0.15 / H])
            bar.set_xlim(0, 1)
            bar.set_ylim(0, 0.15)
            bar.axis("off")
            bar.add_patch(Rectangle((0, 0), 1, 0.15, fc="#000"))
            fig.text((left + 1.15) / W, 0.62 / H, "= 1.000 in   "
                     "(FRONT = player side is the bottom of the board)",
                     fontsize=8)
            pdf.savefig(fig)
            plt.close(fig)


# -------------------------------------------------------------------- main
def main():
    reach = check_maze()
    runs = wall_runs()
    build_floor(runs)
    placed, nxt, regions = nest(runs)
    build_sheets(placed, nxt, regions)
    cl = cut_list(runs)
    wall_len = sum(r["length"] for r in runs if not r["rim"])
    sheet_of = {}
    for s, _, _, _, _, name in placed:
        sheet_of.setdefault(name, set()).add(s + 1)
    notes = [
        "THE LABYRINTH - GE1501 GROUP 1 - LASER LAYOUT (inches, 1:1)",
        "Layers: CUT (red) cut through | ENGRAVE (blue) outline engraved on "
        "the surface: wall footprints and drill guides | RASTER (black) "
        "filled-in engraving: text | "
        "REFERENCE (grey) not plotted",
        "Holes are NOT laser cut: drill them on the drill press with the bit "
        "size in each ring (Forstner, board clamped on scrap).",
        "Ball %s in steel. Corridor %.3f in. Walls %.3f in thick x %s in "
        "tall, rim %s in tall. Interior walls total %.1f in of strip."
        % (frac(BALL_D), CLEAR, T, frac(WALL_H), frac(RIM_H), wall_len),
        "Bed size and material from the 2018 FYE laser guide (12 x 16 in, "
        "1/8 in). Confirm with FYELIC before cutting.",
    ]
    os.makedirs(OUT_DIR, exist_ok=True)
    dxf_path = os.path.join(OUT_DIR, "Labyrinth_Board.dxf")
    write_dxf(dxf_path, notes)
    write_preview(dxf_path, os.path.join(OUT_DIR, "Labyrinth_preview.png"),
                  len(regions))
    write_board_top(os.path.join(OUT_DIR, "Labyrinth_board_top.png"))
    write_templates(os.path.join(OUT_DIR, "Labyrinth_Template_Letter.pdf"),
                    os.path.join(OUT_DIR, "Labyrinth_Template_FullSize.pdf"),
                    runs, cl)
    print("cells reachable from START: %d / %d" % (reach, N * N))
    print("pitch %.4f  corridor %.4f  walls: %d interior pieces, %.1f in"
          % (PITCH, CLEAR, sum(1 for r in runs if not r["rim"]), wall_len))
    for name, L, h, q in cl:
        print("  %-9s L=%.3f  H=%.3f  x%d  (sheet %s)"
              % (name, L, h, q, "+".join(map(str, sorted(sheet_of[name])))))
    print("laser sheets needed: %d (class budget is about 2); free on the "
          "last sheet: %.2f in wide" % (len(regions), regions[-1][1] - nxt[-1]))
    return dxf_path


if __name__ == "__main__":
    main()
