"""Generate figures/ch01-fields.svg: electric field of a charge; magnetic field of a current.
Run from source/:  python3 figures/scripts/ch01_fields.py
"""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "ch01-fields.svg"
RED, BLUE, INK, MUTED, TEAL, PURPLE, MATTER, STROKE = (
    "#d1495b", "#2e6fdb", "#1f2933", "#52606d", "#12a39a", "#8d5a97", "#d9dee5", "#52606d")
W, H = 680, 290
o = []
add = o.append
add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Inter, sans-serif">')
add('<rect width="100%" height="100%" fill="#ffffff"/>')
mk = lambda i, c, s=6: (f'<marker id="{i}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="{s}" markerHeight="{s}" '
                        f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>')
add('<defs>' + mk("ar", RED) + mk("ab", BLUE) + mk("ai", INK, 7) + mk("at", TEAL, 5) + '</defs>')

# ---- (a) electric field of a positive charge ----
cx, cy = 150, 160
add(f'<text x="16" y="24" font-size="13" font-weight="700" fill="{INK}">(a) A charge creates an electric field</text>')
for deg in range(0, 360, 30):
    t = math.radians(deg)
    x1, y1 = cx + 18 * math.cos(t), cy + 18 * math.sin(t)
    x2, y2 = cx + 108 * math.cos(t), cy + 108 * math.sin(t)
    xm, ym = cx + 62 * math.cos(t), cy + 62 * math.sin(t)
    add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{xm:.1f}" y2="{ym:.1f}" stroke="{RED}" stroke-width="1.8" marker-end="url(#ar)"/>')
    add(f'<line x1="{xm:.1f}" y1="{ym:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{RED}" stroke-width="1.8"/>')
add(f'<circle cx="{cx}" cy="{cy}" r="13" fill="{PURPLE}"/>')
add(f'<text x="{cx}" y="{cy + 5}" font-size="16" font-weight="700" fill="#fff" text-anchor="middle">+</text>')
# test charge on the 330-degree line
t = math.radians(-30)
tx, ty = cx + 84 * math.cos(t), cy + 84 * math.sin(t)
add(f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="7.5" fill="#ffffff" stroke="{PURPLE}" stroke-width="2"/>')
add(f'<text x="{tx:.1f}" y="{ty + 4:.1f}" font-size="11" font-weight="700" fill="{PURPLE}" text-anchor="middle">q</text>')
fx, fy = tx + 50 * math.cos(t), ty + 50 * math.sin(t)
add(f'<line x1="{tx + 9 * math.cos(t):.1f}" y1="{ty + 9 * math.sin(t):.1f}" x2="{fx:.1f}" y2="{fy:.1f}" stroke="{INK}" stroke-width="2.4" marker-end="url(#ai)"/>')
add(f'<text x="{fx + 6:.1f}" y="{fy - 2:.1f}" font-size="12.5" font-weight="700" fill="{INK}">F = qE</text>')
add(f'<text x="16" y="262" font-size="11.5" fill="{MUTED}">Red lines: direction of E at each point.</text>')
add(f'<text x="16" y="277" font-size="11.5" fill="{MUTED}">A test charge q placed anywhere feels a force.</text>')

add(f'<line x1="340" y1="14" x2="340" y2="280" stroke="#d9dee5" stroke-width="1"/>')

# ---- (b) magnetic field of a current ----
add(f'<text x="356" y="24" font-size="13" font-weight="700" fill="{INK}">(b) Moving charges create a magnetic field</text>')
wx = 482
ys = [105, 195]
rx = [44, 84]
for y in ys:
    for r in rx:
        ry = r * 0.3
        add(f'<path d="M{wx - r},{y} A{r},{ry} 0 0 1 {wx + r},{y}" fill="none" stroke="{BLUE}" stroke-width="1.6" stroke-opacity="0.5"/>')
add(f'<rect x="{wx - 7}" y="44" width="14" height="196" rx="4" fill="{MATTER}" stroke="{STROKE}" stroke-width="1.2"/>')
for y in (66, 132, 168, 222):
    add(f'<circle cx="{wx}" cy="{y}" r="4" fill="{TEAL}"/>')
for y in ys:
    for r in rx:
        ry = r * 0.3
        add(f'<path d="M{wx + r},{y} A{r},{ry} 0 0 1 {wx - r},{y}" fill="none" stroke="{BLUE}" stroke-width="2"/>')
        # arrowhead at the front-most point, pointing right (+x): current up -> B points right on the near side
        px, py = wx + 0.0, y + ry
        add(f'<path d="M{px + 30:.1f},{py:.1f} m-7,-5 l9,5 l-9,5 z" fill="{BLUE}" transform="rotate(-4 {px + 30:.1f} {py:.1f})"/>')
add(f'<line x1="610" y1="210" x2="610" y2="100" stroke="{INK}" stroke-width="2" marker-end="url(#ai)"/>')
add(f'<text x="610" y="230" font-size="12" fill="{INK}" text-anchor="middle">current I</text>')
add(f'<text x="{wx - 96}" y="72" font-size="12.5" font-weight="700" fill="{BLUE}">B</text>')
add(f'<text x="{wx - 84}" y="72" font-size="11.5" fill="{MUTED}">field loops</text>')
add(f'<text x="356" y="262" font-size="11.5" fill="{MUTED}">Blue loops: B circles the wire. Electrons (teal)</text>')
add(f'<text x="356" y="277" font-size="11.5" fill="{MUTED}">drift down, so the conventional current I is up.</text>')
add('</svg>')
OUT.write_text("\n".join(o))
print("wrote", OUT)
