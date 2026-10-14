"""Figure 8.3 - double-slit geometry (path difference d sin(theta)) and the resulting fringe
pattern. Writes a hand-structured SVG; the fringe strip and intensity curve are computed from
I = cos^2(pi d sin(theta)/lambda) * sinc^2(pi a sin(theta)/lambda).
Output: figures/ch08-double-slit.svg"""
from pathlib import Path
import numpy as np

OUT = Path(__file__).resolve().parents[1] / "ch08-double-slit.svg"
INK, MUTED, AMBER, GREEN, WALLF, WALLS = "#1f2933", "#52606d", "#e09f1f", "#0b6e4f", "#d9dee5", "#52606d"
LASER = "#e3262b"   # ~650 nm red
W, H = 680, 340
cy = 170            # optical axis
xb, xs = 150, 430   # barrier, screen
half_d = 28
s1, s2 = (xb, cy - half_d), (xb, cy + half_d)
fringe = 34.0       # px between bright fringes on the screen
P = (xs, cy - 2 * fringe)   # m = 2 bright fringe
el = []
def T(x, y, s, size=12, anchor="start", fill=INK, weight="400", style="normal"):
    s = s.replace("&", "&amp;").replace("<", "&lt;")
    el.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{fill}" '
              f'font-weight="{weight}" font-style="{style}">{s}</text>')
