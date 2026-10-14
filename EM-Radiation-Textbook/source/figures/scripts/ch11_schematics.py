"""Generates the hand-designed SVG schematics for Chapter 11.

  ch11-xray-tube.svg       Figure 11.1  X-ray tube
  ch11-xray-shadow.svg     Figure 11.3  an X-ray image is a shadow
  ch11-bragg.svg           Figure 11.5  Bragg's law geometry (drawn exactly: 2 d sin(theta) = lambda)
  ch11-planes.svg          Figure 11.6  (110) vs (220); why BCC (100) is absent but (200) is not
  ch11-planar-density.svg  Figure 11.7  FCC (100), (110), (111): planar density vs spacing

Run: python3 ch11_schematics.py   (writes into ../)
"""
from pathlib import Path
import math

FIG = Path(__file__).resolve().parents[1]
INK, MUTED, RULE = "#1f2933", "#52606d", "#d9dee5"
EF, BF, LIGHT, ELEC, NUC, MATF, MATS, GREEN = "#d1495b", "#2e6fdb", "#e09f1f", "#12a39a", "#8d5a97", "#d9dee5", "#52606d", "#0b6e4f"
AMBER_TXT = "#a86a12"
FONT = 'font-family="Inter, sans-serif"'


def svg(w, h, body):
    mk = ""
    for mid, col in (("ah", INK), ("ahb", BF), ("ahr", EF), ("ahl", LIGHT), ("ahm", MUTED), ("ahe", ELEC)):
        mk += (f'<marker id="{mid}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" '
               f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{col}"/></marker>\n')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" {FONT}>\n'
            f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n<defs>\n{mk}</defs>\n' + body + '\n</svg>\n')


def text(x, y, s, size=12, fill=INK, anchor="start", weight="normal", style="normal", halo=False):
    h = ' stroke="#ffffff" stroke-width="3.5" stroke-linejoin="round" paint-order="stroke"' if halo else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}" font-style="{style}"{h}>{s}</text>')


def wave(x0, y0, x1, y1, amp=5, wl=12, phase=0.0):
    L = math.hypot(x1 - x0, y1 - y0); ux, uy = (x1 - x0) / L, (y1 - y0) / L
    nx, ny = -uy, ux
    n = max(int(L / 1.5), 2)
    pts = []
    for i in range(n + 1):
        s = L * i / n
        a = amp * math.sin(2 * math.pi * s / wl + phase)
        pts.append(f"{x0 + ux * s + nx * a:.1f},{y0 + uy * s + ny * a:.1f}")
    return " ".join(pts)


def atom(x, y, r=7, fill=MATF, stroke=MATS, op=1.0):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="1.2" opacity="{op}"/>'


