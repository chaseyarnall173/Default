"""Figure 6.7 - (a) converging lens, (b) diverging lens (thin-lens ray sketches), (c) the eye.
Writes figures/ch06-lenses.svg."""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "ch06-lenses.svg"
AMBER, TEXT, MUTED, STROKE = "#e09f1f", "#1f2933", "#52606d", "#52606d"
GLASS = "#cfe0f0"
W, H = 680, 290
AX = 150   # optical axis y
els = []


def text(x, y, s, size=12, color=TEXT, anchor="start", weight=400):
    els.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{color}" text-anchor="{anchor}" '
               f'font-weight="{weight}">{s}</text>')


def head(x, y, ux, uy, color, size):
    px, py = -uy, ux
    b1 = (x - size * ux + 0.55 * size * px, y - size * uy + 0.55 * size * py)
    b2 = (x - size * ux - 0.55 * size * px, y - size * uy - 0.55 * size * py)
    els.append(f'<polygon points="{x:.1f},{y:.1f} {b1[0]:.1f},{b1[1]:.1f} {b2[0]:.1f},{b2[1]:.1f}" fill="{color}"/>')


def line(x1, y1, x2, y2, color=AMBER, w=1.8, dash=None, op=1):
    ds = f' stroke-dasharray="{dash}"' if dash else ""
    els.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{w}" opacity="{op}"{ds}/>')


def axis(x0, x1):
    line(x0, AX, x1, AX, MUTED, 0.9, "5 4")


def convex(cx, h, t):
    """Biconvex lens outline centered at cx, half-height h, center thickness t."""
    # two circular arcs through (cx, AX-h), (cx +/- t/2, AX), (cx, AX+h)
    s = t / 2
    r = (h * h + s * s) / (2 * s)
    return (f'<path d="M{cx},{AX-h} A{r:.1f},{r:.1f} 0 0 1 {cx},{AX+h} A{r:.1f},{r:.1f} 0 0 1 {cx},{AX-h} Z" '
            f'fill="{GLASS}" stroke="{STROKE}" stroke-width="1.3"/>')


def concave(cx, h, t_edge, t_mid):
    s = (t_edge - t_mid) / 2
    r = (h * h + s * s) / (2 * s)
    xl, xr = cx - t_edge / 2, cx + t_edge / 2
    return (f'<path d="M{xl:.1f},{AX-h} L{xr:.1f},{AX-h} A{r:.1f},{r:.1f} 0 0 0 {xr:.1f},{AX+h} '
            f'L{xl:.1f},{AX+h} A{r:.1f},{r:.1f} 0 0 0 {xl:.1f},{AX-h} Z" fill="{GLASS}" stroke="{STROKE}" stroke-width="1.3"/>')


# ---------------- (a) converging ----------------
text(14, 22, "(a) Converging (convex) lens", 13, TEXT, weight=650)
LX, F = 95, 80
axis(10, 215)
els.append(convex(LX, 62, 22))
for y in (-46, -23, 0, 23, 46):
    yy = AX + y
    line(16, yy, LX, yy)
    head(52, yy, 1, 0, AMBER, 8)
    # through the focal point and beyond
    fx = LX + F
    ux, uy = fx - LX, AX - yy
    L = math.hypot(ux, uy)
    ux, uy = ux / L, uy / L
    t = (210 - LX) / ux
    line(LX, yy, LX + t * ux, yy + t * uy)
els.append(f'<circle cx="{LX+F}" cy="{AX}" r="3.5" fill="{TEXT}"/>')
text(LX + F, AX + 22, "F", 13, TEXT, "middle", 700)
line(LX, AX + 74, LX + F, AX + 74, TEXT, 1)
head(LX + F, AX + 74, 1, 0, TEXT, 7); head(LX, AX + 74, -1, 0, TEXT, 7)
text(LX + F / 2, AX + 90, "focal length f", 12, TEXT, "middle")
text(14, 258, "The thick middle delays the center", 11.5, MUTED)
text(14, 272, "of the wave most, so the wavefront", 11.5, MUTED)
text(14, 286, "curves inward toward F", 11.5, MUTED)

els.append(f'<line x1="228" y1="36" x2="228" y2="280" stroke="#d9dee5" stroke-width="1.2"/>')

