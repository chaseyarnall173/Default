"""Figure 7.3 - "white light in, what's left over comes out": SCHEMATIC reflectance curves for a
red apple skin and a green leaf (shapes typical of published spectra, values approximate).
Colored area = light reflected toward your eye; gray area = light absorbed (mostly becomes heat).
Writes figures/ch07-leftover.svg."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

OUT = Path(__file__).resolve().parents[1] / "ch07-leftover.svg"
plt.rcParams.update({"svg.fonttype": "none", "font.family": "Inter", "font.size": 10,
                     "axes.edgecolor": "#9aa5b1", "axes.labelcolor": "#1f2933",
                     "xtick.color": "#52606d", "ytick.color": "#52606d"})
TEXT, MUTED, ABS = "#1f2933", "#52606d", "#e4e7eb"


def spectral(lam):
    if lam < 440: r, g, b = -(lam - 440) / 60, 0, 1
    elif lam < 490: r, g, b = 0, (lam - 440) / 50, 1
    elif lam < 510: r, g, b = 0, 1, -(lam - 510) / 20
    elif lam < 580: r, g, b = (lam - 510) / 70, 1, 0
    elif lam < 645: r, g, b = 1, -(lam - 645) / 65, 0
    else: r, g, b = 1, 0, 0
    f = 0.3 + 0.7 * (lam - 380) / 40 if lam < 420 else (0.3 + 0.7 * (780 - lam) / 80 if lam > 700 else 1)
    return tuple((max(0, v) * f) ** 0.8 for v in (r, g, b))


lam = np.arange(400, 701, 2.0)
apple = 0.05 + 0.55 / (1 + np.exp(-(lam - 615) / 14))
leaf = (0.05 + 0.11 * np.exp(-0.5 * ((lam - 550) / 28) ** 2)
        - 0.015 * np.exp(-0.5 * ((lam - 675) / 12) ** 2) + 0.35 / (1 + np.exp(-(lam - 712) / 9)))

fig, axes = plt.subplots(1, 2, figsize=(6.8, 2.9), sharey=True)
for ax, R, title, note_xy, note in (
        (axes[0], apple, "Red apple skin", (430, 0.42), "absorbs violet, blue, green\nand yellow; reflects red"),
        (axes[1], leaf, "Green leaf", (420, 0.42), "chlorophyll absorbs blue\nand red; some green escapes")):
    ax.add_patch(Rectangle((400, 0), 300, 1.0, color=ABS, lw=0, zorder=0))
    for l, r in zip(lam, R):
        ax.add_patch(Rectangle((l - 1, 0), 2.05, r, color=spectral(l), lw=0, zorder=1))
    ax.plot(lam, R, color=TEXT, lw=1.4, zorder=3)
    ax.text(403, 0.93, title, fontsize=11, fontweight="semibold", color=TEXT, va="top")
    ax.text(*note_xy, note, fontsize=9.5, color=TEXT, va="bottom", linespacing=1.2)
    ax.text(698, 0.93, "gray = absorbed\n(becomes heat)", fontsize=9, color=MUTED, ha="right", va="top", linespacing=1.15)
    ax.set_xlim(400, 700)
    ax.set_ylim(0, 1.0)
    ax.set_xticks([400, 500, 600, 700])
    ax.set_xlabel("Wavelength (nm)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(length=3)
axes[0].set_ylabel("Fraction of light\nreflected (schematic)")
axes[1].annotate("rising toward the\nnear-infrared", xy=(696, float(leaf[-3])), xytext=(640, 0.30),
                 fontsize=9, color=MUTED, ha="center", arrowprops=dict(arrowstyle="-", color="#9aa5b1", lw=1))
fig.tight_layout(w_pad=1.6)
fig.savefig(OUT, bbox_inches="tight", facecolor="white")
print("wrote", OUT)