# ---------------------------------------------------------------- Figure 11.1
def tube():
    W, H = 680, 320
    b = []
    # envelope
    b.append('<rect x="70" y="70" width="470" height="170" rx="85" fill="#f5f7fa" stroke="#9aa5b1" stroke-width="2"/>')
    b.append(text(305, 92, "vacuum inside the tube", 11, MUTED, "middle"))
    # cathode cup + filament
    b.append('<path d="M118,118 L150,118 L150,132 L136,132 L136,178 L150,178 L150,192 L118,192 Z" fill="#cbd2d9" stroke="#52606d" stroke-width="1.4"/>')
    fil = " ".join(f"{140 + (6 if i % 2 else 0)},{140 + i * 4}" for i in range(9))
    b.append(f'<polyline points="{fil}" fill="none" stroke="{EF}" stroke-width="2"/>')
    b.append(text(98, 266, "hot filament (cathode, −)", 12, INK, "start", "600"))
    b.append(text(98, 281, "boils off electrons", 11, MUTED))
    b.append('<line x1="128" y1="192" x2="128" y2="252" stroke="#52606d" stroke-width="1.4"/>')
    # anode: copper body with angled tungsten target face
    b.append('<path d="M438,112 L560,112 L560,198 L438,198 L462,155 Z" fill="#d08b5b" stroke="#8a4b25" stroke-width="1.4"/>')
    b.append('<path d="M438,112 L462,155 L438,198 L448,198 L470,155 L448,112 Z" fill="#6b7280" stroke="#374151" stroke-width="1"/>')
    b.append('<rect x="560" y="146" width="90" height="18" fill="#d08b5b" stroke="#8a4b25" stroke-width="1.4"/>')
    b.append(text(600, 100, "anode (+)", 12, INK, "middle", "600"))
    b.append(text(600, 115, "metal target", 11, MUTED, "middle"))
    b.append(text(600, 130, "(W, Cu, Mo…)", 11, MUTED, "middle"))
    b.append(text(608, 188, "≈99% of the", 11, EF, "middle", "600"))
    b.append(text(608, 202, "energy → heat", 11, EF, "middle", "600"))
    b.append(text(608, 216, "(cooling needed)", 11, MUTED, "middle"))
    # electron beam
    for dy in (-8, 0, 8):
        b.append(f'<line x1="156" y1="{155 + dy}" x2="{452 - abs(dy) * 0.5:.0f}" y2="{155 + dy * 0.35:.1f}" stroke="{ELEC}" stroke-width="1.6" marker-end="url(#ahe)"/>')
    for x in range(190, 430, 34):
        b.append(f'<circle cx="{x}" cy="155" r="3.2" fill="{ELEC}"/>')
    b.append(text(300, 140, "electrons accelerated across", 11, ELEC, "middle", "600"))
    b.append(text(300, 182, "kinetic energy = eV (e.g. 30 keV at 30 kV)", 11, ELEC, "middle", "600"))
    # high voltage supply on top
    b.append('<polyline points="128,118 128,40 268,40" fill="none" stroke="#52606d" stroke-width="1.4"/>')
    b.append('<polyline points="342,40 500,40 500,112" fill="none" stroke="#52606d" stroke-width="1.4"/>')
    for i, x in enumerate((280, 296, 312, 328)):
        hgt = 22 if i % 2 == 0 else 12
        b.append(f'<line x1="{x}" y1="{40 - hgt / 2}" x2="{x}" y2="{40 + hgt / 2}" stroke="{INK}" stroke-width="2"/>')
    b.append(text(305, 24, "high voltage V (≈20–150 kV)", 12, INK, "middle", "600"))
    b.append(text(262, 58, "−", 13, INK, "middle", "700"))
    b.append(text(350, 58, "+", 13, INK, "middle", "700"))
    # window and X-rays
    b.append('<rect x="416" y="234" width="56" height="10" fill="#fdf3dd" stroke="#e09f1f" stroke-width="1.2"/>')
    for ang in (-28, -8, 12):
        a = math.radians(90 + ang)
        x1, y1 = 456 + 102 * math.cos(a), 168 + 102 * math.sin(a)
        x2, y2 = 456 + 152 * math.cos(a), 168 + 152 * math.sin(a)
        b.append(f'<polyline points="{wave(456 + 22 * math.cos(a), 168 + 22 * math.sin(a), x2, y2, 3.5, 10)}" fill="none" stroke="{LIGHT}" stroke-width="2"/>')
    b.append(text(548, 276, "X-rays (≈1%) leave", 12, AMBER_TXT, "start", "600"))
    b.append(text(548, 291, "through a thin window", 11, MUTED))
    return svg(W, H, "\n".join(b))


