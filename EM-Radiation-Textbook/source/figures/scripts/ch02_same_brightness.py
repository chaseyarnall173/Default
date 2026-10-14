"""Generate figures/ch02-same-brightness.svg: two beams with the same power.
Red (700 nm, 1.77 eV/photon) delivers 7 photons per tick; violet (400 nm, 3.10 eV/photon) delivers 4.
7 x 1.77 = 12.4 eV = 4 x 3.10 eV. On sodium (phi = 2.28 eV) only the violet photons eject electrons.
Run from source/:  python3 figures/scripts/ch02_same_brightness.py
"""
import math
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch03_spectral_color import wavelength_hex

OUT = Path(__file__).resolve().parents[1] / "ch02-same-brightness.svg"
INK, MUTED, TEAL, MATTER, STROKE = "#1f2933", "#52606d", "#12a39a", "#d9dee5", "#52606d"
W, H = 680, 270
o = []
add = o.append
add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Inter, sans-serif">')
add('<rect width="100%" height="100%" fill="#ffffff"/>')
add('<defs><marker id="at" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
    f'<path d="M0,0 L10,5 L0,10 z" fill="{TEAL}"/></marker>'
    '<marker id="ai" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
    f'<path d="M0,0 L10,5 L0,10 z" fill="{MUTED}"/></marker></defs>')


def packet(cx, cy, lam_px, amp, col, sigma):
    pts = []
    for i in range(-60, 61):
        x = cx + i * sigma * 2.7 / 60
        env = math.exp(-0.5 * ((x - cx) / sigma) ** 2)
        pts.append(f"{x:.1f},{cy - amp * env * math.sin(2 * math.pi * (x - cx) / lam_px):.1f}")
    add(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{col}" stroke-width="2.4" stroke-linejoin="round"/>')


add(f'<text x="16" y="22" font-size="12.5" font-weight="700" fill="{INK}">Two beams with the same power (same brightness on a power meter)</text>')
rows = [
    dict(lam=700, cy=92, n=7, name="Red light, 700 nm", e="1.77 eV per photon", lam_px=14, sig=5.6,
         sum="7 × 1.77 eV = 12.4 eV", out1="sodium: no electrons", out2="(1.77 eV &lt; φ = 2.28 eV)", emit=0),
    dict(lam=400, cy=212, n=4, name="Violet light, 400 nm", e="3.10 eV per photon", lam_px=8, sig=5.2,
         sum="4 × 3.10 eV = 12.4 eV", out1="sodium: 4 electrons out,", out2="each with up to 0.82 eV", emit=4),
]
x0, x1, plate = 168, 452, 466
for r in rows:
    col = wavelength_hex(r["lam"])
    cy = r["cy"]
    add(f'<text x="16" y="{cy - 6}" font-size="12.5" font-weight="700" fill="{INK}">{r["name"]}</text>')
    add(f'<text x="16" y="{cy + 10}" font-size="11.5" fill="{MUTED}">{r["e"]}</text>')
    add(f'<line x1="{x0}" y1="{cy}" x2="{x1}" y2="{cy}" stroke="#e4e7eb" stroke-width="1"/>')
    step = (x1 - x0) / r["n"]
    for i in range(r["n"]):
        packet(x0 + step * (i + 0.5), cy, r["lam_px"], 15, col, r["sig"])
    # one-tick bracket
    add(f'<line x1="{x0}" y1="{cy + 30}" x2="{x1}" y2="{cy + 30}" stroke="{MUTED}" stroke-width="1" marker-start="url(#ai)" marker-end="url(#ai)"/>')
    add(f'<text x="{(x0 + x1) / 2}" y="{cy + 46}" font-size="11.5" fill="{INK}" text-anchor="middle">arriving in one tick of time: {r["sum"]}</text>')
    # sodium plate
    add(f'<rect x="{plate}" y="{cy - 34}" width="12" height="68" fill="{MATTER}" stroke="{STROKE}" stroke-width="1.3"/>')
    for k in range(r["emit"]):
        yy = cy - 26 + k * 17
        add(f'<line x1="{plate - 3}" y1="{yy}" x2="{plate - 30}" y2="{yy - 14}" stroke="{TEAL}" stroke-width="1.6" marker-end="url(#at)"/>')
        add(f'<circle cx="{plate - 3}" cy="{yy}" r="4" fill="{TEAL}"/>')
    add(f'<text x="{plate + 22}" y="{cy - 4}" font-size="12" font-weight="700" fill="{INK}">{r["out1"]}</text>')
    add(f'<text x="{plate + 22}" y="{cy + 12}" font-size="11.5" fill="{MUTED}">{r["out2"]}</text>')
add(f'<line x1="16" y1="152" x2="664" y2="152" stroke="#e4e7eb" stroke-width="1"/>')
add('</svg>')
OUT.write_text("\n".join(o))
print("wrote", OUT)
