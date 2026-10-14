#!/usr/bin/env python3
"""Build the textbook PDF (or a single-chapter preview).

  python3 build.py                 # full book -> ../../EM_Waves_and_Radiation.pdf
  python3 build.py --only ch05     # preview one chapter -> ../build/ch05.pdf + PNG pages
  python3 build.py --only ch05 --png-dpi 70
"""
import argparse, json, os, re, subprocess, sys, shutil
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
SRC = TOOLS.parent
BOOK = SRC.parent
BUILD = SRC / "build"
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

ORDER = json.loads((SRC / "order.json").read_text()) if (SRC / "order.json").exists() else []

FOOTER = """<div style="width:100%;font-family:Inter,sans-serif;font-size:7.5pt;color:#7b8794;
  padding:0 0.9in;display:flex;justify-content:space-between;">
  <span>Light, Waves &amp; Radiation</span><span class="pageNumber"></span></div>"""


def wrap(body_html, title):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{title}</title>
<link rel="stylesheet" href="{(TOOLS / 'node_modules/katex/dist/katex.min.css').as_uri()}">
<link rel="stylesheet" href="{(SRC / 'book.css').as_uri()}">
<base href="{SRC.as_uri()}/">
</head><body>
{body_html}
</body></html>"""


def render_math(html_in: Path, html_out: Path):
    r = subprocess.run(["node", str(TOOLS / "render_math.js"), str(html_in), str(html_out)],
                       capture_output=True, text=True)
    if r.stderr:
        print(r.stderr, file=sys.stderr)
    return r.returncode == 0


def to_pdf(html_path: Path, pdf_path: Path, footer=True):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        pg = b.new_page()
        pg.goto(html_path.as_uri(), wait_until="networkidle")
        pg.evaluate("document.fonts.ready")
        pg.pdf(path=str(pdf_path), format="Letter", print_background=True,
               prefer_css_page_size=True, display_header_footer=footer,
               header_template="<span></span>", footer_template=FOOTER if footer else "<span></span>",
               outline=True, tagged=True)
        b.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="chapter file stem, e.g. ch05")
    ap.add_argument("--png-dpi", type=int, default=60)
    ap.add_argument("--no-png", action="store_true")
    a = ap.parse_args()
    BUILD.mkdir(exist_ok=True)

    if a.only:
        f = SRC / "chapters" / f"{a.only}.html"
        body = f.read_text()
        ans = SRC / "answers" / f"{a.only}-answers.html"
        if ans.exists():
            body += '\n<section class="frontback answers">' + ans.read_text() + "</section>"
        raw = BUILD / f"{a.only}.raw.html"; out = BUILD / f"{a.only}.html"; pdf = BUILD / f"{a.only}.pdf"
        raw.write_text(wrap(body, a.only))
        ok = render_math(raw, out)
        to_pdf(out, pdf)
        print(f"PDF: {pdf}  (math ok: {ok})")
        if not a.no_png:
            pdir = BUILD / f"preview-{a.only}"
            shutil.rmtree(pdir, ignore_errors=True); pdir.mkdir()
            subprocess.run(["pdftoppm", "-png", "-r", str(a.png_dpi), str(pdf), str(pdir / "page")], check=True)
            print(f"PNG pages: {pdir}/page-*.png")
        return

    # full book: assembled by assemble.py into build/book.raw.html
    subprocess.run([sys.executable, str(TOOLS / "assemble.py")], check=True)


if __name__ == "__main__":
    main()
