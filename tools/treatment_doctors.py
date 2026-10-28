#!/usr/bin/env python3
"""Doctors on the treatment pages (Anna 2026-10-28: like on celyxmed.com – the treatment page shows the doctor who performs it;
a click opens the doctor's page). Section "Who performs this treatment" (up to 3 doctors: a large block each – photo, education, specialisation,
experience, areas of interest, link to the full profile; hospital departments: "Doctors in this department" with cards)
right before the "How it works with MedLuxLife" / "How MedLuxLife supports you" section; cards = the same cards as the doctor lists.

Clinic pages (Celyxmed): who does what as celyxmed.com names it on its treatment pages – plastic surgery and hair transplant:
Op. Dr. Kemal Aytuğlu (+ Dr. Cüneyt Çavdar, hair transplant coordinator); dental: Dr. Dt. Fikri Can Ayık (+ the dentists of the
specialty); medical aesthetics: Dr. Damla Erdoğan. Hospital department pages (Yeditepe): the doctors whose department has the
page's name (max. 8, then a link to the filtered doctor list). Pages without a matching doctor get no section.
usage: treatment_doctors.py [--dry] [--only ID,ID]"""
import html, json, pathlib, re, subprocess, sys, time
ROOT = pathlib.Path(__file__).resolve().parent.parent
API = 'https://medluxlife-6j8sz55bpn.live-website.com/wp-json/wp/v2/pages'
SITE = 'https://medluxlife.de'
DOCS = json.load(open(ROOT / 'content/partners/doctors.json'))
BY = {(d['partner'], d['slug']): d for d in DOCS}
sys.path.insert(0, str(ROOT / 'tools'))
from build_partners import TITLE, RANK, doctor_url, slug, E  # noqa: E402

DENT_ALL = ['fikri-can-ayik', 'oguzhan-tunc', 'busra-betul-ozturk', 'selin-guzel', 'elif-nil-ada']
CLINIC = [  # (path below /health/clinical-treatments/, Celyxmed doctor slugs) – longest match wins
    ('plastic-surgery', ['kemal-aytuglu']),
    ('hair-transplantation', ['kemal-aytuglu', 'cuneyt-cavdar']),
    ('dental-and-oral-health', DENT_ALL),
    ('dental-and-oral-health/dental-implants', ['fikri-can-ayik', 'oguzhan-tunc']),
    ('dental-and-oral-health/all-on-4-and-all-on-6', ['fikri-can-ayik', 'oguzhan-tunc']),
    ('dental-and-oral-health/hollywood-smile', ['fikri-can-ayik', 'busra-betul-ozturk', 'selin-guzel']),
    ('dental-and-oral-health/zirconium-veneers', ['fikri-can-ayik', 'busra-betul-ozturk', 'selin-guzel']),
    ('dental-and-oral-health/teeth-whitening', ['fikri-can-ayik', 'elif-nil-ada']),
    ('medical-aesthetics', ['damla-erdogan']),
]
MAX = 8


def card(d):
    t = TITLE.get(d['title'], '')
    return ('<li class="mlx-doc"><a class="mlx-doc-a" href="%s"><span class="mlx-doc-photo"><img src="%s" alt="%s" width="320" height="400" loading="lazy" decoding="async"></span>'
            '<span class="mlx-doc-body">%s<span class="mlx-doc-name">%s</span><span class="mlx-doc-depts">%s</span></span></a></li>'
            % (doctor_url(d), d['photo_url'], E((t + ' ' + d['name']).strip(), True), '<span class="mlx-doc-title">%s</span>' % t if t else '',
               E(d['name']), ''.join('<span>%s</span>' % E(n) for n in d['depts'])))


PLACE = {'celyxmed': 'Celyxmed · Ataşehir, Istanbul'}


def profile(d):
    """large block: photo left, who the doctor is + education, specialisation, experience, areas of interest right (Anna 2026-10-28)"""
    t = TITLE.get(d['title'], '')
    rows = []
    for k, label in (('edu', 'Education'), ('spec', 'Specialisation')):
        if d.get(k):
            rows.append('<div class="mlx-tp-row"><h4>%s</h4><p>%s</p></div>' % (label, E(d[k])))
    if d.get('career'):
        rows.append('<div class="mlx-tp-row"><h4>Experience</h4><ul>%s</ul></div>' % ''.join('<li>%s</li>' % E(c) for c in d['career'][:4]))
    if d.get('interests'):
        rows.append('<div class="mlx-tp-row"><h4>Areas of interest</h4><ul class="mlx-doc-tags">%s</ul></div>' % ''.join('<li>%s</li>' % E(i) for i in d['interests'][:8]))
    url = doctor_url(d)
    return ('<article class="mlx-tp"><a class="mlx-tp-photo" href="%s"><img src="%s" alt="%s" width="320" height="400" loading="lazy" decoding="async"></a>'
            '<div class="mlx-tp-info">%s<h3 class="mlx-tp-name"><a href="%s">%s</a></h3><p class="mlx-tp-depts">%s</p>%s%s'
            '<p class="mlx-tp-more"><a href="%s">Full profile →</a></p></div></article>'
            % (url, d['photo_url'], E((t + ' ' + d['name']).strip(), True), '<p class="mlx-tp-title">%s</p>' % t if t else '', url, E(d['name']),
               ''.join('<span>%s</span>' % E(n) for n in d['depts']), '<p class="mlx-tp-place">%s</p>' % PLACE[d['partner']] if d['partner'] in PLACE else '',
               ''.join(rows), url))


