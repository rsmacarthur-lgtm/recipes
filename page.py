#!/usr/bin/env python3
"""
Data for the phone recipe page (the "MacArthur Family Recipes" artifact).

    python3 page.py      -> build/page/recipes.json

The page itself is page/index.html, a small static file. It fetches
recipes.json, which is published beside it. Keep the data OUT of the page: a
republish from a new session has to read the page back first, and a page with
1.5 MB of recipes inside it would cost a few hundred thousand tokens to read.

Every text field is copied from the master verbatim.
"""
import json, re, os, collections, datetime
from recipe import load

def clean(s):
    return re.sub(r"\n{3,}", "\n\n", str(s or "").replace("\r\n", "\n").replace("\r", "\n").strip())

R = load(); seen = collections.Counter(); out = []
for r in R:                                   # same anchors as build2.py, so links match the docs
    name = re.sub(r"\s+", " ", clean(r.get("name")))
    b = re.sub(r"-{2,}", "-", re.sub(r"[^a-z0-9\s-]", "", name.lower()).strip().replace(" ", "-")) or "recipe"
    seen[b] += 1
    t = r.get("timing") or {}; o = r.get("claude_opt") or {}
    d = o.get("delta_min") or 0
    rec = {"id": b if seen[b] == 1 else "%s-%d" % (b, seen[b] - 1), "n": name,
           "c": ([x for x in (r.get("categories") or []) if x and x.strip()] or ["Uncategorized"])[0].strip(),
           "s": re.sub(r"\s+", " ", clean(r.get("source"))), "v": re.sub(r"\s+", " ", clean(r.get("servings"))),
           "u": clean(r.get("source_url")), "d": clean(r.get("description")), "i": clean(r.get("ingredients")),
           "m": clean(r.get("directions")), "x": clean(r.get("notes"))}
    if t.get("total"):
        rec["t"] = ("" if t.get("source") == "stated" else "about ") + t["total"]; rec["tm"] = t.get("total_min")
    if t.get("active"): rec["a"] = ("~" if t.get("active_est") else "") + t["active"]
    if t.get("ahead_label"): rec["h"] = t["ahead_label"]
    if o.get("changes"):
        rec["o"] = clean(o["changes"]); rec["ol"] = [x.strip() for x in (o.get("log") or [])]
        rec["od"] = "no change" if o.get("none") else "no added time" if d == 0 else ("saves %d min" % -d if d < 0 else "+%d min" % d)
    out.append({k: v for k, v in rec.items() if v not in ("", None, [])})

out.sort(key=lambda x: (x["c"].lower(), x["n"].lower()))
os.makedirs("build/page", exist_ok=True)
with open("build/page/recipes.json", "w", encoding="utf-8") as f:
    json.dump({"updated": datetime.date.today().strftime("%-d %B %Y"), "recipes": out}, f, ensure_ascii=False, separators=(",", ":"))
print("page data: %d recipes, %s bytes -> build/page/recipes.json" % (len(out), format(os.path.getsize("build/page/recipes.json"), ",")))
print("publish: Artifact file_path page/index.html, files {recipes.json: build/page/recipes.json, scale.js: page/scale.js}, url = the page's link in CLAUDE.md")
