"""Figure 10.6 - Exponential attenuation of 1 MeV gamma rays (narrow beam).

Mass attenuation coefficients at 1.0 MeV from the NIST X-ray Mass Attenuation
Coefficient tables (Hubbell & Seltzer): lead 0.07102, iron 0.05995, water 0.07072 cm^2/g.
Ordinary concrete ~0.0637 cm^2/g (Compton-dominated; Klein-Nishina with Z/A = 0.50).
Panel (a): versus thickness. Panel (b): versus mass per area (g/cm^2) - the curves collapse.
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parents[1] / "ch10-attenuation.svg"
plt.rcParams.update({"svg.fonttype": "none", "font.family": "Inter", "font.size": 10,
                     "axes.edgecolor": "#52606d", "axes.labelcolor": "#1f2933",
                     "xtick.color": "#52606d", "ytick.color": "#52606d"})
INK, MUTED, GRID = "#1f2933", "#52606d", "#e4e7eb"

mats = [  # name, mu/rho (cm^2/g), density (g/cm^3), color (validated categorical slots 1-4)
    ("water", 0.07072, 1.00, "#2a78d6"),
    ("concrete", 0.0637, 2.30, "#eb6834"),
    ("steel", 0.05995, 7.87, "#1baf7a"),
    ("lead", 0.07102, 11.35, "#eda100"),
]

fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.8, 3.0), sharey=True)
for ax in (a1, a2):
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True)
    ax.set_ylim(0, 1.04)
a1.set_yticks([0, 0.25, 0.5, 0.75, 1.0]); a1.set_yticklabels(["0", "25%", "50%", "75%", "100%"])
a1.set_ylabel("Fraction of photons\nthat get through")

x = np.linspace(0, 32, 600)
for name, mr, rho, c in mats[::-1]:
    mu = mr * rho
    hvl = np.log(2) / mu
    lab = f"{name}  {hvl:.2g} cm" if hvl < 1 else f"{name}  {hvl:.1f} cm"
    a1.plot(x, np.exp(-mu * x), color=c, lw=2, solid_capstyle="round", label=lab)
    a1.plot(hvl, 0.5, "o", ms=6, color=c, mec="white", mew=1.5, zorder=4)
a1.legend(frameon=False, loc="upper right", fontsize=10, handlelength=1.4, borderaxespad=0.1,
          title="half-value layers", title_fontsize=10, alignment="left")
a1.axhline(0.5, color=MUTED, lw=0.8)
a1.set_xlim(0, 32)
a1.set_xlabel("Shield thickness (cm)")
a1.set_title("(a) per centimeter: lead wins", fontsize=10, color=INK, loc="left")

m = np.linspace(0, 75, 400)
for name, mr, rho, c in mats:
    a2.plot(m, np.exp(-mr * m), color=c, lw=2, solid_capstyle="round", label=name)
a2.set_xlim(0, 75)
a2.set_xlabel("Shield mass per area (g/cm²)")
a2.set_title("(b) per gram: nearly a tie", fontsize=10, color=INK, loc="left")
a2.text(22, 0.62, "all four materials:\ncurves nearly overlap", color=INK, fontsize=10, ha="left")
a2.annotate("", xy=(14.5, np.exp(-0.068 * 14.5)), xytext=(21.5, 0.66),
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))

fig.tight_layout(w_pad=1.2)
fig.savefig(OUT, bbox_inches="tight")
print("wrote", OUT)
