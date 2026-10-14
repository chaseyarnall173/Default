"""Generate figures/ch03-spectrum.svg: the full electromagnetic spectrum on a log wavelength axis,
with size comparisons, frequency and photon-energy axes, and an expanded visible strip.
Long wavelengths (radio) on the left, short (gamma) on the right; the visible strip uses the same
orientation (red left, violet right) so the zoom lines do not cross.
Band boundaries are conventions (see Table 3.1). Run from source/:  python3 figures/scripts/ch03_spectrum.py
"""
import math
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch03_spectral_color import wavelength_hex

OUT = Path(__file__).resolve().parents[1] / "ch03-spectrum.svg"
INK, MUTED, TEAL, PURPLE, MATTER, STROKE = "#1f2933", "#52606d", "#12a39a", "#8d5a97", "#d9dee5", "#52606d"
W, H = 680, 436
X0, D = 52, 30.0          # x of 10^4 m, px per decade
LMAX, LMIN = 4, -14       # log10 range of wavelength (m)


def X(lam_m):
    return X0 + (LMAX - math.log10(lam_m)) * D


o = []
add = o.append
add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Inter, sans-serif">')
add('<rect width="100%" height="100%" fill="#ffffff"/>')
ZOOM_INDEX = len(o)
add("")

# ---------------- size comparisons ----------------
add(f'<text x="{X0 - 40}" y="16" font-size="11.5" font-weight="700" fill="{INK}">Wavelength is about the size of a…</text>')
ICON_Y = 48


def icon_building(x, y):
    add(f'<rect x="{x - 9}" y="{y - 20}" width="18" height="34" fill="{MATTER}" stroke="{STROKE}" stroke-width="1.2"/>')
    for r in range(4):
        for cc in range(2):
            add(f'<rect x="{x - 6 + cc * 7}" y="{y - 16 + r * 7.5}" width="4" height="4" fill="{STROKE}"/>')


def icon_human(x, y):
    add(f'<circle cx="{x}" cy="{y - 15}" r="4.2" fill="{STROKE}"/>')
    add(f'<path d="M{x},{y - 10} L{x},{y + 3} M{x - 7},{y - 6} L{x + 7},{y - 6} M{x},{y + 3} L{x - 5},{y + 14} M{x},{y + 3} L{x + 5},{y + 14}" stroke="{STROKE}" stroke-width="2.4" stroke-linecap="round" fill="none"/>')


def icon_bee(x, y):
    add(f'<ellipse cx="{x - 3}" cy="{y - 9}" rx="5" ry="7" fill="#eaf2fb" stroke="{STROKE}" stroke-width="1" transform="rotate(-25 {x - 3} {y - 9})"/>')
    add(f'<ellipse cx="{x}" cy="{y}" rx="10" ry="6" fill="#f2c14e" stroke="{STROKE}" stroke-width="1.1"/>')
    for dx in (-3, 2):
        add(f'<line x1="{x + dx}" y1="{y - 5.5}" x2="{x + dx}" y2="{y + 5.5}" stroke="{INK}" stroke-width="2"/>')


def icon_pin(x, y):
    add(f'<line x1="{x}" y1="{y - 6}" x2="{x}" y2="{y + 14}" stroke="{STROKE}" stroke-width="1.5"/>')
    add(f'<circle cx="{x}" cy="{y - 9}" r="5.5" fill="{MATTER}" stroke="{STROKE}" stroke-width="1.2"/>')


def icon_cell(x, y):
    add(f'<ellipse cx="{x}" cy="{y}" rx="11" ry="9" fill="#f6e3e6" stroke="{STROKE}" stroke-width="1.2"/>')
    add(f'<circle cx="{x + 2}" cy="{y - 1}" r="3.5" fill="{PURPLE}" fill-opacity="0.7"/>')


