#!/usr/bin/env python3
"""
Look up and change ONE existing recipe in recipes_merged.json. Adding a new
recipe is add_recipe.py's job; this is for everything after that.

    python3 recipe.py find chicken cutlet          names containing every word
    python3 recipe.py show "apple pie"             the stored record, for reading

    python3 recipe.py note "apple pie" "Blind-baked the bottom 15 min. Fixed it."
        Appends "RM 10/26: ..." to the COOK'S NOTE. Month/year, the family's own
        convention. --date 11/26 overrides; --who AS for Alan and Steph's lines
        (no prefix). This is the only way to touch the cook's note, and it can
        only add.

    python3 recipe.py replace "apple pie" directions "400 degrees" "425 degrees" --why "..."
        Exact-text swap inside one field. The old text must occur exactly once,
        so a swap that does not match fails loudly instead of doing nothing.

    python3 recipe.py set "apple pie" directions --file new.txt --why "..."
        Replace a whole field (or give the text inline instead of --file).

    python3 recipe.py opt "apple pie" "Cook the filling down first." --delta 15
    python3 recipe.py optlog "apple pie" "RM 10/3/26: tried it, no gap this time."
    python3 recipe.py time "apple pie" --total 75 --hands-on 20
    python3 recipe.py category "apple pie" Desserts
    python3 recipe.py origin "apple pie" "Alan & Steph"
    python3 recipe.py stats                        current counts, computed not remembered

Rules this script enforces so nobody has to remember them:
  * `description` is the family's cook's note. APPEND ONLY - `set` and `replace`
    refuse it. A correction is a new dated line saying what it replaces.
  * `set`/`replace` on ingredients or directions need --why, which is filed in
    `notes` as a dated "Data fix" line. The exact old wording is in git history.
  * --grams re-runs convert.py and applies it to this recipe only (use after
    adding or changing an ingredient line that has a volume and no weight).
  * Every change rebuilds the library and reports which project docs differ from
    what is published. --no-build skips that when several edits are coming.
"""
import json, sys, os, re, subprocess, datetime, argparse

MASTER = "recipes_merged.json"
EDITABLE = {"ingredients", "directions", "notes", "source", "source_url", "servings",
            "prep_time", "cook_time", "total_time", "name"}
NEEDS_WHY = {"ingredients", "directions", "name"}
CATS = {"Appetizers","Basics","Bread","Breakfast","Cookies","Desserts","Dinner","Dressings",
        "Drinks","Non-food","Preserves","Salads","Sauces & Condiments","Soup","Vegetables"}

def load(): return json.load(open(MASTER, encoding="utf-8"))
def save(R):
    with open(MASTER, "w", encoding="utf-8") as f:
        json.dump(R, f, ensure_ascii=False, indent=1); f.write("\n")

def find(R, q):
    """Exact name first, then every word as a substring. Never guesses."""
    ql = q.strip().lower()
    exact = [r for r in R if r["name"].strip().lower() == ql]
    if exact: return exact
    words = ql.split()
    return [r for r in R if all(w in r["name"].lower() for w in words)]

def one(R, q):
    hits = find(R, q)
    if len(hits) == 1: return hits[0]
    if not hits: sys.exit("no recipe matches %r - try: python3 recipe.py find <a word>" % q)
    sys.exit("%r matches %d recipes - use the full name:\n  %s" % (q, len(hits), "\n  ".join(r["name"] for r in hits)))

def today(): return datetime.date.today()
def month_year(d=None):
    d = d or today(); return "%d/%s" % (d.month, str(d.year)[2:])

def datafix(r, why):
    line = "Data fix (%s), at Robert's request: %s" % (today().strftime("%b %Y"), why.strip())
    r["notes"] = ((r.get("notes") or "").rstrip() + "\n\n" + line).strip()

def apply_grams(R, r):
    save(R)   # convert.py reads the master from disk, so the edit has to be there first
    subprocess.run([sys.executable, "convert.py"], check=True, capture_output=True)
    P = json.load(open("convert_preview.json", encoding="utf-8"))
    if r["name"] not in P["ingredients"]:
        print("grams: nothing to convert"); return
    before = r["ingredients"]; r["ingredients"] = P["ingredients"][r["name"]]
    b = set(before.splitlines())
    for ln in r["ingredients"].splitlines():
        if ln not in b: print("grams:", ln.strip())
    for cav in (P["notes"].get(r["name"]) or []):
        if cav.strip() and cav.strip() not in (r.get("notes") or ""):
            r["notes"] = ((r.get("notes") or "") + "\n\n" + cav).strip(); print("weights caveat filed:", cav[:80])

