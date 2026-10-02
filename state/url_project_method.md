# URL + enrichment project — method and state

GOAL: for as many of the 488 recipes as possible, record the source URL, a paraphrase
of the author's headnote, and a digest of reader comments. Confidence-flagged.
Robert's answers: enrich ALL of them; use his logged-in Chrome (Browser 2,
deviceId 30cde6c9-fa35-4431-b613-1b700f09a06d) for paywalled sites; best-available
match flagged high/medium/low; run until his usage limit is reached, then resume.

STATE FILE: url_worklist.json (488 rows, field `status`: pending|done|notfound|blocked).
Always re-read it and process only `pending` rows. Write results back after every batch
so an interrupted run loses at most one batch.

ROUTES
  web    (151) — has a public URL. Use WebFetch with a 3-part prompt (headnote paraphrase,
                 ingredients for verification, comment themes).
  chrome (110) — paywalled. 103 cooking.nytimes.com, 6 washingtonpost.com, 1 wsj.com.
  search (227) — no URL. WebSearch first, verify by ingredient list, then enrich.
                 45 are family/personal sources (Symmes, Cencula, MacArthur, Healy...)
                 and are expected dead ends — mark notfound, do not invent a link.

DOMAINS CONFIRMED BLOCKED to WebFetch (do NOT try to route around these — record the
link and move on, flagged "publisher blocks automated access"):
  seriouseats.com (25 recipes), allrecipes.com
DOMAINS CONFIRMED WORKING via WebFetch: foodnetwork.com, theperfectloaf.com

NYT COOKING PIPELINE (2 calls per recipe)
 1. navigate to the recipe URL. An "Cooking is better in the app" modal may appear;
    its dismiss link is "Not now". get_page_text is UNRELIABLE on this site (it returns
    a sidebar recommendation card) — do not use it.
 2. one javascript_tool call. Headnote lives in [class*="topnote"]; comments are
    [class*="note_note__"] with body in [class*="noteBody"]; the helpful-vote count is
    the digits after "Is this helpful?". Click the "Most Helpful" tab and "Show more
    comments" twice before extracting. Cap each body at ~200 chars and take the top 20 —
    they come back already ordered by votes.

Extractor that works (paste into javascript_tool):

const sleep = ms => new Promise(r => setTimeout(r, ms));
const txt = el => el ? el.innerText.replace(/\s+/g,' ').trim() : '';
const tabs = [...document.querySelectorAll('[role="tab"]')];
const mh = tabs.find(t => /most helpful/i.test(t.innerText));
if (mh) { mh.click(); await sleep(1200); }
for (let i=0;i<2;i++){ const m=[...document.querySelectorAll('button')].find(b=>/show more comments/i.test(b.innerText)); if(!m) break; m.click(); await sleep(1500); }
let head=''; document.querySelectorAll('[class*="topnote"]').forEach(c=>{if(txt(c).length>head.length) head=txt(c);});
const out = [...document.querySelectorAll('[class*="note_note__"]')].map(n=>{
  let b = txt(n.querySelector('[class*="noteBody"]')) || txt(n);
  b = b.replace(/Is this helpful\?\s*[\d,]*\s*$/,'').trim();
  const h = (txt(n).match(/Is this helpful\?\s*([\d,]+)/)||[])[1] || '';
  return h + ' | ' + b.slice(0,200);
}).filter(x=>x.length>70);
JSON.stringify({headnote: head.slice(0,1200), rating: txt(document.querySelector('[class*="rating"]')).slice(0,40), comments: out.slice(0,20)},null,0)

WRITING RESULTS: the digest goes in the recipe's `notes` field, never the `description`
(cook's note) field — that belongs to the family. Prefix "Web: ". Rebuild outputs with
build2.py afterwards.

KNOWN OBSTACLE: Google Drive's mirror hardlinks files in the Cooking folder, which makes
device_stage_files refuse to read them back. Workaround that works: generate on the
device, print per-document md5s, reproduce the edit container-side, and verify the
hashes match before publishing to the project.
