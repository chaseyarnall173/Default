"""Generate figures/ch03-energy-ladder.svg: photon energy decides what light does to matter.
Rows: typical energy ranges of processes in matter (order-of-magnitude, schematic), against the
photon energies of each band. Run from source/:  python3 figures/scripts/ch03_energy_ladder.py
"""
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch03_spectral_color import wavelength_rgb

OUT = Path(__file__).resolve().parents[1] / "ch03-energy-ladder.svg"
INK, MUTED, GRID = "#1f2933", "#52606d", "#e4e7eb"
HEAT, ELEC, ION = "#9aa5b1", "#0b8a5f", "#c2410c"
plt.rcParams.update({"svg.fonttype": "none", "font.family": "Inter", "font.size": 10.5,
                     "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.spines.left": False})

rows = [  # label, lo (eV), hi (eV), color
    ("Drive free electrons in metals\n(antennas, reflection)", 1e-7, 8, HEAT),
    ("Rotate polar molecules (e.g. water)", 1e-5, 5e-3, HEAT),
    ("Vibrate chemical bonds", 0.05, 0.5, HEAT),
    ("Lift outer electrons, cross band gaps\n(color, vision, solar cells)", 1.0, 10, ELEC),
    ("Break chemical bonds\n(photochemistry, sunburn)", 1.5, 10, ELEC),
    ("Ionize atoms and molecules", 10, 1e7, ION),
    ("Knock out inner-shell electrons", 100, 1e5, ION),
    ("Excite atomic nuclei", 1e5, 1e7, ION),
]
fig, ax = plt.subplots(figsize=(6.8, 3.9))
n = len(rows)
for i, (lab, lo, hi, col) in enumerate(rows):
    y = n - 1 - i
    ax.add_patch(Rectangle((lo, y - 0.2), hi - lo, 0.4, color=col, lw=0, zorder=3))
ax.set_yticks(range(n))
ax.set_yticklabels([r[0] for r in rows][::-1], fontsize=10, linespacing=1.05)
ax.tick_params(axis="y", length=0, pad=6)
ax.set_xscale("log")
ax.set_xlim(1e-7, 1e7)
ax.set_ylim(-0.7, n + 0.75)
ax.set_xticks([1e-6, 1e-3, 1, 1e3, 1e6])
ax.set_xticklabels(["1 µeV", "1 meV", "1 eV", "1 keV", "1 MeV"])
ax.xaxis.set_minor_locator(matplotlib.ticker.LogLocator(base=10, subs=(1.0,), numticks=30))
ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
ax.set_xlabel("photon energy (log scale)")
ax.grid(axis="x", which="major", color=GRID, lw=0.7, zorder=0)

# band strip along the top
top = n - 0.05
bands = [("radio", 1e-7, 4.1e-6, "#dbe4ee"), ("microwave", 4.1e-6, 1.24e-3, "#e3dcef"), ("infrared", 1.24e-3, 1.77, "#f3dcd8"),
         ("vis", 1.77, 3.1, None), ("UV", 3.1, 124, "#e6dcf5"), ("X-ray", 124, 1.24e5, "#d6ebe7"), ("gamma", 1.24e5, 1e7, "#ece6d4")]
for name, lo, hi, col in bands:
    if col:
        ax.add_patch(Rectangle((lo, top), hi - lo, 0.62, color=col, lw=0, zorder=2))
        ax.text(np.sqrt(lo * hi), top + 0.31, name, ha="center", va="center", fontsize=10, color=INK, zorder=4)
    else:
        es = np.geomspace(lo, hi, 30)
        for a, b in zip(es[:-1], es[1:]):
            ax.add_patch(Rectangle((a, top), b - a, 0.62, color=wavelength_rgb(1240 / np.sqrt(a * b)), lw=0, zorder=2))

# reference lines
for xval, txt, col in ((0.0259, "room-temperature\nthermal energy kT", MUTED), (10, "ionizing\n(~10 eV)", ION)):
    ax.axvline(xval, ymin=0.0, ymax=(top + 0.7) / (n + 1.45), color=col, lw=1, ls=(0, (3, 2)), zorder=1)
ax.text(0.0259 * 0.8, 0.95, "kT at room\ntemperature\n(0.026 eV)", fontsize=10, color=MUTED, ha="right", va="center")
ax.text(14, 3.0, "ionization threshold (~10 eV)", fontsize=10, color=ION, ha="left", va="center")
fig.tight_layout()
fig.savefig(OUT, bbox_inches="tight", facecolor="white")
print("wrote", OUT)
