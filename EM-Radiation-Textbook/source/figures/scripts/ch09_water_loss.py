"""Figure 9.6 - why microwave ovens heat water: water's dielectric loss vs. frequency in the
single-relaxation (Debye) model at about 25 C: eps'' = (eps_s - eps_inf) w tau / (1 + w^2 tau^2),
with eps_s = 78.4, eps_inf = 5.2, tau = 8.3 ps (relaxation peak near 19 GHz). This is a model, not
measured data; real water has extra weaker features at higher frequency.
Output: figures/ch09-water-loss.svg"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"svg.fonttype": "none", "font.family": "Inter", "font.size": 10,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#9aa5b1", "axes.linewidth": 0.6, "axes.labelcolor": "#52606d",
                     "xtick.color": "#52606d", "ytick.color": "#52606d", "text.color": "#1f2933"})
OUT = Path(__file__).resolve().parents[1] / "ch09-water-loss.svg"
INK, MUTED, AMBER, BLUE = "#1f2933", "#52606d", "#e09f1f", "#2e6fdb"
es, einf, tau = 78.4, 5.2, 8.3e-12
f = np.logspace(8, 12, 800)
w = 2 * np.pi * f
epp = (es - einf) * w * tau / (1 + (w * tau) ** 2)
f245 = 2.45e9
e245 = np.interp(f245, f, epp)
fpk = 1 / (2 * np.pi * tau)

fig, ax = plt.subplots(figsize=(6.8, 2.9))
ax.plot(f / 1e9, epp, color=INK, lw=2)
ax.plot(f245 / 1e9, e245, "o", ms=7, mfc=AMBER, mec="white", mew=1.2, zorder=5)
ax.annotate(f"microwave oven, 2.45 GHz\n(ε″ ≈ {e245:.0f}: absorbed over ~cm)", xy=(2.45, e245), xytext=(0.13, 22),
            fontsize=10, color=INK, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.7))
ax.annotate("broad peak near 20 GHz:\nwater molecules can’t keep up\nwith the field (relaxation)",
            xy=(fpk / 1e9, epp.max()), xytext=(80, 30), fontsize=10, color=INK,
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.7))
ax.set_xscale("log"); ax.set_xlim(0.1, 1000); ax.set_ylim(0, 42)
ax.set_xticks([0.1, 1, 10, 100, 1000]); ax.set_xticklabels(["0.1", "1", "10", "100", "1000"])
ax.set_xlabel("frequency (GHz)")
ax.set_ylabel("how strongly water\nabsorbs (loss factor ε″)")
ax.grid(True, which="major", color="#e4e7eb", lw=0.5); ax.set_axisbelow(True)
fig.savefig(OUT, bbox_inches="tight")
print("wrote", OUT, "eps''(2.45 GHz) = %.2f, peak at %.1f GHz" % (e245, fpk / 1e9))
