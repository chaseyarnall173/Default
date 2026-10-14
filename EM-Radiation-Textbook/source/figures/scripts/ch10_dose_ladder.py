"""Figure 10.4 - The dose ladder (effective dose, mSv, log scale).

Values (see sources/ch10.md): NRC / NCRP Report 160 (US average 6.2 mSv/yr, natural 3.1),
RadiologyInfo/ACR (dental 0.005, chest 0.1, CT abdomen-pelvis 7.7), EPA (NY-LA flight
0.02-0.05), NASA (ISS ~80-160 mSv per 6 months at solar max/min; other NASA estimates
~0.2-0.5 mSv/day), JPL/RAD (Mars cruise 0.66 Sv round trip; full mission ~1 Sv),
NASA-STD-3001 (600 mSv career), NRC (1 mSv/yr public, 50 mSv/yr occupational;
LD50/30 4-5 Sv), CDC (acute radiation syndrome above ~0.7 Gy).
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

OUT = Path(__file__).resolve().parents[1] / "ch10-dose-ladder.svg"
plt.rcParams.update({"svg.fonttype": "none", "font.family": "Inter", "font.size": 10,
                     "axes.edgecolor": "#52606d", "axes.labelcolor": "#1f2933",
                     "xtick.color": "#52606d", "ytick.color": "#1f2933"})
INK, MUTED, GRID = "#1f2933", "#52606d", "#e4e7eb"
C = {"life": "#2a78d6", "space": "#eb6834", "limit": "#52606d"}

rows = [  # label, low, high, category
    ("Dental X-ray", 0.005, None, "life"),
    ("Cross-country flight (one way)", 0.02, 0.05, "life"),
    ("Chest X-ray", 0.1, None, "life"),
    ("One day on the ISS", 0.2, 0.9, "space"),
    ("NRC public limit (per year, man-made)", 1.0, None, "limit"),
    ("US natural background (per year)", 3.1, None, "life"),
    ("US average, all sources (per year)", 6.2, None, "life"),
    ("CT scan, abdomen & pelvis", 7.7, None, "life"),
    ("NRC radiation-worker limit (per year)", 50, None, "limit"),
    ("Six months on the ISS", 40, 160, "space"),
    ("NASA career limit", 600, None, "limit"),
    ("Mars round trip, cruise only", 660, None, "space"),
    ("Acute radiation sickness possible", 700, None, "limit"),
    ("Full Mars mission (~1000 days)", 1000, None, "space"),
    ("Lethal to half (LD50, all at once)", 4000, 5000, "limit"),
]

fig, ax = plt.subplots(figsize=(6.8, 4.5))
ax.set_xscale("log")
ax.set_xlim(0.002, 2e4)
n = len(rows)
for i, (lab, lo, hi, cat) in enumerate(rows):
    y = n - 1 - i
    mk = "D" if cat == "limit" else "o"
    if hi:
        ax.plot([lo, hi], [y, y], color=C[cat], lw=5, solid_capstyle="round", alpha=0.9)
    else:
        ax.plot(lo, y, mk, ms=7 if mk == "o" else 6, color=C[cat], mec="white", mew=1.5, zorder=3)
ax.set_yticks(range(n))
ax.set_yticklabels([r[0] for r in rows][::-1])
ax.tick_params(axis="y", length=0)
ax.set_xticks([0.01, 0.1, 1, 10, 100, 1000, 1e4])
ax.set_xticklabels(["0.01", "0.1", "1", "10", "100", "1,000", "10,000"])
ax.set_xlabel("Effective dose (mSv), log scale: each gridline is 10×")
for s in ["top", "right", "left"]:
    ax.spines[s].set_visible(False)
ax.grid(True, axis="x", color=GRID, lw=0.6); ax.set_axisbelow(True)
ax.set_ylim(-0.7, n - 0.3)
handles = [Line2D([], [], marker="o", ls="", color=C["life"], ms=7, label="everyday & medical"),
           Line2D([], [], marker="o", ls="", color=C["space"], ms=7, label="spaceflight"),
           Line2D([], [], marker="D", ls="", color=C["limit"], ms=6, label="limits & thresholds")]
ax.legend(handles=handles, frameon=False, loc="upper right", fontsize=10, handletextpad=0.3)
fig.tight_layout()
fig.savefig(OUT, bbox_inches="tight")
print("wrote", OUT)
