"""Figure 6.8 - why the same oxide (Al2O3) can be transparent, translucent, or opaque:
single crystal vs dense polycrystal (birefringent grains in random orientations) vs porous
polycrystal. Schematic. Writes figures/ch06-ceramic-opacity.svg."""
import math
import random
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "ch06-ceramic-opacity.svg"
AMBER, TEXT, MUTED, STROKE = "#e09f1f", "#1f2933", "#52606d", "#52606d"
GRAIN, HATCH = "#d9dee5", "#aab4bf"
W, H = 680, 262
BW, BH, Y0 = 176, 150, 62
XS = (22, 252, 482)
els, defs = [], []
random.seed(7)


def text(x, y, s, size=12, color=TEXT, anchor="start", weight=400):
    els.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{color}" text-anchor="{anchor}" '
               f'font-weight="{weight}">{s}</text>')


def head(x, y, ux, uy, color, size):
    px, py = -uy, ux
    b1 = (x - size * ux + 0.55 * size * px, y - size * uy + 0.55 * size * py)
    b2 = (x - size * ux - 0.55 * size * px, y - size * uy - 0.55 * size * py)
    els.append(f'<polygon points="{x:.1f},{y:.1f} {b1[0]:.1f},{b1[1]:.1f} {b2[0]:.1f},{b2[1]:.1f}" fill="{color}"/>')


def arrow(pts, w=2.4, color=AMBER, op=1.0, size=9):
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    els.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round" opacity="{op}"/>')
    (xa, ya), (xb, yb) = pts[-2], pts[-1]
    L = math.hypot(xb - xa, yb - ya)
    head(xb + 3 * (xb - xa) / L, yb + 3 * (yb - ya) / L, (xb - xa) / L, (yb - ya) / L, color, size)


def clip_halfplane(poly, a, b, c):
    """Keep points with a*x + b*y <= c (Sutherland-Hodgman)."""
    out = []
    for i in range(len(poly)):
        P, Q = poly[i], poly[(i + 1) % len(poly)]
        fp, fq = a * P[0] + b * P[1] - c, a * Q[0] + b * Q[1] - c
        if fp <= 0:
            out.append(P)
        if fp * fq < 0:
            t = fp / (fp - fq)
            out.append((P[0] + t * (Q[0] - P[0]), P[1] + t * (Q[1] - P[1])))
    return out


def voronoi(x0, y0, w, h, n):
    seeds = []
    while len(seeds) < n:
        p = (x0 + random.uniform(4, w - 4), y0 + random.uniform(4, h - 4))
        if all(math.hypot(p[0] - q[0], p[1] - q[1]) > 26 for q in seeds):
            seeds.append(p)
    cells = []
    for i, s in enumerate(seeds):
        poly = [(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h)]
        for j, t in enumerate(seeds):
            if i == j:
                continue
            a, b = t[0] - s[0], t[1] - s[1]
            c = (t[0] ** 2 + t[1] ** 2 - s[0] ** 2 - s[1] ** 2) / 2
            poly = clip_halfplane(poly, a, b, c)
        cells.append(poly)
    return cells


