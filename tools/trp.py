#!/usr/bin/env python3
"""TranslatePress translations over the admin-only REST API (Code Snippet 7, snippets/translation_api.php).

  trp.py collect            -> content/translations/current_strings.json: strings that appear on the live pages now
                               (dictionary rows linked to a published page via post_parent_id AND found in that page's HTML)
  trp.py push de_de FILE    -> writes translations from FILE (JSON {original: translation}) for every matching row (status 2)
  trp.py backup de_de       -> backups/wp/trp_<lang>_<time>.json (all rows of the dictionary)
"""
import collections, concurrent.futures as cf, html, json, pathlib, re, subprocess, sys, time
ROOT = pathlib.Path(__file__).resolve().parent.parent
W = 'https://medluxlife-6j8sz55bpn.live-website.com'
API = W + '/wp-json/medlux/v1/trp/'


def get(url):
    return json.loads(subprocess.run(['curl', '-sS', '--max-time', '120', url], capture_output=True).stdout)


def rows(lang):
    out, off = [], 0
    while True:
        d = get(API + 'strings?lang=%s&offset=%d&limit=2000' % (lang, off))
        out += d['rows']; off += 2000
        if len(d['rows']) < 2000:
            return out


def meta():
    out, off = [], 0
    while True:
        d = get(API + 'meta?offset=%d&limit=5000' % off)
        out += d['rows']; off += 5000
        if len(d['rows']) < 5000:
            return out


def norm(s):
    return re.sub(r'\s+', ' ', html.unescape(s)).strip()


def collect():
    pages = []
    for pg in (1, 2, 3):
        r = get(W + '/wp-json/wp/v2/pages?per_page=100&_fields=id,link,title,parent&page=%d' % pg)
        if not isinstance(r, list) or not r:
            break
        pages += r
    ids = {str(p['id']) for p in pages}
    links = collections.defaultdict(set)
    for m in meta():
        if m['meta_key'] == 'post_parent_id' and m['meta_value'] in ids:
            links[m['original_id']].add(m['meta_value'])
    def page_html(p):
        h = subprocess.run(['curl', '-sS', '--max-time', '90', W + p['link'].replace('https://medluxlife.de', '')], capture_output=True).stdout.decode('utf8', 'ignore')
        return str(p['id']), norm(h)
    with cf.ThreadPoolExecutor(6) as ex:
        htm = dict(ex.map(page_html, pages))
    dic = rows('de_de')
    cur = []
    for r in dic:
        o = norm(r['original'])
        if not o or not re.search(r'[A-Za-z]', o):
            continue
        on = [pid for pid in links.get(r['original_id'], ()) if o in htm[pid] or norm(re.sub(r'<[^>]+>', '', r['original'])) in htm[pid]]
        if on:
            cur.append({'original': r['original'], 'pages': sorted(on, key=int), 'block_type': r['block_type']})
    order = {str(p['id']): i for i, p in enumerate(sorted(pages, key=lambda p: p['id']))}
    json.dump({'pages': {str(p['id']): {'title': html.unescape(p['title']['rendered']), 'link': p['link'], 'parent': p['parent']} for p in pages},
               'strings': cur}, open(ROOT / 'content/translations/current_strings.json', 'w'), ensure_ascii=False, indent=0)
    words = sum(len(re.findall(r'[A-Za-z]+', re.sub(r'<[^>]+>', ' ', s['original']))) for s in cur)
    print(len(dic), 'dictionary rows;', len(cur), 'current strings;', words, 'words')


def backup(lang):
    data = rows(lang)
    p = ROOT / 'backups/wp' / ('trp_%s_%s.json' % (lang, time.strftime('%Y%m%d_%H%M%S')))
    p.write_text(json.dumps(data, ensure_ascii=False))
    print('backup', p.name, len(data))


def loose(s):
    s = html.unescape(s)
    for a, b in (('\u2013', '-'), ('\u2014', '-'), ('\u2018', "'"), ('\u2019', "'"), ('\u201c', '"'), ('\u201d', '"'), ('\u2026', '...'), ('\u00d7', 'x')):
        s = s.replace(a, b)
    return re.sub(r'\s+', ' ', s).strip()


def push(lang, fn):
    tr = json.load(open(fn))
    lk = {loose(k): v for k, v in tr.items()}
    items = []
    for r in rows(lang):  # exact key first; else the texturized form WordPress stored (&#8211; for " - ", &amp;, curly quotes)
        t = tr.get(r['original']) or lk.get(loose(r['original']))
        if t and t.strip():
            items.append({'id': int(r['id']), 'translated': t})
    done = 0
    for i in range(0, len(items), 200):
        body = json.dumps({'lang': lang, 'items': items[i:i + 200]}).encode()
        res = json.loads(subprocess.run(['curl', '-sS', '-X', 'POST', API + 'translate', '-H', 'Content-Type: application/json', '--data-binary', '@-'], input=body, capture_output=True).stdout)
        done += res.get('updated', 0)
    print(lang, 'rows matched', len(items), 'updated', done, '| translations in file', len(tr))
    import cache_clear; print('page cache cleared:', cache_clear.clear())


if __name__ == '__main__':
    {'collect': lambda: collect(), 'backup': lambda: backup(sys.argv[2]), 'push': lambda: push(sys.argv[2], sys.argv[3])}[sys.argv[1]]()
