/* Scale the amounts in ONE ingredient line by a factor. Shared by the phone page and
   its test (page/scale_test.js). Pure arithmetic on what is written: a line with no
   amount comes back unchanged, and nothing is ever added to a line.

   What scales: every quantity in the line, including the gram weight beside it.
   What does not: sizes ("1 28 oz. can", "5-ounce", "1-inch"), per-item amounts
   ("6 ounces each"), dimensions, temperatures, percentages, "(Note 1)".

   scaleLine(line, k) -> { parts: [[text, scaled?], ...], changed: bool } */
(function (root) {
  var UF = { '¼': .25, '½': .5, '¾': .75, '⅓': 1 / 3, '⅔': 2 / 3, '⅛': .125, '⅜': .375, '⅝': .625, '⅞': .875 };
  var U = '[¼½¾⅓⅔⅛⅜⅝⅞]';
  var NUM = '(?:\\d{1,3}(?:,\\d{3})+|\\d+\\s+\\d+\\s*[/⁄]\\s*\\d+|\\d+\\s*[/⁄]\\s*\\d+|\\d*\\.\\d+|\\d+(?:\\s?' + U + ')?|' + U + ')';
  var QTY = new RegExp('(' + NUM + ')(?:(\\s*(?:-|–|—|to|or)\\s*)(' + NUM + '))?', 'g');
  var METRIC = /^\s*(g|kg|ml|l|grams?|kilograms?|milliliters?|millilitres?|liters?|litres?)\b/i;
  var NOT_AN_AMOUNT = /^\s*(?:-|–)?\s*(?:inch(?:es)?\b|in\.|"|”|″|cm\b|mm\b|°|º|degrees?\b|%|percent\b|minutes?\b|mins?\b|hours?\b|hrs?\b|per\b|x\s*\d|by\s+\d|st\b|nd\b|rd\b|th\b)/i;
  var NOT_AFTER = /(?:\bnotes?|\bstep|\bpage|\bx|\bby|\binto|\bin|\bat|\bevery|\bsize|\bsetting|\bno\.?|#)\s*$/i;
  var EACH = /^\s*[A-Za-z.\-]*\s*(?:\([^)]*\)\s*)?each\b/i;
  var PAREN_SKIP = /\bper\b|\bnotes?\b|\beach\b|%|\bsee\b|inch|"|”|\bcm\b|\bmm\b|°|º/i;

  function val(s) {
    s = s.replace(/,/g, '').trim(); var m;
    if ((m = /^(\d+)\s+(\d+)\s*[\/⁄]\s*(\d+)$/.exec(s))) return +m[1] + m[2] / m[3];
    if ((m = /^(\d+)\s*[\/⁄]\s*(\d+)$/.exec(s))) return m[1] / m[2];
    if ((m = new RegExp('^(\\d+)\\s?(' + U + ')$').exec(s))) return +m[1] + UF[m[2]];
    if (UF[s] !== undefined) return UF[s];
    return parseFloat(s);
  }
  var FR = [[0, ''], [1 / 8, '1/8'], [1 / 4, '1/4'], [1 / 3, '1/3'], [3 / 8, '3/8'], [1 / 2, '1/2'], [5 / 8, '5/8'], [2 / 3, '2/3'], [3 / 4, '3/4'], [7 / 8, '7/8'], [1, '']];
  function trim(n, d) { return String(parseFloat(n.toFixed(d))); }
  function fmt(v, metric) {
    if (metric) return v < 1 ? trim(v, 2) : v < 10 ? trim(v, 1) : String(Math.round(v));
    var w = Math.floor(v + 1e-9), f = v - w, best = null;
    for (var i = 0; i < FR.length; i++) if (Math.abs(FR[i][0] - f) < 0.02) { best = FR[i]; break; }
    if (!best) return v < 10 ? trim(v, 2) : trim(v, 1);
    if (best[0] === 1) { w += 1; best = FR[0]; }
    return best[1] ? (w ? w + ' ' + best[1] : best[1]) : String(w);
  }

  function scaleLine(line, k) {
    var parts = [], last = 0, changed = false, m, prevEnd = -1, frozen = -1;
    if (!(k > 0) || Math.abs(k - 1) < 1e-9) return { parts: [[line, false]], changed: false };
    var parenAt = function (i) {           // start index of the paren enclosing i, or -1
      var d = 0, st = -1;
      for (var j = 0; j < i; j++) { if (line[j] === '(') { d++; st = j; } else if (line[j] === ')') d = Math.max(0, d - 1); }
      return d > 0 ? st : -1;
    };
    var freezeNextParen = function (after, end) { var p = /^(?:\s*-?\s*[A-Za-z.\-]+)?\s*\(/.exec(after); if (p) frozen = end + p[0].length - 1; };
    QTY.lastIndex = 0;
    while ((m = QTY.exec(line))) {
      var i = m.index, end = i + m[0].length, before = line.slice(0, i), after = line.slice(end), prev = line[i - 1] || '';
      var skip = false, size = false;
      if (/[A-Za-z0-9.]/.test(prev)) skip = true;                       // inside a word or a number
      else if (/^[-–][A-Za-z]/.test(after)) { skip = true; size = true; } // 5-ounce, 1-inch, 2-pound
      else if (NOT_AN_AMOUNT.test(after) || NOT_AFTER.test(before)) skip = true;
      else if (prevEnd >= 0 && /^\s+$/.test(line.slice(prevEnd, i))) { skip = true; size = true; }  // "1 28 oz. can"
      else if (EACH.test(after)) { skip = true; size = true; }
      var ps = parenAt(i);
      if (!skip && ps >= 0) {
        var close = line.indexOf(')', ps), inner = line.slice(ps + 1, close < 0 ? line.length : close);
        if (ps === frozen || PAREN_SKIP.test(inner) || /^\s*\d+\s*$/.test(inner)) skip = true;   // "(1)" is a footnote mark
      }
      if (size) freezeNextParen(after, end);
      prevEnd = skip && !size ? -1 : end;
      if (skip) continue;
      var metric = METRIC.test(after), out = fmt(val(m[1]) * k, metric);
      if (m[3]) out += m[2] + fmt(val(m[3]) * k, metric);
      if (i > last) parts.push([line.slice(last, i), false]);
      parts.push([out, true]); last = end; changed = true;
    }
    if (last < line.length) parts.push([line.slice(last), false]);
    return { parts: parts, changed: changed };
  }
  root.scaleLine = scaleLine;
  if (typeof module !== 'undefined') module.exports = { scaleLine: scaleLine };
})(typeof window !== 'undefined' ? window : globalThis);
