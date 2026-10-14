"""Figure 5.1: absorption, spontaneous emission, and stimulated emission on a two-level energy diagram."""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "ch05-three-processes.svg"
W, H = 680, 300
TEXT, MUTED, GRID = "#1f2933", "#52606d", "#d9dee5"
ELEC, LIGHT = "#12a39a", "#e09f1f"
YU, YL = 112, 188            # upper / lower level y

p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Inter, sans-serif">',
     f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
     '<defs><marker id="ph" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="4" markerHeight="4" orient="auto">'
     f'<path d="M0 0 L10 5 L0 10 z" fill="{LIGHT}"/></marker>'
     '<marker id="gr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto">'
     f'<path d="M0 0 L10 5 L0 10 z" fill="{MUTED}"/></marker></defs>']

def photon(x1, y1, x2, y2, phase=0.0, label=None, lab_dx=0, lab_dy=-10, wl=11, amp=4.2):
    L = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    nx, ny = -uy, ux
    pts = []
    n = int(L / 1.5)
    for i in range(n + 1):
        s = i / n * (L - 7)
        a = amp * math.sin(2 * math.pi * s / wl + phase)
        pts.append((x1 + ux * s + nx * a, y1 + uy * s + ny * a))
    p.append('<polyline points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) +
             f'" fill="none" stroke="{LIGHT}" stroke-width="2"/>')
    p.append(f'<line x1="{x1+ux*(L-9):.1f}" y1="{y1+uy*(L-9):.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{LIGHT}" stroke-width="2" marker-end="url(#ph)"/>')
    if label:
        p.append(f'<text x="{(x1+x2)/2+lab_dx:.1f}" y="{(y1+y2)/2+lab_dy:.1f}" font-size="11" font-weight="700" fill="#8a5a00" text-anchor="middle">{label}</text>')

def levels(x, w, e_up, labels=False):
    for y in (YU, YL):
        p.append(f'<line x1="{x}" y1="{y}" x2="{x+w}" y2="{y}" stroke="{TEXT}" stroke-width="2"/>')
    if labels:
        p.append(f'<text x="{x-5}" y="{YU+4}" font-size="10.5" fill="{MUTED}" text-anchor="end">E₂</text>')
        p.append(f'<text x="{x-5}" y="{YL+4}" font-size="10.5" fill="{MUTED}" text-anchor="end">E₁</text>')
    yc = YU if e_up else YL
    p.append(f'<circle cx="{x+w/2}" cy="{yc-7}" r="6.5" fill="{ELEC}" stroke="#fff" stroke-width="1.2"/>')

def step_arrow(x):
    p.append(f'<line x1="{x}" y1="150" x2="{x+18}" y2="150" stroke="{MUTED}" stroke-width="1.4" marker-end="url(#gr)"/>')

panels = [
    ("A  Absorption", ["A photon with hf = E₂ − E₁ vanishes;", "its energy lifts the electron up.", "Wrong energy: no absorption."]),
    ("B  Spontaneous emission", ["On its own (typically ~ns later) the", "electron drops; a NEW photon is born,", "heading off in a random direction."]),
    ("C  Stimulated emission", ["A passing photon of exactly E₂ − E₁", "triggers the drop: two identical photons", "leave in step (the laser’s trick)."]),
]
for k, (title, lines) in enumerate(panels):
    x0 = 8 + k * 226
    p.append(f'<rect x="{x0}" y="10" width="216" height="282" rx="8" fill="#f5f7fa"/>')
    p.append(f'<text x="{x0+12}" y="32" font-size="12" font-weight="700" fill="{TEXT}">{title}</text>')
    p.append(f'<text x="{x0+48}" y="62" font-size="10" fill="{MUTED}" text-anchor="middle">before</text>')
    p.append(f'<text x="{x0+150}" y="62" font-size="10" fill="{MUTED}" text-anchor="middle">after</text>')
    bx = x0 + 26
    if k == 0:
        ax_ = x0 + 132
        levels(bx, 52, False, True); levels(ax_, 52, True)
        photon(x0 + 98, 74, bx + 34, YL - 22, label="hf", lab_dx=18, lab_dy=-6)
        p.append(f'<line x1="{ax_+26}" y1="{YL-4}" x2="{ax_+26}" y2="{YU+8}" stroke="{ELEC}" stroke-width="1.4" stroke-dasharray="3 3" marker-end="url(#gr)"/>')
    elif k == 1:
        ax_ = x0 + 126
        levels(bx, 52, True, True); levels(ax_, 44, False)
        photon(ax_ + 34, YL - 18, x0 + 208, 80, label="hf", lab_dx=20, lab_dy=4)
        p.append(f'<line x1="{ax_+22}" y1="{YU+2}" x2="{ax_+22}" y2="{YL-16}" stroke="{ELEC}" stroke-width="1.4" stroke-dasharray="3 3" marker-end="url(#gr)"/>')
    else:
        ax_ = x0 + 124
        levels(bx, 52, True, True); levels(ax_, 34, False)
        photon(x0 + 4, 150, bx + 8, 150, label="hf", lab_dy=-10)
        photon(ax_ + 38, 138, x0 + 212, 138, wl=9, amp=3.6)
        photon(ax_ + 38, 162, x0 + 212, 162, wl=9, amp=3.6)
        p.append(f'<text x="{x0+187}" y="124" font-size="10.5" font-weight="700" fill="#8a5a00" text-anchor="middle">2 × hf</text>')
        p.append(f'<line x1="{ax_+17}" y1="{YU+2}" x2="{ax_+17}" y2="{YL-16}" stroke="{ELEC}" stroke-width="1.4" stroke-dasharray="3 3" marker-end="url(#gr)"/>')
    step_arrow(x0 + 100)
    for i, t in enumerate(lines):
        p.append(f'<text x="{x0+12}" y="{238+i*16}" font-size="10.5" fill="{TEXT}">{t}</text>')

p.append("</svg>")
OUT.write_text("\n".join(p))
print("wrote", OUT)
