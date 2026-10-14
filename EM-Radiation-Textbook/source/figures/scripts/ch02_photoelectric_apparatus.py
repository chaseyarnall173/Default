"""Generate figures/ch02-photoelectric-apparatus.svg: the photoelectric-effect experiment.
Light falls on a metal plate in a vacuum tube; ejected electrons reach a collector; an ammeter
measures the current; an adjustable reverse voltage finds the stopping voltage V_s.
Run from source/:  python3 figures/scripts/ch02_photoelectric_apparatus.py
"""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "ch02-photoelectric-apparatus.svg"
INK, MUTED, TEAL, AMBER, MATTER, STROKE = "#1f2933", "#52606d", "#12a39a", "#e09f1f", "#d9dee5", "#52606d"
W, H = 680, 340
o = []
add = o.append
add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Inter, sans-serif">')
add('<rect width="100%" height="100%" fill="#ffffff"/>')
mk = lambda i, c, s=6: (f'<marker id="{i}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="{s}" markerHeight="{s}" '
                        f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>')
add('<defs>' + mk("aa", AMBER, 5) + mk("at", TEAL, 5) + mk("ai", INK, 6) + '</defs>')


def wavy(x0, y0, x1, y1, lam=14, amp=4.5):
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    nx, ny = -uy, ux
    pts = []
    n = int(L / 1.5)
    for i in range(n + 1):
        s = L * i / n
        a = amp * math.sin(2 * math.pi * s / lam)
        pts.append(f"{x0 + ux * s + nx * a:.1f},{y0 + uy * s + ny * a:.1f}")
    return "M" + " L".join(pts)


# vacuum tube
add(f'<rect x="150" y="34" width="380" height="170" rx="40" fill="#f5f7fa" stroke="{STROKE}" stroke-width="1.6"/>')
add(f'<text x="452" y="62" font-size="12" fill="{MUTED}" text-anchor="middle">vacuum</text>')
# window
add(f'<path d="M222,35 L326,35" stroke="#9fc5e8" stroke-width="5"/>')
add(f'<text x="214" y="28" font-size="11.5" fill="{MUTED}" text-anchor="end">quartz window</text>')
# incoming light
for (xs, ye) in ((300, 88), (326, 118), (352, 148)):
    add(f'<path d="{wavy(xs, -6, 214, ye)}" fill="none" stroke="{AMBER}" stroke-width="2.2"/>')
add(f'<text x="364" y="16" font-size="12.5" font-weight="700" fill="{INK}">light <tspan font-weight="400" fill="{MUTED}">(frequency f, intensity I)</tspan></text>')
# emitter plate
add(f'<rect x="198" y="74" width="12" height="104" fill="{MATTER}" stroke="{STROKE}" stroke-width="1.4"/>')
add(f'<text x="188" y="120" font-size="12" fill="{INK}" text-anchor="end" font-weight="600">metal</text>')
add(f'<text x="188" y="135" font-size="12" fill="{INK}" text-anchor="end" font-weight="600">plate</text>')
# collector
add(f'<rect x="470" y="74" width="14" height="104" fill="{MATTER}" stroke="{STROKE}" stroke-width="1.4"/>')
add(f'<text x="462" y="192" font-size="12" fill="{INK}" text-anchor="end" font-weight="600">collector</text>')
# electrons
for (x, y, l) in ((246, 96, 70), (290, 124, 90), (240, 150, 54), (330, 108, 64), (300, 160, 72)):
    add(f'<line x1="{x + 6}" y1="{y}" x2="{x + l}" y2="{y}" stroke="{TEAL}" stroke-width="1.6" marker-end="url(#at)"/>')
    add(f'<circle cx="{x}" cy="{y}" r="5" fill="{TEAL}"/>')
add(f'<text x="236" y="192" font-size="12" fill="{TEAL}" font-weight="700">ejected electrons</text>')
# circuit wires
add(f'<polyline points="203,178 203,290 300,290" fill="none" stroke="{INK}" stroke-width="1.6"/>')
add(f'<polyline points="340,290 410,290" fill="none" stroke="{INK}" stroke-width="1.6"/>')
add(f'<polyline points="446,290 477,290 477,178" fill="none" stroke="{INK}" stroke-width="1.6"/>')
# ammeter
add(f'<circle cx="320" cy="290" r="20" fill="#ffffff" stroke="{INK}" stroke-width="1.6"/>')
add(f'<text x="320" y="295" font-size="14" font-weight="700" fill="{INK}" text-anchor="middle">A</text>')
add(f'<text x="320" y="328" font-size="11.5" fill="{MUTED}" text-anchor="middle">ammeter: electrons per second</text>')
# adjustable voltage source (battery with arrow)
add(f'<line x1="414" y1="276" x2="414" y2="304" stroke="{INK}" stroke-width="2"/>')
add(f'<line x1="424" y1="282" x2="424" y2="298" stroke="{INK}" stroke-width="4"/>')
add(f'<line x1="434" y1="276" x2="434" y2="304" stroke="{INK}" stroke-width="2"/>')
add(f'<line x1="444" y1="282" x2="444" y2="298" stroke="{INK}" stroke-width="4"/>')
add(f'<line x1="402" y1="312" x2="458" y2="266" stroke="{INK}" stroke-width="1.3" marker-end="url(#ai)"/>')
add(f'<text x="470" y="328" font-size="11.5" fill="{MUTED}" text-anchor="middle">adjustable voltage V</text>')
# explanation panel
add(f'<rect x="548" y="40" width="128" height="176" rx="8" fill="#fdf7e9" stroke="#e5c98f" stroke-width="1"/>')
lines = ["Make the collector", "negative and raise V", "until the current", "stops. That stopping", "voltage, V(s), gives", "the fastest electrons'", "kinetic energy:"]
for i, t in enumerate(lines):
    add(f'<text x="557" y="{62 + 16 * i}" font-size="11" fill="{INK}">{t}</text>')
add(f'<text x="610" y="{62 + 16 * 7 + 20}" font-size="13.5" font-weight="700" fill="{INK}" text-anchor="middle">KE<tspan dy="4" font-size="10">max</tspan><tspan dy="-4"> = eV</tspan><tspan dy="4" font-size="10">s</tspan></text>')
add('</svg>')
OUT.write_text("\n".join(o))
print("wrote", OUT)
