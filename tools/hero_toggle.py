#!/usr/bin/env python3
"""Home banner: switch between the new banner (2026-10-15, media 1937 Bosphorus + pool, phone 1938, hero logo 1950; also tried 1929, 1935, 1948, 1954, 1958 baked-in). NOTE: 'old' does not switch the hero logo back (1950 -> 164) and the old one (media 1624).

new : page 23 cover uses medluxlife-home-hero-2026.jpg (focal 50%/45%, alt text) + CSS block HERO-2026
      (assets/home_hero_2026.css: readable slogan/buttons/logo, full first screen on desktop, phone crop 86%).
old : page 23 cover back to medluxlife-home-hero-hd.jpg (focal 50%/75%, 750 px) and the CSS block removed.
Backups of page 23 and global styles go to backups/wp/ before every switch.

Usage: hero_toggle.py new|old
"""
import json, re, subprocess, sys, time, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
API = 'https://medluxlife-6j8sz55bpn.live-website.com/wp-json'
UP = 'https://medluxlife.de/wp-content/uploads/2026/10/'
ALT = ('A patient and a doctor talk in a bright clinic lounge with a view of Istanbul; a golden world map, a plane in the sunset sky, '
       'the Bosphorus bridge, a pool terrace with palms, and small round photos of a smile check-up, a hair examination and a facial consultation')
OLD = {'file': 'medluxlife-home-hero-hd.jpg', 'id': 1624, 'fy': '0.75', 'pos': '50% 75%', 'alt': ''}
NEW = {'file': 'medluxlife-home-hero-2026q.jpg', 'id': 2019, 'fy': '0.1', 'pos': '50% 10%', 'alt': ALT}   # 2014 with the sky behind the world map warmed like Emrah's upload 2018; before: 2014
START, END = '/* >>> HERO-2026 START', '/* <<< HERO-2026 END */'


def api(method, path, body=None):
    cmd = ['curl', '-sS', '-X', method, API + path]
    if body is not None:
        cmd += ['-H', 'Content-Type: application/json', '--data-binary', '@-']
    return json.loads(subprocess.run(cmd, input=json.dumps(body).encode() if body is not None else None, capture_output=True, check=True).stdout)


def cover_attrs(c):
    alt = '"alt":"%s",' % c['alt'] if c['alt'] else ''
    return '{"url":"%s%s","id":%d,%s"focalPoint":{"x":0.5,"y":%s},' % (UP, c['file'], c['id'], alt, c['fy'])


def cover_img(c):
    return ('<img class="wp-block-cover__image-background wp-image-%d size-full" alt="%s" src="%s%s" style="object-position:%s" '
            'data-object-fit="cover" data-object-position="%s"/>' % (c['id'], c['alt'], UP, c['file'], c['pos'], c['pos']))


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ''
    if mode not in ('new', 'old'):
        sys.exit(__doc__)
    src, dst = (OLD, NEW) if mode == 'new' else (NEW, OLD)
    stamp = time.strftime('%Y%m%d_%H%M%S')
    page, gs = api('GET', '/wp/v2/pages/23?context=edit'), api('GET', '/wp/v2/global-styles/5?context=edit')
    bk = ROOT / 'backups' / 'wp'
    (bk / f'page23_before_hero_{mode}_{stamp}.json').write_text(json.dumps(page))
    (bk / f'gs5_before_hero_{mode}_{stamp}.json').write_text(json.dumps(gs))
    raw = page['content']['raw']
    if cover_attrs(src) in raw:
        raw = raw.replace(cover_attrs(src), cover_attrs(dst)).replace(cover_img(src), cover_img(dst))
    css = re.sub(r'\n*' + re.escape(START) + r'.*?' + re.escape(END) + r'\n?', '\n', gs['styles']['css'], flags=re.S).rstrip() + '\n'
    if mode == 'new':
        css += '\n' + (ROOT / 'assets' / 'home_hero_2026.css').read_text()
    r1 = api('POST', '/wp/v2/pages/23', {'content': raw})
    st = gs['styles']; st['css'] = css
    r2 = api('POST', '/wp/v2/global-styles/5', {'styles': st, 'settings': gs['settings']})
    print(mode, '| banner:', dst['file'] in r1['content']['raw'], '| css block:', START in r2['styles']['css'])


if __name__ == '__main__':
    main()
