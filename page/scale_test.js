// Regression check for page/scale.js.   node page/scale_test.js   (after python3 page.py)
// Fixed cases are asserted; the sweep prints counts and a few lines from each risky
// category so a change to the rules can be read against real ingredient lines.
const { scaleLine } = require('./scale.js');
const s = (line, k) => scaleLine(line, k).parts.map(p => p[0]).join('');
const cases = [
  ['2 c. (276 g) Pepperidge Farm Cornmeal Stuffing', 2, '4 c. (552 g) Pepperidge Farm Cornmeal Stuffing'],
  ['3/4 c. (68 g) Parmesan cheese grated', 2, '1 1/2 c. (136 g) Parmesan cheese grated'],
  ['1/2 t. (1.1 g) pepper', 0.5, '1/4 t. (0.55 g) pepper'],
  ['8 boneless chicken breasts', 0.5, '4 boneless chicken breasts'],
  ['3/4-1 c. (150-200 g) sugar', 2, '1 1/2-2 c. (300-400 g) sugar'],
  ['1 28 oz. (794 g) can Italian plum tomatoes, drained and coarsely chopped', 2, '2 28 oz. (794 g) can Italian plum tomatoes, drained and coarsely chopped'],
  ['8 5-ounce (142 g) chicken breasts, skinless and boneless', 2, '16 5-ounce (142 g) chicken breasts, skinless and boneless'],
  ['4 skinless boneless chicken breasts, about 6 ounces (170 g) each', 2, '8 skinless boneless chicken breasts, about 6 ounces (170 g) each'],
  ['2 chickens, 3 1/2 to 4 pounds (1.6-1.8 kg) each, quartered', 0.5, '1 chickens, 3 1/2 to 4 pounds (1.6-1.8 kg) each, quartered'],
  ['1-inch (2.5 cm) piece fresh ginger, peeled and finely chopped', 2, '1-inch (2.5 cm) piece fresh ginger, peeled and finely chopped'],
  ['2 pounds (907 g) (12 to 15 per pound) shrimp in the shell', 2, '4 pounds (1814 g) (12 to 15 per pound) shrimp in the shell'],
  ['12 tablespoons (170 g) (1½ sticks) unsalted butter, at room temperature', 2, '24 tablespoons (340 g) (3 sticks) unsalted butter, at room temperature'],
  ['¼ cup (54 g) plus 2 tablespoons vegetable oil', 2, '1/2 cup (108 g) plus 4 tablespoons vegetable oil'],
  ['4 sprigs fresh thyme or 1 teaspoon dried', 2, '8 sprigs fresh thyme or 2 teaspoon dried'],
  ['12 to 14 thin asparagus, bottom third discarded and tips sliced in 2-inch pieces', 2, '24 to 28 thin asparagus, bottom third discarded and tips sliced in 2-inch pieces'],
  ['4 - 6 tbsp (64-96 g) Thai Green Curry Paste (Maesri best) OR (Note 1)', 2, '8 - 12 tbsp (128-192 g) Thai Green Curry Paste (Maesri best) OR (Note 1)'],
  ['Flour Blend (100%): 206.59 g | 7.29 oz (80% King Arthur AP, 20% semolina, or just KAAP if you don\'t have semolina)', 2, 'Flour Blend (100%): 413 g | 14.6 oz (80% King Arthur AP, 20% semolina, or just KAAP if you don\'t have semolina)'],
  ['250g Pastry flour', 0.5, '125g Pastry flour'],
  ['Kosher salt and freshly ground black pepper', 3, 'Kosher salt and freshly ground black pepper'],
  ['1 4-pound (1.8 kg) chicken', 2, '2 4-pound (1.8 kg) chicken'],
  ['1⁄4 t. celery salt', 2, '1/2 t. celery salt'],
  ['3/4 cup (172 g) sour cream (1)', 2, '1 1/2 cup (344 g) sour cream (1)'],
  ['2 cups (300 g) grated raw potatoes', 1.5, '3 cups (450 g) grated raw potatoes'],
  ['3 large eggs', 1.5, '4 1/2 large eggs'],
  ['Juice of 1/2 lime , to taste', 2, 'Juice of 1 lime , to taste'],
  ['1 small-ish head cauliflower (about 2 pounds), green leaves removed', 2, '2 small-ish head cauliflower (about 4 pounds), green leaves removed'],
];
let bad = 0;
for (const [line, k, want] of cases) { const got = s(line, k); if (got !== want) { bad++; console.log('FAIL x' + k + '\n  line: ' + line + '\n  want: ' + want + '\n  got:  ' + got); } }
console.log(bad ? bad + ' of ' + cases.length + ' fixed cases FAILED' : 'all ' + cases.length + ' fixed cases pass');

let data; try { data = require('../build/page/recipes.json'); } catch (e) { process.exit(bad ? 1 : 0); }
const lines = []; for (const r of data.recipes) for (const l of (r.i || '').split('\n')) if (l.trim() && !/:$/.test(l.trim())) lines.push(l.trim());
const changed = lines.filter(l => scaleLine(l, 2).changed), withDigit = lines.filter(l => /\d|[¼½¾⅓⅔⅛]/.test(l));
console.log('\nsweep x2: ' + lines.length + ' lines, ' + withDigit.length + ' contain a number, ' + changed.length + ' scaled, ' + (withDigit.length - changed.length) + ' with a number left unscaled');
const show = (title, f, n) => { const hit = lines.filter(f); console.log('\n-- ' + title + ' (' + hit.length + ') --'); for (const l of hit.filter((_, i) => i % Math.max(1, Math.floor(hit.length / n)) === 0).slice(0, n)) console.log('   ' + l + '\n=> ' + s(l, 2)); };
const N = +process.argv[2] || 0;
if (N) {
  show('number present, nothing scaled', l => /\d|[¼½¾⅓⅔⅛]/.test(l) && !scaleLine(l, 2).changed, N);
  show('partly scaled: some numbers left as written', l => { const r = scaleLine(l, 2); return r.changed && r.parts.some(p => !p[1] && /\d/.test(p[0])); }, N * 2);
  show('"each"', l => /\beach\b/i.test(l), N);
  show('fully scaled, three or more amounts', l => { const r = scaleLine(l, 2); return r.parts.filter(p => p[1]).length >= 3 && !r.parts.some(p => !p[1] && /\d/.test(p[0])); }, N);
}
process.exit(bad ? 1 : 0);
