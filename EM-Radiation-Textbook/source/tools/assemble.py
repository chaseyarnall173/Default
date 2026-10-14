#!/usr/bin/env python3
"""Assemble the full book: front matter + parts/chapters + generated back matter -> PDF.

Two passes: pass 1 renders with placeholder page numbers and reads the PDF's named
destinations (every TOC / index entry is an internal link, so Chromium emits a destination
for each target); pass 2 renders again with the real page numbers filled in.
"""
import html as htmlmod, json, re, subprocess, sys
from pathlib import Path
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import SRC, BUILD, BOOK, CHROME, FOOTER, wrap, render_math  # noqa: E402

OUT_PDF = BOOK / "Light_Waves_and_Radiation_Textbook.pdf"
TITLE = "Light, Waves & Radiation"
SUBTITLE = "A Personal Textbook on Electromagnetic Waves, Light, Optics, and Radiation"

PARTS = [
    ("I", "What Light Is",
     "Before light can do anything to matter, you need a clear picture of what it is: a traveling ripple "
     "in electric and magnetic fields that is delivered in discrete packets called photons.",
     ["ch01", "ch02", "ch03"]),
    ("II", "Atoms and Energy Levels",
     "Light talks to matter through electrons. Here is where those electrons live, why their energies come "
     "in fixed steps, and how jumping between steps absorbs and creates light.",
     ["ch04", "ch05"]),
    ("III", "When Light Meets Matter",
     "Reflection, transparency, color, diffraction and heat are all the same story told at different "
     "wavelengths: a wave arrives, charges respond, and something new leaves.",
     ["ch06", "ch07", "ch08", "ch09"]),
    ("IV", "Radiation",
     "At the high-energy end of the spectrum, single photons can rip electrons off atoms. This part covers "
     "ionizing radiation, shielding, space, and the X-ray tools materials scientists use to see crystals.",
     ["ch10", "ch11"]),
]
FRONT = ["front/welcome.html"]          # before the generated Contents
PROLOGUE = "front/prologue.html"        # after the questions index, before Part I


def read(p):
    return (SRC / p).read_text()


# ---------------------------------------------------------------- chapter parsing
def tag_boxes(chap_html, cid):
    """Give every You Asked / Myth box a stable id (needed as link targets)."""
    counters = {"asked": 0, "myth": 0}
    def sub(m):
        attrs_before, kind, rest_cls, attrs_after = m.group(1), m.group(2), m.group(3), m.group(4)
        if "id=" in attrs_before + attrs_after:
            return m.group(0)
        counters[kind] += 1
        pre = "q" if kind == "asked" else "m"
        return f'<div{attrs_before} id="{pre}-{cid}-{counters[kind]}" class="box {kind}{rest_cls}"{attrs_after}>'
    return re.sub(r'<div([^>]*?)\sclass="box (asked|myth)\b([^"]*)"([^>]*)>', sub, chap_html)


def first_sentence(inner_html):
    text = inner_html.strip()
    # don't split inside math
    masked = re.sub(r"\\\(.*?\\\)", lambda m: "x" * len(m.group(0)), text, flags=re.S)
    for m in re.finditer(r"[.!?](?:</strong>|</em>|</b>)?\s+(?=[A-Z(<“\"])", masked):
        if m.start() < 25:
            continue
        before = masked[max(0, m.start() - 5):m.start() + 1].lower()
        if before.endswith(("e.g.", "i.e.", "etc.", " vs.", "approx.")):
            continue
        frag = text[:m.end()].strip()
        return str(BeautifulSoup(frag, "html.parser"))
    return text


