# -*- coding: utf-8 -*-
"""Derive a timing block for each recipe.

Two independent estimates, kept separate on purpose:
  fields  - what the recipe's own prep/cook/total fields say (only 232 of 476 have any)
  prose   - durations parsed out of the directions text

Same-day time and start-ahead time are NEVER added together: a dough that rises
overnight is a scheduling fact, not part of the elapsed cooking time. It gets
its own line.
"""
import json, re, unicodedata

FRAC = {'¼':.25,'½':.5,'¾':.75,'⅓':1/3,'⅔':2/3,
        '⅛':.125,'⅜':.375,'⅝':.625,'⅞':.875}
UNIT = {'second':1/60,'sec':1/60,'minute':1,'min':1,'mins':1,'hour':60,'hr':60,
        'hrs':60,'day':1440,'week':10080}

def num(s):
    s = s.strip()
    for f, v in FRAC.items():
        if f in s:
            w = s.replace(f, '').strip()
            return (float(w) if w else 0) + v
    m = re.fullmatch(r'(\d+)\s+(\d+)/(\d+)', s)
    if m: return int(m.group(1)) + int(m.group(2))/int(m.group(3))
    m = re.fullmatch(r'(\d+)/(\d+)', s)
    if m: return int(m.group(1))/int(m.group(2))
    try: return float(s)
    except ValueError: return None

N = r'(?:\d+\s+\d+/\d+|\d+/\d+|\d+\.\d+|\d+\s*[¼½¾⅓⅔⅛⅜⅝⅞]|[¼½¾⅓⅔⅛⅜⅝⅞]|\d+)'
DUR = re.compile(
    r'(?P<lo>' + N + r')\s*(?:to|-|–|or)\s*(?P<hi>' + N + r')\s*(?P<u2>seconds?|secs?|minutes?|mins?|hours?|hrs?|days?|weeks?)\b'
    r'|(?P<q>' + N + r')\s*(?P<u>seconds?|secs?|minutes?|mins?|hours?|hrs?|days?|weeks?)\b', re.I)

def unit(u):
    u = u.lower().rstrip('s')
    return UNIT.get(u) or UNIT.get(u + 's') or UNIT.get(u.rstrip('s'))

COMPACT = re.compile(r'(\d+)\s*h\s*(\d{2})\b|(\d+)\s*h\b(?!\w)', re.I)
WORDNUM = {'one':1,'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,'eight':8,
           'nine':9,'ten':10,'eleven':11,'twelve':12,'fifteen':15,'twenty':20,'thirty':30,
           'forty':40,'forty-five':45,'sixty':60,'half an':0.5,'a half':0.5,'an':1,'a':1}
WORDRE = re.compile(r'\b(' + '|'.join(sorted(WORDNUM, key=len, reverse=True)) +
                    r')\s+(seconds?|secs?|minutes?|mins?|hours?|hrs?|days?|weeks?)\b', re.I)

def normalize(t):
    """'2h15' / '2 h 15' / '3h' -> spelled out, so the duration regex sees them"""
    def rep(m):
        if m.group(1): return f"{m.group(1)} hours {m.group(2)} minutes"
        return f"{m.group(3)} hours"
    t = COMPACT.sub(rep, t)
    # 'Three hours total', 'an hour', 'half an hour'
    t = WORDRE.sub(lambda m: f"{WORDNUM[m.group(1).lower()]} {m.group(2)}", t)
    return t

def parse_field(s):
    """'1 hr 30 min' / '1 1/2 hours' / 'about 45 minutes' -> minutes"""
    if not s: return None
    s = normalize(str(s).lower())
    tot = 0.0; hit = False
    for m in DUR.finditer(s):
        if m.group('q') is not None:
            v, u = num(m.group('q')), unit(m.group('u'))
        else:
            v, u = num(m.group('hi')), unit(m.group('u2'))
        if v is None or u is None: continue
        tot += v * u; hit = True
    return round(tot) if hit else None

# --- directions parsing -------------------------------------------------
WAIT = re.compile(r'\b(bak|roast|simmer|braise|chill|refrigerat|freez|rest|rise|ferment'
                  r'|proof|prove|cool|marinat|brin|soak|steep|slow.?cook|smoke|grill|broil'
                  r'|boil|steam|stand|sit|poach|dry|cure|set aside|let it|let the|until)\w*', re.I)
AHEAD_W = re.compile(r'\b(overnight|over ?night|night before|day before|days? ahead|day ahead|ahead of time)\b', re.I)
OPTIONAL = re.compile(r'\b(up to|if desired|optional|or longer|as long as|at least .{0,12}but|preferably|for best results|if you (?:like|prefer|have)|can be)\b', re.I)
STORAGE = re.compile(r'\b(store|stores|storage|keep|keeps|kept|leftover|will last|lasts|airtight|reheat|serve immediately, or|freezes well)\b', re.I)
# a long duration is "ahead" when you are waiting on it, and "cooking" when heat is on
WAITLONG = re.compile(r'\b(ris|ferment|proof|prove|chill|refrigerat|freez|marinat|brin|soak|rest|thaw|cure|dry|steep|macerat|sit|stand|overnight|starter)\w*', re.I)
COOKLONG = re.compile(r'\b(roast|bake|braise|simmer|smoke|sous ?vide|slow.?cook|stew|boil|poach|cook)\w*', re.I)
PREHEAT = re.compile(r'\b(preheat|pre-?heat|heat the oven|oven to)\b', re.I)

