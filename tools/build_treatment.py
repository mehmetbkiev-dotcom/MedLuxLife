#!/usr/bin/env python3
"""Treatment detail pages from a spec module, same layout as the approved Mommy Makeover page (tools/build_mommy.py, Anna 2026-10-18).

Usage: build_treatment.py plastic            -> writes content/treatments/<slug>.html for every spec in content/treatments/plastic.py
       build_treatment.py plastic --deploy   -> also creates/updates the pages (child pages of the spec's PARENT, template page-with-title);
                                                page IDs are kept in content/treatments/pages.json, backups in backups/wp/
       build_treatment.py plastic --links    -> adds "Learn more →" (medlux-more) to the parent page's cards that have a detail page (backup first)
       build_treatment.py --icons            -> rewrites the banner icon rules (one gold icon per treatment page, Anna 2026-10-18) in
                                                assets/treatment_detail.css from pages.json + icons.json (icons: tools/make_treatment_icons.py);
                                                then switch TREATMENT-DETAIL off/on with tools/css_block_toggle.py
Texts are general information in our own words; no clinic/doctor names, no before/after, no prices, no promises (HWG)."""
import base64, importlib.util, json, pathlib, re, subprocess, sys, time
ROOT = pathlib.Path(__file__).resolve().parent.parent
API = 'https://medluxlife-6j8sz55bpn.live-website.com/wp-json/wp/v2/pages'


def svg(body):
    s = ('<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48" fill="none" stroke="#d4a24c" '
         'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' + body + '</svg>')
    return 'data:image/svg+xml;base64,' + base64.b64encode(s.encode()).decode()

ICON = {
    'tummy': svg('<path d="M16 6c0 8 6 12 6 18s-6 10-6 18"/><path d="M32 6c0 8-6 12-6 18s6 10 6 18"/>'),
    'lift': svg('<circle cx="24" cy="24" r="18"/><path d="M24 33V15M17 21l7-7 7 7"/>'),
    'lipo': svg('<path d="M24 6s-12 14-12 22a12 12 0 0 0 24 0C36 20 24 6 24 6z"/>'),
    'lotus': svg('<path d="M24 9c5 6 5 14 0 23-5-9-5-17 0-23z"/><path d="M24 32c-8 0-14-5-16-12 7 0 12 4 16 12z"/><path d="M24 32c8 0 14-5 16-12-7 0-12 4-16 12z"/><path d="M10 39h28"/>'),
    'consult': svg('<circle cx="20" cy="18" r="8"/><path d="M4 42c0-8.8 7.2-15 16-15s16 6.2 16 15"/><path d="M31 4h13a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2h-8l-4 3v-3h-1a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z"/>'),
    'moon': svg('<g transform="rotate(-45 24 24)"><path d="M3 24h9"/><rect x="12" y="19" width="21" height="10" rx="2"/><path d="M17 19v4M22 19v4M27 19v4"/><path d="M33 24h7"/><path d="M40 18v12"/></g>'),
    'combine': svg('<circle cx="18" cy="19" r="10"/><circle cx="30" cy="19" r="10"/><circle cx="24" cy="30" r="10"/>'),
    'care': svg('<path d="M24 41S6 30.5 6 17.5A9.5 9.5 0 0 1 24 12a9.5 9.5 0 0 1 18 5.5C42 30.5 24 41 24 41z"/>'),
    'bed': svg('<path d="M4 38V12"/><path d="M4 30h40v8"/><path d="M44 38V26a6 6 0 0 0-6-6H20v10"/><circle cx="12" cy="24" r="4"/>'),
    'calendar': svg('<rect x="6" y="10" width="36" height="32" rx="3"/><path d="M6 20h36M16 6v8M32 6v8"/><path d="M14 28h4M22 28h4M30 28h4M14 35h4M22 35h4"/>'),
    'hourglass': svg('<path d="M14 6h20M14 42h20"/><path d="M16 6c0 9 8 12 8 18s-8 9-8 18"/><path d="M32 6c0 9-8 12-8 18s8 9 8 18"/>'),
    'pin': svg('<path d="M24 44s14-13 14-24a14 14 0 0 0-28 0c0 11 14 24 14 24z"/><circle cx="24" cy="20" r="5"/>'),
    'clock': svg('<circle cx="24" cy="24" r="18"/><path d="M24 13v11l7 5"/>'),
    'gem': svg('<path d="M14 9h20l8 10-18 21L6 19z"/><path d="M6 19h36"/><path d="M18 9l-2 10 8 21 8-21-2-10"/>'),
    'breath': svg('<path d="M6 17h22a5 5 0 1 0-5-5"/><path d="M6 25h32a5 5 0 1 1-5 5"/><path d="M6 33h16"/>'),
    'eye': svg('<path d="M4 24s7-11 20-11 20 11 20 11-7 11-20 11S4 24 4 24z"/><circle cx="24" cy="24" r="5"/>'),
    'face': svg('<path d="M24 6c-8 0-13 6-13 15 0 10 6 21 13 21s13-11 13-21c0-9-5-15-13-15z"/><path d="M19 33c3 2 7 2 10 0"/>'),
    'implant': svg('<path d="M8 34c0-11 7-19 16-19s16 8 16 19z"/>'),
}