def parse_chapter(cid):
    raw = tag_boxes(read(f"chapters/{cid}.html"), cid)
    soup = BeautifulSoup(raw, "html.parser")
    num = soup.select_one(".chapter-num")
    title = soup.select_one("h1.chapter-title")
    info = {"id": cid, "html": raw,
            "num": re.sub(r"\D", "", num.get_text()) if num else cid[2:].lstrip("0"),
            "title": title.get_text(" ", strip=True) if title else cid,
            "sections": [], "asked": [], "myths": []}
    for h2 in soup.find_all("h2"):
        if h2.get("id") and h2.find(class_="sec-num"):
            sn = h2.find(class_="sec-num").get_text(strip=True)
            t = h2.get_text(" ", strip=True)[len(sn):].strip()
            info["sections"].append((h2["id"], sn, t))
    for box in soup.select("div.box.asked"):
        q = box.select_one(".question")
        ps = [p for p in box.find_all("p") if "question" not in (p.get("class") or [])]
        info["asked"].append({"id": box["id"], "q": q.decode_contents() if q else "",
                              "a": first_sentence(ps[0].decode_contents()) if ps else ""})
    for box in soup.select("div.box.myth"):
        ps = box.find_all("p")
        myth = reality = ""
        for p in ps:
            t = p.get_text(" ", strip=True)
            inner = p.decode_contents()
            if t.lower().startswith("myth"):
                myth = re.sub(r"^\s*<strong>\s*Myth:?\s*</strong>:?\s*", "", inner)
            elif t.lower().startswith("reality") and not reality:
                reality = first_sentence(re.sub(r"^\s*<strong>\s*Reality:?\s*</strong>:?\s*", "", inner))
        if myth:
            info["myths"].append({"id": box["id"], "myth": myth, "reality": reality})
    return info


# ---------------------------------------------------------------- generated pages
def pg(pages, key):
    return f'<a class="pg" href="#{key}">{pages.get(key, "00")}</a>'


def toc_html(chapters, pages):
    rows = ['<section class="frontback toc" id="toc"><h1 class="fm-title">Contents</h1><div class="toc-list">']
    rows.append(f'<div class="toc-fm"><a href="#questions">Your Questions, Answered</a>{pg(pages, "questions")}</div>')
    rows.append(f'<div class="toc-fm"><a href="#prologue">Prologue: The Whole Story in Ten Minutes</a>{pg(pages, "prologue")}</div>')
    for roman, ptitle, _, cids in PARTS:
        pid = f"part-{roman}"
        rows.append(f'<div class="toc-part"><a href="#{pid}">Part {roman} · {ptitle}</a>{pg(pages, pid)}</div>')
        for cid in cids:
            c = chapters.get(cid)
            if not c:
                continue
            rows.append(f'<div class="toc-ch"><a href="#{cid}"><span class="toc-n">{c["num"]}</span>{c["title"]}</a>{pg(pages, cid)}</div>')
            for sid, sn, t in c["sections"]:
                rows.append(f'<div class="toc-sec"><a href="#{sid}"><span class="toc-n">{sn}</span>{t}</a>{pg(pages, sid)}</div>')
    rows.append('<div class="toc-part"><a href="#backmatter">Reference</a>' + pg(pages, "backmatter") + '</div>')
    for bid, bt in [("formulas", "Formula Sheet & Constants"), ("myths", "Myth-Busting Roundup"),
                    ("glossary", "Glossary"), ("answers", "Answer Key"), ("sources", "Sources & Further Reading")]:
        rows.append(f'<div class="toc-ch"><a href="#{bid}">{bt}</a>{pg(pages, bid)}</div>')
    rows.append("</div></section>")
    return "\n".join(rows)


def questions_html(chapters, pages):
    out = ['<section class="frontback questions" id="questions"><h1 class="fm-title">Your Questions, Answered</h1>',
           '<p class="fm-lead">This book started from the questions you typed into search bars while studying. '
           'Every one of them is answered somewhere in these pages. Here is each question, the one-line answer, '
           'and the page where the full explanation lives.</p>']
    for roman, ptitle, _, cids in PARTS:
        for cid in cids:
            c = chapters.get(cid)
            if not c or not c["asked"]:
                continue
            out.append(f'<h3 class="qi-ch">Chapter {c["num"]} · {c["title"]}</h3>')
            for a in c["asked"]:
                out.append(f'<div class="qi"><div class="qi-q"><a href="#{a["id"]}">{a["q"]}</a>'
                           f'<span class="qi-pg">p.&nbsp;{pg(pages, a["id"])}</span></div>'
                           f'<div class="qi-a">{a["a"]}</div></div>')
    out.append("</section>")
    return "\n".join(out)


