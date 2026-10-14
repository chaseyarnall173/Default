"""Figure 5.5: what happens to absorbed light energy (re-emission, heat, chemistry), contrasted with
reflection, where nothing is absorbed."""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "ch05-fates.svg"
W, H = 680, 336
TEXT, MUTED, GRID = "#1f2933", "#52606d", "#d9dee5"
LIGHT, ELEC, NUC, MATTER, MSTROKE, BAD = "#e09f1f", "#12a39a", "#8d5a97", "#d9dee5", "#52606d", "#d1495b"

p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Inter, sans-serif">',
     f'<rect width="{W}" height="{H}" fill="#ffffff"/>', '<defs>',
     '<marker id="ph" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="4" markerHeight="4" orient="auto">'
     f'<path d="M0 0 L10 5 L0 10 z" fill="{LIGHT}"/></marker>',
     '<marker id="gr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto">'
     f'<path d="M0 0 L10 5 L0 10 z" fill="{MUTED}"/></marker>',
     '<marker id="dbl" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
     f'<path d="M0 0 L10 5 L0 10 z" fill="{ELEC}"/></marker>', '</defs>']

def photon(x1, y1, x2, y2, wl=10, amp=3.8, width=2.0):
    L = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    nx, ny = -uy, ux
    n = int(L / 1.5)
    pts = [(x1 + ux * s + nx * amp * math.sin(2 * math.pi * s / wl), y1 + uy * s + ny * amp * math.sin(2 * math.pi * s / wl))
           for s in [i / n * (L - 7) for i in range(n + 1)]]
    p.append('<polyline points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + f'" fill="none" stroke="{LIGHT}" stroke-width="{width}"/>')
    p.append(f'<line x1="{x1+ux*(L-9):.1f}" y1="{y1+uy*(L-9):.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{LIGHT}" stroke-width="{width}" marker-end="url(#ph)"/>')

# ---------- left: reflection ----------
p.append(f'<rect x="6" y="8" width="226" height="320" rx="8" fill="#f5f7fa"/>')
p.append(f'<text x="18" y="30" font-size="12" font-weight="700" fill="{TEXT}">Not absorbed: reflection</text>')
p.append(f'<text x="18" y="45" font-size="10.5" fill="{MUTED}">(details in Chapter 6)</text>')
sy = 186
p.append(f'<rect x="18" y="{sy}" width="202" height="46" fill="{MATTER}" stroke="{MSTROKE}" stroke-width="1"/>')
p.append(f'<line x1="119" y1="{sy-70}" x2="119" y2="{sy}" stroke="{GRID}" stroke-width="1" stroke-dasharray="3 3"/>')
photon(36, 76, 112, sy - 6)
photon(126, sy - 6, 202, 76)
for x in (60, 90, 120, 150, 180):
    p.append(f'<line x1="{x-7}" y1="{sy+10}" x2="{x+7}" y2="{sy+10}" stroke="{ELEC}" stroke-width="1.3" marker-start="url(#dbl)" marker-end="url(#dbl)"/>')
    p.append(f'<circle cx="{x}" cy="{sy+10}" r="3.2" fill="{ELEC}"/>')
for i, t in enumerate(["Surface electrons are shaken in", "step by the wave and re-radiate", "together: one beam, at the mirror", "angle, no delay, same color.",
                       "", "The energy is passed straight", "back out; nothing is kept."]):
    p.append(f'<text x="18" y="{252+i*13}" font-size="10.3" fill="{TEXT if i < 4 else MUTED}">{t}</text>')

# ---------- right: absorbed ----------
p.append(f'<text x="250" y="30" font-size="12" font-weight="700" fill="{TEXT}">Absorbed: a photon with the right energy</text>')
p.append(f'<text x="250" y="45" font-size="10.5" fill="{MUTED}">is swallowed whole. Then its energy has three possible fates.</text>')
ax, ay = 300, 186
photon(242, ay, ax - 26, ay)
p.append(f'<circle cx="{ax}" cy="{ay}" r="24" fill="{ELEC}" opacity="0.18"/>')
p.append(f'<circle cx="{ax}" cy="{ay}" r="4" fill="{NUC}"/>')
p.append(f'<circle cx="{ax+12}" cy="{ay-14}" r="4.5" fill="{ELEC}"/>')
p.append(f'<text x="{ax}" y="{ay+40}" font-size="10.5" font-weight="700" fill="{TEXT}" text-anchor="middle">excited</text>')
p.append(f'<text x="{ax}" y="{ay+53}" font-size="10.5" font-weight="700" fill="{TEXT}" text-anchor="middle">atom or</text>')
p.append(f'<text x="{ax}" y="{ay+66}" font-size="10.5" font-weight="700" fill="{TEXT}" text-anchor="middle">molecule</text>')

boxes = [
    (62, "1  Re-emitted as light", ["A new photon leaves after ~ns, in a", "random direction, out of step with", "the original. Common in thin gases."], "light"),
    (152, "2  Turned into heat", ["Collisions or atomic vibrations steal", "the energy first: it becomes random", "jiggling, i.e. higher temperature."], "heat"),
    (242, "3  Drives chemistry", ["The energy breaks or rearranges a bond:", "photosynthesis, vision, sunburn,", "fading of dyes (Chapters 7 and 10)."], "chem"),
]
bx0 = 372
for y, title, lines, icon in boxes:
    p.append(f'<rect x="{bx0}" y="{y}" width="{W-bx0-6}" height="80" rx="8" fill="#f5f7fa"/>')
    p.append(f'<line x1="{ax+26}" y1="{ay + (y+40-ay)*0.12:.1f}" x2="{bx0-4}" y2="{y+40}" stroke="{MUTED}" stroke-width="1.4" marker-end="url(#gr)"/>')
    p.append(f'<text x="{bx0+52}" y="{y+20}" font-size="11.5" font-weight="700" fill="{TEXT}">{title}</text>')
    for i, t in enumerate(lines):
        p.append(f'<text x="{bx0+52}" y="{y+37+i*13}" font-size="10.3" fill="{TEXT}">{t}</text>')
    ix, iy = bx0 + 24, y + 40
    if icon == "light":
        p.append(f'<circle cx="{ix-6}" cy="{iy+8}" r="6" fill="{ELEC}" opacity="0.3"/>')
        photon(ix - 2, iy + 4, ix + 16, iy - 22, wl=7, amp=2.6, width=1.6)
    elif icon == "heat":
        for dx, dy in ((-12, -12), (0, -12), (12, -12), (-12, 0), (0, 0), (12, 0), (-12, 12), (0, 12), (12, 12)):
            p.append(f'<circle cx="{ix+dx}" cy="{iy+dy}" r="3.6" fill="{MSTROKE}"/>')
        p.append(f'<path d="M{ix-20} {iy-20} q3 -4 6 0 t6 0" fill="none" stroke="{BAD}" stroke-width="1.3"/>')
        p.append(f'<path d="M{ix+8} {iy+20} q3 -4 6 0 t6 0" fill="none" stroke="{BAD}" stroke-width="1.3"/>')
    else:
        p.append(f'<circle cx="{ix-12}" cy="{iy}" r="6" fill="{MSTROKE}"/><circle cx="{ix+12}" cy="{iy-6}" r="6" fill="{MSTROKE}"/>')
        p.append(f'<line x1="{ix-6}" y1="{iy-1}" x2="{ix-1}" y2="{iy-3}" stroke="{TEXT}" stroke-width="2"/>')
        p.append(f'<line x1="{ix+2}" y1="{iy-4}" x2="{ix+6}" y2="{iy-5}" stroke="{TEXT}" stroke-width="2"/>')
p.append("</svg>")
OUT.write_text("\n".join(p))
print("wrote", OUT)
