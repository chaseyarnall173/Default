"""Generate figures/ch02-energy-diagram.svg: energy picture of the photoelectric effect for sodium
(work function 2.28 eV, HyperPhysics/CRC value). One photon gives all its energy to one electron.
Run from source/:  python3 figures/scripts/ch02_energy_diagram.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch03_spectral_color import wavelength_hex

OUT = Path(__file__).resolve().parents[1] / "ch02-energy-diagram.svg"
INK, MUTED, TEAL, MATTER, STROKE = "#1f2933", "#52606d", "#12a39a", "#d9dee5", "#52606d"
PHI = 2.28
S = 44.0                 # px per eV
YS = 226                 # top of the electron sea
YV = YS - PHI * S        # vacuum level
W, H = 680, 330
o = []
add = o.append
TOP = 22   # crop empty space above the diagram
add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 {TOP} {W} {H - TOP}" width="{W}" height="{H - TOP}" font-family="Inter, sans-serif">')
add(f'<rect x="0" y="{TOP}" width="{W}" height="{H - TOP}" fill="#ffffff"/>')
mk = lambda i, c, s=6: (f'<marker id="{i}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="{s}" markerHeight="{s}" '
                        f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>')
photons = [(650, 110), (530, 185), (400, 260)]
cols = {lam: wavelength_hex(lam) for lam, _ in photons}
# darker stroke versions for thin arrows on white
def darker(h, f=0.78):
    r, g, b = int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)
    return "#{:02x}{:02x}{:02x}".format(int(r * f), int(g * f), int(b * f))
defs = mk("ai", INK, 6) + mk("am", MUTED, 6) + mk("at", TEAL, 6)
for lam, _ in photons:
    defs += mk(f"p{lam}", darker(cols[lam]), 6)
add('<defs>' + defs + '</defs>')

SURF = 372
# metal block and electron sea
add(f'<rect x="64" y="{YV - 70:.1f}" width="{SURF - 64}" height="{H - 46 - (YV - 70):.1f}" fill="{MATTER}" fill-opacity="0.45"/>')
add(f'<rect x="64" y="{YS}" width="{SURF - 64}" height="{H - 46 - YS}" fill="{TEAL}" fill-opacity="0.22"/>')
for i in range(14):
    for j in range(2):
        add(f'<circle cx="{78 + i * 21 + (j % 2) * 10}" cy="{YS + 12 + j * 16}" r="3.4" fill="{TEAL}" fill-opacity="0.75"/>')
add(f'<line x1="64" y1="{YS}" x2="{SURF}" y2="{YS}" stroke="{TEAL}" stroke-width="2"/>')
add(f'<line x1="{SURF}" y1="{YV - 70:.1f}" x2="{SURF}" y2="{H - 46}" stroke="{STROKE}" stroke-width="1.6"/>')
add(f'<text x="{(64 + SURF) / 2}" y="{YS + 52}" font-size="11.5" fill="{INK}" text-anchor="middle">sea of mobile electrons in the metal (sodium)</text>')
add(f'<text x="{(64 + SURF) / 2}" y="{YV - 54:.1f}" font-size="12" font-weight="700" fill="{INK}" text-anchor="middle">inside the metal</text>')
add(f'<text x="{(SURF + 670) / 2}" y="{YV - 54:.1f}" font-size="12" font-weight="700" fill="{INK}" text-anchor="middle">outside (vacuum)</text>')
# vacuum level
add(f'<line x1="64" y1="{YV:.1f}" x2="666" y2="{YV:.1f}" stroke="{INK}" stroke-width="1.3" stroke-dasharray="6 4"/>')
add(f'<text x="666" y="{YV + 16:.1f}" font-size="11.5" fill="{MUTED}" text-anchor="end">escape level (free electron at rest)</text>')
# energy axis
add(f'<line x1="40" y1="{H - 46}" x2="40" y2="30" stroke="{MUTED}" stroke-width="1.3" marker-end="url(#am)"/>')
add(f'<text x="0" y="0" font-size="11.5" fill="{MUTED}" text-anchor="middle" transform="translate(28 170) rotate(-90)">electron energy</text>')
# work function bracket
bx = SURF - 14
add(f'<line x1="{bx}" y1="{YS - 2}" x2="{bx}" y2="{YV + 2:.1f}" stroke="{INK}" stroke-width="1.3" marker-start="url(#ai)" marker-end="url(#ai)"/>')
add(f'<text x="{bx - 6}" y="{(YS + YV) / 2 + 4:.1f}" font-size="12.5" fill="{INK}" text-anchor="end" font-weight="700">φ = 2.28 eV</text>')
add(f'<text x="{bx - 6}" y="{(YS + YV) / 2 + 19:.1f}" font-size="11" fill="{MUTED}" text-anchor="end">work function</text>')
# photon arrows
info = {650: "1.91 eV", 530: "2.34 eV", 400: "3.10 eV"}
names = {650: "red", 530: "green", 400: "violet"}
for lam, x in photons:
    E = 1240.0 / lam
    y1 = YS - E * S
    add(f'<line x1="{x}" y1="{YS - 3}" x2="{x}" y2="{y1 + 2:.1f}" stroke="{darker(cols[lam])}" stroke-width="3" marker-end="url(#p{lam})"/>')
    add(f'<circle cx="{x}" cy="{YS}" r="5.5" fill="{TEAL}" stroke="#ffffff" stroke-width="1.5"/>')
    add(f'<rect x="{x - 9}" y="{H - 40}" width="18" height="8" rx="2" fill="{cols[lam]}"/>')
    add(f'<text x="{x}" y="{H - 18}" font-size="11.5" fill="{INK}" text-anchor="middle">{lam} nm</text>')
    yl = y1 - 8 if lam == 530 else y1 + 4
    add(f'<text x="{x - 10}" y="{yl:.1f}" font-size="11.5" fill="{INK}" text-anchor="end">{info[lam]}</text>')
# outcomes
y650 = YS - 1240 / 650 * S
add(f'<path d="M{110 + 6},{y650 + 6:.1f} q 26 20 4 {YS - y650 - 14:.1f}" fill="none" stroke="{MUTED}" stroke-width="1.3" stroke-dasharray="3 3" marker-end="url(#am)"/>')
add(f'<text x="138" y="{y650 + 32:.1f}" font-size="11" fill="{MUTED}">falls back:</text>')
add(f'<text x="138" y="{y650 + 46:.1f}" font-size="11" fill="{MUTED}">heat</text>')
y400 = YS - 1240 / 400 * S
y530 = YS - 1240 / 530 * S
add(f'<line x1="276" y1="{y400:.1f}" x2="430" y2="{y400:.1f}" stroke="{TEAL}" stroke-width="2" marker-end="url(#at)"/>')
add(f'<circle cx="438" cy="{y400:.1f}" r="5.5" fill="{TEAL}"/>')
add(f'<line x1="191" y1="{y530:.1f}" x2="400" y2="{y530:.1f}" stroke="{TEAL}" stroke-width="1.4" stroke-opacity="0.8" marker-end="url(#at)"/>')
kx = 462
add(f'<line x1="{kx}" y1="{y400:.1f}" x2="{kx}" y2="{YV - 2:.1f}" stroke="{INK}" stroke-width="1.3" marker-start="url(#ai)" marker-end="url(#ai)"/>')
add(f'<text x="{kx + 8}" y="{(y400 + YV) / 2 - 2:.1f}" font-size="12.5" font-weight="700" fill="{INK}">KE = 3.10 − 2.28</text>')
add(f'<text x="{kx + 8}" y="{(y400 + YV) / 2 + 13:.1f}" font-size="12.5" font-weight="700" fill="{INK}">= 0.82 eV</text>')
add(f'<text x="400" y="{YS + 6}" font-size="11.5" fill="{INK}">One photon is absorbed by one electron.</text>')
add(f'<text x="400" y="{YS + 22}" font-size="11.5" fill="{INK}">It escapes only if hf ≥ φ; the leftover</text>')
add(f'<text x="400" y="{YS + 38}" font-size="11.5" fill="{INK}">energy becomes kinetic energy.</text>')
add('</svg>')
OUT.write_text("\n".join(o))
print("wrote", OUT, cols)
