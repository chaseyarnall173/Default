"""Build the AC2 Duplo kangaroo 3-view orthographic drawing (mm) as a DXF.

Assembled coordinates (mm): x = left->right (front view), y = front->back,
z = up. Third-angle layout: TOP view above FRONT, RIGHT view to its right.

Pieces
  B  ramp brick    x 0-47,   z 0-37   (tall back at x=0, R29.6 concave ramp)
  A  2x4 arch      x 0-64,   z 37-75  (opening x 16-48, 19 tall), on B's studs
  C  curved brick  x 48-100, z 75-104 (R17.19 round on the right end), on A
"""
import math
import sys

import ezdxf
from ezdxf.enums import TextEntityAlignment

OUT = sys.argv[1] if len(sys.argv) > 1 else "AC2_Duplo_Kangaroo.dxf"

# ---------------------------------------------------------------- dimensions
W = 31.0                 # depth of every piece (front-back)
STUD_D, STUD_H = 9.0, 5.0
STUD_R = STUD_D / 2
ROW_Y = (7.5, 23.5)      # stud rows (3 mm from front/back edge + radius)
TUBE_Y = W / 2

# B - ramp brick
B_L, B_H, B_LIP, B_TOPW, B_R = 47.0, 37.0, 9.0, 16.0, 29.6
B_CX, B_CZ = B_TOPW + B_R, B_H                        # arc centre (45.6, 37)
B_ARC_END_X = B_CX - math.sqrt(B_R**2 - (B_H - B_LIP) ** 2)   # meets lip
B_STUD_X = (8.0,)
B_TUBE_X, B_TUBE_R = (16.0, 32.0), 6.5

# A - 2x4 arch
A_X0, A_L, A_Z0, A_H = 0.0, 64.0, B_H, 38.0
A_LEG, A_OPEN_H = 16.0, 19.0
A_Z1 = A_Z0 + A_H                                     # 75
A_OPEN_Z = A_Z0 + A_OPEN_H                            # 56
A_STUD_X = (8.0, 24.0, 40.0, 56.0)
A_TUBE_X, A_TUBE_R = 32.0, 4.5

# C - curved-top brick
C_X0, C_L, C_H, C_R = 48.0, 52.0, 29.0, 17.19
C_X1, C_Z0 = C_X0 + C_L, A_Z1                         # 100, 75
C_Z1 = C_Z0 + C_H                                     # 104
C_CX, C_CZ = C_X1 - C_R, C_Z1 - C_R                   # arc centre
C_STUD_X = (C_X0 + 8.0, C_X0 + 24.0)                  # 56, 72
C_TUBE_X, C_TUBE_R = (C_X0 + 16.0, C_X0 + 32.0), 6.5  # 64, 80

TOTAL_L, TOTAL_H = C_X1, C_Z1


def ramp_z(x):
    """Height of B's top / ramp surface at x."""
    if x <= B_TOPW:
        return B_H
    if x >= B_ARC_END_X:
        return B_LIP
    return B_CZ - math.sqrt(B_R**2 - (B_CX - x) ** 2)


def c_top_z(x):
    """Height of C's top / rounded surface at x."""
    if x <= C_CX:
        return C_Z1
    return C_CZ + math.sqrt(C_R**2 - (x - C_CX) ** 2)


# ------------------------------------------------------------------ document
doc = ezdxf.new("R2010", setup=False)
doc.units = ezdxf.units.MM
doc.header["$INSUNITS"] = 4
doc.header["$MEASUREMENT"] = 1
doc.header["$LUNITS"] = 2
doc.header["$LUPREC"] = 2
doc.header["$LTSCALE"] = 0.3
doc.header["$LWDISPLAY"] = 1

# acadiso.lin patterns
doc.linetypes.add("HIDDEN", pattern=[9.525, 6.35, -3.175],
                  description="Hidden __ __ __ __ __")
doc.linetypes.add("CENTER", pattern=[50.8, 31.75, -6.35, 6.35, -6.35],
                  description="Center ____ _ ____ _ ____")

