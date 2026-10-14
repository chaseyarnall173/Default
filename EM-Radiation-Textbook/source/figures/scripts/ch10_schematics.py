"""Generates the hand-designed SVG schematics for Chapter 10.

  ch10-penetration.svg     Figure 10.2  what stops alpha, beta, gamma, neutrons
  ch10-dna-damage.svg      Figure 10.3  direct vs indirect DNA damage, and UV-B thymine dimer
  ch10-inverse-square.svg  Figure 10.5  inverse-square law geometry
  ch10-lorentz.svg         Figure 10.7  Lorentz force: circles and helices; photons/neutrons go straight
  ch10-magnetosphere.svg   Figure 10.8  Earth's magnetosphere, Van Allen belts, aurora (not to scale)

Run: python3 ch10_schematics.py   (writes into ../)
"""
from pathlib import Path
import math

FIG = Path(__file__).resolve().parents[1]
INK, MUTED, RULE = "#1f2933", "#52606d", "#d9dee5"
EF, BF, LIGHT, ELEC, NUC, MATF, MATS, GREEN = "#d1495b", "#2e6fdb", "#e09f1f", "#12a39a", "#8d5a97", "#d9dee5", "#52606d", "#0b6e4f"
FONT = 'font-family="Inter, sans-serif"'


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" {FONT}>\n'
            f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
            '<defs>\n'
            f'<marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker>\n'
            f'<marker id="ahb" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{BF}"/></marker>\n'
            f'<marker id="ahr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{EF}"/></marker>\n'
            f'<marker id="ahl" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{LIGHT}"/></marker>\n'
            f'<marker id="ahm" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{MUTED}"/></marker>\n'
            '</defs>\n' + body + '\n</svg>\n')


def text(x, y, s, size=12, fill=INK, anchor="start", weight="normal", style="normal", halo=False):
    h = ' stroke="#ffffff" stroke-width="3.5" stroke-linejoin="round" paint-order="stroke"' if halo else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}" font-style="{style}"{h}>{s}</text>')


def wave(x0, y0, x1, y1, amp=5, wl=12):
    """Sinusoidal photon path from (x0,y0) to (x1,y1) as a polyline."""
    L = math.hypot(x1 - x0, y1 - y0); ux, uy = (x1 - x0) / L, (y1 - y0) / L
    nx, ny = -uy, ux
    pts = []
    n = max(int(L / 1.5), 2)
    for i in range(n + 1):
        s = L * i / n
        a = amp * math.sin(2 * math.pi * s / wl)
        pts.append(f"{x0 + ux * s + nx * a:.1f},{y0 + uy * s + ny * a:.1f}")
    return " ".join(pts)


