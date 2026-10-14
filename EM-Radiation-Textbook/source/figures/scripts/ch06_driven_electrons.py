"""Figure 6.2 - (a) light drives electrons, which re-radiate coherently (reflection + transmission);
(b) contrast: absorption into a real excited state and delayed, random re-emission (fluorescence).
Writes figures/ch06-driven-electrons.svg."""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "ch06-driven-electrons.svg"
RED, AMBER, TEAL, PURPLE = "#d1495b", "#e09f1f", "#12a39a", "#8d5a97"
TEXT, MUTED, FILL, STROKE = "#1f2933", "#52606d", "#d9dee5", "#52606d"
VIOLET, GREEN = "#7b3fe4", "#2f9e44"
W, H = 680, 466
els = []


def text(x, y, s, size=12, color=TEXT, anchor="start", weight=400):
    els.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{color}" text-anchor="{anchor}" '
               f'font-weight="{weight}">{s}</text>')


def head(x, y, ux, uy, color, size):
    px, py = -uy, ux
    b1 = (x - size * ux + 0.55 * size * px, y - size * uy + 0.55 * size * py)
    b2 = (x - size * ux - 0.55 * size * px, y - size * uy - 0.55 * size * py)
    els.append(f'<polygon points="{x:.1f},{y:.1f} {b1[0]:.1f},{b1[1]:.1f} {b2[0]:.1f},{b2[1]:.1f}" fill="{color}"/>')


def sine(x0, x1, y0, amp, wl, phase=0.0, color=RED, w=2.4, op=1.0, dash=None, arrow=None):
    n = int(abs(x1 - x0) / 2) + 2
    pts = []
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        pts.append((x, y0 - amp * math.sin(2 * math.pi * (x - x0) / wl * (1 if x1 > x0 else -1) + phase)))
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    ds = f' stroke-dasharray="{dash}"' if dash else ""
    els.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" opacity="{op}"{ds}/>')
    if arrow:
        ux = 1 if x1 > x0 else -1
        head(x1 + ux * 10, y0, ux, 0, color, 10)
        els.append(f'<line x1="{x1:.1f}" y1="{y0}" x2="{x1 + ux * 2:.1f}" y2="{y0}" stroke="{color}" stroke-width="1.4"/>')


def wavy_arrow(x0, y0, x1, y1, color, amp=4, wl=11, w=2):
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    px, py = -uy, ux
    n = int(L / 1.5)
    pts = []
    for i in range(n + 1):
        s = (L - 10) * i / n
        o = amp * math.sin(2 * math.pi * s / wl)
        pts.append((x0 + ux * s + px * o, y0 + uy * s + py * o))
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    els.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round"/>')
    head(x1, y1, ux, uy, color, 10)


# ---------------- panel (a) ----------------
text(16, 22, "(a) Driven re-radiation: what happens in reflection and transmission", 13.5, TEXT, weight=650)
BX0, BX1 = 300, 372
els.append(f'<rect x="{BX0}" y="40" width="{BX1-BX0}" height="190" fill="{FILL}" stroke="{STROKE}" stroke-width="1"/>')
text((BX0 + BX1) / 2, 246, "thin layer of material", 11, MUTED, "middle")
ex = (BX0 + BX1) / 2
ys = [68, 108, 148, 188]
# wavelets first (behind atoms)
for y in ys:
    for r in (16, 30, 44):
        op = 0.75 - r / 90
        els.append(f'<path d="M{ex},{y - r} A{r},{r} 0 0 1 {ex},{y + r}" fill="none" stroke="{AMBER}" stroke-width="1.4" opacity="{op:.2f}"/>')
        els.append(f'<path d="M{ex},{y - r} A{r},{r} 0 0 0 {ex},{y + r}" fill="none" stroke="{AMBER}" stroke-width="1.4" opacity="{op:.2f}"/>')
for y in ys:
    els.append(f'<line x1="{ex}" y1="{y}" x2="{ex}" y2="{y + 13}" stroke="{MUTED}" stroke-width="1" />')
    els.append(f'<circle cx="{ex}" cy="{y + 14}" r="3.6" fill="{PURPLE}"/>')
    els.append(f'<circle cx="{ex}" cy="{y}" r="5.5" fill="{TEAL}"/>')
    # up-down double arrow
    ax = ex + 12
    els.append(f'<line x1="{ax}" y1="{y - 8}" x2="{ax}" y2="{y + 8}" stroke="{TEAL}" stroke-width="1.5"/>')
    head(ax, y - 11, 0, -1, TEAL, 5)
    head(ax, y + 11, 0, 1, TEAL, 5)

