"""Figure 5.8: energy bands in solids.
Left: atomic levels broaden into bands as atoms are brought together (schematic, after Callister's figure of
electron energy vs. interatomic separation). Right: metal vs. semiconductor vs. insulator.
Band gaps (room temperature): Si 1.12 eV, GaAs 1.42 eV, diamond ~5.5 eV, sapphire (Al2O3) ~8.8 eV, silica ~9 eV.
Gaps on the right are drawn to a common scale (21 px per eV)."""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "ch05-bands.svg"
W, H = 680, 392
TEXT, MUTED, GRID = "#1f2933", "#52606d", "#d9dee5"
ELEC, LIGHT, FILL, EMPTY = "#12a39a", "#e09f1f", "#9fdcd6", "#ffffff"

p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Inter, sans-serif">',
     f'<rect width="{W}" height="{H}" fill="#ffffff"/>', '<defs>',
     '<marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto">'
     f'<path d="M0 0 L10 5 L0 10 z" fill="{ELEC}"/></marker>',
     '<marker id="ph" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="4" markerHeight="4" orient="auto">'
     f'<path d="M0 0 L10 5 L0 10 z" fill="{LIGHT}"/></marker>',
     '<marker id="gr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
     f'<path d="M0 0 L10 5 L0 10 z" fill="{MUTED}"/></marker>', '</defs>']

