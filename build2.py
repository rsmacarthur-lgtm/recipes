import json, re, os, collections
R = json.load(open("recipes_merged.json"))
CUT = "2022-12-07 20:58:59"
OUT = "build"; os.makedirs(OUT, exist_ok=True)

def clean(s, inline=False):
    if not s: return ""
    s = str(s).replace("\r\n","\n").replace("\r","\n").strip()
    s = re.sub(r"\n{3,}", "\n\n", s)
    return re.sub(r"\s+"," ",s) if inline else s

tok = re.compile(r'(?<![\d/])(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?(?![\d/])')
def note_dates(t):
    o=[]
    for m in tok.finditer(t):
        M=int(m.group(1)); c=m.group(3)
        if c: y=int(c); y=2000+y if y<100 else y
        else:
            y=int(m.group(2))
            if not (20<=y<=26): continue
            y+=2000
        if 1<=M<=12 and 2015<=y<=2027: o.append((y,M))
    return o

for r in R:
    r["_note"]=clean(r.get("description"))
    r["_rm"]= r.get("_origin")=="RM"
    r["_new"]= (not r["_rm"]) and r["created"]>CUT
    # NOTE-UPDATED means Alan and Steph extended their own note since Dec 2022,
    # so Robert's RM-prefixed lines are excluded from the date scan.
    _as_note = "\n".join(l for l in r["_note"].split("\n") if not l.strip().startswith("RM "))
    d=note_dates(_as_note) if _as_note.strip() else []
    r["_upd"]= (not r["_rm"]) and bool(d) and max(d)>(2022,12) and not r["_new"]
    r["_rmnote"]= bool(re.search(r'^RM ', r["_note"], re.M))

DINNER_CATS={"Dinner","Soup","Vegetables","Salads"}
ANCHOR=18*60+30      # 6:30 pm, the family's dinner time; change this one number to re-anchor

def clock(minutes_before):
    t=ANCHOR-int(round(minutes_before))
    while t<0: t+=24*60
    h,m=divmod(t,60); ap="am" if h<12 else "pm"; h12=h%12 or 12
    return f"{h12}:{m:02d} {ap}"

def timeline(r, category):
    """One line at the top of a recipe: how long it takes, how much of that you
    have to stand there for, and whether something must happen the day before.

    Deliberately not here: unattended time (it is the total minus hands-on) and
    any clock time (that would mean assuming when dinner is)."""
    t=r.get("timing") or {}
    if not t.get("total") and not t.get("ahead_label"): return []
    bits=[]
    if t.get("total"):
        # plain number = the recipe's own; 'about' = worked out from the steps
        approx="" if t.get("source")=="stated" else "about "
        head=f"**{approx}{t['total']}**"
        if t.get("active"):
            tilde="~" if t.get("active_est") else ""
            head+=f", {tilde}{t['active']} hands-on"
        bits.append(head)
    if t.get("ahead_label"): bits.append(f"start ahead: {t['ahead_label']}")
    return ["  ·  ".join(bits)]

def optblock(r):
    """Claude's suggested changes. Never edits the original method - it sits
    beside it, with the time it costs or saves stated every time."""
    o=r.get("claude_opt")
    if not o: return []
    d=o.get("delta_min") or 0
    if o.get("none"):   tag="no change"
    elif d==0:          tag="no added time"
    elif d<0:           tag=f"saves {abs(d)} min"
    else:               tag=f"+{d} min"
    out=["",f"**Claude's changes**  ·  *{tag}*  ", clean(o["changes"],True)]
    for ln in (o.get("log") or []):
        out.append(f"> {ln.strip()}")
    return out

def cat(r):
    c=[x for x in (r.get("categories") or []) if x and x.strip()]
    return c[0].strip() if c else "Uncategorized"

seen=collections.Counter()
for r in R:
    b=re.sub(r"[^a-z0-9\s-]","",clean(r.get("name"),True).lower()).strip().replace(" ","-")
    b=re.sub(r"-{2,}","-",b) or "recipe"
    seen[b]+=1
    r["_anchor"]= b if seen[b]==1 else f"{b}-{seen[b]-1}"

bycat=collections.defaultdict(list)
for r in R: bycat[cat(r)].append(r)
for c in bycat: bycat[c].sort(key=lambda r: clean(r.get("name"),True).lower())
cats=sorted(bycat, key=lambda c:(c=="Uncategorized", c.lower()))

new=sorted([r for r in R if r["_new"]], key=lambda r:r["created"])
upd=sorted([r for r in R if r["_upd"]], key=lambda r:r["_note"])
rm =sorted([r for r in R if r["_rm"]], key=lambda r: clean(r.get("name"),True).lower())
rmnotes=[r for r in R if r["_rmnote"]]
noted=[r for r in R if r["_note"]]

