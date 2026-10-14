"""Generate figures/ch03-sun-eye.svg: sunlight's spectrum (modelled as a 5772 K blackbody, per unit
wavelength, outside the atmosphere) and the human eye's daytime sensitivity (CIE photopic V(lambda)),
both normalised to a peak of 1. Run from source/:  python3 figures/scripts/ch03_sun_eye.py
"""
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch03_spectral_color import wavelength_rgb, photopic_v

OUT = Path(__file__).resolve().parents[1] / "ch03-sun-eye.svg"
INK, MUTED, GRID, SUN, EYE = "#1f2933", "#52606d", "#e4e7eb", "#e09f1f", "#0b8a5f"
plt.rcParams.update({"svg.fonttype": "none", "font.family": "Inter", "font.size": 10.5,
                     "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False})

h, c, k, T = 6.626e-34, 2.998e8, 1.381e-23, 5772.0
lam = np.linspace(200, 2000, 1801)
B = 1 / ((lam * 1e-9) ** 5 * (np.exp(h * c / (lam * 1e-9 * k * T)) - 1))
B /= B.max()
V = np.array([photopic_v(l) for l in lam]); V /= V.max()

fig, ax = plt.subplots(figsize=(6.8, 3.2))
ax.axvspan(200, 400, color="#e6dcf5", alpha=0.45, lw=0, zorder=0)
ax.axvspan(700, 2000, color="#f3dcd8", alpha=0.45, lw=0, zorder=0)
ax.fill_between(lam, 0, B, color=SUN, alpha=0.12, lw=0, zorder=1)
ax.plot(lam, B, color=SUN, lw=2.2, zorder=3, label="sunlight (per nm of wavelength)")
ax.plot(lam, V, color=EYE, lw=2.2, zorder=4, label="human eye sensitivity (daylight)")
for l in np.arange(400, 700, 2):
    ax.add_patch(Rectangle((l, -0.11), 2.2, 0.07, color=wavelength_rgb(l + 1), lw=0, zorder=2))
ax.annotate("sunlight peaks near 500 nm", xy=(502, 1.0), xytext=(215, 1.24), fontsize=10, color=INK, va="center",
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8, shrinkB=2))
ax.annotate("eye peaks at 555 nm", xy=(560, 1.0), xytext=(640, 1.12), fontsize=10, color=INK, va="center",
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8, shrinkB=2))
ax.text(285, 0.88, "UV", fontsize=10, color=INK, ha="center", va="center")
ax.text(1460, 0.6, "infrared: about half of sunlight's power,\nbut its photons are too weak for vision", fontsize=10, color=INK, ha="center", va="center")
ax.set_xlim(200, 2000); ax.set_ylim(-0.13, 1.4)
ax.set_xticks([200, 400, 700, 1000, 1500, 2000])
ax.set_yticks([0, 0.5, 1.0]); ax.set_yticklabels(["0", "0.5", "1"])
ax.set_xlabel("wavelength (nm)")
ax.set_ylabel("relative amount")
ax.grid(axis="y", color=GRID, lw=0.7, zorder=0)
ax.legend(loc="upper right", frameon=False, fontsize=10)
fig.tight_layout()
fig.savefig(OUT, bbox_inches="tight", facecolor="white")
print("wrote", OUT)
