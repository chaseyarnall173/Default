"""Generate figures/ch01-wave-anatomy.svg: wavelength and amplitude (snapshot in space) and
period (time trace at one point) for an EM wave's electric field.
Run from source/:  python3 figures/scripts/ch01_wave_anatomy.py
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parents[1] / "ch01-wave-anatomy.svg"
RED, INK, MUTED, GRID = "#d1495b", "#1f2933", "#52606d", "#e4e7eb"
plt.rcParams.update({"svg.fonttype": "none", "font.family": "Inter", "font.size": 10.5,
                     "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False})

fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.8, 2.55))
x = np.linspace(0, 2.25, 600)
for ax, xlabel, title in ((a1, "position along the beam  →", "(a) Snapshot of the wave at one instant"),
                          (a2, "time at one fixed spot  →", "(b) Watching one spot as time passes")):
    ax.plot(x, np.sin(2 * np.pi * x), color=RED, lw=2, solid_capstyle="round")
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.set_ylim(-1.6, 1.75); ax.set_xlim(0, 2.25)
    ax.set_yticks([]); ax.set_xticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_xlabel(xlabel, fontsize=10, color=MUTED, loc="right")
    ax.set_title(title, fontsize=10.5, color=INK, loc="left", fontweight="bold")
    ax.text(0.0, 1.62, "E", color=RED, fontsize=11, fontweight="bold", va="center")

def span(ax, x0, x1, y, label):
    ax.annotate("", xy=(x0, y), xytext=(x1, y),
                arrowprops=dict(arrowstyle="<->", color=INK, lw=1.1, shrinkA=0, shrinkB=0))
    ax.text((x0 + x1) / 2, y + 0.1, label, ha="center", va="bottom", fontsize=10.5, color=INK)
    for xx in (x0, x1):
        ax.plot([xx, xx], [y - 0.06, 1.0], color=MUTED, lw=0.8, ls=(0, (2, 2)))

span(a1, 0.25, 1.25, 1.25, "wavelength λ (meters)")
# amplitude marker
a1.annotate("", xy=(0.75, -1.0), xytext=(0.75, 0.0),
            arrowprops=dict(arrowstyle="<->", color=INK, lw=1.1, shrinkA=0, shrinkB=0))
a1.text(0.75, -1.12, "amplitude E₀ (V/m)", fontsize=10, color=INK, ha="center", va="top")
span(a2, 0.25, 1.25, 1.25, "period T (seconds)")
a2.text(0.75, -1.12, "frequency f = 1/T (Hz)", fontsize=10, color=INK, ha="center", va="top")

fig.tight_layout(w_pad=2.0)
fig.savefig(OUT, bbox_inches="tight", transparent=False, facecolor="white")
print("wrote", OUT)
