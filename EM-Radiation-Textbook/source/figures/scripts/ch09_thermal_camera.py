"""Figure 9.4 - what a thermal camera actually measures. (a) emissivity: a shiny pan at 80 C reads
near room temperature because it emits little and mostly reflects the cool room; black tape (e ~ 0.95)
reads its true temperature. Estimate for bare metal (e = 0.05, room 293 K, camera set to e = 0.95):
T_app^4 = [0.05*353^4 + 0.95*293^4 - 0.05*293^4]/0.95 -> about 297 K (24 C).
(b) window glass passes visible light but absorbs 8-14 um infrared.
Output: figures/ch09-thermal-camera.svg"""
from pathlib import Path
import numpy as np

OUT = Path(__file__).resolve().parents[1] / "ch09-thermal-camera.svg"
INK, MUTED, AMBER, FILL, STROKE, RED, GREY = "#1f2933", "#52606d", "#e09f1f", "#d9dee5", "#52606d", "#d1495b", "#9aa5b1"
W, H = 680, 330
el = []
def T(x, y, s, size=12, anchor="start", fill=INK, weight="400", style="normal"):
    s = s.replace("&", "&amp;").replace("<", "&lt;")
    el.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{fill}" '
              f'font-weight="{weight}" font-style="{style}">{s}</text>')
