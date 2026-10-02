# -*- coding: utf-8 -*-
"""Fold the estimated hands-on times into the master.

    IMPORTANT: timeblock.py rebuilds the whole `timing` dict from scratch, which
    erases these estimates. Any run of timeblock.py MUST be followed by re-running
    this script over all three estimate files, in order, or every recipe loses its
    hands-on figure. (Learned the hard way.)

The estimates came from reading each recipe's steps and costing the work with a
fixed set of calibration anchors. They are used only where the recipe itself did
not say - a stated prep time always wins, because it is the author's own.
"""
import json, os, sys
from timeblock import field_split, fmt

R = json.load(open('recipes_merged.json'))
E = {int(k): v for k, v in json.load(open(os.path.expanduser(
        sys.argv[1] if len(sys.argv) > 1 else 'state/estimates/est_merged.json'))).items()}

applied = ho = tot = 0
for i, r in enumerate(R):
    e = E.get(i)
    if not e: continue
    t = r.setdefault('timing', {})
    ft, _ = field_split(r.get('total_time'))     # did the recipe state a TOTAL?
    fp, _ = field_split(r.get('prep_time'))      # did it state a PREP?

    # --- total ---
    est_total = int(e['total_min'])
    if ft:
        pass                                      # author's own total wins outright
    elif t.get('source') in ('stated', 'stated+steps'):
        # the fields gave cook time but no total, so prep was never counted
        if est_total > (t.get('total_min') or 0):
            t['total_min'] = est_total; t['total'] = fmt(est_total)
            t['source'] = 'field+est'; tot += 1
    else:
        t['total_min'] = est_total; t['total'] = fmt(est_total)
        t['source'] = 'est'; tot += 1

    # --- hands-on ---
    if os.environ.get('FORCE') or not fp:
        h = min(int(e['hands_on_min']), t.get('total_min') or int(e['hands_on_min']))
        if h >= 3:
            t['active_min'] = h; t['active'] = fmt(h)
            t['active_est'] = True
            t['est_confidence'] = e.get('confidence')
            ho += 1
    applied += 1

json.dump(R, open('recipes_merged.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'estimates applied to {applied} recipes | hands-on set {ho} | totals raised/filled {tot}')
have = sum(1 for r in R if (r.get('timing') or {}).get('total_min'))
hoall = sum(1 for r in R if (r.get('timing') or {}).get('active'))
print(f'now: {have}/{len(R)} have a total, {hoall}/{len(R)} have a hands-on figure')