def myths_html(chapters, pages):
    out = ['<section class="frontback myths" id="myths"><h1 class="fm-title">Myth-Busting Roundup</h1>',
           '<p class="fm-lead">Popular explanations of light and radiation are full of half-truths. '
           'Here are the ones this book corrects, with the page where each is explained.</p>']
    for roman, ptitle, _, cids in PARTS:
        for cid in cids:
            c = chapters.get(cid)
            if not c:
                continue
            for m in c["myths"]:
                out.append(f'<div class="mr"><div class="mr-myth"><span class="mr-label">Myth</span>{m["myth"]}'
                           f'<span class="qi-pg">p.&nbsp;{pg(pages, m["id"])}</span></div>'
                           f'<div class="mr-real"><span class="mr-label real">Reality</span>{m["reality"]}</div></div>')
    out.append("</section>")
    return "\n".join(out)


CONSTANTS = [
    ("Speed of light in vacuum", r"c = 2.998\times10^{8}\ \text{m/s} \approx 3.00\times10^{8}\ \text{m/s}"),
    ("Planck's constant", r"h = 6.626\times10^{-34}\ \text{J}\cdot\text{s} = 4.136\times10^{-15}\ \text{eV}\cdot\text{s}"),
    ("Photon-energy shortcut", r"hc = 1240\ \text{eV}\cdot\text{nm}"),
    ("Electron-volt", r"1\ \text{eV} = 1.602\times10^{-19}\ \text{J}"),
    ("Elementary charge", r"e = 1.602\times10^{-19}\ \text{C}"),
    ("Electron mass", r"m_e = 9.109\times10^{-31}\ \text{kg}"),
    ("Proton mass", r"m_p = 1.673\times10^{-27}\ \text{kg}"),
    ("Boltzmann constant", r"k_B = 1.381\times10^{-23}\ \text{J/K} = 8.617\times10^{-5}\ \text{eV/K}"),
    ("Stefan–Boltzmann constant", r"\sigma = 5.670\times10^{-8}\ \text{W}/(\text{m}^2\text{K}^4)"),
    ("Wien's displacement constant", r"b = 2898\ \mu\text{m}\cdot\text{K}"),
    ("Avogadro's number", r"N_A = 6.022\times10^{23}\ \text{mol}^{-1}"),
    ("Hydrogen ground-state energy", r"E_1 = -13.6\ \text{eV}"),
    ("Bohr radius", r"a_0 = 0.0529\ \text{nm}"),
    ("Cu Kα X-ray wavelength", r"\lambda_{\text{Cu K}\alpha} = 0.1542\ \text{nm}"),
]


def formulas_html(chapters):
    out = ['<section class="frontback formulas" id="formulas"><h1 class="fm-title">Formula Sheet &amp; Constants</h1>',
           '<h3>Constants and handy numbers</h3><table class="fs"><tr><th>Quantity</th><th>Value</th></tr>']
    for n, v in CONSTANTS:
        out.append(f"<tr><td>{n}</td><td>\\({v}\\)</td></tr>")
    out.append("</table>")
    for roman, ptitle, _, cids in PARTS:
        for cid in cids:
            f = SRC / "formulas" / f"{cid}.json"
            c = chapters.get(cid)
            if not f.exists() or not c:
                continue
            items = json.loads(f.read_text())
            out.append(f'<h3>Chapter {c["num"]} · {c["title"]}</h3><table class="fs"><tr><th style="width:24%">Name</th>'
                       f'<th style="width:36%">Formula</th><th>What it means</th></tr>')
            for it in items:
                out.append(f'<tr><td>{htmlmod.escape(it.get("name",""))}</td><td>\\({it.get("latex","")}\\)</td>'
                           f'<td>{it.get("meaning","")}</td></tr>')
            out.append("</table>")
    out.append("</section>")
    return "\n".join(out)