def L(x1, y1, x2, y2, stroke=INK, w=1.2, dash=None, extra=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    el.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{w}"{d} {extra}/>')

el.append('<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
          f'<path d="M0,0 L10,5 L0,10 z" fill="{MUTED}"/></marker>'
          '<marker id="ahA" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
          f'<path d="M0,0 L10,5 L0,10 z" fill="{AMBER}"/></marker></defs>')
# incoming plane wavefronts
for x in range(40, 140, 14):
    L(x, cy - 70, x, cy + 70, stroke=AMBER, w=2)
L(36, cy + 92, 132, cy + 92, stroke=MUTED, w=1.2, extra='marker-end="url(#ah)"')
T(36, cy + 110, "laser light,", 12, fill=MUTED)
T(36, cy + 125, "wavelength λ", 12, fill=MUTED)
# barrier with two slits
gap = 5
for y0, y1 in [(30, s1[1] - gap), (s1[1] + gap, s2[1] - gap), (s2[1] + gap, 310)]:
    el.append(f'<rect x="{xb-4}" y="{y0}" width="8" height="{y1-y0}" fill="{WALLF}" stroke="{WALLS}" stroke-width="1"/>')
# screen
el.append(f'<rect x="{xs}" y="30" width="5" height="280" fill="{WALLF}" stroke="{WALLS}" stroke-width="1"/>')
T(xs + 2.5, 326, "screen", 12, "middle", MUTED)
# axis and rays
L(xb, cy, xs, cy, stroke=MUTED, w=0.9, dash="4 3")
for s in (s1, s2):
    L(s[0], s[1], P[0], P[1], stroke=AMBER, w=2.2)
el.append(f'<circle cx="{P[0]}" cy="{P[1]}" r="4" fill="{LASER}" stroke="white" stroke-width="1"/>')
T(P[0] - 8, P[1] - 8, "P", 12, "end", INK, "600")
# theta arc at midpoint
mid = (xb, cy)
ang = np.arctan2(cy - P[1], P[0] - xb)
r = 70
ax_, ay_ = mid[0] + r * np.cos(ang), mid[1] - r * np.sin(ang)
el.append(f'<path d="M {mid[0]+r} {cy} A {r} {r} 0 0 0 {ax_:.1f} {ay_:.1f}" fill="none" stroke="{INK}" stroke-width="1"/>')
L(mid[0], mid[1], mid[0] + 1.25 * r * np.cos(ang), mid[1] - 1.25 * r * np.sin(ang), stroke=INK, w=0.8, dash="2 2")
T(mid[0] + r + 6, cy - 6, "θ", 13, "start", INK, style="italic")
# path difference: foot of perpendicular from S1 onto ray S2->P
v = np.array(P, float) - np.array(s2, float); v /= np.linalg.norm(v)
foot = np.array(s2, float) + np.dot(np.array(s1, float) - np.array(s2, float), v) * v
L(s1[0], s1[1], foot[0], foot[1], stroke=INK, w=0.8, dash="2 2")
L(s2[0], s2[1], foot[0], foot[1], stroke=GREEN, w=4)
T(foot[0] + 10, foot[1] + 30, "extra path", 12, "start", GREEN, "600")
T(foot[0] + 10, foot[1] + 45, "Δ = d sin θ", 12, "start", GREEN, "600")
# d bracket
L(xb - 16, s1[1], xb - 16, s2[1], stroke=MUTED, w=1, extra='marker-start="url(#ah)" marker-end="url(#ah)"')
T(xb - 22, cy + 4, "d", 13, "end", INK, style="italic")
# L dimension
L(xb, 296, xs, 296, stroke=MUTED, w=1, extra='marker-start="url(#ah)" marker-end="url(#ah)"')
T((xb + xs) / 2, 290, "L", 13, "middle", INK, style="italic")
# y on screen
L(xs - 10, cy, xs - 10, P[1] + 3, stroke=MUTED, w=1, extra='marker-end="url(#ah)"')
T(xs - 15, (cy + P[1]) / 2 + 4, "y", 13, "end", INK, style="italic")

# ---- fringe strip + intensity curve ----
x0s, x1s = 452, 478
ys = np.arange(30, 310, 1.0)
yy = (cy - ys) / fringe                    # in units of fringe spacing ~ d sin(theta)/lambda = m
env_zero = 5.0                             # single-slit envelope first zero at m = 5 (a = d/5)
I = np.cos(np.pi * yy) ** 2 * np.sinc(yy / env_zero) ** 2
for y, i in zip(ys, I):
    el.append(f'<rect x="{x0s}" y="{y:.0f}" width="{x1s-x0s}" height="1.05" fill="{LASER}" fill-opacity="{i:.3f}"/>')
el.append(f'<rect x="{x0s}" y="30" width="{x1s-x0s}" height="280" fill="none" stroke="{WALLS}" stroke-width="0.8"/>')
el.insert(1, f'<rect x="{x0s}" y="30" width="{x1s-x0s}" height="280" fill="#111111"/>')
T((x0s + x1s) / 2, 24, "what you see", 12, "middle", MUTED)
# intensity curve
gx0, gx1 = 500, 590
pts = " ".join(f"{gx0 + (gx1-gx0)*i:.1f},{y:.1f}" for y, i in zip(ys, I))
L(gx0, 30, gx0, 310, stroke="#9aa5b1", w=0.8)
el.append(f'<polyline points="{pts}" fill="none" stroke="{LASER}" stroke-width="1.8"/>')
T((gx0 + gx1) / 2 + 6, 24, "brightness", 12, "middle", MUTED)
for m in range(-3, 4):
    y = cy - m * fringe
    lab = f"m = {m}" if m >= 0 else f"m = −{-m}"
    T(gx1 + 34, y + 4, lab, 11.5, "start", INK if m != 2 else LASER, "600" if m in (0, 2) else "400")
    L(gx1 + 4, y, gx1 + 30, y, stroke="#c4ccd5", w=0.8)
T(gx1 + 34, cy - 2.5 * fringe + 4, "dark", 11, "start", MUTED, style="italic")
T(gx1 + 34, cy - 1.5 * fringe + 4, "dark", 11, "start", MUTED, style="italic")

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
       f'font-family="Inter, sans-serif">\n<rect width="{W}" height="{H}" fill="white"/>\n' + "\n".join(el) + "\n</svg>\n")
OUT.write_text(svg)
print("wrote", OUT)
