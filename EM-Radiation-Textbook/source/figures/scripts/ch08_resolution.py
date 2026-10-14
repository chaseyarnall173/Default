"""Figure 8.5 - Airy patterns of two point sources at three separations (Rayleigh criterion).
Airy intensity I(v) = [2 J1(v)/v]^2 with v = pi D sin(theta)/lambda; first zero at v = 3.8317,
i.e. sin(theta) = 1.22 lambda / D. J1 computed from its integral representation.
Output: figures/ch08-resolution.png (300 dpi)"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

plt.rcParams.update({"font.family": "Inter", "font.size": 10, "text.color": "#1f2933",
                     "axes.edgecolor": "#9aa5b1", "axes.linewidth": 0.6, "axes.labelcolor": "#52606d",
                     "xtick.color": "#52606d", "ytick.color": "#52606d"})
OUT = Path(__file__).resolve().parents[1] / "ch08-resolution.png"
INK, MUTED, AMBER = "#1f2933", "#52606d", "#e09f1f"
cmap = LinearSegmentedColormap.from_list("glow", ["#0d1117", "#7a4a06", "#e09f1f", "#fff6dc"])

tau = np.linspace(0, np.pi, 801)
def J1(v):
    v = np.asarray(v, float)
    return np.trapezoid(np.cos(tau[None, :] - v.reshape(-1, 1) * np.sin(tau[None, :])), tau, axis=1).reshape(v.shape) / np.pi
def airy(v):
    v = np.where(np.abs(v) < 1e-9, 1e-9, v)
    return (2 * J1(v) / v) ** 2
V0 = 3.8317  # first zero = Rayleigh separation

n = 260
g = np.linspace(-9, 9, n)
X, Y = np.meshgrid(g, g)
cases = [(2.0, "Well resolved\n(2 × Rayleigh limit)"), (1.0, "Just resolved\n(Rayleigh criterion)"),
         (0.5, "Not resolved\n(½ × Rayleigh limit)")]
fig, axes = plt.subplots(2, 3, figsize=(6.8, 3.5), gridspec_kw=dict(height_ratios=[1.0, 0.62], hspace=0.12, wspace=0.08))
xline = np.linspace(-9, 9, 900)
for col, (f, title) in enumerate(cases):
    s = f * V0 / 2
    r1 = np.hypot(X + s, Y); r2 = np.hypot(X - s, Y)
    I = airy(r1.ravel()).reshape(r1.shape) + airy(r2.ravel()).reshape(r2.shape)
    ax = axes[0, col]
    ax.imshow(np.power(I / I.max(), 0.45), extent=[g[0], g[-1], g[0], g[-1]], cmap=cmap, vmin=0, vmax=1)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(title, fontsize=10, color=INK, pad=4, linespacing=1.25)
    a = axes[1, col]
    i1, i2 = airy(xline + s), airy(xline - s)
    a.plot(xline, i1, color="#9aa5b1", lw=1.0, ls=(0, (3, 2)))
    a.plot(xline, i2, color="#9aa5b1", lw=1.0, ls=(0, (3, 2)))
    a.plot(xline, i1 + i2, color=AMBER, lw=2.0)
    a.set_xlim(-9, 9); a.set_ylim(0, 1.75)
    a.set_yticks([]); a.set_xticks([])
    for sp in ("top", "right", "left"):
        a.spines[sp].set_visible(False)
axes[1, 0].text(-8.8, 1.72, "brightness along\nthe line through both", fontsize=9, color=MUTED, va="top")
axes[1, 1].annotate("dip of ~26%", xy=(0, 1.47 * 0.5 + 0.0), xytext=(1.6, 1.45), fontsize=9, color=INK,
                    arrowprops=dict(arrowstyle="->", color=INK, lw=0.8))
axes[1, 2].text(3.2, 1.45, "one blob", fontsize=9, color=INK)
fig.savefig(OUT, dpi=300, bbox_inches="tight", facecolor="white")
print("wrote", OUT)
# sanity: dip at Rayleigh separation
s = V0 / 2
print("center/peak ratio at Rayleigh:", (2 * airy(np.array([s]))[0]) / (airy(np.array([0.0]))[0] + airy(np.array([2 * s]))[0]))
