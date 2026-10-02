# URL + enrichment project — COMPLETE

Finished 19 September 2026. The pending queue is empty; every one of the 488
recipes has been through the pipeline.

## Final state

| status   | count |
|----------|-------|
| done     | 295 |
| notfound | 159 |
| blocked  | 32 |
| thin     | 2 |

Confidence on the 295 enriched: 180 high, 92 medium, 23 low.
324 of 488 recipes carry a source URL.
294 carry a web summary.
Library is now 1,181,562 bytes.

The 159 notfounds are the correct answer, not a gap: they are family
recipes (Symmes, Cencula, MacArthur, Healy, Vedeen, Cairoli, Kissell, Cordella,
Willingham and others), print-only clippings, and book-only recipes with no
authorised online text. Each got a confirming search; runner-up URLs are recorded
in each row's `notes` where any existed, so a human can promote one.

## Blocked publishers (32 recipes)

  unknown                      9
  bonappetit.com               4
  foodandwine.com              3
  epicurious.com               3
  thespruceeats.com            2
  ampmetrics.allrecipes.com    1
  washingtonpost.com           1
  thequirkandthecool.com       1
  hispanickitchen.com          1
  seriouseats.com              1
  myfoodandfamily.com          1
  liquor.com                   1
  simplyrecipes.com            1
  latimes.com                  1
  cookstr.com                  1
  myrecipes.com                1

These refuse automated fetching. Robert pasted Serious Eats and Allrecipes content
in by hand, which is how 32 of those got enriched anyway. The same route works for
any of the rest: open the page, paste into a file, ask Claude to ingest it.

## Still wanting a human decision

Links accepted at low confidence (23):
  - Asian Grilled Salmon
  - Baked Raclette
  - Baked Shrimp Scampi - Ina
  - Balsamic-Roasted Brussels Sprouts
  - Broiled Chicken Breast Salad with Curry Dressing--Franey
  - Brown Butter and Sage Butternut Squash Bake
  - Candied Orange Peel
  - Cauliflower Cheese Pie
  - Cheese Straws--bread sticks
  - ChefSteps Quiche
  - Chili a la Franey
  - Chocolate Truffles Ina
  - Creamy Hummus—Ina
  - Crockpot Pork and Mushrooms with Shallots
  - Crusty Baked Shells & Cauliflower
  - Dill Fingerling Potatoes
  - Easy Sole Meuniere
  - Farro Tabbouleh with Feta
  - Fresh Crab Nachos - Ina
  - Grilled Herb Shrimp—Ina
  - Hot Artichoke Dip
  - Plain Pastry for Pie Crust
  - Sourdough Naan

Also open:
  - Anzac Biscuits I and Greek Orzo Salad never made it into the paste file.
  - Duplicate entries confirmed during this work and left alone deliberately:
    Black Bean Salsa, Chili Dip, Greek Salad, Original Plum Torte, Panettone,
    Zucchini Gratin, plus Simmered Smoked Links/Sausages, Rugbrod Rye Bread /
    "Rye Bread -", Tortilla Pie/Wedges, and the three Crockpot pork entries.
  - The project's custom instructions still point at recipes/00-roster-all-441.md.
    The live file is recipes/00-roster-all-488.md.

## Gram weights — the natural next project

Robert's standing instruction is to add gram weights everywhere possible. This
pass surfaced a lot of raw material for that, sitting in the enriched notes:
comment threads that supply conversions, publisher pages already in grams, and
several cases where the grams and the volumes on the same page disagree and the
grams are the reliable figure (Flour peanut butter cookies, Flour oatmeal
raisin, NYT whole-wheat pancakes). Worth a dedicated pass rather than ad hoc.
