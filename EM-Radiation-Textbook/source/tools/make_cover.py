#!/usr/bin/env python3
"""Generate front/cover.html (full-bleed cover with a chirped EM wave from radio to gamma)."""
import math
from pathlib import Path
W, H = 816, 1056
x0, x1 = 40, 776
lam0, lam1 = 230.0, 7.0
k = math.log(lam0 / lam1) / (x1 - x0)
pts = []
x = x0
while x <= x1:
    u = x - x0
    phase = 2 * math.pi / lam0 * (math.exp(k * u) - 1) / k
    env = 1.0 if u > 25 else u / 25
    pts.append(f"{x:.1f},{(70 - 52 * env * math.sin(phase)):.2f}")
    x += 0.35
path = "M" + " L".join(pts)
bands = [("RADIO", 95), ("MICROWAVE", 245), ("INFRARED", 395), ("VISIBLE", 503), ("UV", 590), ("X-RAY", 672), ("GAMMA", 748)]
labels = "".join(f'<text x="{bx}" y="160" text-anchor="middle">{b}</text>' for b, bx in bands)
html = f'''<section class="cover"><style>
.cover {{ width: 8.5in; height: 11in; position: relative; overflow: hidden; color: #fff;
  background: radial-gradient(ellipse at 70% 38%, #1d3557 0%, #0f1d33 55%, #0a1424 100%); font-family: Inter, sans-serif; }}
.cover .kicker {{ position: absolute; top: 0.95in; left: 0.9in; font-size: 10pt; letter-spacing: 0.32em; font-weight: 700; color: #e9b44c; }}
.cover h1 {{ position: absolute; top: 1.3in; left: 0.86in; margin: 0; font-family: "Inter Display", Inter, sans-serif; font-weight: 800;
  font-size: 58pt; line-height: 0.98; letter-spacing: -0.03em; }}
.cover .sub {{ position: absolute; top: 3.55in; left: 0.9in; width: 6.2in; font-size: 13.5pt; line-height: 1.45; color: #c9d4e3; font-weight: 400; }}
.cover svg.wave {{ position: absolute; top: 5.05in; left: 0; width: 8.5in; }}
.cover .topics {{ position: absolute; top: 7.75in; left: 0.9in; width: 6.7in; display: grid; grid-template-columns: 1.9fr 2.3fr 1.9fr; gap: 0.08in 0.25in;
  font-size: 9.6pt; color: #aebbd0; }}
.cover .topics div::before {{ content: ""; display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: #e9b44c; margin-right: 8px; vertical-align: 1px; }}
.cover .foot {{ position: absolute; bottom: 0.8in; left: 0.9in; right: 0.9in; border-top: 1px solid rgba(255,255,255,0.22); padding-top: 0.16in;
  display: flex; justify-content: space-between; font-size: 10pt; color: #c9d4e3; }}
.cover .foot strong {{ color: #fff; font-weight: 650; }}
</style>
<div class="kicker">A PERSONAL TEXTBOOK</div>
<h1>Light, Waves<br>&amp; Radiation</h1>
<div class="sub">Electromagnetic waves, photons, atoms and energy levels, reflection and refraction, color, diffraction,
infrared and heat, ionizing radiation, and X-ray diffraction &mdash; explained from the ground up, with the <em>why</em> behind every idea.</div>
<svg class="wave" viewBox="0 0 {W} 200" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="spec" x1="{x0}" x2="{x1}" y1="0" y2="0" gradientUnits="userSpaceOnUse">
<stop offset="0" stop-color="#5b2333"/><stop offset="0.34" stop-color="#8f2d3a"/><stop offset="0.52" stop-color="#b3262e"/>
<stop offset="0.565" stop-color="#ff3b1f"/><stop offset="0.6" stop-color="#ff9a1f"/><stop offset="0.625" stop-color="#ffe23a"/>
<stop offset="0.655" stop-color="#4ccf4c"/><stop offset="0.69" stop-color="#2f8fff"/><stop offset="0.72" stop-color="#6a4cff"/>
<stop offset="0.8" stop-color="#a98bff"/><stop offset="0.9" stop-color="#d9ccff"/><stop offset="1" stop-color="#ffffff"/></linearGradient></defs>
<path d="{path}" fill="none" stroke="url(#spec)" stroke-width="2.4" stroke-linejoin="round"/>
<g font-family="Inter, sans-serif" font-size="10.5" font-weight="700" letter-spacing="1.6" fill="#8496b0">{labels}</g>
<g stroke="#8496b0" stroke-width="1" opacity="0.6"><line x1="{x0}" y1="140" x2="{x1}" y2="140"/></g>
<text x="{x0}" y="186" font-size="10" fill="#8496b0" font-family="Inter, sans-serif">longer wavelength · lower photon energy</text>
<text x="{x1}" y="186" font-size="10" fill="#8496b0" font-family="Inter, sans-serif" text-anchor="end">shorter wavelength · higher photon energy</text>
</svg>
<div class="topics"><div>What a light wave is</div><div>Photons &amp; photoelectric effect</div><div>The full EM spectrum</div>
<div>Atoms &amp; energy levels</div><div>Absorption &amp; emission</div><div>Reflection &amp; refraction</div>
<div>Why things have color</div><div>Interference &amp; diffraction</div><div>Infrared &amp; heat</div>
<div>Ionizing radiation</div><div>Shielding &amp; space</div><div>X-rays &amp; Bragg&rsquo;s law</div></div>
<div class="foot"><span>Written for <strong>Chase Yarnall</strong></span><span>Fall 2026</span></div>
</section>'''
Path(__file__).resolve().parent.parent.joinpath("front/cover.html").write_text(html)
print("cover written")
