"""Figure 6.6 - dispersion. (a) a prism, ray-traced with an EXAGGERATED n(lambda) so the fan is
visible; (b) a raindrop, ray-traced with water's real indices (n = 1.331 red, 1.343 violet) at the
minimum-deviation (rainbow) ray, giving exit angles of about 42.4 and 40.7 degrees.
Writes figures/ch06-prism-rainbow.svg."""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "ch06-prism-rainbow.svg"
TEXT, MUTED, FILL, STROKE, WHITE_BEAM = "#1f2933", "#52606d", "#d9dee5", "#52606d", "#9aa5b1"
W, H = 680, 330
els = []


def spectral(lam):
    """Approximate sRGB hex for a wavelength in nm (Bruton-style piecewise ramp)."""
    if lam < 440: r, g, b = -(lam - 440) / 60, 0, 1
    elif lam < 490: r, g, b = 0, (lam - 440) / 50, 1
    elif lam < 510: r, g, b = 0, 1, -(lam - 510) / 20
    elif lam < 580: r, g, b = (lam - 510) / 70, 1, 0
    elif lam < 645: r, g, b = 1, -(lam - 645) / 65, 0
    else: r, g, b = 1, 0, 0
    f = 0.3 + 0.7 * (lam - 380) / 40 if lam < 420 else (0.3 + 0.7 * (780 - lam) / 80 if lam > 700 else 1)
    c = [int(round(255 * (max(0, v) * f) ** 0.8)) for v in (r, g, b)]
    # darken slightly so thin lines read on white
    c = [int(v * 0.88) for v in c]
    return "#%02x%02x%02x" % tuple(c)


def text(x, y, s, size=12, color=TEXT, anchor="start", weight=400):
    els.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{color}" text-anchor="{anchor}" '
               f'font-weight="{weight}">{s}</text>')


def head(x, y, ux, uy, color, size):
    px, py = -uy, ux
    b1 = (x - size * ux + 0.55 * size * px, y - size * uy + 0.55 * size * py)
    b2 = (x - size * ux - 0.55 * size * px, y - size * uy - 0.55 * size * py)
    els.append(f'<polygon points="{x:.1f},{y:.1f} {b1[0]:.1f},{b1[1]:.1f} {b2[0]:.1f},{b2[1]:.1f}" fill="{color}"/>')


def dot(a, b): return a[0] * b[0] + a[1] * b[1]
def add(a, b, s=1.0): return (a[0] + s * b[0], a[1] + s * b[1])
def norm(a):
    L = math.hypot(*a); return (a[0] / L, a[1] / L)


def refract(d, nrm, n1, n2):
    """d: unit direction; nrm: unit normal pointing back toward the incoming side."""
    cosi = -dot(nrm, d)
    eta = n1 / n2
    k = 1 - eta * eta * (1 - cosi * cosi)
    if k < 0:
        return None
    return norm(add((eta * d[0], eta * d[1]), nrm, eta * cosi - math.sqrt(k)))


def reflect(d, nrm):
    return norm(add(d, nrm, -2 * dot(d, nrm)))


def seg_intersect(p, d, a, b):
    """Ray p + t d with segment ab; returns point or None."""
    ex, ey = b[0] - a[0], b[1] - a[1]
    den = d[0] * (-ey) - d[1] * (-ex)
    if abs(den) < 1e-12: return None
    rx, ry = a[0] - p[0], a[1] - p[1]
    t = (rx * (-ey) - ry * (-ex)) / den
    u = (d[0] * ry - d[1] * rx) / den
    if t > 1e-6 and -1e-9 <= u <= 1 + 1e-9:
        return (p[0] + t * d[0], p[1] + t * d[1])
    return None


# ---------------- (a) prism ----------------
text(16, 22, "(a) Prism: n depends on wavelength", 13.5, TEXT, weight=650)
T, BL, BR = (160, 62), (60, 62 + 173.2), (260, 62 + 173.2)
els.append(f'<polygon points="{T[0]},{T[1]} {BL[0]},{BL[1]:.1f} {BR[0]},{BR[1]:.1f}" fill="#e6ebf1" stroke="{STROKE}" stroke-width="1.4"/>')
M = ((BL[0] + T[0]) / 2, (BL[1] + T[1]) / 2)
n_left_out = (-math.cos(math.radians(30)), -0.5)      # outward normal, left face
n_right_out = (math.cos(math.radians(30)), -0.5)      # outward normal, right face


