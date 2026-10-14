"""Figure 8.1 - superposition of two equal waves in phase vs. half a wavelength out of phase.
Output: figures/ch08-superposition.svg"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"svg.fonttype": "none", "font.family": "Inter", "font.size": 10,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#9aa5b1", "axes.linewidth": 0.6,
                     "text.color": "#1f2933", "axes.labelcolor": "#52606d"})
AMBER, INK, MUTED, GREEN, RED = "#e09f1f", "#1f2933", "#52606d", "#0b6e4f", "#d1495b"
OUT = Path(__file__).resolve().parents[1] / "ch08-superposition.svg"

x = np.linspace(0, 3, 600)          # in wavelengths
w1 = np.sin(2 * np.pi * x)
fig, axes = plt.subplots(3, 2, figsize=(6.8, 3.9), sharex=True, sharey=True,
                         gridspec_kw=dict(hspace=0.25, wspace=0.12))
cases = [(0.0, "In phase (crests line up)", "constructive: amplitude doubles, intensity × 4"),
         (0.5, "Half a wavelength out of phase", "destructive: crest meets trough, they cancel")]
for col, (shift, title, result) in enumerate(cases):
    w2 = np.sin(2 * np.pi * (x - shift))
    rows = [(w1, AMBER, "wave 1"), (w2, AMBER, "wave 2"), (w1 + w2, INK, "sum")]
    for r, (y, colr, lab) in enumerate(rows):
        ax = axes[r, col]
        ax.axhline(0, color="#d9dee5", lw=0.8, zorder=0)
        ax.plot(x, y, color=colr, lw=2.0 if r < 2 else 2.4)
        ax.set_ylim(-2.4, 2.4)
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.tick_params(bottom=False, labelbottom=False)
        ax.text(-0.05, 0, lab, ha="right", va="center", fontsize=10, color=MUTED,
                transform=ax.get_yaxis_transform()) if col == 0 else None
        if r == 2:
            ax.text(0.5, -0.12, result, ha="center", va="top", fontsize=9.5,
                    color=GREEN if shift == 0 else RED, transform=ax.transAxes)
    axes[0, col].set_title(title, fontsize=10.5, color=INK, fontweight="semibold", pad=6)
# mark the half-wavelength shift on wave 2 (right column)
ax = axes[1, 1]
ax.annotate("", xy=(0.75, 1.65), xytext=(0.25, 1.65),
            arrowprops=dict(arrowstyle="<->", color=MUTED, lw=0.9))
ax.text(0.5, 1.85, "shifted λ/2", ha="center", va="bottom", fontsize=9, color=MUTED)
# dashed guides showing crest-on-crest / crest-on-trough
for col, shift in enumerate([0.0, 0.5]):
    for xc in [0.25, 1.25, 2.25]:
        for r in range(3):
            axes[r, col].axvline(xc, color="#c4ccd5", lw=0.7, ls=(0, (2, 2)), zorder=0)
fig.savefig(OUT, bbox_inches="tight")
print("wrote", OUT)