L=[];A=L.append
A("# The MacArthur Family Recipes\n")
A(f"{len(R)} recipes. The core of this collection is Alan and Steph MacArthur's, exported from Paprika in September 2026. "
  f"In September 2026 a second archive of Robert's — kept in Gmail rather than Paprika — was merged in, adding {len(rm)} recipes "
  f"and folding his annotations into {len(rmnotes)-sum(1 for r in rm if r['_rmnote'])} recipes that were already here.\n")
A("A **Cook's note** is what whoever made the dish wrote down afterwards, usually dated. "
  f"{len(noted)} of these {len(R)} recipes carry one. Notes beginning **RM** are Robert's; everything else is Alan and Steph's.\n")
A("---\n")
A("## From Robert's archive (new in September 2026)\n")
A(f"**{len(rm)} recipes** merged in from Robert's Gmail archive.\n")
for r in rm:
    A(f"- [{clean(r.get('name'),True)}](#{r['_anchor']})" + ("  ·  *has a cook's note*" if r["_note"] else ""))
A("")
A(f"**{len([r for r in rmnotes if not r['_rm']])} recipes already in the collection gained one of Robert's notes.**\n")
for r in rmnotes:
    if not r["_rm"]: A(f"- [{clean(r.get('name'),True)}](#{r['_anchor']})")
A("")
A("---\n")
A("## New since the December 2022 collection\n")
A(f"**{len(new)} recipes** were added to Alan and Steph's collection after 7 December 2022.\n")
for r in new:
    A(f"- [{clean(r.get('name'),True)}](#{r['_anchor']}) — added {r['created'][:10]}" + ("  ·  *has a cook's note*" if r["_note"] else ""))
A("")
A(f"**{len(upd)} older recipes picked up a cook's note dated after December 2022.**\n")
for r in upd: A(f"- [{clean(r.get('name'),True)}](#{r['_anchor']})")
A("")
A("---\n")
A("## Contents\n")
for c in cats:
    A(f"- [{c}](#{re.sub(r'[^a-z0-9s-]','',c.lower()).replace(' ','-')}) — {len(bycat[c])} recipes")
A("")
A("---\n")

for c in cats:
    A(f"\n# {c}\n")
    for r in bycat[c]:
        A(f'<a id="{r["_anchor"]}"></a>')
        A(f"\n## {clean(r.get('name'),True)}\n")
        meta=[]
        if clean(r.get("source"),True):   meta.append(f"**Source:** {clean(r.get('source'),True)}")
        if clean(r.get("servings"),True): meta.append(f"**Serves:** {clean(r.get('servings'),True)}")
        if r["_rm"]: meta.append("**From Robert's archive**")
        elif r["_new"]: meta.append("**New since 2022**")
        elif r["_upd"]: meta.append("**Note updated since 2022**")
        if meta: A("  ·  ".join(meta)+"  ")
        for ln in timeline(r,c): A(ln+"  ")
        A("")
        if r["_note"]:
            A("> **Cook's note**  ")
            for ln in r["_note"].split("\n"):
                A(f"> {ln.strip()}  " if ln.strip() else ">")
            A("")
        if clean(r.get("notes")):
            A("**Further notes**\n"); A(clean(r.get("notes"))+"\n")
        for ln in optblock(r): A(ln)
        if r.get("claude_opt"): A("")
        if clean(r.get("ingredients")):
            A("**Ingredients**\n")
            for ln in clean(r.get("ingredients")).split("\n"):
                ln=ln.strip(); A(f"- {ln}" if ln else "")
            A("")
        if clean(r.get("directions")):
            A("**Directions**\n"); A(clean(r.get("directions"))+"\n")
        if clean(r.get("source_url"),True):
            A(f"[Original recipe]({clean(r.get('source_url'),True)})\n")
        A("---\n")

md=os.path.join(OUT,"MacArthur Recipes Sep 26 - library.md")
open(md,"w",encoding="utf-8").write("\n".join(L))
print("library:", f"{os.path.getsize(md):,} bytes")

