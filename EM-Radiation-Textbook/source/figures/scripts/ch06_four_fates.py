"""Figure 6.1 - the four fates of light hitting a slab (reflected, absorbed, transmitted, scattered).
Writes figures/ch06-four-fates.svg. Hand-built SVG; geometry from Snell's law with n = 1.5."""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "ch06-four-fates.svg"
AMBER, TEXT, MUTED, FILL, STROKE, HEAT = "#e09f1f", "#1f2933", "#52606d", "#d9dee5", "#52606d", "#c2410c"
W, H = 680, 340
els = []


def line(x1, y1, x2, y2, color, w, op=1.0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    els.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" '
               f'stroke-width="{w}" stroke-linecap="round" opacity="{op}"{d}/>')


def head(x, y, ux, uy, color, size):
    """Arrowhead with tip at (x, y) pointing along unit vector (ux, uy)."""
    px, py = -uy, ux
    b1 = (x - size * ux + 0.55 * size * px, y - size * uy + 0.55 * size * py)
    b2 = (x - size * ux - 0.55 * size * px, y - size * uy - 0.55 * size * py)
    els.append(f'<polygon points="{x:.1f},{y:.1f} {b1[0]:.1f},{b1[1]:.1f} {b2[0]:.1f},{b2[1]:.1f}" fill="{color}"/>')


def arrow(x1, y1, x2, y2, color, w, size=None, op=1.0, mid=False):
    L = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    size = size or max(9, 2.6 * w)
    if mid:
        line(x1, y1, x2, y2, color, w, op)
        mx, my = (x1 + x2) / 2 + ux * size / 2, (y1 + y2) / 2 + uy * size / 2
        head(mx, my, ux, uy, color, size)
    else:
        line(x1, y1, x2 - ux * size * 0.6, y2 - uy * size * 0.6, color, w, op)
        head(x2, y2, ux, uy, color, size)


def text(x, y, s, size=12, color=TEXT, anchor="start", weight=400, italic=False):
    st = ' font-style="italic"' if italic else ""
    els.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" '
               f'font-weight="{weight}"{st}>{s}</text>')


# slab
X0, X1, YT, YB = 40, 455, 150, 235
els.append(f'<rect x="{X0}" y="{YT}" width="{X1-X0}" height="{YB-YT}" fill="{FILL}" stroke="{STROKE}" stroke-width="1.2"/>')
text(X0 + 8, YB - 9, "material slab (n ≈ 1.5)", 11, MUTED)

th1 = math.radians(40)
th2 = math.asin(math.sin(th1) / 1.5)
Hx, Hy = 200, YT
d1 = (math.sin(th1), math.cos(th1))
S = (Hx - 150 * d1[0], Hy - 150 * d1[1])
# normal
line(Hx, YT - 80, Hx, YT, MUTED, 1, 0.8, "4 4")
# incident (thick = 100 %)
arrow(S[0], S[1], Hx, Hy, AMBER, 9, 22, mid=True)
# reflected
R_end = (Hx + 150 * d1[0], Hy - 150 * d1[1])
arrow(Hx, Hy, R_end[0], R_end[1], AMBER, 3.2, 13)
# inside beam, getting thinner (absorption)
d2 = (math.sin(th2), math.cos(th2))
tE = (YB - YT) / d2[1]
E = (Hx + tE * d2[0], YB)
pts = []
for k in range(0, 11):
    f = k / 10
    pts.append((Hx + f * tE * d2[0], Hy + f * tE * d2[1], 7.5 - 2.5 * f))
# draw as a tapered polygon
px, py = d2[1], -d2[0]
left = [(x + px * w / 2, y + py * w / 2) for x, y, w in pts]
right = [(x - px * w / 2, y - py * w / 2) for x, y, w in pts][::-1]
poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in left + right)
els.append(f'<polygon points="{poly}" fill="{AMBER}" opacity="0.9"/>')
# transmitted
T_end = (E[0] + 120 * d1[0], E[1] + 120 * d1[1])
arrow(E[0], E[1], T_end[0], T_end[1], AMBER, 5, 15)

# heat squiggles beside the inside path
def squiggle(cx, cy, n=3, amp=3.2, wl=7, length=26):
    for j in range(n):
        x0 = cx + j * 9
        d = f"M{x0:.1f},{cy:.1f} "
        steps = 12
        for s in range(1, steps + 1):
            yy = cy - s * length / steps
            xx = x0 + amp * math.sin(2 * math.pi * s * (length / steps) / wl)
            d += f"L{xx:.1f},{yy:.1f} "
        els.append(f'<path d="{d}" fill="none" stroke="{HEAT}" stroke-width="1.6" stroke-linecap="round"/>')

squiggle(250, 212)
text(285, 188, "absorbed (A):", 12, TEXT, weight=600)
text(285, 203, "energy becomes heat (or", 12)
text(285, 218, "chemistry, or a later glow)", 12)

# scattering from a point inside the slab
P = (Hx + 0.45 * tE * d2[0], Hy + 0.45 * tE * d2[1])
for ang in (-150, -112, -35, 160, 128, 55):
    a = math.radians(ang)
    arrow(P[0], P[1], P[0] + 40 * math.cos(a), P[1] + 40 * math.sin(a), AMBER, 1.6, 8, 0.95)
els.append(f'<circle cx="{P[0]:.1f}" cy="{P[1]:.1f}" r="4" fill="#ffffff" stroke="{STROKE}" stroke-width="1.2"/>')
text(40, 258, "scattered: sent off in many", 12, TEXT, weight=600)
text(40, 273, "directions by a pore, grain", 12, MUTED)
text(40, 288, "boundary, or particle", 12, MUTED)
text(40, 303, "(counted in R or T)", 12, MUTED)

# labels for the rays
text(150, 105, "incident light", 12, TEXT, "end", 600)
text(160, 120, "(100% of the energy)", 12, MUTED, "end")
text(R_end[0] + 8, R_end[1] + 12, "reflected (R)", 12, TEXT, weight=600)
text(T_end[0] + 10, T_end[1] - 4, "transmitted (T)", 12, TEXT, weight=600)
text(Hx + 6, YT - 68, "normal", 11, MUTED)

# equation box
bx, by, bw, bh = 488, 112, 178, 150
els.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="8" fill="#f5f7fa" stroke="#c4ccd5"/>')
text(bx + bw / 2, by + 34, "R + A + T = 1", 21, TEXT, "middle", 700)
for i, s in enumerate(["R = fraction reflected", "A = fraction absorbed", "T = fraction transmitted",
                       "Arrow thickness = energy"]):
    text(bx + 14, by + 64 + i * 19, s, 12, MUTED if i == 3 else TEXT)

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
       f'font-family="Inter, sans-serif">\n<rect width="{W}" height="{H}" fill="#ffffff"/>\n'
       + "\n".join(els) + "\n</svg>\n")
OUT.write_text(svg)
print("wrote", OUT)
