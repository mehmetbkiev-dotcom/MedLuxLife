#!/usr/bin/env python3
"""Image alt texts in German and Turkish (the free TranslatePress does not translate alt attributes).

  alt_i18n.py collect          -> content/translations/src/alts.json: every non-empty alt on the live English pages (legal pages skipped)
  alt_i18n.py push de_de|tr_tr -> sends content/translations/<de|tr>/alts.json ({English alt: translation}) to the site
                                  (option medlux_alt_i18n_<lang>, used by Code Snippet "image alt texts", snippets/alt_i18n.php)
  alt_i18n.py check de|tr      -> lists alts on the live /de/ or /tr/ pages that are still English (i.e. missing from the list)
"""
import collections, concurrent.futures as cf, html, json, pathlib, re, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools')); import trp
W = trp.W
LEGAL = {3, 596, 602, 604, 612, 616}
KEEP = {'MedLuxLife'}


def pages():
    out = []
    for pg in (1, 2, 3):
        r = trp.get(W + '/wp-json/wp/v2/pages?per_page=100&_fields=id,link&page=%d' % pg)
        if not isinstance(r, list) or not r:
            break
        out += r
    return [p for p in out if p['id'] not in LEGAL]


def alts(prefix):
    def fetch(p):
        path = p['link'].replace('https://medluxlife.de', '').rstrip('/') + '/'
        if path == '/':
            path = '/index.php'
        h = subprocess.run(['curl', '-sS', '--max-time', '90', W + prefix + path], capture_output=True).stdout.decode('utf8', 'ignore')
        h = re.sub(r'(?s)<(script|style)\b.*?</\1>', ' ', h)
        return p['id'], [html.unescape(a).strip() for a in re.findall(r'<img\b[^>]*?\balt="([^"]*)"', h)]
    found = collections.defaultdict(set)
    with cf.ThreadPoolExecutor(6) as ex:
        for pid, al in ex.map(fetch, pages()):
            for a in al:
                if a:
                    found[a].add(pid)
    return found


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'collect':
        found = alts('')
        json.dump([{'original': a, 'pages': sorted(v)} for a, v in sorted(found.items())],
                  open(ROOT / 'content/translations/src/alts.json', 'w'), ensure_ascii=False, indent=1)
        print(len(found), 'alts')
    elif cmd == 'push':
        lang = sys.argv[2]
        m = json.load(open(ROOT / 'content/translations' / lang[:2] / 'alts.json'))
        body = json.dumps({'lang': lang, 'map': m}).encode()
        out = subprocess.run(['curl', '-sS', '-X', 'POST', trp.W + '/wp-json/medlux/v1/alts', '-H', 'Content-Type: application/json', '--data-binary', '@-'],
                             input=body, capture_output=True).stdout
        print(lang, json.loads(out))
    elif cmd == 'check':
        lang = sys.argv[2][:2]
        en = set(json.load(open(ROOT / 'content/translations' / lang / 'alts.json')))
        left = {a: v for a, v in alts('/' + lang).items() if a not in KEEP and (a in en or re.search(r'\b(the|and|with|of|for|during|while)\b', a))}
        print(len(left), 'English alts left on /%s/' % lang)
        for a, v in sorted(left.items()):
            print(' ', a[:110], sorted(v)[:4])
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    main()