def L(x1, y1, x2, y2, stroke=INK, w=1.2, dash=None, extra=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    el.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{w}"{d} {extra}/>')
el.append('<defs>' + "".join(
    f'<marker id="m{n}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="{s}" markerHeight="{s}" orient="auto">'
    f'<path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>' for n, c, s in [("A", AMBER, 4), ("R", RED, 4), ("G", GREY, 5)])
    + '<linearGradient id="metal" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#c9d0d8"/>'
      '<stop offset="0.35" stop-color="#f4f6f8"/><stop offset="0.6" stop-color="#d4dae1"/><stop offset="1" stop-color="#aeb7c1"/></linearGradient></defs>')
def camera(x, y, label, face=1, label_dy=30):
    el.append(f'<rect x="{x-24}" y="{y-15}" width="48" height="30" rx="5" fill="#3e4c59"/>')
    el.append(f'<circle cx="{x+24*face}" cy="{y}" r="8" fill="#1f2933" stroke="#9aa5b1" stroke-width="1.5"/>')
    T(x, y + label_dy, label, 11, "middle", MUTED)

# ---------- (a) ----------
T(14, 20, "(a) A shiny pan looks cold", 13, weight="600")
# room wall (cool) at left
el.append(f'<rect x="14" y="40" width="16" height="230" fill="#eef4fd" stroke="#2e6fdb" stroke-opacity="0.4"/>')
T(36, 50, "room, 20 °C", 11, "start", "#2e6fdb")
# pan (side view)
px0, px1, py0, py1 = 70, 250, 205, 255
el.append(f'<path d="M{px0} {py0} L{px1} {py0} L{px1-10} {py1} Q{(px0+px1)/2} {py1+8} {px0+10} {py1} Z" fill="url(#metal)" stroke="{STROKE}" stroke-width="1.2"/>')
el.append(f'<rect x="{px1}" y="{py0+6}" width="70" height="9" rx="4" fill="#52606d"/>')
el.append(f'<rect x="185" y="{py0+1}" width="34" height="{py1-py0-3}" fill="#1f2933"/>')
T(202, py1 + 26, "black tape", 11, "middle", INK, "600")
T(110, py1 + 26, "bare metal", 11, "middle", INK, "600")
T(122, py0 + 30, "pan at 80 °C", 11.5, "middle", INK, "600")
camera(306, 72, "thermal camera", face=-1, label_dy=-22)
# rays to camera: emitted (amber) and reflected (grey)
L(202, py0 - 2, 282, 98, stroke=AMBER, w=4.5, extra='marker-end="url(#mA)"')
L(118, py0 - 2, 280, 92, stroke=AMBER, w=1.0, extra='marker-end="url(#mA)"')
L(30, 150, 112, py0 - 4, stroke=GREY, w=2.2, dash="5 3")
L(112, py0 - 4, 278, 86, stroke=GREY, w=2.2, dash="5 3", extra='marker-end="url(#mG)"')
T(244, 172, "tape emits", 11, "start", AMBER, "600")
T(244, 186, "strongly", 11, "start", AMBER, "600")
T(244, 200, "(ε ≈ 0.95)", 11, "start", AMBER)
T(40, 108, "metal mostly reflects", 11, "start", MUTED, "600")
T(40, 122, "the cool room", 11, "start", MUTED, "600")
T(40, 136, "(ε ≈ 0.05)", 11, "start", MUTED)
# readout
el.append(f'<rect x="246" y="262" width="108" height="50" rx="6" fill="#1f2933"/>')
T(255, 281, "tape:   80 °C", 11.5, "start", "#ffd27a", "600")
T(255, 300, "metal: ≈ 24 °C", 11.5, "start", "#9ec5ff", "600")

# ---------- (b) ----------
X0 = 368
T(X0, 20, "(b) Glass: clear to eyes, a wall to the camera", 13, weight="600")
gx = 518
el.append(f'<rect x="{gx-6}" y="45" width="12" height="230" fill="#dfeaf3" stroke="{STROKE}" stroke-width="1"/>')
T(gx, 292, "window glass", 11, "middle", MUTED)
# person behind glass
hx, hy = 640, 105
el.append(f'<circle cx="{hx}" cy="{hy}" r="17" fill="#f2c4a8" stroke="{STROKE}" stroke-width="1"/>')
el.append(f'<path d="M{hx-26} 250 Q{hx-28} 135 {hx} 128 Q{hx+28} 135 {hx+26} 250 Z" fill="#f2c4a8" stroke="{STROKE}" stroke-width="1"/>')
T(hx - 14, 270, "person, 34 °C skin", 11, "middle", INK)
# eye
ex, ey = 400, 80
el.append(f'<path d="M{ex-16} {ey} Q{ex} {ey-12} {ex+16} {ey} Q{ex} {ey+12} {ex-16} {ey} Z" fill="white" stroke="{INK}" stroke-width="1.2"/>')
el.append(f'<circle cx="{ex+2}" cy="{ey}" r="4.5" fill="{INK}"/>')
T(ex, ey + 26, "your eye", 11, "middle", MUTED)
L(hx - 20, 95, ex + 22, ey, stroke=AMBER, w=2.5, extra='marker-end="url(#mA)"')
T(gx + 14, 72, "visible light", 11, "start", AMBER, "600")
T(gx + 14, 86, "passes", 11, "start", AMBER, "600")
# IR stopped at glass
L(hx - 26, 175, gx + 8, 175, stroke=RED, w=3, extra='marker-end="url(#mR)"')
T(gx + 12, 151, "IR (8–14 µm)", 11, "start", RED, "600")
T(gx + 12, 165, "absorbed", 11, "start", RED, "600")
camera(410, 190, "thermal camera")
L(gx - 8, 190, 446, 190, stroke=GREY, w=2.2, dash="5 3", extra='marker-end="url(#mG)"')
T(452, 236, "camera sees only the", 11, "start", MUTED)
T(452, 250, "glass’s own glow and", 11, "start", MUTED)
T(452, 264, "reflections", 11, "start", MUTED)

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
       f'font-family="Inter, sans-serif">\n<rect width="{W}" height="{H}" fill="white"/>\n' + "\n".join(el) + "\n</svg>\n")
OUT.write_text(svg)
Tapp = ((0.05 * 353 ** 4 + 0.95 * 293 ** 4 - 0.05 * 293 ** 4) / 0.95) ** 0.25
print("wrote", OUT, "apparent metal temperature %.1f K = %.1f C" % (Tapp, Tapp - 273.15))
