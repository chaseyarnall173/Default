"""Figure 7.6 - (a) Rayleigh scattering strength vs wavelength, proportional to 1/lambda^4 and
normalized to 1 at 700 nm; (b) why the noon sky is blue and the setting sun is red: path length
through the atmosphere (schematic, atmosphere thickness greatly exaggerated).
Writes figures/ch07-sky.svg."""
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Wedge, Circle, FancyArrowPatch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch07_colorlib import spectral  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "ch07-sky.svg"
plt.rcParams.update({"svg.fonttype": "none", "font.family": "Inter", "font.size": 10,
                     "axes.edgecolor": "#9aa5b1", "axes.labelcolor": "#1f2933",
                     "xtick.color": "#52606d", "ytick.color": "#52606d"})
TEXT, MUTED = "#1f2933", "#52606d"

fig, (ax, bx) = plt.subplots(1, 2, figsize=(6.8, 3.1), gridspec_kw={"width_ratios": [1.0, 1.05]})

# ---------------- (a) ----------------
lam = np.arange(400, 701, 1.0)
rel = (700.0 / lam) ** 4
for l, r in zip(lam, rel):
    ax.add_patch(Rectangle((l - 0.5, 0), 1.05, r, color=spectral(l), lw=0, alpha=0.85))
ax.plot(lam, rel, color=TEXT, lw=1.4)
for l0, lab, dx, dy in ((400, "400 nm: 9.4×", 14, 0.0), (450, "450 nm: 5.9×", 14, 0.3)):
    v = (700 / l0) ** 4
    ax.plot([l0], [v], "o", ms=6.5, mfc=TEXT, mec="white", mew=1.5, zorder=5)
    ax.text(l0 + dx, v + dy, lab, fontsize=9.5, color=TEXT, va="center", fontweight="semibold")
ax.text(700, 2.45, "700 nm: 1×", fontsize=9.5, color=TEXT, ha="right", fontweight="semibold")
ax.set_xlim(400, 700)
ax.set_ylim(0, 10.2)
ax.set_xticks([400, 500, 600, 700])
ax.set_xlabel("Wavelength (nm)")
ax.set_ylabel("Scattering strength\n(relative to 700 nm)")
ax.spines[["top", "right"]].set_visible(False)
ax.tick_params(length=3)
ax.set_title("(a) Scattering goes as 1/λ⁴", fontsize=10.5, loc="left", color=TEXT, fontweight="semibold")

# ---------------- (b) ----------------
bx.axis("off")
xs = np.linspace(-10, 7, 300)
yg = -xs ** 2 / 60
ya = 2.0 - xs ** 2 / 60
bx.fill_between(xs, -2.6, yg, color="#d9dee5", lw=0)
bx.fill_between(xs, yg, ya, color="#dcebf7", lw=0)
bx.plot(xs, yg, color="#52606d", lw=1.2)
bx.plot(xs, ya, color="#9aa5b1", lw=0.8)
bx.plot([0], [0], "o", ms=6, color=TEXT, zorder=6)
bx.text(0.25, -0.45, "you", fontsize=9.5, color=TEXT)


def arrow(x0, y0, x1, y1, col, lw=1.6, ms=10):
    bx.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>", color=col, lw=lw, mutation_scale=ms, shrinkA=0, shrinkB=0))


BLUE = "#3f63e8"
# noon
bx.plot([0], [3.95], "o", ms=15, color="#f4d03f", mec="#e0b000", zorder=6)
arrow(0, 3.5, 0, 0.18, "#e09f1f", lw=2.2, ms=12)
for ang in (25, 155, 205, 335):
    a = np.radians(ang)
    arrow(0, 1.05, 1.5 * np.cos(a), 1.05 + 0.55 * np.sin(a), BLUE, lw=1.3, ms=8)
bx.text(0.75, 3.95, "Noon: short path through air;\nsun looks white, and scattered\nblue fills the whole sky", fontsize=8.8, color=TEXT, va="center", linespacing=1.15)
# sunset
sx, sy = -9.3, 1.0
bx.plot([sx], [sy], "o", ms=15, color="#e8590c", zorder=6)
arrow(sx + 0.5, sy - 0.05, -0.25, 0.04, "#e8590c", lw=2.2, ms=12)
for x in (-7.2, -5.0, -2.8):
    y = sy + (0.04 - sy) * (x - sx) / (0.0 - sx)
    arrow(x, y, x - 0.5, y + 0.75, BLUE, lw=1.2, ms=7)
    arrow(x, y, x + 0.6, y - 0.6, BLUE, lw=1.2, ms=7)
bx.text(-9.8, -0.95, "Sunset: long path through air;\nblue is scattered out on the way,\nso the sun looks orange-red", fontsize=8.8, color=TEXT, va="top", linespacing=1.15)
bx.text(5.6, 1.15, "air (thickness\nexaggerated)", fontsize=8.3, color=MUTED, ha="center", va="center", linespacing=1.1)
bx.set_xlim(-10, 7)
bx.set_ylim(-2.6, 4.7)
bx.set_title("(b) Noon vs. sunset", fontsize=10.5, loc="left", color=TEXT, fontweight="semibold")

fig.tight_layout(w_pad=1.0)
fig.savefig(OUT, bbox_inches="tight", facecolor="white")
print("wrote", OUT, "ratio 450/700 =", round((700 / 450) ** 4, 2), "400/700 =", round((700 / 400) ** 4, 2))
