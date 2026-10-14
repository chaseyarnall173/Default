"""Generate figures/ch03-sources.svg: what kind of accelerating charge produces each band.
Run from source/:  python3 figures/scripts/ch03_sources.py
"""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "ch03-sources.svg"
INK, MUTED, TEAL, PURPLE, MATTER, STROKE, AMBER = (
    "#1f2933", "#52606d", "#12a39a", "#8d5a97", "#d9dee5", "#52606d", "#e09f1f")
W, H = 680, 250
PW = 136
o = []
add = o.append
add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Inter, sans-serif">')
add('<rect width="100%" height="100%" fill="#ffffff"/>')
mk = lambda i, c, s=5: (f'<marker id="{i}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="{s}" markerHeight="{s}" '
                        f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>')
add('<defs>' + mk("at", TEAL) + mk("aa", AMBER) + mk("am", MUTED) + '</defs>')


def wavy(x0, y0, x1, y1, lam=9, amp=3.5):
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    nx, ny = -uy, ux
    pts = []
    n = int(L / 1.2)
    for i in range(n + 1):
        s = L * i / n
        a = amp * math.sin(2 * math.pi * s / lam)
        pts.append(f"{x0 + ux * s + nx * a:.1f},{y0 + uy * s + ny * a:.1f}")
    add(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{AMBER}" stroke-width="2"/>')
    add(f'<line x1="{x1 - ux * 2:.1f}" y1="{y1 - uy * 2:.1f}" x2="{x1 + ux * 4:.1f}" y2="{y1 + uy * 4:.1f}" stroke="{AMBER}" stroke-width="2" marker-end="url(#aa)"/>')


def label(cx, title, lines, energy):
    add(f'<text x="{cx}" y="24" font-size="12.5" font-weight="700" fill="{INK}" text-anchor="middle">{title}</text>')
    for i, t in enumerate(lines):
        add(f'<text x="{cx}" y="{170 + 15 * i}" font-size="11" fill="{INK}" text-anchor="middle">{t}</text>')
    add(f'<text x="{cx}" y="236" font-size="11" fill="{MUTED}" text-anchor="middle">{energy}</text>')


CY = 100
# 1 radio / microwave: antenna
cx = PW * 0.5
add(f'<rect x="{cx - 26}" y="{CY - 48}" width="9" height="96" rx="3" fill="{MATTER}" stroke="{STROKE}" stroke-width="1.2"/>')
for yy in (CY - 34, CY - 12, CY + 10, CY + 32):
    add(f'<circle cx="{cx - 21.5}" cy="{yy}" r="3.6" fill="{TEAL}"/>')
add(f'<line x1="{cx - 40}" y1="{CY - 24}" x2="{cx - 40}" y2="{CY + 24}" stroke="{TEAL}" stroke-width="1.8" marker-start="url(#at)" marker-end="url(#at)"/>')
wavy(cx - 10, CY, cx + 44, CY, lam=18, amp=6)
label(cx, "Radio, microwave", ["electrons sloshing", "in antennas, circuits", "and magnetrons"], "below ~0.001 eV")

# 2 infrared: vibrating molecule
cx = PW * 1.5
a1, a2 = (cx - 32, CY + 4), (cx + 4, CY + 4)
zig = [a1]
for i in range(1, 8):
    zig.append((a1[0] + (a2[0] - a1[0]) * i / 8, CY + 4 + (6 if i % 2 else -6)))
zig.append(a2)
add('<polyline points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in zig) + f'" fill="none" stroke="{STROKE}" stroke-width="1.5"/>')
add(f'<circle cx="{a1[0]}" cy="{a1[1]}" r="11" fill="#d1495b" fill-opacity="0.8"/>')
add(f'<circle cx="{a2[0]}" cy="{a2[1]}" r="8" fill="{MATTER}" stroke="{STROKE}" stroke-width="1.2"/>')
add(f'<line x1="{a1[0] - 26}" y1="{CY - 18}" x2="{a1[0] - 4}" y2="{CY - 18}" stroke="{MUTED}" stroke-width="1.3" marker-start="url(#am)" marker-end="url(#am)"/>')
add(f'<line x1="{a2[0] - 8}" y1="{CY - 18}" x2="{a2[0] + 14}" y2="{CY - 18}" stroke="{MUTED}" stroke-width="1.3" marker-start="url(#am)" marker-end="url(#am)"/>')
wavy(cx + 16, CY + 4, cx + 52, CY - 26, lam=12, amp=4.5)
label(cx, "Infrared", ["molecules vibrating", "and jostling: every", "warm object glows"], "~0.001 to 1.8 eV")

# 3 visible / UV: electron dropping between levels
cx = PW * 2.5
levels = [CY - 34, CY + 0, CY + 30]
for i, y in enumerate(levels):
    add(f'<line x1="{cx - 44}" y1="{y}" x2="{cx + 10}" y2="{y}" stroke="{STROKE}" stroke-width="1.6"/>')
add(f'<text x="{cx - 48}" y="{levels[0] + 4}" font-size="10.5" fill="{MUTED}" text-anchor="end">E₃</text>')
add(f'<text x="{cx - 48}" y="{levels[1] + 4}" font-size="10.5" fill="{MUTED}" text-anchor="end">E₂</text>')
add(f'<text x="{cx - 48}" y="{levels[2] + 4}" font-size="10.5" fill="{MUTED}" text-anchor="end">E₁</text>')
add(f'<circle cx="{cx - 18}" cy="{levels[0]}" r="4.2" fill="{TEAL}" fill-opacity="0.35" stroke="{TEAL}" stroke-dasharray="2 2"/>')
add(f'<line x1="{cx - 18}" y1="{levels[0] + 5}" x2="{cx - 18}" y2="{levels[2] - 7}" stroke="{TEAL}" stroke-width="1.8" marker-end="url(#at)"/>')
add(f'<circle cx="{cx - 18}" cy="{levels[2]}" r="4.2" fill="{TEAL}"/>')
wavy(cx - 10, CY - 4, cx + 48, CY - 26, lam=8, amp=3.5)
label(cx, "Visible, UV", ["outer electrons", "dropping between", "energy levels"], "1.8 to ~100 eV")

# 4 X-rays: electron braking near nucleus
cx = PW * 3.5
nx_, ny_ = cx - 8, CY + 12
add(f'<circle cx="{nx_}" cy="{ny_}" r="9" fill="{PURPLE}"/>')
add(f'<text x="{nx_}" y="{ny_ + 4}" font-size="11" font-weight="700" fill="#fff" text-anchor="middle">+</text>')
add(f'<path d="M{cx - 58},{CY - 16} Q{cx + 16},{CY - 16} {cx + 24},{CY + 38}" fill="none" stroke="{TEAL}" stroke-width="1.8" marker-end="url(#at)"/>')
add(f'<circle cx="{cx - 58}" cy="{CY - 16}" r="4" fill="{TEAL}"/>')
wavy(cx + 6, CY - 20, cx + 50, CY - 46, lam=6, amp=3)
label(cx, "X-rays", ["fast electrons braking", "near nuclei; inner-", "shell electron jumps"], "~100 eV to ~100 keV")

# 5 gamma: nucleus rearranging
cx = PW * 4.5
pts = [(0, 0), (8, -5), (-8, -5), (0, -10), (8, 5), (-8, 5), (0, 10), (12, 0), (-12, 0)]
for i, (dx, dy) in enumerate(pts):
    col = PURPLE if i % 2 == 0 else "#b7a3bd"
    add(f'<circle cx="{cx - 14 + dx}" cy="{CY + 4 + dy}" r="5.6" fill="{col}" stroke="#ffffff" stroke-width="1"/>')
wavy(cx + 2, CY - 6, cx + 50, CY - 34, lam=4.5, amp=2.6)
label(cx, "Gamma rays", ["nuclei rearranging:", "radioactive decay,", "nuclear reactions"], "above ~100 keV")

for i in range(1, 5):
    add(f'<line x1="{PW * i}" y1="10" x2="{PW * i}" y2="242" stroke="#e4e7eb" stroke-width="1"/>')
add('</svg>')
OUT.write_text("\n".join(o))
print("wrote", OUT)
