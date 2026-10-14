"""Figure 11.4 - Why bone and metal cast shadows: mass attenuation coefficient vs photon energy.

Element data: Elam, Ravel & Sieber tables via the xraydb package (agree with NIST XCOM to ~1%
in this range, e.g. lead 30 keV: 30.3 cm^2/g; water 30 keV: 0.376 cm^2/g).
Mixtures use NIST ICRU-44 compositions (mass fractions):
  soft tissue: H .102 C .143 N .034 O .708 Na .002 P .003 S .003 Cl .002 K .003
  cortical bone: H .034 C .155 N .042 O .435 Na .001 Mg .002 P .103 S .003 Ca .225
Needs: pip install xraydb  (the data are cached in ch11_attenuation_z.csv so the plot can be
re-made without it).
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "ch11-attenuation-z.svg"
CSV = HERE / "ch11_attenuation_z.csv"
plt.rcParams.update({"svg.fonttype": "none", "font.family": "Inter", "font.size": 10,
                     "axes.edgecolor": "#52606d", "axes.labelcolor": "#1f2933",
                     "xtick.color": "#52606d", "ytick.color": "#52606d"})
INK, MUTED, GRID = "#1f2933", "#52606d", "#e4e7eb"

if not CSV.exists():
    import xraydb
    soft = dict(H=0.102, C=0.143, N=0.034, O=0.708, Na=0.002, P=0.003, S=0.003, Cl=0.002, K=0.003)
    bone = dict(H=0.034, C=0.155, N=0.042, O=0.435, Na=0.001, Mg=0.002, P=0.103, S=0.003, Ca=0.225)
    E = np.unique(np.concatenate([np.geomspace(10e3, 150e3, 300), [88.0e3 - 1, 88.0e3 + 1]]))
    mix = lambda c: sum(w * xraydb.mu_elam(el, E) for el, w in c.items())
    np.savetxt(CSV, np.column_stack([E / 1e3, mix(soft), mix(bone), xraydb.mu_elam("Pb", E)]),
               delimiter=",", header="E_keV,soft_tissue,cortical_bone,lead (cm^2/g)", fmt="%.6g")
d = np.loadtxt(CSV, delimiter=",")
E, soft, bone, pb = d.T

fig, ax = plt.subplots(figsize=(6.8, 3.3))
ax.set_xscale("log"); ax.set_yscale("log")
ax.axvspan(20, 120, color="#eef1f5", lw=0, zorder=0)
ax.text(49, 520, "typical medical X-ray energies", ha="center", fontsize=10, color=MUTED)
ser = [("soft tissue (Z$_{eff}$ ≈ 7)", soft, "#2a78d6"), ("cortical bone (Ca, P)", bone, "#eb6834"), ("lead (Z = 82)", pb, "#1baf7a")]
for lab, y, c in ser:
    ax.plot(E, y, color=c, lw=2, label=lab, solid_joinstyle="round")
ax.set_xlim(10, 150); ax.set_ylim(0.1, 1000)
ax.set_xticks([10, 20, 30, 50, 100, 150]); ax.set_xticklabels(["10", "20", "30", "50", "100", "150"])
ax.set_yticks([0.1, 1, 10, 100, 1000]); ax.set_yticklabels(["0.1", "1", "10", "100", "1000"])
ax.set_xlabel("Photon energy (keV)")
ax.set_ylabel("Mass attenuation\ncoefficient μ/ρ (cm²/g)")
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.grid(True, which="major", color=GRID, lw=0.6); ax.set_axisbelow(True)
# direct labels
ax.text(146, 0.215, "bone ≈ tissue at\nhigh energy", ha="right", va="bottom", fontsize=10, color=INK)
ax.annotate("lead K-edge, 88 keV:\na new absorption channel opens", xy=(88.5, 5.4), xytext=(97, 60),
            fontsize=10, color=INK, ha="center", arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
i30 = np.argmin(abs(E - 30))
ax.annotate("", xy=(30, bone[i30]), xytext=(30, soft[i30]),
            arrowprops=dict(arrowstyle="<->", color=INK, lw=1.0, shrinkA=1, shrinkB=1))
ax.text(31.5, 0.62, f"at 30 keV, bone absorbs\n{bone[i30] / soft[i30]:.1f}× more per gram", fontsize=10, color=INK, va="center")
ax.legend(frameon=False, loc="lower left", fontsize=10, handlelength=1.5)
fig.savefig(OUT, bbox_inches="tight")
print("wrote", OUT)
