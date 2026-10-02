import json, os, sys, re

R = json.load(open("recipes.json"))
B = json.load(open(os.path.expanduser("~/mnt/Cooking/_merge_bundle_sep2026.json")))
idx = {}
for r in R:
    idx.setdefault(r["name"].strip().lower(), []).append(r)

log = {"job1":[], "merges":[], "adds":[], "job3":[], "errors":[]}

def find(name):
    hits = idx.get(name.strip().lower(), [])
    if len(hits) == 1: return hits[0]
    if len(hits) > 1:
        log["errors"].append(f"AMBIGUOUS master name '{name}' ({len(hits)} entries)"); return hits[0]
    log["errors"].append(f"MASTER ENTRY NOT FOUND: '{name}' — note NOT merged"); return None

def append_note(rec, text, label):
    cur = (rec.get("description") or "").strip()
    rec["description"] = (cur + "\n\n" + text.strip()).strip() if cur else text.strip()
    log[label].append({"recipe": rec["name"], "added_chars": len(text.strip()),
                       "had_existing_note": bool(cur)})

# ---------------- JOB 1: supplied annotations ----------------------------
JOB1 = {
"Apple Pie":
"""RM 2026: Four persistent defects, none yet solved — (1) bottom crust underbaked, (2) apples shrink leaving a gap under the top crust, (3) filling runs when sliced, (4) crimped edge burns or slumps.
RM 11/16 (from James, Thanksgiving): par-cooking the bottom crust does NOT fix the soggy bottom — tried and failed. Pre-cooking the apples Kenji-style was good and is the live candidate for the shrinkage gap.
RM note: open to ingredient changes, not just technique, provided it still reads as Mom's pie.""",

"Foolproof Pan Pizza":
"""RM 3/13: ~5 oz cheese per pizza is ideal. Microwave pepperoni briefly before it goes on. Use Kenji's sauce recipe rather than a substitute. Baked in Lodge 10.25" and 12" skillets simultaneously, one dough batch split between them. Made regularly with the kids.""",

"Hawaiian Chicken Salad":
"""RM 2026: Cut the oil in the dressing and add a little mayonnaise. Quantities not yet pinned down — set them on the next make.""",

"No-Knead Bread":
"""RM 2/13: I find that it takes less overall cooking time than he suggests.
RM 4/20: The overnight white bread version is the one now used, not the original 2013 formula.""",

"Red Lentil Soup with Lemon":
"""RM 1/24: Laura's read — may be too involved for a weeknight. Fallback that night was sausages and mashed potatoes.""",

"Beef Kabobs--California":
"""RM 2026: Robert's family rotation includes "Mom's chicken kebabs (California kebabs)," almost certainly a chicken variant of this recipe. The master entry notes it is "also great with chicken." Worth confirming whether these are one recipe or two.""",
}
for name, note in JOB1.items():
    rec = find(name)
    if rec: append_note(rec, note, "job1")

# Hawaiian vinegar verification
h = find("Hawaiian Chicken Salad")
log["hawaiian_vinegar_present"] = bool(h and re.search(r"white wine vinegar", h.get("ingredients") or "", re.I))

# ---------------- JOB 4: merges -----------------------------------------
for v in B["verdicts"]:
    if v["verdict"] != "MERGE": continue
    if not v.get("note_found") or not (v.get("cooks_note") or "").strip():
        log["merges"].append({"recipe": v.get("master_match"), "added_chars": 0,
                              "had_existing_note": None, "noop": True}); continue
    rec = find(v["master_match"])
    if rec: append_note(rec, v["cooks_note"], "merges")

# ---------------- JOB 2 + JOB 4 adds ------------------------------------
def add(d, origin_note):
    nm = d["name"].strip()
    if nm.strip().lower() in idx:
        log["errors"].append(f"ADD collides with existing master name: '{nm}' — added anyway, review")
    rec = {
        "name": nm,
        "categories": [d["category"]] if d.get("category") and d["category"] != "Uncategorized" else [],
        "source": d.get("source") or "",
        "source_url": d.get("source_url") or "",
        "servings": d.get("servings") or "",
        "prep_time": d.get("prep_time") or "",
        "cook_time": d.get("cook_time") or "",
        "total_time": d.get("total_time") or "",
        "ingredients": d.get("ingredients") or "",
        "directions": d.get("directions") or "",
        "description": (d.get("cooks_note") or "").strip(),
        "notes": origin_note,
        "created": "2026-09-18 12:00:00",
        "_origin": "RM",
    }
    R.append(rec); idx.setdefault(nm.lower(), []).append(rec)
    log["adds"].append({"recipe": nm, "category": d.get("category"), "has_note": bool(rec["description"])})

for h_ in B["harvest"]:
    prov = "Merged from Robert's Gmail archive, Sept 2026. " + (h_.get("provenance") or "")
    if h_.get("editorial_note"): prov += " " + h_["editorial_note"]
    add(h_, prov.strip())