def n_prism(lam):  # EXAGGERATED dispersion (Cauchy form) so the colors separate on paper
    A, B = 1.535, 0.030
    return A + B / (lam / 1000) ** 2


i_mid = math.asin(n_prism(550) * 0.5)
a_in = math.radians(30) - i_mid
d_in = (math.cos(a_in), math.sin(a_in))
start = add(M, d_in, -100)
els.append(f'<line x1="{start[0]:.1f}" y1="{start[1]:.1f}" x2="{M[0]:.1f}" y2="{M[1]:.1f}" stroke="{WHITE_BEAM}" stroke-width="4" stroke-linecap="round"/>')
mid = add(M, d_in, -55)
head(mid[0], mid[1], d_in[0], d_in[1], WHITE_BEAM, 12)
ang_in = math.degrees(math.atan2(d_in[1], d_in[0]))
lab = add(add(M, d_in, -62), (d_in[1], -d_in[0]), 10)
els.append(f'<text x="{lab[0]:.1f}" y="{lab[1]:.1f}" font-size="12" fill="{TEXT}" font-weight="600" text-anchor="middle" '
           f'transform="rotate({ang_in:.1f} {lab[0]:.1f} {lab[1]:.1f})">white light</text>')
lams = [400 + 10 * k for k in range(31)]
exits = []
for lam in lams:
    n = n_prism(lam)
    d1 = refract(d_in, n_left_out, 1.0, n)
    P2 = seg_intersect(M, d1, T, BR)
    d2 = refract(d1, (-n_right_out[0], -n_right_out[1]), n, 1.0)
    exits.append((lam, P2, d2, d1))
Lout = 112
for (l1, p1, e1, _), (l2, p2, e2, _) in zip(exits[:-1], exits[1:]):
    q1, q2 = add(p1, e1, Lout), add(p2, e2, Lout)
    col = spectral((l1 + l2) / 2)
    els.append(f'<polygon points="{p1[0]:.1f},{p1[1]:.1f} {q1[0]:.1f},{q1[1]:.1f} {q2[0]:.1f},{q2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="{col}" stroke="{col}" stroke-width="0.6"/>')
# inside: thin red and violet paths
for lam in (400, 700):
    e = [x for x in exits if x[0] == lam][0]
    els.append(f'<line x1="{M[0]:.1f}" y1="{M[1]:.1f}" x2="{e[1][0]:.1f}" y2="{e[1][1]:.1f}" stroke="{spectral(lam)}" stroke-width="1.4"/>')
red, vio = exits[-1], exits[0]
qr, qv = add(red[1], red[2], Lout + 6), add(vio[1], vio[2], Lout + 6)
text(qr[0] + 2, qr[1] - 2, "red", 12, TEXT, weight=600)
text(qv[0] - 4, qv[1] + 14, "violet", 12, TEXT, weight=600)
text(160, 222, "glass", 12, MUTED, "middle")
text(16, 284, "n is larger for shorter wavelengths, so", 12, MUTED)
text(16, 300, "violet bends most. (Spread exaggerated", 12, MUTED)
text(16, 316, "for clarity; real glass fans less.)", 12, MUTED)

# divider
els.append(f'<line x1="372" y1="36" x2="372" y2="320" stroke="#d9dee5" stroke-width="1.2"/>')

# ---------------- (b) raindrop ----------------
text(388, 22, "(b) Raindrop: the primary rainbow", 13.5, TEXT, weight=650)
C, R = (470.0, 128.0), 70.0
els.append(f'<circle cx="{C[0]}" cy="{C[1]}" r="{R}" fill="#e3eef8" stroke="{STROKE}" stroke-width="1.3"/>')


def circle_hit(p, d):
    fx, fy = p[0] - C[0], p[1] - C[1]
    b = 2 * (d[0] * fx + d[1] * fy); c = fx * fx + fy * fy - R * R
    t = (-b + math.sqrt(b * b - 4 * c)) / 2
    return (p[0] + t * d[0], p[1] + t * d[1])


