"""Figure 7.7 - structural color from a thin film. Left: the two reflections (front surface and back
surface) that interfere. Right: COMPUTED reflected color of a soap film (n = 1.33) in air vs
thickness, under a 6500 K illuminant, from the standard two-surface (Airy) reflectance
R = 2r^2(1 - cos d) / (1 + r^4 - 2r^2 cos d), d = 4 pi n t / lambda, at normal incidence.
Brightness is scaled up (real films reflect at most ~8%). Writes figures/ch07-thin-film.svg."""
import math
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch07_colorlib import LAM, linear_rgb, to_hex  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "ch07-thin-film.svg"
AMBER, TEXT, MUTED, STROKE = "#e09f1f", "#1f2933", "#52606d", "#52606d"
W, H = 680, 270
els = []


def text(x, y, s, size=12, color=TEXT, anchor="start", weight=400):
    els.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{color}" text-anchor="{anchor}" '
               f'font-weight="{weight}">{s}</text>')


def head(x, y, ux, uy, color, size):
    px, py = -uy, ux
    b1 = (x - size * ux + 0.55 * size * px, y - size * uy + 0.55 * size * py)
    b2 = (x - size * ux - 0.55 * size * px, y - size * uy - 0.55 * size * py)
    els.append(f'<polygon points="{x:.1f},{y:.1f} {b1[0]:.1f},{b1[1]:.1f} {b2[0]:.1f},{b2[1]:.1f}" fill="{color}"/>')


def ray(pts, w=2.0, color=AMBER, op=1.0):
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    els.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" opacity="{op}" stroke-linejoin="round"/>')
    (xa, ya), (xb, yb) = pts[-2], pts[-1]
    L = math.hypot(xb - xa, yb - ya)
    head(xb + 3 * (xb - xa) / L, yb + 3 * (yb - ya) / L, (xb - xa) / L, (yb - ya) / L, color, 9)


# ---------------- left: ray diagram ----------------
text(16, 22, "(a) Two reflections from one thin film", 13.5, TEXT, weight=650)
FT, FB = 140, 176
els.append(f'<rect x="16" y="{FT}" width="300" height="{FB-FT}" fill="#dcebf7" stroke="{STROKE}" stroke-width="1.1"/>')
text(22, FT + 22, "soap film, n ≈ 1.33", 11.5, MUTED)
th = math.radians(35)
th2 = math.asin(math.sin(th) / 1.33)
A = (128.0, FT)
S = (A[0] - 100 * math.sin(th), FT - 100 * math.cos(th))
ray([S, A], 2.2)
R1 = (A[0] + 92 * math.sin(th), FT - 92 * math.cos(th))
ray([A, R1], 2.0)
B = (A[0] + (FB - FT) * math.tan(th2), FB)
C = (B[0] + (FB - FT) * math.tan(th2), FT)
els.append(f'<polyline points="{A[0]:.1f},{A[1]} {B[0]:.1f},{B[1]} {C[0]:.1f},{C[1]}" fill="none" stroke="{AMBER}" stroke-width="1.8"/>')
R2 = (C[0] + 92 * math.sin(th), FT - 92 * math.cos(th))
ray([C, R2], 2.0)
text(R1[0] - 4, R1[1] - 8, "1", 13, TEXT, "middle", 700)
text(R2[0] + 6, R2[1] - 8, "2", 13, TEXT, "middle", 700)
# thickness marker
tx = 296
els.append(f'<line x1="{tx}" y1="{FT}" x2="{tx}" y2="{FB}" stroke="{TEXT}" stroke-width="1"/>')
head(tx, FT, 0, -1, TEXT, 6); head(tx, FB, 0, 1, TEXT, 6)
text(tx - 6, (FT + FB) / 2 + 4, "t", 13, TEXT, "end", 700)
lines = [("Ray 1 reflects off the front surface (its phase flips).", TEXT),
         ("Ray 2 makes an extra round trip of about 2nt.", TEXT),
         ("Colors whose crests line up are reinforced;", MUTED),
         ("the others cancel. Change t and the color changes.", MUTED)]
for i, (s, c) in enumerate(lines):
    text(16, 204 + i * 16, s, 11.5, c)

els.append(f'<line x1="340" y1="36" x2="340" y2="262" stroke="#d9dee5" stroke-width="1.2"/>')

# ---------------- right: computed color strip ----------------
text(356, 22, "(b) Reflected color vs. film thickness", 13.5, TEXT, weight=650)
text(356, 40, "computed for a soap film in white light", 11.5, MUTED)
n = 1.33
r = (1 - n) / (1 + n)
SX0, SX1, SY0, SY1 = 360, 664, 62, 132
TMAX = 1000.0
cols = []
tvals = np.linspace(0, TMAX, 305)
for t in tvals:
    d = 4 * np.pi * n * t / LAM
    R = 2 * r * r * (1 - np.cos(d)) / (1 + r ** 4 - 2 * r * r * np.cos(d))
    cols.append(linear_rgb(R))
peak = max(max(c) for c in cols)
exposure = 0.95 / peak
for k, t in enumerate(tvals[:-1]):
    x0 = SX0 + (SX1 - SX0) * t / TMAX
    x1 = SX0 + (SX1 - SX0) * tvals[k + 1] / TMAX
    els.append(f'<rect x="{x0:.2f}" y="{SY0}" width="{x1 - x0 + 0.4:.2f}" height="{SY1-SY0}" fill="{to_hex(cols[k], exposure)}"/>')
els.append(f'<rect x="{SX0}" y="{SY0}" width="{SX1-SX0}" height="{SY1-SY0}" fill="none" stroke="{STROKE}" stroke-width="1"/>')
for t in range(0, 1001, 200):
    x = SX0 + (SX1 - SX0) * t / TMAX
    els.append(f'<line x1="{x:.1f}" y1="{SY1}" x2="{x:.1f}" y2="{SY1 + 5}" stroke="{TEXT}" stroke-width="1"/>')
    text(x, SY1 + 18, f"{t}", 11, MUTED, "middle")
text(SX1, SY1 + 34, "film thickness t (nm)", 11.5, MUTED, "end")
# callouts
text(SX0, SY1 + 56, "Left end, thinner than about 30 nm: the two", 11.5, TEXT)
text(SX0, SY1 + 71, "reflections cancel for every color, so", 11.5, TEXT)
text(SX0, SY1 + 86, "the film looks black (about to pop).", 11.5, TEXT)
text(SX0, SY1 + 108, "Thicker films: bands of color that repeat and fade.", 11.5, MUTED)
text(SX0, SY1 + 123, "Oil slicks and soap bubbles work this way.", 11.5, MUTED)

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
       f'font-family="Inter, sans-serif">\n<rect width="{W}" height="{H}" fill="#ffffff"/>\n'
       + "\n".join(els) + "\n</svg>\n")
OUT.write_text(svg)
print("wrote", OUT, "exposure", round(exposure, 2))