def lattice_hatch(clip_id, x0, y0, w, h, ang, spacing=7):
    """Parallel lines at angle ang (deg), clipped by clip_id: stands for a crystal orientation."""
    cx, cy = x0 + w / 2, y0 + h / 2
    R = math.hypot(w, h)
    ux, uy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    px, py = -uy, ux
    lines = []
    k = -R
    while k <= R:
        ax, ay = cx + k * px - R * ux, cy + k * py - R * uy
        bx, by = cx + k * px + R * ux, cy + k * py + R * uy
        lines.append(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{bx:.1f}" y2="{by:.1f}"/>')
        k += spacing
    return f'<g clip-path="url(#{clip_id})" stroke="{HATCH}" stroke-width="0.9">' + "".join(lines) + "</g>"


titles = [("Single crystal", "(sapphire)"), ("Dense polycrystal", "(fully dense alumina)"),
          ("Porous polycrystal", "(alumina, ~5% pores)")]
results = [("transparent", "no internal boundaries"), ("translucent", "light deflected at each grain boundary"),
           ("opaque, white", "many pores scatter light every way")]
YM = Y0 + BH / 2

for k, x0 in enumerate(XS):
    text(x0 + BW / 2, 24, titles[k][0], 13, TEXT, "middle", 650)
    text(x0 + BW / 2, 40, titles[k][1], 11.5, MUTED, "middle")
    if k == 0:
        cid = "c0"
        defs.append(f'<clipPath id="{cid}"><rect x="{x0}" y="{Y0}" width="{BW}" height="{BH}"/></clipPath>')
        els.append(f'<rect x="{x0}" y="{Y0}" width="{BW}" height="{BH}" fill="{GRAIN}"/>')
        els.append(lattice_hatch(cid, x0, Y0, BW, BH, 30))
    else:
        cells = voronoi(x0, Y0, BW, BH, 15)
        for j, poly in enumerate(cells):
            cid = f"c{k}_{j}"
            pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in poly)
            defs.append(f'<clipPath id="{cid}"><polygon points="{pts}"/></clipPath>')
            els.append(f'<polygon points="{pts}" fill="{GRAIN}"/>')
            els.append(lattice_hatch(cid, x0, Y0, BW, BH, random.uniform(0, 180)))
            els.append(f'<polygon points="{pts}" fill="none" stroke="{STROKE}" stroke-width="1.1"/>')
        if k == 2:
            pores = []
            for poly in cells:
                for (x, y) in poly[:: max(1, len(poly) // 3)]:
                    if x0 + 6 < x < x0 + BW - 6 and Y0 + 6 < y < Y0 + BH - 6 and random.random() < 0.75:
                        pores.append((x, y))
            for (x, y) in pores:
                els.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{random.uniform(3.2, 5.2):.1f}" fill="#ffffff" stroke="{STROKE}" stroke-width="1"/>')
    els.append(f'<rect x="{x0}" y="{Y0}" width="{BW}" height="{BH}" fill="none" stroke="{STROKE}" stroke-width="1.3"/>')
    text(x0 + BW / 2, Y0 + BH + 24, results[k][0], 13, TEXT, "middle", 700)
    text(x0 + BW / 2, Y0 + BH + 40, results[k][1], 11.5, MUTED, "middle")

# beams
x0 = XS[0]
arrow([(x0 - 14, YM), (x0 + BW + 14, YM)], w=4.5)
x0 = XS[1]
zig = [(x0 - 14, YM), (x0 + 30, YM), (x0 + 60, YM - 6), (x0 + 92, YM + 3), (x0 + 122, YM - 4), (x0 + 150, YM + 6), (x0 + BW + 14, YM + 9)]
arrow(zig, w=3)
for (sx, sy), ang in (((x0 + 60, YM - 6), -60), ((x0 + 92, YM + 3), 115), ((x0 + 122, YM - 4), -125), ((x0 + 150, YM + 6), 60)):
    a = math.radians(ang)
    arrow([(sx, sy), (sx + 24 * math.cos(a), sy + 24 * math.sin(a))], w=1.4, size=7, op=0.9)
x0 = XS[2]
arrow([(x0 - 14, YM), (x0 + 34, YM)], w=4.5)
for ang, L in ((-155, 40), (-100, 50), (-40, 52), (12, 60), (65, 52), (115, 50), (160, 36), (-12, 112)):
    a = math.radians(ang)
    w = 1.4 if L < 100 else 1.2
    arrow([(x0 + 34, YM), (x0 + 34 + L * math.cos(a), YM + L * math.sin(a))], w=w, size=7, op=0.9)

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
       f'font-family="Inter, sans-serif">\n<defs>' + "".join(defs) + f'</defs>\n<rect width="{W}" height="{H}" fill="#ffffff"/>\n'
       + "\n".join(els) + "\n</svg>\n")
OUT.write_text(svg)
print("wrote", OUT)