# ---------------------------------------------------------------- Figure 11.3
def shadow():
    W, H = 680, 300
    b = []
    S = (46.0, 150.0)
    det_x = 520.0
    arm = (360.0, 150.0, 62.0, 84.0)      # soft tissue ellipse cx, cy, rx, ry
    bone = (352.0, 150.0, 25.0, 29.0)
    metal = (384.0, 104.0, 26.0, 7.0)     # rectangle centre, width, height
    def in_ell(x, y, e):
        return ((x - e[0]) / e[2]) ** 2 + ((y - e[1]) / e[3]) ** 2 <= 1
    def in_rect(x, y, r):
        return abs(x - r[0]) <= r[2] / 2 and abs(y - r[1]) <= r[3] / 2
    def march(yd, n=900):
        """Return path lengths in tissue/bone/metal and first-entry x for bone/metal."""
        Lt = Lb = Lm = 0.0; xb = xm = None
        for i in range(n):
            x = S[0] + (det_x - S[0]) * (i + 0.5) / n
            y = S[1] + (yd - S[1]) * (x - S[0]) / (det_x - S[0])
            ds = (det_x - S[0]) / n
            if in_rect(x, y, metal):
                Lm += ds; xm = xm or x
            elif in_ell(x, y, bone):
                Lb += ds; xb = xb or x
            elif in_ell(x, y, arm):
                Lt += ds
        return Lt, Lb, Lm, xb, xm
    # body
    b.append(f'<ellipse cx="{arm[0]}" cy="{arm[1]}" rx="{arm[2]}" ry="{arm[3]}" fill="#f3d9cc" stroke="#b9826b" stroke-width="1.4"/>')
    b.append(f'<ellipse cx="{bone[0]}" cy="{bone[1]}" rx="{bone[2]}" ry="{bone[3]}" fill="#f2efe6" stroke="#8d8577" stroke-width="2.5"/>')
    b.append(f'<ellipse cx="{bone[0]}" cy="{bone[1]}" rx="11" ry="13" fill="#e8d7b0" stroke="#b5a37a" stroke-width="1"/>')
    b.append(f'<rect x="{metal[0] - metal[2] / 2}" y="{metal[1] - metal[3] / 2}" width="{metal[2]}" height="{metal[3]}" rx="2" fill="#4b5563"/>')
    # rays
    for yd in [16 + 19.1 * k for k in range(15)]:
        Lt, Lb, Lm, xb, xm = march(yd)
        def at(x):
            return S[1] + (yd - S[1]) * (x - S[0]) / (det_x - S[0])
        if Lm > 0:
            b.append(f'<line x1="{S[0]}" y1="{S[1]}" x2="{xm:.1f}" y2="{at(xm):.1f}" stroke="{LIGHT}" stroke-width="1.6"/>')
        elif Lb > 0:
            xe = xb + 0.5 * Lb
            b.append(f'<line x1="{S[0]}" y1="{S[1]}" x2="{xe:.1f}" y2="{at(xe):.1f}" stroke="{LIGHT}" stroke-width="1.6"/>')
            b.append(f'<line x1="{xe:.1f}" y1="{at(xe):.1f}" x2="{det_x}" y2="{yd:.1f}" stroke="{LIGHT}" stroke-width="1" opacity="0.35" stroke-dasharray="3 4"/>')
        elif Lt > 0:
            b.append(f'<line x1="{S[0]}" y1="{S[1]}" x2="{det_x}" y2="{yd:.1f}" stroke="{LIGHT}" stroke-width="1.6" opacity="0.8"/>')
        else:
            b.append(f'<line x1="{S[0]}" y1="{S[1]}" x2="{det_x}" y2="{yd:.1f}" stroke="{LIGHT}" stroke-width="2"/>')
    b.append(f'<circle cx="{S[0]}" cy="{S[1]}" r="8" fill="{LIGHT}" stroke="#fff" stroke-width="2"/>')
    b.append(text(S[0], S[1] + 28, "X-ray", 11, MUTED, "middle"))
    b.append(text(S[0], S[1] + 42, "source", 11, MUTED, "middle"))
    b.append(f'<rect x="{det_x}" y="10" width="12" height="280" fill="#cbd2d9" stroke="#52606d" stroke-width="1"/>')
    b.append(text(det_x + 6, 6 + 0, "", 10))
    # computed image: transmitted intensity -> radiograph grey (more X-rays = darker)
    gx = 560
    stops = []
    for k in range(141):
        yd = 10 + 280 * k / 140
        Lt, Lb, Lm, _, _ = march(yd, 500)
        T = math.exp(-0.006 * Lt - 0.05 * Lb - 2.0 * Lm)
        g = int(round(235 - 205 * T))
        stops.append(f'<stop offset="{k / 140:.4f}" stop-color="rgb({g},{g},{g + 4 if g < 250 else g})"/>')
    b.append(f'<defs><linearGradient id="img" x1="0" y1="0" x2="0" y2="1">{"".join(stops)}</linearGradient></defs>')
    b.append(f'<rect x="{gx}" y="10" width="34" height="280" fill="url(#img)" stroke="#52606d" stroke-width="1"/>')
    b.append(text(gx + 44, 30, "image", 12, INK, "start", "700"))
    b.append(text(gx + 44, 46, "dark: many", 11, MUTED))
    b.append(text(gx + 44, 60, "X-rays arrived", 11, MUTED))
    b.append(text(gx + 44, 146, "white: few", 11, MUTED))
    b.append(text(gx + 44, 160, "arrived", 11, MUTED))
    b.append(text(gx + 44, 174, "(bone, metal)", 11, MUTED))
    # labels
    b.append(text(arm[0], 292, "soft tissue (H, C, N, O): most photons get through", 11, "#8a5a46", "middle", "600", halo=True))
    b.append(text(bone[0] - 6, 202, "bone (Ca, P):", 11, "#5f574a", "middle", "600", halo=True))
    b.append(text(bone[0] - 6, 216, "absorbs strongly", 11, "#5f574a", "middle", halo=True))
    b.append(text(metal[0] + 4, 84, "metal pin: stops nearly all", 11, "#374151", "start", "600", halo=True))
    return svg(W, H, "\n".join(b))


