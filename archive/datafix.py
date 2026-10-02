# -*- coding: utf-8 -*-
"""Repair the data problems the optimization passes turned up.

Rules: the family's cook's note (`description`) is never touched. Every repair
appends a dated line to `notes` so it can be audited or reversed. Where the
right value is genuinely ambiguous, the entry is FLAGGED rather than changed.
"""
import json, re
R = json.load(open('recipes_merged.json'))
by = {r['name']: r for r in R}
log = []

def note(r, msg):
    cur = r.get('notes') or ''
    line = 'Data fix (Sept 2026): ' + msg
    if line not in cur:
        r['notes'] = (cur + ('\n\n' if cur else '') + line).strip()
    log.append((r['name'], msg))

def split(name, ing, dirs, msg):
    r = by[name]; r['ingredients'] = ing; r['directions'] = dirs; note(r, msg)

# ---------------------------------------------------------------- structural
# Eight index-card recipes had their method written into the ingredients field
# (or the reverse). Nothing is invented here; the lines are only moved.

split('Beef Stew',
 "1 lg. onion chopped\n2 cloves garlic chopped\n1 lb. (454 g) beef cubes coated in flour and salt\n"
 "1/2 c. (118 g) red wine\n1 6-oz. (170 g) can tomato paste\n2 c. (474 g) water\n2 carrots, chopped\n"
 "3-4 boiling potatoes, chopped",
 "Saute the onion, garlic and floured beef cubes.\n\nAdd the red wine, tomato paste and water. "
 "Simmer 1 1/2 hours.\n\nAdd the carrots and potatoes and cook for 1 1/2 hours more.",
 "the method was written inside the ingredients list; moved to Directions, wording unchanged.")

split('Blue Cheese Dressing',
 "1 c. (135 g) blue cheese\n2 c. (440 g) mayonnaise\n1/4 c. (60 g) vinegar\n1/2 c. (115 g) sour cream\n"
 "1 to 3 cloves of garlic minced\n2 T. (25 g) sugar, optional\n1/2 c. (68 g) blue cheese chunks",
 "Mix the blue cheese, mayonnaise, vinegar, sour cream, garlic and optional sugar. Beat until fluffy.\n\n"
 "Then add the blue cheese chunks. Chill and serve.",
 "the method was written inside the ingredients list; moved to Directions, wording unchanged.")

split('Chocolate Sauce',
 "1/4 c. (57 g) butter\n1/4 c. (42 g) shaved unsweetened chocolate (2 one-ounce squares)\n"
 "3/4 c. (150 g) sugar\n1/4 c. (21 g) cocoa\n1/2 c. (119 g) light cream\npinch salt\n1 t. (4.2 g) vanilla",
 "Melt the butter in a saucepan. Add the shaved chocolate and keep over a low flame until smooth, "
 "or use a double boiler.\n\nThen add the sugar, cocoa, cream, salt and vanilla. Bring to a boil.\n\n"
 "Chill. Reheat as needed. Never sugars.",
 "the method was written inside the ingredients list; moved to Directions, wording unchanged.")

split('Playdough',
 "3 c. (360 g) flour\n1 1/2 c. (432 g) regular table salt\n6 teaspoons (19 g) cream of tartar\n"
 "3 c. (711 g) water (optional - with a few drops of food coloring)\n3 Tablespoons (41 g) cooking oil",
 "Mix together the flour, salt and cream of tartar.\n\nAdd the water and cooking oil.\n\n"
 "Cook and stir over low heat until the mixture forms a ball. Cool and knead a bit. "
 "Store in an airtight container or ziplock bag.",
 "the method was written inside the ingredients list; moved to Directions, wording unchanged.")

r = by['Sourdough Pizza Dough For Ooni']
_full = r['ingredients']
r['ingredients'] = ("160 g water at about 80°\n50 g sourdough leaven prepared last night\n"
                    "25 g whole wheat flour\n235 g pizza flour such as Nuvola Super\n20 g water\n6 g salt")
r['directions'] = re.sub(r'^\s*\n', '', _full)
note(r, "ingredients and method were both in the ingredients field; the full text is now under Directions "
        "and the ingredients list extracted from it.")

r = by['Orange Whip']
r['ingredients'] = ("1/4 c. orange juice\n1 T. unflavored gelatin (1 pkg.)\n1/2 c. sugar\n2 T. lemon juice\n"
                    "1 1/4 c. orange juice\ngrated orange zest, if desired\n3/4 c. chilled evaporated milk (1/2 can)")
note(r, "the ingredients were listed only inside the directions; extracted into an ingredients list. "
        "The card reads '1/c. orange juice' for the first quantity, taken as 1/4 cup.")

r = by['RO-TEL Cheese Dip and Spread']
r['ingredients'] = "1/2 can Ro-Tel Tomatoes and Green Chilies\n1/2 lb. (227 g) pasteurized cheese"
note(r, "the ingredients field was empty; the two quantities were stated only in the directions and "
        "have been extracted into an ingredients list.")