# ---------------------------------------------------------------- Figure 10.2
def penetration():
    W, H = 680, 336
    b = []
    rows = [(92, "α", "alpha", "helium nucleus, +2", NUC),
            (160, "β", "beta", "fast electron, −1", ELEC),
            (236, "γ", "gamma / X-ray", "photon, no charge", LIGHT),
            (292, "n", "neutron", "no charge", MUTED)]
    # barriers start at the row they first stop: x, width, top, fill, stroke, label lines
    bars = [(236, 5, 60, "#f4efe1", "#b9a77a", ["paper", ""]),
            (336, 14, 136, "#cfd6de", "#7b8794", ["aluminum", "(a few mm)"]),
            (446, 30, 206, "#8a96a3", "#3e4c59", ["lead (cm)", "or concrete"]),
            (574, 56, 206, "#d6e6f5", "#6f9fcf", ["water or", "polyethylene"])]
    for x, w, top, f, s_, lab in bars:
        b.append(f'<rect x="{x}" y="{top}" width="{w}" height="{304 - top}" rx="2" fill="{f}" stroke="{s_}" stroke-width="1"/>')
        b.append(text(x + w / 2, top - (22 if lab[1] else 8), lab[0], 12, INK, "middle", "600"))
        if lab[1]:
            b.append(text(x + w / 2, top - 8, lab[1], 11, MUTED, "middle"))
    b.append(f'<rect x="172" y="64" width="14" height="240" rx="7" fill="#fdf1ec" stroke="#c2410c" stroke-width="1"/>')
    b.append(text(179, 52, "source", 11, "#c2410c", "middle", "600"))
    for y, sym, name, desc, col in rows:
        b.append(text(10, y - 3, f'<tspan font-weight="700" fill="{col if col != LIGHT else "#a86a12"}">{sym}</tspan>  {name}', 13, INK))
        b.append(text(10, y + 13, desc, 11, MUTED))
    x0 = 188
    # alpha
    y = 92
    b.append(f'<line x1="{x0}" y1="{y}" x2="228" y2="{y}" stroke="{NUC}" stroke-width="5" stroke-linecap="round"/>')
    b.append(f'<circle cx="232" cy="{y}" r="6" fill="{NUC}" stroke="#fff" stroke-width="1.5"/>')
    b.append(text(256, y + 4, "stopped by a sheet of paper or the dead outer layer of skin", 11, MUTED))
    # beta
    y = 160
    pts = []
    for i in range(0, 59):
        x = x0 + i * 2.6
        jitter = 3.2 * math.sin(i * 1.7) + 2.0 * math.sin(i * 0.63)
        pts.append(f"{x:.1f},{y + jitter:.1f}")
    b.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{ELEC}" stroke-width="2.2" stroke-linejoin="round"/>')
    b.append(f'<circle cx="342" cy="{y + 1}" r="4.5" fill="{ELEC}" stroke="#fff" stroke-width="1.2"/>')
    b.append(text(362, y + 4, "stopped by a few mm of aluminum or plastic", 11, MUTED))
    # gamma
    y = 236
    b.append(f'<polyline points="{wave(x0, y, 444, y, 5, 12)}" fill="none" stroke="{LIGHT}" stroke-width="2.4"/>')
    b.append(f'<polyline points="{wave(478, y, 572, y, 2.5, 12)}" fill="none" stroke="{LIGHT}" stroke-width="1.6" opacity="0.8"/>')
    b.append(f'<polyline points="{wave(632, y, 672, y, 1.2, 12)}" fill="none" stroke="{LIGHT}" stroke-width="1.2" opacity="0.6" marker-end="url(#ahl)"/>')
    b.append(text(525, y + 22, "weakened,", 11, MUTED, "middle"))
    b.append(text(525, y + 36, "never zero", 11, MUTED, "middle"))
    # neutron
    y = 292
    b.append(f'<line x1="{x0}" y1="{y}" x2="580" y2="{y}" stroke="{MUTED}" stroke-width="2" stroke-dasharray="7 4"/>')
    zz = [(580, y), (590, y - 10), (600, y + 6), (608, y - 6), (616, y + 4), (622, y)]
    b.append(f'<polyline points="{" ".join(f"{a},{c}" for a, c in zz)}" fill="none" stroke="{MUTED}" stroke-width="1.6" stroke-linejoin="round"/>')
    b.append(f'<circle cx="622" cy="{y}" r="4.5" fill="#fff" stroke="{MUTED}" stroke-width="2"/>')
    b.append(text(x0, 324, "neutrons slip through lead; hydrogen-rich water or plastic slows and stops them", 11, MUTED))
    return svg(W, H, "\n".join(b))