# incident wave
sine(20, 288, 100, 26, 64, color=RED, w=2.4, arrow=True)
text(22, 56, "incoming light wave", 12, TEXT, weight=600)
text(22, 71, "(its electric field pushes on electrons)", 12, MUTED)
# reflected wave (smaller, going left)
sine(288, 40, 196, 10, 64, color=RED, w=1.8, op=0.9, arrow=True)
text(30, 222, "reflected wave = backward re-radiation", 12, TEXT, weight=600)
text(30, 237, "from all the electrons, adding in step", 12, MUTED)
# transmitted wave + ghost of the undelayed wave
ghost_phase = 2 * math.pi * (382 - 20) / 64
sine(384, 640, 100, 26, 64, phase=ghost_phase, color="#9aa5b1", w=1.4, dash="4 4")
sine(384, 640, 100, 24, 64, phase=ghost_phase - 0.75, color=RED, w=2.4, arrow=True)
text(386, 52, "transmitted wave = incoming + forward", 12, TEXT, weight=600)
text(386, 67, "re-radiation; crests arrive a bit late", 12, MUTED)
text(640, 148, "dashed: same wave with no material", 11, MUTED, "end")
text(386, 182, "electrons are forced to oscillate at", 12, TEXT)
text(386, 197, "exactly the light's frequency, in lockstep;", 12, TEXT)
text(386, 212, "each radiates like a tiny antenna", 12, TEXT)
text(386, 227, "(no waiting, no change of color)", 12, MUTED)

# divider
els.append(f'<line x1="10" y1="262" x2="670" y2="262" stroke="#d9dee5" stroke-width="1.2"/>')

# ---------------- panel (b) ----------------
text(16, 288, "(b) Absorption, then re-emission (fluorescence): a different process", 13.5, TEXT, weight=650)
# incoming photon
wavy_arrow(24, 372, 168, 372, VIOLET, amp=4.5, wl=10, w=2.2)
text(24, 330, "a photon whose energy", 12, TEXT)
text(24, 345, "matches an energy gap", 12, TEXT)
text(24, 400, "violet / UV", 11, MUTED)
# energy levels
LX0, LX1 = 196, 276
els.append(f'<line x1="{LX0}" y1="320" x2="{LX1}" y2="320" stroke="{TEXT}" stroke-width="2"/>')
els.append(f'<line x1="{LX0}" y1="340" x2="{LX1}" y2="340" stroke="{MUTED}" stroke-width="1.2" stroke-dasharray="3 3"/>')
els.append(f'<line x1="{LX0}" y1="420" x2="{LX1}" y2="420" stroke="{TEXT}" stroke-width="2"/>')
els.append(f'<line x1="{LX0 + 24}" y1="414" x2="{LX0 + 24}" y2="330" stroke="{VIOLET}" stroke-width="1.8"/>')
head(LX0 + 24, 326, 0, -1, VIOLET, 8)
els.append(f'<circle cx="{LX0 + 24}" cy="420" r="5" fill="#ffffff" stroke="{TEAL}" stroke-width="1.6"/>')
els.append(f'<circle cx="{LX0 + 24}" cy="320" r="5" fill="{TEAL}"/>')
els.append(f'<line x1="{LX0 + 56}" y1="345" x2="{LX0 + 56}" y2="414" stroke="{GREEN}" stroke-width="1.8"/>')
head(LX0 + 56, 418, 0, 1, GREEN, 8)
text(LX1 + 10, 318, "real excited state:", 12, TEXT, weight=600)
text(LX1 + 10, 333, "electron lingers ~ns,", 12, TEXT)
text(LX1 + 10, 348, "loses a little energy", 12, TEXT)
text(LX1 + 10, 424, "ground state", 12, MUTED)
# random re-emission
atoms = [(512, 398), (596, 386), (560, 432)]
dirs = [(-0.92, 0.38), (0.93, -0.36), None]
for (ax_, ay_) in atoms:
    els.append(f'<circle cx="{ax_}" cy="{ay_}" r="5" fill="{PURPLE}"/>')
    els.append(f'<circle cx="{ax_ + 7}" cy="{ay_ - 5}" r="3.5" fill="{TEAL}"/>')
for (ax_, ay_), dd in zip(atoms, dirs):
    if dd:
        dx, dy = dd
        wavy_arrow(ax_ + dx * 10, ay_ + dy * 10, ax_ + dx * 50, ay_ + dy * 50, GREEN, amp=3.5, wl=12, w=2)
text(478, 318, "re-emitted later, in a random", 12, TEXT, weight=600)
text(478, 333, "direction, usually at a", 12, TEXT, weight=600)
text(478, 348, "longer wavelength", 12, TEXT, weight=600)
text(670, 456, "→ an incoherent glow, never an image", 12, MUTED, "end")

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
       f'font-family="Inter, sans-serif">\n<rect width="{W}" height="{H}" fill="#ffffff"/>\n'
       + "\n".join(els) + "\n</svg>\n")
OUT.write_text(svg)
print("wrote", OUT)