# ---------------------------------------------------------------- Figure 11.5
def bragg():
    W, H = 680, 350
    b = []
    th = math.radians(32)
    d = 100
    lam = 2 * d * math.sin(th)          # exactly n = 1 Bragg condition
    A = (330.0, 175.0); B = (330.0, A[1] + d)
    u = (math.cos(th), math.sin(th))    # incoming direction (right, downward)
    w = (math.cos(th), -math.sin(th))   # outgoing direction (right, upward)
    L = 225.0
    S1 = (A[0] - L * u[0], A[1] - L * u[1]); S2 = (B[0] - (L + d * math.sin(th)) * u[0], B[1] - (L + d * math.sin(th)) * u[1])
    E1 = (A[0] + L * w[0], A[1] + L * w[1]); E2 = (B[0] + (L + d * math.sin(th)) * w[0], B[1] + (L + d * math.sin(th)) * w[1])
    P = (B[0] - d * math.sin(th) * u[0], B[1] - d * math.sin(th) * u[1])
    Q = (B[0] + d * math.sin(th) * w[0], B[1] + d * math.sin(th) * w[1])
    # planes and atoms
    for k, y in enumerate((A[1], B[1])):
        op = 1.0 if k < 2 else 0.45
        b.append(f'<line x1="30" y1="{y}" x2="650" y2="{y}" stroke="#9aa5b1" stroke-width="1" opacity="{op}"/>')
        for x in range(30, 660, 50):
            b.append(atom(x, y, 8, op=op))
    b.append(atom(A[0], A[1], 9, fill="#c9b6d1", stroke=NUC))
    b.append(atom(B[0], B[1], 9, fill="#c9b6d1", stroke=NUC))
    b.append(text(A[0] - 14, A[1] + 26, "A", 13, NUC, "end", "700", halo=True))
    b.append(text(B[0] - 14, B[1] + 26, "B", 13, NUC, "end", "700", halo=True))
    b.append(text(645, A[1] - 12, "plane 1", 11, MUTED, "end"))
    b.append(text(645, B[1] - 12, "plane 2", 11, MUTED, "end"))
    # rays as phase-continuous waves
    def wpath(points, amp=5.5):
        segs = []
        for (p0, p1) in zip(points[:-1], points[1:]):
            segs.append((p0, p1))
        total = 0.0; out = []
        for (p0, p1) in segs:
            Ls = math.hypot(p1[0] - p0[0], p1[1] - p0[1]); ux_, uy_ = (p1[0] - p0[0]) / Ls, (p1[1] - p0[1]) / Ls
            nx_, ny_ = -uy_, ux_
            n = int(Ls / 1.2)
            for i in range(n + 1):
                s = Ls * i / n
                a = amp * math.sin(2 * math.pi * (total + s) / lam)
                out.append(f"{p0[0] + ux_ * s + nx_ * a:.1f},{p0[1] + uy_ * s + ny_ * a:.1f}")
            total += Ls
        return " ".join(out)
    b.append(f'<polyline points="{wpath([S1, A, E1])}" fill="none" stroke="{LIGHT}" stroke-width="2.2" stroke-linejoin="round"/>')
    b.append(f'<polyline points="{wpath([S2, B, E2])}" fill="none" stroke="{LIGHT}" stroke-width="2.2" stroke-linejoin="round"/>')
    # thin center lines for the rays
    for p0, p1 in ((S1, A), (A, E1), (S2, B), (B, E2)):
        b.append(f'<line x1="{p0[0]:.1f}" y1="{p0[1]:.1f}" x2="{p1[0]:.1f}" y2="{p1[1]:.1f}" stroke="{LIGHT}" stroke-width="0.8" opacity="0.7"/>')
    for p0, p1 in ((S1, A), (S2, B)):
        mx, my = p0[0] + 0.45 * (p1[0] - p0[0]), p0[1] + 0.45 * (p1[1] - p0[1])
        b.append(f'<line x1="{mx:.1f}" y1="{my:.1f}" x2="{mx + 12 * u[0]:.1f}" y2="{my + 12 * u[1]:.1f}" stroke="{LIGHT}" stroke-width="2" marker-end="url(#ahl)"/>')
    for p0, p1 in ((A, E1), (B, E2)):
        mx, my = p0[0] + 0.62 * (p1[0] - p0[0]), p0[1] + 0.62 * (p1[1] - p0[1])
        b.append(f'<line x1="{mx:.1f}" y1="{my:.1f}" x2="{mx + 12 * w[0]:.1f}" y2="{my + 12 * w[1]:.1f}" stroke="{LIGHT}" stroke-width="2" marker-end="url(#ahl)"/>')
    # wavefronts (dashed): incoming S1-S2 and A-P, outgoing A-Q and E1-E2
    for p0, p1 in ((S1, S2), (A, P), (A, Q), (E1, E2)):
        b.append(f'<line x1="{p0[0]:.1f}" y1="{p0[1]:.1f}" x2="{p1[0]:.1f}" y2="{p1[1]:.1f}" stroke="{MUTED}" stroke-width="1.1" stroke-dasharray="4 3"/>')
    # extra path segments
    for p0, p1 in ((P, B), (B, Q)):
        b.append(f'<line x1="{p0[0]:.1f}" y1="{p0[1]:.1f}" x2="{p1[0]:.1f}" y2="{p1[1]:.1f}" stroke="{EF}" stroke-width="4.5" stroke-linecap="round" opacity="0.9"/>')
    b.append(text((P[0] + B[0]) / 2 - 14, (P[1] + B[1]) / 2 + 4, "d sin θ", 13, EF, "end", "700", halo=True))
    b.append(text((Q[0] + B[0]) / 2 + 14, (Q[1] + B[1]) / 2 + 4, "d sin θ", 13, EF, "start", "700", halo=True))
    # line A-B (spacing) and right-angle marks
    b.append(f'<line x1="{A[0]}" y1="{A[1]}" x2="{B[0]}" y2="{B[1]}" stroke="{NUC}" stroke-width="1.2" stroke-dasharray="2 3"/>')
    def right_angle(at, d1, d2, s=8):
        p1 = (at[0] + d1[0] * s, at[1] + d1[1] * s); p2 = (p1[0] + d2[0] * s, p1[1] + d2[1] * s); p3 = (at[0] + d2[0] * s, at[1] + d2[1] * s)
        return f'<polyline points="{p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f} {p3[0]:.1f},{p3[1]:.1f}" fill="none" stroke="{MUTED}" stroke-width="1"/>'
    pa = (A[0] - P[0], A[1] - P[1]); n_pa = math.hypot(*pa); pa = (pa[0] / n_pa, pa[1] / n_pa)
    b.append(right_angle(P, (u[0], u[1]), pa))
    qa = (A[0] - Q[0], A[1] - Q[1]); n_qa = math.hypot(*qa); qa = (qa[0] / n_qa, qa[1] / n_qa)
    b.append(right_angle(Q, (-w[0], -w[1]), qa))
    # spacing dimension
    xd = 600
    b.append(f'<line x1="{xd}" y1="{A[1] + 3}" x2="{xd}" y2="{B[1] - 3}" stroke="{INK}" stroke-width="1.4" marker-start="url(#ah)" marker-end="url(#ah)"/>')
    b.append(text(xd + 10, (A[1] + B[1]) / 2 + 5, "d", 15, INK, "start", "700", "italic", halo=True))
    # theta arcs at A (incoming side, left) and outgoing side (right)
    def arc(c, r, a0, a1, col=INK, wdt=1.4):
        x0, y0 = c[0] + r * math.cos(a0), c[1] + r * math.sin(a0)
        x1, y1 = c[0] + r * math.cos(a1), c[1] + r * math.sin(a1)
        sweep = 1 if a1 > a0 else 0
        return f'<path d="M{x0:.1f},{y0:.1f} A{r},{r} 0 0 {sweep} {x1:.1f},{y1:.1f}" fill="none" stroke="{col}" stroke-width="{wdt}"/>'
    b.append(arc(A, 46, math.pi + th, math.pi + 0.0001 + 0 * th) if False else arc(A, 46, math.pi, math.pi + th))
    b.append(text(A[0] - 62, A[1] - 9, "θ", 15, INK, "middle", "700", "italic", halo=True))
    b.append(arc(A, 46, -th, 0))
    b.append(text(A[0] + 62, A[1] - 9, "θ", 15, INK, "middle", "700", "italic", halo=True))
    # 2theta: continuation of incoming beam
    C = (A[0] + 120 * u[0], A[1] + 120 * u[1])
    b.append(f'<line x1="{A[0]}" y1="{A[1]}" x2="{C[0]:.1f}" y2="{C[1]:.1f}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="5 4"/>')
    b.append(arc(A, 92, -th, th, col=BF, wdt=1.4))
    b.append(text(A[0] + 101 * math.cos(math.radians(17)), A[1] + 101 * math.sin(math.radians(17)) + 5, "2θ", 14, BF, "start", "700", "italic", halo=True))
    # labels
    b.append(text(20, 24, "incoming X-rays, in step", 12, AMBER_TXT, "start", "700"))
    b.append(text(20, 39, "(dashed line = a wavefront)", 11, MUTED))
    b.append(text(664, 24, "scattered X-rays: in step again", 12, AMBER_TXT, "end", "700"))
    b.append(text(664, 39, "because the extra path is exactly λ", 11, MUTED, "end"))
    b.append(text(340, 336, "Ray 2 travels  d sin θ + d sin θ = 2d sin θ  farther than ray 1.   Bright reflection when  2d sin θ = nλ.", 12, INK, "middle", "600"))
    return svg(W, H, "\n".join(b))


