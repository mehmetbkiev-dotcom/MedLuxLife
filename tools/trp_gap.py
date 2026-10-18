#!/usr/bin/env python3
"""List TranslatePress strings that are on a live page but not translated yet (status 0 = new, 1 = old machine translation).

  trp_gap.py de_de|tr_tr  -> prints them and writes content/translations/gap_<lang>.json
Checks every published page (home via /index.php, so header, footer, chat and the home page are included); legal pages are skipped.
More complete than "trp.py collect", which only sees strings linked to a page. Brand names, language names, URLs and the German
legal texts in the contact form stay as they are on purpose."""
import json, re, html, subprocess, sys, concurrent.futures as cf
import pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools')); import trp
W = trp.W
LEGAL = {3, 596, 602, 604, 612, 616}
lang = sys.argv[1]
pages = []
for pg in (1, 2, 3):
    r = trp.get(W + '/wp-json/wp/v2/pages?per_page=100&_fields=id,link&page=%d' % pg)
    if not isinstance(r, list) or not r: break
    pages += r
def norm(s): return re.sub(r'\s+', ' ', html.unescape(s)).strip()
def fetch(p):
    path = p['link'].replace('https://medluxlife.de', '').rstrip('/') + '/'
    if path == '/': path = '/index.php'
    h = subprocess.run(['curl', '-sS', '--max-time', '90', W + path], capture_output=True).stdout.decode('utf8', 'ignore')
    h = re.sub(r'(?s)<(script|style)\b.*?</\1>', ' ', h)
    return p['id'], norm(h), norm(re.sub(r'<[^>]+>', ' | ', h))
with cf.ThreadPoolExecutor(6) as ex:
    H = list(ex.map(fetch, pages))
out = []
for r in trp.rows(lang):
    if str(r['status']) == '2': continue
    o = norm(r['original'])
    if not o or not re.search('[A-Za-z]', o): continue
    plain = norm(re.sub(r'<[^>]+>', '', r['original']))
    hit = [pid for pid, h, t in H if (o in h) and (len(o) > 30 or ('>' + o + '<').replace('> ', '>') in h.replace('> ', '>').replace(' <', '<') or ('"' + o + '"') in h)]
    hit_nonlegal = [p for p in hit if p not in LEGAL]
    if hit_nonlegal:
        out.append({'id': r['id'], 'status': r['status'], 'original': r['original'], 'pages': hit_nonlegal[:6], 'n': len(hit_nonlegal)})
json.dump(out, open(ROOT / 'content/translations' / ('gap_%s.json' % lang), 'w'), ensure_ascii=False, indent=0)
print(len(out), 'untranslated rows on live pages')
for x in out: print(x['id'], x['status'], x['n'], '|', x['original'][:140].replace('\n', ' '), '|', x['pages'][:3])
