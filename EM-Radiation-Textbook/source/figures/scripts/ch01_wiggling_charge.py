"""Generate figures/ch01-wiggling-charge.svg.

(a) Field lines of a charge that was jerked upward a short time ago (the "kink" picture):
    outside radius r2 = ct the field still points from the OLD position; inside r1 = c(t - tau)
    it points from the NEW position; the connecting kinks are the radiation pulse.
(b) A charge driven up and down continuously (an antenna) sends out a train of such kinks:
    an electromagnetic wave. Arrows show the E field along a line perpendicular to the antenna.
Run from source/:  python3 figures/scripts/ch01_wiggling_charge.py
"""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "ch01-wiggling-charge.svg"
RED, BLUE, INK, MUTED, TEAL, PURPLE, MATTER, STROKE = (
    "#d1495b", "#2e6fdb", "#1f2933", "#52606d", "#12a39a", "#8d5a97", "#d9dee5", "#52606d")
W, H = 680, 330
out = []
add = out.append
add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Inter, sans-serif">')
add('<rect width="100%" height="100%" fill="#ffffff"/>')
mk = lambda i, c, s=6: (f'<marker id="{i}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="{s}" markerHeight="{s}" '
                        f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>')
add('<defs>' + mk("ar", RED) + mk("am", MUTED) + mk("at", TEAL, 5) + mk("ai", INK, 7) + '</defs>')

# ---------------- panel (a) ----------------
cx, cy = 165, 178          # old position O
h = 28                     # displacement to new position O' (upward)
nx, ny = cx, cy - h
r1, r2, R = 56, 80, 150    # inner radius, outer radius, line length
add(f'<text x="16" y="24" font-size="13" font-weight="700" fill="{INK}">(a) Jerk a charge once</text>')
add(f'<text x="16" y="41" font-size="11.5" fill="{MUTED}">The news spreads outward at speed c</text>')
add(f'<circle cx="{cx}" cy="{cy}" r="{r2}" fill="none" stroke="{MUTED}" stroke-width="1" stroke-dasharray="4 4"/>')
add(f'<circle cx="{nx}" cy="{ny}" r="{r1}" fill="none" stroke="{MUTED}" stroke-width="1" stroke-dasharray="4 4"/>')
for deg in range(0, 360, 30):
    t = math.radians(deg)
    ux, uy = math.cos(t), math.sin(t)
    # inner segment from new position, outer from old position
    p1 = (nx + 14 * ux, ny + 14 * uy)
    p2 = (nx + r1 * ux, ny + r1 * uy)
    p3 = (cx + r2 * ux, cy + r2 * uy)
    p4 = (cx + R * ux, cy + R * uy)
    if p4[1] < 52 or p4[1] > 280:      # clip to panel height (leave room for notes)
        f = ((52 if p4[1] < 52 else 280) - cy) / (R * uy)
        p4 = (cx + R * f * ux, cy + R * f * uy)
    if p4[0] > 330:
        f = (330 - cx) / (R * ux)
        p4 = (cx + R * f * ux, cy + R * f * uy)
    if p4[0] < 8:
        f = (8 - cx) / (R * ux)
        p4 = (cx + R * f * ux, cy + R * f * uy)
    add(f'<polyline points="{p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f} {p3[0]:.1f},{p3[1]:.1f} {p4[0]:.1f},{p4[1]:.1f}" '
        f'fill="none" stroke="{RED}" stroke-width="1.8" stroke-linejoin="round" marker-end="url(#ar)"/>')
# ghost of old position + charge at new position
add(f'<circle cx="{cx}" cy="{cy}" r="9" fill="none" stroke="{PURPLE}" stroke-width="1.4" stroke-dasharray="2 2"/>')
add(f'<line x1="{cx - 26}" y1="{cy + 4}" x2="{cx - 26}" y2="{ny - 2}" stroke="{INK}" stroke-width="1.6" marker-end="url(#ai)"/>')
add(f'<circle cx="{nx}" cy="{ny}" r="10" fill="{PURPLE}"/>')
add(f'<text x="{nx}" y="{ny + 4.5}" font-size="14" font-weight="700" fill="#ffffff" text-anchor="middle">+</text>')
# callouts
add(f'<text x="252" y="64" font-size="11.5" fill="{INK}">kink = the</text>')
add(f'<text x="252" y="79" font-size="11.5" fill="{INK}">radiation pulse</text>')
add(f'<line x1="250" y1="84" x2="{cx + 74 * math.cos(math.radians(-30)):.1f}" y2="{cy - 6 + 74 * math.sin(math.radians(-30)):.1f}" stroke="{MUTED}" stroke-width="1"/>')
add(f'<text x="16" y="300" font-size="11.5" fill="{MUTED}">inside: field already points</text>')
add(f'<text x="16" y="314" font-size="11.5" fill="{MUTED}">from the new position</text>')
add(f'<text x="226" y="300" font-size="11.5" fill="{MUTED}">outside: news has</text>')
add(f'<text x="226" y="314" font-size="11.5" fill="{MUTED}">not arrived yet</text>')

# divider
add(f'<line x1="345" y1="18" x2="345" y2="316" stroke="#d9dee5" stroke-width="1"/>')

# ---------------- panel (b) ----------------
add(f'<text x="362" y="24" font-size="13" font-weight="700" fill="{INK}">(b) Keep wiggling it: an antenna</text>')
add(f'<text x="362" y="41" font-size="11.5" fill="{MUTED}">A train of kinks = an electromagnetic wave</text>')
axl, axy = 392, 178          # antenna x, axis y
add(f'<rect x="{axl - 5}" y="{axy - 80}" width="10" height="160" rx="3" fill="{MATTER}" stroke="{STROKE}" stroke-width="1.2"/>')
for yy in (axy - 58, axy - 30, axy + 2, axy + 30, axy + 58):
    add(f'<circle cx="{axl}" cy="{yy - 6}" r="4.2" fill="{TEAL}"/>')
add(f'<line x1="{axl - 18}" y1="{axy - 40}" x2="{axl - 18}" y2="{axy + 40}" stroke="{TEAL}" stroke-width="2" marker-start="url(#at)" marker-end="url(#at)"/>')
add(f'<text x="{axl - 4}" y="{axy + 104}" font-size="11.5" fill="{INK}" text-anchor="middle">electrons slosh</text>')
add(f'<text x="{axl - 4}" y="{axy + 118}" font-size="11.5" fill="{INK}" text-anchor="middle">up and down at f</text>')
# wave of E arrows to the right
x0, x1 = axl + 22, 616
lam = 120
amp = 62
add(f'<line x1="{x0}" y1="{axy}" x2="{x1 + 40}" y2="{axy}" stroke="{INK}" stroke-width="1.4" marker-end="url(#ai)"/>')
pts = []
for i in range(0, 301):
    x = x0 + (x1 - x0) * i / 300
    pts.append((x, axy - amp * math.sin(2 * math.pi * (x - x0) / lam)))
add('<polyline points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in pts) + f'" fill="none" stroke="{RED}" stroke-width="1.2" stroke-opacity="0.55"/>')
x = x0 + lam / 16
while x < x1:
    s = math.sin(2 * math.pi * (x - x0) / lam)
    if abs(s) > 0.25:
        add(f'<line x1="{x:.1f}" y1="{axy}" x2="{x:.1f}" y2="{axy - amp * s:.1f}" stroke="{RED}" stroke-width="2" marker-end="url(#ar)"/>')
    x += lam / 8
# wavelength bracket
b1 = x0 + lam / 4; b2 = b1 + lam
add(f'<line x1="{b1:.1f}" y1="{axy - amp - 18}" x2="{b2:.1f}" y2="{axy - amp - 18}" stroke="{MUTED}" stroke-width="1.2" marker-start="url(#am)" marker-end="url(#am)"/>')
add(f'<text x="{(b1 + b2) / 2:.1f}" y="{axy - amp - 25}" font-size="13" fill="{INK}" text-anchor="middle" font-style="italic">λ</text>')
add(f'<text x="{x1 + 50}" y="{axy - amp - 22}" font-size="12" fill="{INK}" text-anchor="end" font-weight="600">moves out at c</text>')
add(f'<text x="478" y="{axy + 104}" font-size="11.5" fill="{RED}" font-weight="700">E</text>')
add(f'<text x="491" y="{axy + 104}" font-size="11.5" fill="{MUTED}">field at points along</text>')
add(f'<text x="478" y="{axy + 118}" font-size="11.5" fill="{MUTED}">a line out from the antenna</text>')

add('</svg>')
OUT.write_text("\n".join(out))
print("wrote", OUT)
