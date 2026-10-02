#!/usr/bin/env python3
"""
Add one recipe to the MacArthur collection, in the house format, end to end.

    python3 add_recipe.py new.json --check   # duplicate check only, changes nothing
    python3 add_recipe.py new.json           # do it

new.json needs {"name", "ingredients", "directions"} and should have "category".
Optional: source, source_url, servings, prep_time, cook_time, total_time,
description (the COOK'S NOTE - the family's own words), notes.
"origin" is REQUIRED: whose recipe it is ("Robert", "Laura", "Alan & Steph").

"ingredients" and "directions" may be given either as the master's newline-joined
string or as a list of lines; a list is joined here - ingredients one per line,
directions with a blank line between steps. Anything else is refused. Every one
of the 477 records stores both as a string, so an unjoined list put straight
into the master breaks convert.py and build2.py downstream.

Optional, and supplied by Claude rather than typed by hand:
    "hands_on_min": 25,              estimated hands-on minutes
    "same_day_total_min": 95,        estimated elapsed time, excluding overnight steps
    "claude_opt": {"changes": "...", "delta_min": 0,
                   "confidence": "high", "kind": "technique"}

The optimization note's text key is "changes". An unrecognised key inside
claude_opt is refused rather than ignored: a note filed under the wrong key used
to vanish without a word and the recipe shipped as the only one without one.

What this does, in order:
  1. normalises to the collection schema
  2. refuses if it looks like a duplicate of something already here
  3. converts volumes to grams (house rules) and files any salt caveat in `notes`
  4. computes the timing block FOR THIS RECIPE ONLY
  5. applies the hands-on estimate and the optimization note if given
  6. rebuilds the library, roster and spreadsheet

WHY IT ONLY TIMES THE NEW RECIPE: timeblock.py rebuilds `timing` for all 476
from scratch, which erases the hands-on estimates that took three passes to
produce. Never run it to add one recipe. This script calls timing() directly on
the new record instead.
"""
import json, sys, os, re, shutil, subprocess

CATS = {"Appetizers","Basics","Bread","Breakfast","Cookies","Desserts","Dinner","Dressings",
        "Drinks","Non-food","Preserves","Salads","Sauces & Condiments","Soup","Vegetables"}
MASTER = "recipes_merged.json"
OPT_KEYS = {"changes", "delta_min", "confidence", "kind", "log"}

def as_text(v, field, sep):
    """The master stores ingredients and directions as newline-joined strings.
    Accept that, or a list of lines, and refuse anything else."""
    if v is None: return ""
    if isinstance(v, str): return v
    if isinstance(v, (list, tuple)):
        for x in v:
            if not isinstance(x, str):
                sys.exit("%s: every item must be a string, found %r" % (field, x))
        return sep.join(x.strip() for x in v if x.strip())
    sys.exit("%s must be a string or a list of strings, not %s" % (field, type(v).__name__))

def check_opt(opt):
    """Refuse a malformed claude_opt loudly. The old code read opt['changes']
    and silently filed nothing when the key was spelled otherwise."""
    if opt is None: return None
    if not isinstance(opt, dict): sys.exit("claude_opt must be an object, not %s" % type(opt).__name__)
    unknown = sorted(set(opt) - OPT_KEYS)
    if unknown:
        hint = "\n  the note's text goes in \"changes\"" if {"note","text","summary"} & set(unknown) else ""
        sys.exit("claude_opt: unrecognised key(s) %s%s\n  valid keys: %s"
                 % (", ".join(repr(k) for k in unknown), hint, ", ".join(sorted(OPT_KEYS))))
    if not (opt.get("changes") or "").strip():
        sys.exit("claude_opt has no \"changes\" text - write the note, or leave claude_opt out entirely")
    return opt

def fingerprint(r):
    return frozenset(re.findall(r'[a-z]{4,}', (r.get("ingredients") or "").lower()))

def dupe_check(new, R):
    hits = []
    nf = fingerprint(new); nn = new["name"].strip().lower()
    for r in R:
        if r["name"].strip().lower() == nn:
            hits.append(("same name", 1.0, r["name"])); continue
        rf = fingerprint(r)
        if not (nf and rf): continue
        j = len(nf & rf) / len(nf | rf)
        if j >= 0.72: hits.append(("ingredients %.0f%% alike" % (j*100), j, r["name"]))
    return sorted(hits, key=lambda x: -x[1])