def p(t, cls=None):
    if cls:
        return '<!-- wp:paragraph {"className":"%s"} -->\n<p class="%s">%s</p>\n<!-- /wp:paragraph -->' % (cls, cls, t)
    return '<!-- wp:paragraph -->\n<p>%s</p>\n<!-- /wp:paragraph -->' % t

def h(t, lvl=2):
    if lvl == 2:
        return '<!-- wp:heading -->\n<h2 class="wp-block-heading">%s</h2>\n<!-- /wp:heading -->' % t
    return '<!-- wp:heading {"level":%d} -->\n<h%d class="wp-block-heading">%s</h%d>\n<!-- /wp:heading -->' % (lvl, lvl, t, lvl)

def ul(items, cls=None):
    lis = '\n'.join('<!-- wp:list-item -->\n<li>%s</li>\n<!-- /wp:list-item -->' % i for i in items)
    if cls:
        return '<!-- wp:list {"className":"%s"} -->\n<ul class="wp-block-list %s">%s</ul>\n<!-- /wp:list -->' % (cls, cls, lis)
    return '<!-- wp:list -->\n<ul class="wp-block-list">%s</ul>\n<!-- /wp:list -->' % lis

def group(cls, inner, layout='{"type":"constrained"}'):
    return ('<!-- wp:group {"className":"%s","layout":%s} -->\n<div class="wp-block-group %s">%s</div>\n<!-- /wp:group -->'
            % (cls, layout, cls, '\n\n'.join(inner)))

def icon(name):
    return ('<!-- wp:image {"className":"medlux-card-icon"} -->\n<figure class="wp-block-image medlux-card-icon"><img src="%s" alt=""/></figure>\n<!-- /wp:image -->' % ICON[name])

def faq(items):
    out = []
    for q, a in items:
        out.append('<!-- wp:accordion-item {"style":{"spacing":{"blockGap":"0"}}} -->\n<div class="wp-block-accordion-item"><!-- wp:accordion-heading -->\n'
                   '<h3 class="wp-block-accordion-heading"><button type="button" class="wp-block-accordion-heading__toggle"><span class="wp-block-accordion-heading__toggle-title">%s</span><span class="wp-block-accordion-heading__toggle-icon" aria-hidden="true">+</span></button></h3>\n'
                   '<!-- /wp:accordion-heading -->\n\n<!-- wp:accordion-panel -->\n<div role="region" class="wp-block-accordion-panel">%s</div>\n<!-- /wp:accordion-panel --></div>\n<!-- /wp:accordion-item -->' % (q, p(a)))
    return ('<!-- wp:accordion {"className":"medlux-faq","style":{"spacing":{"blockGap":"var:preset|spacing|20"}},"layout":{"type":"default"}} -->\n'
            '<div role="group" class="wp-block-accordion medlux-faq">%s</div>\n<!-- /wp:accordion -->' % '\n\n'.join(out))

def fact(ic, label, value):
    return group('medlux-fact', [icon(ic), p(label, 'medlux-fact-label'), p(value, 'medlux-fact-value')])

def step(n, title, text):
    return group('medlux-card', [h('<span class="medlux-step-no">%d</span>%s' % (n, title), 3), p(text)])

def cards(cls, items):
    return group(('medlux-treatment-grid medlux-centered-cards ' + cls).strip(), items, '{"type":"grid","minimumColumnWidth":"14rem"}')


# wording per treatment group; a spec module may override any of these in VOCAB (e.g. dentist instead of surgeon)
VOCAB = {
    'doctor': 'surgeon',
    'proc_title': 'How the operation is performed',
    'suitable_note': 'Whether the procedure is suitable for you is decided by the {doctor} after a personal assessment.',
    'step3_title': 'Arrival and surgery',
    'step3_lead': 'After a pre-operative examination, the operation takes place as planned. ',
    'step4_title': 'Recovery in Istanbul',
    'step4': 'You rest in your hotel and attend the check-ups at the clinic. The {doctor} decides when you are ready to fly home.',
    'docs': 'No. If the {doctor} needs photos or documents, you share them directly with the doctor in your online consultation.',
    'recovery_title': 'Recovery step by step',
}


