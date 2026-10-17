#!/usr/bin/env python3
"""Polish a Travel subpage (2026-10-17, Anna): gold line icons on the "What we offer" cards,
"Good to know" as a framed note, big gold step numbers in "How it works".
Reads the backup backups/wp/page<ID>_before_travel_polish.json, writes content/travel_<ID>.html.
Usage: travel_polish.py ID [ID ...]   (then publish content/travel_<ID>.html to /wp/v2/pages/<ID>)"""
import json, re, sys, base64, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent

def svg(body):
    s = ('<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48" fill="none" stroke="#d4a24c" '
         'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' + body + '</svg>')
    return 'data:image/svg+xml;base64,' + base64.b64encode(s.encode()).decode()

# icons per card title (no crosses or plus signs)
ICONS = {
    'Seaside holidays': svg('<path d="M14 24a10 10 0 0 1 20 0"/><path d="M24 6v4M11 12l3 3M37 12l-3 3"/><path d="M4 32c4 0 4 3 8 3s4-3 8-3 4 3 8 3 4-3 8-3 4 3 8 3"/><path d="M4 40c4 0 4 3 8 3s4-3 8-3 4 3 8 3 4-3 8-3 4 3 8 3"/>'),
    'City breaks': svg('<path d="M4 42h40"/><path d="M8 42V22h8v20M16 42V10h10v32M26 42V18h8v24M34 42V26h6v16"/><path d="M19 16h4M19 22h4M19 28h4M29 24h2M29 30h2"/>'),
    'Wellness and spa holidays': svg('<path d="M24 9c5 6 5 14 0 23-5-9-5-17 0-23z"/><path d="M24 32c-8 0-14-5-16-12 7 0 12 4 16 12z"/><path d="M24 32c8 0 14-5 16-12-7 0-12 4-16 12z"/><path d="M10 39h28"/>'),
    'Family holidays': svg('<circle cx="17" cy="11" r="5"/><path d="M8 42V28a9 9 0 0 1 18 0v14"/><circle cx="34" cy="21" r="4"/><path d="M28 42v-9a6 6 0 0 1 12 0v9"/>'),
    'Group and special-occasion travel': svg('<path d="M10 6h10l-1 12a4 4 0 0 1-8 0z"/><path d="M15 22v14M10 36h10"/><path d="M28 10h10l-1 12a4 4 0 0 1-8 0z"/><path d="M33 26v12M28 38h10"/>'),
    'Excursions and tours': svg('<path d="M6 12l11-4 14 4 11-4v28l-11 4-14-4-11 4z"/><path d="M17 8v28M31 12v28"/>'),
}

def icon_block(uri):
    return ('<!-- wp:image {"className":"medlux-card-icon"} -->\n<figure class="wp-block-image medlux-card-icon"><img src="%s" alt=""/></figure>\n<!-- /wp:image -->\n\n' % uri)

def polish(pid):
    c = json.loads((ROOT / f'backups/wp/page{pid}_before_travel_polish.json').read_text())['content']['raw']
    # 1. icons on the "What we offer" cards
    n_icons = 0
    def add_icon(m):
        nonlocal n_icons
        title = m.group(2)
        if title in ICONS:
            n_icons += 1
            return m.group(1) + icon_block(ICONS[title]) + m.group(0)[len(m.group(1)):]
        return m.group(0)
    c = re.sub(r'(<div class="wp-block-group medlux-card">)<!-- wp:heading \{"level":3\} -->\n<h3 class="wp-block-heading">([^<]+)</h3>', add_icon, c)
    # 2. "Good to know" section gets its own class (framed note)
    c, n_note = re.subn(r'<!-- wp:group \{"className":"medlux-section","layout":\{"type":"constrained"\}\} -->\n<div class="wp-block-group medlux-section">(<!-- wp:heading -->\n<h2 class="wp-block-heading">Good to know</h2>)',
                        r'<!-- wp:group {"className":"medlux-section medlux-good-to-know","layout":{"type":"constrained"}} -->\n<div class="wp-block-group medlux-section medlux-good-to-know">\1', c)
    # 3. step numbers as big gold numerals
    c, n_steps = re.subn(r'<h3 class="wp-block-heading">([1-4])\. ([^<]+)</h3>', r'<h3 class="wp-block-heading"><span class="medlux-step-no">\1</span>\2</h3>', c)
    (ROOT / f'content/travel_{pid}.html').write_text(c)
    print(pid, 'icons', n_icons, 'note', n_note, 'steps', n_steps)

for a in sys.argv[1:]:
    polish(int(a))
