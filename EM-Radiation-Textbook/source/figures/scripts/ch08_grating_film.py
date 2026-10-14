"""Figure 8.4 - (a) a CD as a reflection grating (d = 1.6 um, normal incidence): ray angles from
d sin(theta) = m lambda for 400-700 nm; (b) thin-film interference in a soap film (n = 1.33) and the
computed reflected color vs. film thickness (Airy reflectance, CIE 1931 fit, 6500 K illuminant).
Output: figures/ch08-grating-film.svg"""
from pathlib import Path
import sys
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch08_colorutil import wavelength_rgb, hexcolor, spectrum_to_xyz, xyz_to_srgb

OUT = Path(__file__).resolve().parents[1] / "ch08-grating-film.svg"
INK, MUTED, AMBER, WALLF, WALLS = "#1f2933", "#52606d", "#e09f1f", "#d9dee5", "#52606d"
W, H = 680, 360
el = []
def T(x, y, s, size=12, anchor="start", fill=INK, weight="400", style="normal"):
    s = s.replace("&", "&amp;").replace("<", "&lt;")
    el.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{fill}" '
              f'font-weight="{weight}" font-style="{style}">{s}</text>')
def L(x1, y1, x2, y2, stroke=INK, w=1.2, dash=None, extra=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    el.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{w}"{d} {extra}/>')
el.append('<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
          f'<path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker>'
          '<marker id="ahA" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
          f'<path d="M0,0 L10,5 L0,10 z" fill="{AMBER}"/></marker></defs>')

# ---------- (a) CD grating ----------
T(14, 22, "(a) A CD is a reflection grating", 13, weight="600")
cx, cy = 170, 292
d_nm = 1600.0
for m, R in [(1, 205), (2, 168)]:
    for sgn in (1, -1):
        for lam in np.linspace(400, 700, 41):
            th = np.arcsin(m * lam / d_nm)
            x2, y2 = cx + sgn * R * np.sin(th), cy - R * np.cos(th)
            L(cx, cy, x2, y2, stroke=hexcolor(wavelength_rgb(lam)), w=1.5, extra='stroke-opacity="0.9"')
        th_mid = np.arcsin(m * (700 if m == 1 else 470) / d_nm)
        lab = f"m = {m}" if sgn > 0 else f"m = −{m}"
        lx, ly = cx + sgn * (R + 14) * np.sin(th_mid), cy - (R + 14) * np.cos(th_mid)
        T(lx, ly, lab, 12, "start" if sgn > 0 else "end", INK, "600")
# incoming white light (normal incidence); m = 0 goes straight back
L(cx, 40, cx, cy - 4, stroke="#9aa5b1", w=5)
L(cx, 40, cx, cy - 6, stroke=INK, w=1.2, extra='marker-end="url(#ah)"')
T(cx + 8, 50, "white light in;", 11.5, fill=MUTED)
T(cx + 8, 64, "m = 0 bounces straight back", 11.5, fill=MUTED)
# disc surface with tracks
el.append(f'<rect x="28" y="{cy}" width="284" height="14" fill="{WALLF}" stroke="{WALLS}" stroke-width="1"/>')
for x in range(32, 312, 8):
    el.append(f'<rect x="{x}" y="{cy}" width="4" height="4" fill="{WALLS}"/>')
T(170, cy + 34, "tracks 1.6 µm apart (drawn much larger)", 11.5, "middle", MUTED)
T(170, cy + 50, "violet bends least, red most:  sin θ = mλ/d", 11.5, "middle", INK)

# ---------- (b) soap film ----------
X0 = 360
T(X0, 22, "(b) A soap film: two reflections interfere", 13, weight="600")
ft, fb = 84, 116                     # film top/bottom
el.append(f'<rect x="{X0+10}" y="{ft}" width="300" height="{fb-ft}" fill="#dfeaf3" stroke="{WALLS}" stroke-width="1"/>')
T(X0 + 300, ft + 23, "soap film", 11.5, "end", MUTED)
# rays
A = (X0 + 80, ft)
L(X0 + 22, 40, A[0], A[1], stroke=AMBER, w=2.2, extra='marker-end="url(#ahA)"')
L(A[0], A[1], A[0] + 58, 40, stroke=AMBER, w=2.2, extra='marker-end="url(#ahA)"')
B = (A[0] + 22, fb)
L(A[0], A[1], B[0], B[1], stroke=AMBER, w=1.8)
C = (B[0] + 22, ft)
L(B[0], B[1], C[0], C[1], stroke=AMBER, w=1.8)
L(C[0], C[1], C[0] + 58, 40, stroke=AMBER, w=2.2, extra='marker-end="url(#ahA)"')
T(A[0] + 62, 40, "1", 12, weight="600")
T(C[0] + 62, 40, "2", 12, weight="600")
T(X0 + 10, fb + 20, "Ray 2 travels about 2t farther than ray 1:", 11.5, fill=INK)
T(X0 + 10, fb + 35, "in step = bright color, out of step = dark.", 11.5, fill=INK)
# thickness marker
L(X0 + 22, ft, X0 + 22, fb, stroke=MUTED, w=1, extra='marker-end="url(#ah)"')
T(X0 + 28, fb - 6, "t", 13, fill=INK, style="italic")

# color strip vs thickness
lam = np.linspace(380, 780, 401)
h, c, k = 6.626e-34, 3e8, 1.381e-23
S = 1 / (lam * 1e-9) ** 5 / (np.exp(h * c / (lam * 1e-9 * k * 6500)) - 1); S /= S.max()
n = 1.33; r1 = (1 - n) / (1 + n); r2 = -r1
def refl(t):
    dlt = 4 * np.pi * n * t / lam
    num = r1 + r2 * np.exp(1j * dlt); den = 1 + r1 * r2 * np.exp(1j * dlt)
    return np.abs(num / den) ** 2
Ravg = 2 * r1 ** 2 / (1 + r1 ** 2)
Yref = spectrum_to_xyz(lam, S * Ravg)[1]
sx0, sx1, sy0, sy1 = X0 + 10, X0 + 295, 190, 220
ts = np.linspace(0, 1000, 301)
wcol = (sx1 - sx0) / (len(ts) - 1)
for i, t in enumerate(ts):
    XYZ = spectrum_to_xyz(lam, S * refl(t)) / Yref * 0.42
    col = hexcolor(xyz_to_srgb(XYZ))
    el.append(f'<rect x="{sx0 + i*wcol:.2f}" y="{sy0}" width="{wcol+0.6:.2f}" height="{sy1-sy0}" fill="{col}"/>')
el.append(f'<rect x="{sx0}" y="{sy0}" width="{sx1-sx0}" height="{sy1-sy0}" fill="none" stroke="{WALLS}" stroke-width="0.8"/>')
T(sx0, sy0 - 8, "reflected color vs. film thickness (computed, n = 1.33)", 11.5, fill=MUTED)
for tv in range(0, 1001, 200):
    x = sx0 + (sx1 - sx0) * tv / 1000
    L(x, sy1, x, sy1 + 5, stroke=MUTED, w=0.8)
    T(x, sy1 + 19, str(tv), 11, "middle", MUTED)
T((sx0 + sx1) / 2, sy1 + 36, "film thickness t (nm)", 11.5, "middle", MUTED)
# black-film callout
L(sx0 + 3, sy1 + 44, sx0 + 3, sy1 + 2, stroke=INK, w=0.9, extra='marker-end="url(#ah)"')
T(sx0 + 10, sy1 + 58, "thinner than ~30 nm: the two reflections cancel", 11.5, fill=INK)
T(sx0 + 10, sy1 + 73, "for every color, so the film looks black", 11.5, fill=INK)

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
       f'font-family="Inter, sans-serif">\n<rect width="{W}" height="{H}" fill="white"/>\n' + "\n".join(el) + "\n</svg>\n")
OUT.write_text(svg)
print("wrote", OUT)
