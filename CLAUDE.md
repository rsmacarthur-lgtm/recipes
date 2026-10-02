# The MacArthur recipe collection

This repo is the master copy of the family recipe collection. It moved here from
Google Drive on 2 October 2026 so that any session - phone included - can change
a recipe without a computer being on. Nothing else is a master: the Cooking
project docs, and any library/roster/spreadsheet files in Drive, are built from
`recipes_merged.json` and are overwritten on the next build.

Work from the repo root. Commit and push every change to `main`; git history is
the backup, so there are no `pre-*.json` copies any more.

## The loop

    python3 recipe.py find <words>         # which recipe
    python3 recipe.py show "<name>"        # read it (cheap - do this, not project_read)
    python3 recipe.py note|replace|set|opt|optlog|time|category|origin ...   # change it
    python3 add_recipe.py new.json         # or add one (see the macarthur-recipes skill)
    python3 card.py "<name>"               # printable PDF, cook's notes folded in

Every change rebuilds `build/` and prints which project docs are NEW / CHANGED /
GONE against `published.json`. Then:

1. `Projects project_write` each NEW/CHANGED doc with `local_path`
   `build/docs/<name>` to project path `recipes/<name>`; `project_delete` each GONE.
2. `python3 publish_prep.py --mark`
3. Refresh the phone page: `python3 page.py`, then Artifact publish with
   `url` https://claude.ai/artifact/ARwkTugsPV1RqGrtng8zmQ, `file_path`
   `page/index.html` and `files` `{"recipes.json": "build/page/recipes.json"}`.
   A new session must `read` that artifact once before it may publish to it; the
   page is small on purpose, the recipes travel in recipes.json.
4. `git add -A && git commit && git push`

`published.json` is what the project holds. It moves only on `--mark`, so run
`--mark` only after the writes succeeded, and commit it with the change.

`python3 recipe.py stats` gives current counts. Do not quote counts from memory
or from HISTORY.md.

The phone page is what Robert cooks from: search, cook's notes first, ingredients
to tick off. It is private to him unless he shares it from the page's Share menu.
It shows whatever was in the master at the last step 3, so skipping step 3 leaves
the page behind the project docs.

## Rules the scripts enforce

- `description` is the family's COOK'S NOTE. Append only. `recipe.py note` is the
  only way in; `set` and `replace` refuse the field. A correction is a new dated
  line that says what it replaces. Robert's lines are `RM m/yy: ...` (month/year,
  the family's own convention - "9/26" is September 2026).
- `notes` is everything generated and may be rewritten. `claude_opt.changes` is
  the optimization note; `claude_opt.log` holds Robert's trial notes.
- Changing `ingredients`, `directions` or `name` needs `--why`, filed in `notes`
  as a dated "Data fix" line.
- `replace` needs the old text to occur exactly once. A swap that does not match
  fails; it never silently does nothing.
- `add_recipe.py` needs `origin` (whose recipe: "Robert", "Laura", "Alan & Steph").
  `"RM"` means the September 2026 Gmail-archive merge only and needs `--archive`.

## Rules the scripts cannot enforce

- An ingredient line is carried VERBATIM wherever it is shown: original measure
  and gram weight both, and no quantity invented for a line that has none. For a
  printed card use `card.py`; never retype a recipe into a card or a reply.
- Never `project_read` a category doc or the roster to check it. It returns the
  whole document into context, about 25,000 tokens each. `build/docs/` holds the
  same text; `recipe.py show` holds one recipe.
- Never run `timeblock.py` on the whole master to time one recipe: it rebuilds
  every `timing` block and wipes the hands-on estimates. If it must be run:

      python3 merge_est.py state/estimates/est_merged.json
      FORCE=1 python3 merge_est.py state/estimates/est_p2.json
      FORCE=1 python3 merge_est.py state/estimates/est_p3.json

- After any bulk gram conversion, sweep for outliers: implied g-per-cup above 350
  or below 25, and any derived weight over 1500 g that is not a roast or a sack
  of flour. "1 1/2 cups" with its space lost reads as 11/2; `convert.py` refuses
  such lines.
- When a publisher is blocked (SITE_BLOCKED), record the link and move on. No
  curl, cache, mirror or archive. Robert pastes the text himself.

## What is here

    recipes_merged.json   the master, one JSON list, pretty-printed for readable diffs
    recipe.py             look up / edit one recipe        card.py   print card
    add_recipe.py         add one recipe, end to end       convert.py + density.py   grams
    build2.py             master -> build/ library, roster, spreadsheet
    publish_prep.py       build/ -> build/docs/ and the changed list; --mark
    published.json        hashes of the docs the project currently holds
    timeblock.py merge_est.py merge_opt.py   bulk passes (see the warning above)
    state/                estimate and optimization passes, page digests, URL worklist
    archive/              one-off scripts from the September 2026 merge; not part of the loop
    page/index.html       the phone page ("MacArthur Family Recipes" artifact); page.py builds its data
    HISTORY.md            the log up to 2 Oct 2026, written when this lived in Drive

## Open items

- Stubs that need entering from a real source: Beer Can Chicken (no ingredients or
  method), Corn Muffin Recipe - Ina (fragments of a search page), Cucumber Spread
  (no quantities or method), Lobster - Steamed (no ingredients).
- Low-confidence links worth a human look: Hot Artichoke Dip, Plain Pastry for
  Pie Crust.
- Not yet built: a weeknight shortlist of sub-hour mains George will eat, and
  green vegetable sides.
- Project doc `recipes/00-roster-all-441.md` is only a redirect page with stale
  counts. Remove it once the project instructions point at
  `recipes/00-roster-complete.md` (only Robert can edit the instructions). The two
  September report docs were removed on 2 Oct 2026; copies are in
  `archive/project-docs/`.
- The Drive folder `My Drive/Cooking` still holds the Paprika export and the old
  working files as an archive. Its library/roster/spreadsheet are frozen at
  2 Oct 2026 unless someone copies `build/` output there.