# ---------------------------------------------------------------- Figure 10.3
def dna_ladder(x0, y0, h, n=9, twist=10, broken=None, dimer=None, kink=0):
    """Simple DNA ladder: two backbones with rungs. Returns svg list. broken = (strand, index)."""
    out = []
    step = h / (n - 1)
    left, right = [], []
    for i in range(n):
        y = y0 + i * step
        k = kink if dimer and i >= dimer else 0
        dx = twist * math.sin(i * 0.8)
        left.append((x0 - 16 + dx + k, y)); right.append((x0 + 16 + dx + k, y))
    for i in range(n):
        (lx, ly), (rx, ry) = left[i], right[i]
        out.append(f'<line x1="{lx:.1f}" y1="{ly:.1f}" x2="{rx:.1f}" y2="{ry:.1f}" stroke="#aeb8c2" stroke-width="4" stroke-linecap="round"/>')
    for strand, pts in (("L", left), ("R", right)):
        segs = []
        for i in range(n - 1):
            if broken and broken[0] == strand and broken[1] == i:
                continue
            segs.append((pts[i], pts[i + 1]))
        for (a, c) in segs:
            out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{c[0]:.1f}" y2="{c[1]:.1f}" stroke="{MATS}" stroke-width="3" stroke-linecap="round"/>')
    return out, left, right


def dna_damage():
    W, H = 680, 300
    b = []
    titles = [(113, "(a) Direct hit"), (340, "(b) Indirect: free radicals"), (567, "(c) UV-B: thymine dimer")]
    for x, t in titles:
        b.append(text(x, 22, t, 13, INK, "middle", "700"))
    for x in (226, 453):
        b.append(f'<line x1="{x}" y1="10" x2="{x}" y2="290" stroke="{RULE}" stroke-width="1"/>')
    # (a) direct: track crosses DNA, strand broken
    parts, L, R = dna_ladder(130, 52, 196, broken=("R", 4))
    b += parts
    b.append(f'<line x1="18" y1="118" x2="212" y2="196" stroke="{NUC}" stroke-width="2.4" marker-end="url(#ahm)"/>')
    b.append(text(18, 108, "ionizing track", 11, NUC, "start", "600"))
    mx = (R[4][0] + R[5][0]) / 2; my = (R[4][1] + R[5][1]) / 2
    b.append(f'<path d="M{mx - 9:.1f},{my - 9:.1f} l6,5 l-4,3 l7,6" fill="none" stroke="{EF}" stroke-width="2"/>')
    b.append(text(mx + 14, my + 4, "strand", 11, EF, "start", "600"))
    b.append(text(mx + 14, my + 18, "break", 11, EF, "start", "600"))
    b.append(text(113, 272, "energy deposited in DNA", 11, MUTED, "middle"))
    b.append(text(113, 286, "itself breaks a bond", 11, MUTED, "middle"))
    # (b) indirect
    parts, L, R = dna_ladder(392, 52, 196, broken=("L", 3))
    b += parts
    b.append(f'<line x1="240" y1="70" x2="300" y2="190" stroke="{NUC}" stroke-width="2.4" marker-end="url(#ahm)"/>')
    # water molecules ionized along track -> OH radicals
    for (cx, cy) in [(262, 112), (286, 160)]:
        b.append(f'<circle cx="{cx}" cy="{cy}" r="7" fill="#fff" stroke="{BF}" stroke-width="1.5"/>')
        b.append(text(cx - 12, cy + 4, "", 10))
    b.append(text(240, 100, "H₂O", 11, BF, "end", "600"))
    b.append(text(270, 215, "H₂O → H₂O⁺ + e⁻", 11, BF, "start"))
    b.append(text(270, 230, "→ •OH radicals", 11, BF, "start", "600"))
    for (sx, sy, ex, ey) in [(270, 112, 360, 120), (294, 160, 362, 137)]:
        b.append(f'<line x1="{sx}" y1="{sy}" x2="{ex}" y2="{ey}" stroke="{BF}" stroke-width="1.4" stroke-dasharray="4 3" marker-end="url(#ahb)"/>')
    for (cx, cy) in [(318, 116), (330, 148)]:
        b.append(f'<circle cx="{cx}" cy="{cy}" r="4" fill="{BF}"/>')
    mx = (L[3][0] + L[4][0]) / 2; my = (L[3][1] + L[4][1]) / 2
    b.append(f'<path d="M{mx - 8:.1f},{my - 9:.1f} l6,5 l-4,3 l7,6" fill="none" stroke="{EF}" stroke-width="2"/>')
    b.append(text(340, 272, "track ionizes water; the radicals", 11, MUTED, "middle"))
    b.append(text(340, 286, "drift a few nm and attack DNA", 11, MUTED, "middle"))
    # (c) thymine dimer: UV photon, two adjacent T bases fused, kink
    parts, L, R = dna_ladder(586, 52, 196, twist=6)
    b += parts
    i1, i2 = 4, 5
    for i in (i1, i2):
        (lx, ly), (rx, ry) = L[i], R[i]
        b.append(f'<line x1="{lx:.1f}" y1="{ly:.1f}" x2="{(lx + rx) / 2:.1f}" y2="{(ly + ry) / 2:.1f}" stroke="#c2410c" stroke-width="5" stroke-linecap="round"/>')
        b.append(text(lx - 10, ly + 4, "T", 12, "#c2410c", "end", "700"))
    (ax_, ay_), (bx_, by_) = L[i1], L[i2]
    mxa = (ax_ + R[i1][0]) / 2 - 8
    b.append(f'<line x1="{mxa:.1f}" y1="{ay_:.1f}" x2="{mxa:.1f}" y2="{by_:.1f}" stroke="#c2410c" stroke-width="3"/>')
    b.append(f'<polyline points="{wave(470, 82, 548, 150, 4, 11)}" fill="none" stroke="#7c3aed" stroke-width="2" marker-end="url(#ahm)"/>')
    b.append(text(470, 72, "UV-B photon (~4 eV)", 11, "#7c3aed", "start", "600"))
    b.append(text(640, 172, "new bond", 11, "#c2410c", "middle", "600"))
    b.append(text(640, 186, "kinks DNA", 11, "#c2410c", "middle", "600"))
    b.append(text(567, 272, "no ionization: a chemical bond", 11, MUTED, "middle"))
    b.append(text(567, 286, "rearranges between two bases", 11, MUTED, "middle"))
    return svg(W, H, "\n".join(b))


