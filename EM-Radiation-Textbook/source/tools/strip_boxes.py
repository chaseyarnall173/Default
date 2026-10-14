"""Remove whole <div class="box KIND ..."> blocks (balanced) from chapter HTML files."""
import re, sys, glob
def strip(html, kinds):
    out, i, removed = [], 0, 0
    pat = re.compile(r'<div[^>]*class="box (%s)\b[^"]*"[^>]*>' % "|".join(kinds))
    while True:
        m = pat.search(html, i)
        if not m:
            out.append(html[i:]); break
        out.append(html[i:m.start()])
        depth, j = 0, m.start()
        tok = re.compile(r'<div\b|</div>')
        for t in tok.finditer(html, m.start()):
            depth += 1 if t.group(0) == '<div' else -1
            if depth == 0:
                j = t.end(); break
        # eat trailing newline
        if html[j:j+1] == "\n": j += 1
        i = j; removed += 1
    return "".join(out), removed
if __name__ == "__main__":
    kinds = sys.argv[1].split(",")
    for f in sys.argv[2:]:
        s = open(f).read(); s2, n = strip(s, kinds)
        if n: open(f, "w").write(s2); print(f, "removed", n)
