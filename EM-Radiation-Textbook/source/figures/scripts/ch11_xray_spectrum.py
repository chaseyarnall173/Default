"""Figure 11.2 - Where X-ray tube photons come from (SCHEMATIC).

Left: energy-level picture of characteristic emission (K-shell vacancy filled from L -> K-alpha,
from M -> K-beta). Right: schematic spectrum from a copper-target tube at two voltages:
Kramers-law bremsstrahlung continuum I(lambda) ~ (lambda/lambda_min - 1)/lambda^2, softened by a
beryllium window, plus Cu K-alpha (0.1542 nm) and K-beta (0.1392 nm) lines.
Line wavelengths: Cu Ka1 8.0463 keV, Ka2 8.0267 keV, Kb1 8.9039 keV (xraydb / Elam tables).
Peak heights are illustrative, not measured.
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parents[1] / "ch11-xray-spectrum.svg"
plt.rcParams.update({"svg.fonttype": "none", "font.family": "Inter", "font.size": 10,
                     "axes.edgecolor": "#52606d", "axes.labelcolor": "#1f2933",
                     "xtick.color": "#52606d", "ytick.color": "#52606d"})
INK, MUTED, GRID = "#1f2933", "#52606d", "#e4e7eb"
LIGHT, ELEC, NUC = "#e09f1f", "#12a39a", "#8d5a97"

HC = 1.23984  # keV*nm
lam = np.linspace(0.02, 0.26, 3000)
# Be window ~0.3 mm: mu/rho(Be) ~ 0.6 cm^2/g at 8 keV scaling ~ E^-3 (photoelectric) + 0.13 (scatter)
E = HC / lam
mu_be = (0.65 * (8.0 / E) ** 3 + 0.13) * 1.85  # 1/cm
window = np.exp(-mu_be * 0.03)

def spectrum(kV):
    """Kramers continuum (peak height scales ~ V^2) + Cu K lines (height ~ (V - 8.98 kV)^1.6)."""
    lmin = HC / kV
    cont = np.where(lam > lmin, (lam / lmin - 1) / lam ** 2, 0.0) * window
    lines_scale = ((kV - 8.98) / (35 - 8.98)) ** 1.6
    g = lambda c, w, h: h * np.exp(-0.5 * ((lam - c) / w) ** 2)
    return cont, lines_scale * (g(0.15418, 0.0011, 2.2) + g(0.13922, 0.0011, 0.45)), lmin


cont35 = spectrum(35)[0]
NORM = 1.0 / cont35.max()

fig = plt.figure(figsize=(6.8, 3.15))
gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 2.25], wspace=0.08)
a0 = fig.add_subplot(gs[0]); a1 = fig.add_subplot(gs[1])

# ---- left: energy levels
a0.set_xlim(0, 1); a0.set_ylim(-0.12, 1.08); a0.axis("off")
levels = [(0.0, "K  (n = 1)"), (0.74, "L  (n = 2)"), (0.88, "M  (n = 3)")]
for y, lab in levels:
    a0.plot([0.28, 0.92], [y, y], color=INK, lw=1.6)
    a0.text(0.26, y, lab, ha="right", va="center", fontsize=10, color=INK)
# vacancy in K
a0.plot(0.42, 0.0, "o", ms=9, mfc="white", mec=ELEC, mew=1.8)
a0.text(0.42, -0.09, "vacancy", ha="center", fontsize=10, color=ELEC)
# electron drops
a0.annotate("", xy=(0.62, 0.02), xytext=(0.62, 0.72), arrowprops=dict(arrowstyle="-|>", color=ELEC, lw=1.6))
a0.annotate("", xy=(0.82, 0.02), xytext=(0.82, 0.86), arrowprops=dict(arrowstyle="-|>", color=ELEC, lw=1.6))
a0.text(0.62, 0.40, "Kα", ha="right", va="center", fontsize=11, color=INK, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))
a0.text(0.82, 0.52, "Kβ", ha="left", va="center", fontsize=11, color=INK, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))
a0.text(0.55, -0.24, "an L or M electron drops into\nthe K vacancy and emits an\nX-ray of a fixed energy",
        ha="center", va="top", fontsize=10, color=MUTED, linespacing=1.15)

# ---- right: spectrum
cols = {35: "#2a78d6", 25: "#eb6834"}
for kV, ytxt in ((35, 2.55), (25, 2.15)):
    cont, lines, lmin = spectrum(kV)
    tot = cont * NORM + lines
    c = cols[kV]
    a1.plot(lam, tot, color=c, lw=2, label=f"{kV} kV tube voltage", solid_joinstyle="round")
    a1.plot([lmin], [0], marker="o", ms=6, color=c, mec="white", mew=1.4, zorder=5, clip_on=False)
    a1.annotate(f"λ$_{{min}}$ = {lmin:.4f} nm ({kV} kV)", xy=(lmin, 0.01), xytext=(0.024, ytxt),
                fontsize=10, color=INK, ha="left", arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
a1.text(0.1580, 2.95, "Cu Kα  0.1542 nm", fontsize=10, color=INK, ha="left", va="center")
a1.text(0.1360, 1.62, "Cu Kβ\n0.1392 nm", fontsize=10, color=INK, ha="right", va="center")
a1.text(0.205, 0.95, "bremsstrahlung\n(continuous)", fontsize=10, color=INK, ha="center")
a1.set_xlim(0.02, 0.26); a1.set_ylim(0, 3.15)
a1.set_yticks([])
a1.set_xlabel("Wavelength (nm)")
a1.set_ylabel("Intensity (schematic)")
for s in ("top", "right"):
    a1.spines[s].set_visible(False)
a1.grid(True, axis="x", color=GRID, lw=0.6); a1.set_axisbelow(True)
a1.legend(frameon=False, loc="upper right", fontsize=10, handlelength=1.5, bbox_to_anchor=(1.0, 0.80))
fig.savefig(OUT, bbox_inches="tight")
print("wrote", OUT)
