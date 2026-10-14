"""Prologue figure: what each band of the spectrum does to matter (log photon-energy axis)."""
import math
from pathlib import Path
OUT = Path(__file__).resolve().parents[1] / "ch00-ladder.svg"
W = 680
AX0, AX1 = 150, 395            # x-range of the log-energy axis
E0, E1 = -9, 7                 # log10(eV) range
def X(logE): return AX0 + (logE - E0) / (E1 - E0) * (AX1 - AX0)
L = lambda nm: math.log10(1240.0 / nm)   # wavelength in nm -> log10 photon energy (eV)
rows = [
  ("Radio",      E0,        L(1e9),    "#7a8794", ["Drives currents in antennas and metal;", "too weak to change atoms or molecules"]),
  ("Microwave",  L(1e9),    L(1e6),    "#8f6b5a", ["Spins (rotates) polar molecules such", "as water: the microwave oven"]),
  ("Infrared",   L(1e6),    L(700),    "#b3262e", ["Shakes chemical bonds (vibrations):", "absorbed as warmth; what warm things emit"]),
  ("Visible",    L(700),    L(400),    "url(#vis)", ["Lifts outer electrons across 1.8–3.1 eV gaps:", "color, vision, photosynthesis, LEDs"]),
  ("Ultraviolet",L(400),    L(10),     "#6a4cff", ["Breaks chemical bonds (sunburn); above", "≈10 eV it can ionize atoms"]),
  ("X-ray",      L(10),     L(0.01),   "#8a7fd6", ["Ejects inner-shell electrons; passes soft", "tissue; diffracts off crystal planes"]),
  ("Gamma ray",  L(0.01),   E1,        "#5b5f8f", ["Born in atomic nuclei; deeply penetrating", "and strongly ionizing"]),
]
top, rowh = 58, 40
parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {top + rowh*len(rows) + 52}" font-family="Inter, sans-serif">',
  '<defs><linearGradient id="vis" x1="0" x2="1"><stop offset="0" stop-color="#ff2a1a"/><stop offset="0.3" stop-color="#ffb000"/>'
  '<stop offset="0.5" stop-color="#3ccf3c"/><stop offset="0.75" stop-color="#2a7fff"/><stop offset="1" stop-color="#7b3cff"/></linearGradient></defs>',
  f'<text x="{AX0}" y="18" font-size="11.5" font-weight="700" fill="#1f2933">Photon energy (eV, log scale)</text>',
  f'<text x="{AX1+18}" y="18" font-size="11.5" font-weight="700" fill="#1f2933">What it mainly does to matter</text>',
  f'<text x="8" y="18" font-size="11.5" font-weight="700" fill="#1f2933">Band</text>']
# axis ticks
SUP = str.maketrans("-0123456789", "\u207b\u2070\u00b9\u00b2\u00b3\u2074\u2075\u2076\u2077\u2078\u2079")
for e in range(-8, 8, 2):
    x = X(e)
    lab = "1" if e == 0 else "10" + str(e).translate(SUP)
    parts.append(f'<line x1="{x:.1f}" y1="{top-14}" x2="{x:.1f}" y2="{top + rowh*len(rows) - 6}" stroke="#d9dee5" stroke-width="1"/>')
    parts.append(f'<text x="{x:.1f}" y="{top-20}" font-size="10.5" fill="#52606d" text-anchor="middle">{lab}</text>')
# ionization threshold
xi = X(1.0)
parts.append(f'<line x1="{xi:.1f}" y1="{top-14}" x2="{xi:.1f}" y2="{top + rowh*len(rows) + 4}" stroke="#d1495b" stroke-width="1.6" stroke-dasharray="4 3"/>')
parts.append(f'<text x="{xi+4:.1f}" y="{top + rowh*len(rows) + 16}" font-size="10.5" font-weight="700" fill="#d1495b">≈10 eV: ionizing →</text>')
parts.append(f'<text x="{xi-4:.1f}" y="{top + rowh*len(rows) + 16}" font-size="10.5" fill="#52606d" text-anchor="end">← non-ionizing</text>')
for i, (name, a, b, col, txt) in enumerate(rows):
    y = top + i * rowh
    if i % 2 == 0:
        parts.append(f'<rect x="0" y="{y-4}" width="{W}" height="{rowh}" fill="#f5f7fa"/>')
    x0, x1 = X(a), X(b)
    wbar = max(x1 - x0, 4)
    parts.append(f'<rect x="{x0:.1f}" y="{y+6}" width="{wbar:.1f}" height="18" rx="3" fill="{col}"/>')
    parts.append(f'<text x="8" y="{y+20}" font-size="12.5" font-weight="700" fill="#1f2933">{name}</text>')
    for j, t in enumerate(txt):
        parts.append(f'<text x="{AX1+18}" y="{y+13+j*14}" font-size="11" fill="#1f2933">{t}</text>')
parts.append(f'<text x="{X(L(550))+8:.1f}" y="{top + 3*rowh + 19}" font-size="10" fill="#52606d">← tiny slice!</text>')
parts.append(f'<text x="{AX0}" y="{top + rowh*len(rows) + 40}" font-size="10" fill="#52606d">Wavelength runs the other way: about 1 km at the far left, about 10\u207b\u00b9\u00b3 m at the far right.</text>')
parts.append("</svg>")
OUT.write_text("\n".join(parts))
print("wrote", OUT)