def glossary_html(chapters):
    terms = {}
    for roman, ptitle, _, cids in PARTS:
        for cid in cids:
            f = SRC / "glossary" / f"{cid}.json"
            if not f.exists() or cid not in chapters:
                continue
            for it in json.loads(f.read_text()):
                key = it["term"].strip().lower()
                if key not in terms:
                    terms[key] = (it["term"].strip(), it["definition"].strip(), [chapters[cid]["num"]])
                elif chapters[cid]["num"] not in terms[key][2]:
                    terms[key][2].append(chapters[cid]["num"])
    out = ['<section class="frontback glossary" id="glossary"><h1 class="fm-title">Glossary</h1><div class="gl-cols">']
    for key in sorted(terms, key=lambda k: re.sub(r"[^a-z0-9 ]", "", k)):
        t, d, chs = terms[key]
        out.append(f'<p class="gl"><strong>{t}</strong> — {d} <span class="gl-ch">(Ch.&nbsp;{", ".join(chs)})</span></p>')
    out.append("</div></section>")
    return "\n".join(out)


def answers_html(chapters):
    out = ['<section class="frontback answers" id="answers"><h1 class="fm-title">Answer Key</h1>',
           '<p class="fm-lead">Full solutions to every Check Yourself question. Try each question before you look.</p>']
    for roman, ptitle, _, cids in PARTS:
        for cid in cids:
            f = SRC / "answers" / f"{cid}-answers.html"
            if f.exists() and cid in chapters:
                out.append(f'<div class="ans-ch">{f.read_text()}</div>')
    out.append("</section>")
    return "\n".join(out)


def sources_html(chapters):
    out = ['<section class="frontback sources" id="sources"><h1 class="fm-title">Sources &amp; Further Reading</h1>',
           '<p class="fm-lead">The references each chapter was checked against. Great places to keep exploring: '
           'HyperPhysics, OpenStax University Physics (free), NASA Science, and the optical-properties and '
           'X-ray-diffraction sections of Callister’s <em>Materials Science and Engineering</em>.</p>']
    for roman, ptitle, _, cids in PARTS:
        for cid in cids:
            f = SRC / "sources" / f"{cid}.md"
            if not f.exists() or cid not in chapters:
                continue
            out.append(f'<h3>Chapter {chapters[cid]["num"]} · {chapters[cid]["title"]}</h3><ul class="src">')
            for line in f.read_text().splitlines():
                line = line.strip()
                if not line.startswith(("-", "*")):
                    continue
                line = htmlmod.escape(line.lstrip("-* ").strip(), quote=False)
                line = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'\1 — <a href="\2">\2</a>', line)
                line = re.sub(r"(?<![\"'>])(https?://[^\s<)]+)", r'<a href="\1">\1</a>', line)
                out.append(f"<li>{line}</li>")
            out.append("</ul>")
    out.append("</section>")
    return "\n".join(out)


def part_html(roman, title, blurb, cids, chapters):
    items = "".join(f'<li><span class="toc-n">{chapters[c]["num"]}</span>{chapters[c]["title"]}</li>'
                    for c in cids if c in chapters)
    return (f'<section class="part" id="part-{roman}"><div class="part-label">Part {roman}</div>'
            f'<h1>{title}</h1><p>{blurb}</p><ul>{items}</ul></section>')


# ---------------------------------------------------------------- build
def assemble(chapters, pages):
    body = []
    for f in FRONT:
        body.append(read(f))
    body.append(toc_html(chapters, pages))
    body.append(questions_html(chapters, pages))
    if (SRC / PROLOGUE).exists():
        body.append(read(PROLOGUE))
    for roman, title, blurb, cids in PARTS:
        body.append(part_html(roman, title, blurb, cids, chapters))
        for cid in cids:
            if cid in chapters:
                body.append(chapters[cid]["html"])
    body.append('<section class="part" id="backmatter"><div class="part-label">Reference</div><h1>Tools for Review</h1>'
                '<p>Formula sheet, myth-busting roundup, glossary, full answer key, and sources.</p></section>')
    body.append(formulas_html(chapters))
    body.append(myths_html(chapters, pages))
    body.append(glossary_html(chapters))
    body.append(answers_html(chapters))
    body.append(sources_html(chapters))
    return "\n".join(body)


