"""Figure 5.3: hydrogen transitions (Lyman, Balmer, Paschen) and the visible Balmer emission lines.

Levels E_n = -13.6 eV / n^2. Wavelengths from lambda = 1240 eV nm / dE; measured Balmer air wavelengths:
H-alpha 656.3, H-beta 486.1, H-gamma 434.0, H-delta 410.2 nm.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "ch05-hydrogen-spectrum.svg"
W, H = 680, 444
TEXT, MUTED, GRID = "#1f2933", "#52606d", "#d9dee5"
UV, IR = "#6a4cff", "#9b2226"


def wl_rgb(w):
    """Approximate display color of a wavelength (nm), after D. Bruton's algorithm."""
    if 380 <= w < 440: r, g, b = -(w - 440) / 60, 0.0, 1.0
    elif 440 <= w < 490: r, g, b = 0.0, (w - 440) / 50, 1.0
    elif 490 <= w < 510: r, g, b = 0.0, 1.0, -(w - 510) / 20
    elif 510 <= w < 580: r, g, b = (w - 510) / 70, 1.0, 0.0
    elif 580 <= w < 645: r, g, b = 1.0, -(w - 645) / 65, 0.0
    else: r, g, b = 1.0, 0.0, 0.0
    f = 0.3 + 0.7 * (w - 380) / 40 if w < 420 else (0.3 + 0.7 * (780 - w) / 80 if w > 700 else 1.0)
    c = [int(round(255 * (v * f) ** 0.8)) if v > 0 else 0 for v in (r, g, b)]
    return "#%02x%02x%02x" % tuple(c)


E = lambda n: -13.6 / n ** 2
def Y(e):
    return 292 if e < -5 else 40 - e * 60

p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Inter, sans-serif">',
     f'<rect width="{W}" height="{H}" fill="#ffffff"/>', '<defs>']
for name, col in (("uv", UV), ("ir", IR), ("tx", TEXT)):
    p.append(f'<marker id="m{name}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="4.5" markerHeight="4.5" orient="auto">'
             f'<path d="M0 0 L10 5 L0 10 z" fill="{col}"/></marker>')
balmer = [(3, 656.3, "Hα"), (4, 486.1, "Hβ"), (5, 434.0, "Hγ"), (6, 410.2, "Hδ")]
for n, w, _ in balmer:
    p.append(f'<marker id="b{n}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="4.5" markerHeight="4.5" orient="auto">'
             f'<path d="M0 0 L10 5 L0 10 z" fill="{wl_rgb(w)}"/></marker>')
p.append('</defs>')

XL, XR = 92, 440
# levels
for n in (1, 2, 3, 4, 5, 6):
    y = Y(E(n))
    p.append(f'<line x1="{XL}" y1="{y:.1f}" x2="{XR}" y2="{y:.1f}" stroke="{TEXT}" stroke-width="{2.2 if n < 3 else 1.5}"/>')
p.append(f'<line x1="{XL}" y1="40" x2="{XR}" y2="40" stroke="{TEXT}" stroke-width="1" stroke-dasharray="5 3"/>')
lab = [(1, "n = 1  (−13.6 eV)"), (2, "n = 2  (−3.40)"), (3, "n = 3  (−1.51)"), (4, "n = 4")]
for n, t in lab:
    p.append(f'<text x="{XL-6}" y="{Y(E(n))+4:.1f}" font-size="10.5" fill="{TEXT}" text-anchor="end">{t}</text>')
p.append(f'<text x="{XL-6}" y="{Y(E(5.5))+3:.1f}" font-size="10.5" fill="{TEXT}" text-anchor="end">5, 6, …</text>')
p.append(f'<text x="{XL-6}" y="38" font-size="10.5" fill="{MUTED}" text-anchor="end">∞  (0 eV)</text>')
# axis break
p.append(f'<path d="M{XL-14} 258 L{XL-2} 264 M{XL-14} 266 L{XL-2} 272" stroke="{MUTED}" stroke-width="1.2"/>')
p.append(f'<text x="{XL-18}" y="270" font-size="10" fill="{MUTED}" text-anchor="end">gap not to scale</text>')

def down(x, n_hi, n_lo, col, marker, width=2.0):
    y0, y1 = Y(E(n_hi)), Y(E(n_lo))
    p.append(f'<line x1="{x}" y1="{y0:.1f}" x2="{x}" y2="{y1-2:.1f}" stroke="{col}" stroke-width="{width}" marker-end="url(#{marker})"/>')

for i, n in enumerate((2, 3, 4, 5)):
    down(112 + i * 16, n, 1, UV, "muv")
