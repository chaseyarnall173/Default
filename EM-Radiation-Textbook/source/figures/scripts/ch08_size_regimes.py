"""Figure 8.6 - scattering efficiency of a water sphere (m = 1.33) vs. size/wavelength, computed
with Mie theory (Bohren & Huffman BHMIE algorithm) and the small-particle Rayleigh limit
Q = (8/3) x^4 |(m^2-1)/(m^2+2)|^2, x = pi d / lambda. Output: figures/ch08-size-regimes.svg"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"svg.fonttype": "none", "font.family": "Inter", "font.size": 10,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#9aa5b1", "axes.linewidth": 0.6, "axes.labelcolor": "#52606d",
                     "xtick.color": "#52606d", "ytick.color": "#52606d", "text.color": "#1f2933"})
OUT = Path(__file__).resolve().parents[1] / "ch08-size-regimes.svg"
INK, MUTED, AMBER, GREEN, RED = "#1f2933", "#52606d", "#e09f1f", "#0b6e4f", "#d1495b"

def qsca_mie(x, m=1.33):
    nstop = int(x + 4 * x ** (1 / 3) + 2)
    y = m * x
    nmx = int(max(nstop, abs(y))) + 16
    D = np.zeros(nmx + 1, dtype=complex)
    for n in range(nmx, 0, -1):
        D[n - 1] = n / y - 1 / (D[n] + n / y)
    psi0, psi1 = np.cos(x), np.sin(x)
    chi0, chi1 = -np.sin(x), np.cos(x)
    xi1 = complex(psi1, -chi1)
    q = 0.0
    for n in range(1, nstop + 1):
        psi = (2 * n - 1) * psi1 / x - psi0
        chi = (2 * n - 1) * chi1 / x - chi0
        xi = complex(psi, -chi)
        an = ((D[n] / m + n / x) * psi - psi1) / ((D[n] / m + n / x) * xi - xi1)
        bn = ((m * D[n] + n / x) * psi - psi1) / ((m * D[n] + n / x) * xi - xi1)
        q += (2 * n + 1) * (abs(an) ** 2 + abs(bn) ** 2)
        psi0, psi1, chi0, chi1 = psi1, psi, chi1, chi
        xi1 = complex(psi1, -chi1)
    return 2 * q / x ** 2

m = 1.33
K2 = abs((m ** 2 - 1) / (m ** 2 + 2)) ** 2
ratio = np.logspace(-4, 2, 1500)          # d / lambda
x = np.pi * ratio
Q = np.array([(8 / 3) * xi ** 4 * K2 if xi < 0.05 else qsca_mie(xi, m) for xi in x])
Qr = (8 / 3) * x ** 4 * K2

fig, ax = plt.subplots(figsize=(6.8, 3.6))
ax.axvspan(1e-4, 0.1, color="#eef4fd", zorder=0)
ax.axvspan(0.1, 10, color="#fdf7e9", zorder=0)
ax.axvspan(10, 1e3, color="#ecf8f3", zorder=0)
ax.plot(ratio, Qr, color=MUTED, lw=1.0, ls=(0, (4, 3)))
ax.plot(ratio, Q, color=INK, lw=1.8)
ax.plot([100, 1e3], [2, 2], color=INK, lw=1.8)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlim(1e-4, 1e3); ax.set_ylim(1e-16, 30)
ax.set_xlabel("object size ÷ wavelength  (d / λ)")
ax.set_ylabel("scattering strength per area\n(efficiency Q)")
ax.grid(True, which="major", color="#e4e7eb", lw=0.5)
ax.set_axisbelow(True)
ax.set_yticks([1e-15, 1e-12, 1e-9, 1e-6, 1e-3, 1])
for xt, lab, col in [(0.0035, "Rayleigh: d ≪ λ\nscattering ∝ (d/λ)⁴", "#2e6fdb"),
                     (2.4, "Mie: d ∼ λ\nstrong, wiggly", "#a86a12"),
                     (150, "geometric optics:\nd ≫ λ, shadows", GREEN)]:
    ax.text(xt, 4e-2 if xt > 0.5 else 1.2e-1, lab, ha="center", va="top", fontsize=9.5, color=col)
ax.text(2.2e-3, 1e-13, "slope 4: halve d/λ and\nscattering drops 16×", fontsize=9.5,
        color=MUTED, rotation=0, ha="left")
# examples for visible light (lambda = 500 nm)
ex = [(0.3e-9 / 500e-9, "air molecule\nin sunlight"), (0.1 / 500, None),
      (0.2e-6 / 500e-9, "smoke particle\n(0.2 µm) in sunlight"),
      (10e-6 / 500e-9, "cloud droplet\nin sunlight")]
for r, lab in ex:
    if lab is None:
        continue
    q = (8 / 3) * (np.pi * r) ** 4 * K2 if np.pi * r < 0.05 else qsca_mie(np.pi * r, m)
    ax.plot(r, q, "o", ms=6, mfc=AMBER, mec="white", mew=1.2, zorder=5)
    dy = 30 if r < 1 else 1 / 2000
    ax.annotate(lab, xy=(r, q), xytext=(r * (1.0 if r > 1 else 1.0), q * (2000 if r < 0.1 else 1e-4)),
                ha="center", va="bottom" if r < 0.1 else "top", fontsize=9, color=INK,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.7))
fig.savefig(OUT, bbox_inches="tight")
print("wrote", OUT)
for r in [0.01, 0.1, 0.38, 1, 10]:
    print(r, qsca_mie(np.pi * r))
