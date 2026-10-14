"""Generate figures/ch01-plane-wave.svg: E and B fields of a linearly polarized plane wave.

Oblique projection: x = direction of travel (right), y = up (E), z = toward the viewer (B).
E x B points along +x, as it must for a wave travelling in +x.
Run from source/:  python3 figures/scripts/ch01_plane_wave.py
"""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "ch01-plane-wave.svg"
RED, BLUE, INK, MUTED, AMBER = "#d1495b", "#2e6fdb", "#1f2933", "#52606d", "#e09f1f"

W, H = 680, 360
X0, Y0 = 70, 185          # origin on screen
LAM = 200                 # wavelength in px
L = 2.5 * LAM             # length of drawn wave
A = 82                    # amplitude in px (E and B drawn the same size)
ZC, ZS = 0.62 * math.cos(math.radians(32)), 0.62 * math.sin(math.radians(32))


def P(x, y, z):
    """3D -> screen. +z comes toward the viewer (drawn down-left)."""
    return X0 + x - z * ZC, Y0 - y + z * ZS


def poly(pts):
    return " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)


k = 2 * math.pi / LAM
N = 400
xs = [L * i / N for i in range(N + 1)]
e_curve = [P(x, A * math.sin(k * x), 0) for x in xs]
b_curve = [P(x, 0, A * math.sin(k * x)) for x in xs]

parts = []
add = parts.append
add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Inter, sans-serif">')
add('<rect width="100%" height="100%" fill="#ffffff"/>')
add('<defs>'
    f'<marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker>'
    f'<marker id="ahr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{RED}"/></marker>'
    f'<marker id="ahb" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{BLUE}"/></marker>'
    f'<marker id="ahm" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{MUTED}"/></marker>'
    '</defs>')

# faint planes to help the eye read the 3D geometry
ex0, ey0 = P(0, A + 10, 0); ex1, ey1 = P(L, A + 10, 0)
ex2, ey2 = P(L, -A - 10, 0); ex3, ey3 = P(0, -A - 10, 0)
add(f'<polygon points="{poly([(ex0,ey0),(ex1,ey1),(ex2,ey2),(ex3,ey3)])}" fill="{RED}" fill-opacity="0.045" stroke="{RED}" stroke-opacity="0.18" stroke-width="1"/>')
bz = A + 10
q = [P(0, 0, -bz), P(L, 0, -bz), P(L, 0, bz), P(0, 0, bz)]
add(f'<polygon points="{poly(q)}" fill="{BLUE}" fill-opacity="0.045" stroke="{BLUE}" stroke-opacity="0.18" stroke-width="1"/>')

# stems (field vectors) at regular spacing
step = LAM / 12
nst = int(L / step)
for i in range(1, nst + 1):
    x = i * step
    s = math.sin(k * x)
    if abs(s) < 0.08:
        continue
    bx0, by0 = P(x, 0, 0)
    bx1, by1 = P(x, 0, A * s)
    add(f'<line x1="{bx0:.1f}" y1="{by0:.1f}" x2="{bx1:.1f}" y2="{by1:.1f}" stroke="{BLUE}" stroke-width="1.6" stroke-opacity="0.75" marker-end="url(#ahb)"/>')
for i in range(1, nst + 1):
    x = i * step
    s = math.sin(k * x)
    if abs(s) < 0.08:
        continue
    ax0, ay0 = P(x, 0, 0)
    ax1, ay1 = P(x, A * s, 0)
    add(f'<line x1="{ax0:.1f}" y1="{ay0:.1f}" x2="{ax1:.1f}" y2="{ay1:.1f}" stroke="{RED}" stroke-width="1.6" stroke-opacity="0.75" marker-end="url(#ahr)"/>')

add(f'<polyline points="{poly(b_curve)}" fill="none" stroke="{BLUE}" stroke-width="2.6" stroke-linejoin="round"/>')
add(f'<polyline points="{poly(e_curve)}" fill="none" stroke="{RED}" stroke-width="2.6" stroke-linejoin="round"/>')

