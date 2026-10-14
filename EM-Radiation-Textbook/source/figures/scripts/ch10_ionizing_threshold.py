"""Figure 10.1 - The ionizing threshold on the electromagnetic spectrum.

Photon energy (log scale) with the conventional ionizing threshold (~10 eV = 124 nm),
the range of conventions (10-33 eV), the range of atomic ionization energies
(Cs 3.89 eV ... He 24.59 eV, NIST), and some everyday photons.
Run from anywhere: python3 ch10_ionizing_threshold.py
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

OUT = Path(__file__).resolve().parents[1] / "ch10-ionizing-threshold.svg"
plt.rcParams.update({"svg.fonttype": "none", "font.family": "Inter", "font.size": 10})
INK, MUTED, RULE = "#1f2933", "#52606d", "#d9dee5"
ION = "#c2410c"

def wl_to_rgb(nm):
    """Rough visible-spectrum color for a wavelength (nm)."""
    if nm < 440: r, g, b = -(nm - 440) / 60, 0.0, 1.0
    elif nm < 490: r, g, b = 0.0, (nm - 440) / 50, 1.0
    elif nm < 510: r, g, b = 0.0, 1.0, -(nm - 510) / 20
    elif nm < 580: r, g, b = (nm - 510) / 70, 1.0, 0.0
    elif nm < 645: r, g, b = 1.0, -(nm - 645) / 65, 0.0
    else: r, g, b = 1.0, 0.0, 0.0
    f = 0.3 + 0.7 * (nm - 380) / 40 if nm < 420 else (0.3 + 0.7 * (700 - nm) / 50 if nm > 650 else 1.0)
    return (max(r, 0) * f, max(g, 0) * f, max(b, 0) * f)

fig, ax = plt.subplots(figsize=(6.8, 3.7))
ax.set_xscale("log")
xmin, xmax = 1e-7, 1e7
ax.set_xlim(xmin, xmax)
ax.set_ylim(0, 1)
for s in ["left", "right", "top"]:
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(MUTED)
ax.set_yticks([])
ax.set_xlabel("Photon energy (eV)", color=INK)
ax.tick_params(axis="x", colors=MUTED, labelcolor=INK)
ax.set_xticks([1e-6, 1e-4, 1e-2, 1, 1e2, 1e4, 1e6])
ax.set_xticklabels(["10$^{-6}$", "10$^{-4}$", "0.01", "1", "100", "10$^{4}$", "10$^{6}$"])

# ionizing region tint
ax.add_patch(Rectangle((10, 0), xmax - 10, 1, color=ION, alpha=0.07, lw=0))
ax.add_patch(Rectangle((10, 0), 33 - 10, 1, color=ION, alpha=0.13, lw=0))

# spectrum strip
y0, h = 0.66, 0.15
bands = [("Radio", xmin, 1.24e-6), ("Microwave", 1.24e-6, 1.24e-3), ("Infrared", 1.24e-3, 1.77),
         ("", 1.77, 3.10), ("UV", 3.10, 124), ("X-ray", 124, 1.0e5), ("Gamma", 1.0e5, xmax)]
fills = ["#e3e8ee", "#eef1f5", "#e3e8ee", None, "#eef1f5", "#e3e8ee", "#eef1f5"]
for (name, a, b), fc in zip(bands, fills):
    if fc:
        ax.add_patch(Rectangle((a, y0), b - a, h, facecolor=fc, edgecolor="white", lw=1.5))
        xc = 45 if name == "UV" else np.sqrt(a * b)
        ax.text(xc, y0 + h / 2, name, ha="center", va="center", fontsize=10, color=INK)
for nm in np.linspace(400, 700, 60):
    e1, e2 = 1240 / (nm + 2.6), 1240 / nm
    ax.add_patch(Rectangle((e1, y0), e2 - e1, h, facecolor=wl_to_rgb(nm), lw=0))
ax.annotate("visible", xy=(2.35, y0 + h), xytext=(0.3, 0.905), fontsize=10, color=INK, ha="center",
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))

# threshold line
ax.plot([10, 10], [0.0, 0.84], color=INK, lw=1.6)
ax.text(13, 0.9, "ionizing threshold\n≈ 10 eV (λ ≈ 124 nm)", fontsize=10, color=INK, va="center", fontweight="bold", linespacing=1.15)
ax.text(1.0e-5, 0.905, "←  NON-IONIZING", fontsize=10, color=MUTED, ha="center", fontweight="bold")
ax.text(3.0e2, 0.575, "darker band: definitions put\nthe line anywhere from 10 to 33 eV", fontsize=10, color=ION, ha="left", va="center")
ax.text(4.0e5, 0.9, "IONIZING  →", fontsize=10, color=ION, ha="center", fontweight="bold")

# ionization energies of atoms
yb = 0.47
ax.plot([3.89, 24.59], [yb, yb], color="#8d5a97", lw=2.2, solid_capstyle="butt")
for x in (3.89, 24.59):
    ax.plot([x, x], [yb - 0.03, yb + 0.03], color="#8d5a97", lw=1.6)
ax.text(3.2, yb, "ionization energies of atoms:\n3.9 eV (cesium) to 24.6 eV (helium)", fontsize=10,
        color=INK, ha="right", va="center")

# everyday photons (lollipops): (energy, label, dot height, label side)
ex = [(4.1e-7, "FM radio\n100 MHz", 0.25, "c"), (1.0e-5, "Wi-Fi\n2.4 GHz", 0.08, "c"),
      (4.1, "UV-B (sunburn)\n4.1 eV", 0.20, "l"), (6.0e4, "medical X-ray\n~60 keV", 0.24, "l"),
      (1.25e6, "Co-60 gamma\n1.25 MeV", 0.24, "c")]
for x, lab, yl, side in ex:
    ax.plot([x, x], [0.0, yl], color=MUTED, lw=0.8)
    ax.plot(x, yl, "o", ms=6, color="#e09f1f", mec="white", mew=1.2, zorder=3)
    if side == "c":
        ax.text(x, yl + 0.04, lab, fontsize=10, color=INK, va="bottom", ha="center", linespacing=1.1)
    else:
        ax.text(x / 1.5, yl, lab, fontsize=10, color=INK, va="center", ha="right", linespacing=1.1)

# top axis: wavelength
sec = ax.secondary_xaxis("top", functions=(lambda E: 1240 / np.clip(E, 1e-30, None), lambda L: 1240 / np.clip(L, 1e-30, None)))
sec.set_xticks([1e10, 1e7, 1e4, 124, 1, 1e-3])
sec.set_xticklabels(["10 m", "1 cm", "10 µm", "124 nm", "1 nm", "1 pm"])
sec.tick_params(colors=MUTED, labelcolor=MUTED, labelsize=10)
sec.spines["top"].set_visible(False)
sec.set_xlabel("Wavelength", color=MUTED, fontsize=10)

fig.savefig(OUT, bbox_inches="tight")
print("wrote", OUT)