for v in B["verdicts"]:
    if v["verdict"] != "ADD": continue
    rc = v.get("recipe") or {}
    rc = dict(rc); rc["cooks_note"] = v.get("cooks_note") or ""
    if not rc.get("name"): rc["name"] = v.get("gmail_name") or v["slug"]
    prov = ("Merged from Robert's Gmail archive, Sept 2026. Kept separate from master entry "
            f"\"{v.get('master_match')}\": {v.get('reasoning','')} " if v.get("master_match")
            else "Merged from Robert's Gmail archive, Sept 2026. ") + (v.get("provenance") or "")
    add(rc, prov.strip())

# ---------------- JOB 3: entries that exist in no archive ---------------
R.append({
 "name": "Filet Mignon — Carryover Temperature Log",
 "categories": ["Dinner"], "source": "Robert MacArthur", "source_url": "",
 "servings": "", "prep_time": "", "cook_time": "", "total_time": "",
 "ingredients": "",
 "directions": """Not a recipe. A running log calibrating pull temperature against carryover.

Data point 1: 1.5" filet, 450F pan set next to the grill, pulled at 110F, rested to 143F. Carryover +33F. Overcooked.

Reading: that carryover is far larger than normal. The cause is the resting position — the steak kept absorbing radiant heat from the grill, on top of the steep gradient a very hot pan creates.

Adjustments to test: resting on a wire rack away from heat, pull at 118-120F. Resting in the same hot environment, pull at 100-105F. Probe from the side into the geometric center, not down through the top.

Columns for future entries: thickness · pan temp · pull temp · rest location and surface · rest time · final temp.

Open question: whether the steak rested on the pan itself, and for how long, was not recorded.""",
 "description": "RM 2026: Started because a 110F pull came off at 143F. One data point so far.",
 "notes": "Created Sept 2026 from Claude conversations; exists in no email archive.",
 "created": "2026-09-18 12:00:00", "_origin": "RM"})
log["job3"].append("Filet Mignon — Carryover Temperature Log")

gs = next((v for v in B["verdicts"] if v["slug"] == "grilled-shrimp"), None)
gsr = (gs or {}).get("recipe") or {}
R.append({
 "name": "Robert's Grilled Shrimp",
 "categories": ["Dinner"], "source": gsr.get("source") or "", "source_url": gsr.get("source_url") or "",
 "servings": gsr.get("servings") or "", "prep_time": gsr.get("prep_time") or "",
 "cook_time": gsr.get("cook_time") or "", "total_time": gsr.get("total_time") or "",
 "ingredients": gsr.get("ingredients") or "",
 "directions": (gsr.get("directions") or "") + """

--- 2026 REVISION — UNTESTED AS OF SEPTEMBER 2026 ---

The version above puts lemon juice in the marinade. Acid cures the surface, so at the two-hour end of the window the exterior goes chalky instead of snapping. Revised approach:

Dry brine first: salt plus 1/4 tsp baking soda, 20-30 minutes in the fridge. Firmer texture, faster browning in the three minutes available.

Marinate in oil and spices only, 30 minutes. Lemon zest into the oil; juice squeezed over after cooking, never before.

Warm the oil with the oregano, paprika and garlic powder for 30 seconds first — they are fat-soluble and otherwise sit there raw. Smoked paprika is an upgrade.

Cook loose on the Weber Slate, no skewers. Skewers exist only to stop shrimp falling through grates.

60-90 seconds a side. Loose C-shape, not a tight O. About 120F on the instant-read.

Buy U/15 or 16/20 rather than "large", dry-packed rather than phosphate-soaked.

Finish: reserve a spoonful of the seasoned oil, stir in fresh garlic, lemon juice and parsley, toss the hot shrimp off the heat.""",
 "description": ((gs or {}).get("cooks_note") or "").strip(),
 "notes": ("Recipe body merged from Robert's Gmail archive (emailed to Laura, June 2025). "
           "The 2026 revision below the rule is untested as of September 2026 and came from Claude "
           "conversations, not from any archive. " + ((gs or {}).get("provenance") or "")).strip(),
 "created": "2026-09-18 12:00:00", "_origin": "RM"})
log["job3"].append("Robert's Grilled Shrimp (original + untested 2026 revision)")

json.dump(R, open("recipes_merged.json","w"), ensure_ascii=False)
json.dump(log, open("merge_log.json","w"), ensure_ascii=False, indent=1)
print("total recipes now:", len(R))
print("job1 merged:", len(log["job1"]), "| job4 merges:", len([m for m in log['merges'] if not m.get('noop')]),
      "| adds:", len(log["adds"]), "| job3:", len(log["job3"]))
print("hawaiian vinegar already present in master:", log["hawaiian_vinegar_present"])
print("ERRORS:", log["errors"] if log["errors"] else "none")
