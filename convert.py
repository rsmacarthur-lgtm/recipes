import json,re,collections
from density import CUP,TSP
R=json.load(open("recipes_merged.json"))
ATKRE=re.compile(r"america's test kitchen|americastestkitchen|cook's illustrated|cooks illustrated|cook's country|cookscountry|new best recipe|test kitchen",re.I)
BAKE={"Bread","Cookies","Desserts"}
FRAC={'¼':.25,'½':.5,'¾':.75,'⅓':1/3,'⅔':2/3,'⅛':.125,'⅜':.375,'⅝':.625,'⅞':.875}
UC={'cup':1,'cups':1,'c':1,'pint':2,'pints':2,'quart':4,'quarts':4,'qt':4,'gallon':16,'gallons':16}
UT={'teaspoon':1,'teaspoons':1,'tsp':1,'t':1,'tablespoon':3,'tablespoons':3,'tbsp':3,'tbs':3,'tb':3}
NUM=r'(?:\d+\s+\d+/\d+|\d+/\d+|\d*\.\d+|\d+\s*[¼½¾⅓⅔⅛⅜⅝⅞]|[¼½¾⅓⅔⅛⅜⅝⅞]|\d+)'
QTY=r'(?:(?P<lo>'+NUM+r')\s*(?:to|-|–|or)\s*)?(?P<qty>'+NUM+r')'
UNIT=r'(?P<unit>cups?|c\.|tablespoons?|tbsp?\.|tbsp|tbs|T\.|teaspoons?|tsp\.?|t\.|pints?|quarts?|qt\.|gallons?)'
VOLRE=re.compile(QTY+r'\s*'+UNIT+r'(?![a-z])',re.I)
WTRE=re.compile(r'(?:(?P<lo>'+NUM+r')\s*-?\s*(?:to|-|–|or)\s*)?(?P<qty>'+NUM+r')\s*-?\s*(?P<unit>ounces?|oz\.?|pounds?|lbs?\.?)(?![a-z])',re.I)
HASMET=re.compile(r'\b\d[\d.,]*\s*(g|grams?|ml|kg)\b',re.I)
STOP=r'\b(of|the|a|an|plus|more|for|or|and|to|into|finely|freshly|coarsely|very|good|large|small|medium|about|such|as|preferably|divided|packed|lightly|well|room|temperature|softened|melted|cold|warm|hot|fresh|dried|chopped|minced|sliced|grated|shredded|diced|crushed|ground|peeled|trimmed|rinsed|drained|optional|best|quality|extra)\b'
def q(s):
    s=s.strip()
    for ch,v in FRAC.items():
        if s.endswith(ch):
            b=s[:-1].strip(); return (float(b) if b else 0)+v
    if ' ' in s and '/' in s:
        a,b=s.split(None,1); n,d=b.split('/'); return float(a)+float(n)/float(d)
    if '/' in s: n,d=s.split('/'); return float(n)/float(d)
    return float(s)
def nu(u):
    raw=u.rstrip('.')
    # 'T' is tablespoon, 't' is teaspoon - case is the only thing distinguishing them
    if raw=='T': return ('tsp',3)
    if raw=='t': return ('tsp',1)
    u=raw.lower()
    if u in UC: return ('cup',UC[u])
    if u in UT: return ('tsp',UT[u])
    return (None,None)
LOSTSPACE=re.compile(r'(?<![\d/])(\d)(\d/\d)(?![\d/])')
def lost_space(ln):
    """'1 1/2 cups' transcribed without its space reads as 11/2 - eleven halves.
    Refuse to convert such a line; it has produced 1100 g of sugar once already."""
    return bool(LOSTSPACE.search(ln))

def deacc(x):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFKD",x) if not unicodedata.combining(c))
def look(rest,tbl,loose=False):
    r=deacc(rest.lower()); r=re.sub(r'\(.*?\)','',r); r=re.sub(r'[^a-z0-9\s-]',' ',r)
    if loose: r=re.sub(STOP,' ',r)
    w=[x for x in r.split() if x]
    for n in (4,3,2,1):
        for i in range(len(w)-n+1):
            k=" ".join(w[i:i+n])
            if k in tbl: return k,tbl[k]
    return None,None
def weight(x, hi=None):
    """Render a weight WE derived from an imperial or volume measure.

    Above a kilogram the gram figure is false precision - '5 pounds of onions'
    is not known to 2268 g - so switch to kg at one decimal. Source-stated gram
    weights are never touched: those sit outside the parentheses, and a baker's
    formula that says 1,000 g flour means exactly that.
    """
    def one(v):
        return f"{round(v)}" if v >= 10 else f"{round(v,1)}"
    top = hi if hi is not None else x
    if top >= 1000:
        lo_s = f"{round(x/1000,1):g}"
        if hi is None: return f"{lo_s} kg"
        return f"{lo_s}-{round(hi/1000,1):g} kg"
    if hi is None: return f"{one(x)} g"
    return f"{one(x)}-{one(hi)} g"

