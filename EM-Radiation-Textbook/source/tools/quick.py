#!/usr/bin/env python3
"""Build the Quick Version PDF: prologue + per chapter (your questions, key ideas, summary).

Run after assemble.py: page references point at the full book (build/book.pdf).
"""
import sys
from pathlib import Path
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
from assemble import PARTS, BOOK, BUILD, SRC, parse_chapter, render, dest_pages, read  # noqa: E402

OUT = BOOK / "Light_Waves_and_Radiation_QUICK_VERSION.pdf"


def main():
    pages, _ = dest_pages(BUILD / "book.pdf")
    body = ['''<section class="frontback qv-intro">
<div class="chapter-num">Light, Waves &amp; Radiation</div>
<h1 class="fm-title">The Quick Version</h1>
<p class="fm-lead">The essentials of the full book in a fraction of the pages. Read the Prologue for the whole story,
then for each chapter: your questions with one-line answers, the key ideas, and the summary.
Page numbers (“p.&nbsp;57”) and figure numbers point to the full textbook, where each idea is explained properly.</p>
</section>''']
    prologue = read("front/prologue.html").replace('class="chapter" id="prologue"', 'class="qv-prologue"')
    body.append(prologue)
    for roman, ptitle, _, cids in PARTS:
        body.append(f'<div class="part-banner qv-part">Part {roman} · <span>{ptitle}</span></div>')
        for cid in cids:
            c = parse_chapter(cid)
            soup = BeautifulSoup(c["html"], "html.parser")
            out = [f'<section class="qv-ch"><h2 class="qv-title"><span class="sec-num">{c["num"]}</span>{c["title"]}'
                   f'<span class="qi-pg">full chapter p.&nbsp;{pages.get(cid, "?")}</span></h2>']
            if c["asked"]:
                for a in c["asked"]:
                    out.append(f'<div class="qi"><div class="qi-q"><span>{a["q"]}</span>'
                               f'<span class="qi-pg">p.&nbsp;{pages.get(a["id"], "?")}</span></div>'
                               f'<div class="qi-a">{a["a"]}</div></div>')
            for k in soup.select("div.box.key"):
                for t in k.find_all(id=True):
                    del t["id"]
                out.append(str(k))
            summ = soup.select_one(".summary ul")
            if summ:
                out.append('<div class="qv-summary"><div class="box-title">Summary</div>' + str(summ) + "</div>")
            out.append("</section>")
            body.append("\n".join(out))
    pdf = render("\n".join(body), "quick")
    import shutil
    shutil.copy(pdf, OUT)
    from pypdf import PdfReader
    print(f"wrote {OUT} ({len(PdfReader(str(OUT)).pages)} pages)")


if __name__ == "__main__":
    main()
