"""Generate figures/ch01-plane-wave.svg: E and B fields of a linearly polarized plane wave.

Oblique projection: x = direction of travel (right), y = up (E), z = toward the viewer (B).
E x B points along +x, as it must for a wave travelling in +x. E and B are in phase.
Run from source/:  python3 figures/scripts/ch01_plane_wave.py
"""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "ch01-plane-wave.svg"
RED, BLUE, INK, MUTED = "#d1495b", "#2e6fdb", "#1f2933", "#52606d"

W, H = 680, 380
X0, Y0 = 62, 178          # origin on screen
LAM = 250                 # wavelength in px
L = 2.0 * LAM             # length of drawn wave
A = 76                    # amplitude in px (E and B drawn the same size)
ZK, ZANG = 0.66, 40       # oblique depth scale and angle
ZC, ZS = ZK * math.cos(math.radians(ZANG)), ZK * math.sin(math.radians(ZANG))


def P(x, y, z):
    """3D -> screen. +z comes toward the viewer (drawn down-left)."""
    return X0 + x - z * ZC, Y0 - y + z * ZS


def poly(pts):
    return " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)


k = 2 * math.pi / LAM
N = 500
xs = [L * i / N for i in range(N + 1)]
e_curve = [P(x, A * math.sin(k * x), 0) for x in xs]
b_curve = [P(x, 0, A * math.sin(k * x)) for x in xs]