def mx(p):  # mirror left-right about the drop center (sunlight then travels right-to-left)
    return (2 * C[0] - p[0], p[1])


paths = {}
for lam, n in ((700, 1.331), (400, 1.343)):
    i = math.acos(math.sqrt((n * n - 1) / 3))        # minimum-deviation incidence angle
    P1 = (C[0] - R * math.cos(i), C[1] - R * math.sin(i))
    nrm = norm((P1[0] - C[0], P1[1] - C[1]))
    d1 = refract((1.0, 0.0), nrm, 1.0, n)
    P2 = circle_hit(P1, d1)
    n2 = norm((P2[0] - C[0], P2[1] - C[1]))
    d2 = reflect(d1, n2)
    P3 = circle_hit(P2, d2)
    n3 = norm((P3[0] - C[0], P3[1] - C[1]))
    d3 = refract(d2, (-n3[0], -n3[1]), n, 1.0)
    ang = math.degrees(math.atan2(d3[1], -d3[0]))     # angle below the antisolar direction
    paths[lam] = (mx(P1), mx(P2), mx(P3), (-d3[0], d3[1]), ang)
    print(lam, "exit angle", round(ang, 2))

P1r = paths[700][0]
els.append(f'<line x1="672" y1="{P1r[1]:.1f}" x2="{P1r[0]:.1f}" y2="{P1r[1]:.1f}" stroke="{WHITE_BEAM}" stroke-width="3.5"/>')
head(612, P1r[1], -1, 0, WHITE_BEAM, 11)
text(670, P1r[1] - 9, "sunlight", 12, TEXT, "end", 600)
for lam in (700, 400):
    P1, P2, P3, d3, ang = paths[lam]
    col = spectral(lam)
    els.append(f'<polyline points="{P1[0]:.1f},{P1[1]:.1f} {P2[0]:.1f},{P2[1]:.1f} {P3[0]:.1f},{P3[1]:.1f}" fill="none" stroke="{col}" stroke-width="1.6"/>')
    E = add(P3, d3, 128)
    els.append(f'<line x1="{P3[0]:.1f}" y1="{P3[1]:.1f}" x2="{E[0]:.1f}" y2="{E[1]:.1f}" stroke="{col}" stroke-width="2.2"/>')
    head(E[0] + 3 * d3[0], E[1] + 3 * d3[1], d3[0], d3[1], col, 9)
P3r = paths[700][2]
els.append(f'<line x1="{P3r[0]:.1f}" y1="{P3r[1]:.1f}" x2="{P3r[0] + 150:.1f}" y2="{P3r[1]:.1f}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="4 4"/>')
rr = 70
a_r = math.radians(paths[700][4])
end_r = (P3r[0] + rr * math.cos(a_r), P3r[1] + rr * math.sin(a_r))
els.append(f'<path d="M{P3r[0] + rr:.1f},{P3r[1]:.1f} A{rr},{rr} 0 0 1 {end_r[0]:.1f},{end_r[1]:.1f}" fill="none" stroke="{TEXT}" stroke-width="1.1"/>')
text(P3r[0] + rr + 14, P3r[1] + 22, f"red: {round(paths[700][4] + 1e-6, 1)}°", 12, TEXT, "start", 600)
text(P3r[0] + rr + 14, P3r[1] + 37, f"violet: {round(paths[400][4] + 1e-6, 1)}°", 12, TEXT, "start", 600)
text(C[0] - R - 6, C[1] - 6, "one internal", 11.5, MUTED, "end")
text(C[0] - R - 6, C[1] + 8, "reflection", 11.5, MUTED, "end")
text(388, 300, "Angles from the antisolar direction (dashed);", 12, MUTED)
text(388, 316, "water: n = 1.331 (red), 1.343 (violet)", 12, MUTED)

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
       f'font-family="Inter, sans-serif">\n<rect width="{W}" height="{H}" fill="#ffffff"/>\n'
       + "\n".join(els) + "\n</svg>\n")
OUT.write_text(svg)
print("wrote", OUT)
