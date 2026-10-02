#!/usr/bin/env python3
"""
A printable card for one recipe, with the cook's notes folded in.

    python3 card.py "apple pie"            -> build/cards/apple-pie.pdf (and .html)
    python3 card.py "apple pie" --notes    also print the generated "Further notes"
    python3 card.py "apple pie" --no-opt   leave out Claude's changes

Every ingredient line, direction and cook's note is copied from the master
VERBATIM. This script exists so that a card is never retyped by a model: a
retyped card once dropped the original measures, and another invented "45 g" for
a line that deliberately has no quantity. Nothing here computes, rounds, scales
or fills in anything.
"""
import json, sys, os, re, html, subprocess, shutil, glob, argparse
from recipe import load, one

CSS = """
@page { size: Letter; margin: 0.6in 0.65in; }
* { box-sizing: border-box; }
body { font-family: Georgia, 'DejaVu Serif', serif; font-size: 11pt; line-height: 1.38; color: #111; margin: 0; }
h1 { font-size: 21pt; margin: 0 0 3pt; line-height: 1.15; }
.meta { font-family: Helvetica, Arial, 'DejaVu Sans', sans-serif; font-size: 9pt; color: #444; margin-bottom: 10pt; }
.note { border: 1pt solid #888; border-left: 4pt solid #222; padding: 7pt 10pt; margin: 0 0 10pt; page-break-inside: avoid; }
.note p, .opt p { margin: 0 0 4pt; } .note p:last-child, .opt p:last-child { margin-bottom: 0; }
.label { font-family: Helvetica, Arial, 'DejaVu Sans', sans-serif; font-size: 8pt; letter-spacing: 0.08em; text-transform: uppercase;
         font-weight: bold; color: #222; margin: 0 0 4pt; }
.opt { border: 1pt dashed #888; padding: 7pt 10pt; margin: 0 0 12pt; font-size: 10pt; page-break-inside: avoid; }
table.body { width: 100%; border-collapse: collapse; }
td { vertical-align: top; padding: 0; }
td.ing { width: 37%; padding-right: 18pt; }
ul { list-style: none; margin: 0; padding: 0; }
li { margin: 0 0 3.5pt; padding-left: 10pt; text-indent: -10pt; }
li.head { font-weight: bold; margin-top: 7pt; } li.gap { height: 5pt; }
.dir p { margin: 0 0 7pt; }
.further { margin-top: 12pt; font-size: 9.5pt; color: #222; } .further p { margin: 0 0 5pt; }
.foot { font-family: Helvetica, Arial, 'DejaVu Sans', sans-serif; font-size: 8pt; color: #666; margin-top: 12pt; border-top: 0.5pt solid #aaa; padding-top: 4pt; }
"""

def esc(s): return html.escape(s, quote=False)
def lines(s): return (s or "").replace("\r\n", "\n").replace("\r", "\n").split("\n")
def paras(s):
    return "".join("<p>%s</p>" % esc(ln.strip()) for ln in lines(s) if ln.strip())

def render(r, with_notes=False, with_opt=True):
    t = r.get("timing") or {}; o = r.get("claude_opt") or {}
    meta = []
    if (r.get("source") or "").strip(): meta.append(esc(r["source"].strip()))
    if (r.get("servings") or "").strip(): meta.append("Serves: " + esc(r["servings"].strip()))
    if t.get("total"):
        s = ("" if t.get("source") == "stated" else "about ") + t["total"]
        if t.get("active"): s += ", %s%s hands-on" % ("~" if t.get("active_est") else "", t["active"])
        meta.append(s)
    if t.get("ahead_label"): meta.append("start ahead: " + esc(t["ahead_label"]))
    H = ["<!doctype html><html><head><meta charset='utf-8'><title>%s</title><style>%s</style></head><body>" % (esc(r["name"]), CSS)]
    H.append("<h1>%s</h1>" % esc(r["name"]))
    if meta: H.append("<div class='meta'>%s</div>" % " &nbsp;·&nbsp; ".join(meta))
    if (r.get("description") or "").strip():
        H.append("<div class='note'><div class='label'>Cook's notes</div>%s</div>" % paras(r["description"]))
    if with_opt and o.get("changes") and not o.get("none"):
        log = "".join("<p>&rarr; %s</p>" % esc(x.strip()) for x in (o.get("log") or []))
        H.append("<div class='opt'><div class='label'>Claude's suggested changes (the method below is the original)</div><p>%s</p>%s</div>"
                 % (esc(o["changes"].strip()), log))
    ing = []
    for ln in lines(r.get("ingredients")):
        s = ln.strip()
        if not s: ing.append("<li class='gap'></li>")
        elif s.endswith(":"): ing.append("<li class='head'>%s</li>" % esc(s))
        else: ing.append("<li>%s</li>" % esc(s))
    while ing and ing[0] == "<li class='gap'></li>": ing.pop(0)
    H.append("<table class='body'><tr>")
    if ing: H.append("<td class='ing'><div class='label'>Ingredients</div><ul>%s</ul></td>" % "".join(ing))
    H.append("<td class='dir'><div class='label'>Directions</div>%s</td></tr></table>" % (paras(r.get("directions")) or "<p>(none recorded)</p>"))
    if with_notes and (r.get("notes") or "").strip():
        H.append("<div class='further'><div class='label'>Further notes</div>%s</div>" % paras(r["notes"]))
    foot = "MacArthur family recipes"
    if (r.get("source_url") or "").strip().startswith("http"): foot += " &nbsp;·&nbsp; " + esc(r["source_url"].strip().split("?")[0])
    H.append("<div class='foot'>%s</div></body></html>" % foot)
    return "\n".join(H)

def to_pdf(src, dst):
    chrome = (glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome") + [shutil.which(x) for x in
              ("chromium", "chromium-browser", "google-chrome")])
    for c in [x for x in chrome if x]:
        p = subprocess.run([c, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                            "--print-to-pdf=" + dst, "file://" + os.path.abspath(src)], capture_output=True)
        if p.returncode == 0 and os.path.exists(dst): return "chromium"
    w = shutil.which("wkhtmltopdf")
    if w:
        p = subprocess.run([w, "--quiet", "--page-size", "Letter", src, dst], capture_output=True)
        if os.path.exists(dst): return "wkhtmltopdf"
    return None

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("recipe"); ap.add_argument("--notes", action="store_true"); ap.add_argument("--no-opt", action="store_true")
    a = ap.parse_args()
    r = one(load(), a.recipe)
    slug = re.sub(r"[^a-z0-9]+", "-", r["name"].lower()).strip("-")
    os.makedirs("build/cards", exist_ok=True)
    h = "build/cards/%s.html" % slug; p = "build/cards/%s.pdf" % slug
    open(h, "w", encoding="utf-8").write(render(r, a.notes, not a.no_opt))
    if os.path.exists(p): os.remove(p)
    how = to_pdf(h, p)
    print(("card: %s (%s)" % (p, how)) if how else "no PDF tool found - the card is at %s; print it from a browser" % h)

if __name__ == "__main__": main()
