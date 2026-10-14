"""Figure 9.1 - Planck blackbody spectra at 300 K (you), 1000 K (red-hot stove), 3000 K (incandescent
filament) and 5800 K (Sun's surface). (a) absolute spectral radiance on log-log axes;
(b) each curve divided by its own peak. Visible band (400-700 nm) shaded in spectral colors.
Output: figures/ch09-blackbody.svg"""
from pathlib import Path
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch08_colorutil import wavelength_rgb

plt.rcParams.update({"svg.fonttype": "none", "font.family": "Inter", "font.size": 10,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#9aa5b1", "axes.linewidth": 0.6, "axes.labelcolor": "#52606d",
                     "xtick.color": "#52606d", "ytick.color": "#52606d", "text.color": "#1f2933"})
OUT = Path(__file__).resolve().parents[1] / "ch09-blackbody.svg"
h, c, k = 6.626e-34, 3.00e8, 1.381e-23
def B(lam_um, T):   # spectral radiance, W m^-2 sr^-1 um^-1
    l = lam_um * 1e-6
    with np.errstate(over="ignore"):
        return 2 * h * c ** 2 / l ** 5 / np.expm1(h * c / (l * k * T)) * 1e-6
lam = np.logspace(np.log10(0.1), np.log10(100), 2000)
curves = [(300, "300 K: you", "#52606d"), (1000, "1000 K: red-hot stove", "#b3261e"),
          (3000, "3000 K: bulb filament", "#d9730d"), (5800, "5800 K: Sun", "#b8860b")]

fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.8, 3.3), gridspec_kw=dict(wspace=0.28))
for ax in (a1, a2):
    for wl in np.linspace(400, 700, 31):
        ax.axvspan(wl / 1000, (wl + 10) / 1000, color=wavelength_rgb(wl), alpha=0.28, lw=0, zorder=0)
    ax.set_xscale("log"); ax.set_xlim(0.1, 100)
    ax.set_xticks([0.1, 1, 10, 100]); ax.set_xticklabels(["0.1", "1", "10", "100"])
    ax.set_xlabel("wavelength (µm)")
    ax.grid(True, which="major", color="#e4e7eb", lw=0.5); ax.set_axisbelow(True)
for T, lab, col in curves:
    y = B(lam, T)
    a1.plot(lam, y, color=col, lw=1.8)
    lp = 2898 / T
    a1.plot(lp, B(np.array([lp]), T)[0], "o", ms=5, mfc=col, mec="white", mew=1, zorder=5)
    a2.plot(lam, y / y.max(), color=col, lw=1.8)
a1.set_yscale("log"); a1.set_ylim(1e-2, 3e8)
a1.set_yticks([1e-2, 1e1, 1e4, 1e7])
a1.set_ylabel("brightness per µm of wavelength\n(W m⁻² sr⁻¹ µm⁻¹)")
a1.set_title("(a) Hotter is brighter at every wavelength", fontsize=10, loc="left", color="#1f2933", pad=6)
names = {300: "you, 300 K", 1000: "stove, 1000 K", 3000: "filament, 3000 K", 5800: "Sun, 5800 K"}
for T, lab, col in curves:
    lx = 2898 / T * 2.6 if T != 300 else 10.5
    ly = B(np.array([lx]), T)[0] * 4 if T != 300 else 0.04
    a1.text(lx, ly, names[T], color=col, fontsize=10, fontweight="semibold", ha="left", va="bottom")
a1.text(0.12, 0.05, "dots: peaks\n(Wien's law)", fontsize=10, color="#52606d")
a2.set_ylim(0, 1.25); a2.set_yticks([0, 0.5, 1])
a2.set_ylabel("brightness ÷ own peak")
a2.set_title("(b) The peak slides to shorter λ", fontsize=10, loc="left", color="#1f2933", pad=6)
for T, lab, col in curves:
    if T == 5800:
        a2.text(0.36, 0.93, f"{T} K", color=col, fontsize=10, fontweight="semibold", ha="right", va="center")
    else:
        a2.text(2898 / T, 1.13 if T in (3000, 300) else 1.03, f"{T} K", color=col, fontsize=10, fontweight="semibold", ha="center", va="bottom")
a2.text(0.55, 0.06, "visible", fontsize=10, color="#52606d", ha="center")
fig.savefig(OUT, bbox_inches="tight")
print("wrote", OUT)
