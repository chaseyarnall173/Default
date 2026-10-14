"""Figure 4.4: standing waves on a guitar string vs. de Broglie waves wrapped around an orbit."""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "ch04-standing-waves.svg"
W, H = 680, 330
TEXT, MUTED, GRID = "#1f2933", "#52606d", "#d9dee5"
STRING, ELEC, NUC, BAD = "#3e4c59", "#12a39a", "#8d5a97", "#d1495b"

p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Inter, sans-serif">',
     f'<rect width="{W}" height="{H}" fill="#ffffff"/>']

def poly(pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)

# ---------- left: guitar string ----------
p.append(f'<text x="14" y="22" font-size="12" font-weight="700" fill="{TEXT}">A guitar string: only whole half-waves fit</text>')
x0, x1, A = 120, 318, 15
rows = [(1, 66, True), (2, 128, True), (3, 190, True), (2.5, 262, False)]
for n, yc, ok in rows:
    col = STRING if ok else BAD
    for sgn, dash in ((1, ""), (-1, ' stroke-dasharray="4 3" opacity="0.55"')):
        pts = [(x0 + t * (x1 - x0), yc - sgn * A * math.sin(n * math.pi * t)) for t in [i / 120 for i in range(121)]]
        p.append(f'<polyline points="{poly(pts)}" fill="none" stroke="{col}" stroke-width="2"{dash}/>')
    for xp in (x0, x1):
        p.append(f'<rect x="{xp-3}" y="{yc-20}" width="6" height="40" rx="2" fill="#9aa5b1"/>')
    if ok:
        half = {1: "1 half-wave", 2: "2 half-waves", 3: "3 half-waves"}[n]
        p.append(f'<text x="14" y="{yc-2}" font-size="11.5" font-weight="700" fill="{TEXT}">n = {n}</text>')
        p.append(f'<text x="14" y="{yc+12}" font-size="10.5" fill="{MUTED}">{half}</text>')
    else:
        p.append(f'<text x="14" y="{yc-2}" font-size="11.5" font-weight="700" fill="{BAD}">2.5 half-</text>')
        p.append(f'<text x="14" y="{yc+12}" font-size="11.5" font-weight="700" fill="{BAD}">waves ✗</text>')
        p.append(f'<text x="{x1+8}" y="{yc-24}" font-size="10" fill="{BAD}" text-anchor="end">end can’t move: not allowed</text>')
p.append(f'<text x="14" y="306" font-size="10.5" fill="{MUTED}">Each allowed pattern has its own frequency, so the string</text>')
p.append(f'<text x="14" y="320" font-size="10.5" fill="{MUTED}">can only ring at certain notes.</text>')

p.append(f'<line x1="345" y1="14" x2="345" y2="318" stroke="{GRID}" stroke-width="1"/>')

# ---------- right: de Broglie wave around an orbit ----------
p.append(f'<text x="362" y="22" font-size="12" font-weight="700" fill="{TEXT}">An electron wave around a nucleus</text>')
p.append(f'<text x="362" y="37" font-size="10.5" fill="{MUTED}">(de Broglie’s helpful model, not the full quantum picture)</text>')

def ring(cx, cy, R0, amp, k, laps, col, width=2.0, opacity=1.0):
    N = 720 * laps
    pts = []
    for i in range(N + 1):
        th = 2 * math.pi * laps * i / N
        r = R0 + amp * math.sin(k * th)
        pts.append((cx + r * math.cos(th), cy - r * math.sin(th)))
    p.append(f'<polyline points="{poly(pts)}" fill="none" stroke="{col}" stroke-width="{width}" opacity="{opacity}" stroke-linejoin="round"/>')

for cx, k, ok in ((432, 4, True), (592, 4.4, False)):
    cy, R0 = 158, 60
    p.append(f'<circle cx="{cx}" cy="{cy}" r="{R0}" fill="none" stroke="{GRID}" stroke-width="1" stroke-dasharray="3 3"/>')
    if ok:
        ring(cx, cy, R0, 10, k, 1, ELEC, 2.2)
    else:
        ring(cx, cy, R0, 10, k, 3, BAD, 1.5, 0.75)
    p.append(f'<circle cx="{cx}" cy="{cy}" r="5" fill="{NUC}"/>')

p.append(f'<text x="432" y="248" font-size="11.5" font-weight="700" fill="{TEXT}" text-anchor="middle">Fits: exactly 4 wavelengths</text>')
p.append(f'<text x="432" y="263" font-size="10.5" fill="{MUTED}" text-anchor="middle">wave joins itself smoothly</text>')
p.append(f'<text x="432" y="277" font-size="10.5" fill="{MUTED}" text-anchor="middle">→ an allowed state (n = 4)</text>')
p.append(f'<text x="592" y="248" font-size="11.5" font-weight="700" fill="{BAD}" text-anchor="middle">4.4 wavelengths ✗</text>')
p.append(f'<text x="592" y="263" font-size="10.5" fill="{MUTED}" text-anchor="middle">each lap lands out of step</text>')
p.append(f'<text x="592" y="277" font-size="10.5" fill="{MUTED}" text-anchor="middle">and cancels → not allowed</text>')
p.append(f'<text x="362" y="306" font-size="10.5" fill="{MUTED}">Rule: circumference = n × wavelength (n = 1, 2, 3, …),</text>')
p.append(f'<text x="362" y="320" font-size="10.5" fill="{MUTED}">so only certain orbits, and certain energies, are possible.</text>')

p.append("</svg>")
OUT.write_text("\n".join(p))
print("wrote", OUT)
