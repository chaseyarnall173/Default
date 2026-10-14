"""Figure 6.5 - (a) rays leaving glass (n = 1.50) for air at increasing angles: refraction, the
critical angle (41.8 deg), total internal reflection. (b) an optical fiber guiding light by TIR.
Writes figures/ch06-tir-fiber.svg."""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "ch06-tir-fiber.svg"
AMBER, TEXT, MUTED, FILL, STROKE = "#e09f1f", "#1f2933", "#52606d", "#d9dee5", "#52606d"
W, H = 680, 420
n = 1.50
tc = math.degrees(math.asin(1 / n))
els = []


def text(x, y, s, size=12, color=TEXT, anchor="start", weight=400):
    els.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{color}" text-anchor="{anchor}" '
               f'font-weight="{weight}">{s}</text>')


def head(x, y, ux, uy, color, size):
    px, py = -uy, ux
    b1 = (x - size * ux + 0.55 * size * px, y - size * uy + 0.55 * size * py)
    b2 = (x - size * ux - 0.55 * size * px, y - size * uy - 0.55 * size * py)
    els.append(f'<polygon points="{x:.1f},{y:.1f} {b1[0]:.1f},{b1[1]:.1f} {b2[0]:.1f},{b2[1]:.1f}" fill="{color}"/>')


def ray(x1, y1, x2, y2, w=2.2, op=1.0, arrow_at=0.55, end_arrow=False, color=AMBER):
    L = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    els.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{w}" opacity="{op}" stroke-linecap="round"/>')
    if end_arrow:
        head(x2 + 4 * ux, y2 + 4 * uy, ux, uy, color, 9)
    elif arrow_at:
        head(x1 + arrow_at * L * ux + 4 * ux, y1 + arrow_at * L * uy + 4 * uy, ux, uy, color, 9)


# ---------------- (a) ----------------
text(16, 22, f"(a) Leaving glass for air: past the critical angle, nothing gets out", 13.5, TEXT, weight=650)
YI = 92
els.append(f'<rect x="20" y="{YI}" width="400" height="128" fill="{FILL}"/>')
els.append(f'<line x1="20" y1="{YI}" x2="420" y2="{YI}" stroke="{STROKE}" stroke-width="1.5"/>')
text(26, YI - 8, "air (n = 1.00)", 12, MUTED)
text(26, 210, "glass (n = 1.50)", 12, MUTED)
S = (138, 212)
els.append(f'<circle cx="{S[0]}" cy="{S[1]}" r="4.5" fill="{AMBER}"/>')
D = S[1] - YI
for k, th in enumerate((25.0, tc, 60.0)):
    t = math.radians(th)
    hx = S[0] + D * math.tan(t)
    ray(S[0], S[1], hx, YI, w=2.2)
    els.append(f'<line x1="{hx:.1f}" y1="{YI - 6}" x2="{hx:.1f}" y2="{YI + 34}" stroke="{MUTED}" stroke-width="0.9" stroke-dasharray="3 3"/>')
    if k == 0:
        t2 = math.asin(n * math.sin(t))
        ray(hx, YI, hx + 64 * math.sin(t2), YI - 64 * math.cos(t2), w=2.2, end_arrow=True)
        ray(hx, YI, hx + 44 * math.sin(t), YI + 44 * math.cos(t), w=1.1, op=0.75, end_arrow=True)
        text(hx + 52, YI - 44, "θ = 25°: refracts out", 11.5, TEXT, weight=600)
        text(hx + 52, YI - 30, "(plus a weak reflection)", 11.5, MUTED)
    elif k == 1:
        els.append(f'<line x1="{hx:.1f}" y1="{YI - 2}" x2="{hx + 80:.1f}" y2="{YI - 2}" stroke="{AMBER}" stroke-width="1.2" opacity="0.8"/>')
        head(hx + 84, YI - 2, 1, 0, AMBER, 8)
        ray(hx, YI, hx + 44 * math.sin(t), YI + 44 * math.cos(t), w=2.0, end_arrow=True)
        text(hx + 8, YI - 9, f"θc = {tc:.1f}°: grazes the surface", 11.5, TEXT, weight=600)
    else:
        ray(hx, YI, hx + 70 * math.sin(t), YI + 70 * math.cos(t), w=2.2, end_arrow=True)
        text(414, YI + 98, "θ = 60°: 100% reflected", 11.5, TEXT, "end", 600)
        text(414, YI + 112, "(total internal reflection)", 11.5, MUTED, "end")