p.append(f'<text x="112" y="312" font-size="11" font-weight="700" fill="{UV}">Lyman series → n = 1</text>')
p.append(f'<text x="112" y="326" font-size="10.5" fill="{MUTED}">ultraviolet (121.6 nm and shorter)</text>')
for i, (n, w, nm) in enumerate(balmer):
    x = 236 + i * 22
    down(x, n, 2, wl_rgb(w), f"b{n}", 2.6)
p.append(f'<text x="236" y="262" font-size="11" font-weight="700" fill="{TEXT}">Balmer series → n = 2</text>')
p.append(f'<text x="236" y="276" font-size="10.5" fill="{MUTED}">visible (656 nm and shorter)</text>')
for i, n in enumerate((4, 5, 6)):
    down(378 + i * 16, n, 3, IR, "mir")
p.append(f'<text x="{XR}" y="152" font-size="11" font-weight="700" fill="{IR}" text-anchor="end">Paschen → n = 3</text>')
p.append(f'<text x="{XR}" y="166" font-size="10.5" fill="{MUTED}" text-anchor="end">infrared (1875 nm and shorter)</text>')

# right-hand table of Balmer lines
tx = 470
p.append(f'<text x="{tx}" y="58" font-size="11.5" font-weight="700" fill="{TEXT}">Balmer lines</text>')
p.append(f'<text x="{tx}" y="78" font-size="10" fill="{MUTED}">line</text><text x="{tx+42}" y="78" font-size="10" fill="{MUTED}">jump</text>'
         f'<text x="{tx+96}" y="78" font-size="10" fill="{MUTED}">ΔE (eV)</text><text x="{tx+158}" y="78" font-size="10" fill="{MUTED}">λ (nm)</text>')
p.append(f'<line x1="{tx}" y1="84" x2="{tx+204}" y2="84" stroke="{GRID}"/>')
for i, (n, w, nm) in enumerate(balmer):
    y = 102 + i * 20
    dE = 13.6 * (1 / 4 - 1 / n ** 2)
    p.append(f'<rect x="{tx}" y="{y-9}" width="8" height="10" rx="2" fill="{wl_rgb(w)}"/>')
    p.append(f'<text x="{tx+12}" y="{y}" font-size="10.5" fill="{TEXT}">{nm}</text>')
    p.append(f'<text x="{tx+42}" y="{y}" font-size="10.5" fill="{TEXT}">{n} → 2</text>')
    p.append(f'<text x="{tx+96}" y="{y}" font-size="10.5" fill="{TEXT}">{dE:.2f}</text>')
    p.append(f'<text x="{tx+158}" y="{y}" font-size="10.5" fill="{TEXT}">{w:.1f}</text>')
p.append(f'<text x="{tx}" y="196" font-size="10" fill="{MUTED}">Bigger drop → more energy →</text>')
p.append(f'<text x="{tx}" y="209" font-size="10" fill="{MUTED}">shorter wavelength (bluer).</text>')

# spectrum strip
SX0, SX1, SY = 60, 640, 366
def SX(w): return SX0 + (w - 380) / (700 - 380) * (SX1 - SX0)
p.append(f'<text x="{SX0}" y="{SY-12}" font-size="11.5" font-weight="700" fill="{TEXT}">What you see through a diffraction grating: hydrogen’s visible fingerprint</text>')
p.append(f'<rect x="{SX0}" y="{SY}" width="{SX1-SX0}" height="40" fill="#0d1117"/>')
for n, w, nm in balmer:
    x = SX(w)
    col = wl_rgb(w)
    p.append(f'<rect x="{x-4:.1f}" y="{SY}" width="8" height="40" fill="{col}" opacity="0.35"/>')
    p.append(f'<rect x="{x-1.6:.1f}" y="{SY}" width="3.2" height="40" fill="{col}"/>')
    p.append(f'<text x="{x:.1f}" y="{SY+54}" font-size="10" fill="{TEXT}" text-anchor="middle">{nm} {w:.0f}</text>')
for w in (400, 450, 500, 550, 600, 650, 700):
    p.append(f'<line x1="{SX(w):.1f}" y1="{SY+40}" x2="{SX(w):.1f}" y2="{SY+44}" stroke="{MUTED}"/>')
    p.append(f'<text x="{SX(w):.1f}" y="{SY+68}" font-size="10" fill="{MUTED}" text-anchor="middle">{w}</text>')
p.append(f'<text x="{SX0-6}" y="{SY+68}" font-size="10" fill="{MUTED}" text-anchor="end">nm</text>')
p.append("</svg>")
OUT.write_text("\n".join(p))
print("wrote", OUT)