def icon_virus(x, y):
    for k in range(10):
        a = 2 * math.pi * k / 10
        add(f'<line x1="{x + 6 * math.cos(a):.1f}" y1="{y + 6 * math.sin(a):.1f}" x2="{x + 10.5 * math.cos(a):.1f}" y2="{y + 10.5 * math.sin(a):.1f}" stroke="{STROKE}" stroke-width="1.3"/>')
        add(f'<circle cx="{x + 11 * math.cos(a):.1f}" cy="{y + 11 * math.sin(a):.1f}" r="1.5" fill="{STROKE}"/>')
    add(f'<circle cx="{x}" cy="{y}" r="7" fill="{MATTER}" stroke="{STROKE}" stroke-width="1.2"/>')


def icon_molecule(x, y):
    add(f'<line x1="{x}" y1="{y - 2}" x2="{x - 8}" y2="{y + 6}" stroke="{STROKE}" stroke-width="2"/>')
    add(f'<line x1="{x}" y1="{y - 2}" x2="{x + 8}" y2="{y + 6}" stroke="{STROKE}" stroke-width="2"/>')
    add(f'<circle cx="{x}" cy="{y - 2}" r="6.5" fill="#d1495b" fill-opacity="0.75" stroke="{STROKE}" stroke-width="1"/>')
    add(f'<circle cx="{x - 9}" cy="{y + 7}" r="4" fill="{MATTER}" stroke="{STROKE}" stroke-width="1"/>')
    add(f'<circle cx="{x + 9}" cy="{y + 7}" r="4" fill="{MATTER}" stroke="{STROKE}" stroke-width="1"/>')


def icon_atom(x, y):
    for ang in (0, 60, 120):
        add(f'<ellipse cx="{x}" cy="{y}" rx="11" ry="4.2" fill="none" stroke="{STROKE}" stroke-width="1" transform="rotate({ang} {x} {y})"/>')
    add(f'<circle cx="{x}" cy="{y}" r="2.6" fill="{PURPLE}"/>')
    add(f'<circle cx="{x + 11}" cy="{y}" r="2" fill="{TEAL}"/>')


def icon_nucleus(x, y):
    pts = [(0, 0), (5, -3), (-5, -3), (0, -6), (5, 3), (-5, 3), (0, 6)]
    for i, (dx, dy) in enumerate(pts):
        col = PURPLE if i % 2 == 0 else "#b7a3bd"
        add(f'<circle cx="{x + dx}" cy="{y + dy}" r="3.8" fill="{col}" stroke="#ffffff" stroke-width="0.8"/>')


icons = [(1e2, icon_building, "building", 0), (1.0, icon_human, "human", 0), (1.2e-2, icon_bee, "bee", 0),
         (1.5e-3, icon_pin, "pinhead", 1), (1e-5, icon_cell, "cell", 0), (1e-7, icon_virus, "virus", 0),
         (2e-9, icon_molecule, "molecule", 0), (1e-10, icon_atom, "atom", 0), (1e-14, icon_nucleus, "nucleus", 0)]
for lam, fn, name, row in icons:
    x = X(lam)
    fn(x, ICON_Y)
    ly = ICON_Y + 30 + row * 13
    add(f'<text x="{x:.1f}" y="{ly}" font-size="11" fill="{INK}" text-anchor="middle">{name}</text>')

# ---------------- chirped wave ----------------
WY = 132
pts = []
xs = X(10 ** LMAX)
phase = 0.0
x = xs
xend = X(10 ** LMIN)
while x <= xend:
    # local drawn wavelength shrinks from 70 px to 3 px across the axis
    t = (x - xs) / (xend - xs)
    lam_px = 70 * (3 / 70) ** t
    pts.append(f"{x:.1f},{WY - 11 * math.sin(phase):.1f}")
    phase += 2 * math.pi * 0.5 / lam_px
    x += 0.5
