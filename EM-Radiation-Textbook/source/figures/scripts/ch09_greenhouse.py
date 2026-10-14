"""Figure 9.5 - the greenhouse effect in one plot. Blackbody spectral radiance B_lambda
(per unit wavelength), each normalized to its peak, for sunlight (5800 K) and Earth's surface (288 K).
Shaded: main absorption bands of the atmosphere (simplified, approximate edges): O3 (UV, <0.3 um),
CO2 (4.2-4.4 um and 13-17 um), H2O (5.5-7.5 um and >18 um), O3 (9.4-9.9 um).
Output: figures/ch09-greenhouse.svg"""
from pathlib import Path
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch08_colorutil import wavelength_rgb

plt.rcParams.update({"svg.fonttype": "none", "font.family": "Inter", "font.size": 10,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#9aa5b1", "axes.linewidth": 0.6, "axes.labelcolor": "#52606d",
                     "xtick.color": "#52606d", "ytick.color": "#52606d", "text.color": "#1f2933"})
OUT = Path(__file__).resolve().parents[1] / "ch09-greenhouse.svg"
INK, MUTED, GOLD = "#1f2933", "#52606d", "#c58a0b"
h, c, k = 6.626e-34, 3.00e8, 1.381e-23
lam = np.logspace(-1, 2, 3000)
def B(lum, T):
    l = lum * 1e-6
    with np.errstate(over="ignore"):
        return 2 * h * c ** 2 / l ** 5 / np.expm1(h * c / (l * k * T))
sun = B(lam, 5800); sun /= sun.max()
earth = B(lam, 288); earth /= earth.max()

fig, ax = plt.subplots(figsize=(6.8, 3.2))
bands = [(0.1, 0.3, "O₃\n(UV)"), (4.2, 4.4, ""), (5.5, 7.5, "H₂O"), (9.4, 9.9, ""),
         (13, 17, "CO₂"), (18, 100, "H₂O")]
for a, b, lab in bands:
    ax.axvspan(a, b, color="#c9d3de", alpha=0.55, lw=0, zorder=0)
    if lab:
        ax.text(np.sqrt(a * b), 1.13, lab, ha="center", va="bottom", fontsize=10, color=MUTED)
ax.text(4.3, 1.13, "CO₂", ha="center", va="bottom", fontsize=10, color=MUTED)
ax.text(9.65, 1.13, "O₃", ha="center", va="bottom", fontsize=10, color=MUTED)
for wl in np.linspace(400, 690, 30):
    ax.axvspan(wl / 1000, (wl + 10) / 1000, ymin=0, ymax=0.06, color=wavelength_rgb(wl), lw=0, zorder=1)
ax.plot(lam, sun, color=GOLD, lw=2)
ax.plot(lam, earth, color=INK, lw=2)
ax.annotate("", xy=(8.0, 0.16), xytext=(13.0, 0.16), arrowprops=dict(arrowstyle="<->", color="#0b6e4f", lw=1))
ax.text(10.2, 0.20, "window\n8\u201313 \u00b5m", ha="center", va="bottom", fontsize=10, color="#0b6e4f")
ax.text(0.78, 1.03, "sunlight in (5800 K):\nmostly passes through", fontsize=10, color=GOLD, va="top", fontweight="semibold")
ax.text(19.5, 1.03, "Earth\u2019s glow out\n(288 K): partly\nabsorbed", fontsize=10, color=INK, va="top", fontweight="semibold")
ax.set_xscale("log"); ax.set_xlim(0.1, 100); ax.set_ylim(0, 1.3)
ax.set_xticks([0.1, 0.3, 1, 3, 10, 30, 100]); ax.set_xticklabels(["0.1", "0.3", "1", "3", "10", "30", "100"])
ax.set_yticks([0, 0.5, 1])
ax.set_xlabel("wavelength (µm)")
ax.set_ylabel("emission ÷ own peak")
ax.grid(True, which="major", axis="y", color="#e4e7eb", lw=0.5); ax.set_axisbelow(True)
fig.savefig(OUT, bbox_inches="tight")
print("wrote", OUT)