r = by['White Sauce']
r['directions'] = ("Melt the butter in a saucepan over medium heat. Whisk in the flour and cook, stirring, "
                   "about 2 minutes, until it smells nutty but has not coloured.\n\n"
                   "Add the milk gradually, whisking constantly. Bring to a simmer and cook, still stirring, "
                   "until thickened and no longer tasting of raw flour, 5 to 8 minutes. Season with salt.\n\n"
                   "Choose thin, medium or thick according to what the sauce is for.")
note(r, "the card records only the three butter/flour/milk ratios and no method, which leaves it unusable "
        "on its own. The standard roux method has been added; it is not from the family card.")

# ---------------------------------------------------------------- metadata
r = by['Greek Salad (Washington Post)']
r['source_url'] = ''
note(r, "the stored link pointed at Ina Garten's Greek salad on Food Network, which is a different recipe "
        "(this one has balsamic, mint and green peppers). Link removed rather than left wrong.")

r = by['Zucchini Gratin (Richard Olney)']
r['source_url'] = 'https://www.kermitlynch.com/media/Zucchini%20recipe.pdf'
note(r, "the stored link pointed at Ina Garten's zucchini gratin. The text here is Richard Olney's "
        "persillade gratin from a Kermit Lynch newsletter; the link now points there.")

r = by['Flour Bakery Chocolate Chip Cookies']
note(r, "this shares a source link with Chocolate Chunk Cookies, but the two ingredient lists differ "
        "(flour ratios, chip vs chunk). Treat the link as a lead rather than a citation.")

r = by['Rye Bread –']
r['name'] = 'Rugbrod Rye Bread — Food Geek (second transcription)'
note(r, "the title was a truncated 'Rye Bread -'. Renamed. This and 'Rugbrod Rye Bread—Food Geek' are two "
        "transcriptions of the same foodgeek.io page with different levain quantities; this is the fuller one.")

r = by['Corn Muffin Recipe - Ina']
note(r, "this entry is not a recipe. The ingredients and directions are fragments of a Google results page "
        "(note 'View full list'), the quantities are duplicated and inconsistent, and eggs, butter, milk and "
        "salt are missing entirely. The stored link is the Google search itself. Needs re-entering from "
        "Ina Garten's actual corn muffin recipe before it can be cooked from.")

r = by['Beer Can Chicken']
note(r, "this entry is an empty stub - no ingredients and no directions, only the title. "
        "Nothing was recoverable; it needs entering from scratch.")

r = by['Cucumber Spread']
note(r, "incomplete as recorded: salt, onion powder, Accent and cucumber are listed without quantities and "
        "there is no method. Only the 8 oz cream cheese is specified.")

r = by['Snickerdoodles']
note(r, "the research notes above describe Betty Crocker's published version, which uses a butter and "
        "shortening split. The family card itself calls for margarine; that has been left as written.")

# ---------------------------------------------------------------- quantities
r = by['Roast Chicken With Mustard Vinaigrette']
r['directions'] = r['directions'].replace('3 cup chopped shallots', '3 tablespoons chopped shallots')
note(r, "the mustard vinaigrette read '3 cup chopped shallots' against a stated yield of about 1 1/2 cups, "
        "which is impossible - the other ingredients already come to roughly 1 1/8 cups. Read as 3 tablespoons.")

r = by['Red-Braised Pork (Dunlop)']
r['ingredients'] = re.sub(r'3\.4 tsp \(20 g\) salt', '3/4 tsp salt', r['ingredients'])
note(r, "'3.4 tsp (20 g) salt' was a misread of 3/4 tsp, and our gram figure was computed from it. "
        "Corrected; the dish takes most of its salt from the soy sauce.")

r = by['Roasted Brussels Sprouts with Garlic']
r['ingredients'] = re.sub(r'1 pint \(176 g\) brussels sprouts', '1 pint brussels sprouts', r['ingredients'],
                          flags=re.I)
note(r, "the line read '1 pint (176 g) brussels sprouts (about a pound)'. A pint of sprouts is roughly 340 g "
        "and a pound is 454 g, so our 176 g figure was wrong and the source contradicts itself. "
        "Gram figure removed; weigh to about 450 g if following 'about a pound'.")

r = by['Rolled Onion Sandwich']
r['directions'] = r['directions'].replace('Broil until thickens', 'Boil until it thickens')
note(r, "'Broil until thickens' read as a slip for 'Boil' - broiling a raw yolk, sugar and vinegar mixture "
        "would scramble it rather than thicken it.")

# --------------------------------------------------- flagged, not changed
for nm, msg in [
 ("Julia Child's Berry Clafoutis",
  "the card calls for 1 tablespoon of vanilla extract, where most clafoutis recipes use 1 teaspoon. "
  "Left as written - it may well be deliberate - but worth checking against the source before baking."),
 ('Vanillekipferl (German Vanilla Crescent Cookies)',
  "'1 Tbsp vanilla pod' measures a pod by volume, which is unusual; it may mean vanilla sugar. "
  "Left as written."),
]:
    if nm in by: note(by[nm], msg)
    else:
        cand=[k for k in by if nm.split('(')[0].strip()[:14].lower() in k.lower()]
        print('  ! not found:', nm, '| candidates:', cand[:4])

json.dump(R, open('recipes_merged.json','w'), ensure_ascii=False)
print(f'\n{len(log)} repairs logged\n')
for n,m in log: print(f'  {n[:44]:<44} {m[:88]}')
