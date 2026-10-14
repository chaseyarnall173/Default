"""Figure 5.2: how an atom makes a photon.

During a transition the electron is in a superposition of 1s and 2p (exact hydrogen wavefunctions,
lengths in Bohr radii). Its charge density is
    |psi|^2 = (psi_1s^2 + psi_2p^2 + 2 psi_1s psi_2p cos(w t)) / 2,
so the cloud sloshes up and down at f = (E2 - E1)/h. The dipole <z> = 0.745 a0 cos(w t).
For hydrogen 2p -> 1s: dE = 10.2 eV, f = 2.47e15 Hz, period 0.41 fs, photon 122 nm (Lyman-alpha).
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, PowerNorm

OUT = Path(__file__).resolve().parents[1] / "ch05-sloshing.svg"
plt.rcParams.update({"svg.fonttype": "none", "font.family": "Inter", "font.size": 10,
                     "axes.edgecolor": "#52606d", "axes.labelcolor": "#1f2933",
                     "xtick.color": "#52606d", "ytick.color": "#52606d"})
TEXT, MUTED, ELEC, NUC, LIGHT = "#1f2933", "#52606d", "#12a39a", "#8d5a97", "#e09f1f"
cmap = LinearSegmentedColormap.from_list("teal", ["#ffffff", "#9fdcd6", ELEC, "#075e58"])

L = 5.0
x = np.linspace(-L, L, 361)
X, Z = np.meshgrid(x, x)
R = np.hypot(X, Z)
psi1 = np.exp(-R) / np.sqrt(np.pi)
psi2 = Z * np.exp(-R / 2) / (4 * np.sqrt(2 * np.pi))
zbar = 128 * np.sqrt(2) / 243          # <1s|z|2pz> in a0  (= 0.745)

fig = plt.figure(figsize=(6.8, 3.55))
gs = fig.add_gridspec(2, 4, height_ratios=[1.25, 1], hspace=0.55, wspace=0.12)
phases = [0, np.pi / 2, np.pi, 3 * np.pi / 2]
names = ["t = 0", "¼ cycle", "½ cycle", "¾ cycle"]
dens_max = None
for i, (ph, nm) in enumerate(zip(phases, names)):
    d = 0.5 * (psi1 ** 2 + psi2 ** 2 + 2 * psi1 * psi2 * np.cos(ph))
    if dens_max is None:
        dens_max = d.max()
    ax = fig.add_subplot(gs[0, i])
    ax.imshow(d / dens_max, extent=[-L, L, -L, L], origin="lower", cmap=cmap,
              norm=PowerNorm(gamma=0.55, vmin=0, vmax=1), interpolation="bilinear")
    ax.axhline(0, color="#c4ccd5", lw=0.6, ls=":")
    ax.plot(0, 0, "o", ms=3.2, color=NUC, mec="white", mew=0.6)
    zc = zbar * np.cos(ph) * 2.2          # center-of-charge marker, exaggerated x2.2 for visibility
    if abs(zc) > 0.05:
        ax.annotate("", xy=(0, zc), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=TEXT, lw=1.3, mutation_scale=9))
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color("#d9dee5")
    ax.set_title(nm, fontsize=10, color=TEXT, pad=3)
    lab = {0: "cloud shifted up", 1: "centered", 2: "shifted down", 3: "centered"}[i]
    ax.text(0, -L - 0.8, lab, fontsize=9, color=MUTED, ha="center", va="top")

ax = fig.add_subplot(gs[1, :])
t = np.linspace(0, 2.6, 800)
ax.plot(t, zbar * np.cos(2 * np.pi * t), color=ELEC, lw=2)
for k, ph in enumerate(phases):
    tk = ph / (2 * np.pi)
    ax.plot(tk, zbar * np.cos(ph), "o", ms=6, color=ELEC, mec="white", mew=1.2, zorder=3)
ax.axhline(0, color=MUTED, lw=0.8)
ax.set_xlim(0, 2.6); ax.set_ylim(-1.05, 1.95)
ax.set_yticks([-0.745, 0, 0.745]); ax.set_yticklabels(["−0.75", "0", "+0.75"])
ax.set_ylabel("center of charge\n(units of a₀)", fontsize=9)
ax.set_xlabel("time (in cycles; one cycle = 1/f = 0.41 fs for hydrogen’s 10.2 eV jump)", fontsize=9.5)
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
ax.text(0.03, 1.9, "An oscillating charge radiates (Chapter 1), here at exactly f = ΔE / h.", fontsize=9.5,
        color=TEXT, fontweight="bold", va="top")
ax.text(0.03, 1.48, "A real jump lasts ~ns: millions of these cycles, which together make one photon.", fontsize=9, color=MUTED, va="top")

fig.savefig(OUT, bbox_inches="tight", facecolor="white")
print("wrote", OUT, "zbar =", zbar)