X = 445
text(X, 70, "sin θc = n₂ / n₁", 18, TEXT, weight=700)
for i, s in enumerate(["Only possible going from higher n", "to lower n. For glass into air:",
                       "θc = sin⁻¹(1/1.50) = 41.8°.",
                       "Water: 48.6°.  Diamond: 24.4°."]):
    text(X, 98 + i * 18, s, 12.5, TEXT if i < 3 else MUTED, weight=600 if i == 2 else 400)

els.append(f'<line x1="10" y1="246" x2="670" y2="246" stroke="#d9dee5" stroke-width="1.2"/>')

# ---------------- (b) fiber ----------------
text(16, 272, "(b) Optical fiber: light trapped in the core by repeated total internal reflection", 13.5, TEXT, weight=650)
X0, X1 = 30, 540
yj0, yc0, yk0, yk1, yc1, yj1 = 292, 304, 330, 362, 388, 400
els.append(f'<rect x="{X0}" y="{yj0}" width="{X1-X0}" height="{yj1-yj0}" rx="6" fill="#9aa5b1"/>')
els.append(f'<rect x="{X0}" y="{yc0}" width="{X1-X0}" height="{yc1-yc0}" fill="#e6ebf1"/>')
els.append(f'<rect x="{X0}" y="{yk0}" width="{X1-X0}" height="{yk1-yk0}" fill="#c9d3de"/>')
# zig-zag inside core
y_top, y_bot = yk0 + 1.5, yk1 - 1.5
x = X0 + 6
y = (y_top + y_bot) / 2
pts = [(x, y)]
going_up = True
step = 64
while x < X1 - 10:
    target = y_top if going_up else y_bot
    dx = step * abs(target - y) / (y_bot - y_top)
    if x + dx > X1 - 4:
        f = (X1 - 4 - x) / dx
        pts.append((X1 - 4, y + f * (target - y)))
        break
    x, y = x + dx, target
    pts.append((x, y))
    going_up = not going_up
d = "M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in pts)
els.append(f'<path d="{d}" fill="none" stroke="{AMBER}" stroke-width="2.2" stroke-linejoin="round"/>')
for (xa, ya), (xb, yb) in zip(pts[1::3], pts[2::3]):
    L = math.hypot(xb - xa, yb - ya)
    head((xa + xb) / 2 + 5 * (xb - xa) / L, (ya + yb) / 2 + 5 * (yb - ya) / L, (xb - xa) / L, (yb - ya) / L, AMBER, 8)
text(X1 + 12, (yc0 + yk0) / 2 + 4, "cladding, n ≈ 1.46", 11.5, TEXT)
text(X1 + 12, (yk0 + yk1) / 2 + 4, "core, n ≈ 1.48", 11.5, TEXT, weight=600)
text(X1 + 12, (yk1 + yc1) / 2 + 4, "cladding, n ≈ 1.46", 11.5, TEXT)
text(X1 + 12, yj1 - 1, "jacket", 11.5, MUTED)
text(X0, yj1 + 16, "Angles exaggerated: in a real fiber the guided rays travel within about 9° of the axis.", 11, MUTED)

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
       f'font-family="Inter, sans-serif">\n<rect width="{W}" height="{H}" fill="#ffffff"/>\n'
       + "\n".join(els) + "\n</svg>\n")
OUT.write_text(svg)
print("wrote", OUT, round(tc, 2))
