"""Build the search-suggestion index (content/search_index.json) from the live pages + content/search_terms.py.
Run after page titles/sections change, then upload with tools/upload_search_index.py."""
import glob, html, json, re, sys, collections
sys.path.insert(0, '/home/user/MedLuxLife/content')
from search_terms import T
# card names in German/Turkish from the reviewed translations (content/translations/<de|tr>/*.json, {English: translation})
CARD_TR = {}
for l in ('de', 'tr'):
    CARD_TR[l] = {}
    for f in glob.glob('/home/user/MedLuxLife/content/translations/%s/*.json' % l):
        if f.endswith('alts.json'):
            continue
        for k, v in json.load(open(f)).items():
            CARD_TR[l][re.sub(r'\s+', ' ', html.unescape(k)).strip()] = html.unescape(v).replace('\u00a0', ' ').strip()
raw = json.load(open(sys.argv[1]))           # produced by the collector (titles, parents, EN card titles)
pages = raw['pages']
cnt = collections.Counter(c for it in raw['items'] for c in set(it['en']['cards']))
L = ('de', 'tr', 'ru', 'uk')
def tr(pid, lang):
    pid = int(pid)
    if lang == 'en' or pid not in T: return pages[str(pid)]['title']
    return T[pid][L.index(lang)]
out = []
for it in raw['items']:
    pid = it['id']
    chain = []; p = it['parent']
    while p and str(p) in pages:
        chain.insert(0, p); p = pages[str(p)]['parent']
    cards = [c for c in dict.fromkeys(it['en']['cards']) if cnt[c] <= 2 and not re.match(r'^\d+\.', c) and len(c) <= 60
             and '?' not in c and not c.endswith('+')]   # no FAQ questions (accordion headings end with the toggle '+')
    e = {'u': it['path'],
         't': {l: tr(pid, l) for l in ('en',) + L},
         'b': {l: ' › '.join(tr(c, l) for c in chain) for l in ('en',) + L},
         'c': cards,
         'k': T.get(pid, ('',) * 5)[4]}
    cl = {l: [CARD_TR[l].get(c, c) for c in cards] for l in ('de', 'tr')}
    if any(cl[l] != cards for l in cl):
        e['cl'] = cl                          # shown instead of the English card name on /de/ and /tr/
    out.append(e)
B = []
for e in out:
    key = json.dumps(e['b'], ensure_ascii=False)
    if key not in B: B.append(key)
    e['b'] = B.index(key)
out = {'B': [json.loads(b) for b in B], 'E': out}
json.dump(out, open('/home/user/MedLuxLife/content/search_index.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print(len(out['E']), 'entries,', sum(len(e['c']) for e in out['E']), 'section names,', len(json.dumps(out, ensure_ascii=False, separators=(',', ':')).encode()) // 1024, 'KB')
