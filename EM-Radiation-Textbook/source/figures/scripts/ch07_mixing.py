"""Figure 7.2 - additive (light) vs subtractive (ink/pigment/filter) color mixing.
Overlap regions are drawn explicitly with clip paths (no blend modes), so it prints reliably.
Writes figures/ch07-mixing.svg."""
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "ch07-mixing.svg"
TEXT, MUTED = "#1f2933", "#52606d"
W, H = 680, 330
defs, els = [], []
r = 66


def text(x, y, s, size=12, color=TEXT, anchor="middle", weight=400):
    els.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{color}" text-anchor="{anchor}" '
               f'font-weight="{weight}">{s}</text>')


def venn(prefix, centers, singles, pairs, triple):
    (a, b, c) = centers
    for k, (x, y) in zip("abc", centers):
        defs.append(f'<clipPath id="{prefix}{k}"><circle cx="{x}" cy="{y}" r="{r}"/></clipPath>')
    for (x, y), col in zip(centers, singles):
        els.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{col}"/>')
    for (i, j), col in pairs.items():
        x, y = centers[j]
        els.append(f'<g clip-path="url(#{prefix}{"abc"[i]})"><circle cx="{x}" cy="{y}" r="{r}" fill="{col}"/></g>')
    x, y = centers[2]
    els.append(f'<g clip-path="url(#{prefix}a)"><g clip-path="url(#{prefix}b)"><circle cx="{x}" cy="{y}" r="{r}" fill="{triple}"/></g></g>')


import math


def label_points(centers):
    cx = sum(c[0] for c in centers) / 3; cy = sum(c[1] for c in centers) / 3
    pts = []
    for (x, y) in centers:
        dx, dy = x - cx, y - cy; L = math.hypot(dx, dy)
        pts.append((x + dx / L * 26, y + dy / L * 26))
    pairs = {}
    for i, j, k in ((0, 1, 2), (1, 2, 0), (0, 2, 1)):
        mx_, my_ = (centers[i][0] + centers[j][0]) / 2, (centers[i][1] + centers[j][1]) / 2
        dx, dy = mx_ - centers[k][0], my_ - centers[k][1]; L = math.hypot(dx, dy)
        pairs[(i, j)] = (mx_ + dx / L * 21, my_ + dy / L * 21)
    return pts, pairs, (cx, cy)


# ---------------- (a) additive ----------------
text(170, 22, "(a) Additive: mixing light", 13.5, TEXT, weight=650)
els.append('<rect x="22" y="36" width="296" height="222" rx="8" fill="#14181f"/>')
ca = [(136, 120), (204, 120), (170, 179)]
venn("A", ca, ["#e8413c", "#3cbf5a", "#3f63e8"],
     {(0, 1): "#f2e14a", (1, 2): "#55d6ea", (0, 2): "#d653d6"}, "#ffffff")
sp, pp, cc = label_points(ca)
lab = [(sp[0], "red", "#ffffff"), (sp[1], "green", "#ffffff"), (sp[2], "blue", "#ffffff"),
       (pp[(0, 1)], "yellow", TEXT), (pp[(0, 2)], "magenta", TEXT), (pp[(1, 2)], "cyan", TEXT), (cc, "white", TEXT)]
for (x, y), nm, col in lab:
    text(x, y + 4, nm, 11 if nm in ("yellow", "magenta", "cyan", "white") else 12, col, weight=600)
text(170, 280, "Start dark and add light. Screens and stage", 12, MUTED)
text(170, 296, "lights work this way: red + green looks yellow.", 12, MUTED)

# ---------------- (b) subtractive ----------------
text(510, 22, "(b) Subtractive: mixing inks and filters", 13.5, TEXT, weight=650)
els.append('<rect x="362" y="36" width="296" height="222" rx="8" fill="#ffffff" stroke="#c4ccd5"/>')
cb = [(476, 120), (544, 120), (510, 179)]
venn("B", cb, ["#22b5e3", "#e0368f", "#f5dc2a"],
     {(0, 1): "#3446a8", (1, 2): "#e2402d", (0, 2): "#2e9e4a"}, "#1d1f24")
sp, pp, cc = label_points(cb)
lab = [(sp[0], "cyan", TEXT), (sp[1], "magenta", "#ffffff"), (sp[2], "yellow", TEXT),
       (pp[(0, 1)], "blue", "#ffffff"), (pp[(0, 2)], "green", "#ffffff"), (pp[(1, 2)], "red", "#ffffff"), (cc, "black", "#ffffff")]
for (x, y), nm, col in lab:
    text(x, y + 4, nm, 11 if nm in ("blue", "green", "red", "black") else 12, col, weight=600)
text(510, 280, "Start white; each ink removes a band. Cyan absorbs", 12, MUTED)
text(510, 296, "red, magenta absorbs green, yellow absorbs blue.", 12, MUTED)
text(510, 318, "(Real inks are imperfect, so printers add black ink: CMYK.)", 11, MUTED)

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
       f'font-family="Inter, sans-serif">\n<defs>' + "".join(defs) + f'</defs>\n<rect width="{W}" height="{H}" fill="#ffffff"/>\n'
       + "\n".join(els) + "\n</svg>\n")
OUT.write_text(svg)
print("wrote", OUT)