def render(html_body, name, footer=True):
    from playwright.sync_api import sync_playwright
    raw = BUILD / f"{name}.raw.html"; out = BUILD / f"{name}.html"; pdf = BUILD / f"{name}.pdf"
    raw.write_text(wrap(html_body, TITLE))
    if not render_math(raw, out):
        print("!! math errors above", file=sys.stderr)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        page = b.new_page()
        page.goto(out.as_uri(), wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        page.pdf(path=str(pdf), format="Letter", print_background=True, prefer_css_page_size=True,
                 display_header_footer=footer, header_template="<span></span>",
                 footer_template=FOOTER if footer else "<span></span>", outline=False, tagged=True)
        b.close()
    return pdf


def dest_pages(pdf):
    from pypdf import PdfReader
    r = PdfReader(str(pdf))
    return {k.lstrip("/"): str(r.get_destination_page_number(v) + 1) for k, v in r.named_destinations.items()}, len(r.pages)


def main():
    BUILD.mkdir(exist_ok=True)
    cids = [c for _, _, _, cs in PARTS for c in cs]
    chapters = {c: parse_chapter(c) for c in cids if (SRC / "chapters" / f"{c}.html").exists()}
    missing = [c for c in cids if c not in chapters]
    if missing:
        print("missing chapters:", missing)

    pdf1 = render(assemble(chapters, {}), "book-pass1")
    pages, n1 = dest_pages(pdf1)
    body_pdf = render(assemble(chapters, pages), "book")
    pages2, n2 = dest_pages(body_pdf)
    drift = [k for k in pages if pages2.get(k) != pages[k]]
    print(f"pass1 {n1} pages, pass2 {n2} pages, page-number drift on {len(drift)} targets")
    if drift:  # one more pass if the TOC length changed
        body_pdf = render(assemble(chapters, pages2), "book"); pages = pages2

    cover_pdf = render(read("front/cover.html"), "cover", footer=False)

    from pypdf import PdfReader, PdfWriter
    w = PdfWriter(clone_from=str(body_pdf))
    w.insert_page(PdfReader(str(cover_pdf)).pages[0], 0)
    P = lambda key: int(pages[key])  # body page n -> merged index n (cover at 0)
    w.add_outline_item("Cover", 0)
    for key, t in [("welcome", "How to Use This Book"), ("toc", "Contents"), ("questions", "Your Questions, Answered"),
                   ("prologue", "Prologue: The Whole Story in Ten Minutes")]:
        if key in pages:
            w.add_outline_item(t, P(key))
    for roman, title, _, cs in PARTS:
        pid = f"part-{roman}"
        part = w.add_outline_item(f"Part {roman} · {title}", P(pid)) if pid in pages else None
        for cid in cs:
            if cid not in chapters or cid not in pages:
                continue
            c = chapters[cid]
            ch = w.add_outline_item(f"{c['num']}. {c['title']}", P(cid), parent=part)
            for sid, sn, t in c["sections"]:
                if sid in pages:
                    w.add_outline_item(f"{sn} {t}", P(sid), parent=ch)
    ref = w.add_outline_item("Reference", P("backmatter")) if "backmatter" in pages else None
    for key, t in [("formulas", "Formula Sheet & Constants"), ("myths", "Myth-Busting Roundup"),
                   ("glossary", "Glossary"), ("answers", "Answer Key"), ("sources", "Sources & Further Reading")]:
        if key in pages:
            w.add_outline_item(t, P(key), parent=ref)
    w.add_metadata({"/Title": f"{TITLE}: {SUBTITLE}", "/Author": "Written for Chase Yarnall",
                    "/Subject": "Electromagnetic waves, light, optics, color, infrared, diffraction, ionizing radiation, X-ray diffraction"})
    w.page_mode = "/UseOutlines"
    with open(OUT_PDF, "wb") as fh:
        w.write(fh)
    print(f"wrote {OUT_PDF} ({len(w.pages)} pages)")


if __name__ == "__main__":
    main()
