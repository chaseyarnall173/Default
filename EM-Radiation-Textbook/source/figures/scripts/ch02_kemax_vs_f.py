"""Generate figures/ch02-kemax-vs-f.svg: maximum photoelectron kinetic energy vs light frequency
for sodium (phi = 2.28 eV) and copper (phi = 4.7 eV), using KE_max = hf - phi.
Work functions: HyperPhysics table (CRC Handbook values). h = 4.136e-15 eV*s.
Run from source/:  python3 figures/scripts/ch02_kemax_vs_f.py
"""
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch03_spectral_color import wavelength_rgb

OUT = Path(__file__).resolve().parents[1] / "ch02-kemax-vs-f.svg"
INK, MUTED, GRID = "#1f2933", "#52606d", "#e4e7eb"
NA_C, CU_C = "#12a39a", "#c2410c"
H_EV = 4.136e-15  # eV*s
plt.rcParams.update({"svg.fonttype": "none", "font.family": "Inter", "font.size": 10.5,
                     "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False})

fig, ax = plt.subplots(figsize=(6.8, 3.15))
f = np.linspace(0, 16, 800)            # units of 1e14 Hz
for phi, col, name in ((2.28, NA_C, "sodium, φ = 2.28 eV"), (4.7, CU_C, "copper, φ = 4.7 eV")):
    f0 = phi / (H_EV * 1e14)
    ke = np.where(f >= f0, H_EV * 1e14 * f - phi, 0.0)
    ax.plot(f[f >= f0], ke[f >= f0], color=col, lw=2.2, label=name, solid_capstyle="round", zorder=3)
    ax.plot([0, f0], [0, 0], color=col, lw=2.2, alpha=0.35, zorder=2)
    ax.plot([f0], [0], "o", ms=7, color=col, mec="white", mew=1.6, zorder=4)
    ax.annotate(f"threshold f₀ = {f0:.1f}×10¹⁴ Hz\n(λ₀ = {1240 / phi:.0f} nm)", xy=(f0, 0), xytext=(f0 - 0.2, 1.45 if phi < 3 else 0.62),
                fontsize=10, color=INK, ha="right", va="bottom",
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.text(16.15, H_EV * 1e14 * 16 - phi, name.split(",")[0], color=INK, fontsize=10.5, va="center", ha="left")

# visible band strip along the bottom of the plot
for lam in np.arange(400, 751, 2):
    fr = 3.0e8 / (lam * 1e-9) / 1e14
    ax.add_patch(Rectangle((fr - 0.04, -0.62), 0.09, 0.22, color=wavelength_rgb(lam), lw=0, zorder=1))
ax.text(9.4, -0.51, "ultraviolet →", fontsize=10, color=MUTED, ha="center", va="center")
ax.text(2.6, -0.51, "← infrared", fontsize=10, color=MUTED, ha="center", va="center")

# slope annotation
ax.annotate("", xy=(13.0, H_EV * 1e14 * 13 - 2.28), xytext=(11.0, H_EV * 1e14 * 11 - 2.28),
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=0))
ax.plot([11, 13, 13], [H_EV * 1e14 * 11 - 2.28] * 2 + [H_EV * 1e14 * 13 - 2.28], color=MUTED, lw=0.9)
ax.text(13.2, 2.45, "slope = h\n(same for every metal)", fontsize=10, color=INK, va="center")
ax.text(0.25, 0.08, "however bright", fontsize=10, color=MUTED, va="bottom")
ax.text(0.25, 0.42, "no electrons at all,", fontsize=10, color=MUTED, va="bottom")
ax.text(0.25, 0.76, "below threshold:", fontsize=10, color=MUTED, va="bottom")

ax.set_xlim(0, 16); ax.set_ylim(-0.65, 4.6)
ax.set_xlabel("frequency of light f  (×10¹⁴ Hz)")
ax.set_ylabel("KE of fastest electron (eV)")
ax.set_yticks([0, 1, 2, 3, 4])
ax.grid(axis="y", color=GRID, lw=0.7, zorder=0)
ax.legend(loc="upper left", frameon=False, fontsize=10)
ax.spines["bottom"].set_position(("data", -0.65))
fig.tight_layout()
fig.savefig(OUT, bbox_inches="tight", facecolor="white")
print("wrote", OUT)