LAYERS = {  # name: (ACI color, linetype, lineweight in 1/100 mm)
    "VISIBLE": (7, "Continuous", 50),
    "HIDDEN": (1, "HIDDEN", 25),
    "CENTER": (3, "CENTER", 18),
    "DIMENSIONS": (4, "Continuous", 18),
    "TEXT": (7, "Continuous", 25),
}
for name, (color, lt, lw) in LAYERS.items():
    doc.layers.add(name, color=color, linetype=lt, lineweight=lw)

doc.styles.add("AC2", font="arial.ttf")
ds = doc.dimstyles.add("AC2_MM")
ds.dxf.dimtxsty = "AC2"
for k, v in dict(dimtxt=2.5, dimasz=2.5, dimexo=1.0, dimexe=1.5, dimgap=0.8,
                 dimdec=2, dimzin=8, dimtad=1, dimtih=0, dimtoh=0, dimcen=0,
                 dimlunit=2, dimdsep=ord("."), dimtofl=1, dimclrd=0,
                 dimclre=0, dimclrt=0, dimscale=1.0, dimlfac=1.0).items():
    ds.set_dxf_attrib(k, v)

msp = doc.modelspace()
GAP_TOP = 40.0   # front-view top (z = 100 with studs) to top-view front edge
GAP_RIGHT = 45.0
TOP_OY = 140.0                               # top view: Y = TOP_OY + y
RIGHT_OX = TOTAL_L + GAP_RIGHT               # right view: X = RIGHT_OX + y


def line(p1, p2, layer):
    msp.add_line(p1, p2, dxfattribs={"layer": layer})


def poly(pts, layer, close=False):
    msp.add_lwpolyline(pts, close=close, dxfattribs={"layer": layer})


def arc(c, r, a0, a1, layer):
    msp.add_arc(c, r, a0, a1, dxfattribs={"layer": layer})


def circle(c, r, layer):
    msp.add_circle(c, r, dxfattribs={"layer": layer})


def cmark(c, size=2.0):
    line((c[0] - size, c[1]), (c[0] + size, c[1]), "CENTER")
    line((c[0], c[1] - size), (c[0], c[1] + size), "CENTER")


def vcl(x, z0, z1, ext=2.0):
    line((x, z0 - ext), (x, z1 + ext), "CENTER")


def hcl(y, x0, x1, ext=2.0):
    line((x0 - ext, y), (x1 + ext, y), "CENTER")


def rect(x0, y0, x1, y1, layer):
    poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], layer, close=True)


def open_box(x0, y0, x1, y1, layer):
    """Three sides of a rectangle (bottom side omitted - it lies on a face)."""
    poly([(x0, y0), (x0, y1), (x1, y1), (x1, y0)], layer)


def label(text, x, y, h=3.5):
    msp.add_text(text, height=h, dxfattribs={"layer": "TEXT", "style": "AC2"}
                 ).set_placement((x, y), align=TextEntityAlignment.TOP_CENTER)


def lin_dim(p1, p2, base, angle=0, override=None):
    d = msp.add_linear_dim(base=base, p1=p1, p2=p2, angle=angle,
                           dimstyle="AC2_MM", override=override,
                           dxfattribs={"layer": "DIMENSIONS"})
    d.render()


# ================================================================ FRONT VIEW
# B - ramp brick profile
poly([(B_TOPW, B_H), (0, B_H), (0, 0), (B_L, 0), (B_L, B_LIP),
      (B_ARC_END_X, B_LIP)], "VISIBLE")
arc((B_CX, B_CZ), B_R, 180,
    math.degrees(math.atan2(B_LIP - B_CZ, B_ARC_END_X - B_CX)) % 360,
    "VISIBLE")
# A - arch
poly([(A_LEG, A_Z0), (A_LEG, A_OPEN_Z), (A_L - A_LEG, A_OPEN_Z),
      (A_L - A_LEG, A_Z0), (A_L, A_Z0), (A_L, A_Z1), (0, A_Z1), (0, A_Z0)],
     "VISIBLE")
line((0, A_Z0), (A_LEG, A_Z0), "VISIBLE")          # left leg on B
# C - curved brick (bottom edge shared with A's top from 48 to 64)
poly([(C_CX, C_Z1), (C_X0, C_Z1), (C_X0, C_Z0), (C_X1, C_Z0),
      (C_X1, C_CZ)], "VISIBLE")
