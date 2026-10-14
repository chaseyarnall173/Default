"""Figure 4.2: the marble-in-a-football-field scale model, drawn to scale.

Scale model: nucleus = 1.5 cm marble. Cloud diameter = 1.5 cm x (atom diameter / nucleus diameter).
  atom diameters: H = 2 x Bohr radius (0.0529 nm); C, Fe, Au from Callister's atomic radii
  (0.071, 0.124, 0.144 nm), doubled.
  nucleus diameters: proton 2 x 0.84 fm; others 2 x 1.2 fm x A^(1/3).
American football field incl. end zones: 120 yd x 53.3 yd = 109.7 m x 48.8 m.
"""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "ch04-marble-field.svg"
W, H = 680, 390
TEXT, MUTED, GRID = "#1f2933", "#52606d", "#d9dee5"
ELEC, NUC, GREEN = "#12a39a", "#8d5a97", "#0b6e4f"
MARBLE = 0.015  # m

def scaled(d_atom_nm, d_nuc_fm):
    return MARBLE * (d_atom_nm * 1e-9) / (d_nuc_fm * 1e-15)

atoms = [  # label, scaled diameter (m)
    ("Hydrogen", scaled(2 * 0.0529, 2 * 0.84)),
    ("Carbon", scaled(2 * 0.071, 2 * 1.2 * 12 ** (1 / 3))),
    ("Iron", scaled(2 * 0.124, 2 * 1.2 * 55.85 ** (1 / 3))),
    ("Gold", scaled(2 * 0.144, 2 * 1.2 * 197 ** (1 / 3))),
]
FIELD_L, FIELD_W = 109.7, 48.8

p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Inter, sans-serif">',
     f'<rect width="{W}" height="{H}" fill="#ffffff"/>']

# ---------- left: map view, to scale ----------
cx, cy, S = 196, 196, 0.33            # center and px per meter
a0_m = atoms[0][1] / 2                 # scaled Bohr radius (m)
a0 = a0_m * S
# fuzzy hydrogen 1s cloud: density ~ exp(-2r/a0); show sqrt(density) as opacity so the tail is visible
R = 3.2 * a0
stops = []
for i in range(0, 41):
    r = i / 40 * R
    op = 0.55 * math.exp(-r / a0)      # sqrt of exp(-2r/a0)
    stops.append(f'<stop offset="{i/40:.3f}" stop-color="{ELEC}" stop-opacity="{op:.3f}"/>')
p.append('<defs><radialGradient id="cloud" cx="0.5" cy="0.5" r="0.5">' + "".join(stops) + '</radialGradient>'
         f'<clipPath id="panel"><rect x="6" y="14" width="380" height="370" rx="8"/></clipPath></defs>')
p.append(f'<rect x="6" y="14" width="380" height="370" rx="8" fill="#f5f7fa"/>')
p.append(f'<g clip-path="url(#panel)"><circle cx="{cx}" cy="{cy}" r="{R:.1f}" fill="url(#cloud)"/></g>')
p.append(f'<rect x="6" y="14" width="380" height="370" rx="8" fill="none" stroke="{GRID}"/>')

# nominal diameters as dashed circles
for name, d in (atoms[0], atoms[3]):
    r = d / 2 * S
    p.append(f'<circle cx="{cx}" cy="{cy}" r="{r:.1f}" fill="none" stroke="{TEXT}" stroke-width="1.1" stroke-dasharray="5 4"/>')
r_h, r_au = atoms[0][1] / 2 * S, atoms[3][1] / 2 * S
p.append(f'<text x="{cx}" y="{cy - r_h + 26:.1f}" font-size="11" font-weight="600" fill="{TEXT}" text-anchor="middle">hydrogen: ≈ {atoms[0][1]:.0f} m across</text>')
p.append(f'<text x="{cx}" y="{cy - r_au - 7:.1f}" font-size="11" font-weight="600" fill="{TEXT}" text-anchor="middle">gold: ≈ {atoms[3][1]:.0f} m</text>')

# football field (to scale) with end zones
fl, fw = FIELD_L * S, FIELD_W * S
fx, fy = cx - fl / 2, cy - fw / 2
ez = 9.14 * S
p.append(f'<rect x="{fx:.1f}" y="{fy:.1f}" width="{fl:.1f}" height="{fw:.1f}" fill="{GREEN}" stroke="#ffffff" stroke-width="0.8"/>')
for xline in (fx + ez, fx + fl - ez):
    p.append(f'<line x1="{xline:.1f}" y1="{fy:.1f}" x2="{xline:.1f}" y2="{fy+fw:.1f}" stroke="#ffffff" stroke-width="0.8"/>')
