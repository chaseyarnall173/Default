// Server-side KaTeX: replaces \( ... \) (inline) and \[ ... \] (display) in an HTML file.
// Usage: node render_math.js in.html out.html
const fs = require('fs');
const katex = require('katex');
const [,, inPath, outPath] = process.argv;
let html = fs.readFileSync(inPath, 'utf8');
let errors = 0;
function render(tex, display, ctx) {
  // middle dot inside \text{} breaks KaTeX: split the text group around it
  let prev;
  do { prev = tex; tex = tex.replace(/\\(text|mathrm)\{([^{}]*)·([^{}]*)\}/g, '\\$1{$2}\\cdot\\$1{$3}'); } while (tex !== prev);
  tex = tex.replace(/·/g, '\\cdot ');
  try {
    return katex.renderToString(tex, { displayMode: display, throwOnError: true, strict: 'ignore', output: 'html', macros: { '\\unit': '\\,\\mathrm{#1}' } });
  } catch (e) {
    errors++;
    console.error(`KaTeX error (${display ? 'display' : 'inline'}): ${e.message}\n   in: ${tex.slice(0, 120)}`);
    return `<span style="color:#c00;font-weight:bold">[MATH ERROR: ${tex.replace(/</g,'&lt;')}]</span>`;
  }
}
// Skip <script>/<style> blocks
const parts = html.split(/(<script[\s\S]*?<\/script>|<style[\s\S]*?<\/style>)/i);
for (let i = 0; i < parts.length; i += 2) {
  parts[i] = parts[i]
    .replace(/\\\[([\s\S]+?)\\\]/g, (m, tex) => render(tex.trim(), true))
    .replace(/\\\(([\s\S]+?)\\\)/g, (m, tex) => render(tex.trim(), false));
}
fs.writeFileSync(outPath, parts.join(''));
if (errors) { console.error(`${errors} math error(s)`); process.exitCode = 2; }
