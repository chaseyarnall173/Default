"""Figure 11.8 - Simulated powder X-ray diffraction patterns, Cu K-alpha (lambda = 0.15418 nm).

FCC copper (a = 0.3615 nm) and BCC iron (a = 0.2866 nm). Peak positions from Bragg's law with
d = a / sqrt(h^2 + k^2 + l^2) and the cubic selection rules (FCC: h,k,l all odd or all even;
BCC: h+k+l even). Relative heights are APPROXIMATE: multiplicity x Lorentz-polarization factor
x (structure factor x atomic scattering factor f0)^2 x exp(-2B s^2), B = 0.5 A^2,
f0 from Waasmaier & Kirfel (via xraydb). No absorption, instrument, or K-alpha2 effects.
Absent (forbidden) reflections are marked with open triangles.
Needs: pip install xraydb (falls back to cached values in ch11_xrd_patterns.csv).
"""
from pathlib import Path
import itertools, csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "ch11-xrd-patterns.svg"
CSV = HERE / "ch11_xrd_patterns.csv"
LAM = 0.15418
plt.rcParams.update({"svg.fonttype": "none", "font.family": "Inter", "font.size": 10,
                     "axes.edgecolor": "#52606d", "axes.labelcolor": "#1f2933",
                     "xtick.color": "#52606d", "ytick.color": "#52606d"})
INK, MUTED, GRID, COL = "#1f2933", "#52606d", "#e4e7eb", "#2a78d6"


def reflections(a, lat, maxh=5, lo=20, hi=122):
    out = {}
    for h, k, l in itertools.product(range(maxh), repeat=3):
        if (h, k, l) == (0, 0, 0) or not (h >= k >= l):
            continue
        N = h * h + k * k + l * l
        s = LAM * np.sqrt(N) / (2 * a)
        if s >= 1:
            continue
        tt = 2 * np.degrees(np.arcsin(s))
        if not lo <= tt <= hi:
            continue
        allowed = {"fcc": h % 2 == k % 2 == l % 2, "bcc": (h + k + l) % 2 == 0}[lat]
        out.setdefault(N, []).append(((h, k, l), tt, allowed))
    return out


def intensity(el, a, lat, hkl_list, tt):
    import xraydb
    th = np.radians(tt / 2)
    mult = 0
    fams = {tuple(sorted(x, reverse=True)) for x in hkl_list}
    for p in itertools.product(range(-6, 7), repeat=3):
        if tuple(sorted(map(abs, p), reverse=True)) in fams:
            mult += 1
    q = np.sin(th) / (LAM * 10)
    f = xraydb.f0(el, q)[0]
    S = 4 if lat == "fcc" else 2
    LP = (1 + np.cos(2 * th) ** 2) / (np.sin(th) ** 2 * np.cos(th))
    return mult * LP * (S * f) ** 2 * np.exp(-2 * 0.5 * q * q)


samples = [("Cu", 0.3615, "fcc", "(a) Copper: FCC, a = 0.3615 nm"), ("Fe", 0.2866, "bcc", "(b) α-iron: BCC, a = 0.2866 nm")]
rows = []
if CSV.exists():
    with open(CSV) as fh:
        rows = [r for r in csv.DictReader(fh)]
else:
    for el, a, lat, _ in samples:
        R = reflections(a, lat)
        for N, lst in sorted(R.items()):
            hkls = [x[0] for x in lst]; tt = lst[0][1]; ok = lst[0][2]
            I = intensity(el, a, lat, hkls, tt) if ok else 0.0
            rows.append(dict(el=el, N=N, hkl=" ".join("".join(map(str, x)) for x in hkls), tt=f"{tt:.3f}", allowed=int(ok), I=f"{I:.6g}"))
    with open(CSV, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

fig, axes = plt.subplots(2, 1, figsize=(6.8, 4.4), sharex=True)
x = np.linspace(20, 122, 4000)
for ax, (el, a, lat, title) in zip(axes, samples):
    rr = [r for r in rows if r["el"] == el]
    Imax = max(float(r["I"]) for r in rr)
    y = np.full_like(x, 0.012)
    for r in rr:
        if int(r["allowed"]):
            h = float(r["I"]) / Imax
            y += h * np.exp(-0.5 * ((x - float(r["tt"])) / 0.18) ** 2)
    ax.plot(x, y, color=COL, lw=1.6, solid_joinstyle="round")
    for r in rr:
        tt = float(r["tt"]); lab = "(" + r["hkl"].split()[0] + ")"
        if int(r["allowed"]):
            h = float(r["I"]) / Imax
            ax.text(tt, h + 0.05, lab, ha="center", va="bottom", fontsize=10, color=INK)
        elif int(r["N"]) <= 6:
            ax.plot(tt, 0.0, marker="^", ms=7, mfc="white", mec=MUTED, mew=1.2, clip_on=False, zorder=4)
            ax.text(tt, 0.10, lab, ha="center", va="bottom", fontsize=9.5 if False else 10, color=MUTED, style="italic")
    ax.set_ylim(0, 1.32); ax.set_yticks([])
    ax.set_title(title, loc="left", fontsize=10, color=INK, fontweight="bold")
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.grid(True, axis="x", color=GRID, lw=0.6); ax.set_axisbelow(True)
axes[1].set_xlim(20, 122)
axes[1].set_xlabel("Diffraction angle 2θ (degrees), Cu Kα, λ = 0.1542 nm")
axes[0].text(121, 1.2, "open triangles: first few positions where\nthe selection rule forces zero intensity",
             ha="right", va="top", fontsize=10, color=MUTED)
fig.tight_layout(h_pad=0.6)
fig.savefig(OUT, bbox_inches="tight")
print("wrote", OUT)