def show(r):
    t = r.get("timing") or {}; o = r.get("claude_opt") or {}
    print("# %s   [%s]" % (r["name"], ", ".join(r.get("categories") or [])))
    for k in ("source", "source_url", "servings"):
        if r.get(k): print("%s: %s" % (k, r[k]))
    print("origin: %s | time: %s%s%s" % (r.get("_origin") or "Alan & Steph", t.get("total") or "-",
          ", %s hands-on" % t["active"] if t.get("active") else "",
          " | start ahead: " + t["ahead_label"] if t.get("ahead_label") else ""))
    for label, k in (("COOK'S NOTE (description - append only)", "description"), ("INGREDIENTS", "ingredients"),
                     ("DIRECTIONS", "directions"), ("NOTES (generated)", "notes")):
        print("\n-- %s --\n%s" % (label, (r.get(k) or "(none)").replace("\r\n", "\n")))
    if o:
        print("\n-- CLAUDE'S CHANGES (delta %+d min) --\n%s" % (o.get("delta_min") or 0, o.get("changes")))
        for ln in o.get("log") or []: print("  log:", ln)

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["find", "show", "stats", "note", "replace", "set", "opt", "optlog", "time", "category", "origin"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--why"); ap.add_argument("--file"); ap.add_argument("--date"); ap.add_argument("--who", default="RM")
    ap.add_argument("--delta", type=int); ap.add_argument("--total", type=int); ap.add_argument("--hands-on", type=int, dest="hands_on")
    ap.add_argument("--grams", action="store_true"); ap.add_argument("--no-build", action="store_true")
    a = ap.parse_args(); R = load()

    if a.cmd == "find":
        for r in find(R, " ".join(a.args)): print("%-12s %s" % ((r.get("categories") or ["?"])[0], r["name"]))
        return
    if a.cmd == "stats":
        n = len(R); c = lambda f: sum(1 for r in R if f(r))
        print("recipes                 ", n)
        print("with a cook's note      ", c(lambda r: (r.get("description") or "").strip()))
        print("with an RM line         ", c(lambda r: re.search(r"^RM ", r.get("description") or "", re.M)))
        print("from Robert's archive   ", c(lambda r: r.get("_origin") == "RM"))
        print("with a source URL       ", c(lambda r: (r.get("source_url") or "").strip()))
        print("optimization notes      ", c(lambda r: r.get("claude_opt")))
        print(" of which 'no change'   ", c(lambda r: (r.get("claude_opt") or {}).get("none")))
        print("with a hands-on time    ", c(lambda r: (r.get("timing") or {}).get("active")))
        print("no ingredients or method", ", ".join(r["name"] for r in R if not (r.get("ingredients") or "").strip() or not (r.get("directions") or "").strip()))
        return
    if not a.args: sys.exit("which recipe?")
    r = one(R, a.args[0]); rest = a.args[1:]
    if a.cmd == "show": show(r); return

    if a.cmd == "note":
        if not rest or not rest[0].strip(): sys.exit("note text is missing")
        text = " ".join(rest[0].split())
        line = text if a.who.upper() == "AS" else "%s %s: %s" % (a.who, a.date or month_year(), text)
        old = r.get("description") or ""
        r["description"] = (old.rstrip() + "\n" + line) if old.strip() else line
        assert r["description"].startswith(old.rstrip()), "append-only violated"
        print("cook's note +=", line)

    elif a.cmd in ("replace", "set"):
        if not rest: sys.exit("which field? one of: " + ", ".join(sorted(EDITABLE)))
        field = rest[0]
        if field == "description":
            sys.exit("the cook's note is append-only - use: python3 recipe.py note %r \"...\"" % r["name"])
        if field not in EDITABLE: sys.exit("field must be one of: " + ", ".join(sorted(EDITABLE)))
        if field in NEEDS_WHY and not (a.why or "").strip():
            sys.exit("--why is required for %s: one line saying what changed and why (it is filed in notes)" % field)
        cur = r.get(field) or ""
        if a.cmd == "replace":
            if len(rest) != 3: sys.exit('usage: replace "<recipe>" <field> "<old text>" "<new text>"')
            old, new = rest[1], rest[2]; n = cur.count(old)
            if n != 1: sys.exit("old text occurs %d times in %s (must be exactly 1) - nothing changed.\ncurrent:\n%s" % (n, field, cur))
            r[field] = cur.replace(old, new)
        else:
            new = open(a.file, encoding="utf-8").read().strip() if a.file else (rest[1] if len(rest) > 1 else None)
            if new is None: sys.exit("give the new text inline or with --file")
            if field == "name" and any(x is not r and x["name"].strip().lower() == new.strip().lower() for x in R):
                sys.exit("another recipe is already called %r" % new)
            r[field] = new
        if a.why and field != "notes": datafix(r, a.why)
        print("%s changed" % field)
        if a.grams and field == "ingredients": apply_grams(R, r)

    elif a.cmd == "category":
        if not rest or rest[0] not in CATS: sys.exit("category must be one of: " + ", ".join(sorted(CATS)))
        r["categories"] = [rest[0]]; print("category ->", rest[0])

    elif a.cmd == "origin":
        if not rest or not rest[0].strip(): sys.exit('whose recipe? e.g. "Robert", "Laura"; "RM" = the Sept 2026 Gmail archive')
        r["_origin"] = rest[0].strip(); print("origin ->", r["_origin"])

    elif a.cmd == "opt":
        if not rest or not rest[0].strip(): sys.exit("the note text is missing")
        if a.delta is None: sys.exit("--delta is required: minutes added (+) or saved (-), 0 for none")
        o = r.get("claude_opt") or {"log": []}
        o.update({"changes": rest[0].strip(), "delta_min": a.delta,
                  "none": "nothing worth changing" in rest[0].lower(), "pass": "edit %s" % today().isoformat()})
        o.setdefault("log", []); r["claude_opt"] = o; print("optimization note rewritten")

    elif a.cmd == "optlog":
        if not rest: sys.exit("the log line is missing")
        r.setdefault("claude_opt", {"changes": "", "delta_min": 0, "log": []}).setdefault("log", []).append(rest[0].strip())
        print("trial note logged")

    elif a.cmd == "time":
        from timeblock import fmt
        t = r.setdefault("timing", {})
        if a.total is not None: t["total_min"] = a.total; t["total"] = fmt(a.total); t["source"] = "est"
        if a.hands_on is not None: t["active_min"] = a.hands_on; t["active"] = fmt(a.hands_on); t["active_est"] = True
        print("timing ->", t.get("total"), "/", t.get("active"))

    save(R)
    if a.no_build: print("saved (not rebuilt)"); return
    subprocess.run([sys.executable, "build2.py"], check=True, capture_output=True)
    print(subprocess.run([sys.executable, "publish_prep.py"], check=True, capture_output=True, text=True).stdout)

if __name__ == "__main__": main()