# ---------------------------------------------------------------- Figure 10.5
def inverse_square():
    W, H = 680, 270
    b = []
    S = (60, 140)
    # base parallelogram (square seen obliquely) at distance 1
    base = [(150, 110), (172, 98), (172, 158), (150, 170)]
    def scale(p, k):
        return (S[0] + k * (p[0] - S[0]), S[1] + k * (p[1] - S[1]))
    # rays to corners of the k=3 square
    for p in base:
        q = scale(p, 4.0)
        b.append(f'<line x1="{S[0]}" y1="{S[1]}" x2="{q[0]:.1f}" y2="{q[1]:.1f}" stroke="{LIGHT}" stroke-width="1.2" opacity="0.8"/>')
    for k, lab, frac in [(1, "distance r", "1 square: intensity I"), (2, "2r", "4 squares: I/4"), (3, "3r", "9 squares: I/9")]:
        P = [scale(p, k) for p in base]
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in P)
        b.append(f'<polygon points="{pts}" fill="#fdf3dd" fill-opacity="0.85" stroke="{LIGHT}" stroke-width="1.6"/>')
        # grid lines k x k
        for j in range(1, k):
            t = j / k
            a = (P[0][0] + t * (P[1][0] - P[0][0]), P[0][1] + t * (P[1][1] - P[0][1]))
            c = (P[3][0] + t * (P[2][0] - P[3][0]), P[3][1] + t * (P[2][1] - P[3][1]))
            b.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{c[0]:.1f}" y2="{c[1]:.1f}" stroke="{LIGHT}" stroke-width="1"/>')
            a = (P[0][0] + t * (P[3][0] - P[0][0]), P[0][1] + t * (P[3][1] - P[0][1]))
            c = (P[1][0] + t * (P[2][0] - P[1][0]), P[1][1] + t * (P[2][1] - P[1][1]))
            b.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{c[0]:.1f}" y2="{c[1]:.1f}" stroke="{LIGHT}" stroke-width="1"/>')
        xb = (P[0][0] + P[1][0]) / 2
        ybot = max(p[1] for p in P)
        b.append(text(xb, ybot + 22, lab, 12, INK, "middle", "600", halo=True))
        b.append(text(xb, ybot + 38, frac, 11, MUTED, "middle", halo=True))
    b.append(f'<circle cx="{S[0]}" cy="{S[1]}" r="8" fill="{LIGHT}" stroke="#fff" stroke-width="2"/>')
    b.append(text(S[0], S[1] + 28, "point", 11, MUTED, "middle"))
    b.append(text(S[0], S[1] + 42, "source", 11, MUTED, "middle"))
    return svg(W, H, "\n".join(b))


