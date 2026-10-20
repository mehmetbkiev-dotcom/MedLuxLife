#!/usr/bin/env python3
"""Ukrainian (/uk/) and Russian (/ru/) without extra TranslatePress languages (the free plugin allows 2 besides English).
The Code Snippet "UK/RU language layer" (snippets/xlang.php) serves /uk/… and /ru/… as the English page and swaps every
text node / alt / placeholder / aria-label / title / submit label found in the list for that language (option medlux_xlang_<lang>).

  xlang.py collect          -> content/translations/src/xlang.json: every visible English string on the live pages (legal pages skipped)
  xlang.py push uk|ru       -> sends content/translations/<uk|ru>/*.json (merged, {English: translation}) to the site
  xlang.py check uk|ru      -> lists strings with Latin letters on the live /uk|ru/ pages that are not a translation from the list
"""
import collections, concurrent.futures as cf, glob, html, json, pathlib, re, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools')); import trp
W = trp.W
LEGAL = {3, 596, 602, 604, 612, 616}
TEXT = re.compile(r'>([^<>]+)<')
ATTR = re.compile(r'\b(alt|placeholder|aria-label|title)="([^"]*)"')
SUBMIT = re.compile(r'<input[^>]*type="submit"[^>]*value="([^"]*)"')


def norm(s):
    return re.sub(r'\s+', ' ', s).strip()


def strings(h):
    h = re.sub(r'(?is)<(script|style|noscript|textarea|title)\b.*?</\1>', ' ', h)
    h = re.sub(r'(?s)<!--.*?-->', ' ', h)
    out = set()
    for t in TEXT.findall(h):
        t = norm(t)
        if t and re.search(r'[A-Za-z]', html.unescape(t)):
            out.add(t)
    for _, v in ATTR.findall(h):
        v = norm(v)
        if v and re.search(r'[A-Za-z]', html.unescape(v)) and not v.startswith(('http', '/', '#')):
            out.add(v)
    for v in SUBMIT.findall(h):
        out.add(norm(v))
    return out


def pages():
    out = []
    for pg in (1, 2, 3):
        r = trp.get(W + '/wp-json/wp/v2/pages?per_page=100&_fields=id,link&page=%d' % pg)
        if not isinstance(r, list) or not r:
            break
        out += r
    return [p for p in out if p['id'] not in LEGAL]


def fetch_all(prefix=''):
    def fetch(p):
        path = p['link'].replace('https://medluxlife.de', '').rstrip('/') + '/'
        if path == '/':
            path = '/index.php'
        h = subprocess.run(['curl', '-sS', '--max-time', '90', W + prefix + path], capture_output=True).stdout.decode('utf8', 'ignore')
        return p['id'], strings(h)
    found = collections.defaultdict(set)
    with cf.ThreadPoolExecutor(6) as ex:
        for pid, ss in ex.map(fetch, pages()):
            for s in ss:
                found[s].add(pid)
    return found


def merged(lang):
    m = {}
    # the big lists (xlang_*.json) first, so later files with fixes and new texts override them
    for f in sorted(glob.glob(str(ROOT / 'content/translations' / lang / '*.json')), key=lambda f: (not pathlib.Path(f).name.startswith('xlang_'), f)):
        m.update(json.load(open(f)))
    return m


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'collect':
        found = fetch_all()
        rows = [{'original': s, 'pages': sorted(v)} for s, v in sorted(found.items(), key=lambda x: (-len(x[1]), x[0]))]
        json.dump(rows, open(ROOT / 'content/translations/src/xlang.json', 'w'), ensure_ascii=False, indent=1)
        print(len(rows), 'strings,', sum(len(re.findall(r'[A-Za-z]+', html.unescape(r['original']))) for r in rows), 'words')
    elif cmd == 'push':
        lang = sys.argv[2]
        m = merged(lang)
        body = json.dumps({'lang': lang, 'map': m}).encode()
        out = subprocess.run(['curl', '-sS', '-X', 'POST', W + '/wp-json/medlux/v1/xlang', '-H', 'Content-Type: application/json', '--data-binary', '@-'],
                             input=body, capture_output=True).stdout
        print(lang, out[:300])
        import cache_clear; print('page cache cleared:', cache_clear.clear())
    elif cmd == 'check':
        lang = sys.argv[2]
        m = merged(lang)
        done = {norm(v) for v in m.values()}
        left = {s: v for s, v in fetch_all('/' + lang).items() if s not in done and re.search(r'[A-Za-z]{3,}', html.unescape(s))}
        print(len(left), 'English strings left on /%s/' % lang)
        for s, v in sorted(left.items(), key=lambda x: -len(x[1]))[:200]:
            print(' ', len(v), '|', s[:120], sorted(v)[:4])
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    main()
