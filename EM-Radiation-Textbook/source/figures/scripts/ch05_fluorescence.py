"""Figure 5.6: fluorescence (fast) and phosphorescence (slow) on a simplified molecular energy diagram,
plus a schematic of the Stokes shift between absorption and emission bands.
Example numbers: black-light UV at 365 nm (3.40 eV) excites a highlighter dye that emits near 510 nm (2.43 eV)."""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "ch05-fluorescence.svg"
W, H = 680, 372
TEXT, MUTED, GRID = "#1f2933", "#52606d", "#d9dee5"
UV, HEAT = "#6a4cff", "#d1495b"


def wl_rgb(w):
    if 380 <= w < 440: r, g, b = -(w - 440) / 60, 0.0, 1.0
    elif 440 <= w < 490: r, g, b = 0.0, (w - 440) / 50, 1.0
    elif 490 <= w < 510: r, g, b = 0.0, 1.0, -(w - 510) / 20
    elif 510 <= w < 580: r, g, b = (w - 510) / 70, 1.0, 0.0
    elif 580 <= w < 645: r, g, b = 1.0, -(w - 645) / 65, 0.0
    else: r, g, b = 1.0, 0.0, 0.0
    f = 0.3 + 0.7 * (w - 380) / 40 if w < 420 else (0.3 + 0.7 * (780 - w) / 80 if w > 700 else 1.0)
    c = [int(round(255 * (v * f) ** 0.8)) if v > 0 else 0 for v in (r, g, b)]
    return "#%02x%02x%02x" % tuple(c)

GREEN = "#1fae3a"          # display color for ~510-520 nm emission (slightly darkened for print)
p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Inter, sans-serif">',
     f'<rect width="{W}" height="{H}" fill="#ffffff"/>', '<defs>']
for nm, col in (("uv", UV), ("gr", GREEN), ("ht", HEAT), ("tx", MUTED)):
    p.append(f'<marker id="m{nm}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="4.5" markerHeight="4.5" orient="auto">'
             f'<path d="M0 0 L10 5 L0 10 z" fill="{col}"/></marker>')
p.append('</defs>')

