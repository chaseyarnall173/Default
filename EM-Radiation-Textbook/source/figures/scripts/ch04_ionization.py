"""Figure 4.6: first ionization energy vs. atomic number, Z = 1-36.

Values: NIST Atomic Spectra Database ground levels and ionization energies (rounded to 0.001 eV).
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parents[1] / "ch04-ionization.svg"
plt.rcParams.update({"svg.fonttype": "none", "font.family": "Inter", "font.size": 10,
                     "axes.edgecolor": "#52606d", "axes.labelcolor": "#1f2933",
                     "xtick.color": "#52606d", "ytick.color": "#52606d"})
TEXT, MUTED, ELEC, NUC, ACC = "#1f2933", "#52606d", "#12a39a", "#8d5a97", "#0b6e4f"

sym = ("H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn "
       "Ga Ge As Se Br Kr").split()
ie = [13.598, 24.587, 5.392, 9.323, 8.298, 11.260, 14.534, 13.618, 17.423, 21.565,
      5.139, 7.646, 5.986, 8.152, 10.487, 10.360, 12.968, 15.760, 4.341, 6.113,
      6.561, 6.828, 6.746, 6.767, 7.434, 7.902, 7.881, 7.640, 7.726, 9.394,
      5.999, 7.899, 9.789, 9.752, 11.814, 14.000]
Z = list(range(1, 37))

fig, ax = plt.subplots(figsize=(6.8, 2.9))
ax.axhspan(1.8, 3.1, color="#e09f1f", alpha=0.16, lw=0)
ax.text(36.6, 2.45, "visible-light photons (1.8–3.1 eV): too weak to ionize any atom",
        fontsize=8.8, color="#8a5a00", ha="right", va="center")
ax.plot(Z, ie, color=ELEC, lw=1.6, zorder=2)
ax.plot(Z, ie, "o", ms=4, color=ELEC, mec="white", mew=1.0, zorder=3)
noble = {2: "He", 10: "Ne", 18: "Ar", 36: "Kr"}
alkali = {3: "Li", 11: "Na", 19: "K"}
for z, s in noble.items():
    ax.plot(z, ie[z - 1], "o", ms=7, color=NUC, mec="white", mew=1.2, zorder=4)
    ax.text(z + 0.6, ie[z - 1] + 0.3, f"{s} {ie[z-1]:.1f}", fontsize=9.5, color=TEXT, fontweight="bold", va="bottom")
for z, s in alkali.items():
    ax.plot(z, ie[z - 1], "o", ms=7, color=ACC, mec="white", mew=1.2, zorder=4)
    ax.text(z + 0.7, ie[z - 1] - 0.1, f"{s} {ie[z-1]:.1f}", fontsize=9.5, color=TEXT, fontweight="bold", va="center")
ax.text(1.6, 13.6, "H 13.6", fontsize=9.5, color=TEXT, fontweight="bold", va="center")
ax.text(36.8, 25.0, "Peaks (purple): noble gases; full shells hold on tightly.", fontsize=9, color=MUTED, ha="right")
ax.text(36.8, 23.0, "Dips (green): alkali metals; one lone outer electron.", fontsize=9, color=MUTED, ha="right")
ax.set_xlim(0, 37.2); ax.set_ylim(0, 27)
ax.set_xticks([1, 5, 10, 15, 20, 25, 30, 35])
ax.set_xlabel("atomic number Z")
ax.set_ylabel("first ionization energy (eV)")
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
ax.grid(True, axis="y", color="#e4e7eb", lw=0.6); ax.set_axisbelow(True)
fig.savefig(OUT, bbox_inches="tight", facecolor="white")
print("wrote", OUT)