# the marble: true size here would be 0.0054 px, so mark its position
p.append(f'<circle cx="{cx}" cy="{cy}" r="1.6" fill="{NUC}" stroke="#ffffff" stroke-width="0.8"/>')
p.append(f'<line x1="{cx+1.5}" y1="{cy+1.5}" x2="{cx+30}" y2="{cy+58}" stroke="{TEXT}" stroke-width="0.9"/>')
p.append(f'<text x="{cx+16}" y="{cy+72}" font-size="10.5" fill="{TEXT}">marble = nucleus (true</text>')
p.append(f'<text x="{cx+16}" y="{cy+85}" font-size="10.5" fill="{TEXT}">size here: 1/200 pixel)</text>')
p.append(f'<line x1="{fx+4:.1f}" y1="{fy+fw:.1f}" x2="{cx-34:.1f}" y2="{cy+58:.1f}" stroke="{TEXT}" stroke-width="0.9"/>')
p.append(f'<text x="{cx-24:.1f}" y="{cy+72:.1f}" font-size="10.5" fill="{TEXT}" text-anchor="end">football field</text>')
p.append(f'<text x="{cx-24:.1f}" y="{cy+85:.1f}" font-size="10.5" fill="{TEXT}" text-anchor="end">(110 m), to scale</text>')
# scale bar
sb = 300 * S
p.append(f'<line x1="22" y1="368" x2="{22+sb:.1f}" y2="368" stroke="{TEXT}" stroke-width="2"/>')
p.append(f'<line x1="22" y1="363" x2="22" y2="373" stroke="{TEXT}" stroke-width="1.2"/><line x1="{22+sb:.1f}" y1="363" x2="{22+sb:.1f}" y2="373" stroke="{TEXT}" stroke-width="1.2"/>')
p.append(f'<text x="{22+sb+6:.1f}" y="372" font-size="10.5" fill="{MUTED}">300 m</text>')
p.append(f'<text x="16" y="32" font-size="10" fill="{MUTED}">no hard edge:</text>')
p.append(f'<text x="16" y="45" font-size="10" fill="{MUTED}">shading just fades</text>')

# ---------- right: bar chart of scaled diameters ----------
bx0, bx1 = 488, 640      # bar origin and length of the longest scale value (1000 m)
def BX(m):
    return bx0 + m / 1000 * (bx1 - bx0)
p.append(f'<text x="404" y="34" font-size="11.5" font-weight="700" fill="{TEXT}">If the nucleus were a 1.5 cm marble,</text>')
p.append(f'<text x="404" y="49" font-size="11.5" font-weight="700" fill="{TEXT}">the electron cloud would be:</text>')
rows = atoms + [("Football field", FIELD_L)]
y = 80
for name, d in rows:
    col = GREEN if name.startswith("Football") else ELEC
    p.append(f'<text x="{bx0-8}" y="{y+12}" font-size="11" fill="{TEXT}" text-anchor="end">{name}</text>')
    p.append(f'<rect x="{bx0}" y="{y+2}" width="{BX(d)-bx0:.1f}" height="14" rx="3" fill="{col}"/>')
    p.append(f'<text x="{BX(d)+5:.1f}" y="{y+13}" font-size="11" font-weight="600" fill="{TEXT}">{d:,.0f} m</text>')
    y += 30
# axis for bars
p.append(f'<line x1="{bx0}" y1="74" x2="{bx0}" y2="{y-6}" stroke="{MUTED}" stroke-width="1"/>')
for m in (0, 500, 1000):
    p.append(f'<text x="{BX(m):.1f}" y="{y+8}" font-size="10" fill="{MUTED}" text-anchor="middle">{m:,} m</text>')
notes = ["Heavier atoms have bigger nuclei, so", "their ratio is smaller, but every cloud", "is still several fields across.",
         "", "Fraction of the atom’s volume", "filled by the nucleus: less than", "one part in a trillion (10⁻¹²)."]
for i, t in enumerate(notes):
    p.append(f'<text x="404" y="{y+40+i*15}" font-size="10.5" fill="{MUTED}">{t}</text>')

p.append("</svg>")
OUT.write_text("\n".join(p))
print("wrote", OUT, [(n, round(d)) for n, d in atoms])
