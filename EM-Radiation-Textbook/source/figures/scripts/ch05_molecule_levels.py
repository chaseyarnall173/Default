"""Figure 5.7: a molecule's three nested energy ladders: electronic (eV: visible/UV),
vibrational (~0.05-0.5 eV: infrared), rotational (~0.001 eV: microwave / far-IR). Schematic spacings."""
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "ch05-molecule-levels.svg"
W, H = 680, 352
TEXT, MUTED, GRID = "#1f2933", "#52606d", "#d9dee5"
UVVIS, IR, MW = "#6a4cff", "#9b2226", "#8f6b5a"
ATOM = "#52606d"

p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Inter, sans-serif">',
     f'<rect width="{W}" height="{H}" fill="#ffffff"/>', '<defs>']
for nm, col in (("uv", UVVIS), ("ir", IR), ("mw", MW)):
    p.append(f'<marker id="m{nm}" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="4.5" markerHeight="4.5" orient="auto-start-reverse">'
             f'<path d="M0 0 L10 5 L0 10 z" fill="{col}"/></marker>')
p.append('</defs>')

cols = [(30, 190), (262, 422), (494, 654)]
titles = [("Electronic levels", "electron jumps between orbitals"),
          ("Vibrational levels", "bonds stretch and bend like springs"),
          ("Rotational levels", "the whole molecule spins")]
for (x1, x2), (t, s) in zip(cols, titles):
    p.append(f'<text x="{x1}" y="24" font-size="12" font-weight="700" fill="{TEXT}">{t}</text>')
    p.append(f'<text x="{x1}" y="39" font-size="10" fill="{MUTED}">{s}</text>')

# column 1: two electronic states, each with faint vibrational stacks
x1, x2 = cols[0]
for y0 in (110, 262):
    p.append(f'<line x1="{x1}" y1="{y0}" x2="{x2-40}" y2="{y0}" stroke="{TEXT}" stroke-width="2.4"/>')
    for k in range(1, 5):
        p.append(f'<line x1="{x1}" y1="{y0-k*8}" x2="{x2-40}" y2="{y0-k*8}" stroke="#9aa5b1" stroke-width="0.9"/>')
p.append(f'<line x1="{x2-22}" y1="{262-2}" x2="{x2-22}" y2="{110+2}" stroke="{UVVIS}" stroke-width="2.2" marker-start="url(#muv)" marker-end="url(#muv)"/>')
p.append(f'<text x="{x1}" y="290" font-size="11" font-weight="700" fill="{UVVIS}">≈ 1–10 eV</text>')
p.append(f'<text x="{x1}" y="304" font-size="10.5" fill="{TEXT}">visible and UV photons</text>')
p.append(f'<text x="{x1}" y="318" font-size="10" fill="{MUTED}">dyes, chlorophyll, sunburn</text>')
# zoom box around ground-state vibrational stack
p.append(f'<rect x="{x1-4}" y="226" width="{x2-40-x1+8}" height="40" fill="none" stroke="{MUTED}" stroke-width="1" stroke-dasharray="3 2"/>')
p.append(f'<path d="M{x2-36} 266 L{cols[1][0]-6} 266" stroke="{MUTED}" stroke-width="1" stroke-dasharray="2 3"/>')

# column 2: vibrational ladder
x1, x2 = cols[1]
vy = [262, 216, 172, 130, 90]
for k, y in enumerate(vy):
    p.append(f'<line x1="{x1}" y1="{y}" x2="{x2-40}" y2="{y}" stroke="{TEXT}" stroke-width="{2.0 if k == 0 else 1.6}"/>')
    for j in range(1, 4):
        p.append(f'<line x1="{x1}" y1="{y-j*4}" x2="{x2-40}" y2="{y-j*4}" stroke="#c4ccd5" stroke-width="0.7"/>')
    p.append(f'<text x="{x2-34}" y="{y+4}" font-size="10" fill="{MUTED}">v = {k}</text>')