S0, S1, T1 = 296, 120, 176
def state(x1, x2, y, name, sub=True):
    p.append(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{TEXT}" stroke-width="2.4"/>')
    if sub:
        for k in (1, 2, 3):
            p.append(f'<line x1="{x1}" y1="{y-k*11}" x2="{x2}" y2="{y-k*11}" stroke="#9aa5b1" stroke-width="1"/>')
    p.append(f'<text x="{x1-6}" y="{y+4}" font-size="10.5" font-weight="700" fill="{TEXT}" text-anchor="end">{name}</text>')

def wiggle_down(x, y1, y2):
    pts, n = [], 30
    for i in range(n + 1):
        y = y1 + (y2 - y1 - 6) * i / n
        pts.append((x + 3.5 * math.sin(i / n * 6 * math.pi), y))
    p.append('<polyline points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in pts) + f'" fill="none" stroke="{HEAT}" stroke-width="1.6"/>')
    p.append(f'<line x1="{x}" y1="{y2-8}" x2="{x}" y2="{y2-1}" stroke="{HEAT}" stroke-width="1.6" marker-end="url(#mht)"/>')

p.append(f'<text x="14" y="24" font-size="12" font-weight="700" fill="{TEXT}">Inside a fluorescent molecule or crystal</text>')
p.append(f'<text x="14" y="39" font-size="10" fill="{MUTED}">thin lines = vibrational sub-levels of each electronic state</text>')
state(60, 372, S0, "ground")
state(60, 240, S1, "excited")
p.append(f'<line x1="270" y1="{T1}" x2="372" y2="{T1}" stroke="{TEXT}" stroke-width="2.4"/>')
p.append(f'<text x="321" y="{T1-8}" font-size="10" font-weight="700" fill="{TEXT}" text-anchor="middle">“stuck” state</text>')
p.append(f'<text x="321" y="{T1+14}" font-size="10" fill="{MUTED}" text-anchor="middle">(triplet or trap)</text>')

# absorption
p.append(f'<line x1="86" y1="{S0}" x2="86" y2="{S1-33+2}" stroke="{UV}" stroke-width="3" marker-end="url(#muv)"/>')
p.append(f'<text x="80" y="214" font-size="10.5" font-weight="700" fill="{UV}" text-anchor="end">absorb</text>')
p.append(f'<text x="80" y="227" font-size="10" fill="{UV}" text-anchor="end">UV</text>')
p.append(f'<text x="80" y="240" font-size="10" fill="{UV}" text-anchor="end">3.40 eV</text>')
# vibrational relaxation
wiggle_down(116, S1 - 33, S1)
p.append(f'<text x="124" y="{S1-38}" font-size="10" fill="{HEAT}">heat (≈ps)</text>')
# fluorescence
p.append(f'<line x1="150" y1="{S1}" x2="150" y2="{S0-22-2}" stroke="{GREEN}" stroke-width="3" marker-end="url(#mgr)"/>')
p.append(f'<text x="156" y="214" font-size="10.5" font-weight="700" fill="#137a28">emit</text>')
p.append(f'<text x="156" y="227" font-size="10" fill="#137a28">visible</text>')
p.append(f'<text x="156" y="240" font-size="10" fill="#137a28">2.43 eV</text>')
wiggle_down(206, S0 - 22, S0)
p.append(f'<text x="214" y="{S0-26}" font-size="10" fill="{HEAT}">heat</text>')
# phosphorescence path
p.append(f'<path d="M226 {S1+2} Q 262 {S1+8} 286 {T1-2}" fill="none" stroke="{MUTED}" stroke-width="1.5" stroke-dasharray="4 3" marker-end="url(#mtx)"/>')
p.append(f'<text x="250" y="{S1-6}" font-size="10" fill="{MUTED}">side-step</text>')
p.append(f'<line x1="344" y1="{T1+20}" x2="344" y2="{S0-2}" stroke="{GREEN}" stroke-width="3" stroke-dasharray="6 4" marker-end="url(#mgr)"/>')
p.append(f'<text x="350" y="236" font-size="10.5" font-weight="700" fill="#137a28">slow,</text>')
p.append(f'<text x="350" y="249" font-size="10" fill="#137a28">“forbidden”</text>')
p.append(f'<text x="350" y="262" font-size="10" fill="#137a28">drop</text>')

p.append(f'<text x="14" y="324" font-size="10.5" fill="{TEXT}"><tspan font-weight="700">Fluorescence</tspan> (solid arrows): emission within ~ns; stops when the UV stops.</text>')
p.append(f'<text x="14" y="340" font-size="10.5" fill="{TEXT}"><tspan font-weight="700">Phosphorescence</tspan> (dashed): electron parked in a stuck state;</text>')
p.append(f'<text x="14" y="354" font-size="10.5" fill="{TEXT}">leaks out over seconds to hours (glow-in-the-dark).</text>')

# ---------- right: Stokes shift schematic ----------
x0, x1, yb, yt = 440, 668, 268, 110
p.append(f'<text x="{x0-20}" y="24" font-size="12" font-weight="700" fill="{TEXT}">The Stokes shift (schematic)</text>')
p.append(f'<text x="{x0-20}" y="39" font-size="10" fill="{MUTED}">emitted light is redder than absorbed light</text>')
def X(w): return x0 + (w - 300) / (650 - 300) * (x1 - x0)
def band(center, width, col, fill_op):
    pts = []
    for i in range(0, 141):
        w = 300 + i * 2.5
        v = math.exp(-((w - center) / width) ** 2)
        pts.append((X(w), yb - v * (yb - yt)))
    d = "M" + " L".join(f"{a:.1f} {b:.1f}" for a, b in pts)
    p.append(f'<path d="{d} L{X(650):.1f} {yb} L{X(300):.1f} {yb} Z" fill="{col}" opacity="{fill_op}"/>')
    p.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="2"/>')
band(365, 32, UV, 0.12)
band(510, 38, GREEN, 0.14)
p.append(f'<line x1="{x0}" y1="{yb}" x2="{x1}" y2="{yb}" stroke="{MUTED}" stroke-width="1.2"/>')
for w in (300, 400, 500, 600):
    p.append(f'<line x1="{X(w):.1f}" y1="{yb}" x2="{X(w):.1f}" y2="{yb+4}" stroke="{MUTED}"/>')
    p.append(f'<text x="{X(w):.1f}" y="{yb+17}" font-size="10" fill="{MUTED}" text-anchor="middle">{w}</text>')
p.append(f'<text x="{x1}" y="{yb+32}" font-size="10" fill="{MUTED}" text-anchor="end">wavelength (nm) →</text>')
p.append(f'<text x="{X(365):.1f}" y="{yt-8}" font-size="10.5" font-weight="700" fill="{UV}" text-anchor="middle">absorbs</text>')
p.append(f'<text x="{X(510):.1f}" y="{yt-8}" font-size="10.5" font-weight="700" fill="#137a28" text-anchor="middle">emits</text>')
p.append(f'<line x1="{X(372):.1f}" y1="{yt+40}" x2="{X(500):.1f}" y2="{yt+40}" stroke="{TEXT}" stroke-width="1.3" marker-end="url(#mtx)"/>')
p.append(f'<text x="{X(436):.1f}" y="{yt+34}" font-size="10" fill="{TEXT}" text-anchor="middle">Stokes shift</text>')
p.append(f'<text x="{x0-20}" y="324" font-size="10.5" fill="{TEXT}">Each emitted photon carries less energy</text>')
p.append(f'<text x="{x0-20}" y="340" font-size="10.5" fill="{TEXT}">than the absorbed one; the difference</text>')
p.append(f'<text x="{x0-20}" y="354" font-size="10.5" fill="{TEXT}">became heat (red wiggles at left).</text>')
p.append("</svg>")
OUT.write_text("\n".join(p))
print("wrote", OUT)
