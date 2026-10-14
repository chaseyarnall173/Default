"""Generate figures/ch02-double-slit-buildup.svg: simulated arrival points of single photons on a
screen behind two slits. Each photon lands at one random spot; the probability of landing at x
follows the wave intensity I(x) = cos^2(pi x) * sinc^2(x / 4.5) (fringe spacing = 1 unit).
This is a simulation that reproduces what single-photon experiments show.
Run from source/:  python3 figures/scripts/ch02_double_slit_buildup.py
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parents[1] / "ch02-double-slit-buildup.svg"
INK, MUTED, AMBER = "#1f2933", "#52606d", "#e09f1f"
plt.rcParams.update({"svg.fonttype": "none", "font.family": "Inter", "font.size": 10.5})

rng = np.random.default_rng(7)
XMAX = 5.5


def intensity(x):
    return np.cos(np.pi * x) ** 2 * np.sinc(x / 4.5) ** 2


def sample(n):
    out = []
    while len(out) < n:
        x = rng.uniform(-XMAX, XMAX, 4 * n)
        keep = rng.uniform(0, 1, 4 * n) < intensity(x)
        out.extend(x[keep].tolist())
    return np.array(out[:n])


counts = [20, 200, 2000, 20000]
fig, axes = plt.subplots(1, 4, figsize=(6.8, 2.1), sharey=True)
for ax, n in zip(axes, counts):
    x = sample(n)
    y = rng.uniform(0, 1, n)
    size = {20: 9, 200: 5, 2000: 1.6, 20000: 0.35}[n]
    ax.set_facecolor("#1f2933")
    ax.scatter(x, y, s=size, c="#f6e3b0", lw=0, rasterized=True)
    ax.set_xlim(-XMAX, XMAX); ax.set_ylim(0, 1)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_title(f"{n:,} photons", fontsize=10.5, color=INK, pad=5)
# wave prediction under the last panel
xx = np.linspace(-XMAX, XMAX, 600)
axes[-1].plot(xx, 0.02 + 0.3 * intensity(xx), color=AMBER, lw=1.4)
fig.subplots_adjust(left=0.01, right=0.99, top=0.86, bottom=0.02, wspace=0.06)
fig.savefig(OUT, facecolor="white", dpi=300)
print("wrote", OUT)
