"""Figure 8.7 - (a) an atom in a visible light wave: the field is uniform across it (dipole picture);
(b) antenna size vs. wavelength: a resonant half-wave dipole vs. a short stub.
Radiation resistances: half-wave dipole ~73 ohm; short dipole ~20 pi^2 (L/lambda)^2 = 0.49 ohm at L = lambda/20.
Output: figures/ch08-atom-antenna.svg"""
from pathlib import Path
import numpy as np

OUT = Path(__file__).resolve().parents[1] / "ch08-atom-antenna.svg"
INK, MUTED, AMBER, RED, TEAL, PURPLE, GREEN = "#1f2933", "#52606d", "#e09f1f", "#d1495b", "#12a39a", "#8d5a97", "#0b6e4f"
W, H = 680, 340
el = []
def T(x, y, s, size=12, anchor="start", fill=INK, weight="400", style="normal"):
    s = s.replace("&", "&amp;").replace("<", "&lt;")
    el.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{fill}" '
              f'font-weight="{weight}" font-style="{style}">{s}</text>')
def L(x1, y1, x2, y2, stroke=INK, w=1.2, dash=None, extra=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    el.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{w}"{d} {extra}/>')
el.append('<defs>'
          '<marker id="aR" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto">'
          f'<path d="M0,0 L10,5 L0,10 z" fill="{RED}"/></marker>'
          '<marker id="aM" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
          f'<path d="M0,0 L10,5 L0,10 z" fill="{MUTED}"/></marker></defs>')

# ---------- (a) atom in a light wave ----------
T(14, 22, "(a) An atom inside a 500 nm light wave", 13, weight="600")
x0, lam_px, ay, A = 24, 300, 104, 46
xs = np.linspace(x0, x0 + 1.2 * lam_px, 400)
ys = ay - A * np.sin(2 * np.pi * (xs - x0) / lam_px)
L(x0, ay, x0 + 1.2 * lam_px, ay, stroke="#c4ccd5", w=0.8)
for xa in np.arange(x0 + 12, x0 + 1.2 * lam_px, 24):
    ya = ay - A * np.sin(2 * np.pi * (xa - x0) / lam_px)
    if abs(ya - ay) > 7:
        L(xa, ay, xa, ya, stroke=RED, w=1.4, extra='marker-end="url(#aR)"')
el.append('<polyline points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in zip(xs, ys)) + f'" fill="none" stroke="{RED}" stroke-width="2"/>')
T(x0 + 1.2 * lam_px, ay - A - 6, "electric field E", 11.5, "end", RED)
L(x0, ay + 62, x0 + lam_px, ay + 62, stroke=MUTED, w=1, extra='marker-start="url(#aM)" marker-end="url(#aM)"')
T(x0 + lam_px / 2, ay + 78, "one wavelength = 500 nm  (about 5000 atoms side by side)", 11.5, "middle", MUTED)
# the atom (to scale it would be 0.06 px wide)
axm = x0 + lam_px * 0.25
el.append(f'<circle cx="{axm}" cy="{ay}" r="3.2" fill="{TEAL}" stroke="white" stroke-width="0.8"/>')
L(axm, ay + 4, axm, ay + 56, stroke=MUTED, w=0.8, dash="2 2")
L(axm, ay + 84, axm, 208, stroke=MUTED, w=0.8, dash="2 2")
T(axm - 7, ay + 20, "atom, drawn", 11, "end", INK)
T(axm - 7, ay + 33, "100× too big", 11, "end", INK)
# inset
el.append(f'<rect x="14" y="208" width="380" height="122" rx="8" fill="#f5f7fa" stroke="#c4ccd5" stroke-width="1"/>')
cx_, cy_ = 82, 272
for xa in (34, 130):
    L(xa, 312, xa, 236, stroke=RED, w=2, extra='marker-end="url(#aR)"')
T(130 + 6, 244, "E", 12, "start", RED, "600")
el.append(f'<circle cx="{cx_}" cy="{cy_-7}" r="30" fill="{TEAL}" fill-opacity="0.22" stroke="{TEAL}" stroke-width="1.2"/>')
el.append(f'<circle cx="{cx_}" cy="{cy_+1}" r="4.5" fill="{PURPLE}"/>')
T(cx_, cy_ - 22, "−", 15, "middle", TEAL, "700")
T(cx_ + 11, cy_ + 13, "+", 13, "middle", PURPLE, "700")
T(cx_, 326, "electron cloud pushed up", 10.5, "middle", MUTED)
lines = ["Zoomed in on the atom: the field is",
         "the same across the whole atom (it",
         "varies by only ~0.1%). It pushes the",
         "electron cloud one way, then the other:",
         "an oscillating dipole, the first step",
         "in absorbing (or emitting) light."]
for i, s in enumerate(lines):
    T(158, 232 + i * 15.5, s, 11.5, "start", INK)

# ---------- (b) antennas ----------
X = 418
T(X, 22, "(b) Antennas: length sets efficiency", 13, weight="600")
lam_b = 220
L(X + 16, 58, X + 16 + lam_b, 58, stroke=MUTED, w=1, extra='marker-start="url(#aM)" marker-end="url(#aM)"')
T(X + 16 + lam_b / 2, 50, "one wavelength λ", 11.5, "middle", MUTED)
def dipole(cx, cy, length, strong):
    half = length / 2
    for k, r in enumerate([22, 38, 54]):
        op = (0.85 - 0.22 * k) if strong else (0.22 - 0.06 * k)
        for sgn in (1, -1):
            a0, a1 = np.radians(-50), np.radians(50)
            pts = [(cx + sgn * r * np.cos(t) + sgn * half * 0.0, cy + r * np.sin(t)) for t in np.linspace(a0, a1, 30)]
            el.append('<polyline points="' + " ".join(f"{p:.1f},{q:.1f}" for p, q in pts) +
                      f'" fill="none" stroke="{AMBER}" stroke-width="{2.6 if strong else 1.6}" stroke-opacity="{op:.2f}"/>')
    el.append(f'<rect x="{cx-half:.1f}" y="{cy-2.5}" width="{half-2:.1f}" height="5" fill="#52606d"/>')
    el.append(f'<rect x="{cx+2:.1f}" y="{cy-2.5}" width="{half-2:.1f}" height="5" fill="#52606d"/>')
    el.append(f'<circle cx="{cx}" cy="{cy}" r="2.6" fill="white" stroke="{INK}" stroke-width="1"/>')
cxb = X + 16 + lam_b / 2
dipole(cxb, 116, lam_b / 2, True)
T(cxb, 186, "half-wave dipole (λ/2): resonant,", 11.5, "middle", INK, "600")
T(cxb, 201, "radiation resistance ≈ 73 Ω: radiates well", 11.5, "middle", GREEN)
dipole(cxb, 248, lam_b / 20, False)
T(cxb, 300, "short stub (λ/20): ≈ 0.5 Ω, so most", 11.5, "middle", INK, "600")
T(cxb, 315, "of the drive power just heats the wire", 11.5, "middle", RED)

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
       f'font-family="Inter, sans-serif">\n<rect width="{W}" height="{H}" fill="white"/>\n' + "\n".join(el) + "\n</svg>\n")
OUT.write_text(svg)
print("wrote", OUT, " R_short =", 20 * np.pi ** 2 * (1 / 20) ** 2)