# A phrase that says you *may* do something early is convenience, not a requirement.
OPTAHEAD = re.compile(r'\b(can be made|can be prepared|may be prepared|can be stored|can be refrigerated'
                      r'|can, however|do ahead|plan ahead|if you like|for best results|can prepare|could be made'
                      r'|if freezing|overnight .{0,10}option|option:)\b', re.I)
PURE_STORAGE = re.compile(r'\b(stored|store|stay fresh|keeps|will last|leftover|freezes well|up to \d+ (?:weeks?|months?))\b', re.I)

def tidy(p):
    p = re.sub(r'\s+', ' ', p).strip().strip('(').strip()
    p = re.sub(r'^[-*\u2013]\s*', '', p)
    if len(p) > 105:
        p = p[:105].rsplit(' ', 1)[0] + '\u2026'
    return p

STRONG = re.compile(r'\b(overnight|night before|day before|days? ahead|days? before|at least \d|minimum of|\d+ *(?:to *\d+ *)?(?:hours?|hrs?|days?))\b', re.I)

def score(p):
    """Prefer the phrase that actually states the requirement over an incidental mention."""
    v = 0
    if STRONG.search(p): v += 2
    if re.match(r'^(the )?(night|day)s? (before|ahead)|^start this|^\d+ days? ahead|^at least', p, re.I): v += 2
    if re.match(r'^(if not|gently|once the|when ready)', p, re.I): v -= 2
    return -v

def bucket(phrases):
    req, opt, seen = [], [], set()
    raw = {}
    full = {tidy(x): re.sub(r'\s+', ' ', x).strip() for x in phrases}
    for p in sorted(full, key=score):
        k = p.lower()[:40]
        if not p or k in seen: continue
        if p.endswith(':') and len(p) < 28: continue   # bare step headers ('Two days ahead:')
        seen.add(k)
        if OPTAHEAD.search(p) or re.match(r'^if not', p, re.I) or (re.search(r'\bup to\b', p, re.I) and not STRONG.search(p)):
            opt.append(p)
        elif PURE_STORAGE.search(p) and not re.search(r'\b(night before|day before|days? ahead|overnight|at least)\b', p, re.I): continue
        else:
            req.append(p); raw[p] = full[p]
    return req, opt, raw

ACTIONS = [
    (r'\b(dry.?brin|brin(e|ing))\w*', 'brine'),
    (r'\bmarinat\w*', 'marinade'),
    (r'\b(ris(e|ing)|ferment|proof|prove|levain|starter|biga|sponge|bulk)\w*', 'rise'),
    (r'\bsoak\w*', 'soak'),
    (r'\bthaw\w*', 'thaw'),
    (r'\b(cur(e|ing)|air.?dry|dry uncovered)\w*', 'cure'),
    (r'\b(salt(ed|ing)? (?:the |all over|generously|under))', 'salt'),
    (r'\b(chill|refrigerat|cool|set(s)? up|freez)\w*', 'chill'),
]
SCALE = [
    (r'\b(\d+)\s*(?:to|-|\u2013)\s*(\d+)\s*days?\b', lambda m: f"{m.group(1)}-{m.group(2)} days"),
    (r'\bat least (\d+)\s*days?\b',                     lambda m: f"{m.group(1)} days"),
    (r'\b(\d+)\s*days?\s*(?:ahead|before)\b',           lambda m: f"{m.group(1)} days"),
    (r'\b(night before|the night before)\b',              lambda m: "the night before"),
    (r'\bovernight\b',                                    lambda m: "overnight"),
    (r'\bat least (\d+)\s*(?:hours?|hrs?)\b',            lambda m: f"{m.group(1)} h+"),
    (r'\b(\d+)\s*(?:to|-|\u2013)\s*(\d+)\s*(?:hours?|hrs?)\b', lambda m: f"{m.group(1)}-{m.group(2)} h"),
    (r'\b(\d+)\s*(?:hours?|hrs?)\b',                     lambda m: f"{m.group(1)} h"),
    (r'\b(\d+)\s*(?:minutes?|mins?)\b',                  lambda m: f"{m.group(1)} min"),
]

def label(phrases):
    """Turn a quoted sentence into a few words: 'overnight rise', '2 days brine'.

    The full phrase stays in the record; only this short form is printed, because
    the cook only needs to know that something has to happen early and roughly what."""
    blob = ' '.join(phrases)
    scale = None
    for pat, f in SCALE:
        m = re.search(pat, blob, re.I)
        if m: scale = f(m); break
    act = None
    for pat, name in ACTIONS:
        if re.search(pat, blob, re.I): act = name; break
    if scale: scale = re.sub(r'^1 days', '1 day', scale)
    if scale and act:  return f"{scale} {act}"
    if scale:          return scale
    if act:            return act
    p = tidy(phrases[0])
    return p if len(p) <= 45 else p[:45].rsplit(' ', 1)[0] + '\u2026'