# ---- roster ----
STOP=set("cup cups tablespoon tablespoons teaspoon teaspoons pound pounds ounce ounces oz lb lbs gram grams kg ml large small medium fresh freshly ground chopped minced sliced diced taste plus more for and the etc optional divided into inch inches can cans package jar salt pepper kosher water".split())
rows=sorted(R,key=lambda r:(cat(r)=="Uncategorized",cat(r).lower(),clean(r.get("name"),True).lower()))
R2=["# Recipe roster — all %d, one line each"%len(R),"",
"Complete inventory in compact form: every recipe name, category, servings, total time, provenance flags, whether it carries a cook's note, and main ingredients as keywords.","",
"Flags: **RM** = merged from Robert's Gmail archive in Sept 2026 · **NEW** = added to Alan and Steph's collection after Dec 2022 · **NOTE-UPDATED** = older recipe whose note was extended since Dec 2022.","",
"Use this doc for questions needing the whole collection at once — counting, filtering, ranking, \"what can I make in under 30 minutes\", \"which ones use anchovies\". For a single recipe's full text use the category docs.","",
"Total time is the recipe's own where it gave one; **about** means it was worked out from the steps. An **ahead:** note means something must happen before the day you cook — that waiting is not in the total.","",
"Format: **Name** — category · serves · total time · flags · ingredient keywords","","---"]
cur=None
for r in rows:
    c=cat(r)
    if c!=cur: R2+=["",f"## {c}",""]; cur=c
    tm=r.get("timing") or {}
    total=tm.get("total") or "-"
    raw=re.sub(r"[0-9¼½¾⅓⅔⅛/().,;:–—\-]+"," ",str(r.get("ingredients") or "").lower())
    w=[]
    for x in raw.split():
        if x in STOP or len(x)<3: continue
        if x not in w: w.append(x)
    f=["RM"] if r["_rm"] else (["NEW"] if r["_new"] else (["NOTE-UPDATED"] if r["_upd"] else []))
    bits=[c, clean(r.get("servings"),True) or "-", ("" if tm.get("source")=="stated" else "about ")+total]+f+([f"ahead: {tm['ahead_label']}"] if tm.get("ahead_label") else [])+(["has cook's note"] if r["_note"] else [])
    R2.append(f"- **{clean(r.get('name'),True)}** — {' · '.join(bits)} · {' '.join(w[:18])}")
ro=os.path.join(OUT,"MacArthur Recipes Sep 26 - roster.md")
open(ro,"w",encoding="utf-8").write("\n".join(R2))
print("roster:", f"{os.path.getsize(ro):,} bytes")

# ---- xlsx ----
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
wb=Workbook(); ws=wb.active; ws.title="Recipe Index"
ws.append(["Recipe","Category","Source","Serves","Total time","Cook's note","Ingredients","Link","Origin","New since 2022","Note updated"])
for r in rows:
    tm=r.get("timing") or {}
    total=tm.get("total") or ""
    ing="; ".join(l.strip() for l in clean(r.get("ingredients")).split("\n") if l.strip())[:900]
    url=clean(r.get("source_url"),True)
    ws.append([clean(r.get("name"),True),cat(r),clean(r.get("source"),True),clean(r.get("servings"),True),
               total,tm.get("total_min") or "", tm.get("ahead_label") or "",
               clean(r.get("_note"),True)[:1000],ing,url,
               "Robert" if r["_rm"] else "Alan & Steph","NEW" if r["_new"] else "","UPDATED" if r["_upd"] else ""])
    if url.startswith("http"):
        c=ws.cell(row=ws.max_row,column=10); c.hyperlink=url; c.value="link"
ws.freeze_panes="A2"; ws.auto_filter.ref=ws.dimensions
for cell in ws[1]:
    cell.font=Font(name="Arial",size=10,bold=True,color="FFFFFF")
    cell.fill=PatternFill("solid",fgColor="33582F")
    cell.alignment=Alignment(vertical="center",horizontal="left")
for row in ws.iter_rows(min_row=2):
    for cell in row:
        cell.font=Font(name="Arial",size=10)
        cell.alignment=Alignment(vertical="top",wrap_text=cell.column in (7,8,9))
    row[0].font=Font(name="Arial",size=10,bold=True)
    if row[9].value: row[9].font=Font(name="Arial",size=10,color="0563C1",underline="single")
    if row[10].value=="Robert": row[10].font=Font(name="Arial",size=10,bold=True,color="7A3E9D")
    if row[11].value: row[11].font=Font(name="Arial",size=10,bold=True,color="1F7A1F")
    if row[12].value: row[12].font=Font(name="Arial",size=10,bold=True,color="B36B00")
for i,w_ in enumerate([44,14,24,14,16,9,22,62,64,8,13,13,13],start=1):
    ws.column_dimensions[get_column_letter(i)].width=w_
ws.row_dimensions[1].height=22
xl=os.path.join(OUT,"MacArthur Recipes Sep 26 - index.xlsx")
wb.save(xl)
print("xlsx:", f"{os.path.getsize(xl):,} bytes")
print("totals -> recipes",len(R),"| RM",len(rm),"| with note",len(noted),"| RM-tagged notes",len(rmnotes))