# ---------------------------------------------------------------- Figure 10.7
def lorentz():
    W, H = 680, 300
    b = []
    # (a) B into page, circular orbit
    b.append(text(14, 22, "(a) Field into the page: a circle", 13, INK, "start", "700"))
    for i in range(6):
        for j in range(5):
            x, y = 30 + i * 38, 56 + j * 50
            if (x, y) in ((144, 106), (182, 106), (144, 206), (182, 206)):
                continue
            b.append(f'<circle cx="{x}" cy="{y}" r="5" fill="none" stroke="{BF}" stroke-width="1.2"/>')
            b.append(f'<path d="M{x - 3.2},{y - 3.2} L{x + 3.2},{y + 3.2} M{x - 3.2},{y + 3.2} L{x + 3.2},{y - 3.2}" stroke="{BF}" stroke-width="1.2"/>')
    cx, cy, r = 125, 156, 74
    b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{NUC}" stroke-width="2.2" stroke-dasharray="1 0"/>')
    # particle at top of circle moving left (counterclockwise for + charge with B into page)
    px, py = cx, cy - r
    b.append(f'<line x1="{px}" y1="{py}" x2="{px - 52}" y2="{py}" stroke="{INK}" stroke-width="2.2" marker-end="url(#ah)"/>')
    b.append(text(px - 58, py - 8, "v", 14, INK, "end", "700", "italic"))
    b.append(f'<line x1="{px}" y1="{py}" x2="{px}" y2="{py + 46}" stroke="{EF}" stroke-width="2.2" marker-end="url(#ahr)"/>')
    b.append(text(px + 9, py + 30, "F = qv × B", 12, EF, "start", "700", halo=True))
    b.append(f'<circle cx="{px}" cy="{py}" r="8" fill="{NUC}" stroke="#fff" stroke-width="1.5"/>')
    b.append(text(px, py + 4, "+", 12, "#fff", "middle", "700"))
    b.append(f'<line x1="{cx}" y1="{cy}" x2="{cx + r * 0.707:.1f}" y2="{cy + r * 0.707:.1f}" stroke="{MUTED}" stroke-width="1"/>')
    b.append(text(cx + 8, cy + 44, "r = mv/qB", 12, INK, "start", "600", halo=True))
    b.append(text(125, 286, "B (⊗) points into the page", 11, BF, "middle", "600"))
    b.append(f'<line x1="262" y1="12" x2="262" y2="292" stroke="{RULE}" stroke-width="1"/>')
    # (b) field lines horizontal; helix; photon & neutron straight
    b.append(text(280, 22, "(b) Velocity partly along B: a helix", 13, INK, "start", "700"))
    for y in (70, 130, 190, 250):
        b.append(f'<line x1="282" y1="{y}" x2="668" y2="{y}" stroke="{BF}" stroke-width="1" opacity="0.55" marker-end="url(#ahb)"/>')
    b.append(text(662, 62, "B", 14, BF, "end", "700", "italic"))
    # helix around y = 130
    y0, R, pitch, x0, x1 = 130, 30, 52, 300, 640
    front, back = [], []
    n = 600
    prev = None
    segs = []
    for i in range(n + 1):
        t = i / n * (x1 - x0) / pitch * 2 * math.pi
        x = x0 + t / (2 * math.pi) * pitch + 0.42 * R * math.cos(t)
        y = y0 + R * math.sin(t)
        z = math.cos(t)
        segs.append((x, y, z))
    # draw back (z<0) faint, front strong
    def path(sel):
        out, cur = [], []
        for (x, y, z) in segs:
            if sel(z):
                cur.append(f"{x:.1f},{y:.1f}")
            elif cur:
                out.append(cur); cur = []
        if cur:
            out.append(cur)
        return out
    for pl in path(lambda z: z < 0):
        b.append(f'<polyline points="{" ".join(pl)}" fill="none" stroke="{NUC}" stroke-width="1.6" opacity="0.35"/>')
    for pl in path(lambda z: z >= 0):
        b.append(f'<polyline points="{" ".join(pl)}" fill="none" stroke="{NUC}" stroke-width="2.2"/>')
    b.append(f'<circle cx="{segs[-1][0]:.1f}" cy="{segs[-1][1]:.1f}" r="7" fill="{NUC}" stroke="#fff" stroke-width="1.5"/>')
    b.append(text(300, 92, "proton spirals along the field line", 11, NUC, "start", "600"))
    # electron: smaller, tighter helix, opposite sense, around y=250? keep simple: label
    y0e, Re, pe = 190, 9, 18
    segs = []
    for i in range(700):
        t = i / 699 * (640 - 300) / pe * 2 * math.pi
        segs.append((300 + t / (2 * math.pi) * pe, y0e - Re * math.sin(t), math.cos(t)))
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y, z in segs)
    b.append(f'<polyline points="{pts}" fill="none" stroke="{ELEC}" stroke-width="1.6"/>')
    b.append(text(300, 214, "electron: much lighter, so a much tighter spiral (opposite sense)", 11, ELEC, "start", "600"))
    # photon & neutron straight across, at an angle
    b.append(f'<polyline points="{wave(296, 278, 520, 236, 4, 12)}" fill="none" stroke="{LIGHT}" stroke-width="2" marker-end="url(#ahl)"/>')
    b.append(text(528, 240, "photon: no charge, no bend", 11, "#a86a12", "start", "600"))
    b.append(f'<line x1="296" y1="292" x2="520" y2="262" stroke="{MUTED}" stroke-width="2" stroke-dasharray="7 4" marker-end="url(#ahm)"/>')
    b.append(text(528, 270, "neutron: no charge, no bend", 11, MUTED, "start", "600"))
    return svg(W, H, "\n".join(b))


