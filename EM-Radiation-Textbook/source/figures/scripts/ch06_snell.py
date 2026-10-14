"""Figure 6.4 - refraction at an air/glass boundary drawn with wavefronts (crests).
Wavefront spacing shrinks by n inside the glass; the phase is continuous across the boundary,
which forces n1 sin(t1) = n2 sin(t2). Writes figures/ch06-snell.svg."""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "ch06-snell.svg"
AMBER, DARKAMBER, TEXT, MUTED = "#e09f1f", "#a86a12", "#1f2933", "#52606d"
W, H = 680, 360
n1, n2 = 1.00, 1.50
t1 = math.radians(50)
t2 = math.asin(n1 * math.sin(t1) / n2)
YI = 175            # interface
HX = 230            # hit point of the central ray
wbeam = 36          # beam half-width (perpendicular)
lam1 = 30.0
lam2 = lam1 / n2
els = []


def text(x, y, s, size=12, color=TEXT, anchor="start", weight=400):
    els.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{color}" text-anchor="{anchor}" '
               f'font-weight="{weight}">{s}</text>')


def head(x, y, ux, uy, color, size):
    px, py = -uy, ux
    b1 = (x - size * ux + 0.55 * size * px, y - size * uy + 0.55 * size * py)
    b2 = (x - size * ux - 0.55 * size * px, y - size * uy - 0.55 * size * py)
    els.append(f'<polygon points="{x:.1f},{y:.1f} {b1[0]:.1f},{b1[1]:.1f} {b2[0]:.1f},{b2[1]:.1f}" fill="{color}"/>')


# media
els.append(f'<rect x="0" y="{YI}" width="420" height="{H-YI}" fill="#e6ebf1"/>')
els.append(f'<line x1="0" y1="{YI}" x2="420" y2="{YI}" stroke="#52606d" stroke-width="1.5"/>')
text(14, 26, "air: n₁ = 1.00", 13, TEXT, weight=600)
text(14, H - 14, "glass: n₂ = 1.50", 13, TEXT, weight=600)

d1 = (math.sin(t1), math.cos(t1))
p1 = (d1[1], -d1[0])          # perpendicular to d1
d2 = (math.sin(t2), math.cos(t2))
p2 = (d2[1], -d2[0])
# beam edges meet the interface at x = HX +/- wbeam / cos(t1)
half = wbeam / math.cos(t1)
eL, eR = HX - half, HX + half
w2 = half * math.cos(t2)      # beam half-width inside the glass

# beam bands (light fill)
Ltop = 150
tl = (eL - Ltop * d1[0], YI - Ltop * d1[1]); tr = (eR - Ltop * d1[0], YI - Ltop * d1[1])
els.append(f'<polygon points="{tl[0]:.1f},{tl[1]:.1f} {tr[0]:.1f},{tr[1]:.1f} {eR:.1f},{YI} {eL:.1f},{YI}" fill="{AMBER}" opacity="0.13"/>')
Lbot = 175
bl = (eL + Lbot * d2[0], YI + Lbot * d2[1]); br = (eR + Lbot * d2[0], YI + Lbot * d2[1])
els.append(f'<polygon points="{eL:.1f},{YI} {eR:.1f},{YI} {br[0]:.1f},{br[1]:.1f} {bl[0]:.1f},{bl[1]:.1f}" fill="{AMBER}" opacity="0.13"/>')

# wavefronts: crest m sits where (r - H).d = m*lambda in each medium; each crest is drawn as
# its air part (y <= YI) plus its glass part (y >= YI); the two meet on the boundary.
def clip(a, b, keep_above):
    """Clip segment ab to y <= YI (keep_above) or y >= YI."""
    ina = a[1] <= YI if keep_above else a[1] >= YI
    inb = b[1] <= YI if keep_above else b[1] >= YI
    if ina and inb:
        return a, b
    if not ina and not inb:
        return None
    f = (YI - a[1]) / (b[1] - a[1])
    q = (a[0] + f * (b[0] - a[0]), YI)
    return (a, q) if ina else (q, b)


def seg(a, b):
    els.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{DARKAMBER}" stroke-width="1.6"/>')


