"""Figure 8.2 - Huygens' principle at a slit: computed wave field behind a narrow (a = lambda)
and a wide (a = 6 lambda) opening. Each point of the opening is treated as a source of
2-D wavelets (Huygens-Fresnel sum); the plot shows the instantaneous field (crests amber,
troughs slate). Output: figures/ch08-single-slit.png (300 dpi)"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle

plt.rcParams.update({"font.family": "Inter", "font.size": 10, "text.color": "#1f2933"})
OUT = Path(__file__).resolve().parents[1] / "ch08-single-slit.png"
INK, MUTED, WALLF, WALLS, AMBER = "#1f2933", "#52606d", "#d9dee5", "#52606d", "#e09f1f"
cmap = LinearSegmentedColormap.from_list("wave", ["#3e4c59", "#ffffff", "#e09f1f"])

lam = 1.0; k = 2 * np.pi / lam
xs = np.linspace(-3, 15, 720); ys = np.linspace(-8, 8, 640)
X, Y = np.meshgrid(xs, ys)

def field(a):
    U = np.zeros_like(X, dtype=complex)
    n = max(int(a / lam * 40), 8)
    yp = np.linspace(-a / 2, a / 2, n); dy = a / n
    right = X > 0.02
    Xr, Yr = X[right], Y[right]
    acc = np.zeros(Xr.shape, dtype=complex)
    for y0 in yp:
        r = np.hypot(Xr, Yr - y0)
        cos_t = Xr / r
        acc += np.exp(1j * k * r) / np.sqrt(r) * 0.5 * (1 + cos_t) * dy
    U[right] = acc / np.sqrt(1j * lam)
    left = X <= 0
    U[left] = np.exp(1j * k * X[left])
    return U.real

fig, axes = plt.subplots(1, 2, figsize=(6.8, 3.3), gridspec_kw=dict(wspace=0.06))
for ax, a, title, note in [
        (axes[0], 1.0, "Narrow opening:  a ≈ λ", "spreads into nearly\ncircular waves"),
        (axes[1], 6.0, "Wide opening:  a = 6λ", "stays a beam; edges spread\nby an angle ≈ λ/a")]:
    F = field(a)
    ax.imshow(F, extent=[xs[0], xs[-1], ys[0], ys[-1]], origin="lower", cmap=cmap,
              vmin=-0.7, vmax=0.7, interpolation="bilinear")
    wall_w = 0.45
    ax.add_patch(Rectangle((-wall_w / 2, a / 2), wall_w, 8 - a / 2, fc=WALLF, ec=WALLS, lw=0.8))
    ax.add_patch(Rectangle((-wall_w / 2, -8), wall_w, 8 - a / 2, fc=WALLF, ec=WALLS, lw=0.8))
    n_dots = 3 if a < 2 else 9
    for y0 in np.linspace(-a / 2 * 0.8, a / 2 * 0.8, n_dots):
        ax.plot(0.05, y0, "o", ms=3.2, mfc=INK, mec="white", mew=0.6)
    if a > 2:
        th = np.arcsin(lam / a)
        for sgn in (1, -1):
            ax.plot([0, 15], [sgn * a / 2, sgn * (a / 2 + 15 * np.tan(th))], color=INK, lw=0.8, ls=(0, (3, 2)))
    ax.set_xlim(xs[0], xs[-1]); ax.set_ylim(ys[0], ys[-1])
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color("#c4ccd5"); s.set_linewidth(0.6)
    ax.set_title(title, fontsize=10.5, fontweight="semibold", color=INK, pad=5)
    ax.text(14.6, -7.6, note, ha="right", va="bottom", fontsize=9.5, color=INK,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="none", alpha=0.85))
    ax.text(-2.8, 7.6, "incoming\nwave", ha="left", va="top", fontsize=9, color=MUTED,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.85))
    ax.annotate("", xy=(-0.6, -6.6), xytext=(-2.8, -6.6),
                arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.0))
axes[0].annotate("Huygens wavelet\nsources in the opening", xy=(0.15, 0.35), xytext=(3.0, 5.2),
                 fontsize=9, color=INK, ha="left",
                 bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.85),
                 arrowprops=dict(arrowstyle="->", color=INK, lw=0.8))
fig.savefig(OUT, dpi=300, bbox_inches="tight", facecolor="white")
print("wrote", OUT)
