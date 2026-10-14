"""Figure 9.2 - the color of a glowing blackbody vs. temperature (top) and how much visible light it
emits (bottom). Color: Planck spectrum integrated against a CIE 1931 color-matching-function fit and
converted to sRGB, each swatch scaled to full display brightness. Bottom: visible (400-700 nm) power per
square meter emitted (pi * integral of Planck radiance), log scale.
Output: figures/ch09-glow-colors.svg"""
from pathlib import Path
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch08_colorutil import spectrum_to_xyz, M

plt.rcParams.update({"svg.fonttype": "none", "font.family": "Inter", "font.size": 10,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#9aa5b1", "axes.linewidth": 0.6, "axes.labelcolor": "#52606d",
                     "xtick.color": "#52606d", "ytick.color": "#52606d", "text.color": "#1f2933"})
OUT = Path(__file__).resolve().parents[1] / "ch09-glow-colors.svg"
INK, MUTED = "#1f2933", "#52606d"
h, c, k = 6.626e-34, 3.00e8, 1.381e-23
lam = np.linspace(380, 780, 401)
def planck(lam_nm, T):
    l = lam_nm * 1e-9
    with np.errstate(over="ignore"):
        return 2 * h * c ** 2 / l ** 5 / np.expm1(h * c / (l * k * T))
Ts = np.linspace(700, 7000, 316)
cols = []
for T in Ts:
    XYZ = spectrum_to_xyz(lam, planck(lam, T))
    rgb = M @ XYZ
    rgb = rgb - min(rgb.min(), 0)                 # pull out-of-gamut reds back in
    rgb = rgb / rgb.max()                         # brightest displayable version of this color
    rgb = np.where(rgb <= 0.0031308, 12.92 * rgb, 1.055 * rgb ** (1 / 2.4) - 0.055)
    cols.append(np.clip(rgb, 0, 1))
lv = np.linspace(400, 700, 301)
vis = np.array([np.pi * np.trapezoid(planck(lv, T), lv * 1e-9) for T in Ts])   # W/m^2 in 400-700 nm

fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.8, 3.6), sharex=True,
                             gridspec_kw=dict(height_ratios=[0.55, 1.0], hspace=0.12))
for T, col in zip(Ts, cols):
    a1.axvspan(T - 10.1, T + 10.1, color=col, lw=0)
a1.set_ylim(0, 1); a1.set_yticks([])
from matplotlib.patches import Rectangle
a1.add_patch(Rectangle((700, 0), 6300, 1, fill=False, ec="#9aa5b1", lw=0.6, zorder=3))
for x, t in [(760, "red"), (1450, "orange"), (2900, "yellowish white"), (5300, "white")]:
    a1.text(x, 0.5, t, fontsize=10, color=INK, va="center", ha="left")
for sp in ("left", "bottom"):
    a1.spines[sp].set_visible(False)
a1.tick_params(bottom=False)
a1.set_title("Color of the glow (each swatch shown as bright as possible)", fontsize=10, loc="left", color=INK, pad=5)
marks = [(798, "Draper point (\u2248800 K):\nglow just visible in the dark", 950, 2e-5, "left"),
         (1000, "red-hot stove (\u22481000 K)", 1150, 0.25, "left"),
         (2700, "incandescent bulb (2700 K)", 2850, 1.5e3, "left"),
         (5800, "Sun\u2019s surface (5800 K)", 5650, 2e5, "right")]
a2.semilogy(Ts, vis, color=INK, lw=1.8)
a2.set_ylim(1e-6, 1e9)
a2.set_yticks([1e-5, 1e-2, 1e1, 1e4, 1e7])
a2.set_ylabel("visible light emitted\n(W per m²)")
a2.set_xlabel("temperature (K)")
a2.set_xlim(700, 7000)
a2.grid(True, which="major", color="#e4e7eb", lw=0.5); a2.set_axisbelow(True)
for T, lab, tx, ty, ha in marks:
    v = np.interp(T, Ts, vis)
    a2.plot(T, v, "o", ms=5.5, mfc="#e09f1f", mec="white", mew=1, zorder=5)
    a2.annotate(lab, xy=(T, v), xytext=(tx, ty), fontsize=10, color=INK, ha=ha, va="center",
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.7, shrinkA=2, shrinkB=3))
fig.savefig(OUT, bbox_inches="tight")
print("wrote", OUT)
for T in (798, 1000, 2700, 5800):
    print(T, "visible W/m2 = %.3g" % np.interp(T, Ts, vis), " fraction of sigma T^4 = %.3g" % (np.interp(T, Ts, vis) / (5.67e-8 * T ** 4)))
