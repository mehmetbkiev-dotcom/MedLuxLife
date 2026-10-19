#!/usr/bin/env python3
"""Switch a marked CSS block in global styles on or off.

A block looks like  /* >>> NAME START ... */ ... /* <<< NAME END */  and its source is a file in assets/.
  on  : appends the file to global styles (if the block is not there yet)
  off : removes the block
Backups go to backups/wp/gs5_before_<name>_<on|off>_<time>.json.

Usage: css_block_toggle.py NAME on|off [assets/file.css]
Known blocks: LANG-SLIM (assets/home_lang_slim.css), HERO-LANG (assets/home_hero_lang.css), HOME-JOURNEYS (assets/home_journeys.css),
              ELEVATE-FIT (assets/home_elevate_fit.css)
"""
import json, re, subprocess, sys, time, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
API = 'https://medluxlife-6j8sz55bpn.live-website.com/wp-json/wp/v2/global-styles/5'
FILES = {'HERO-2026': 'assets/home_hero_2026.css', 'LANG-SLIM': 'assets/home_lang_slim.css', 'HERO-LANG': 'assets/home_hero_lang.css', 'HOME-JOURNEYS': 'assets/home_journeys.css', 'ELEVATE-FIT': 'assets/home_elevate_fit.css', 'LANG-MOBILE': 'assets/lang_switcher_mobile.css', 'CARD-HOVER': 'assets/card_hover.css', 'CHAT-DARK': 'assets/chat_dark.css', 'ABOUT-2026': 'assets/about_2026.css', 'TRAVEL-SUB': 'assets/travel_sub.css', 'JUSTIFY-TEXT': 'assets/justify_text.css', 'TREATMENT-DETAIL': 'assets/treatment_detail.css', 'FAQ-SIZE': 'assets/faq_size.css', 'HOME-JOURNEYS-CHAT': 'assets/home_journeys_chat.css', 'INTRO-CENTER': 'assets/home_intro_center.css', 'LANG-ALIGN': 'assets/lang_align.css'}


def main():
    if len(sys.argv) < 3 or sys.argv[2] not in ('on', 'off'):
        sys.exit(__doc__)
    name, mode = sys.argv[1], sys.argv[2]
    src = ROOT / (sys.argv[3] if len(sys.argv) > 3 else FILES.get(name, ''))
    gs = json.loads(subprocess.run(['curl', '-sS', API + '?context=edit'], capture_output=True, check=True).stdout)
    stamp = time.strftime('%Y%m%d_%H%M%S')
    (ROOT / 'backups' / 'wp' / f'gs5_before_{name.lower()}_{mode}_{stamp}.json').write_text(json.dumps(gs))
    css = gs['styles']['css']
    start, end = f'/* >>> {name} START', f'/* <<< {name} END */'
    if mode == 'off':
        css = re.sub(r'\n*' + re.escape(start) + r'.*?' + re.escape(end) + r'\n?', '\n', css, flags=re.S).rstrip() + '\n'
    elif start not in css:
        css = css.rstrip() + '\n\n' + src.read_text()
    st = gs['styles']; st['css'] = css
    body = json.dumps({'styles': st, 'settings': gs['settings']}).encode()
    out = subprocess.run(['curl', '-sS', '-X', 'POST', API, '-H', 'Content-Type: application/json', '--data-binary', '@-'], input=body, capture_output=True, check=True).stdout
    print(name, mode, '| block present now:', start in json.loads(out)['styles']['css'])


if __name__ == '__main__':
    main()