def in_paren(ln,pos):
    return ln.count('(',0,pos)>ln.count(')',0,pos)
def salt(ln):
    l=ln.lower()
    if 'morton' in l: return 4.8,"Morton kosher",False
    if 'diamond crystal' in l: return 2.8,"Diamond Crystal",False
    if 'kosher' in l: return 2.8,"kosher salt, taken as Diamond Crystal",True
    if 'flaky' in l or 'maldon' in l: return 2.5,"flaky",False
    if 'fine sea' in l or 'table salt' in l: return 6.0,"table salt",False
    if 'sea salt' in l: return 5.5,"sea salt",False
    return 6.0,"plain 'salt', taken as table salt",True
out={}; stats=collections.Counter(); unmatched=collections.Counter(); saltnotes={}
for r in R:
    cat=(r.get("categories") or ["Uncategorized"])[0]
    is_atk=bool(ATKRE.search(" ".join([r.get("source") or "",r.get("source_url") or "",r.get("notes") or ""])))
    ing=r.get("ingredients") or ""
    if not ing.strip(): continue
    is_bake = cat in BAKE or (re.search(r'\bflour\b',ing,re.I) and re.search(r'baking powder|baking soda|\byeast\b',ing,re.I))
    NL=[]; ch=False; sn=set()
    for ln in ing.split("\n"):
        if not ln.strip() or HASMET.search(ln): NL.append(ln); continue
        if lost_space(ln):
            NL.append(ln); stats["lost-space fraction, skipped"]+=1; continue
        m=VOLRE.search(ln)
        if m and not in_paren(ln,m.start()):
            try: qv=q(m.group('qty'))
            except Exception: NL.append(ln); stats["unparseable"]+=1; continue
            kind,mult=nu(m.group('unit'))
            if not kind: NL.append(ln); continue
            rest=ln[m.end():]; g=None
            if re.search(r'\bsalt\b',ln,re.I):
                per,desc,amb=salt(ln)
                g=qv*mult*per*(48 if kind=='cup' else 1)
                if amb and is_bake: sn.add(desc)
            elif kind=='cup':
                k,per=look(rest,CUP) ; k,per=(k,per) if per else look(rest,CUP,True)
                if per:
                    if k in ("all-purpose flour","flour","ap flour","unbleached flour","bread flour") and is_atk:
                        per=142; sn.add("ATK dip-and-sweep flour at 142 g/cup")
                    g=qv*mult*per
                else: unmatched[re.sub(r'\s+',' ',rest.strip().lower())[:38]]+=1
            else:
                k,per=look(rest,TSP); k,per=(k,per) if per else look(rest,TSP,True)
                if per: g=qv*mult*per
                else:
                    k,pc=look(rest,CUP); k,pc=(k,pc) if pc else look(rest,CUP,True)
                    if pc: g=qv*mult*pc/48
                    else: unmatched[re.sub(r'\s+',' ',rest.strip().lower())[:38]]+=1
            if g:
                lo=m.groupdict().get('lo')
                if lo:
                    try:
                        gl=g*q(lo)/qv
                        txt=f" ({weight(gl, g)})"
                    except Exception: txt=f" ({weight(g)})"
                else: txt=f" ({weight(g)})"
                NL.append(ln[:m.end()]+txt+ln[m.end():]); ch=True; stats["volume→g"]+=1; continue
            NL.append(ln); stats["no density"]+=1; continue
        w=WTRE.search(ln)
        if w and not in_paren(ln,w.start()):
            try: qv=q(w.group('qty'))
            except Exception: NL.append(ln); continue
            u=w.group('unit').lower().rstrip('.')
            f=453.6 if u.startswith('lb') or u.startswith('pound') else 28.35
            g=qv*f
            lo=w.groupdict().get('lo')
            if lo:
                try: txt=f" ({weight(q(lo)*f, g)})"
                except Exception: txt=f" ({weight(g)})"
            else: txt=f" ({weight(g)})"
            NL.append(ln[:w.end()]+txt+ln[w.end():]); ch=True; stats["oz/lb→g"]+=1; continue
        NL.append(ln); stats["untouched"]+=1
    if ch:
        out[r["name"]]="\n".join(NL)
        if sn: saltnotes[r["name"]]=sorted(sn)
print("STATS:",dict(stats))
print("recipes changed:",len(out),"| recipes needing a weights note:",len(saltnotes))
print()
print("UNMATCHED:",sum(unmatched.values()),"lines,",len(unmatched),"distinct")
for k,v in unmatched.most_common(15): print(f"   {v:3d}  {k}")
json.dump({"ingredients":out,"notes":saltnotes},open("convert_preview.json","w"),ensure_ascii=False)
print()
print("=== SAMPLES ===")
for nm in ["Original Plum Torte","Foolproof Pan Pizza","Overnight White Bread","Really Good Hummus"]:
    if nm in out:
        print(f"--- {nm}"); print("\n".join(out[nm].split("\n")[:9])); print()
