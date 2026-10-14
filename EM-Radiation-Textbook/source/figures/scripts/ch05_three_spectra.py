"""Figure 5.4: continuous, absorption-line, and emission-line spectra (Kirchhoff's three cases),
using hydrogen's Balmer lines (656.3, 486.1, 434.0, 410.2 nm) for both kinds of line spectrum."""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "ch05-three-spectra.svg"
W, H = 680, 352
TEXT, MUTED, GRID = "#1f2933", "#52606d", "#d9dee5"
LIGHT, MATTER, MSTROKE = "#e09f1f", "#d9dee5", "#52606d"
LINES = [656.3, 486.1, 434.0, 410.2]


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


SX0, SX1 = 430, 668
def SX(w): return SX0 + (w - 390) / (700 - 390) * (SX1 - SX0)

p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Inter, sans-serif">',
     f'<rect width="{W}" height="{H}" fill="#ffffff"/>', '<defs>',
     '<linearGradient id="rainbow" x1="0" x2="1">' +
     "".join(f'<stop offset="{(w-390)/310:.3f}" stop-color="{wl_rgb(w)}"/>' for w in range(390, 701, 10)) + '</linearGradient>',
     '<radialGradient id="glow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#fff4c2"/>'
     f'<stop offset="0.55" stop-color="{LIGHT}"/><stop offset="1" stop-color="{LIGHT}" stop-opacity="0"/></radialGradient>',
     '<marker id="am" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto">'
     f'<path d="M0 0 L10 5 L0 10 z" fill="{LIGHT}"/></marker>', '</defs>']

def ray(x1, y1, x2, y2, w=2.4, dash=""):
    p.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{LIGHT}" stroke-width="{w}" marker-end="url(#am)"{dash}/>')

def strip(y, kind):
    h = 34
    if kind == "cont":
        p.append(f'<rect x="{SX0}" y="{y}" width="{SX1-SX0}" height="{h}" fill="url(#rainbow)"/>')
    elif kind == "abs":
        p.append(f'<rect x="{SX0}" y="{y}" width="{SX1-SX0}" height="{h}" fill="url(#rainbow)"/>')
        for w in LINES:
            p.append(f'<rect x="{SX(w)-1.7:.1f}" y="{y}" width="3.4" height="{h}" fill="#0d1117"/>')
    else:
        p.append(f'<rect x="{SX0}" y="{y}" width="{SX1-SX0}" height="{h}" fill="#0d1117"/>')
        for w in LINES:
            p.append(f'<rect x="{SX(w)-1.7:.1f}" y="{y}" width="3.4" height="{h}" fill="{wl_rgb(w)}"/>')
    p.append(f'<rect x="{SX0}" y="{y}" width="{SX1-SX0}" height="{h}" fill="none" stroke="{GRID}"/>')

# hot dense source (glowing filament / bulb)
bx, by = 64, 176
p.append(f'<circle cx="{bx}" cy="{by}" r="34" fill="url(#glow)"/>')
p.append(f'<circle cx="{bx}" cy="{by}" r="16" fill="#fff4c2" stroke="{LIGHT}" stroke-width="2"/>')
p.append(f'<text x="{bx}" y="{by+50}" font-size="10.5" font-weight="700" fill="{TEXT}" text-anchor="middle">hot, dense</text>')
p.append(f'<text x="{bx}" y="{by+63}" font-size="10.5" font-weight="700" fill="{TEXT}" text-anchor="middle">source</text>')
p.append(f'<text x="{bx}" y="{by+77}" font-size="10" fill="{MUTED}" text-anchor="middle">(filament, the</text>')
p.append(f'<text x="{bx}" y="{by+90}" font-size="10" fill="{MUTED}" text-anchor="middle">Sun’s surface)</text>')

# cool gas cloud
cx, cy = 240, 176
p.append(f'<ellipse cx="{cx}" cy="{cy}" rx="54" ry="40" fill="{MATTER}" stroke="{MSTROKE}" stroke-width="1.2"/>')
for dx, dy in ((-24, -12), (8, -20), (26, 8), (-10, 14), (-30, 10), (14, -2)):
    p.append(f'<circle cx="{cx+dx}" cy="{cy+dy}" r="3" fill="#12a39a"/>')
p.append(f'<text x="{cx}" y="{cy+56}" font-size="10.5" font-weight="700" fill="{TEXT}" text-anchor="middle">cooler, thin gas</text>')
p.append(f'<text x="{cx}" y="{cy+69}" font-size="10" fill="{MUTED}" text-anchor="middle">(here: hydrogen)</text>')

# rays
ray(bx + 30, by - 18, SX0 - 18, 58)                    # A: direct view
ray(bx + 36, by, cx - 56, cy)                          # into the cloud
ray(cx + 56, cy, SX0 - 18, 176)                        # B: through the cloud
for ang in (105, 150, 205):                  # re-emission in all directions
    a = math.radians(ang)
    x1, y1 = cx + 58 * math.cos(a), cy - 44 * math.sin(a)
    x2, y2 = cx + 86 * math.cos(a), cy - 70 * math.sin(a)
    ray(round(x1), round(y1), round(x2), round(y2), 1.6, ' stroke-dasharray="3 2"')
ray(cx + 40, cy + 30, SX0 - 18, 286, 1.8, ' stroke-dasharray="3 2"')   # C: side view of the cloud
p.append(f'<text x="{cx-40}" y="{cy-96}" font-size="10" fill="{MUTED}" text-anchor="middle">absorbed light is re-emitted</text>')
p.append(f'<text x="{cx-40}" y="{cy-84}" font-size="10" fill="{MUTED}" text-anchor="middle">in random directions</text>')

# spectra + labels
rows = [(44, "cont", "A  Continuous spectrum", "a hot, dense object glows at all wavelengths"),
        (160, "abs", "B  Absorption lines", "the gas removes exactly its own wavelengths"),
        (272, "emis", "C  Emission lines", "the same gas, seen from the side")]
for y, kind, title, sub in rows:
    strip(y, kind)
    p.append(f'<text x="{SX0}" y="{y-20}" font-size="11.5" font-weight="700" fill="{TEXT}">{title}</text>')
    p.append(f'<text x="{SX0}" y="{y-6}" font-size="10" fill="{MUTED}">{sub}</text>')
for w in (400, 500, 600, 700):
    p.append(f'<text x="{SX(w):.1f}" y="{272+48}" font-size="10" fill="{MUTED}" text-anchor="{'end' if w == 700 else 'middle'}">{w}{' nm' if w == 700 else ''}</text>')
p.append(f'<text x="{SX0}" y="{272+64}" font-size="10" fill="{TEXT}">Dark lines in B sit exactly where bright lines are in C.</text>')
p.append("</svg>")
OUT.write_text("\n".join(p))
print("wrote", OUT)