# propagation axis
ax0, ay0 = P(-15, 0, 0)
ax1, ay1 = P(L + 70, 0, 0)
add(f'<line x1="{ax0:.1f}" y1="{ay0:.1f}" x2="{ax1:.1f}" y2="{ay1:.1f}" stroke="{INK}" stroke-width="2" marker-end="url(#ah)"/>')
add(f'<text x="{ax1 - 2:.1f}" y="{ay1 + 22:.1f}" font-size="13" fill="{INK}" text-anchor="end" font-weight="600">direction of travel</text>')
add(f'<text x="{ax1 - 2:.1f}" y="{ay1 + 38:.1f}" font-size="12" fill="{MUTED}" text-anchor="end">speed c = 3.00 × 10⁸ m/s</text>')

# wavelength bracket between E crests at x = LAM/4 and 5LAM/4
c1 = P(LAM / 4, A, 0); c2 = P(5 * LAM / 4, A, 0)
yb = c1[1] - 22
add(f'<line x1="{c1[0]:.1f}" y1="{yb:.1f}" x2="{c2[0]:.1f}" y2="{yb:.1f}" stroke="{MUTED}" stroke-width="1.3" marker-start="url(#ahm)" marker-end="url(#ahm)"/>')
for c in (c1, c2):
    add(f'<line x1="{c[0]:.1f}" y1="{yb - 6:.1f}" x2="{c[0]:.1f}" y2="{c[1] - 4:.1f}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="3 3"/>')
add(f'<text x="{(c1[0] + c2[0]) / 2:.1f}" y="{yb - 7:.1f}" font-size="14" fill="{INK}" text-anchor="middle" font-style="italic">wavelength λ</text>')

# labels for the fields
ex, ey = P(9 * LAM / 4, A, 0)
add(f'<text x="{ex + 14:.1f}" y="{ey - 4:.1f}" font-size="14" fill="{RED}" font-weight="700">E</text>')
add(f'<text x="{ex + 28:.1f}" y="{ey - 4:.1f}" font-size="12.5" fill="{INK}">electric field</text>')
add(f'<text x="{ex + 14:.1f}" y="{ey + 12:.1f}" font-size="11.5" fill="{MUTED}">(points up/down)</text>')
bxl, byl = P(7 * LAM / 4, 0, -A)  # B trough (pointing away from viewer -> drawn up-right)
bxl, byl = P(5 * LAM / 4 + 8, 0, A)
add(f'<text x="{bxl - 92:.1f}" y="{byl + 22:.1f}" font-size="14" fill="{BLUE}" font-weight="700">B</text>')
add(f'<text x="{bxl - 78:.1f}" y="{byl + 22:.1f}" font-size="12.5" fill="{INK}">magnetic field</text>')
add(f'<text x="{bxl - 92:.1f}" y="{byl + 38:.1f}" font-size="11.5" fill="{MUTED}">(points toward/away from you)</text>')

# small axis triad (bottom-left)
tx, ty = 600, 300
def tri(dx, dy, col, lab, lx, ly):
    add(f'<line x1="{tx}" y1="{ty}" x2="{tx + dx:.1f}" y2="{ty + dy:.1f}" stroke="{col}" stroke-width="2" marker-end="url(#{ {RED:"ahr", BLUE:"ahb", INK:"ah"}[col] })"/>')
    add(f'<text x="{tx + dx + lx:.1f}" y="{ty + dy + ly:.1f}" font-size="12.5" fill="{col}" font-weight="700">{lab}</text>')
tri(0, -36, RED, "E", -4, -6)
tri(-36 * ZC / 0.62, 36 * ZS / 0.62, BLUE, "B", -12, 12)
tri(40, 0, INK, "v", 6, 4)
add(f'<text x="{tx - 6}" y="{ty + 46}" font-size="11" fill="{MUTED}" text-anchor="middle">all three mutually ⟂</text>')

add('</svg>')
OUT.write_text("\n".join(parts))
print("wrote", OUT)
