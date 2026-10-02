# -*- coding: utf-8 -*-
"""Fold a pass of Claude optimizations into the master.

Each recipe gets a `claude_opt` block: the changes, the time they cost or save,
how confident the pass was, and a log that Robert's own trial notes append to.
The original ingredients and directions are never touched.
"""
import json, os, sys

R = json.load(open('recipes_merged.json'))
src = os.path.expanduser(sys.argv[1] if len(sys.argv) > 1
                         else 'state/optimizations/opt_p1.json')
E = {int(k): v for k, v in json.load(open(src)).items()}

applied = skipped = 0
for i, r in enumerate(R):
    e = E.get(i)
    if not e: continue
    txt = (e.get('changes') or '').strip()
    if not txt: skipped += 1; continue
    none = 'nothing worth changing' in txt.lower()
    prev = (r.get('claude_opt') or {}).get('log') or []   # never lose Robert's trial notes
    r['claude_opt'] = {
        'changes': txt,
        'delta_min': int(e.get('delta_min') or 0),
        'confidence': e.get('confidence'),
        'kind': e.get('kind'),
        'none': none,
        'pass': os.path.basename(src),
        'log': prev,
    }
    applied += 1

json.dump(R, open('recipes_merged.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
tot = sum(1 for r in R if r.get('claude_opt'))
nun = sum(1 for r in R if (r.get('claude_opt') or {}).get('none'))
print(f'applied {applied} (skipped {skipped}) | collection now has {tot} optimization notes, '
      f'{nun} of them "nothing worth changing"')
