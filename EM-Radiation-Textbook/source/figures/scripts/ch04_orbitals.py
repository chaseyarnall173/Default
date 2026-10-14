"""Figure 4.3: hydrogen 1s and 2p electron-density slices plus radial probability curves.

Exact hydrogen wavefunctions (lengths in Bohr radii a0 = 0.0529 nm):
  1s : |psi|^2 ~ exp(-2r)          radial probability P(r) = 4 r^2 exp(-2r)        (peak at r = a0)
  2pz: |psi|^2 ~ z^2 exp(-r)       radial probability P(r) = r^4 exp(-r) / 24      (peak at r = 4 a0)
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, PowerNorm

OUT = Path(__file__).resolve().parents[1] / "ch04-orbitals.svg"
plt.rcParams.update({"svg.fonttype": "none", "font.family": "Inter", "font.size": 10,
                     "axes.edgecolor": "#52606d", "axes.labelcolor": "#1f2933",
                     "xtick.color": "#52606d", "ytick.color": "#52606d"})
TEXT, MUTED, ELEC, NUC = "#1f2933", "#52606d", "#12a39a", "#8d5a97"
cmap = LinearSegmentedColormap.from_list("teal", ["#ffffff", "#9fdcd6", ELEC, "#075e58"])

L = 7.5
x = np.linspace(-L, L, 501)
X, Z = np.meshgrid(x, x)
R = np.hypot(X, Z)
d1s = np.exp(-2 * R)
d2p = Z ** 2 * np.exp(-R)

fig = plt.figure(figsize=(6.8, 2.7))
gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 1.45], wspace=0.5)

def slice_panel(ax, dens, title, note):
    ax.imshow(dens / dens.max(), extent=[-L, L, -L, L], origin="lower", cmap=cmap,
              norm=PowerNorm(gamma=0.35, vmin=0, vmax=1), interpolation="bilinear")
    ax.plot(0, 0, "o", ms=3.2, color=NUC, mec="white", mew=0.6)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color("#d9dee5")
    ax.set_title(title, fontsize=10.5, color=TEXT, fontweight="bold", pad=4)
    # 0.1 nm scale bar (= 1.89 a0)
    ax.plot([-L + 1, -L + 1 + 0.1 / 0.0529], [-L + 1.1, -L + 1.1], color=TEXT, lw=1.6)
    ax.text(-L + 1.4 + 0.1 / 0.0529, -L + 0.75, "0.1 nm", fontsize=9, color=TEXT)
    ax.text(0, -L - 1.2, note, fontsize=9, color=MUTED, ha="center", va="top", linespacing=1.3)

ax1 = fig.add_subplot(gs[0]); slice_panel(ax1, d1s, "1s (ground state)", "spherical;\ndensest at the center")
ax2 = fig.add_subplot(gs[1]); slice_panel(ax2, d2p, "2p (excited state)", "two lobes; zero density\non the midplane (a node)")

# radial probability
ax3 = fig.add_subplot(gs[2])
r = np.linspace(0, 14, 600)
P1 = 4 * r ** 2 * np.exp(-2 * r)
P2 = r ** 4 * np.exp(-r) / 24
ax3.plot(r, P1, color=ELEC, lw=2)
ax3.plot(r, P2, color="#075e58", lw=2, ls=(0, (5, 2)))
# 90% radius of 1s: solve 1 - exp(-2x)(1+2x+2x^2) = 0.9
xs = np.linspace(0, 10, 100001)
cum = 1 - np.exp(-2 * xs) * (1 + 2 * xs + 2 * xs ** 2)
r90 = xs[np.searchsorted(cum, 0.9)]
mask = r <= r90
ax3.fill_between(r[mask], 0, P1[mask], color=ELEC, alpha=0.12, lw=0)
ax3.axvline(1, color=MUTED, lw=0.8, ls=":")
ax3.text(1.25, 0.585, "peak at a₀ (most\nprobable distance)", fontsize=9, color=MUTED, va="top")
ax3.annotate(f"shaded: 90% chance\nof being within {r90:.1f} a₀", xy=(1.9, 0.12), xytext=(4.6, 0.36),
             fontsize=9, color=TEXT, arrowprops=dict(arrowstyle="-", color=TEXT, lw=0.7))
ax3.text(1.75, 0.43, "1s", fontsize=10, color=ELEC, fontweight="bold")
ax3.text(6.6, 0.18, "2p", fontsize=10, color="#075e58", fontweight="bold")
ax3.text(8.8, 0.07, "tails never\nreach zero", fontsize=9, color=MUTED)
ax3.set_xlim(0, 14); ax3.set_ylim(0, 0.6)
ax3.set_xlabel("distance from nucleus, r (units of a₀ = 0.0529 nm)", fontsize=9.5)
ax3.set_ylabel("probability per unit r", fontsize=9.5)
ax3.spines["top"].set_visible(False); ax3.spines["right"].set_visible(False)
ax3.grid(True, color="#e4e7eb", lw=0.6); ax3.set_axisbelow(True)
ax3.set_yticks([0, 0.2, 0.4, 0.6])
ax3.set_title("How far out is the electron?", fontsize=10.5, color=TEXT, fontweight="bold", pad=4)

fig.savefig(OUT, bbox_inches="tight", facecolor="white")
print("wrote", OUT, "r90 =", r90)