# ---------------------------------------------------------------- Figure 10.8
def magnetosphere():
    W, H = 680, 400
    b = []
    E = (404, 200); RE = 26

    def P(seq):
        return " ".join(f"{x:.1f},{y:.1f}" for x, y in seq)

    def dline(L, side, sx=1.0, lam=None):
        lm = math.acos(math.sqrt(1 / L)) if lam is None else lam
        seq = []
        for i in range(161):
            la = -lm + 2 * lm * i / 160
            r = L * math.cos(la) ** 2
            seq.append((E[0] + side * sx * r * math.cos(la) * RE, E[1] - r * math.sin(la) * RE))
        return seq

    # solar wind
    for y in (100, 150, 200, 250, 300):
        b.append(f'<line x1="14" y1="{y}" x2="70" y2="{y}" stroke="{NUC}" stroke-width="1.6" marker-end="url(#ahm)"/>')
    b.append(text(14, 350, "Solar wind", 13, INK, "start", "700"))
    b.append(text(14, 365, "charged particles", 11, MUTED))
    b.append(text(14, 379, "streaming from the Sun", 11, MUTED))
    # bow shock (dashed) and magnetopause (smooth, flaring into the tail)
    bs = [(E[0] - 262 + 92 * t * t, E[1] + 168 * t) for t in [-1.1 + 2.2 * i / 100 for i in range(101)]]
    b.append(f'<polyline points="{P(bs)}" fill="none" stroke="{MUTED}" stroke-width="1.2" stroke-dasharray="5 4"/>')
    b.append(text(bs[0][0] + 6, bs[0][1] + 6, "bow shock", 11, MUTED, "start", halo=True))
    mp = [(E[0] - 200 + 72 * t * t, E[1] + 140 * t) for t in [-1 + 2 * i / 100 for i in range(101)]]
    x_end, y_top, y_bot = mp[0][0], mp[0][1], mp[-1][1]
    d = f"M{x_end:.1f},{y_top:.1f} C{x_end + 26:.1f},{y_top - 28:.1f} {x_end + 170:.1f},{E[1] - 168:.1f} 676,{E[1] - 170}"
    b.append(f'<path d="{d}" fill="none" stroke="{BF}" stroke-width="1.6"/>')
    d = f"M{x_end:.1f},{y_bot:.1f} C{x_end + 26:.1f},{y_bot + 28:.1f} {x_end + 170:.1f},{E[1] + 168:.1f} 676,{E[1] + 170}"
    b.append(f'<path d="{d}" fill="none" stroke="{BF}" stroke-width="1.6"/>')
    b.append(f'<polyline points="{P(mp)}" fill="none" stroke="{BF}" stroke-width="1.6"/>')
    b.append(text(E[0] - 206, E[1] - 52, "magnetopause", 11, BF, "end", "600", halo=True))
    # Van Allen belts
    def belt(L1, L2, cut, fill, op):
        out = []
        for side in (-1, 1):
            o, inn = [], []
            for i in range(61):
                la = -cut + 2 * cut * i / 60
                for L, arr in ((L2, o), (L1, inn)):
                    r = L * math.cos(la) ** 2
                    arr.append((E[0] + side * r * math.cos(la) * RE, E[1] - r * math.sin(la) * RE))
            out.append(f'<polygon points="{P(o + inn[::-1])}" fill="{fill}" fill-opacity="{op}"/>')
        return out
    b += belt(1.25, 2.1, math.radians(38), NUC, 0.30)
    b += belt(3.1, 5.2, math.radians(40), ELEC, 0.22)
    # closed field lines
    for L in (1.6, 2.6, 3.8, 5.0):
        for side in (-1, 1):
            b.append(f'<polyline points="{P(dline(L, side))}" fill="none" stroke="{BF}" stroke-width="1.1" opacity="0.8"/>')
    for L, sx in ((6.0, 0.86), (6.8, 0.78)):
        b.append(f'<polyline points="{P(dline(L, -1, sx))}" fill="none" stroke="{BF}" stroke-width="1.1" opacity="0.8"/>')
    # open tail lines
    for lat0, yend in ((60, 70), (65, 104), (70, 138)):
        for sg in (-1, 1):
            la = math.radians(lat0)
            x0, y0 = E[0] + math.cos(la) * RE, E[1] - sg * math.sin(la) * RE
            d = f"M{x0:.1f},{y0:.1f} C{x0 + 40:.1f},{y0 - sg * 60:.1f} {x0 + 110:.1f},{E[1] - sg * yend:.1f} 676,{E[1] - sg * yend:.1f}"
            b.append(f'<path d="{d}" fill="none" stroke="{BF}" stroke-width="1.1" opacity="0.8"/>')
    # trapped particle on the L = 3.8 dayside line (gyrating, bouncing)
    L = 3.8; pts = []
    for i in range(500):
        la = math.radians(-36 + 72 * i / 499)
        r = L * math.cos(la) ** 2
        bx, by = E[0] - r * math.cos(la) * RE, E[1] - r * math.sin(la) * RE
        dl = 3.2 * math.sin(i * 0.19)
        pts.append((bx - math.cos(la) * dl, by - math.sin(la) * dl))
    b.append(f'<polyline points="{P(pts)}" fill="none" stroke="{NUC}" stroke-width="1.4"/>')
    for la_deg in (-36, 36):
        la = math.radians(la_deg); r = L * math.cos(la) ** 2
        b.append(f'<circle cx="{E[0] - r * math.cos(la) * RE:.1f}" cy="{E[1] - r * math.sin(la) * RE:.1f}" r="3" fill="{NUC}"/>')
    b.append(text(E[0] - 98, E[1] - 92, "trapped particle: spirals along a field", 11, NUC, "end", "600", halo=True))
    b.append(text(E[0] - 98, E[1] - 78, "line, bouncing between mirror points", 11, NUC, "end", "600", halo=True))
    # Earth (day side lit)
    b.append(f'<circle cx="{E[0]}" cy="{E[1]}" r="{RE}" fill="#9cc3e6" stroke="{BF}" stroke-width="1.2"/>')
    b.append(f'<path d="M{E[0]} {E[1] - RE} A{RE} {RE} 0 0 1 {E[0]} {E[1] + RE} Z" fill="#3e4c59" opacity="0.55"/>')
    b.append(text(E[0], E[1] + 4, "Earth", 11, INK, "middle", "700"))
    # aurora ovals
    for sg in (-1, 1):
        y = E[1] - sg * (RE - 2)
        b.append(f'<ellipse cx="{E[0]}" cy="{y - sg * 2:.1f}" rx="12" ry="3.5" fill="none" stroke="#2fbf71" stroke-width="3"/>')
    b.append(f'<line x1="{E[0] + 12}" y1="{E[1] - RE - 4}" x2="{E[0] + 34}" y2="{E[1] - RE - 22}" stroke="{GREEN}" stroke-width="1"/>')
    b.append(text(E[0] + 36, E[1] - RE - 24, "aurora", 11, GREEN, "start", "700", halo=True))
    # belt labels
    lx = 548
    b.append(f'<line x1="{lx - 4}" y1="{E[1] + 118}" x2="{E[0] + 1.6 * RE:.1f}" y2="{E[1] + 10}" stroke="{NUC}" stroke-width="1"/>')
    b.append(text(lx, E[1] + 122, "inner Van Allen belt", 11, NUC, "start", "700", halo=True))
    b.append(text(lx, E[1] + 136, "(mostly protons)", 11, NUC, "start", halo=True))
    b.append(f'<line x1="{lx - 4}" y1="{E[1] + 156}" x2="{E[0] + 4.3 * RE:.1f}" y2="{E[1] + 20}" stroke="{ELEC}" stroke-width="1"/>')
    b.append(text(lx, E[1] + 160, "outer Van Allen belt", 11, ELEC, "start", "700", halo=True))
    b.append(text(lx, E[1] + 174, "(mostly electrons)", 11, ELEC, "start", halo=True))
    # cosmic ray near the pole
    b.append(f'<line x1="244" y1="30" x2="{E[0] - 4}" y2="{E[1] - RE - 6}" stroke="{EF}" stroke-width="1.8" marker-end="url(#ahr)"/>')
    b.append(text(14, 22, "very-high-energy cosmic ray: barely bent;", 11, EF, "start", "600"))
    b.append(text(14, 36, "the atmosphere has to stop it", 11, EF, "start", "600"))
    # photon
    b.append(f'<polyline points="{wave(84, 262, E[0] - RE - 8, E[1] + 14, 4, 12)}" fill="none" stroke="{LIGHT}" stroke-width="2" marker-end="url(#ahl)"/>')
    b.append(text(150, 300, "X-ray / UV photon: the field does nothing;", 11, "#a86a12", "start", "600", halo=True))
    b.append(text(150, 314, "absorbed high in the atmosphere", 11, "#a86a12", "start", "600", halo=True))
    b.append(text(670, 394, "magnetotail →  (not to scale)", 11, MUTED, "end"))
    return svg(W, H, "\n".join(b))


if __name__ == "__main__":
    for name, fn in [("ch10-penetration.svg", penetration), ("ch10-dna-damage.svg", dna_damage),
                     ("ch10-inverse-square.svg", inverse_square), ("ch10-lorentz.svg", lorentz),
                     ("ch10-magnetosphere.svg", magnetosphere)]:
        (FIG / name).write_text(fn())
        print("wrote", FIG / name)
