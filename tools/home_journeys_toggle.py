#!/usr/bin/env python3
"""Home page 2nd screen: language card + both journeys (on) or the old order (off).

on  : puts the language card + "Your Medical Journey" + "Travel Journey" in one group (div.mlx-journeys)
      where the language card was, and adds the HOME-JOURNEYS CSS block (assets/home_journeys.css) to
      global styles. On desktop that group is one screen: card on top, journeys side by side, centred.
off : language card back on its own after the banner, both journeys back to the end of the page (after
      the FAQ), CSS block removed. The snap script needs no change either way. The "Elevate" block
      (ELEVATE-FIT) is separate and stays.

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
            inner = top_blocks(w[len(WRAP_OPEN):-len(WRAP_CLOSE)])
            band = [b for b in inner if 'mlx-lang2' in b[:200]]
            jour = [b for b in inner if b not in band]
            i = blocks.index(w)
            raw = '\n\n'.join(blocks[:i] + band + blocks[i + 1:] + jour)
        css = re.sub(r'\n*' + re.escape(CSS_START) + r'.*?' + re.escape(CSS_END) + r'\n?', '\n', css, flags=re.S).rstrip() + '\n'
    else:
        if not wrapped:
            jour = [b for b in blocks if is_journey(b)]
            assert len(jour) == 2, 'journey sections not found'
            rest = [b for b in blocks if b not in jour]
            bi = next(i for i, b in enumerate(rest) if 'mlx-lang2' in b[:200])
            rest[bi] = WRAP_OPEN + '\n\n'.join([rest[bi]] + jour) + WRAP_CLOSE
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
