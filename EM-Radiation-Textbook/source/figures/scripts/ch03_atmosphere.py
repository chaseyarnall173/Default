"""Generate figures/ch03-atmosphere.svg: SCHEMATIC atmospheric opacity vs wavelength
(what fraction of each wavelength is blocked before reaching the ground).
Shape follows the familiar NASA-style diagram: ozone/O2 cut off UV below ~290-300 nm; X-rays and
gamma rays are absorbed by the whole air column; water vapor and CO2 absorb much of the infrared
except windows near 3-5 um and 8-14 um; the radio window runs from about 1 cm to ~30 m; below
~10 MHz (lambda > ~30 m) the ionosphere reflects radio waves. Values are illustrative, not data.
Long wavelengths on the left to match Figure 3.1. Run from source/:  python3 figures/scripts/ch03_atmosphere.py
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

OUT = Path(__file__).resolve().parents[1] / "ch03-atmosphere.svg"
INK, MUTED, GRID = "#1f2933", "#52606d", "#e4e7eb"
plt.rcParams.update({"svg.fonttype": "none", "font.family": "Inter", "font.size": 10.5,
                     "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False})

# (wavelength in m, percent blocked) control points
pts = [(1e-12, 100), (2.9e-7, 100), (3.2e-7, 30), (4.0e-7, 18), (5.5e-7, 12), (7.0e-7, 12),
       (9.0e-7, 14), (9.4e-7, 55), (1.0e-6, 15), (1.13e-6, 55), (1.25e-6, 14), (1.4e-6, 95), (1.55e-6, 15),
       (1.8e-6, 30), (1.9e-6, 100), (2.05e-6, 25), (2.3e-6, 18), (2.6e-6, 70), (2.8e-6, 100), (3.0e-6, 60),
       (3.6e-6, 25), (4.1e-6, 35), (4.3e-6, 100), (4.6e-6, 55), (5.2e-6, 85), (5.6e-6, 100), (7.5e-6, 100),
       (8.2e-6, 30), (9.2e-6, 22), (9.6e-6, 60), (10.2e-6, 20), (12.0e-6, 25), (13.5e-6, 45), (14.5e-6, 100),
       (8e-4, 100), (1.1e-3, 80), (2.5e-3, 45), (4.5e-3, 70), (5.0e-3, 100), (5.6e-3, 60), (8e-3, 25),
       (1.35e-2, 40), (1.8e-2, 8), (3e-2, 3), (10, 3), (20, 8), (30, 60), (40, 100), (1e3, 100)]
lx = np.log10([p[0] for p in pts]); oy = np.array([p[1] for p in pts], float)
grid = np.linspace(-12, 3, 3000)
op = np.interp(grid, lx, oy)
lam = 10 ** grid

fig, ax = plt.subplots(figsize=(6.8, 3.3))
ax.fill_between(lam, 0, op, color="#9aa5b1", alpha=0.55, lw=0, zorder=2)
ax.plot(lam, op, color="#52606d", lw=1.2, zorder=3)
ax.set_xscale("log")
ax.set_xlim(1e3, 1e-12)   # inverted: long wavelengths on the left
ax.set_ylim(-26, 138)
ax.set_yticks([0, 50, 100]); ax.set_yticklabels(["0%", "50%", "100%"])
ax.set_ylabel("blocked by the atmosphere")
ax.set_xticks([1e3, 1, 1e-3, 1e-6, 1e-9, 1e-12])
ax.set_xticklabels(["1 km", "1 m", "1 mm", "1 µm", "1 nm", "1 pm"])
ax.xaxis.set_minor_locator(matplotlib.ticker.LogLocator(base=10, subs=(1.0,), numticks=30))
ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
ax.set_xlabel("wavelength (schematic)")
ax.grid(axis="y", color=GRID, lw=0.7, zorder=0)
ax.spines["left"].set_bounds(0, 100)

# band strip below the curve
bands = [("radio", 1e3, 0.3, "#dbe4ee"), ("microwave", 0.3, 1e-3, "#e3dcef"), ("infrared", 1e-3, 7e-7, "#f3dcd8"),
         ("vis", 7e-7, 4e-7, None), ("UV", 4e-7, 1e-8, "#e6dcf5"), ("X-ray", 1e-8, 1e-11, "#d6ebe7"), ("gamma", 1e-11, 1e-12, "#ece6d4")]
for name, a, b, col in bands:
    if col:
        ax.add_patch(Rectangle((b, -24), a - b, 17, color=col, lw=0, zorder=2))
        ax.text(np.sqrt(a * b), -15.5, name, ha="center", va="center", fontsize=10, color=INK, zorder=4)
    else:
        ls = np.linspace(700, 400, 25)
        for l1, l2 in zip(ls[:-1], ls[1:]):
            ax.add_patch(Rectangle((l2 * 1e-9, -24), (l1 - l2) * 1e-9, 17, color=wavelength_rgb((l1 + l2) / 2), lw=0, zorder=2))

notes = [(2e2, 118, "reflected by\nionosphere"), (0.3, 38, "radio window\n(~1 cm to ~30 m)"),
         (2.5e-4, 118, "water vapor and\nCO₂ absorb most IR"), (1e-10, 118, "UV, X-rays and\ngamma rays absorbed")]
for x, y, t in notes:
    ax.text(x, y, t, ha="center", va="center", fontsize=10, color=INK, linespacing=1.1, zorder=5)
ax.annotate("visible\nwindow", xy=(5.2e-7, 45), xytext=(5.2e-7, 118), ha="center", va="center", fontsize=10,
            color=INK, linespacing=1.1, zorder=5, arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.9, shrinkA=8, shrinkB=0))
ax.annotate("IR windows", xy=(1.0e-5, 30), xytext=(2.2e-5, 62), ha="center", va="center", fontsize=10, color=INK, zorder=5,
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"),
            arrowprops=dict(arrowstyle="-", color=INK, lw=0.8))
fig.tight_layout()
fig.savefig(OUT, bbox_inches="tight", facecolor="white")
print("wrote", OUT)