parts = []
add = parts.append
add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Inter, sans-serif">')
add('<rect width="100%" height="100%" fill="#ffffff"/>')
mk = lambda i, c, s=6: (f'<marker id="{i}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="{s}" markerHeight="{s}" '
                        f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>')
add('<defs>' + mk("ah", INK, 7) + mk("ahr", RED) + mk("ahb", BLUE) + mk("ahm", MUTED) + '</defs>')

# faint planes to help the eye read the 3D geometry
pad = 10
q = [P(0, A + pad, 0), P(L, A + pad, 0), P(L, -A - pad, 0), P(0, -A - pad, 0)]
add(f'<polygon points="{poly(q)}" fill="{RED}" fill-opacity="0.04" stroke="{RED}" stroke-opacity="0.2" stroke-width="1"/>')
q = [P(0, 0, -A - pad), P(L, 0, -A - pad), P(L, 0, A + pad), P(0, 0, A + pad)]
add(f'<polygon points="{poly(q)}" fill="{BLUE}" fill-opacity="0.05" stroke="{BLUE}" stroke-opacity="0.22" stroke-width="1"/>')

# field vectors (stems)
for i in range(1, 16 * 2 + 1):
    x = i * LAM / 16
    s = math.sin(k * x)
    if abs(s) < 0.3:
        continue
    x0, y0 = P(x, 0, 0); x1, y1 = P(x, 0, A * s)
    add(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{BLUE}" stroke-width="1.5" stroke-opacity="0.7" marker-end="url(#ahb)"/>')
for i in range(1, 16 * 2 + 1):
    x = i * LAM / 16
    s = math.sin(k * x)
    if abs(s) < 0.3:
        continue
    x0, y0 = P(x, 0, 0); x1, y1 = P(x, A * s, 0)
    add(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{RED}" stroke-width="1.5" stroke-opacity="0.7" marker-end="url(#ahr)"/>')

add(f'<polyline points="{poly(b_curve)}" fill="none" stroke="{BLUE}" stroke-width="2.6" stroke-linejoin="round"/>')
add(f'<polyline points="{poly(e_curve)}" fill="none" stroke="{RED}" stroke-width="2.6" stroke-linejoin="round"/>')

# propagation axis
ax0, ay0 = P(-12, 0, 0)
ax1, ay1 = P(L + 95, 0, 0)
add(f'<line x1="{ax0:.1f}" y1="{ay0:.1f}" x2="{ax1:.1f}" y2="{ay1:.1f}" stroke="{INK}" stroke-width="2" marker-end="url(#ah)"/>')
add(f'<text x="{ax1 + 2:.1f}" y="{ay1 + 26:.1f}" font-size="13" fill="{INK}" text-anchor="end" font-weight="600">direction</text>')
add(f'<text x="{ax1 + 2:.1f}" y="{ay1 + 42:.1f}" font-size="13" fill="{INK}" text-anchor="end" font-weight="600">of travel</text>')
add(f'<text x="{ax1 + 2:.1f}" y="{ay1 + 58:.1f}" font-size="12" fill="{MUTED}" text-anchor="end">speed c</text>')

# wavelength bracket between E crests at x = LAM/4 and 5LAM/4
c1 = P(LAM / 4, A, 0); c2 = P(5 * LAM / 4, A, 0)
yb = c1[1] - 24
add(f'<line x1="{c1[0]:.1f}" y1="{yb:.1f}" x2="{c2[0]:.1f}" y2="{yb:.1f}" stroke="{MUTED}" stroke-width="1.3" marker-start="url(#ahm)" marker-end="url(#ahm)"/>')
for c in (c1, c2):
    add(f'<line x1="{c[0]:.1f}" y1="{yb - 6:.1f}" x2="{c[0]:.1f}" y2="{c[1] - 5:.1f}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="3 3"/>')
add(f'<rect x="{(c1[0] + c2[0]) / 2 - 62:.1f}" y="{yb - 21:.1f}" width="124" height="18" fill="#ffffff"/>')
add(f'<text x="{(c1[0] + c2[0]) / 2:.1f}" y="{yb - 7:.1f}" font-size="14" fill="{INK}" text-anchor="middle" font-style="italic">one wavelength λ</text>')

# field labels
ex, ey = P(5 * LAM / 4, A, 0)
add(f'<text x="{ex + 24:.1f}" y="{ey + 4:.1f}" font-size="14" fill="{RED}" font-weight="700">E</text>')
add(f'<text x="{ex + 38:.1f}" y="{ey + 4:.1f}" font-size="12.5" fill="{INK}">electric field</text>')
add(f'<text x="{ex + 24:.1f}" y="{ey + 20:.1f}" font-size="11.5" fill="{MUTED}">oscillates up and down</text>')
bx, by = 34, Y0 + A + 2
add(f'<text x="{bx:.1f}" y="{by:.1f}" font-size="14" fill="{BLUE}" font-weight="700">B</text>')
add(f'<text x="{bx + 14:.1f}" y="{by:.1f}" font-size="12.5" fill="{INK}">magnetic field</text>')
add(f'<text x="{bx:.1f}" y="{by + 16:.1f}" font-size="11.5" fill="{MUTED}">oscillates toward and away from you</text>')

# axis triad (bottom-left)
tx, ty = 622, 338
def tri(dx, dy, col, mid, lab, lx, ly):
    add(f'<line x1="{tx}" y1="{ty}" x2="{tx + dx:.1f}" y2="{ty + dy:.1f}" stroke="{col}" stroke-width="2" marker-end="url(#{mid})"/>')
    add(f'<text x="{tx + dx + lx:.1f}" y="{ty + dy + ly:.1f}" font-size="12.5" fill="{col}" font-weight="700">{lab}</text>')
tri(0, -34, RED, "ahr", "E", -4, -6)
tri(-34 * math.cos(math.radians(ZANG)), 34 * math.sin(math.radians(ZANG)), BLUE, "ahb", "B", -14, 8)
tri(38, 0, INK, "ah", "v", 6, 4)
add(f'<text x="{tx - 44}" y="{ty - 18}" font-size="11.5" fill="{MUTED}" text-anchor="end">E, B and the direction</text>')
add(f'<text x="{tx - 44}" y="{ty - 3}" font-size="11.5" fill="{MUTED}" text-anchor="end">of travel v are all</text>')
add(f'<text x="{tx - 44}" y="{ty + 12}" font-size="11.5" fill="{MUTED}" text-anchor="end">perpendicular to each other</text>')

add('</svg>')
OUT.write_text("\n".join(parts))
print("wrote", OUT)