# ---------------------------------------------------------------- Figure 11.6
def planes():
    W, H = 680, 384
    b = []
    # (a) top view of a cubic lattice, (110) and (220) traces
    b.append(text(14, 22, "(a) Top view: (110) and (220) planes are parallel", 13, INK, "start", "700"))
    a = 66; ox, oy = 40, 312  # origin bottom-left, y up
    X = lambda x: ox + x * a
    Y = lambda y: oy - y * a
    # clip region
    b.append(f'<defs><clipPath id="cl"><rect x="{X(0) - 2}" y="{Y(3.2) - 2}" width="{3 * a + 4}" height="{3.2 * a + 4}"/></clipPath></defs>')
    b.append(f'<rect x="{X(0)}" y="{Y(3)}" width="{3 * a}" height="{3 * a}" fill="#fafbfc" stroke="{RULE}"/>')
    for i in range(4):
        b.append(f'<line x1="{X(i)}" y1="{Y(0)}" x2="{X(i)}" y2="{Y(3)}" stroke="{RULE}" stroke-width="1"/>')
        b.append(f'<line x1="{X(0)}" y1="{Y(i)}" x2="{X(3)}" y2="{Y(i)}" stroke="{RULE}" stroke-width="1"/>')
    # plane traces x + y = c  (c in units of a)
    g = []
    for k in range(1, 12):
        c = k * 0.5
        x0, y0 = max(0, c - 3), min(3, c)
        x1, y1 = min(3, c), max(0, c - 3)
        if k % 2 == 0:
            g.append(f'<line x1="{X(x0):.1f}" y1="{Y(y0):.1f}" x2="{X(x1):.1f}" y2="{Y(y1):.1f}" stroke="{BF}" stroke-width="2.2"/>')
        else:
            g.append(f'<line x1="{X(x0):.1f}" y1="{Y(y0):.1f}" x2="{X(x1):.1f}" y2="{Y(y1):.1f}" stroke="{EF}" stroke-width="1.6" stroke-dasharray="6 4"/>')
    b += g
    for i in range(4):
        for j in range(4):
            b.append(atom(X(i), Y(j), 6))
    # spacing markers along the [110] normal from origin
    def nrm(t):  # point at distance t*a along [110] from origin
        return (X(t / math.sqrt(2)), Y(t / math.sqrt(2)))
    p0, p1, p2 = nrm(1 / math.sqrt(2) * 2), nrm(1 / math.sqrt(2) * 3), nrm(1 / math.sqrt(2) * 4)
    # d110: between planes c=1 and c=2 ; d220: c=1 to c=1.5
    q1 = (X(0.5), Y(0.5)); q15 = (X(0.75), Y(0.75)); q2 = (X(1.0), Y(1.0))
    b.append(f'<line x1="{q1[0]:.1f}" y1="{q1[1]:.1f}" x2="{q2[0]:.1f}" y2="{q2[1]:.1f}" stroke="{INK}" stroke-width="1.3" marker-start="url(#ah)" marker-end="url(#ah)"/>')
    b.append(text(q2[0] + 6, q2[1] + 16, "d₁₁₀", 12, INK, "start", "700", halo=True))
    r1 = (X(1.85), Y(0.15 + 1.0)); r1 = (X(1.5), Y(1.5))
    s1 = (X(1.5), Y(1.5)); s2 = (X(1.75), Y(1.75))
    b.append(f'<line x1="{s1[0]:.1f}" y1="{s1[1]:.1f}" x2="{s2[0]:.1f}" y2="{s2[1]:.1f}" stroke="{EF}" stroke-width="1.3" marker-start="url(#ahr)" marker-end="url(#ahr)"/>')
    b.append(text(s2[0] + 6, s2[1] + 14, "d₂₂₀", 12, EF, "start", "700", halo=True))
    # axes labels
    b.append(f'<line x1="{X(0)}" y1="{Y(0) + 22}" x2="{X(1)}" y2="{Y(0) + 22}" stroke="{MUTED}" stroke-width="1.2" marker-end="url(#ahm)"/>')
    b.append(text(X(1) + 6, Y(0) + 26, "x [100]", 11, MUTED))
    b.append(f'<line x1="{X(0) - 18}" y1="{Y(0)}" x2="{X(0) - 18}" y2="{Y(1)}" stroke="{MUTED}" stroke-width="1.2" marker-end="url(#ahm)"/>')
    b.append(text(X(0) - 22, Y(1) - 6, "y", 11, MUTED, "middle"))
    b.append(text(X(1.5), Y(0) + 46, "a = edge of the cubic cell", 11, MUTED, "middle"))
    # legend for (a)
    lx = 252
    b.append(f'<line x1="{lx}" y1="68" x2="{lx + 22}" y2="68" stroke="{BF}" stroke-width="2.2"/>')
    b.append(text(lx + 28, 72, "(110) planes", 12, INK, "start", "700"))
    b.append(text(lx + 28, 87, "cut x and y at a", 11, MUTED))
    b.append(text(lx + 28, 101, "d = a/√2", 11, MUTED))
    b.append(f'<line x1="{lx}" y1="124" x2="{lx + 22}" y2="124" stroke="{EF}" stroke-width="1.6" stroke-dasharray="6 4"/>')
    b.append(text(lx + 28, 128, "(220) adds these", 12, INK, "start", "700"))
    b.append(text(lx + 28, 143, "cut x and y at a/2", 11, MUTED))
    b.append(text(lx + 28, 157, "d = a/(2√2) = d₁₁₀/2", 11, MUTED))
    b.append(f'<line x1="396" y1="12" x2="396" y2="372" stroke="{RULE}" stroke-width="1"/>')
    # (b) BCC side view: (100) planes vs body-centre planes
    b.append(text(410, 22, "(b) BCC: why (100) vanishes", 13, INK, "start", "700"))
    bx0, by0, s = 440, 318, 74
    for i in range(3):
        x = bx0 + i * s
        b.append(f'<line x1="{x}" y1="{by0 - 2.6 * s}" x2="{x}" y2="{by0 + 4}" stroke="{BF}" stroke-width="2"/>')
        for j in range(3):
            b.append(atom(x, by0 - j * s, 7))
    for i in range(2):
        x = bx0 + (i + 0.5) * s
        b.append(f'<line x1="{x}" y1="{by0 - 2.6 * s}" x2="{x}" y2="{by0 + 4}" stroke="{EF}" stroke-width="1.6" stroke-dasharray="6 4"/>')
        for j in range(2):
            b.append(atom(x, by0 - (j + 0.5) * s, 7, fill="#f6d6db", stroke=EF))
    b.append(f'<line x1="{bx0}" y1="{by0 + 18}" x2="{bx0 + s}" y2="{by0 + 18}" stroke="{INK}" stroke-width="1.2" marker-start="url(#ah)" marker-end="url(#ah)"/>')
    b.append(text(bx0 + s / 2, by0 + 34, "a: (100) spacing", 11, INK, "middle", "600"))
    b.append(f'<line x1="{bx0 + s}" y1="{by0 + 18}" x2="{bx0 + 1.5 * s}" y2="{by0 + 18}" stroke="{EF}" stroke-width="1.2" marker-start="url(#ahr)" marker-end="url(#ahr)"/>')
    b.append(text(bx0 + 1.75 * s + 4, by0 + 34, "a/2", 11, EF, "middle", "600"))
    b.append(text(410, 48, "corner atoms (blue planes): path difference λ", 11, BF, "start", "600"))
    b.append(text(410, 62, "→ in step for a \"(100)\" reflection", 11, BF, "start"))
    b.append(text(410, 82, "body-center atoms (red planes) sit halfway:", 11, EF, "start", "600"))
    b.append(text(410, 96, "path difference λ/2 → exactly out of step", 11, EF, "start"))
    b.append(text(410, 114, "equal numbers of atoms → total cancels", 11, INK, "start", "700"))
    b.append(text(410, 374, "At the (200) angle all planes, a/2 apart, are in step.", 11, INK, "start", "600"))
    return svg(W, H, "\n".join(b))