for m in range(-4, 9):
    c = (HX + m * lam1 * d1[0], YI + m * lam1 * d1[1])
    r_ = clip((c[0] - wbeam * p1[0], c[1] - wbeam * p1[1]), (c[0] + wbeam * p1[0], c[1] + wbeam * p1[1]), True)
    if r_:
        seg(*r_)
    c = (HX + m * lam2 * d2[0], YI + m * lam2 * d2[1])
    r_ = clip((c[0] - w2 * p2[0], c[1] - w2 * p2[1]), (c[0] + w2 * p2[0], c[1] + w2 * p2[1]), False)
    if r_ and max(r_[0][1], r_[1][1]) < H - 30:
        seg(*r_)

# central ray
s0 = (HX - Ltop * d1[0], YI - Ltop * d1[1])
els.append(f'<line x1="{s0[0]:.1f}" y1="{s0[1]:.1f}" x2="{HX}" y2="{YI}" stroke="{AMBER}" stroke-width="2.4"/>')
head(HX - 0.45 * Ltop * d1[0] + 6 * d1[0], YI - 0.45 * Ltop * d1[1] + 6 * d1[1], d1[0], d1[1], AMBER, 11)
e0 = (HX + Lbot * d2[0], YI + Lbot * d2[1])
els.append(f'<line x1="{HX}" y1="{YI}" x2="{e0[0]:.1f}" y2="{e0[1]:.1f}" stroke="{AMBER}" stroke-width="2.4"/>')
head(HX + 0.62 * Lbot * d2[0], YI + 0.62 * Lbot * d2[1], d2[0], d2[1], AMBER, 11)
# weak reflection
r_end = (HX + 120 * d1[0], YI - 120 * d1[1])
els.append(f'<line x1="{HX}" y1="{YI}" x2="{r_end[0]:.1f}" y2="{r_end[1]:.1f}" stroke="{AMBER}" stroke-width="1.2" opacity="0.8"/>')
head(r_end[0], r_end[1], d1[0], -d1[1], AMBER, 8)
text(272, 150, "weak reflection", 11.5, MUTED)
text(272, 164, "(about 4%)", 11.5, MUTED)

# normal + angles
els.append(f'<line x1="{HX}" y1="{YI-130}" x2="{HX}" y2="{YI+150}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="4 4"/>')
r = 44
a1 = (HX - r * math.sin(t1), YI - r * math.cos(t1))
els.append(f'<path d="M{HX},{YI - r} A{r},{r} 0 0 0 {a1[0]:.1f},{a1[1]:.1f}" fill="none" stroke="{TEXT}" stroke-width="1.2"/>')
text(HX - 14, YI - 52, "θ₁", 13, TEXT, "middle", 600)
r = 52
a2 = (HX + r * math.sin(t2), YI + r * math.cos(t2))
els.append(f'<path d="M{HX},{YI + r} A{r},{r} 0 0 0 {a2[0]:.1f},{a2[1]:.1f}" fill="none" stroke="{TEXT}" stroke-width="1.2"/>')
text(HX + 15, YI + 66, "θ₂", 13, TEXT, "middle", 600)
text(HX + 5, YI - 118, "normal", 11, MUTED)

# explanation panel
X = 440
text(X, 60, "n₁ sin θ₁ = n₂ sin θ₂", 18, TEXT, weight=700)
text(X, 84, "here: 1.00 × sin 50° = 1.50 × sin 30.7°", 12, MUTED)
lines = [("Lines across the beam are wave crests.", TEXT, 600),
         ("Inside the glass:", TEXT, 400),
         ("• frequency is unchanged,", TEXT, 400),
         ("• speed drops to c/n,", TEXT, 400),
         ("• so crests bunch up: λ₂ = λ₁ / n.", TEXT, 400),
         ("Crests must stay connected at the", MUTED, 400),
         ("surface, so the wavefront pivots and", MUTED, 400),
         ("the ray bends toward the normal.", MUTED, 400)]
for i, (s, c, wgt) in enumerate(lines):
    text(X, 128 + i * 19 + (8 if i >= 5 else 0), s, 12.5, c, weight=wgt)

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
       f'font-family="Inter, sans-serif">\n<rect width="{W}" height="{H}" fill="#ffffff"/>\n'
       + "\n".join(els) + "\n</svg>\n")
OUT.write_text(svg)
print("wrote", OUT, "theta2 =", round(math.degrees(t2), 2))
