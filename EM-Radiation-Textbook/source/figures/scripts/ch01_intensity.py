"""Generate figures/ch01-intensity.svg: intensity grows as the square of the field amplitude.
Left: waves with amplitude 1, 2, 3 (same wavelength). Right: their relative intensity 1, 4, 9.
Run from source/:  python3 figures/scripts/ch01_intensity.py
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parents[1] / "ch01-intensity.svg"
RED, INK, MUTED, GRID, AMBER = "#d1495b", "#1f2933", "#52606d", "#e4e7eb", "#e09f1f"
plt.rcParams.update({"svg.fonttype": "none", "font.family": "Inter", "font.size": 10.5,
                     "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False})

fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.8, 2.7), gridspec_kw={"width_ratios": [1.45, 1]})
x = np.linspace(0, 2, 500)
offs = [0, 5.0, 11.0]
for amp, off in zip([1, 2, 3], offs):
    a1.axhline(off, color=GRID, lw=0.9, zorder=0)
    a1.plot(x, off + 0.8 * amp * np.sin(2 * np.pi * x), color=RED, lw=2)
    a1.text(-0.08, off, f"E₀ = {amp}", ha="right", va="center", fontsize=10.5, color=INK)
a1.set_xlim(-0.55, 2.02); a1.set_ylim(-1.4, 14)
a1.axis("off")
a1.set_title("(a) Same color, bigger field amplitude", fontsize=10.5, loc="left", fontweight="bold", color=INK)

vals = [1, 4, 9]
ypos = offs
a2.barh(ypos, vals, height=1.5, color=AMBER, zorder=2)
for y, v in zip(ypos, vals):
    a2.text(v + 0.25, y, f"{v}×", va="center", fontsize=10.5, color=INK)
a2.set_yticks([]); a2.set_ylim(-1.4, 14); a2.set_xlim(0, 10.5)
a2.set_xticks([0, 2, 4, 6, 8, 10])
a2.grid(axis="x", color=GRID, lw=0.7, zorder=0)
a2.spines["left"].set_visible(False)
a2.set_xlabel("relative intensity (power per m²)", fontsize=10, color=MUTED)
a2.set_title("(b) Intensity ∝ E₀²", fontsize=10.5, loc="left", fontweight="bold", color=INK)
fig.tight_layout(w_pad=1.5)
fig.savefig(OUT, bbox_inches="tight", facecolor="white")
print("wrote", OUT)