# ---------------------------------------------------------------- Figure 11.7
def planar_density():
    W, H = 680, 330
    b = []
    R = 25.0
    a = 2 * math.sqrt(2) * R
    def circ(x, y, r=R):
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{MATF}" stroke="{MATS}" stroke-width="1.2" opacity="0.92"/>'
    cy0 = 150
    # (100): square a x a, corners + centre
    cx = 113
    x0, y0 = cx - a / 2, cy0 - a / 2
    for (x, y) in ((x0, y0), (x0 + a, y0), (x0, y0 + a), (x0 + a, y0 + a), (cx, cy0)):
        b.append(circ(x, y))
    b.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{a:.1f}" height="{a:.1f}" fill="none" stroke="{BF}" stroke-width="2"/>')
    # (110): rectangle a (vertical) x a*sqrt2 (horizontal)
    cx = 340
    wdt, hgt = a * math.sqrt(2), a
    x0, y0 = cx - wdt / 2, cy0 - hgt / 2
    for (x, y) in ((x0, y0), (x0 + wdt, y0), (x0, y0 + hgt), (x0 + wdt, y0 + hgt), (cx, y0), (cx, y0 + hgt)):
        b.append(circ(x, y))
    b.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{wdt:.1f}" height="{hgt:.1f}" fill="none" stroke="{BF}" stroke-width="2"/>')
    # (111): equilateral triangle side a*sqrt2, corners + edge midpoints
    cx = 567
    side = a * math.sqrt(2)
    hh = side * math.sqrt(3) / 2
    T = [(cx - side / 2, cy0 + hh / 2), (cx + side / 2, cy0 + hh / 2), (cx, cy0 - hh / 2)]
    M = [((T[i][0] + T[(i + 1) % 3][0]) / 2, (T[i][1] + T[(i + 1) % 3][1]) / 2) for i in range(3)]
    for (x, y) in T + M:
        b.append(circ(x, y))
    b.append(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in T)}" fill="none" stroke="{BF}" stroke-width="2"/>')
    titles = [(113, "(100)", "2 atoms on a² ", "2.00 / a²", "a/2 = 0.500 a"),
              (340, "(110)", "2 atoms on √2 a²", "1.41 / a²", "a/(2√2) = 0.354 a"),
              (567, "(111)", "2 atoms on (√3/2) a²", "2.31 / a²", "a/√3 = 0.577 a")]
    for x, t, how, pd, dd in titles:
        b.append(text(x, 30, t, 15, INK, "middle", "700"))
        b.append(text(x, 242, "planar density", 11, MUTED, "middle"))
        b.append(text(x, 258, pd, 13, INK, "middle", "700"))
        b.append(text(x, 280, "spacing between planes", 11, MUTED, "middle"))
        b.append(text(x, 296, dd, 13, INK, "middle", "700"))
    for x in (226, 453):
        b.append(f'<line x1="{x}" y1="14" x2="{x}" y2="300" stroke="{RULE}" stroke-width="1"/>')
    b.append(text(340, 322, "In every case: planar density × spacing = 4/a³ = atoms per unit volume (FCC)", 12, GREEN, "middle", "700"))
    b.append(text(567, 52, "densest + widest-spaced", 11, GREEN, "middle", "600"))
    return svg(W, H, "\n".join(b))


if __name__ == "__main__":
    for name, fn in [("ch11-xray-tube.svg", tube), ("ch11-xray-shadow.svg", shadow), ("ch11-bragg.svg", bragg),
                     ("ch11-planes.svg", planes), ("ch11-planar-density.svg", planar_density)]:
        (FIG / name).write_text(fn())
        print("wrote", FIG / name)
