"""Figure 4.7: why mostly-empty atoms still make solid matter.

Schematic net energy of two atoms vs. separation (Lennard-Jones-like shape, as in Callister's
bonding-energy curve): E(r) = (r0/r)^12 - 2 (r0/r)^6 in units of the well depth. Not to scale for any
particular material; r0 is typically 0.2-0.3 nm in solids.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "ch04-why-solid.svg"
W, H = 680, 392
TEXT, MUTED, GRID = "#1f2933", "#52606d", "#d9dee5"
ELEC, NUC, BAD, ACC = "#12a39a", "#8d5a97", "#d1495b", "#0b6e4f"

def E(r):
    return (1 / r) ** 12 - 2 * (1 / r) ** 6

RX0, RX1 = 0.8, 2.7
PX0, PX1 = 92, 660
def X(r): return PX0 + (r - RX0) / (RX1 - RX0) * (PX1 - PX0)
def Y(e): return 236 - e * 74

p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Inter, sans-serif">',
     f'<rect width="{W}" height="{H}" fill="#ffffff"/>']
# gradient for fuzzy clouds
stops = "".join(f'<stop offset="{i/10:.1f}" stop-color="{ELEC}" stop-opacity="{0.62*(1-i/10)**1.6:.3f}"/>' for i in range(11))
p.append(f'<defs><radialGradient id="cl" cx="0.5" cy="0.5" r="0.5">{stops}</radialGradient></defs>')

# axes
p.append(f'<line x1="{PX0}" y1="{Y(0)}" x2="{PX1}" y2="{Y(0)}" stroke="{MUTED}" stroke-width="1"/>')
p.append(f'<line x1="{PX0}" y1="128" x2="{PX0}" y2="{Y(-1.15)}" stroke="{MUTED}" stroke-width="1.2"/>')
p.append(f'<text x="{PX1}" y="{Y(0)+17}" font-size="10.5" fill="{MUTED}" text-anchor="end">distance between nuclei →</text>')
p.append(f'<text x="{PX0-8}" y="{Y(0)+4}" font-size="10.5" fill="{MUTED}" text-anchor="end">0</text>')
p.append(f'<text x="34" y="{Y(0)}" font-size="10.5" fill="{MUTED}" text-anchor="middle" transform="rotate(-90 34 {Y(0)})">energy of the pair</text>')

# curve
pts = []
r = 0.862
while r <= RX1:
    pts.append((X(r), Y(E(r))))
    r += 0.004
p.append('<polyline points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + f'" fill="none" stroke="{TEXT}" stroke-width="2.2"/>')
# shade the repulsive wall
wall = [(x, y) for x, y in pts if x <= X(0.965)]
p.append('<polyline points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in wall) + f'" fill="none" stroke="{BAD}" stroke-width="4" opacity="0.5"/>')
# r0 marker
p.append(f'<line x1="{X(1):.1f}" y1="{Y(0)}" x2="{X(1):.1f}" y2="{Y(-1)+16:.1f}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="3 3"/>')
p.append(f'<text x="{X(1)+14:.1f}" y="{Y(-1)+18:.1f}" font-size="11" font-weight="700" fill="{ACC}">r₀ = equilibrium spacing (≈ 0.2–0.3 nm in solids):</text>')
p.append(f'<text x="{X(1)+14:.1f}" y="{Y(-1)+32:.1f}" font-size="10.5" fill="{MUTED}">the “atom diameter” in the hard-sphere model of crystals</text>')

# wall label
p.append(f'<text x="{X(0.93)+10:.1f}" y="140" font-size="11" font-weight="700" fill="{BAD}">steep wall = “solid”</text>')
p.append(f'<text x="{X(0.93)+10:.1f}" y="154" font-size="10.5" fill="{TEXT}">overlapping clouds: electron repulsion</text>')
p.append(f'<text x="{X(0.93)+10:.1f}" y="168" font-size="10.5" fill="{TEXT}">+ Pauli exclusion → energy soars</text>')
p.append(f'<text x="{X(1.55):.1f}" y="{Y(E(1.55))+20:.1f}" font-size="10.5" fill="{MUTED}">gentle attraction (bonding)</text>')
p.append(f'<text x="{X(2.2):.1f}" y="{Y(0)-14:.1f}" font-size="10.5" fill="{MUTED}" text-anchor="middle">far apart: almost no force</text>')

# cartoons along the top, linked to points on the curve
def cartoon(cx, cy, sep, rad, label, col_label, rpt, tag):
    for dx in (-sep / 2, sep / 2):
        p.append(f'<circle cx="{cx+dx:.1f}" cy="{cy}" r="{rad}" fill="url(#cl)"/>')
        p.append(f'<circle cx="{cx+dx:.1f}" cy="{cy}" r="2.6" fill="{NUC}"/>')
    p.append(f'<text x="{cx}" y="{cy+rad+14}" font-size="10.5" font-weight="700" fill="{col_label}" text-anchor="middle">{tag}  {label}</text>')
    px, py = X(rpt), Y(E(rpt))
    p.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="{col_label}" stroke="#fff" stroke-width="1.2"/>')
    dx = -14 if tag == "A" else 0
    dy = 4 if tag == "A" else 20
    p.append(f'<text x="{px+dx:.1f}" y="{py+dy:.1f}" font-size="11" font-weight="700" fill="{col_label}" text-anchor="middle">{tag}</text>')
    return px, py

R = 36
cartoon(132, 46, 0.6 * 2 * R * 0.62, R, "squeezed", BAD, 0.88, "A")
cartoon(330, 46, 2 * R * 0.62, R, "comfortable", ACC, 1.0, "B")
cartoon(540, 46, 2.2 * 2 * R * 0.62, R, "far apart", MUTED, 2.2, "C")
p.append(f'<text x="{W/2}" y="382" font-size="10" fill="{MUTED}" text-anchor="middle">Schematic, not to scale for a specific material. Cloud shading fades smoothly: there is no hard edge to “touch.”</text>')
p.append("</svg>")
OUT.write_text("\n".join(p))
print("wrote", OUT)
