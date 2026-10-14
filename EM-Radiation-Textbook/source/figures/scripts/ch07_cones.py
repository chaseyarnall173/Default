"""Figure 7.1 - approximate relative sensitivity of the three cone pigments (S, M, L).
Curves use the Govardovskii et al. (2000) visual-pigment template with peaks at 420, 534 and
564 nm (HyperPhysics values). They are APPROXIMATE and normalized to 1 at the peak; real cones
at the cornea are also filtered by the lens and macular pigment.
Writes figures/ch07-cones.svg."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

OUT = Path(__file__).resolve().parents[1] / "ch07-cones.svg"
plt.rcParams.update({"svg.fonttype": "none", "font.family": "Inter", "font.size": 10,
                     "axes.edgecolor": "#9aa5b1", "axes.labelcolor": "#1f2933",
                     "xtick.color": "#52606d", "ytick.color": "#52606d"})
TEXT, MUTED = "#1f2933", "#52606d"


def template(lam, lmax):
    x = lmax / lam
    a = 0.8795 + 0.0459 * np.exp(-((lmax - 300) ** 2) / 11940)
    alpha = 1 / (np.exp(69.7 * (a - x)) + np.exp(28 * (0.922 - x)) + np.exp(-14.9 * (1.104 - x)) + 0.674)
    lmb = 189 + 0.315 * lmax
    bb = -40.5 + 0.195 * lmax
    # beta-band omitted: in the living eye the lens absorbs most light below ~420 nm, so M and L
    # cones respond only weakly there (keeps the sketch closer to real cone responses).
    s = alpha
    return s / s.max()


def spectral(lam):
    if lam < 440: r, g, b = -(lam - 440) / 60, 0, 1
    elif lam < 490: r, g, b = 0, (lam - 440) / 50, 1
    elif lam < 510: r, g, b = 0, 1, -(lam - 510) / 20
    elif lam < 580: r, g, b = (lam - 510) / 70, 1, 0
    elif lam < 645: r, g, b = 1, -(lam - 645) / 65, 0
    else: r, g, b = 1, 0, 0
    f = 0.3 + 0.7 * (lam - 380) / 40 if lam < 420 else (0.3 + 0.7 * (780 - lam) / 80 if lam > 700 else 1)
    return tuple((max(0, v) * f) ** 0.8 for v in (r, g, b))


lam = np.linspace(380, 720, 681)
cones = [("S", 420, "#4c5fd5", "S cones\npeak ≈ 420 nm", (424, 1.03), "center"),
         ("M", 534, "#1f9e6e", "M cones\npeak ≈ 534 nm", (500, 1.03), "center"),
         ("L", 564, "#d9480f", "L cones\npeak ≈ 564 nm", (612, 1.03), "center")]

fig, ax = plt.subplots(figsize=(6.8, 3.25))
for name, lmax, col, label, (lx, ly), ha in cones:
    ax.plot(lam, template(lam, lmax), color=col, lw=2, solid_capstyle="round")
    ax.text(lx, ly, label, color=TEXT, ha=ha, va="bottom", fontsize=10, linespacing=1.15)
# key showing which curve is which (small colored dashes beside labels)
for name, lmax, col, label, (lx, ly), ha in cones:
    ax.plot([lx - 30, lx - 22], [ly + 0.13, ly + 0.13], color=col, lw=3, solid_capstyle="round", clip_on=False)

# yellow-light example at 580 nm
l0 = 580
vals = {n: float(np.interp(l0, lam, template(lam, lm))) for n, lm, *_ in cones}
ax.plot([l0, l0], [0, 1.0], color="#9aa5b1", lw=1, zorder=0)
for n, lm, col, *_ in cones:
    v = vals[n]
    ax.plot([l0], [v], "o", ms=7, mfc=col, mec="white", mew=1.5, zorder=5)
ax.text(l0 - 4, 0.05, "580 nm\n(yellow)", fontsize=9.5, color=TEXT, ha="right", va="bottom", linespacing=1.1)

# spectrum strip
for l in np.arange(380, 720, 1.0):
    ax.add_patch(Rectangle((l, -0.15), 1.05, 0.08, color=spectral(l + 0.5), lw=0))
ax.set_xlim(380, 720)
ax.set_ylim(-0.16, 1.32)
ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
ax.set_xlabel("Wavelength (nm)")
ax.set_ylabel("Relative sensitivity\n(approximate)")
ax.spines[["top", "right"]].set_visible(False)
ax.spines["left"].set_bounds(0, 1)
ax.grid(axis="y", color="#e4e7eb", lw=0.6)
ax.set_axisbelow(True)
ax.tick_params(length=3)
fig.savefig(OUT, bbox_inches="tight", transparent=False, facecolor="white")
print("wrote", OUT, {k: round(v, 2) for k, v in vals.items()})