add(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{MUTED}" stroke-width="1.3"/>')
add(f'<text x="{X0}" y="{WY - 18}" font-size="11" fill="{MUTED}">← longer λ, lower f, lower-energy photons</text>')
add(f'<text x="{xend}" y="{WY - 18}" font-size="11" fill="{MUTED}" text-anchor="end">shorter λ, higher f, higher-energy photons →</text>')

# ---------------- band bar ----------------
BY, BH = 168, 30
bands = [("Radio", 10 ** LMAX, 0.3, "#dbe4ee"), ("Microwave", 0.3, 1e-3, "#e3dcef"), ("Infrared", 1e-3, 700e-9, "#f3dcd8"),
         ("Visible", 700e-9, 400e-9, None), ("UV", 400e-9, 10e-9, "#e6dcf5"), ("X-ray", 10e-9, 1e-11, "#d6ebe7"),
         ("Gamma ray", 1e-11, 10 ** LMIN, "#ece6d4")]
for name, l1, l2, col in bands:
    x1, x2 = X(l1), X(l2)
    if col:
        add(f'<rect x="{x1:.1f}" y="{BY}" width="{x2 - x1:.1f}" height="{BH}" fill="{col}"/>')
        add(f'<text x="{(x1 + x2) / 2:.1f}" y="{BY + BH / 2 + 4}" font-size="11.5" font-weight="700" fill="{INK}" text-anchor="middle">{name}</text>')
    else:
        n = 40
        for i in range(n):
            lam = 700 - 300 * (i + 0.5) / n
            xa = x1 + (x2 - x1) * i / n
            add(f'<rect x="{xa:.2f}" y="{BY}" width="{(x2 - x1) / n + 0.3:.2f}" height="{BH}" fill="{wavelength_hex(lam)}"/>')
# white separators between bands
for name, l1, l2, col in bands[1:]:
    add(f'<line x1="{X(l1):.1f}" y1="{BY}" x2="{X(l1):.1f}" y2="{BY + BH}" stroke="#ffffff" stroke-width="2"/>')

# ---------------- axes ----------------
def axis(y, label):
    add(f'<line x1="{X0}" y1="{y}" x2="{X(10 ** LMIN)}" y2="{y}" stroke="{MUTED}" stroke-width="1"/>')
    add(f'<text x="{X0 - 6}" y="{y + 4}" font-size="11" font-weight="700" fill="{INK}" text-anchor="end">{label}</text>')


def tick(x, y, txt, major=True):
    add(f'<line x1="{x:.1f}" y1="{y - (4 if major else 2.5)}" x2="{x:.1f}" y2="{y + (4 if major else 2.5)}" stroke="{MUTED}" stroke-width="1"/>')
    if txt:
        add(f'<text x="{x:.1f}" y="{y + 16}" font-size="11" fill="{INK}" text-anchor="middle" stroke="#ffffff" stroke-width="4" stroke-linejoin="round" paint-order="stroke">{txt}</text>')


AY = BY + BH + 14
axis(AY, "λ")
wl_labels = {3: "1 km", 0: "1 m", -2: "1 cm", -3: "1 mm", -6: "1 µm", -9: "1 nm", -12: "1 pm"}
for e in range(LMAX, LMIN - 1, -1):
    tick(X(10 ** e), AY, wl_labels.get(e, ""), e in wl_labels)
FY = AY + 34
axis(FY, "f")
for f_hz, txt in ((1e6, "1 MHz"), (1e9, "1 GHz"), (1e12, "1 THz"), (1e15, "10¹⁵ Hz"), (1e18, "10¹⁸ Hz"), (1e21, "10²¹ Hz")):
    tick(X(3.0e8 / f_hz), FY, txt)
EY = FY + 34
axis(EY, "E")
for e_ev, txt in ((1e-6, "1 µeV"), (1e-3, "1 meV"), (1.0, "1 eV"), (1e3, "1 keV"), (1e6, "1 MeV")):
    tick(X(1240e-9 / e_ev), EY, txt)
add(f'<text x="{X(10 ** LMIN) + 6}" y="{AY + 4}" font-size="10.5" fill="{MUTED}">wavelength</text>')
add(f'<text x="{X(10 ** LMIN) + 6}" y="{FY + 4}" font-size="10.5" fill="{MUTED}">frequency</text>')
add(f'<text x="{X(10 ** LMIN) + 6}" y="{EY + 4}" font-size="10.5" fill="{MUTED}">photon</text>')
add(f'<text x="{X(10 ** LMIN) + 6}" y="{EY + 16}" font-size="10.5" fill="{MUTED}">energy</text>')

# ---------------- expanded visible strip ----------------
SY, SH = EY + 58, 30
SX0, SX1 = 70, 610
L_LEFT, L_RIGHT = 750, 380
vx1, vx2 = X(700e-9), X(400e-9)


def SXl(lam):
    return SX0 + (L_LEFT - lam) / (L_LEFT - L_RIGHT) * (SX1 - SX0)


add(f'<rect x="{min(vx1, vx2) - 2:.1f}" y="{BY - 3}" width="{abs(vx2 - vx1) + 4:.1f}" height="{BH + 6}" fill="none" stroke="{INK}" stroke-width="1.2"/>')
add(f'<text x="{(vx1 + vx2) / 2:.1f}" y="{BY - 8}" font-size="11" font-weight="700" fill="{INK}" text-anchor="middle">Visible</text>')
n = 370
for i in range(n):
    lam = L_LEFT - (L_LEFT - L_RIGHT) * (i + 0.5) / n
    xa = SX0 + (SX1 - SX0) * i / n
    add(f'<rect x="{xa:.2f}" y="{SY}" width="{(SX1 - SX0) / n + 0.35:.2f}" height="{SH}" fill="{wavelength_hex(lam)}"/>')
names = [(690, "red"), (612, "orange"), (578, "yellow"), (530, "green"), (490, "cyan"), (460, "blue"), (415, "violet")]
for lam, nm in names:
    add(f'<text x="{SXl(lam):.1f}" y="{SY - 6}" font-size="11" fill="{INK}" text-anchor="middle">{nm}</text>')
for lam in (700, 650, 600, 550, 500, 450, 400):
    x = SXl(lam)
    add(f'<line x1="{x:.1f}" y1="{SY + SH}" x2="{x:.1f}" y2="{SY + SH + 4}" stroke="{MUTED}" stroke-width="1"/>')
    add(f'<text x="{x:.1f}" y="{SY + SH + 16}" font-size="11" fill="{INK}" text-anchor="middle">{lam} nm</text>')
    add(f'<text x="{x:.1f}" y="{SY + SH + 30}" font-size="10.5" fill="{MUTED}" text-anchor="middle">{1240 / lam:.2f} eV</text>')
add(f'<text x="{SX0 - 8}" y="{SY + SH + 16}" font-size="10.5" fill="{MUTED}" text-anchor="end">λ</text>')
add(f'<text x="{SX0 - 8}" y="{SY + SH + 30}" font-size="10.5" fill="{MUTED}" text-anchor="end">E</text>')
add(f'<text x="{SX1 + 6}" y="{SY + 12}" font-size="10.5" fill="{MUTED}">UV →</text>')
add(f'<text x="{SX0 - 6}" y="{SY + 12}" font-size="10.5" fill="{MUTED}" text-anchor="end">← IR</text>')
o[ZOOM_INDEX] = (f'<path d="M{vx1:.1f},{BY + BH} L{vx1:.1f},{EY + 6} L{SXl(700):.1f},{SY} M{vx2:.1f},{BY + BH} L{vx2:.1f},{EY + 6} L{SXl(400):.1f},{SY}" '
                 f'stroke="#9aa5b1" stroke-width="0.9" stroke-dasharray="3 3" fill="none"/>')
add('</svg>')
OUT.write_text("\n".join(o))
print("wrote", OUT)