def fmt(mins):
    mins = float(mins)
    if mins >= 720: mins = round(mins/30)*30      # half-hour precision past 12 h
    elif mins >= 240: mins = round(mins/15)*15    # quarter-hour past 4 h
    elif mins >= 90: mins = round(mins/5)*5
    mins = int(round(mins))
    if mins < 60: return f"{mins} min"
    h, m = divmod(mins, 60)
    if h >= 24:
        d, h = divmod(h, 24)
        return f"{d} day" + ("s" if d > 1 else "") + (f" {h} h" if h else "")
    return f"{h} h" + (f" {m} min" if m else "")

def scan(directions):
    """-> (same_day_minutes, active, unattended, [ahead descriptions])"""
    if not directions: return (0, 0, 0, [])
    txt = normalize(unicodedata.normalize('NFKC', directions))
    sents = re.split(r'(?<=[.!?])\s+|\n+', txt)
    active = unattended = 0.0
    ahead = []
    for s in sents:
        if not s.strip(): continue
        if STORAGE.search(s): continue
        opt = bool(OPTIONAL.search(s))
        if AHEAD_W.search(s) and not STORAGE.search(s):
            ahead.append(s.strip())
            continue
        best = 0.0; best_is_ahead = False
        for m in DUR.finditer(s):
            if m.group('q') is not None:
                v, u = num(m.group('q')), unit(m.group('u'))
            else:
                v, u = num(m.group('hi')), unit(m.group('u2'))
            if v is None or u is None: continue
            v = v * u
            if v >= 240:                      # 4 h+ is a scheduling fact, not elapsed cook time
                best_is_ahead = True
                continue
            if PREHEAT.search(s): continue    # preheating overlaps prep
            if opt: continue
            if v > best: best = v             # within one sentence take the longest, don't sum
        if best_is_ahead:
            ahead.append(s.strip())
        if best:
            if WAIT.search(s): unattended += best
            else: active += best
    return (active + unattended, active, unattended, ahead)

def field_split(raw):
    """-> (same_day_minutes_or_None, ahead_text_or_None)

    Several recipes use prep_time/cook_time as a scheduling note rather than a
    duration: '2 days ahead', 'refrigerate at least 8 hours', '12-14 hr bulk +
    about 1 1/4 hr proof'. Those belong on the start-ahead line, not in elapsed time."""
    if not raw or not str(raw).strip(): return (None, None)
    txt = str(raw).strip()
    v = parse_field(txt)
    if v is None: return (None, None)
    if AHEAD_W.search(txt) or (v >= 240 and WAITLONG.search(txt) and not COOKLONG.search(txt)):
        return (None, txt)
    return (v, None)

def timing(r):
    ft, aht = field_split(r.get('total_time'))
    fp, ahp = field_split(r.get('prep_time'))
    fc, ahc = field_split(r.get('cook_time'))
    field_ahead = [x for x in (aht, ahp, ahc) if x]
    ptot, pact, pun, ahead = scan(r.get('directions'))
    ahead = field_ahead + ahead
    fields = ft or ((fp or 0) + (fc or 0)) or None
    out = {}
    if fields and ft:
        src = 'stated'; total = fields
    elif fields and ptot and ptot > fields * 1.25:
        src = 'stated+steps'; total = ptot
    elif fields:
        src = 'stated'; total = fields
    elif ptot:
        src = 'steps'; total = ptot
    else:
        src = None; total = None
    if total:
        out['total_min'] = int(round(total))
        out['total'] = fmt(total)
        out['source'] = src
        act = fp if (fp and src == 'stated') else (round(pact) if pact else None)
        un = fc if (fc and src == 'stated' and not ft) else (round(pun) if pun else None)
        # a 1-minute 'hands-on' figure is noise, not information
        def useful(v): return v and v >= 5 and v <= total * 0.9
        if useful(act): out['active_min'] = int(act); out['active'] = fmt(act)
        if useful(un):  out['unattended_min'] = int(un); out['unattended'] = fmt(un)
    req, opt, raw = bucket(ahead)
    if req:
        out['ahead'] = req[:2]
        out['ahead_label'] = label([raw.get(p, p) for p in req])
    if opt: out['makeahead'] = opt[:1]
    return out

if __name__ == '__main__':
    R = json.load(open('recipes_merged.json'))
    n = {'stated':0,'stated+steps':0,'steps':0,None:0}
    ah = 0
    for r in R:
        t = timing(r)
        r['timing'] = t
        n[t.get('source')] += 1
        ah += bool(t.get('ahead'))
    print('source counts:', n)
    print('required start-ahead:', ah, '| optional make-ahead:', sum(1 for r in R if r['timing'].get('makeahead')))
    json.dump(R, open('recipes_merged.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
    print('written back into recipes_merged.json')