arc((C_CX, C_CZ), C_R, 0, 90, "VISIBLE")
# studs on top
for x in A_STUD_X[:3]:
    open_box(x - STUD_R, A_Z1, x + STUD_R, A_Z1 + STUD_H, "VISIBLE")
    vcl(x, A_Z1, A_Z1 + STUD_H)
for x in C_STUD_X:
    open_box(x - STUD_R, C_Z1, x + STUD_R, C_Z1 + STUD_H, "VISIBLE")
    vcl(x, C_Z1, C_Z1 + STUD_H)
cmark((B_CX, B_CZ))
cmark((C_CX, C_CZ))

# front-view dimensions (5)
lin_dim((A_LEG, A_Z0), (A_L - A_LEG, A_Z0), base=(0, A_Z0 + 12))      # 32
lin_dim((0, 0), (B_L, 0), base=(0, -10))                              # 47
lin_dim((0, 0), (A_L, A_Z0), base=(0, -20))                        # 64
ang = math.radians(215)
d = msp.add_radius_dim(center=(B_CX, B_CZ), radius=B_R,
                       location=(B_CX + 16 * math.cos(ang),
                                 B_CZ + 16 * math.sin(ang)),
                       dimstyle="AC2_MM", override={"dimtmove": 0},
                       dxfattribs={"layer": "DIMENSIONS"})
d.render()
d = msp.add_radius_dim(center=(C_CX, C_CZ), radius=C_R, angle=40,
                       dimstyle="AC2_MM", override={"dimdec": 2},
                       dxfattribs={"layer": "DIMENSIONS"})
d.render()
label("FRONT VIEW", TOTAL_L / 2, -28)

# ================================================================== TOP VIEW
def T(x, y):
    return (x, TOP_OY + y)


poly([T(0, 0), T(TOTAL_L, 0), T(TOTAL_L, W), T(0, W)], "VISIBLE", close=True)
line(T(C_X0, 0), T(C_X0, W), "VISIBLE")              # C's left end
for x in (A_LEG, B_ARC_END_X, B_L, A_L):              # 16, 36, 47, 64
    line(T(x, 0), T(x, W), "HIDDEN")
studs_top = [*A_STUD_X[:3], *C_STUD_X]
for x in studs_top:
    for y in ROW_Y:
        circle(T(x, y), STUD_R, "VISIBLE")
    line(T(x, ROW_Y[0] - STUD_R - 2), T(x, ROW_Y[1] + STUD_R + 2), "CENTER")
for y in ROW_Y:
    hcl(TOP_OY + y, studs_top[0] - STUD_R, studs_top[-1] + STUD_R)
tubes = [(x, B_TUBE_R) for x in B_TUBE_X] + [(A_TUBE_X, A_TUBE_R)] + \
        [(x, C_TUBE_R) for x in C_TUBE_X]
for x, r in tubes:
    circle(T(x, TUBE_Y), r, "HIDDEN")
for x in sorted({x for x, _ in tubes}):
    line(T(x, TUBE_Y - 6.5 - 2), T(x, TUBE_Y + 6.5 + 2), "CENTER")
hcl(TOP_OY + TUBE_Y, B_TUBE_X[0] - B_TUBE_R, C_TUBE_X[-1] + C_TUBE_R)

# top-view dimensions (5)
lin_dim(T(A_STUD_X[0], ROW_Y[1]), T(A_STUD_X[1], ROW_Y[1]),
        base=T(0, W + 8))                                             # 16
lin_dim(T(C_X0, W), T(C_X1, W), base=T(0, W + 8))                     # 52
lin_dim(T(0, W), T(TOTAL_L, W), base=T(0, W + 17))                    # 100
d = msp.add_diameter_dim(center=T(A_STUD_X[0], ROW_Y[0]), radius=STUD_R,
                         location=T(-7, -6), dimstyle="AC2_MM",
                         override={"dimtmove": 0},
                         dxfattribs={"layer": "DIMENSIONS"})