def main():
    if len(sys.argv) < 2: sys.exit(__doc__)
    src = json.load(open(sys.argv[1], encoding="utf-8"))
    check_only = "--check" in sys.argv
    check_opt(src.get("claude_opt"))
    if not src.get("name") or not src.get("ingredients"):
        sys.exit("need at least a name and ingredients")
    R = json.load(open(MASTER, encoding="utf-8"))

    # Whose recipe this is. Required: it used to default to "RM", which tagged a
    # recipe Robert found on the web as "From Robert's archive" (the Sept 2026 Gmail
    # merge). "RM" is reserved for that merge and needs --archive to use.
    origin = (src.get("origin") or "").strip()
    if not origin:
        sys.exit('origin is required: whose recipe is this? e.g. "Robert", "Laura", "Alan & Steph"')
    if origin == "RM" and "--archive" not in sys.argv:
        sys.exit('origin "RM" means the Sept 2026 Gmail-archive merge. Use "Robert" for something he added since, '
                 'or pass --archive if this really is from that archive.')

    cat = (src.get("category") or "").strip()
    if cat and cat not in CATS:
        sys.exit("category %r is not one of: %s" % (cat, ", ".join(sorted(CATS))))

    new = {
      "name": src["name"].strip(),
      "categories": [cat] if cat else [],
      "source": src.get("source","") or "",
      "source_url": src.get("source_url","") or "",
      "servings": src.get("servings","") or "",
      "prep_time": src.get("prep_time","") or "",
      "cook_time": src.get("cook_time","") or "",
      "total_time": src.get("total_time","") or "",
      "ingredients": as_text(src.get("ingredients"), "ingredients", "\n"),
      "directions": as_text(src.get("directions"), "directions", "\n\n"),
      "description": src.get("description","") or "",   # cook's note - append only, forever
      "notes": src.get("notes","") or "",
      "created": src.get("created") or __import__("datetime").date.today().isoformat()+" 12:00:00",
      "_origin": origin,
    }

    hits = dupe_check(new, R)
    if hits:
        print("STOP - this looks like something already in the collection:")
        for why,_,nm in hits[:6]: print("   %-28s %s" % (why, nm))
        print("\nIf it really is the same recipe, merge into the existing entry instead of")
        print("adding a second copy - the collection had 12 of these and they took work to unpick.")
        if not check_only: sys.exit(1)
        return
    print("[1/6] no duplicate found")
    if check_only: return
    if not cat:
        sys.exit("refusing to add without a category - pick one of: " + ", ".join(sorted(CATS)))

    R.append(new)
    json.dump(R, open(MASTER,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
    print("[2/6] added %r (%d recipes now); git is the backup" % (new["name"], len(R)))

    # --- grams -------------------------------------------------------------
    subprocess.run([sys.executable, "convert.py"], check=True, capture_output=True)
    P = json.load(open("convert_preview.json"))
    R = json.load(open(MASTER, encoding="utf-8"))
    rec = [r for r in R if r["name"] == new["name"]][0]
    if new["name"] in P["ingredients"]:
        rec["ingredients"] = P["ingredients"][new["name"]]
        n = len(re.findall(r'\(\s*[\d.,\-]+\s*g\s*\)', rec["ingredients"]))
        print("[3/6] converted %d ingredient lines to grams" % n)
        for cav in (P["notes"].get(new["name"]) or []):
            if cav.strip() and cav.strip() not in (rec.get("notes") or ""):
                rec["notes"] = ((rec.get("notes") or "") + "\n\n" + cav).strip()
            print("      weights caveat filed:", cav[:80])
    else:
        print("[3/6] nothing to convert")

    # --- timing, this recipe only -----------------------------------------
    from timeblock import timing
    rec["timing"] = timing(rec)
    t = rec["timing"]
    print("[4/6] timing: %s%s%s" % (t.get("total","(none)"),
          ", "+t["active"]+" hands-on" if t.get("active") else "",
          ", start ahead: "+t["ahead_label"] if t.get("ahead_label") else ""))

    # --- Claude's estimates and optimization note --------------------------
    from timeblock import fmt, field_split
    ho = src.get("hands_on_min"); sd = src.get("same_day_total_min")
    if sd and (not t.get("total_min") or sd > t["total_min"]) and not field_split(rec.get("total_time"))[0]:
        t["total_min"] = int(sd); t["total"] = fmt(sd); t["source"] = "est"
    if ho:
        ho = min(int(ho), t.get("total_min") or int(ho))
        if ho >= 3:
            t["active_min"] = ho; t["active"] = fmt(ho); t["active_est"] = True
    opt = check_opt(src.get("claude_opt"))
    if opt:
        rec["claude_opt"] = {"changes": opt["changes"].strip(),
                             "delta_min": int(opt.get("delta_min") or 0),
                             "confidence": opt.get("confidence"), "kind": opt.get("kind"),
                             "none": "nothing worth changing" in opt["changes"].lower(),
                             "pass": "on intake", "log": opt.get("log") or []}
    print("[5/6] estimates %s | optimization note %s" % (
          "applied" if (ho or sd) else "NOT SUPPLIED", "applied" if rec.get("claude_opt") else "NOT SUPPLIED"))

    json.dump(R, open(MASTER,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
    subprocess.run([sys.executable, "build2.py"], check=True, capture_output=True)
    print("[6/6] library, roster and spreadsheet rebuilt")

    missing = [x for x,y in [("category",cat),("hands-on estimate",ho),
                             ("optimization note",rec.get("claude_opt"))] if not y]
    if missing: print("\nSTILL MISSING (judgement calls - see the skill): " + ", ".join(missing))
    print("\nnext: python3 publish_prep.py, project_write the changed docs, then publish_prep.py --mark")

if __name__ == "__main__": main()
