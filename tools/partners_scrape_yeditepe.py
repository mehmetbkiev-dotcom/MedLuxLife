"""Scrape Yeditepe doctors (EN list + EN/TR detail pages) into yeditepe_doctors.json."""
import re, html, json, subprocess, concurrent.futures as cf, os, sys
B = 'https://yeditepehastaneleri.com'
D = os.environ.get("SCRAPE_DIR", "/tmp/partners_src/yd")  # raw HTML cache (not in the repo)


def get(url, fn=None):
    fn = fn and os.path.join(D, fn)
    if fn and os.path.exists(fn) and os.path.getsize(fn) > 5000:
        return open(fn, encoding='utf-8', errors='ignore').read()
    for _ in range(3):
        r = subprocess.run(['curl', '-sS', '-L', '--max-time', '40', '-A', 'Mozilla/5.0', url], capture_output=True)
        s = r.stdout.decode('utf-8', 'ignore')
        if len(s) > 5000:
            if fn:
                open(fn, 'w', encoding='utf-8').write(s)
            return s
    return ''


def txt(x):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', x))).strip()


def parse_list(s):
    out = []
    for c in s.split('<div class="card mb-3 border">')[1:]:
        m = re.search(r'href="(/en/doct?orlar/[^"]+|/en/doctors/[^"]+)" class="card-img-top" title="([^"]*)" aria-label="([^"]*)"', c)
        if not m:
            continue
        img = re.search(r'<img[^>]*src="([^"]+)"', c)
        deps = re.findall(r'href="/en/services/([^"]+)" title="([^"]*)"', c)
        out.append({'url': m.group(1), 'name_en': html.unescape(m.group(2)).strip(), 'title_en': html.unescape(m.group(3)).strip(),
                    'photo': img and html.unescape(img.group(1)), 'deps': [(a, html.unescape(b)) for a, b in deps]})
    return out


def parse_detail(s):
    d = {}
    m = s.find('physicians-wrapper')
    s = s[m:] if m > 0 else s
    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S)
    d['h1'] = h1 and txt(h1.group(1))
    d['hospitals'] = [(a, html.unescape(b)) for a, b in re.findall(r'href="/(?:en/hospitals|hastaneler)/([^"]+)"[^>]*>([^<]+)<', s.split('physicians-bottom-wrapper')[0])]
    d['deps'] = [(a, html.unescape(b)) for a, b in re.findall(r'href="/(?:en/services|tibbi-birimler)/([^"]+)" class="btn[^"]*btn-arrow[^"]*"[^>]*>([^<]+)<', s)]
    pairs = re.findall(r'<p class="text-info mb-1">(.*?)</p>\s*(.*?)(?=<p class="text-info mb-1">|</div>)', s, re.S)
    d['fields'] = [(txt(a), txt(b)) for a, b in pairs if 'mailto:' not in b]
    lists = []
    for h, body in re.findall(r'<h2>(.*?)</h2>\s*(<ul>.*?</ul>|<p>.*?</p>)', s, re.S):
        lists.append((txt(h), [txt(li) for li in re.findall(r'<li>(.*?)</li>', body, re.S)] or [txt(body)]))
    d['lists'] = lists
    tr = re.search(r'hreflang="tr" href="([^"]+)"', s) or re.search(r'hreflang="tr" href="([^"]+)"', s)
    return d


if __name__ == '__main__':
    os.makedirs(D, exist_ok=True)
    first = get(B + '/en/doctors', 'list_1.html')
    last = max(int(x) for x in re.findall(r'href="\?pg=(\d+)"', first))
    pages = [first] + list(cf.ThreadPoolExecutor(6).map(lambda n: get(B + '/en/doctors?pg=%d' % n, 'list_%d.html' % (n + 1)), range(1, last + 1)))
    docs, seen = [], set()
    for p in pages:
        for c in parse_list(p):
            if c['url'] not in seen:
                seen.add(c['url']); docs.append(c)
    print('list', len(docs), 'pages', len(pages), file=sys.stderr)

    def detail(c):
        slug = c['url'].rstrip('/').split('/')[-1]
        en = get(B + c['url'], 'en_%s.html' % slug)
        c['en'] = parse_detail(en)
        m = re.search(r'hreflang="tr" href="([^"]+)"', en)
        c['tr_url'] = m and m.group(1)
        if c['tr_url']:
            trs = get(c['tr_url'], 'tr_%s.html' % slug)
            c['tr'] = parse_detail(trs)
        big = re.search(r'physicians-left-content.*?<img[^>]*src="([^"]+)"', en, re.S)
        c['photo_big'] = big and html.unescape(big.group(1))
        return c
    docs = list(cf.ThreadPoolExecutor(6).map(detail, docs))
    json.dump(docs, open(os.path.join(os.path.dirname(D), "yeditepe_doctors.json"), "w"), ensure_ascii=False, indent=1)
    print('done', len(docs), file=sys.stderr)
