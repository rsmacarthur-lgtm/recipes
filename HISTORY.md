> **Historical log, frozen 2 October 2026.** Written while the master lived in
> `My Drive/Cooking/_claude-state/`. Paths, the Downloads staging folder, the
> `pre-*.json` backups and the manifest warnings below describe that setup, not
> this repo. Counts are as of the dates given - use `python3 recipe.py stats`.
> Current instructions are in CLAUDE.md.

# Cooking project — state of play, 25 September 2026

Everything in this folder is the project's working state. It syncs through Drive,
so either machine can pick up from here. Copy the scripts and the master into the
device VM's `$HOME/work` and work there:

    mkdir -p $HOME/work && cp $HOME/mnt/Cooking/_claude-state/*.py $HOME/mnt/Cooking/_claude-state/recipes_merged.json $HOME/work/

The Cooking folder must be connected to the session, and Downloads too — the
publish step writes through `Downloads/claude-transfer/`.

## Where the collection stands

479 recipes. No duplicate names, all categorised, all timed, all carrying an
optimization note. 198 have a family cook's note.

| what                              | count |
|-----------------------------------|-------|
| recipes                           | 479   |
| with a cook's note                | 198   |
| merged from Robert's Gmail archive| 46    |
| ingredient lines carrying grams   | 3,002 of 4,122 quantities (73%) |
| with a source URL                 | 311   |
| with a web/comment digest         | 311   |
| optimization notes                | 479   |
| of which "nothing worth changing" | 104   |
| flagged for food safety           | 19    |
| hands-on estimates                | 466   |

Every figure above was recomputed from `recipes_merged.json` on 21 September.
The gram count runs about 8 higher than the 19 September figure because this
sweep matches any `g`/`kg` figure on a quantity line, not only the parenthesised
derived ones (2,737 of those).

## The scripts, in the order they run

    add_recipe.py     one recipe, end to end: dedupe, grams, timing, estimates,
                      optimization note, rebuild. THE ONLY WAY to add a recipe.
    convert.py        gram conversion (idempotent; refuses lost-space fractions)
    density.py        the density tables
    timeblock.py      rebuilds ALL timing — see the warning below
    merge_est.py      re-applies the hands-on estimates after timeblock.py
    merge_opt.py      folds an optimization pass into the master
    build2.py         regenerates library.md, roster.md and index.xlsx
    publish_prep.py   splits into project docs, reports what changed
    datafix.py        the September data repairs (already applied; kept as a record)

## The things that will bite you

**`timeblock.py` rebuilds every recipe's `timing` from scratch** and erases the
hands-on estimates. It happened once. If you run it, immediately run all three
estimate files in order:

    python3 merge_est.py _claude-state/estimates/est_merged.json
    FORCE=1 python3 merge_est.py _claude-state/estimates/est_p2.json
    FORCE=1 python3 merge_est.py _claude-state/estimates/est_p3.json

To add a single recipe, don't run timeblock.py at all — `add_recipe.py` times
only the new record.

**`publish_prep.py` only knows what it last saw.** It compares against its own
manifest and updates it as it runs, so if someone runs it, publishes, then
edits the master again and publishes without re-running it, the manifest is
stale and the next run over-reports. That is exactly what happened between
19 and 21 September: it listed all seven dinner docs as changed when only three
docs had actually moved. Re-run it immediately before publishing, and if the
list looks larger than the edit, rebuild the previous state from a backup and
hash the docs both ways before writing 600 KB of unchanged text to the project.

**The master is now compact JSON.** `add_recipe.py` rewrites it without indent,
so it went from pretty-printed to one line on 21 September. Content is
unaffected — every one of the 476 prior records was verified identical after
parsing — but diffs are useless until someone re-pretty-prints it.

**Lost-space fractions.** "1 1/2 cups" transcribed without its space reads as
`11/2`. `convert.py` refuses such lines; the current master has none.

**Sweep for outliers after any conversion run.** Recompute implied g-per-cup and
look at anything above 350 or below 25, and at any derived weight over 1500 g
that isn't a roast or a sack of flour. The current master has none.

**Google Drive hardlinks files**, which breaks `device_stage_files`. Stage
through `C:\Users\Robert\Downloads\claude-transfer`, which is outside Drive.

## Backups kept here

`recipes_merged.pre-*.json` are point-in-time copies from before each major pass
(grams, dedupe, timing, estimates, optimization, the data fixes), plus
`pre-add` from before the most recent single-recipe add and `pre-urlfix` from
before the source-URL cleanup below. `estimates/` holds the
three hands-on estimate files; `optimizations/` holds the three optimization
passes and the second round of pasted-in page digests.

## Settled since 19 September

- **The source-URL count.** The previous version of this file reported 324 with
  a source URL; the real figure has been 320 (at 488 records), then 313 after
  the dedupe pass, and 310 once the three non-URL values below were cleared.
  324 appears in no backup. Nothing was lost. The dedupe
  removed 14 duplicate records, 6 of which carried a URL that no longer appears
  anywhere — and in all six the surviving record kept an equal or better link:
  the wildyeastblog panettone URL survives verbatim minus its tracking
  parameter, and the other five moved from an aggregator or a section page to
  the publisher's own recipe page. No action needed.
- **Three `source_url` values were not URLs**, so `build2.py` was rendering them
  as broken `[Original recipe](PierreFraney)` links in the library and the
  project docs. In all three the field held attribution text, twice swapped with
  or duplicating `source`: `PierreFraney` (Chicken Breasts with Lemon, whose
  `source` held the site instead — now `Pierre Franey, cooking.nytimes.com`),
  `visitalbuquerque.com` (New Mexico Green Chile Sauce, and the site is .org)
  and `Alison Roman NYT` (Perfect Buttermilk Pancakes, duplicating `source`).
  All three cleared, nothing invented; the count is 310 and every remaining
  value resolves. `breakfast.md`, `dinner-1.md` and `dinner-5.md` republished.
- **`new.json`'s shape is now enforced by `add_recipe.py`.** Both mismatches
  that bit the 21 September add are refused instead of tolerated.
  `ingredients` and `directions` may be a newline-joined string or a list of
  lines — a list is joined here, ingredients one per line and directions with a
  blank line between steps, rather than going into the master as an array and
  breaking `convert.py` and `build2.py` downstream. `claude_opt` accepts only
  `changes`, `delta_min`, `confidence`, `kind` and `log`; an unrecognised key or
  an empty `changes` exits with a message naming the valid ones, where a note
  filed under `note` used to vanish without a word and the recipe shipped as the
  only one of 477 without an optimization note. Both checks run under `--check`
  too, and a supplied `log` is now kept rather than overwritten with `[]`.
  Verified by re-running the 21 September add from both the list and the string
  form on a sandbox copy: each reproduces the shipped record exactly. The
  unpatched original is kept as `add_recipe.py.pre-patch`.

## Added 25 September 2026

- **Quick-Pickled Cucumbers With Rice Vinegar** (Preserves; Kenji, Serious Eats, https://www.seriouseats.com/quick-pickled-cucumbers-rice-vinegar-recipe) and **Laura's Salmon Poke Bowl** (Dinner; Laura's own), in that order via add_recipe.py. Grams were already in every line; convert.py added none. Table counts above updated (the gram-line figures were not recomputed). Published: preserves, dinner-4, dinner-5 (the bowl pushed My Thai Chicken Wraps across the split), roster-complete, overview. Pre-add master kept as recipes_merged.pre-sep25add.json.
- The pickle's roster tag reads RM / "From Robert's archive" because its intake JSON had no `origin`, and add_recipe.py defaults to RM. It did not come from the Gmail archive.

## Open items

- **Beer Can Chicken** is an empty stub — no ingredients, no directions — and
  **Corn Muffin Recipe - Ina** is fragments of a Google results page, with a
  `google.com/search?q=` string sitting in its `source_url`. Both need
  re-entering from a real source.
- **Cucumber Spread** has ingredients but no quantities and no method.
  **Lobster - Steamed** has no ingredient list and a 53-character method.
- Two links are worth a human eye: Hot Artichoke Dip and Plain Pastry for Pie
  Crust, both flagged low confidence.
- The project instructions still point at `recipes/00-roster-all-441.md`. That
  path now holds a "Start here" doc that redirects to `00-roster-complete.md`,
  so nothing breaks, but the instructions are worth updating.
- Standing recommendation not yet done: a curated weeknight shortlist. The gaps
  Robert named are sub-hour mains George will eat (no pork, no fish, no vegetable
  but carrots and cucumbers) and green vegetable sides, of which there are only
  a handful.

## Changed 2 October 2026

- **Chicken Cutlets in Cornmeal Stuffing** (Dinner) edited by hand at Robert's request, not through add_recipe.py: oven 325 to 375, flat casserole to half sheet pan, "1-2 sticks butter" to "2 sticks (227 g) butter", step 5 "45 minutes" to "until temperature reaches 150º F". An `RM 9/26` line was appended to the cook's note (Pepperidge Farm stuffing required, no panko or bread crumbs); the original wording is recorded in `notes`. Timing total 65 to 45 min; optimization note rewritten. Published: dinner-1, roster-complete. Pre-edit master kept as recipes_merged.pre-cutlet.json.
- The Sept 26-29 edits (Greek Orzo Salad feta/olives, Grilled Marinated Shrimp Skewers revision) were checked against the project and are already published in salads and dinner-3, although the publish_prep manifest of 26 September did not show it. The manifest is current as of this run.
- On this machine the Drive folder mounts at `~/mnt/My Drive/Cooking`, not `~/mnt/Cooking`. build2.py and publish_prep.py were run unmodified with HOME pointed at a directory whose `mnt/Cooking` and `mnt/Downloads` are symlinks to the real mounts.
