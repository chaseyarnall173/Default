"""Figure 7.4 - the band-gap color rule. Photon-energy axis with the visible window (1.77-3.10 eV)
and where real materials' band gaps fall. Band gaps: HyperPhysics semiconductor table (Si, GaAs,
CdSe, CdS, ZnSe, GaN, ZnS, diamond); WebExhibits "Causes of Color" (PbS, HgS, cadmium orange).
Swatch colors are COMPUTED: reflectance ~0 below the absorption-edge wavelength 1240/Eg and high
above it, under a 6500 K illuminant, using CIE color-matching functions (see ch07_colorlib.py).
Si, GaAs and PbS absorb all visible light; their swatches show the neutral gray/black of their
surface reflection instead. Writes figures/ch07-bandgap-chart.svg."""
import math
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch07_colorlib import LAM, reflectance_to_hex, spectral_hex  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "ch07-bandgap-chart.svg"
TEXT, MUTED, STROKE = "#1f2933", "#52606d", "#52606d"
W, H = 680, 314
X0, PX = 50, 140.0          # x of 0 eV, pixels per eV (axis shows 0-4 eV)
EMAX = 4.0
YB0, YB1 = 104, 150          # band strip
els = []


def X(E): return X0 + PX * E


def text(x, y, s, size=12, color=TEXT, anchor="start", weight=400):
    els.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{color}" text-anchor="{anchor}" '
               f'font-weight="{weight}">{s}</text>')


def swatch_for(Eg):
    edge = 1240.0 / Eg
    R = 0.04 + 0.86 / (1 + np.exp(-(LAM - edge) / 10.0))
    return reflectance_to_hex(R)


# --- region strips ---
EV1, EV2 = 1240 / 700, 1240 / 400
els.append(f'<rect x="{X(0):.1f}" y="{YB0}" width="{X(EV1) - X(0):.1f}" height="{YB1-YB0}" fill="#30353d"/>')
steps = 160
for k in range(steps):
    e0 = EV1 + (EV2 - EV1) * k / steps
    e1 = EV1 + (EV2 - EV1) * (k + 1) / steps
    lam = 1240 / ((e0 + e1) / 2)
    els.append(f'<rect x="{X(e0):.2f}" y="{YB0}" width="{X(e1) - X(e0) + 0.35:.2f}" height="{YB1-YB0}" fill="{spectral_hex(lam)}"/>')
els.append(f'<rect x="{X(EV2):.1f}" y="{YB0}" width="{X(EMAX) + 46 - X(EV2):.1f}" height="{YB1-YB0}" fill="#eef1f5"/>')
text((X(0) + X(EV1)) / 2, YB0 + 28, "infrared", 12, "#c4ccd5", "middle", 600)
text((X(EV2) + X(EMAX) + 46) / 2, YB0 + 28, "ultraviolet", 12, MUTED, "middle", 600)
# wavelength ticks over the visible strip
for lam in (700, 600, 500, 400):
    x = X(1240 / lam)
    els.append(f'<line x1="{x:.1f}" y1="{YB0 - 6}" x2="{x:.1f}" y2="{YB0}" stroke="{TEXT}" stroke-width="1"/>')
    text(x, YB0 - 10, f"{lam} nm" if lam in (700, 400) else f"{lam}", 11, TEXT, "middle")

# --- region explanations ---
cols = [((X(0) + X(EV1)) / 2, ["Eg below 1.8 eV", "absorbs every visible color", "→ black, gray, or metallic"]),
        ((X(EV1) + X(EV2)) / 2, ["Eg 1.8 to 3.1 eV", "absorbs only the blue end", "→ yellow, orange, red"]),
        ((X(EV2) + X(EMAX) + 46) / 2, ["Eg above 3.1 eV", "absorbs no visible light", "→ colorless, transparent"])]
for cx, lines in cols:
    for i, s in enumerate(lines):
        text(cx, 20 + 15 * i, s, 12.5 if i == 0 else 12, TEXT if i != 1 else MUTED, "middle", 700 if i == 0 else 400)

# --- energy axis ---
els.append(f'<line x1="{X(0)}" y1="{YB1}" x2="{X(EMAX) + 46:.1f}" y2="{YB1}" stroke="{TEXT}" stroke-width="1.3"/>')
for E in range(0, 5):
    x = X(E)
    els.append(f'<line x1="{x:.1f}" y1="{YB1}" x2="{x:.1f}" y2="{YB1 + 5}" stroke="{TEXT}" stroke-width="1"/>')
    text(x, YB1 + 17, f"{E}", 11, MUTED, "middle")
text(X(EMAX) + 46, YB1 + 17, "eV", 11, MUTED, "end")

# --- materials: true band-gap ticks on the axis, labels in evenly spaced cards below ---
mats = [  # short name, Eg (eV), appearance, swatch override (None = computed)
    ("PbS", 0.4, "black", "#2f3237"),
    ("Si", 1.1, "gray", "#7d838b"),
    ("GaAs", 1.42, "gray", "#6b7178"),
    ("CdSe", 1.73, "near-black", None),
    ("HgS", 2.0, "red", None),
    ("CdS·Se", 2.3, "orange", None),
    ("CdS", 2.42, "yellow", None),
    ("ZnSe", 2.7, "yellow", None),
    ("GaN", 3.4, "colorless", "#ffffff"),
    ("ZnS", 3.6, "colorless", "#ffffff"),
]
n = len(mats)
cx0, cx1 = 72, 628
for k, (name, Eg, look, override) in enumerate(mats):
    x = X(Eg)
    cx = cx0 + (cx1 - cx0) * k / (n - 1)
    col = override or swatch_for(Eg)
    els.append(f'<polygon points="{x:.1f},{YB1 - 1} {x - 5:.1f},{YB1 + 9} {x + 5:.1f},{YB1 + 9}" fill="{TEXT}"/>')
    els.append(f'<line x1="{x:.1f}" y1="{YB1 + 9}" x2="{cx:.1f}" y2="{196}" stroke="#9aa5b1" stroke-width="1"/>')
    els.append(f'<circle cx="{cx:.1f}" cy="{205}" r="9" fill="{col}" stroke="{STROKE}" stroke-width="1"/>')
    text(cx, 231, name, 12, TEXT, "middle", 650)
    text(cx, 246, f"{Eg:g} eV", 11, TEXT, "middle")
    text(cx, 261, look, 11, MUTED, "middle")
    print(f"{name:8s} Eg={Eg:4.2f}  edge={1240/Eg:6.0f} nm  swatch={col}")

text(X(0), 288, "PbS = galena; HgS = vermilion (cinnabar); CdS·Se = cadmium orange; CdS = cadmium yellow.", 11, MUTED, "start")
text(X(0), 304, "Off the scale to the right: diamond (5.5 eV) and sapphire, Al₂O₃ (about 9 eV), both colorless.", 11, MUTED, "start")

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
       f'font-family="Inter, sans-serif">\n<rect width="{W}" height="{H}" fill="#ffffff"/>\n'
       + "\n".join(els) + "\n</svg>\n")
OUT.write_text(svg)
print("wrote", OUT)
