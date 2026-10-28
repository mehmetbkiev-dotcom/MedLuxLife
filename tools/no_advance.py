#!/usr/bin/env python3
"""Anna 2026-10-28: "no advance payment" everywhere – the consultation is free, there is no advance payment and no deposit, the patient pays
the clinic or hospital directly in Istanbul, only after signing the treatment documents there (flight tickets are enough to confirm the dates).
The home page stays unchanged (Anna: she will think about the home page herself).

  - a gold-framed line in every call-to-action box (medlux-cta) of the health, partner, doctor and About us pages – not on the travel pages
  - FAQ: "Do I have to pay in advance for my treatment?" as the first question with a gold tick (class mlx-faq-nopay, CSS block NO-ADVANCE)
    on the 25 clinical treatment pages (new there) and on the contact page (moved to the top, new answer)
  - Partners overview (2916): the payment card says when you pay
  - contact page: both FAQ columns with 7 questions (Anna 2026-10-28: the same number left and right; one new question about a companion)
apply() is idempotent; build_partners.py and build_treatment.py call it, so rebuilt pages keep the line and the FAQ.
Backups in backups/wp/nopay/. usage: no_advance.py [--dry]"""
import json, pathlib, re, subprocess, sys, time
ROOT = pathlib.Path(__file__).resolve().parent.parent
W = 'https://medluxlife-6j8sz55bpn.live-website.com/wp-json/wp/v2/pages/'
SITE = 'https://medluxlife.de'

LEAD = 'No advance payment:'
LINE = 'you pay for your treatment directly at the clinic or hospital – only once you are in Istanbul and have signed the treatment documents there.'
NOPAY_P = ('<!-- wp:paragraph {"className":"medlux-nopay"} -->\n<p class="medlux-nopay"><span><strong>%s</strong> %s</span></p>\n<!-- /wp:paragraph -->\n\n'
           % (LEAD, LINE))
Q = 'Do I have to pay in advance for my treatment?'
A = ('No. Your consultation is free of charge, and you make no advance payment and pay no deposit for your treatment – neither to MedLuxLife nor to the clinic '
     'or hospital. The money for your treatment stays with you until you have arrived in Istanbul and signed the treatment documents with the clinic or '
     'hospital; only then do you pay for your treatment, directly on site. To confirm your dates, it is enough to show the clinic your flight tickets – '
     'whether you buy them yourself or we arrange them for you.')
HUB_OLD = 'MedLuxLife does not take any advance payment for treatments. You pay for your treatment directly at the clinic or hospital.'
HUB_NEW = ('MedLuxLife does not take any advance payment for treatments. You pay for your treatment directly at the clinic or hospital – only once you are in '
           'Istanbul and have signed the treatment documents there.')
HOME, CONTACT, HUB = 23, 26, 2916
COMPANION = ('Can someone accompany me?',
             'Yes. For clinic treatments, accommodation at the five-star Dedeman Kozyatağı for you and one companion, with breakfast, is included in your '
             'treatment package. For hospital treatments, you choose your hotel yourself – on request, we suggest hotels close to your hospital for you and '
             'your companion.')
# contact page: question order in the left and the right FAQ column (title beginnings)
CONTACT_LEFT = [Q, 'How does the free consultation work?', 'Does MedLuxLife carry out medical treatments itself?', 'Where do the treatments take place?',
                'Where will I stay during my treatment?', COMPANION[0], 'How do I get to the hotel, the clinic or the hospital?']
CONTACT_RIGHT = ['Should I send medical documents with my first enquiry?', 'How much does a treatment cost?', 'Can I book travel services without a treatment?',
                 'Do you arrange Hajj and Umrah trips?', 'Which languages do you speak?', 'Where is MedLuxLife based?', 'How can I cancel a booking?']


def faq_item(q=Q, a=A, cls='mlx-faq-nopay'):
    attrs = '{"className":"%s","style":{"spacing":{"blockGap":"0"}}}' % cls if cls else '{"style":{"spacing":{"blockGap":"0"}}}'
    return ('<!-- wp:accordion-item %s -->\n<div class="wp-block-accordion-item%s"><!-- wp:accordion-heading -->\n'
            '<h3 class="wp-block-accordion-heading"><button type="button" class="wp-block-accordion-heading__toggle"><span class="wp-block-accordion-heading__toggle-title">%s</span>'
            '<span class="wp-block-accordion-heading__toggle-icon" aria-hidden="true">+</span></button></h3>\n<!-- /wp:accordion-heading -->\n\n'
            '<!-- wp:accordion-panel -->\n<div role="region" class="wp-block-accordion-panel"><!-- wp:paragraph -->\n<p>%s</p>\n<!-- /wp:paragraph --></div>\n'
            '<!-- /wp:accordion-panel --></div>\n<!-- /wp:accordion-item -->\n\n') % (attrs, ' ' + cls if cls else '', q, a)