def photon(x1, y1, x2, y2, wl=8, amp=3.0, width=1.8):
    L = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    nx, ny = -uy, ux
    n = int(L / 1.2)
    pts = [(x1 + ux * s + nx * amp * math.sin(2 * math.pi * s / wl), y1 + uy * s + ny * amp * math.sin(2 * math.pi * s / wl))
           for s in [i / n * (L - 6) for i in range(n + 1)]]
    p.append('<polyline points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + f'" fill="none" stroke="{LIGHT}" stroke-width="{width}"/>')
    p.append(f'<line x1="{x1+ux*(L-8):.1f}" y1="{y1+uy*(L-8):.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{LIGHT}" stroke-width="{width}" marker-end="url(#ph)"/>')

# ---------- left: levels -> bands ----------
p.append(f'<text x="12" y="22" font-size="12" font-weight="700" fill="{TEXT}">Bring atoms together…</text>')
p.append(f'<text x="12" y="37" font-size="10" fill="{MUTED}">each level spreads into a band</text>')
X0, X1 = 40, 236           # separation axis: small (left) to large (right)
p.append(f'<line x1="{X0}" y1="330" x2="{X1}" y2="330" stroke="{MUTED}" stroke-width="1.2" marker-end="url(#gr)"/>')
p.append(f'<text x="{X1}" y="346" font-size="10" fill="{MUTED}" text-anchor="end">distance between atoms →</text>')
p.append(f'<line x1="{X0}" y1="330" x2="{X0}" y2="56" stroke="{MUTED}" stroke-width="1.2" marker-end="url(#gr)"/>')
p.append(f'<text x="26" y="200" font-size="10" fill="{MUTED}" text-anchor="middle" transform="rotate(-90 26 200)">electron energy</text>')
def band_shape(yc, spread, col):
    # band edges: spread grows as separation shrinks below x_on
    x_on = 200
    top, bot = [], []
    for i in range(0, 61):
        x = X0 + (X1 - X0) * i / 60
        s = spread * max(0.0, (x_on - x) / (x_on - X0)) ** 1.6
        top.append((x, yc - s)); bot.append((x, yc + s))
    d = "M" + " L".join(f"{a:.1f} {b:.1f}" for a, b in top) + " L" + " L".join(f"{a:.1f} {b:.1f}" for a, b in reversed(bot)) + " Z"
    p.append(f'<path d="{d}" fill="{col}" stroke="{TEXT}" stroke-width="1"/>')
band_shape(250, 34, FILL)          # filled (valence) band from the outer level
band_shape(130, 46, "#eef1f5")     # empty (conduction) band from the next level up
xr = 104
p.append(f'<line x1="{xr}" y1="70" x2="{xr}" y2="330" stroke="{TEXT}" stroke-width="1" stroke-dasharray="4 3"/>')
p.append(f'<text x="{xr}" y="64" font-size="10" fill="{TEXT}" text-anchor="middle">solid’s spacing</text>')
p.append(f'<text x="{X1-2}" y="124" font-size="10" fill="{MUTED}" text-anchor="end">empty level</text>')
p.append(f'<text x="{X1-2}" y="244" font-size="10" fill="{MUTED}" text-anchor="end">filled level</text>')
# mark the gap at the solid's spacing
def edge(yc, spread, x):
    return spread * max(0.0, (200 - x) / (200 - X0)) ** 1.6
g_top = 130 + edge(130, 46, xr)
g_bot = 250 - edge(250, 34, xr)
p.append(f'<line x1="{xr+8}" y1="{g_top+1:.1f}" x2="{xr+8}" y2="{g_bot-1:.1f}" stroke="{MUTED}" stroke-width="1.2" marker-start="url(#gr)" marker-end="url(#gr)"/>')
p.append(f'<text x="{xr+13}" y="{(g_top+g_bot)/2+4:.1f}" font-size="10.5" font-weight="700" fill="{TEXT}">band gap</text>')
p.append(f'<line x1="250" y1="16" x2="250" y2="376" stroke="{GRID}"/>')

# ---------- right: three kinds of solid ----------
K = 21.0                     # px per eV
BASE = 300                   # bottom of valence band
VB_H = 70
VB_TOP = BASE - VB_H
cols = [("Metal", 266), ("Semiconductor", 404), ("Insulator", 542)]
CW = 112
for name, x in cols:
    p.append(f'<text x="{x+CW/2}" y="22" font-size="12" font-weight="700" fill="{TEXT}" text-anchor="middle">{name}</text>')

# metal: one partly filled band
x = cols[0][1]
p.append(f'<rect x="{x}" y="{VB_TOP-110}" width="{CW}" height="{VB_H+110}" fill="{EMPTY}" stroke="{TEXT}" stroke-width="1.2"/>')
p.append(f'<rect x="{x}" y="{VB_TOP-30}" width="{CW}" height="{VB_H+30}" fill="{FILL}" stroke="none"/>')
p.append(f'<rect x="{x}" y="{VB_TOP-110}" width="{CW}" height="{VB_H+110}" fill="none" stroke="{TEXT}" stroke-width="1.2"/>')
p.append(f'<line x1="{x}" y1="{VB_TOP-30}" x2="{x+CW}" y2="{VB_TOP-30}" stroke="{TEXT}" stroke-width="1" stroke-dasharray="4 3"/>')
p.append(f'<text x="{x+CW/2}" y="{VB_TOP-36}" font-size="10" fill="{MUTED}" text-anchor="middle">filled up to here</text>')
p.append(f'<text x="{x+CW/2}" y="{VB_TOP+20}" font-size="10" fill="{TEXT}" text-anchor="middle">filled</text>')
p.append(f'<text x="{x+CW/2}" y="{VB_TOP-70}" font-size="10" fill="{TEXT}" text-anchor="middle">empty states</text>')
p.append(f'<text x="{x+CW/2}" y="{VB_TOP-57}" font-size="10" fill="{TEXT}" text-anchor="middle">right above</text>')
p.append(f'<line x1="{x+CW-14}" y1="{VB_TOP-24}" x2="{x+CW-14}" y2="{VB_TOP-84}" stroke="{ELEC}" stroke-width="1.6" marker-end="url(#ah)"/>')

def gap_column(x, eg, label, sublabel, extra=None):
    cb_bot = VB_TOP - eg * K
    p.append(f'<rect x="{x}" y="{VB_TOP}" width="{CW}" height="{VB_H}" fill="{FILL}" stroke="{TEXT}" stroke-width="1.2"/>')
    p.append(f'<rect x="{x}" y="{cb_bot-50:.1f}" width="{CW}" height="50" fill="{EMPTY}" stroke="{TEXT}" stroke-width="1.2"/>')
    p.append(f'<text x="{x+CW/2}" y="{VB_TOP+40}" font-size="10" fill="{TEXT}" text-anchor="middle">valence band</text>')
    p.append(f'<text x="{x+CW/2}" y="{VB_TOP+53}" font-size="10" fill="{TEXT}" text-anchor="middle">(filled)</text>')
    p.append(f'<text x="{x+CW/2}" y="{cb_bot-28:.1f}" font-size="10" fill="{TEXT}" text-anchor="middle">conduction band</text>')
    p.append(f'<text x="{x+CW/2}" y="{cb_bot-15:.1f}" font-size="10" fill="{TEXT}" text-anchor="middle">(empty)</text>')
    p.append(f'<line x1="{x+CW-10}" y1="{cb_bot+1:.1f}" x2="{x+CW-10}" y2="{VB_TOP-1}" stroke="{MUTED}" stroke-width="1.1" marker-start="url(#gr)" marker-end="url(#gr)"/>')
    ym = (cb_bot + VB_TOP) / 2
    p.append(f'<text x="{x+CW-15}" y="{ym+4:.1f}" font-size="10.5" font-weight="700" fill="{TEXT}" text-anchor="end">{label}</text>')
    if extra:
        extra(x, cb_bot)
    return cb_bot

def semi_extra(x, cb_bot):
    # absorption: photon in, electron up; LED: electron down, photon out
    p.append(f'<line x1="{x+20}" y1="{VB_TOP+6}" x2="{x+20}" y2="{cb_bot-6:.1f}" stroke="{ELEC}" stroke-width="1.6" marker-end="url(#ah)"/>')
    p.append(f'<circle cx="{x+20}" cy="{cb_bot-8:.1f}" r="3.6" fill="{ELEC}"/>')

gap_column(cols[1][1], 1.12, "1.12 eV", "", semi_extra)
gap_column(cols[2][1], 5.5, "≈ 5.5 eV", "")

# captions under each column
caps = [["Partly filled band: tiny", "energies lift electrons,", "so it conducts and", "reflects visible light", "(Chapter 6)."],
        ["Small gap (Si 1.12,", "GaAs 1.42 eV). Photons", "with E ≥ Eg absorbed;", "an electron falling back", "gives LED light, E ≈ Eg."],
        ["Wide gap (diamond 5.5,", "Al₂O₃ ≈ 8.8 eV). Visible", "photons can’t bridge it:", "transparent and", "non-conducting."]]
for (name, x), lines in zip(cols, caps):
    for i, t in enumerate(lines):
        p.append(f'<text x="{x}" y="{BASE+22+i*13}" font-size="10" fill="{TEXT}">{t}</text>')
p.append(f'<text x="{cols[1][1]}" y="{VB_TOP-1.12*K-62:.1f}" font-size="10" fill="{MUTED}">gaps drawn to the same scale</text>')
p.append("</svg>")
OUT.write_text("\n".join(p))
print("wrote", OUT)
