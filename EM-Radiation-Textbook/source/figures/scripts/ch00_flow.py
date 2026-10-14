"""Prologue figure: decision flow for what happens when light hits matter."""
from pathlib import Path
OUT = Path(__file__).resolve().parents[1] / "ch00-flow.svg"
W, H = 680, 470
o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Inter, sans-serif">',
     '<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
     '<path d="M0,0 L10,5 L0,10 z" fill="#52606d"/></marker></defs>']
def box(x, y, w, h, lines, fill="#ffffff", stroke="#52606d", bold_first=False, size=11.2, color="#1f2933", sw=1.3):
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
    n = len(lines); lh = size * 1.35
    y0 = y + h / 2 - (n - 1) * lh / 2 + size * 0.36
    for i, t in enumerate(lines):
        wgt = "700" if (bold_first and i == 0) else "400"
        o.append(f'<text x="{x + w/2}" y="{y0 + i*lh:.1f}" font-size="{size}" font-weight="{wgt}" fill="{color}" text-anchor="middle">{t}</text>')
def arrow(x1, y1, x2, y2):
    o.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#52606d" stroke-width="1.5" marker-end="url(#ar)"/>')
box(180, 8, 320, 44, ["Light of frequency f arrives at a material", "(each photon carries energy E = hf)"], fill="#fdf5e6", stroke="#e09f1f", sw=1.8)
arrow(340, 52, 340, 72)
box(130, 74, 420, 50, ["Does the material have an allowed jump (electronic,", "vibrational, or rotational) whose energy matches hf?"], fill="#f5f7fa", bold_first=False, size=11.6)
# branches
o.append('<path d="M130,99 L90,99 L90,150" fill="none" stroke="#52606d" stroke-width="1.5" marker-end="url(#ar)"/>')
o.append('<path d="M550,99 L590,99 L590,150" fill="none" stroke="#52606d" stroke-width="1.5" marker-end="url(#ar)"/>')
o.append('<text x="98" y="92" font-size="12" font-weight="800" fill="#2e6fdb" text-anchor="end">NO</text>')
o.append('<text x="582" y="92" font-size="12" font-weight="800" fill="#d1495b">YES</text>')
LX, RX, CW = 8, 352, 320
box(LX, 152, CW, 58, ["NOT ABSORBED", "Electrons are shaken off-resonance and", "re-radiate in step with the wave (coherently)"], fill="#eef4fd", stroke="#2e6fdb", bold_first=True, sw=1.8)
box(RX, 152, CW, 58, ["ABSORBED", "The photon disappears; its energy lifts the", "atom or molecule into an excited state"], fill="#fbeef0", stroke="#d1495b", bold_first=True, sw=1.8)
left = [["Reflection: the re-radiated waves add up", "backward (mirrors, shiny metals) · Ch 6"],
        ["Transmission &amp; refraction: they add up forward", "with a slower phase speed (glass) · Ch 6"],
        ["Scattering: small particles send light sideways", "(blue sky, white clouds) · Ch 7–8"]]
right = [["Re-emitted after a delay in a random direction", "(fluorescence, glow-in-the-dark) · Ch 5"],
         ["Shared into atomic vibrations: becomes heat", "(black car in the sun, IR warmth) · Ch 9"],
         ["Drives chemistry: vision, photosynthesis,", "sunburn · Ch 7, 10"],
         ["If hf exceeds the ionization energy, an electron", "is knocked out: ionization · Ch 2, 10"]]
y0, step, bh = 228, 52, 42
for i, t in enumerate(left):
    box(LX + 14, y0 + i*step, CW - 14, bh, t, size=10.8)
    o.append(f'<path d="M{LX+6},{210} L{LX+6},{y0 + i*step + bh/2} L{LX+12},{y0 + i*step + bh/2}" fill="none" stroke="#2e6fdb" stroke-width="1.4"/>')
for i, t in enumerate(right):
    box(RX + 14, y0 + i*step, CW - 14, bh, t, size=10.8)
    o.append(f'<path d="M{RX+6},{210} L{RX+6},{y0 + i*step + bh/2} L{RX+12},{y0 + i*step + bh/2}" fill="none" stroke="#d1495b" stroke-width="1.4"/>')
o.append(f'<text x="{W/2}" y="{H-12}" font-size="10.5" fill="#52606d" text-anchor="middle">Most real materials do several of these at once; the mix depends on wavelength. Energy is conserved: R + A + T = 1.</text>')
o.append("</svg>")
OUT.write_text("\n".join(o)); print("wrote", OUT)