d.render()
d = msp.add_diameter_dim(center=T(C_TUBE_X[1], TUBE_Y), radius=C_TUBE_R,
                         location=T(TOTAL_L + 8, -6), dimstyle="AC2_MM",
                         override={"dimtmove": 0},
                         dxfattribs={"layer": "DIMENSIONS"})
d.render()
label("TOP VIEW", TOTAL_L / 2, TOP_OY - 14)

# ================================================================ RIGHT VIEW
def R(y, z):
    return (RIGHT_OX + y, z)


poly([R(0, 0), R(W, 0), R(W, C_Z1), R(0, C_Z1)], "VISIBLE", close=True)
for z in (B_LIP, A_Z0, C_Z0):                         # 9, 37, 75
    line(R(0, z), R(W, z), "VISIBLE")
for y in ROW_Y:
    open_box(RIGHT_OX + y - STUD_R, C_Z1, RIGHT_OX + y + STUD_R,
             C_Z1 + STUD_H, "VISIBLE")
    vcl(RIGHT_OX + y, C_Z1, C_Z1 + STUD_H)
    # arch studs hidden behind the curved brick
    open_box(RIGHT_OX + y - STUD_R, A_Z1, RIGHT_OX + y + STUD_R,
             A_Z1 + STUD_H, "HIDDEN")
    vcl(RIGHT_OX + y, A_Z1, A_Z1 + STUD_H)
line(R(0, A_OPEN_Z), R(W, A_OPEN_Z), "HIDDEN")        # top of arch opening

# right-view dimensions (5)
lin_dim(R(0, 0), R(W, 0), base=R(0, -10))                             # 31
lin_dim(R(W, 0), R(W, B_H), base=R(W + 10, 0), angle=90)              # 37
lin_dim(R(W, A_Z0), R(W, A_Z1), base=R(W + 10, 0), angle=90)          # 38
lin_dim(R(W, C_Z0), R(W, C_Z1), base=R(W + 10, 0), angle=90)          # 20
lin_dim(R(0, 0), R(0, B_LIP), base=R(-10, 0), angle=90)               # 9
label("RIGHT SIDE VIEW", RIGHT_OX + W / 2, -28)

# ======================================================= notes + title block
NX, NY = RIGHT_OX - 5, TOP_OY + W + 30
notes = "\\P".join([
    "ASSUMPTIONS:",
    "1. All dimensions in mm, estimated to approx. 0.5 mm.",
    "2. Wall thickness of each piece is shown with one line (thin-wall), "
    "so inside walls coincide with outside faces.",
    "3. Small vertical ribs along the inside bottom edges of each piece "
    "are not shown.",
    "4. LEGO/DUPLO text is not shown; studs are shown as single circles.",
    "5. Underside tubes are shown only as hidden circles in the top view; "
    "hidden tube lines and studs plugged into the piece above are not shown.",
    "6. Tangent edges (curved surface blending into a flat surface) are "
    "not drawn.",
    "7. Third-angle projection.",
])
msp.add_mtext(notes, dxfattribs={"layer": "TEXT", "style": "AC2",
                                 "char_height": 2.5, "width": 95,
                                 "insert": (NX, NY)})
TBX, TBY = RIGHT_OX - 5, -45
rect(TBX, TBY, TBX + 95, TBY - 22, "VISIBLE")
line((TBX, TBY - 11), (TBX + 95, TBY - 11), "VISIBLE")
msp.add_text("AC2 - ORTHOGRAPHIC DUPLO KANGAROO", height=3,
             dxfattribs={"layer": "TEXT", "style": "AC2"}).set_placement(
    (TBX + 2, TBY - 4))
msp.add_text("UNITS: mm    SCALE 1:1", height=2.5,
             dxfattribs={"layer": "TEXT", "style": "AC2"}).set_placement(
    (TBX + 2, TBY - 8.5))
msp.add_text("NAME:                         DATE:", height=2.5,
             dxfattribs={"layer": "TEXT", "style": "AC2"}).set_placement(
    (TBX + 2, TBY - 17))

doc.saveas(OUT)
print("wrote", OUT)
print(f"B arc meets lip at x={B_ARC_END_X:.2f}; C arc centre=({C_CX:.2f},{C_CZ:.2f})")
