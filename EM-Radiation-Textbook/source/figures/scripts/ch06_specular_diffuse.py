"""Figure 6.3 - specular vs diffuse reflection. Each ray obeys the law of reflection about the
LOCAL surface normal. Writes figures/ch06-specular-diffuse.svg."""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "ch06-specular-diffuse.svg"
AMBER, TEXT, MUTED, FILL, STROKE = "#e09f1f", "#1f2933", "#52606d", "#d9dee5", "#52606d"
W, H = 680, 300
els = []


def text(x, y, s, size=12, color=TEXT, anchor="start", weight=400, italic=False):
    st = ' font-style="italic"' if italic else ""
    els.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{color}" text-anchor="{anchor}" '
               f'font-weight="{weight}"{st}>{s}</text>')


def head(x, y, ux, uy, color, size):
    px, py = -uy, ux
    b1 = (x - size * ux + 0.55 * size * px, y - size * uy + 0.55 * size * py)
    b2 = (x - size * ux - 0.55 * size * px, y - size * uy - 0.55 * size * py)
    els.append(f'<polygon points="{x:.1f},{y:.1f} {b1[0]:.1f},{b1[1]:.1f} {b2[0]:.1f},{b2[1]:.1f}" fill="{color}"/>')


def ray(x1, y1, x2, y2, color=AMBER, w=2.2, mid=False):
    L = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    if mid:
        els.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{w}"/>')
        head((x1 + x2) / 2 + 5 * ux, (y1 + y2) / 2 + 5 * uy, ux, uy, color, 9)
    else:
        els.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2 - 5*ux:.1f}" y2="{y2 - 5*uy:.1f}" stroke="{color}" stroke-width="{w}"/>')
        head(x2, y2, ux, uy, color, 9)


d_in = (math.sqrt(0.5), math.sqrt(0.5))  # 45 degrees, travelling down-right

# ---------- (a) smooth ----------
text(16, 22, "(a) Specular reflection: smooth surface", 13.5, TEXT, weight=650)
SY = 205
els.append(f'<rect x="20" y="{SY}" width="300" height="32" fill="{FILL}"/>')
els.append(f'<line x1="20" y1="{SY}" x2="320" y2="{SY}" stroke="{STROKE}" stroke-width="1.5"/>')
for hx in (120, 160, 200):
    L = 118
    ray(hx - L * d_in[0], SY - L * d_in[1], hx, SY, mid=True)
    ray(hx, SY, hx + L * d_in[0], SY - L * d_in[1])
els.append(f'<line x1="160" y1="{SY}" x2="160" y2="{SY-112}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="4 4"/>')
# angle arcs at the middle hit
r = 34
a1 = (160 - r * math.sin(math.radians(45)), SY - r * math.cos(math.radians(45)))
els.append(f'<path d="M160,{SY - r} A{r},{r} 0 0 0 {a1[0]:.1f},{a1[1]:.1f}" fill="none" stroke="{TEXT}" stroke-width="1.1"/>')
a2 = (160 + r * math.sin(math.radians(45)), SY - r * math.cos(math.radians(45)))
els.append(f'<path d="M160,{SY - r} A{r},{r} 0 0 1 {a2[0]:.1f},{a2[1]:.1f}" fill="none" stroke="{TEXT}" stroke-width="1.1"/>')
text(147, SY - 40, "θᵢ", 13, TEXT, "end", italic=False)
text(173, SY - 40, "θᵣ", 13, TEXT, "start")
text(166, SY - 100, "normal", 11, MUTED)
text(20, 262, "mirror, still water, polished metal:", 12, TEXT, weight=600)
text(20, 278, "rays leave parallel, so an image survives", 12, MUTED)

# ---------- (b) rough ----------
text(356, 22, "(b) Diffuse reflection: rough surface", 13.5, TEXT, weight=650)
# rough profile: "hit" facets whose tilts send rays into a fan, joined by connector facets
# reflected angle from vertical = 45 deg - 2*tilt, so tilts 40, 27, 15, 3, -8 give -35..60 deg
hit_tilts = [27, -8, 40, 15, 3]
prof = [(364.0, 212.0)]
hits = []
for k, sl in enumerate(hit_tilts):
    # short lead-in facet
    x, y = prof[-1]
    prof.append((x + 18, 212.0 + (6 if k % 2 else -4)))
    x, y = prof[-1]
    dx = 20
    p1 = (x + dx, y - dx * math.tan(math.radians(sl)))
    hits.append((len(prof) - 1))
    prof.append(p1)
    # connector back toward the baseline
    x, y = prof[-1]
    prof.append((x + 22, 212.0 + (-3 if k % 2 else 5)))
x, y = prof[-1]
prof.append((662.0, y))
poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in prof) + f" 662,237 364,237"
els.append(f'<polygon points="{poly}" fill="{FILL}"/>')
els.append('<polyline points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in prof) + f'" fill="none" stroke="{STROKE}" stroke-width="1.5"/>')


def seg_hit(seg_i, frac=0.5):
    (x0, y0), (x1, y1) = prof[seg_i], prof[seg_i + 1]
    hx, hy = x0 + frac * (x1 - x0), y0 + frac * (y1 - y0)
    tx, ty = (x1 - x0), (y1 - y0)
    L = math.hypot(tx, ty)
    nx, ny = ty / L, -tx / L
    if ny > 0:
        nx, ny = -nx, -ny
    return hx, hy, nx, ny


for seg_i in hits:
    hx, hy, nx, ny = seg_hit(seg_i)
    L = 104
    ray(hx - L * d_in[0], hy - L * d_in[1], hx, hy, mid=True)
    dot = d_in[0] * nx + d_in[1] * ny
    rx, ry = d_in[0] - 2 * dot * nx, d_in[1] - 2 * dot * ny
    assert ry < 0, (seg_i, rx, ry)
    Lr = 66
    ray(hx, hy, hx + Lr * rx, hy + Lr * ry)
    els.append(f'<line x1="{hx:.1f}" y1="{hy:.1f}" x2="{hx + 20*nx:.1f}" y2="{hy + 20*ny:.1f}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="3 3"/>')
text(360, 262, "paper, matte paint, chalk, frosted glass:", 12, TEXT, weight=600)
text(360, 278, "each ray still obeys θᵢ = θᵣ about its local", 12, MUTED)
text(360, 294, "normal (gray), but the rays fan out: no image", 12, MUTED)

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
       f'font-family="Inter, sans-serif">\n<rect width="{W}" height="{H}" fill="#ffffff"/>\n'
       + "\n".join(els) + "\n</svg>\n")
OUT.write_text(svg)
print("wrote", OUT)