def build(t, card, stages, vocab=None):
    v = dict(VOCAB, **(vocab or {}))
    v = {k: val.format(doctor=v['doctor']) for k, val in v.items()}
    intro = ('<!-- wp:columns {"verticalAlignment":"center","className":"medlux-intro"} -->\n<div class="wp-block-columns are-vertically-aligned-center medlux-intro">'
             '<!-- wp:column {"verticalAlignment":"center"} -->\n<div class="wp-block-column is-vertically-aligned-center">'
             + p(t['intro'], 'medlux-lead')
             + '</div>\n<!-- /wp:column -->\n\n<!-- wp:column {"verticalAlignment":"center"} -->\n<div class="wp-block-column is-vertically-aligned-center">'
             '<!-- wp:image {"id":%d,"sizeSlug":"large","linkDestination":"none","className":"medlux-intro-img"} -->\n'
             '<figure class="wp-block-image size-large medlux-intro-img"><img src="%s" alt="%s" class="wp-image-%d"/></figure>\n<!-- /wp:image -->'
             '</div>\n<!-- /wp:column --></div>\n<!-- /wp:columns -->') % (card['img_id'], card['img'], card['alt'], card['img_id'])

    facts = group('medlux-section medlux-facts-sec', [
        h('Quick facts'),
        group('medlux-facts', [fact(*f) for f in t['facts']], '{"type":"default"}'),
        p('General information; your %s plans the details for you personally.' % v['doctor'], 'medlux-facts-note'),
    ])

    suitable = group('medlux-section medlux-suitable', [
        h('Who it may be suitable for'),
        ul(t['suitable'], 'medlux-checklist'),
        p(t.get('note', v['suitable_note']), 'medlux-suitable-note'),
    ])

    sections = [intro, facts, suitable]
    if t['options']:
        n = len(t['options'])
        sections.append(group('medlux-section', [
            h(t.get('options_title', 'What it can include')),
            cards('medlux-cols-%d' % n if n < 4 else '', [group('medlux-card', [icon(ic), h(title, 3), p(text)]) for ic, title, text in t['options']]),
        ]))

    sections.append(group('medlux-section', [
        h(v['proc_title']),
        cards('medlux-stages', [group('medlux-card', [icon(ic), h(title, 3), p(text)]) for ic, title, text in stages]),
    ]))

    sections.append(group('medlux-section', [
        h('How it works with MedLuxLife'),
        group('medlux-steps medlux-steps--list', [
            step(1, 'Contact and online consultation', 'Contact us and tell us what you are interested in. We refer you to the right %s for an online consultation. Photos or medical documents go directly to the doctor, only on request.' % v['doctor']),
            step(2, 'Your personal plan', 'The %s recommends the right approach for you. We plan your dates, flights, hotel and transfers around it.' % v['doctor']),
            step(3, v['step3_title'], v['step3_lead'] + t['hospital']),
            step(4, v['step4_title'], v['step4']),
            step(5, 'Back home', 'Stay in touch with us on WhatsApp – we help with follow-up questions.'),
        ], '{"type":"default"}'),
    ]))

    sections.append(group('medlux-section', [
        h(t.get('recovery_title', v['recovery_title'])),
        cards('medlux-timeline', [group('medlux-card', [p(label, 'medlux-time-label'), p(text)]) for label, text in t['recovery']]),
    ]))

    sections.append(group('medlux-section', [
        h('Frequently asked questions'),
        faq(t['faq'] + ([] if t.get('no_stay_faq') else [
            ('How long should I stay in Türkiye?', 'This is planned individually with the clinic. We organise your flights and hotel accordingly.')]) + [
            ('Should I send photos or medical documents to MedLuxLife?', v['docs']),
        ]),
    ]))

    sections.append(group('medlux-cta', [
        h('Plan your %s' % t['short']),
        p('Contact us and tell us what you are interested in – we refer you to the right specialist for an online consultation.'),
        '<!-- wp:buttons -->\n<div class="wp-block-buttons"><!-- wp:button {"className":"medlux-btn-primary"} -->\n'
        '<div class="wp-block-button medlux-btn-primary"><a class="wp-block-button__link wp-element-button" href="https://medluxlife.de/contact/">Request a Free Consultation</a></div>\n'
        '<!-- /wp:button -->\n\n<!-- wp:button {"className":"medlux-btn-whatsapp"} -->\n'
        '<div class="wp-block-button medlux-btn-whatsapp"><a class="wp-block-button__link wp-element-button" href="https://wa.me/380979092326" target="_blank" rel="noreferrer noopener">WhatsApp</a></div>\n'
        '<!-- /wp:button --></div>\n<!-- /wp:buttons -->',
        p('The information on this page is for general guidance only and does not replace a medical consultation. Suitability for any treatment is assessed individually by a qualified doctor.', 'medlux-disclaimer'),
    ]))
    return '\n\n'.join(sections) + '\n'


