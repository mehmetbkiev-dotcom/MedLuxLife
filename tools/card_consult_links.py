#!/usr/bin/env python3
"""Treatment cards without their own page get "Free consultation →" (class medlux-more medlux-ask) linking to the contact form.
The footer script (assets/contact_topic_prefill.js) fills the form with the card's treatment in the page language; with the
CARD-HOVER rules the whole card is clickable. Numbered step cards ("1. Free consultation" …) are left alone. Backup first.

Usage: card_consult_links.py PAGE_ID [PAGE_ID …] [--dry]
"""
import json, re, subprocess, sys, time, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
API = 'https://medluxlife-6j8sz55bpn.live-website.com/wp-json/wp/v2/pages/'
START = '<!-- wp:group {"className":"medlux-card'
END = '</div>\n<!-- /wp:group -->'
LINK = ('\n\n<!-- wp:paragraph {"className":"medlux-more medlux-ask"} -->\n'
        '<p class="medlux-more medlux-ask"><a href="https://medluxlife.de/contact/">Free consultation →</a></p>\n<!-- /wp:paragraph -->')


def curl(*a, data=None):
    return json.loads(subprocess.run(['curl', '-sS', *a], input=data, capture_output=True, check=True).stdout)


def main():
    ids = [int(a) for a in sys.argv[1:] if a.isdigit()]
    dry = '--dry' in sys.argv
    if not ids:
        sys.exit(__doc__)
    for pid in ids:
        page = curl(API + '%d?context=edit' % pid)
        if not dry:
            (ROOT / 'backups/wp' / ('page%d_before_consult_links_%s.json' % (pid, time.strftime('%Y%m%d_%H%M%S')))).write_text(json.dumps(page))
        parts = page['content']['raw'].split(START)
        out, done = [parts[0]], []
        for chunk in parts[1:]:
            card = chunk.split(END)[0]
            title = re.search(r'<h3 class="wp-block-heading">(.*?)</h3>', card)
            title = re.sub(r'<[^>]+>', '', title.group(1)) if title else ''
            if title and not re.match(r'^\d+\.', title) and 'medlux-more' not in card and '<a ' not in card:
                k = chunk.index(END)
                chunk = chunk[:k] + LINK + chunk[k:]
                done.append(title)
            out.append(chunk)
        if not dry and done:
            res = curl('-X', 'POST', API + str(pid), '-H', 'Content-Type: application/json', '--data-binary', '@-',
                       data=json.dumps({'content': START.join(out)}).encode())
            print(pid, 'saved', res.get('id'), '|', len(done), done)
        else:
            print(pid, 'dry' if dry else 'nothing to add', '|', len(done), done)


if __name__ == '__main__':
    main()
