"""Figure 9.3 - why infrared turns into heat. Top: photon energies (E = hc/lambda, hc = 1240 eV nm)
on a log scale against molecular rotation, bond vibration and electronic-transition energies, with
k_B T at 300 K (0.026 eV). Bottom: mechanism - IR photon excites a bond vibration, collisions spread
it into random thermal motion. Output: figures/ch09-ir-absorption.svg"""
from pathlib import Path
import numpy as np

OUT = Path(__file__).resolve().parents[1] / "ch09-ir-absorption.svg"
INK, MUTED, AMBER, FILL, STROKE, RED, GREEN = "#1f2933", "#52606d", "#e09f1f", "#d9dee5", "#52606d", "#d1495b", "#0b6e4f"
W, H = 680, 350
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
          '<marker id="aA" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
          f'<path d="M0,0 L10,5 L0,10 z" fill="{AMBER}"/></marker></defs>')

# ---- energy axis ----
x0, x1, ay = 70, 640, 112
def X(E):
    return x0 + (np.log10(E) + 5) / 6 * (x1 - x0)
T(14, 20, "(a) Photon energy vs. what molecules can do with it", 13, weight="600")
bands = [(1e-4, 1e-2, "molecules rotate (gases)", "#eef4fd", "#2e6fdb"),
         (0.05, 0.5, "bonds vibrate", "#fdf1ec", RED),
         (1.6, 10, "electrons jump (Ch. 5)", "#ecf8f3", GREEN)]
for a, b, lab, fc, tc in bands:
    el.append(f'<rect x="{X(a):.1f}" y="40" width="{X(b)-X(a):.1f}" height="36" rx="4" fill="{fc}" stroke="{tc}" stroke-opacity="0.5"/>')
    T((X(a) + X(b)) / 2, 63, lab, 11.5, "middle", tc, "600")
L(x0, ay, x1, ay, stroke=MUTED, w=1)
for p in range(-5, 2):
    L(X(10.0 ** p), ay, X(10.0 ** p), ay + 5, stroke=MUTED, w=1)
    lab = "1" if p == 0 else ("10" if p == 1 else f"10^{p}")
    if p < 0:
        el.append(f'<text x="{X(10.0**p):.1f}" y="{ay+19}" font-size="11" text-anchor="middle" fill="{MUTED}">10<tspan dy="-5" font-size="8.5">−{-p}</tspan></text>')
    else:
        T(X(10.0 ** p), ay + 19, lab, 11, "middle", MUTED)
T(x1 + 4, ay + 4, "eV", 11, "start", MUTED)
kT = 0.0259
L(X(kT), 40, X(kT), ay, stroke=MUTED, w=1, dash="3 3")
el.append(f'<text x="{X(kT)+5:.1f}" y="95" font-size="11" text-anchor="start" fill="{MUTED}">thermal jiggle at 300 K: k<tspan dy="3" font-size="8.5">B</tspan><tspan dy="-3">T ≈ 0.026 eV</tspan></text>')
marks = [(1.0e-5, "microwave oven", "12 cm → 0.00001 eV"),
         (1240 / 9400, "your thermal glow", "9.4 µm → 0.13 eV"),
         (1240 / 500, "visible light", "500 nm → 2.5 eV")]
for E, l1, l2 in marks:
    el.append(f'<circle cx="{X(E):.1f}" cy="{ay}" r="5" fill="{AMBER}" stroke="white" stroke-width="1.2"/>')
    anchor = "start" if (E < 1e-4 or E > 1) else "end"
    xx = X(E) - 6 if E < 1e-4 else (X(E) - 12 if E > 1 else X(E) + 14)
    T(xx, ay + 38, l1, 11.5, anchor, INK, "600")
    T(xx, ay + 53, l2, 11, anchor, MUTED)

# ---- mechanism ----
T(14, 200, "(b) How an absorbed infrared photon becomes heat", 13, weight="600")
def water(cx, cy, springs=False, scale=1.0):
    ro, rh, bl = 11 * scale, 6.5 * scale, 31 * scale
    hs = [(cx - bl * np.sin(np.radians(52)), cy + bl * np.cos(np.radians(52))),
          (cx + bl * np.sin(np.radians(52)), cy + bl * np.cos(np.radians(52)))]
    for hx, hy in hs:
        if springs:
            n = 7
            pts = []
            for i in range(n + 1):
                t = i / n
                px, py = cx + (hx - cx) * t, cy + (hy - cy) * t
                nx, ny = -(hy - cy) / bl, (hx - cx) / bl
                off = (4 if i % 2 else -4) if 0 < i < n else 0
                pts.append((px + nx * off, py + ny * off))
            el.append('<polyline points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in pts) + f'" fill="none" stroke="{STROKE}" stroke-width="1.4"/>')
        else:
            L(cx, cy, hx, hy, stroke=STROKE, w=2.5)
    for hx, hy in hs:
        el.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{rh}" fill="white" stroke="{STROKE}" stroke-width="1.2"/>')
    el.append(f'<circle cx="{cx}" cy="{cy}" r="{ro}" fill="{FILL}" stroke="{STROKE}" stroke-width="1.2"/>')
    return hs
# step 1
xs = np.linspace(22, 108, 120)
el.append('<polyline points="' + " ".join(f"{x:.1f},{248 + 6*np.sin((x-22)/7):.1f}" for x in xs) + f'" fill="none" stroke="{AMBER}" stroke-width="2.2" marker-end="url(#aA)"/>')
T(20, 228, "IR photon", 11.5, "start", AMBER, "600")
water(150, 240)
T(20, 300, "1. Photon energy matches a", 11.5)
T(20, 315, "bond-vibration step, so it", 11.5)
T(20, 330, "is absorbed.", 11.5)
L(205, 262, 238, 262, stroke=MUTED, w=1.2, extra='marker-end="url(#ah)"')
# step 2
hs = water(320, 240, springs=True)
for hx, hy in hs:
    dx, dy = hx - 320, hy - 240
    nrm = np.hypot(dx, dy)
    ux, uy = dx / nrm, dy / nrm
    L(hx + ux * 10, hy + uy * 10, hx + ux * 30, hy + uy * 30, stroke=RED, w=1.4, extra='marker-start="url(#ah)" marker-end="url(#ah)"')
T(250, 300, "2. The bonds stretch and", 11.5)
T(250, 315, "bend: one molecule is now", 11.5)
T(250, 330, "vibrating hard.", 11.5)
L(420, 262, 453, 262, stroke=MUTED, w=1.2, extra='marker-end="url(#ah)"')
# step 3
rng = np.random.default_rng(3)
for cx, cy in [(490, 232), (545, 222), (600, 238), (650, 226), (515, 270), (575, 272), (632, 268)]:
    water(cx, cy, scale=0.62)
    ang = rng.uniform(0, 2 * np.pi)
    L(cx + 11 * np.cos(ang), cy + 11 * np.sin(ang), cx + 24 * np.cos(ang), cy + 24 * np.sin(ang), stroke=RED, w=1.2, extra='marker-end="url(#ah)"')
T(468, 300, "3. Collisions share the energy:", 11.5)
T(468, 315, "more random jiggling of many", 11.5)
T(468, 330, "molecules = higher temperature.", 11.5)

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
       f'font-family="Inter, sans-serif">\n<rect width="{W}" height="{H}" fill="white"/>\n' + "\n".join(el) + "\n</svg>\n")
OUT.write_text(svg)
print("wrote", OUT)