# ---------------- (b) diverging ----------------
text(242, 22, "(b) Diverging (concave) lens", 13, TEXT, weight=650)
LX2, F2 = 345, 96
axis(238, 446)
els.append(concave(LX2, 62, 26, 8))
for y in (-46, -23, 0, 23, 46):
    yy = AX + y
    line(244, yy, LX2, yy)
    head(280, yy, 1, 0, AMBER, 8)
    vx = LX2 - F2              # virtual focus
    ux, uy = LX2 - vx, yy - AX
    L = math.hypot(ux, uy)
    ux, uy = ux / L, uy / L
    t = (440 - LX2) / ux
    line(LX2, yy, LX2 + t * ux, yy + t * uy)
    if y != 0:
        line(vx, AX, LX2, yy, MUTED, 1, "3 3")
els.append(f'<circle cx="{LX2-F2}" cy="{AX}" r="3.5" fill="{TEXT}"/>')
text(LX2 - F2, AX + 22, "F", 13, TEXT, "middle", 700)
text(242, 258, "The thin middle lets the center run", 11.5, MUTED)
text(242, 272, "ahead; rays spread as if they came", 11.5, MUTED)
text(242, 286, "from F (dashed): a virtual focus", 11.5, MUTED)

els.append(f'<line x1="456" y1="36" x2="456" y2="280" stroke="#d9dee5" stroke-width="1.2"/>')

# ---------------- (c) eye ----------------
text(470, 22, "(c) The eye", 13, TEXT, weight=650)
EC, ER = (585, AX), 66
els.append(f'<circle cx="{EC[0]}" cy="{EC[1]}" r="{ER}" fill="#f7f9fb" stroke="{STROKE}" stroke-width="1.3"/>')
# retina: back arc
a0, a1 = math.radians(-50), math.radians(50)
p0 = (EC[0] + ER * math.cos(a0), EC[1] + ER * math.sin(a0))
p1 = (EC[0] + ER * math.cos(a1), EC[1] + ER * math.sin(a1))
els.append(f'<path d="M{p0[0]:.1f},{p0[1]:.1f} A{ER},{ER} 0 0 1 {p1[0]:.1f},{p1[1]:.1f}" fill="none" stroke="#d1495b" stroke-width="3.2"/>')
# cornea bulge
cx0 = EC[0] - ER
els.append(f'<path d="M{cx0 + 9:.1f},{AX - 34} Q{cx0 - 22:.1f},{AX} {cx0 + 9:.1f},{AX + 34}" fill="{GLASS}" stroke="{STROKE}" stroke-width="1.3"/>')
# crystalline lens
els.append(f'<ellipse cx="{cx0 + 30}" cy="{AX}" rx="10" ry="27" fill="{GLASS}" stroke="{STROKE}" stroke-width="1.3"/>')
# rays from a distant object, focused on the retina
fx, fy = EC[0] + ER, AX
for y in (-24, 0, 24):
    yy = AX + y
    line(470, yy, cx0 - 8, yy)
    head(492, yy, 1, 0, AMBER, 8)
    # bend at cornea toward an intermediate point, then at lens to the retina
    mid = (cx0 + 30, AX + y * 0.62)
    line(cx0 - 8, yy, mid[0], mid[1])
    line(mid[0], mid[1], fx, fy)
els.append(f'<circle cx="{fx}" cy="{fy}" r="3" fill="{TEXT}"/>')
text(cx0 - 14, AX - 46, "cornea", 12, TEXT, "middle", 600)
text(cx0 + 36, AX + 52, "lens", 12, TEXT, "start", 600)
text(EC[0] + ER - 4, AX - ER + 2, "retina", 12, TEXT, "start", 600)
text(470, 258, "Cornea: about 2/3 of the bending", 11.5, MUTED)
text(470, 272, "(fixed). Lens: changes shape to", 11.5, MUTED)
text(470, 286, "focus near or far.", 11.5, MUTED)

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H+6}" width="{W}" height="{H+6}" '
       f'font-family="Inter, sans-serif">\n<rect width="{W}" height="{H+6}" fill="#ffffff"/>\n'
       + "\n".join(els) + "\n</svg>\n")
OUT.write_text(svg)
print("wrote", OUT)