def balance_contact(c):
    """put the contact FAQ items into CONTACT_LEFT / CONTACT_RIGHT order (two accordions, one per column)"""
    accs = [m.start() for m in re.finditer(r'<!-- wp:accordion \{', c)]
    if len(accs) != 2:
        return c
    items = {}
    for m in re.finditer(r'<!-- wp:accordion-item .*?<!-- /wp:accordion-item -->', c, re.S):
        t = re.search(r'toggle-title">(.*?)</span>', m.group(0)).group(1)
        items[t] = m.group(0) + '\n\n'
    if COMPANION[0] not in items:
        items[COMPANION[0]] = faq_item(*COMPANION, cls='')
    want = CONTACT_LEFT + CONTACT_RIGHT
    if sorted(items) != sorted(want):
        sys.exit('contact FAQ: unexpected questions %s' % sorted(set(items) ^ set(want)))
    out, pos = '', 0
    for a, order in zip(accs, (CONTACT_LEFT, CONTACT_RIGHT)):
        open_end = c.find('>', c.find('<div role="group" class="wp-block-accordion', a)) + 1
        close = c.find('</div>\n<!-- /wp:accordion -->', open_end)
        out += c[pos:open_end] + ''.join(items[t] for t in order).rstrip('\n')
        pos = close
    return out + c[pos:]


def item_bounds(c, question):
    """(start, end) of the accordion item whose title is `question`; end stops right after its closing comment"""
    q = c.find(question)
    if q < 0:
        return None
    s = c.rfind('<!-- wp:accordion-item', 0, q)
    e = c.find('<!-- /wp:accordion-item -->', s) + len('<!-- /wp:accordion-item -->')
    return s, e


def first_item_pos(c):
    """offset of the first item inside the first FAQ accordion"""
    a = c.find('<!-- wp:accordion {')
    return -1 if a < 0 else c.find('<!-- wp:accordion-item', a)


def add_line(c):
    if 'medlux-nopay' in c:
        return c
    k = c.find('<!-- wp:group {"className":"medlux-cta"')
    if k < 0:
        return c
    e = c.find('<!-- /wp:paragraph -->', k)
    if e < 0 or e > c.find('<!-- wp:buttons', k):
        return c
    e += len('<!-- /wp:paragraph -->')
    return c[:e] + '\n\n' + NOPAY_P.rstrip('\n') + c[e:]


def add_faq(c):
    if 'mlx-faq-nopay' in c:
        return c
    b = item_bounds(c, Q)
    if b:  # an older copy of the question (contact page): take it out, the new item goes to the top
        s, e = b
        if c[s - 2:s] == '</' and c[e:].lstrip().startswith('div>'):  # repair the tag stay_transfer.py split on 2026-10-28
            c = c[:s - 2] + '\n\n</' + c[e:].lstrip()
        else:
            c = c[:s] + c[e:].lstrip('\n')
    k = first_item_pos(c)
    return c if k < 0 else c[:k] + faq_item() + c[k:]


def apply(c, link):
    path = link.replace(SITE, '')
    if path.startswith('/travel/') or path in ('/', '/home/'):
        return c
    c = add_line(c)
    if path.startswith('/health/clinical-treatments/') and 'wp:accordion {' in c:
        c = add_faq(c)
    return c


def change(p):
    c = p['content']['raw']
    if p['id'] == HOME:
        return c
    new = apply(c, p['link'])
    if p['id'] == CONTACT:
        new = balance_contact(add_faq(new))
    if p['id'] == HUB:
        new = new.replace(HUB_OLD, HUB_NEW)
    return new


def main(dry):
    pages = []
    for n in (1, 2, 3, 4):
        r = json.loads(subprocess.run(['curl', '-sS', W + '?per_page=100&page=%d&context=edit&_fields=id,link,content,modified' % n], capture_output=True).stdout)
        if not isinstance(r, list) or not r:
            break
        pages += r
    todo = [(p, change(p)) for p in pages]
    todo = [(p, new) for p, new in todo if new != p['content']['raw']]
    lines = sum('medlux-nopay' in new and 'medlux-nopay' not in p['content']['raw'] for p, new in todo)
    faqs = sum('mlx-faq-nopay' in new and 'mlx-faq-nopay' not in p['content']['raw'] for p, new in todo)
    print('pages:', len(pages), '| to change:', len(todo), '| new CTA lines:', lines, '| new FAQ items:', faqs)
    if dry:
        return pages, todo
    d = ROOT / 'backups/wp/nopay'; d.mkdir(parents=True, exist_ok=True)
    json.dump([{'id': p['id'], 'link': p['link'], 'modified': p['modified'], 'content': p['content']['raw']} for p, _ in todo],
              open(d / ('pages_before_nopay_%s.json' % time.strftime('%Y%m%d_%H%M%S')), 'w'), ensure_ascii=False)
    bad = []
    for p, new in todo:
        r = subprocess.run(['curl', '-sS', '-X', 'POST', W + str(p['id']), '-H', 'Content-Type: application/json', '--data-binary', '@-'],
                           input=json.dumps({'content': new}).encode(), capture_output=True).stdout
        try:
            ok = json.loads(r).get('id') == p['id']
        except ValueError:
            ok = False
        if not ok:
            bad.append(p['id']); print(p['id'], p['link'].replace(SITE, ''), r[:200])
    print('updated:', len(todo) - len(bad), '| failed:', bad)
    sys.path.insert(0, str(ROOT / 'tools')); import cache_clear; print('page cache cleared:', cache_clear.clear())


if __name__ == '__main__':
    main('--dry' in sys.argv)