def curl(*args, data=None):
    out = subprocess.run(['curl', '-sS', *args], input=data, capture_output=True, check=True).stdout
    return json.loads(out)


def icon_css():
    ids = json.loads((ROOT / 'content/treatments/pages.json').read_text())
    icons = json.loads((ROOT / 'content/treatments/icons.json').read_text())
    rules = ['body.page-id-%d main > .ext-hero-section .wp-block-cover::before { background-image: url("%s") !important; }' % (ids[slug], icons[slug]['url'])
             for slug in sorted(icons) if slug in ids]
    css_file = ROOT / 'assets/treatment_detail.css'
    css = css_file.read_text()
    start, end = '/* banner icon per treatment page (generated by tools/build_treatment.py --icons) */\n', '/* end of banner icons */\n'
    block = start + '\n'.join(rules) + '\n' + end
    if start in css:
        css = css[:css.index(start)] + block + css[css.index(end) + len(end):]
    else:
        css = css.replace('/* <<< TREATMENT-DETAIL END */', block + '/* <<< TREATMENT-DETAIL END */')
    css_file.write_text(css)
    print(len(rules), 'icon rules')


def add_links(mod):
    url = API + '/%d' % mod.PARENT
    page = curl(url + '?context=edit')
    (ROOT / 'backups/wp' / ('page%d_before_links_%s.json' % (mod.PARENT, time.strftime('%Y%m%d_%H%M%S')))).write_text(json.dumps(page))
    base = page['link'].replace('https://medluxlife-6j8sz55bpn.live-website.com', 'https://medluxlife.de')
    link = {t['card']: base + t['slug'] + '/' for t in mod.TREATMENTS}
    start = '<!-- wp:group {"className":"medlux-card'
    end = '</div>\n<!-- /wp:group -->'
    parts = page['content']['raw'].split(start)
    out, done, had = [parts[0]], [], []
    for chunk in parts[1:]:
        title = re.search(r'<h3 class="wp-block-heading">(.*?)</h3>', chunk.split(end)[0])
        title = title.group(1) if title else None
        if title in link and 'medlux-more' in chunk.split(end)[0]:
            had.append(title)
        elif title in link:
            k = chunk.index(end)
            chunk = (chunk[:k] + '\n\n<!-- wp:paragraph {"className":"medlux-more"} -->\n<p class="medlux-more"><a href="%s">Learn more →</a></p>\n'
                     '<!-- /wp:paragraph -->' % link[title] + chunk[k:])
            done.append(title)
        out.append(chunk)
    res = curl('-X', 'POST', url, '-H', 'Content-Type: application/json', '--data-binary', '@-', data=json.dumps({'content': start.join(out)}).encode())
    print('links added:', done, '| already linked:', len(had), '| card not found:', [k for k in link if k not in done + had], '| page', res.get('id'))


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    if sys.argv[1] == '--icons':
        return icon_css()
    group_name, deploy = sys.argv[1], '--deploy' in sys.argv
    spec = importlib.util.spec_from_file_location(group_name, ROOT / 'content/treatments' / (group_name + '.py'))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    if '--links' in sys.argv:
        return add_links(mod)
    cards_data = json.loads((ROOT / 'content/treatments' / (group_name + '_cards.json')).read_text())
    ids_file = ROOT / 'content/treatments/pages.json'
    ids = json.loads(ids_file.read_text()) if ids_file.exists() else {}
    for t in mod.TREATMENTS:
        html = build(t, cards_data[t['card']], mod.STAGES[t['slug']], getattr(mod, 'VOCAB', None))
        (ROOT / 'content/treatments' / (t['slug'] + '.html')).write_text(html)
        if not deploy:
            print('written', t['slug'], len(html)); continue
        body = {'title': t['title'], 'slug': t['slug'], 'content': html, 'status': 'publish', 'parent': mod.PARENT, 'template': 'page-with-title'}
        if t['slug'] in ids:
            pid = ids[t['slug']]
            old = curl(API + '/%d?context=edit' % pid)
            (ROOT / 'backups/wp' / ('page%d_before_build_%s.json' % (pid, time.strftime('%Y%m%d_%H%M%S')))).write_text(json.dumps(old))
            res = curl('-X', 'POST', API + '/%d' % pid, '-H', 'Content-Type: application/json', '--data-binary', '@-', data=json.dumps(body).encode())
        else:
            res = curl('-X', 'POST', API, '-H', 'Content-Type: application/json', '--data-binary', '@-', data=json.dumps(body).encode())
            ids[t['slug']] = res['id']
            ids_file.write_text(json.dumps(ids, indent=1) + '\n')
        print(t['slug'], res.get('id'), res.get('status'), res.get('link'))


if __name__ == '__main__':
    main()
