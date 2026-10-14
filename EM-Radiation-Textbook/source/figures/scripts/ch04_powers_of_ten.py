"""Figure 4.1: powers-of-ten size ladder from a human hair down to a proton (log scale).

Sizes (approximate, for scale only):
  human hair ~80 um, red blood cell ~7 um, green light wavelength 500 nm, flu virus ~100 nm,
  DNA double-helix width ~2 nm, atoms 0.1-0.5 nm across (H: 2 x 0.0529 nm; Cs ~0.5 nm),
  gold nucleus ~14 fm across (R = 1.2 fm x 197^(1/3) = 7.0 fm), proton ~1.7 fm (r = 0.84 fm).
"""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "ch04-powers-of-ten.svg"
W, H = 680, 322
X0, DEC = 46, 49.0            # x of 10^-3 m and px per decade
AXY = 186                     # axis y
TEXT, MUTED, GRID = "#1f2933", "#52606d", "#d9dee5"
ELEC, NUC, LIGHT = "#12a39a", "#8d5a97", "#e09f1f"


def X(log_m):
    return X0 + (-3 - log_m) * DEC


SUP = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
names = {-3: "1 mm", -4: "100 µm", -5: "10 µm", -6: "1 µm", -7: "100 nm", -8: "10 nm", -9: "1 nm",
         -10: "100 pm", -11: "10 pm", -12: "1 pm", -13: "100 fm", -14: "10 fm", -15: "1 fm"}

p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
     f'font-family="Inter, sans-serif">', f'<rect width="{W}" height="{H}" fill="#ffffff"/>']

# axis + ticks
p.append(f'<line x1="{X(-3)-8}" y1="{AXY}" x2="{X(-15)+8}" y2="{AXY}" stroke="{TEXT}" stroke-width="1.4"/>')
for e in range(-3, -16, -1):
    x = X(e)
    p.append(f'<line x1="{x:.1f}" y1="{AXY-5}" x2="{x:.1f}" y2="{AXY+5}" stroke="{TEXT}" stroke-width="1.2"/>')
    p.append(f'<text x="{x:.1f}" y="{AXY+19}" font-size="11" fill="{TEXT}" text-anchor="middle">{names[e]}</text>')
    p.append(f'<text x="{x:.1f}" y="{AXY+32}" font-size="10" fill="{MUTED}" text-anchor="middle">10{str(e).translate(SUP)} m</text>')

# objects: (log10 size in m, label lines, color, stem height above axis)
items = [
    (math.log10(80e-6), ["Human hair", "≈ 80 µm wide"], MUTED, 40),
    (math.log10(7e-6), ["Red blood", "cell ≈ 7 µm"], MUTED, 92),
    (math.log10(500e-9), ["Green light", "wavelength 500 nm"], LIGHT, 144),
    (math.log10(100e-9), ["Flu virus", "≈ 100 nm"], MUTED, 40),
    (math.log10(2e-9), ["DNA helix", "≈ 2 nm wide"], MUTED, 92),
    (math.log10(14e-15), ["Gold nucleus", "≈ 14 fm"], NUC, 40),
    (math.log10(1.7e-15), ["Proton", "≈ 1.7 fm"], NUC, 92),
]
for lg, lab, col, h in items:
    x = X(lg)
    p.append(f'<line x1="{x:.1f}" y1="{AXY}" x2="{x:.1f}" y2="{AXY-h}" stroke="{col}" stroke-width="1.2"/>')
    p.append(f'<circle cx="{x:.1f}" cy="{AXY}" r="4.5" fill="{col}" stroke="#fff" stroke-width="1.5"/>')
    p.append(f'<text x="{x:.1f}" y="{AXY-h-20}" font-size="11.5" font-weight="600" fill="{TEXT}" text-anchor="middle">{lab[0]}</text>')
    p.append(f'<text x="{x:.1f}" y="{AXY-h-6}" font-size="10.5" fill="{MUTED}" text-anchor="middle">{lab[1]}</text>')

# atoms: a bar spanning 0.1-0.5 nm
xa, xb = X(math.log10(0.5e-9)), X(math.log10(0.1e-9))
p.append(f'<rect x="{xa:.1f}" y="{AXY-6}" width="{xb-xa:.1f}" height="12" rx="4" fill="{ELEC}"/>')
xm = (xa + xb) / 2
p.append(f'<line x1="{xm:.1f}" y1="{AXY-6}" x2="{xm:.1f}" y2="{AXY-144}" stroke="{ELEC}" stroke-width="1.2"/>')
p.append(f'<text x="{xm:.1f}" y="{AXY-164}" font-size="11.5" font-weight="700" fill="{TEXT}" text-anchor="middle">Whole atoms</text>')
p.append(f'<text x="{xm:.1f}" y="{AXY-150}" font-size="10.5" fill="{MUTED}" text-anchor="middle">0.1–0.5 nm across</text>')

# brackets below the axis
def bracket(xl, xr, y, text, col, text2=None):
    p.append(f'<path d="M{xl:.1f} {y-6} L{xl:.1f} {y} L{xr:.1f} {y} L{xr:.1f} {y-6}" fill="none" stroke="{col}" stroke-width="1.4"/>')
    p.append(f'<text x="{(xl+xr)/2:.1f}" y="{y+15}" font-size="11" font-weight="600" fill="{TEXT}" text-anchor="middle">{text}</text>')
    if text2:
        p.append(f'<text x="{(xl+xr)/2:.1f}" y="{y+29}" font-size="10.5" fill="{MUTED}" text-anchor="middle">{text2}</text>')

bracket(X(math.log10(500e-9)), X(math.log10(0.1e-9)), AXY + 58,
        "a light wave is ≈ 5,000× an atom", LIGHT)
bracket(X(math.log10(0.3e-9)), X(math.log10(14e-15)), AXY + 98,
        "atom → nucleus: 20,000–60,000× smaller", ELEC, "nothing in between but the electron cloud")

p.append("</svg>")
OUT.write_text("\n".join(p))
print("wrote", OUT)
