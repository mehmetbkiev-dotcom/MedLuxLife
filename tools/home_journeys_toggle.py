#!/usr/bin/env python3
"""Home page 2nd screen: language card + both journeys (on) or the old order (off).

on  : wraps "Your Medical Journey" + "Travel Journey" in a group (div.mlx-journeys) right after the
      language card and adds the HOME-JOURNEYS CSS block (assets/home_journeys.css) to global styles.
off : moves both journeys back to the end of the page (after the FAQ) and removes the CSS block.
      The snap script just skips .mlx-journeys when it exists, so the footer needs no change.

Usage: home_journeys_toggle.py on|off [--dry]
"""
import json, re, subprocess, sys, time, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
API = 'https://medluxlife-6j8sz55bpn.live-website.com/wp-json'
CSS_START, CSS_END = '/* >>> HOME-JOURNEYS START', '/* <<< HOME-JOURNEYS END */'
WRAP_OPEN = ('<!-- wp:group {"metadata":{"name":"Journeys (medical + travel)"},"align":"full","className":"mlx-journeys","layout":{"type":"default"}} -->\n'
             '<div class="wp-block-group alignfull mlx-journeys">')
WRAP_CLOSE = '</div>\n<!-- /wp:group -->'
TOK = re.compile(r'<!-- (/?)wp:([a-z0-9/-]+)(\s+\{.*?\})?\s*(/?)-->', re.S)


def api(method, path, body=None):
    cmd = ['curl', '-sS', '-X', method, API + path]
    if body is not None:
        cmd += ['-H', 'Content-Type: application/json', '--data-binary', '@-']
    out = subprocess.run(cmd, input=json.dumps(body).encode() if body is not None else None, capture_output=True, check=True).stdout
    return json.loads(out)


def top_blocks(raw):
    depth, start, blocks = 0, None, []
    for m in TOK.finditer(raw):
        closing, selfc = m.group(1), m.group(4)
        if selfc:
            if depth == 0:
                blocks.append(raw[m.start():m.end()])
            continue
        if not closing:
            if depth == 0:
                start = m.start()
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                blocks.append(raw[start:m.end()])
    return blocks


def is_journey(b):
    head = b[:400]
    return ('"name":"Features"' in head and 'Your Medical Journey' in b) or '"name":"Travel Journey"' in head


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ''
    dry = '--dry' in sys.argv
    if mode not in ('on', 'off'):
        sys.exit(__doc__)
    stamp = time.strftime('%Y%m%d_%H%M%S')
    page = api('GET', '/wp/v2/pages/23?context=edit')
    gs = api('GET', '/wp/v2/global-styles/5?context=edit')
    if not dry:
        bk = ROOT / 'backups' / 'wp'
        (bk / f'page23_before_journeys_{mode}_{stamp}.json').write_text(json.dumps(page))
        (bk / f'gs5_before_journeys_{mode}_{stamp}.json').write_text(json.dumps(gs))
    raw, css = page['content']['raw'], gs['styles']['css']
    blocks = top_blocks(raw)
    wrapped = [b for b in blocks if 'mlx-journeys' in b[:300]]
    if mode == 'off':
        if wrapped:
            w = wrapped[0]
            inner = w[len(WRAP_OPEN):-len(WRAP_CLOSE)]
            rest = [b for b in blocks if b is not w]
            raw = '\n\n'.join(rest + top_blocks(inner))
        css = re.sub(r'\n*' + re.escape(CSS_START) + r'.*?' + re.escape(CSS_END) + r'\n?', '\n', css, flags=re.S).rstrip() + '\n'
    else:
        if not wrapped:
            jour = [b for b in blocks if is_journey(b)]
            assert len(jour) == 2, 'journey sections not found'
            rest = [b for b in blocks if b not in jour]
            band = next(i for i, b in enumerate(rest) if 'mlx-lang2' in b)
            rest.insert(band + 1, WRAP_OPEN + '\n\n'.join(jour) + WRAP_CLOSE)
            raw = '\n\n'.join(rest)
        if CSS_START not in css:
            css = css.rstrip() + '\n\n' + (ROOT / 'assets' / 'home_journeys.css').read_text()
    if dry:
        print('dry run; page length', len(page['content']['raw']), '->', len(raw), '| css has block:', CSS_START in css)
        return raw
    r1 = api('POST', '/wp/v2/pages/23', {'content': raw})
    st = gs['styles']; st['css'] = css
    r2 = api('POST', '/wp/v2/global-styles/5', {'styles': st, 'settings': gs['settings']})
    print(mode, '| page wrapped:', 'mlx-journeys' in r1['content']['raw'], '| css block:', CSS_START in r2['styles']['css'])


if __name__ == '__main__':
    main()
