"""Figure 7.5 - APPROXIMATE normal-incidence reflectance of polished silver, aluminum, gold and
copper vs wavelength. Smooth curves that follow the familiar textbook shapes: silver's drop near
320 nm (UV), aluminum's broad high reflectance with a shallow dip near 830 nm, gold's rise near
520 nm (interband absorption starts near 2.4 eV), copper's rise near 580 nm. Not measured data.
Writes figures/ch07-metals.svg."""
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch07_colorlib import spectral  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "ch07-metals.svg"
plt.rcParams.update({"svg.fonttype": "none", "font.family": "Inter", "font.size": 10,
                     "axes.edgecolor": "#9aa5b1", "axes.labelcolor": "#1f2933",
                     "xtick.color": "#52606d", "ytick.color": "#52606d"})
TEXT, MUTED = "#1f2933", "#52606d"

lam = np.linspace(300, 800, 501)
ag = 0.04 + 0.93 / (1 + np.exp(-(lam - 336) / 8)) + 0.13 * np.exp(-((lam - 300) / 9) ** 2)
al = 0.92 - 0.05 * np.exp(-((lam - 830) / 90) ** 2)
au = 0.37 + 0.60 / (1 + np.exp(-(lam - 535) / 16))
cu = 0.40 + 0.56 / (1 + np.exp(-(lam - 585) / 14))

fig, ax = plt.subplots(figsize=(6.8, 3.2))
ax.axvspan(400, 700, color="#f3f5f8", zorder=0)
for y, col in ((ag, "#7d8fb3"), (al, "#1c4fb8"), (au, "#c8960c"), (cu, "#a3471b")):
    ax.plot(lam, y, color=col, lw=2, solid_capstyle="round", zorder=3)
# direct labels (text in ink, colored key dash beside each)
labels = [("silver", 425, 1.005, "left", "bottom", "#7d8fb3"),
          ("aluminum", 425, 0.895, "left", "top", "#1c4fb8"),
          ("gold", 527, 0.70, "right", "center", "#c8960c"),
          ("copper", 600, 0.56, "left", "center", "#a3471b")]
for s, x, y, ha, va, col in labels:
    ax.text(x, y, s, ha=ha, va=va, fontsize=10, color=TEXT, fontweight="semibold", zorder=4)
ax.annotate("silver absorbs only in the UV\n(edge near 320 nm)", xy=(322, 0.12), xytext=(345, 0.24),
            fontsize=9, color=MUTED, arrowprops=dict(arrowstyle="-", color="#9aa5b1", lw=1))
ax.annotate("gold and copper absorb\nmuch of the blue and violet", xy=(505, 0.385), xytext=(492, 0.13),
            fontsize=9, color=MUTED, arrowprops=dict(arrowstyle="-", color="#9aa5b1", lw=1))
for l in np.arange(400, 700, 1.0):
    ax.add_patch(Rectangle((l, 0.006), 1.05, 0.04, color=spectral(l + 0.5), lw=0, zorder=2))
ax.text(550, 1.065, "visible", ha="center", fontsize=9, color=MUTED)
ax.set_xlim(300, 800)
ax.set_ylim(0, 1.1)
ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
ax.set_yticklabels(["0", "25%", "50%", "75%", "100%"])
ax.set_xlabel("Wavelength (nm)")
ax.set_ylabel("Reflectance (approximate)")
ax.spines[["top", "right"]].set_visible(False)
ax.spines["left"].set_bounds(0, 1)
ax.grid(axis="y", color="#e4e7eb", lw=0.6)
ax.set_axisbelow(True)
ax.tick_params(length=3)
fig.savefig(OUT, bbox_inches="tight", facecolor="white")
print("wrote", OUT)
