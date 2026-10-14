"""Figure 4.5: hydrogen energy-level ladder, E_n = -13.6 eV / n^2 (axis broken between n=1 and n=2)."""
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "ch04-hydrogen-ladder.svg"
W, H = 680, 390
TEXT, MUTED, GRID = "#1f2933", "#52606d", "#d9dee5"
ELEC, ACC, LIGHT = "#12a39a", "#0b6e4f", "#e09f1f"
E = lambda n: -13.6 / n ** 2
Y0, K = 66, 60.0          # y of 0 eV and px per eV for the upper (n >= 2) region
Y1 = 352                  # y of the n = 1 level (below the axis break)
def Y(e):
    return Y1 if e < -5 else Y0 - e * K

XL, XR = 92, 326
p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Inter, sans-serif">',
     f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
     '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
     f'<path d="M0 0 L10 5 L0 10 z" fill="{TEXT}"/></marker></defs>']

# continuum above zero
p.append(f'<rect x="{XL}" y="14" width="{XR-XL}" height="{Y0-14}" fill="#eef1f5"/>')
for i in range(12):
    yy = 18 + i * 4
    p.append(f'<line x1="{XL}" y1="{yy}" x2="{XR}" y2="{yy}" stroke="#c4ccd5" stroke-width="0.6"/>')
p.append(f'<text x="{(XL+XR)/2}" y="38" font-size="10.5" font-weight="600" fill="{TEXT}" text-anchor="middle">free electron (ionized): any energy</text>')

# energy axis with a break
p.append(f'<line x1="62" y1="14" x2="62" y2="300" stroke="{MUTED}" stroke-width="1.2"/>')
p.append(f'<path d="M56 300 L68 306 M56 308 L68 314" stroke="{MUTED}" stroke-width="1.2"/>')
p.append(f'<line x1="62" y1="314" x2="62" y2="372" stroke="{MUTED}" stroke-width="1.2"/>')
for e in (0, -1, -2, -3):
    p.append(f'<line x1="58" y1="{Y(e)}" x2="62" y2="{Y(e)}" stroke="{MUTED}"/>')
    p.append(f'<text x="54" y="{Y(e)+4}" font-size="10" fill="{MUTED}" text-anchor="end">{e}</text>')
p.append(f'<line x1="58" y1="{Y1}" x2="62" y2="{Y1}" stroke="{MUTED}"/>')
p.append(f'<text x="54" y="{Y1+4}" font-size="10" fill="{MUTED}" text-anchor="end">−13.6</text>')
p.append(f'<text x="20" y="200" font-size="10.5" fill="{MUTED}" text-anchor="middle" transform="rotate(-90 20 200)">energy (eV)</text>')

# levels and labels (label y positions nudged apart where levels crowd)
labels = {0: (Y0 - 2, "0", "n = ∞"), 6: (84, "−0.38", "n = 6"), 5: (99, "−0.54", "n = 5"),
          4: (Y(E(4)) + 4, "−0.85", "n = 4"), 3: (Y(E(3)) + 4, "−1.51", "n = 3"),
          2: (Y(E(2)) + 4, "−3.40", "n = 2"), 1: (Y1 + 4, "−13.6", "n = 1")}
for n in (1, 2, 3, 4, 5, 6):
    y = Y(E(n))
    p.append(f'<line x1="{XL}" y1="{y:.1f}" x2="{XR}" y2="{y:.1f}" stroke="{TEXT}" stroke-width="{2.4 if n == 1 else 1.8}"/>')
p.append(f'<line x1="{XL}" y1="{Y0}" x2="{XR}" y2="{Y0}" stroke="{TEXT}" stroke-width="1.2" stroke-dasharray="5 3"/>')
for n, (ly, ev, name) in labels.items():
    y = Y0 if n == 0 else Y(E(n))
    p.append(f'<path d="M{XR+2} {y:.1f} L{XR+12} {ly-4:.1f}" stroke="{MUTED}" stroke-width="0.8" fill="none"/>')
    p.append(f'<text x="{XR+15}" y="{ly:.1f}" font-size="11" font-weight="700" fill="{TEXT}">{name}</text>')
    p.append(f'<text x="{XR+60}" y="{ly:.1f}" font-size="11" fill="{TEXT}">{ev} eV</text>')
p.append(f'<text x="{XR+15}" y="{Y1+19}" font-size="10.5" fill="{ACC}" font-weight="600">ground state</text>')
p.append(f'<text x="{XR+15}" y="{Y(E(2))+19:.1f}" font-size="10.5" fill="{MUTED}">first excited state</text>')

# arrows
def arrow(x, e_from, e_to, label, sub, col=TEXT, side="right"):
    y0, y1 = Y(e_from), Y(e_to)
    p.append(f'<line x1="{x}" y1="{y0-2:.1f}" x2="{x}" y2="{y1+2:.1f}" stroke="{col}" stroke-width="1.6" marker-end="url(#ah)"/>')
    ym = (y0 + y1) / 2 if e_from > -5 else 333
    anchor = "start" if side == "right" else "end"
    dx = 6 if side == "right" else -6
    p.append(f'<text x="{x+dx}" y="{ym:.1f}" font-size="11" font-weight="700" fill="{TEXT}" text-anchor="{anchor}">{label}</text>')
    p.append(f'<text x="{x+dx}" y="{ym+13:.1f}" font-size="10" fill="{MUTED}" text-anchor="{anchor}">{sub}</text>')

arrow(108, E(1), E(2), "10.2 eV", "1 → 2")
arrow(146, E(2), E(3), "1.89 eV", "2 → 3")
arrow(196, E(2), 0, "3.40 eV", "ionize from n = 2")
arrow(306, E(1), 0, "13.6 eV", "ionize from n = 1", side="left")
# the break across the levels region
p.append(f'<rect x="{XL-30}" y="302" width="{XR-XL+30}" height="10" fill="#ffffff"/>')
p.append(f'<path d="M56 300 L68 306 M56 308 L68 314" stroke="{MUTED}" stroke-width="1.2"/>')

# right-hand notes
xn = 478
p.append(f'<rect x="{xn-12}" y="40" width="{W-xn+4}" height="300" rx="8" fill="#f5f7fa"/>')
p.append(f'<text x="{xn}" y="68" font-size="15" font-weight="700" fill="{TEXT}">Eₙ = −13.6 eV / n²</text>')
notes = [("Negative means bound:", "you must add energy to free", "the electron (0 eV = free, at rest)."),
         ("Gaps shrink as n grows:", "levels crowd together just", "below 0 eV."),
         ("Higher n = bigger cloud:", "in the Bohr model the radius", "grows as n² (n = 2 is 4× wider)."),
         ("Every jump has an exact size:", "only photons carrying exactly", "that energy can cause it (Ch. 5).")]
y = 96
for head, l1, l2 in notes:
    p.append(f'<text x="{xn}" y="{y}" font-size="11" font-weight="700" fill="{TEXT}">{head}</text>')
    p.append(f'<text x="{xn}" y="{y+14}" font-size="10.5" fill="{MUTED}">{l1}</text>')
    p.append(f'<text x="{xn}" y="{y+28}" font-size="10.5" fill="{MUTED}">{l2}</text>')
    y += 60
p.append("</svg>")
OUT.write_text("\n".join(p))
print("wrote", OUT)