p.append(f'<line x1="{x1+30}" y1="{vy[0]-2}" x2="{x1+30}" y2="{vy[1]+2}" stroke="{IR}" stroke-width="2.2" marker-start="url(#mir)" marker-end="url(#mir)"/>')
# spring icon
sx, sy = x1 + 70, 68
p.append(f'<circle cx="{sx-26}" cy="{sy}" r="7" fill="{ATOM}"/><circle cx="{sx+26}" cy="{sy}" r="9" fill="{ATOM}"/>')
zz = " ".join(f"{sx-19+i*4},{sy + (5 if i % 2 else -5)}" for i in range(10))
p.append(f'<polyline points="{sx-19},{sy} {zz} {sx+17},{sy}" fill="none" stroke="{TEXT}" stroke-width="1.4"/>')
p.append(f'<text x="{x1}" y="290" font-size="11" font-weight="700" fill="{IR}">≈ 0.05–0.5 eV</text>')
p.append(f'<text x="{x1}" y="304" font-size="10.5" fill="{TEXT}">infrared photons (≈ 2.5–25 µm)</text>')
p.append(f'<text x="{x1}" y="318" font-size="10" fill="{MUTED}">CO₂ and H₂O absorbing heat rays</text>')
p.append(f'<rect x="{x1-4}" y="244" width="{x2-40-x1+4}" height="22" fill="none" stroke="{MUTED}" stroke-width="1" stroke-dasharray="3 2"/>')
p.append(f'<path d="M{x2-36} 266 L{cols[2][0]-6} 266" stroke="{MUTED}" stroke-width="1" stroke-dasharray="2 3"/>')

# column 3: rotational ladder, E ~ J(J+1)
x1, x2 = cols[2]
for J in range(0, 6):
    y = 262 - J * (J + 1) * 5.0
    p.append(f'<line x1="{x1}" y1="{y:.1f}" x2="{x2-40}" y2="{y:.1f}" stroke="{TEXT}" stroke-width="1.6"/>')
    p.append(f'<text x="{x2-34}" y="{y+4:.1f}" font-size="10" fill="{MUTED}">J = {J}</text>')
p.append(f'<line x1="{x1+60}" y1="{262-10-2}" x2="{x1+60}" y2="{262-30+2}" stroke="{MW}" stroke-width="2.2" marker-start="url(#mmw)" marker-end="url(#mmw)"/>')
# rotating molecule icon
rx, ry = x1 + 70, 74
p.append(f'<line x1="{rx-20}" y1="{ry+8}" x2="{rx+20}" y2="{ry-8}" stroke="{TEXT}" stroke-width="2"/>')
p.append(f'<circle cx="{rx-20}" cy="{ry+8}" r="7" fill="{ATOM}"/><circle cx="{rx+20}" cy="{ry-8}" r="9" fill="{ATOM}"/>')
p.append(f'<path d="M{rx-34} {ry-4} A 34 16 0 0 1 {rx+4} {ry-20}" fill="none" stroke="{MW}" stroke-width="1.5" marker-end="url(#mmw)"/>')
p.append(f'<text x="{x1}" y="290" font-size="11" font-weight="700" fill="{MW}">≈ 0.0001–0.01 eV</text>')
p.append(f'<text x="{x1}" y="304" font-size="10.5" fill="{TEXT}">microwave / far-IR photons</text>')
p.append(f'<text x="{x1}" y="318" font-size="10" fill="{MUTED}">radio astronomy maps molecules</text>')
p.append(f'<text x="{W/2}" y="344" font-size="10" fill="{MUTED}" text-anchor="middle">Each dashed box is magnified in the next panel. Spacings are schematic: each ladder is roughly 10–100× finer than the last.</text>')
p.append("</svg>")
OUT.write_text("\n".join(p))
print("wrote", OUT)
