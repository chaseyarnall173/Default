# Style Guide — "Light, Waves & Radiation: A Personal Textbook"

## Who the reader is
- First-year Mechanical Engineering student at Northeastern (BSME, aerospace minor), currently in
  **ME2340 Intro to Materials Science** (Callister-style course: crystal structures, Miller indices,
  ceramics, interstitial sites) and a Cornerstone engineering design course.
- Comfortable with algebra and basic trig; has seen some calculus. No prior quantum mechanics.
- Very curious; gets pulled down "rabbit holes" wanting the *why* behind everything (e.g. spent 40 minutes
  on how EM radiation produces color). Wants ONE resource that answers everything so they stop
  having to Google. Reading *Project Hail Mary* (Andy Weir) and asked several physics questions from it.
- Goal of the book: genuine understanding. Every claim should come with the *mechanism* ("what is
  physically happening"), not just a definition. Build intuition first, then numbers.

## Voice
- **Concise (reader request: "not too wordy").** ~2,000–3,000 words of main text per chapter. One idea per
  paragraph, 2–4 sentences. No throat-clearing or repeated restatements. Let figures, tables and short bullet
  lists carry comparisons and steps. Analogies 1–3 sentences; Rabbit Holes short.
- Warm, direct, second person ("you"). Clear like a great TA explaining at a whiteboard.
- Short paragraphs. Concrete numbers and everyday examples (microwave oven, sunglasses, a black car in sun,
  a stovetop glowing red, Wi-Fi, a rainbow, sunburn, X-ray at the dentist, gold vs. silver color).
- Accurate. Where pop-science simplifications are wrong or misleading, say so (Myth vs. Reality box).
  When something is a model/approximation, say it is. Never invent numbers — verify them.
- No emoji. American spelling. SI units, with eV for photon/atomic energies.
- Plain-language first, then the precise statement. Define every term the first time you use it (bold it).

## File layout (all paths relative to `EM-Radiation-Textbook/source/`)
- `chapters/chNN.html` — your chapter HTML fragment (NN = two-digit chapter number).
- `answers/chNN-answers.html` — full worked answers to that chapter's Check Yourself questions.
- `figures/chNN-<name>.svg` (preferred) or `.png` (only for raster, ≥ 300 dpi) — figure files.
- `figures/scripts/chNN_<name>.py` — the matplotlib script that generated each data figure.
- `glossary/chNN.json` — `[{"term": "...", "definition": "one or two sentences"}, ...]` (8–20 terms).
- `formulas/chNN.json` — `[{"name": "...", "latex": "...", "meaning": "plain-language meaning + units"}]`.
- `sources/chNN.md` — bullet list of sources you actually consulted: `- Title — Publisher — URL`.
- DO NOT edit files outside your own chapters/figures. DO NOT run any git commands.

## HTML fragment structure (copy this skeleton exactly)
```html
<section class="chapter" id="ch05">
<div class="chapter-opener">
  <div class="chapter-num">Chapter 5</div>
  <h1 class="chapter-title">Absorption and Emission</h1>
  <p class="chapter-hook">One or two italic sentences that make the reader care.</p>
  <div class="big-picture"><h4>The big picture</h4><ul><li>3–5 one-line takeaways</li></ul></div>
  <div class="learning-goals"><h4>After this chapter you can</h4><ul><li>3–6 goals</li></ul></div>
</div>

<h2 id="ch05-1"><span class="sec-num">5.1</span>Section title</h2>
<p>...</p>
<h3>Subsection title (no number)</h3>
...
<div class="summary"><h2>Chapter summary</h2><ul><li>...</li></ul></div>
<div class="check"><h2>Check yourself</h2><ol>
  <li><span class="tag">Concept</span>...</li>
  <li><span class="tag">Calc</span>...</li>
</ol><p class="small muted">Full solutions are in the Answer Key at the back of the book.</p></div>
</section>
```
- Section ids: `chNN-K` (e.g. `ch05-3`). `<h2>` = numbered sections, `<h3>` = unnumbered subsections.
  Do not use `<h1>` except the chapter title.

## Boxes (use these classes only)
```html
<div class="box key"><div class="box-title">Key Idea</div><p>...</p></div>
<div class="box analogy"><div class="box-title">Analogy</div><p>...</p></div>
<div class="box myth"><div class="box-title">Myth vs. Reality</div>
  <p class="myth-line"><strong>Myth:</strong> ...</p><p><strong>Reality:</strong> ...</p></div>
<div class="box rabbit"><div class="box-title">Rabbit Hole <span class="sub">(optional) — Short title</span></div><p>...</p></div>
<div class="box asked"><div class="box-title">You Asked</div><p class="question">“The reader's question, lightly cleaned up”</p><p>Direct answer...</p></div>
<div class="box hailmary"><div class="box-title">Project Hail Mary Connection</div><p>...</p></div>
<div class="box matsci"><div class="box-title">Materials Science Connection</div><p>...</p></div>
<div class="box example"><div class="box-title">Worked Example 5.1 <span class="sub">— Title</span></div>
  <p class="given"><strong>Given:</strong> ...</p><p><strong>Find:</strong> ...</p>
  <p><strong>Think:</strong> what physics applies and why</p>
  <p>steps with math...</p>
  <p class="answer">Answer: ...</p></div>
```
- **Rabbit Hole** boxes are the release valve for this reader: put fascinating-but-optional depth there
  so the main text stays clean. Say explicitly that it's safe to skip.
- **You Asked** boxes answer the reader's actual search questions (listed in your task). Answer each
  one directly in the first sentence, then explain. Each listed question must get its own box.
- Add `long` to a box's class (`class="box rabbit long"`) only if it is longer than ~1/3 page so it may split across pages.
- Aim per chapter: 2–4 Key Ideas, 1–3 Analogies, 2–4 Myth vs. Reality, 1–3 Rabbit Holes,
  2–4 Worked Examples, plus all assigned You Asked / Hail Mary / Materials Science boxes.

## Math (rendered by KaTeX at build time)
- Inline: `\( E = hf \)`. Display: inside an equation div:
  `<div class="equation" data-eq="5.2">\[ E_\text{photon} = E_\text{upper} - E_\text{lower} \]</div>`
  Use `class="equation boxed"` for the 1–3 most important equations of the chapter.
  Number equations `N.k` in order within your chapter. Optional `<p class="where">where ...</p>` after.
- Inside math NEVER use raw `<`, `>` or `&` — use `\lt`, `\gt`, `\approx`, `\sim`, `\ll`, `\gg`.
  Do not put `·` inside `\text{}`; write `\text{eV}\cdot\text{nm}`.
- Units in math: `500\,\text{nm}`, `3.00\times10^{8}\,\text{m/s}`.
- Use KaTeX-supported LaTeX only (no `\SI`, no `\unit` from siunitx, no `align` — use `aligned` inside `\[ \]`).
- Use the book's constants consistently: \(c = 3.00\times10^8\) m/s, \(h = 6.626\times10^{-34}\) J·s,
  \(hc = 1240\) eV·nm, \(1\ \text{eV} = 1.602\times10^{-19}\) J, \(k_B = 1.381\times10^{-23}\) J/K,
  \(\sigma = 5.67\times10^{-8}\) W/(m²K⁴), Wien \(b = 2898\ \mu\text{m·K}\) (write as `2898\,\mu\text{m}\cdot\text{K}`).

## Figures
- Every chapter needs **4–8 figures**: schematic diagrams that show the real mechanism, plus data plots where useful.
- Markup:
```html
<figure id="fig-5-2"><img src="figures/ch05-energy-levels.svg" alt="...">
<figcaption><span class="fig-num">Figure 5.2</span> Caption that explains what to notice.</figcaption></figure>
```
  Add `class="narrow"` (72% width) or `class="small"` (52%) on `<figure>` for tall/simple figures.
  Text width is 6.7 in; design figures ~ 680 × (250–420) px viewBox so text inside stays readable.
- Hand-written SVG files are great for schematics. Requirements: `xmlns="http://www.w3.org/2000/svg"`,
  a `viewBox`, `font-family="Inter, sans-serif"`, text ≥ 11 px at a 680-px-wide viewBox, white or
  transparent background, no external references. Label things directly instead of using legends.
- matplotlib (installed) for data plots: save as SVG with `plt.rcParams['svg.fonttype']='none'`,
  `font.family='Inter'`, font size ≥ 10, figure width 6.8 in, no top/right spines, thin gridlines,
  `bbox_inches='tight'`. Load the `dataviz` skill (Skill tool) before writing your first chart.
- Shared color meanings across the whole book (use them!):
  - Electric field **#d1495b** (red) · Magnetic field **#2e6fdb** (blue) · Light/photon ray **#e09f1f** (amber)
  - Electron **#12a39a** (teal) · Nucleus **#8d5a97** (purple) · Matter/material fills **#d9dee5** with **#52606d** strokes
  - Text **#1f2933**, secondary text **#52606d**, accent green **#0b6e4f**
  - For anything showing visible light, use physically sensible spectral colors (violet ≈ 400 nm → red ≈ 700 nm).
- Number figures `Figure N.k` in order of appearance. Reference them in the text ("see Figure 5.2").
- Tables: `<table><caption><span class="tab-num">Table 5.1</span> ...</caption> ...</table>`.

## Check Yourself + Answer Key
- 8–12 questions per chapter: mix of `Concept`, `Calc`, and `Apply` (real-world / materials science) tags.
  At least 3 numeric.
- `answers/chNN-answers.html` contains:
```html
<h3>Chapter 5 — Absorption and Emission</h3>
<ol><li><p>Full solution with reasoning (not just the number)...</p></li> ...</ol>
```
  Same order/count as the questions.

## Previewing your work (required before you finish)
From `EM-Radiation-Textbook/source/`:
```
python3 tools/build.py --only ch05            # -> build/ch05.pdf and build/preview-ch05/page-*.png
```
It reports KaTeX errors on stderr — fix all of them. Then LOOK at the PNG pages with the Read tool
(at least every page that has a figure or a table). Fix overlapping labels, clipped SVG text, figures that
are too small/large, broken math, or boxes that look wrong. Use `--png-dpi 90` to inspect detail.

## Accuracy
- Verify facts and numbers with reputable sources (OpenStax University Physics / College Physics,
  HyperPhysics (Georgia State), NASA Science, NIST, Callister's *Materials Science and Engineering*,
  US NRC / EPA / CDC for radiation, Britannica, university physics department pages).
  Do not cite journal articles. Record what you used in `sources/chNN.md`.
- Use WebSearch / WebFetch to check anything you are not certain about. If load-bearing details for a
  Project Hail Mary box can't be verified, keep the box general rather than guessing.
- Project Hail Mary: assume the reader is mid-book. Discuss only the specific scene/question given; do not
  reveal later plot twists or the ending.