def section(docs, heading, more=None, big=False):
    if big:
        cards = '<div class="mlx-treat-profiles">%s</div>' % ''.join(profile(d) for d in docs)
    else:
        cards = '<div class="mlx-treat-docs"><ul class="mlx-doc-grid">%s</ul>%s</div>' % (
            ''.join(card(d) for d in docs), '<p class="mlx-treat-docs-more"><a href="%s">%s</a></p>' % more if more else '')
    return ('<!-- wp:group {"className":"medlux-section medlux-treatment-doctors","layout":{"type":"constrained"}} -->\n'
            '<div class="wp-block-group medlux-section medlux-treatment-doctors"><!-- wp:heading -->\n<h2 class="wp-block-heading">%s</h2>\n<!-- /wp:heading -->\n\n'
            '<!-- wp:paragraph {"className":"medlux-treatment-doctors-note"} -->\n<p class="medlux-treatment-doctors-note">Which doctor treats you is agreed during your consultation.</p>\n<!-- /wp:paragraph -->\n\n'
            '<!-- wp:html -->\n%s\n<!-- /wp:html --></div>\n<!-- /wp:group -->\n\n') % (heading, cards)


def doctors_for(page):
    path = page['link'].replace(SITE, '')
    m = re.match(r'^/health/clinical-treatments/(.+?)/?$', path)
    if m:
        best = [c for c in CLINIC if m.group(1) == c[0] or m.group(1).startswith(c[0] + '/')]
        if not best:
            return None
        slugs = max(best, key=lambda c: len(c[0]))[1]
        docs = [BY[('celyxmed', s)] for s in slugs]
        heading = 'Who performs these treatments' if '/' not in m.group(1) else 'Who performs this treatment'
        return section(docs, heading, big=len(docs) <= 3)
    m = re.match(r'^/health/hospital-specialist-treatments/[^/]+/?$', path)
    if m:
        title = html.unescape(page['title']['raw'])
        docs = [d for d in DOCS if d['partner'] == 'yeditepe' and title in d['depts']]
        if not docs:
            return None
        docs.sort(key=lambda d: (RANK.get(d['title'], 5), slug(d['name'])))
        more = None
        if len(docs) > MAX:
            more = (SITE + '/partners/yeditepe-university-hospitals/doctors/?dept=' + slug(title), 'All doctors in this department →')
        return section(docs[:MAX], 'Doctors in this department', more)
    return None


def strip_old(c):
    """remove an earlier doctors section (re-runs)"""
    i = c.find('<!-- wp:group {"className":"medlux-section medlux-treatment-doctors"')
    if i < 0:
        return c
    depth = 0
    for m in re.finditer(r'<!-- (/?)wp:group', c[i:]):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            end = i + m.end() + len(' -->')
            return c[:i] + c[end:].lstrip('\n')
    return c


def insert(c, sec):
    c = strip_old(c)
    k = c.find('<!-- wp:group {"className":"medlux-steps')
    if k < 0:
        k = c.find('<!-- wp:group {"className":"medlux-cta"')
        return c[:k] + sec + c[k:]
    s = c.rfind('<!-- wp:group {"className":"medlux-section"', 0, k)
    return c[:s] + sec + c[s:]


def main():
    dry = '--dry' in sys.argv
    only = {int(x) for x in sys.argv[sys.argv.index('--only') + 1].split(',')} if '--only' in sys.argv else None
    pages = []
    for n in (1, 2, 3, 4):
        r = json.loads(subprocess.run(['curl', '-sS', API + '?per_page=100&page=%d&context=edit&_fields=id,link,title,content' % n], capture_output=True).stdout)
        if not isinstance(r, list) or not r:
            break
        pages += r
    todo = []
    for p in pages:
        if only and p['id'] not in only:
            continue
        sec = doctors_for(p)
        if not sec:
            continue
        new = insert(p['content']['raw'], sec)
        if new != p['content']['raw']:
            todo.append((p, new))
    print(len(todo), 'pages')
    if dry:
        for p, _ in todo:
            print(' ', p['id'], p['link'].replace(SITE, ''))
        return
    json.dump([{'id': p['id'], 'content': p['content']['raw']} for p, _ in todo],
              open(ROOT / ('backups/wp/partners/pages_before_treatment_doctors_%s.json' % time.strftime('%Y%m%d_%H%M%S')), 'w'), ensure_ascii=False)
    for p, new in todo:
        r = json.loads(subprocess.run(['curl', '-sS', '-X', 'POST', API + '/%d' % p['id'], '-H', 'Content-Type: application/json', '--data-binary', '@-'],
                                      input=json.dumps({'content': new}).encode(), capture_output=True).stdout)
        print(p['id'], p['link'].replace(SITE, ''), 'ok' if r.get('id') == p['id'] else str(r)[:200])
    import cache_clear
    print('page cache cleared:', cache_clear.clear())


if __name__ == '__main__':
    main()
