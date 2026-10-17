#!/usr/bin/env python3
"""Build the About Us page content (page 24) -> content/about_us_2026.html.
Keeps the legal note (with its DE/TR translations) from the backup taken before the 2026-10-17 rewrite.
Usage: build_about_us.py   (then publish the file to /wp/v2/pages/24)"""
import json, re, base64, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
old = json.loads((ROOT / 'backups/wp/page24_before_about_rewrite.json').read_text())['content']['raw']
disc = re.search(r'<!-- wp:paragraph \{"className":"medlux-disclaimer"\} -->.*?<!-- /wp:paragraph -->', old, re.S).group(0)

def svg(body):
    s = ('<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48" fill="none" stroke="#d4a24c" '
         'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' + body + '</svg>')
    return 'data:image/svg+xml;base64,' + base64.b64encode(s.encode()).decode()

# gold line icons (same style as the Health page "Why MedLuxLife" box; no crosses or plus signs)
ICON = {
    'contact': svg('<circle cx="20" cy="18" r="8"/><path d="M4 42c0-8.8 7.2-15 16-15s16 6.2 16 15"/><path d="M31 4h13a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2h-8l-4 3v-3h-1a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z"/>'),
    'language': svg('<path d="M6 8h22a3 3 0 0 1 3 3v11a3 3 0 0 1-3 3H15l-6 5v-5H6a3 3 0 0 1-3-3V11a3 3 0 0 1 3-3z"/><path d="M35 17h7a3 3 0 0 1 3 3v10a3 3 0 0 1-3 3h-2v5l-6-5h-9a3 3 0 0 1-3-3v-1"/>'),
    'steps': svg('<path d="M12 4h17l9 9v29a2 2 0 0 1-2 2H12a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z"/><path d="M29 4v9h9"/><path d="M15 23l3 3 5-6M27 24h6M15 33l3 3 5-6M27 34h6"/>'),
    'lock': svg('<rect x="10" y="21" width="28" height="22" rx="3"/><path d="M16 21v-6a8 8 0 0 1 16 0v6"/><circle cx="24" cy="31" r="2.5"/><path d="M24 33.5v4"/>'),
    'clock': svg('<circle cx="24" cy="24" r="18"/><path d="M24 13v11l7 5"/>'),
    'after': svg('<path d="M24 41S6 30.5 6 17.5A9.5 9.5 0 0 1 24 12a9.5 9.5 0 0 1 18 5.5C42 30.5 24 41 24 41z"/><path d="M14 24h6l2-4 4 8 2-4h6"/>'),
    'health': svg('<path d="M24 41S6 30.5 6 17.5A9.5 9.5 0 0 1 24 12a9.5 9.5 0 0 1 18 5.5C42 30.5 24 41 24 41z"/>'),
    'travel': svg('<circle cx="24" cy="24" r="18"/><path d="M6 24h36M24 6c5 5 7.5 11 7.5 18S29 37 24 42M24 6c-5 5-7.5 11-7.5 18S19 37 24 42"/>'),
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

def icon(name, cls):
    return '<!-- wp:image {"className":"%s"} -->\n<figure class="wp-block-image %s"><img src="%s" alt=""/></figure>\n<!-- /wp:image -->' % (cls, cls, ICON[name])

def why_item(name, title, text):
    return group('medlux-why-item', [icon(name, 'medlux-why-icon'), h(title, 3), p(text)])

IMG = 'https://medluxlife.de/wp-content/uploads/2026/10/medluxlife-team-2026b.jpg'
intro = (
    '<!-- wp:columns {"verticalAlignment":"center","className":"medlux-intro medlux-about-intro"} -->\n'
    '<div class="wp-block-columns are-vertically-aligned-center medlux-intro medlux-about-intro">'
    '<!-- wp:column {"verticalAlignment":"center"} -->\n<div class="wp-block-column is-vertically-aligned-center">'
    + p('Treatment in Türkiye.<br><span>Travel wherever you wish.</span>', 'medlux-about-headline') + '\n\n'
    + p('MedLuxLife was founded by Anna and Emrah in Aachen, Germany. We bring two things together: medical treatment '
        'with qualified specialists at our partner clinics and hospitals in Türkiye – and travel to any destination you '
        'choose, whether a holiday, a city break, a business trip or a pilgrimage.', 'medlux-lead') + '\n\n'
    + p('We adapt to you – to your wishes, your budget and your pace. No wish is too big or too small: we always look for '
        'the comfortable solution that suits you, and one personal contact plans every step with you.', 'medlux-lead')
    + '</div>\n<!-- /wp:column -->\n\n<!-- wp:column {"verticalAlignment":"center"} -->\n<div class="wp-block-column is-vertically-aligned-center">'
    '<!-- wp:image {"id":2048,"sizeSlug":"full","linkDestination":"none","className":"medlux-intro-img medlux-about-founders"} -->\n'
    '<figure class="wp-block-image size-full medlux-intro-img medlux-about-founders"><img src="%s" alt="Anna and Emrah, the founders of MedLuxLife, at their office desk" class="wp-image-2048"/>'
    '<figcaption class="wp-element-caption">Anna &amp; Emrah, founders of MedLuxLife</figcaption></figure>\n<!-- /wp:image -->'
    '</div>\n<!-- /wp:column --></div>\n<!-- /wp:columns -->') % IMG

what = group('medlux-section', [
    h('What we do'),
    group('medlux-treatment-grid medlux-about-what', [
        group('medlux-card', [icon('health', 'medlux-card-icon'), h('Health', 3),
              p('We are your coordinator, not a clinic. We listen to your wishes, arrange your consultation with qualified '
                'specialists at our partner clinics and hospitals in Türkiye and organise your stay. All medical decisions '
                'are made by licensed doctors, together with you.')]),
        group('medlux-card', [icon('travel', 'medlux-card-icon'), h('Travel', 3),
              p('Travel is not limited to Türkiye: we plan holidays, city breaks, business trips and pilgrimages to the '
                'destination of your choice – flights, hand-picked hotels, private transfers and excursions, tailored to '
                'your wishes and budget.')]),
    ], '{"type":"grid","minimumColumnWidth":"20rem"}'),
])

partners = group('medlux-section medlux-partners', [
    h('Our partners'),
    p('We have personally visited the clinics and hospitals we work with in Istanbul. '
      'What we would not recommend to our own family, we do not recommend to you.', 'medlux-partners-quote'),
    p('What we look at', 'medlux-partners-label'),
    ul(['Valid licences', 'International accreditation', 'Experienced specialists', 'Experience with international patients'],
       'medlux-criteria'),
    group('medlux-treatment-grid medlux-partners-grid', [
        group('medlux-card', [h('Hospital &amp; specialist care', 3),
              p('A large university hospital group in Istanbul', 'medlux-partner-type'),
              ul(['Several hospitals and specialised centres',
                  'Academic specialists in almost every field',
                  'Modern diagnostics such as 3-Tesla MRI and PET-CT',
                  'International JCI accreditation'])]),
        group('medlux-card', [h('Aesthetic, hair, dental &amp; weight-loss treatments', 3),
              p('A specialised clinic for international patients', 'medlux-partner-type'),
              ul(['Surgical team with more than 25 years of experience',
                  'Treatments in partner hospitals approved by the Turkish Ministry of Health and accredited by JCI, or at the clinic itself',
                  'Quiet rest areas, for example after a hair transplant'])]),
    ], '{"type":"grid","minimumColumnWidth":"20rem"}'),
    p('We plan to add further renowned hospitals to our network – always selected by the same criteria.', 'medlux-partners-note'),
])

care = group('medlux-why medlux-why--six', [
    h('How we take care of you'),
    group('medlux-why-grid', [
        why_item('contact', 'One personal contact', 'From your first question until you are back home, one person who knows your plan.'),
        why_item('language', 'Your language', 'We speak Turkish, Ukrainian, Russian, English and German. At our partner clinics, native-speaking interpreters are available for nine languages.'),
        why_item('steps', 'Clear steps', 'Before you decide, we explain the planned steps of your treatment and journey. No obligation.'),
        why_item('lock', 'Confidential', 'Your medical documents are shared only in your consultation with the doctor, with your consent, and handled in line with the GDPR.'),
        why_item('clock', 'Reply within 24 hours', 'We answer every enquiry personally within 24 hours.'),
        why_item('after', 'After you are home', 'Stay in touch with us on WhatsApp after your return and tell us how you are.'),
    ], '{"type":"default"}'),
])

values = group('medlux-section medlux-values', [
    h('What we stand for'),
    p('<span>Honesty</span><span>Care</span><span>Discretion</span><span>Reliability</span>', 'medlux-values-words'),
    p('These are the values we work by – with every guest, every partner and every plan.'),
])

cta = group('medlux-cta', [
    h("Let's plan it together"),
    p('Tell us what you have in mind – by phone, WhatsApp or our contact form. The first conversation is free and without obligation.'),
    '<!-- wp:buttons -->\n<div class="wp-block-buttons"><!-- wp:button {"className":"medlux-btn-primary"} -->\n'
    '<div class="wp-block-button medlux-btn-primary"><a class="wp-block-button__link wp-element-button" href="https://medluxlife.de/contact/">Request a Free Consultation</a></div>\n'
    '<!-- /wp:button -->\n\n<!-- wp:button {"className":"medlux-btn-whatsapp"} -->\n'
    '<div class="wp-block-button medlux-btn-whatsapp"><a class="wp-block-button__link wp-element-button" href="https://wa.me/380979092326" target="_blank" rel="noreferrer noopener">WhatsApp</a></div>\n'
    '<!-- /wp:button --></div>\n<!-- /wp:buttons -->',
    disc,
])

(ROOT / 'content/about_us_2026.html').write_text('\n\n'.join([intro, what, partners, care, values, cta]) + '\n')
print('written', len((ROOT / 'content/about_us_2026.html').read_text()))
