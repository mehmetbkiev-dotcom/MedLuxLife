#!/usr/bin/env python3
"""Mommy Makeover detail page (sample for treatment detail pages, Anna 2026-10-18) -> content/mommy_makeover.html.
Facts are general information from the partner clinic's own page (discharge after 1-2 days, daily activities after
2-4 weeks, final result after 6-12 months, general anaesthesia); written in our own words, no clinic/doctor names,
no before/after, no prices, no promises (HWG)."""
import base64, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent

def svg(body):
    s = ('<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48" fill="none" stroke="#d4a24c" '
         'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' + body + '</svg>')
    return 'data:image/svg+xml;base64,' + base64.b64encode(s.encode()).decode()

ICON = {
    'tummy': svg('<path d="M16 6c0 8 6 12 6 18s-6 10-6 18"/><path d="M32 6c0 8-6 12-6 18s6 10 6 18"/>'),
    'lift': svg('<circle cx="24" cy="24" r="18"/><path d="M24 33V15M17 21l7-7 7 7"/>'),
    'lipo': svg('<path d="M24 6s-12 14-12 22a12 12 0 0 0 24 0C36 20 24 6 24 6z"/>'),
    'lotus': svg('<path d="M24 9c5 6 5 14 0 23-5-9-5-17 0-23z"/><path d="M24 32c-8 0-14-5-16-12 7 0 12 4 16 12z"/><path d="M24 32c8 0 14-5 16-12-7 0-12 4-16 12z"/><path d="M10 39h28"/>'),
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

IMG = 'https://medluxlife.de/wp-content/uploads/2026/10/medizinische-voruntersuchung-mit-korpermarkierungen-opt-1.jpg'
intro = ('<!-- wp:columns {"verticalAlignment":"center","className":"medlux-intro"} -->\n<div class="wp-block-columns are-vertically-aligned-center medlux-intro">'
         '<!-- wp:column {"verticalAlignment":"center"} -->\n<div class="wp-block-column is-vertically-aligned-center">'
         + p('A mommy makeover combines several procedures in one operation to address changes after pregnancy and childbirth – '
             'for example loose skin and separated abdominal muscles, a change in breast shape or stubborn fat deposits. Which '
             'procedures are combined is decided together with your surgeon. MedLuxLife arranges your online consultation with '
             'the surgeon in Istanbul and organises your stay.', 'medlux-lead')
         + '</div>\n<!-- /wp:column -->\n\n<!-- wp:column {"verticalAlignment":"center"} -->\n<div class="wp-block-column is-vertically-aligned-center">'
         '<!-- wp:image {"id":1412,"sizeSlug":"large","linkDestination":"none","className":"medlux-intro-img"} -->\n'
         '<figure class="wp-block-image size-large medlux-intro-img"><img src="%s" alt="Abdomen marked before a mommy makeover consultation" class="wp-image-1412"/></figure>\n<!-- /wp:image -->'
         '</div>\n<!-- /wp:column --></div>\n<!-- /wp:columns -->') % IMG

def fact(label, value):
    return group('medlux-fact', [p(label, 'medlux-fact-label'), p(value, 'medlux-fact-value')])

facts = group('medlux-section medlux-facts-sec', [
    h('At a glance'),
    group('medlux-facts', [
        fact('Anaesthesia', 'General anaesthesia'),
        fact('Hospital stay', 'Usually 1–2 nights'),
        fact('Daily activities', 'After about 2–4 weeks'),
        fact('Final result', 'After 6–12 months'),
        fact('Stay in Türkiye', 'Planned individually with the clinic'),
    ], '{"type":"default"}'),
    p('General information; your surgeon plans the details for you personally.', 'medlux-facts-note'),
])

include = group('medlux-section', [
    h('What it can include'),
    group('medlux-treatment-grid medlux-centered-cards', [
        group('medlux-card', [icon('tummy'), h('Tummy tuck', 3), p('Removes excess skin and tightens the abdominal muscles.')]),
        group('medlux-card', [icon('lift'), h('Breast lift or augmentation', 3), p('Restores the shape and volume of the breasts.')]),
        group('medlux-card', [icon('lipo'), h('Liposuction', 3), p('Removes stubborn fat on the abdomen, hips or thighs.')]),
        group('medlux-card', [icon('lotus'), h('Intimate rejuvenation', 3), p('For example labiaplasty, if you wish.')]),
    ], '{"type":"grid","minimumColumnWidth":"14rem"}'),
])

suitable = group('medlux-section medlux-good-to-know', [
    h('Who it may be suitable for'),
    ul(['You have completed your family planning and are no longer breastfeeding.',
        'Your weight has been stable for some time.',
        'You are in good general health.',
        'You would like to address several changes after pregnancy at the same time.',
        'Whether the procedure is suitable for you is decided by the surgeon after a personal assessment.']),
])

def step(n, title, text):
    return group('medlux-card', [h('<span class="medlux-step-no">%d</span>%s' % (n, title), 3), p(text)])

how = group('medlux-section', [
    h('How it works with MedLuxLife'),
    group('medlux-steps medlux-steps--list', [
        step(1, 'Contact and online consultation', 'Contact us and tell us what you are interested in. We refer you to the right surgeon for an online consultation. Photos or medical documents go directly to the doctor, only on request.'),
        step(2, 'Your personal plan', 'The surgeon recommends which procedures to combine. We plan your dates, flights, hotel and transfers around it.'),
        step(3, 'Arrival and surgery', 'After a pre-operative examination, the operation takes place under general anaesthesia. You usually stay in hospital for 1–2 nights.'),
        step(4, 'Recovery in Istanbul', 'You rest in your hotel and attend the check-ups at the clinic. The surgeon decides when you are ready to fly home.'),
        step(5, 'Back home', 'Stay in touch with us on WhatsApp – we help with follow-up questions.'),
    ], '{"type":"default"}'),
])

recovery = group('medlux-section', [
    h('Recovery step by step'),
    group('medlux-treatment-grid medlux-centered-cards medlux-timeline', [
        group('medlux-card', [p('First days', 'medlux-time-label'), p('Gentle movement soon after surgery and 1–2 nights in hospital. Follow the care instructions of your surgeon.')]),
        group('medlux-card', [p('Weeks 2–4', 'medlux-time-label'), p('Most people gradually return to their daily activities. Heavy lifting and sport come later, as advised.')]),
        group('medlux-card', [p('Months 6–12', 'medlux-time-label'), p('Swelling goes down over the weeks; the final result usually shows after 6–12 months.')]),
    ], '{"type":"grid","minimumColumnWidth":"14rem"}'),
])

faqs = group('medlux-section', [
    h('Frequently asked questions'),
    faq([
        ('Which procedures are combined?', 'This is planned individually. A mommy makeover often combines a tummy tuck, a breast lift or augmentation and liposuction – depending on your body and your wishes.'),
        ('Can I get pregnant after a mommy makeover?', 'Yes, but a later pregnancy can stretch the skin and abdominal muscles again and change the result. For this reason it is usually recommended to wait until your family planning is complete.'),
        ('How long is the recovery?', 'It depends on the combination of procedures. Most people return to their daily activities after about 2–4 weeks; heavy lifting and sport take longer.'),
        ('How long should I stay in Türkiye?', 'This is planned individually with the clinic, depending on the procedures. We organise your flights and hotel accordingly.'),
        ('Should I send photos or medical documents to MedLuxLife?', 'No. If the surgeon needs photos or documents, you share them directly with the doctor in your online consultation.'),
    ]),
])

cta = group('medlux-cta', [
    h('Plan your mommy makeover'),
    p('Contact us and tell us what you are interested in – we refer you to the right specialist for an online consultation.'),
    '<!-- wp:buttons -->\n<div class="wp-block-buttons"><!-- wp:button {"className":"medlux-btn-primary"} -->\n'
    '<div class="wp-block-button medlux-btn-primary"><a class="wp-block-button__link wp-element-button" href="https://medluxlife.de/contact/">Request a Free Consultation</a></div>\n'
    '<!-- /wp:button -->\n\n<!-- wp:button {"className":"medlux-btn-whatsapp"} -->\n'
    '<div class="wp-block-button medlux-btn-whatsapp"><a class="wp-block-button__link wp-element-button" href="https://wa.me/380979092326" target="_blank" rel="noreferrer noopener">WhatsApp</a></div>\n'
    '<!-- /wp:button --></div>\n<!-- /wp:buttons -->',
    p('The information on this page is for general guidance only and does not replace a medical consultation. Suitability for any treatment is assessed individually by a qualified doctor.', 'medlux-disclaimer'),
])

(ROOT / 'content/mommy_makeover.html').write_text('\n\n'.join([intro, facts, include, suitable, how, recovery, faqs, cta]) + '\n')
print('written', len((ROOT / 'content/mommy_makeover.html').read_text()))
