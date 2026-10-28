#!/usr/bin/env python3
"""Partner pages under /partners/ (Emrah 2026-10-28: header "Partners" after About Us → Hospital / Clinic / Tourism;
Hospital → Hospitals + Doctors, Clinic → Clinic + Doctors (no "Our": they are the partners' doctors, Emrah 2026-10-28); doctor pages with hospital / department filters and
name search like Yeditepe's own doctor list; one look for the doctors of both partners).
Content: facts from the partners' own websites, rewritten factually (HWG: no superlatives, no promises, no before/after);
doctor data in content/partners/doctors.json (tools/partners_data.py + tools/partners_photos.py), photos in content/partners/media.json.
Creates or updates the pages (template page-with-title) and records their ids in content/partners/pages.json.
usage: build_partners.py [--dry] [--only KEY [--sub]]   (KEY e.g. partners/yeditepe-university-hospitals; --sub also its subpages)"""
import html, json, pathlib, re, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
API = 'https://medluxlife-6j8sz55bpn.live-website.com/wp-json/wp/v2/pages'
SITE = 'https://medluxlife.de'
UP = SITE + '/wp-content/uploads/2026/10/'
M = json.load(open(ROOT / 'content/partners/media.json'))
DOCS = json.load(open(ROOT / 'content/partners/doctors.json'))
E = html.escape

# media already in the library (home partner cards, stay section)
IMG = {'yeditepe': (2576, None), 'celyxmed': (2577, None), 'travel': (2578, None)}

# our own treatment pages, for links from department names (Yeditepe names are normalised to these in partners_data.py)
PAGES = {}
for f in ('hosp_pages.json', 'clin_pages.json'):
    p = pathlib.Path('/tmp/claude-0/-home-user-MedLuxLife/58e49045-1f3b-5625-b667-4a635b0b1d5b/scratchpad') / f
    if p.exists():
        for x in json.load(open(p)):
            PAGES[html.unescape(x['title']['rendered'])] = x['link']
json.dump(PAGES, open(ROOT / 'content/partners/treatment_links.json', 'w'), ensure_ascii=False, indent=1) if PAGES else None
PAGES = PAGES or json.load(open(ROOT / 'content/partners/treatment_links.json'))
PAGES.update({'Plastic, Reconstructive and Aesthetic Surgery': SITE + '/health/clinical-treatments/plastic-surgery/',
              'Oral and Maxillofacial Surgery': SITE + '/health/clinical-treatments/dental-and-oral-health/',
              'Dentistry': SITE + '/health/clinical-treatments/dental-and-oral-health/',
              'Prosthodontics': SITE + '/health/clinical-treatments/dental-and-oral-health/'})

HOSP = {'kozyatagi': 'Yeditepe University Kozyatağı Hospital', 'kosuyolu': 'Yeditepe University Koşuyolu Hospital',
        'eye': 'Yeditepe University Eye Center', 'genetic': 'Yeditepe University Genetic Diagnosis Center',
        'tissue': 'Yeditepe University Tissue Typing Laboratory', 'dental': 'Yeditepe University Dental Hospital', 'celyxmed': 'Celyxmed · Ataşehir, Istanbul'}
TITLE = {'prof': 'Prof. Dr.', 'assoc': 'Assoc. Prof. Dr.', 'asst': 'Asst. Prof. Dr.', 'spec': 'Spec. Dr.', 'op': 'Op. Dr.', 'dr': 'Dr.', 'drdt': 'Dr. Dt.', 'dt': 'Dt.'}
RANK = {'prof': 0, 'assoc': 1, 'asst': 2, 'op': 3, 'spec': 3, 'dr': 3, 'drdt': 3, 'dt': 4}


def slug(s):
    t = s.lower()
    for a, b in zip('çğıöşüâîû', 'cgiosuaiu'):
        t = t.replace(a, b)
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')


# ---------- blocks ----------
def para(text, cls=None):
    if cls:
        return '<!-- wp:paragraph {"className":"%s"} -->\n<p class="%s">%s</p>\n<!-- /wp:paragraph -->\n\n' % (cls, cls, text)
    return '<!-- wp:paragraph -->\n<p>%s</p>\n<!-- /wp:paragraph -->\n\n' % text


def h(text, level=2):
    a = '' if level == 2 else ' {"level":%d}' % level
    return '<!-- wp:heading%s -->\n<h%d class="wp-block-heading">%s</h%d>\n<!-- /wp:heading -->\n\n' % (a, level, text, level)


def image(mid, url, alt, cls):
    return ('<!-- wp:image {"id":%d,"sizeSlug":"large","linkDestination":"none","className":"%s"} -->\n'
            '<figure class="wp-block-image size-large %s"><img src="%s" alt="%s" class="wp-image-%d"/></figure>\n<!-- /wp:image -->\n\n') % (mid, cls, cls, url, E(alt, True), mid)


def group(cls, inner, layout='{"type":"constrained"}'):
    return ('<!-- wp:group {"className":"%s","layout":%s} -->\n<div class="wp-block-group %s">%s</div>\n<!-- /wp:group -->\n\n'
            % (cls.replace('--', '\\u002d\\u002d'), layout, cls, inner))


def section(title, inner, extra=''):
    return group(('medlux-section ' + extra).strip(), h(title) + inner)


def grid(cards, cls='medlux-treatment-grid', min_col='20rem'):
    return group(cls, ''.join(cards), '{"type":"grid","minimumColumnWidth":"%s"}' % min_col)


def photo_card(img, title, text, links=(), label=None):
    mid, url, alt = img
    inner = image(mid, url, alt, 'medlux-card-img')
    if label:
        inner += para(label, 'medlux-card-label')
    inner += h(title, 3) + para(text)
    for t, u in links:
        inner += para('<a href="%s">%s →</a>' % (u, t), 'medlux-more')
    return group('medlux-card medlux-card--photo' + (' medlux-card--links' if len(links) > 1 else ''), inner)


def text_card(title, text):
    return group('medlux-card', h(title, 3) + para(text))


def intro(lead, img):
    mid, url, alt = img
    return ('<!-- wp:columns {"verticalAlignment":"center","className":"medlux-intro"} -->\n<div class="wp-block-columns are-vertically-aligned-center medlux-intro">'
            '<!-- wp:column {"verticalAlignment":"center"} -->\n<div class="wp-block-column is-vertically-aligned-center">%s</div>\n<!-- /wp:column -->\n\n'
            '<!-- wp:column {"verticalAlignment":"center"} -->\n<div class="wp-block-column is-vertically-aligned-center">%s</div>\n<!-- /wp:column --></div>\n<!-- /wp:columns -->\n\n'
            % (para(lead, 'medlux-lead'), image(mid, url, alt, 'medlux-intro-img')))


def buttons(items):
    b = ''
    for t, u, cls in items:
        b += ('<!-- wp:button {"className":"%s"} -->\n<div class="wp-block-button %s"><a class="wp-block-button__link wp-element-button" href="%s">%s</a></div>\n<!-- /wp:button -->\n\n'
              % (cls, cls, u, t))
    return '<!-- wp:buttons -->\n<div class="wp-block-buttons">%s</div>\n<!-- /wp:buttons -->\n\n' % b


def ul(items, cls):
    li = ''.join('<!-- wp:list-item -->\n<li>%s</li>\n<!-- /wp:list-item -->\n\n' % i for i in items)
    return '<!-- wp:list {"className":"%s"} -->\n<ul class="wp-block-list %s">%s</ul>\n<!-- /wp:list -->\n\n' % (cls, cls, li)


def gallery(keys):
    return group('medlux-photo-row', ''.join(image(M[k]['id'], M[k]['url'], M[k]['alt'], 'medlux-photo') for k in keys),
                 '{"type":"grid","minimumColumnWidth":"14rem"}')


def chips(names):
    items = []
    for n in names:
        items.append('<a href="%s">%s</a>' % (PAGES[n], n) if n in PAGES else n)
    return ul(items, 'medlux-chips')


CTA = ('<!-- wp:group {"className":"medlux-cta","layout":{"type":"constrained"}} -->\n<div class="wp-block-group medlux-cta">'
       + h('Plan your treatment with confidence')
       + para('Every treatment begins with a personal, no-obligation consultation. Contact us and we will get back to you as soon as possible.')
       + '<!-- wp:buttons -->\n<div class="wp-block-buttons"><!-- wp:button {"className":"medlux-btn-primary"} -->\n<div class="wp-block-button medlux-btn-primary"><a class="wp-block-button__link wp-element-button" href="https://medluxlife.de/contact/">Request a Free Consultation</a></div>\n<!-- /wp:button -->\n\n'
       '<!-- wp:button {"className":"medlux-btn-whatsapp"} -->\n<div class="wp-block-button medlux-btn-whatsapp"><a class="wp-block-button__link wp-element-button" href="https://wa.me/380979092326" target="_blank" rel="noreferrer noopener">WhatsApp</a></div>\n<!-- /wp:button --></div>\n<!-- /wp:buttons -->\n\n'
       + para('The information on this page is for general guidance only and does not replace a medical consultation. Suitability for any treatment is assessed individually by a qualified doctor.', 'medlux-disclaimer')
       + '</div>\n<!-- /wp:group -->\n')


def stay_section(kind):
    sys.path.insert(0, str(ROOT / 'tools'))
    import stay_transfer
    return stay_transfer.SEC_CLINIC if kind == 'clinic' else stay_transfer.SEC_HOSPITAL


# ---------- doctors component ----------
def doctors_html(partner):
    docs = [d for d in DOCS if d['partner'] == partner]
    if partner == 'yeditepe':
        docs.sort(key=lambda d: (RANK.get(d['title'], 5), slug(d['name'])))
    depts = sorted({n for d in docs for n in d['depts']})
    hosps = [k for k in ('kozyatagi', 'kosuyolu', 'eye', 'genetic', 'tissue') if any(k in d['hospitals'] for d in docs)]
    o = ['<div class="mlx-doctors" data-partner="%s">' % partner]
    o.append('<div class="mlx-doc-filters" role="search">')
    if partner == 'yeditepe':
        o.append('<label class="mlx-doc-f"><span class="mlx-doc-l">Hospital</span><select data-f="hospital"><option value="">All hospitals</option>%s</select></label>'
                 % ''.join('<option value="%s">%s</option>' % (k, HOSP[k]) for k in hosps))
    o.append('<label class="mlx-doc-f"><span class="mlx-doc-l">Department</span><select data-f="dept"><option value="">All departments</option>%s</select></label>'
             % ''.join('<option value="%s">%s</option>' % (slug(n), E(n)) for n in depts))
    o.append('<label class="mlx-doc-f mlx-doc-q"><span class="mlx-doc-l">Doctor\'s name</span><input type="search" data-f="q" placeholder="Search by name" autocomplete="off"></label>')
    o.append('<button type="button" class="mlx-doc-reset" hidden>Reset filters</button></div>')
    o.append('<p class="mlx-doc-count" aria-live="polite"><span class="mlx-doc-n">%d</span> <span>doctors</span></p>' % len(docs))
    o.append('<ul class="mlx-doc-grid">')
    for d in docs:
        t = TITLE.get(d['title'], '')
        alt = (t + ' ' + d['name']).strip()
        # Emrah 2026-10-28: card = photo, title + name and speciality only; the whole card opens the doctor's own page
        o.append('<li class="mlx-doc" data-hospital="%s" data-dept="%s" data-name="%s"><a class="mlx-doc-a" href="%s">'
                 % (' '.join(d['hospitals']), ' '.join(slug(n) for n in d['depts']), slug(d['name']).replace('-', ' '), doctor_url(d)))
        o.append('<span class="mlx-doc-photo"><img src="%s" alt="%s" width="320" height="400" loading="lazy" decoding="async"></span>' % (d['photo_url'], E(alt, True)))
        o.append('<span class="mlx-doc-body">%s<span class="mlx-doc-name">%s</span>' % ('<span class="mlx-doc-title">%s</span>' % t if t else '', E(d['name'])))
        o.append('<span class="mlx-doc-depts">%s</span></span></a></li>' % ''.join('<span>%s</span>' % E(n) for n in d['depts']))
    o.append('</ul>')
    o.append('<p class="mlx-doc-empty" hidden>No doctor found for this selection.</p>')
    o.append('<p class="mlx-doc-morewrap"><button type="button" class="mlx-doc-showmore">Show more doctors</button></p>')
    o.append('<script>' + open(ROOT / 'assets/doctors.js').read() + '</script>')
    o.append('</div>')
    return '<!-- wp:html -->\n' + '\n'.join(o) + '\n<!-- /wp:html -->\n\n'


HOSP_PAGE = {'kozyatagi': 'kozyatagi-hospital', 'kosuyolu': 'kosuyolu-hospital', 'eye': 'eye-center', 'dental': 'dental-hospital'}
PARTNER_PATH = {'yeditepe': 'yeditepe-university-hospitals', 'celyxmed': 'celyxmed'}
SOURCE = {'yeditepe': 'Information as published by Yeditepe University Hospitals. Which doctor treats you is agreed during your consultation.',
          'celyxmed': 'Information as published by Celyxmed. Which doctor treats you is agreed during your consultation.'}


def doctor_url(d):
    return SITE + '/partners/%s/doctors/%s/' % (PARTNER_PATH[d['partner']], d['slug'])


def doctor_title(d):
    return (TITLE.get(d['title'], '') + ' ' + d['name']).strip()


def doctor_page(d):
    """the doctor's own page (Emrah 2026-10-28: a click on the card opens the doctor's detail page, like on celyxmed.com)"""
    t = TITLE.get(d['title'], '')
    list_url = SITE + '/partners/%s/doctors/' % PARTNER_PATH[d['partner']]
    depts = ''.join(('<span><a href="%s">%s</a></span>' % (PAGES[n], E(n))) if n in PAGES else '<span>%s</span>' % E(n) for n in d['depts'])
    hosp = ''
    for k in d['hospitals']:
        if k in HOSP_PAGE:
            hosp += '<span><a href="%s">%s</a></span>' % (SITE + '/partners/yeditepe-university-hospitals/hospitals/%s/' % HOSP_PAGE[k], E(HOSP[k]))
        elif k == 'celyxmed':
            hosp += '<span><a href="%s">%s</a></span>' % (SITE + '/partners/celyxmed/clinic/', E(HOSP[k]))
        else:
            hosp += '<span>%s</span>' % E(HOSP[k])
    rows = []
    for k, label in (('edu', 'Education'), ('spec', 'Specialisation'), ('side', 'Subspecialty'), ('assoc', 'Associate professorship'), ('prof', 'Professorship')):
        if d.get(k):
            rows.append('<div class="mlx-dd-row"><h3>%s</h3><p>%s</p></div>' % (label, E(d[k])))
    if d.get('career'):
        rows.append('<div class="mlx-dd-row"><h3>Career</h3><ul>%s</ul></div>' % ''.join('<li>%s</li>' % E(c) for c in d['career']))
    if d.get('interests'):
        rows.append('<div class="mlx-dd-row mlx-dd-wide"><h3>Areas of interest</h3><ul class="mlx-doc-tags">%s</ul></div>' % ''.join('<li>%s</li>' % E(i) for i in d['interests']))
    if d.get('langs'):
        rows.append('<div class="mlx-dd-row"><h3>Foreign languages</h3><p class="mlx-doc-langs">%s</p></div>' % ''.join('<span>%s</span>' % l for l in d['langs']))
    o = ['<div class="mlx-doc-detail" data-partner="%s">' % d['partner'],
         '<div class="mlx-dd-head"><img class="mlx-dd-photo" src="%s" alt="%s" width="320" height="400">' % (d['photo_url'], E(doctor_title(d), True)),
         '<div class="mlx-dd-info">%s<h2 class="mlx-doc-name">%s</h2>' % ('<p class="mlx-doc-title">%s</p>' % t if t else '', E(d['name'])),
         '<p class="mlx-doc-depts">%s</p><p class="mlx-doc-hosp">%s</p>' % (depts, hosp),
         ('<p class="mlx-doc-role">%s</p>' % E(d['role'])) if d.get('role') else '',
         # Anna 2026-10-28: photo on the left, ALL information about the doctor on the right (nothing below); no consultation button (Emrah)
         ('<div class="mlx-dd-list">%s</div>' % ''.join(rows)) if rows else '',
         '</div></div>',
         '<p class="mlx-dd-back"><a class="mlx-doc-back" href="%s">← All doctors</a></p>' % list_url,
         '<p class="mlx-dd-source">%s</p>' % SOURCE[d['partner']],
         '<script>' + open(ROOT / 'assets/doctors.js').read() + '</script></div>']
    return '<!-- wp:html -->\n' + '\n'.join(x for x in o if x) + '\n<!-- /wp:html -->\n\n' + CTA


# ---------- pages ----------
def mi(k):
    return (M[k]['id'], M[k]['url'], M[k]['alt'])


Y_IMG = (2576, UP + 'medluxlife-partner-yeditepe-kozyatagi.jpg', None)
C_IMG = (2577, UP + 'medluxlife-partner-celyxmed.jpg', None)
T_IMG = (2578, UP + 'medluxlife-partner-hotel.jpg', None)


def media_info(mid):
    r = json.loads(subprocess.run(['curl', '-sS', 'https://medluxlife-6j8sz55bpn.live-website.com/wp-json/wp/v2/media/%d?_fields=source_url,alt_text' % mid], capture_output=True).stdout)
    return (mid, r['source_url'], r['alt_text'])


def build():
    global Y_IMG, C_IMG, T_IMG
    Y_IMG, C_IMG, T_IMG = media_info(2576), media_info(2577), media_info(2578)
    P = {}
    url = lambda *p: SITE + '/partners/' + ''.join(x + '/' for x in p)
    Y, C = 'yeditepe-university-hospitals', 'celyxmed'
    Y_DOCS = url(Y, 'doctors')
    HOSPITALS = [
        ('kozyatagi-hospital', 'Yeditepe University Kozyatağı Hospital', Y_IMG, 'Ataşehir · Asian side of Istanbul · 190 beds',
         'Opened in 2005: internal medicine, cardiology, obstetrics and IVF, paediatrics, orthopaedics and many other departments.'),
        ('kosuyolu-hospital', 'Yeditepe University Koşuyolu Hospital', mi('s_card'), 'Kadıköy · Asian side of Istanbul · 180 beds',
         'Focus on neurosciences and oncology, with bone marrow transplantation, organ transplant clinics and nine operating theatres.'),
        ('dental-hospital', 'Yeditepe University Dental Hospital', mi('d_card'), 'Göztepe, Kadıköy · Asian side of Istanbul',
         'The dental hospital of the Faculty of Dentistry, with 120 treatment units for all fields of dentistry.'),
        ('eye-center', 'Yeditepe University Eye Center', mi('e_card'), 'Beşiktaş · European side of Istanbul',
         'Eye centre of Yeditepe University Hospitals for the diagnosis and treatment of eye diseases.')]
    hosp_cards = [photo_card(img, name, text, [('Learn more', url(Y, 'hospitals', s))], label=loc) for s, name, img, loc, text in HOSPITALS]

    # Partners hub
    P[('partners',)] = ('Partners', intro(
        'MedLuxLife works with selected partners. Your treatment is carried out by the doctors of our partner hospital and partner clinic, '
        'and your travel is booked with our travel partner – we coordinate everything in between and remain your contact throughout.', Y_IMG)
        + section('Our partners', grid([
            photo_card(Y_IMG, 'Yeditepe University Hospitals', 'The hospitals of Yeditepe University in Istanbul – Kozyatağı and Koşuyolu hospitals, a dental hospital and an eye centre – for hospital and specialist treatments.',
                       [('Hospitals', url(Y, 'hospitals')), ('Doctors', Y_DOCS)], label='Hospital'),
            photo_card(C_IMG, 'Celyxmed', 'Clinic in Ataşehir, Istanbul, for plastic surgery, hair transplantation, dental treatments and medical aesthetics.',
                       [('Clinic', url(C, 'clinic')), ('Doctors', url(C, 'doctors'))], label='Clinic'),
            photo_card(T_IMG, 'Travel partner', 'A tour operator based in Germany books your flights, hotels, transfers and holiday packages. We will introduce our travel partner here soon.',
                       [('Learn more', url('travel-partner'))], label='Tourism')], min_col='15rem'))
        + section('How we work with our partners', grid([
            text_card('Medical treatment by our partners', 'Examinations and treatments are carried out exclusively by the doctors of our partner hospital and clinic. Your treatment contract is concluded directly with them.'),
            text_card('Coordination by MedLuxLife', 'We prepare your enquiry, arrange appointments, accommodation and transfers and stay in touch with you before, during and after your stay.'),
            text_card('Payment directly to the clinic or hospital', 'MedLuxLife does not take any advance payment for treatments. You pay for your treatment directly at the clinic or hospital.')], min_col='15rem'))
        + CTA, None)

    # Yeditepe overview
    P[('partners', Y)] = ('Yeditepe University Hospitals', intro(
        'Yeditepe University Hospitals are the hospitals of Yeditepe University, a foundation university in Istanbul founded in 1996. '
        'As university hospitals, they combine patient care with teaching and research. MedLuxLife coordinates hospital and specialist treatments with Yeditepe University Hospitals.', Y_IMG)
        + section('Hospitals', grid(hosp_cards))
        + section('Doctors', para('More than 170 doctors and specialists of Yeditepe University Hospitals – filter by hospital or department and open their profiles.')
                  + buttons([('Meet the doctors', Y_DOCS, 'medlux-btn-primary')]))
        + stay_section('hospital') + CTA, ('partners',))

    P[('partners', Y, 'hospitals')] = ('Hospitals', intro(
        'Yeditepe University Hospitals have several locations in Istanbul. Your treatment takes place at the hospital where the department and the doctor for your treatment are based – we coordinate the appointment for you.', mi('s_card'))
        + section('Hospitals of Yeditepe University', grid(hosp_cards)) + CTA, ('partners', Y))

    S = json.load(open(ROOT / 'content/partners/services.json'))
    sys.path.insert(0, str(ROOT / 'tools'))
    from partners_data import dept
    svc = lambda k: list(dict.fromkeys(dept(n) for n in S.get(k, []) if 'Clone of' not in n))
    doc_btn = lambda k, name: section('Doctors at this hospital', para('See the doctors and specialists who work at %s.' % name)
                                      + buttons([('Show the doctors of this hospital', Y_DOCS + '?hospital=' + k, 'medlux-btn-primary')]))
    addr = lambda a, transport: section('Address and transport', para(a, 'medlux-address') + (para(transport) if transport else ''))
    P[('partners', Y, 'hospitals', 'kozyatagi-hospital')] = ('Yeditepe University Kozyatağı Hospital', intro(
        'Yeditepe University Kozyatağı Hospital in Ataşehir, on the Asian side of Istanbul, opened on 26 August 2005. It has 190 beds and a wide range of departments, from internal medicine and cardiology to obstetrics, IVF and paediatrics.', Y_IMG)
        + section('About the hospital', para('The building was planned with fire-resistant, scratch-resistant and antibacterial materials. Particular attention is paid to hygiene and sterilisation: in addition to manual disinfection, all patient beds can be cleaned with a high-temperature water spray system.')
                  + para('The imaging centre is equipped with multislice computed tomography (CT) and 3 Tesla magnetic resonance imaging (MRI).') + gallery(['k1', 'k2', 'k3']))
        + section('Departments', chips(svc('kozyatagi-hospital')))
        + addr('İçerenköy Mah. Hastahane Sok. 4, 4/1, 34752 Ataşehir / İstanbul', 'Nearest metro stations: Bostancı and Kozyatağı.')
        + doc_btn('kozyatagi', 'Yeditepe University Kozyatağı Hospital') + stay_section('hospital') + CTA, ('partners', Y, 'hospitals'))
    P[('partners', Y, 'hospitals', 'kosuyolu-hospital')] = ('Yeditepe University Koşuyolu Hospital', intro(
        'Yeditepe University Koşuyolu Hospital in Kadıköy, on the Asian side of Istanbul, has 180 beds, six intensive care beds and nine operating theatres on 35,000 m² of indoor space. Around 100 specialists and academic physicians work at the hospital.', mi('s_card'))
        + section('About the hospital', para('The hospital focuses on neurosciences and oncology: neurosurgery, cancer surgery, medical oncology, bone marrow transplantation for children and adults, orthopaedics, thoracic surgery, ENT, general surgery, gastroenterology, nuclear medicine and interventional radiology.')
                  + para('An intraoperative 3 Tesla MRI scanner is installed in the neurosurgical operating theatre. As part of infection prevention, the surfaces of the hospital were treated with a boron-based antimicrobial coating developed at Yeditepe University.')
                  + para('Koşuyolu Hospital holds the JCI accreditation as an Academic Medical Center (valid until 2028).') + gallery(['s1', 's2', 's3']))
        + section('Departments', chips(svc('kosuyolu-hospital')))
        + addr('Koşuyolu Mah. Koşuyolu Cad. No: 168, 34718 Kadıköy / İstanbul', 'Nearest metro station: Ayrılık Çeşmesi.')
        + doc_btn('kosuyolu', 'Yeditepe University Koşuyolu Hospital') + stay_section('hospital') + CTA, ('partners', Y, 'hospitals'))
    P[('partners', Y, 'hospitals', 'dental-hospital')] = ('Yeditepe University Dental Hospital', intro(
        'Yeditepe University Dental Hospital on Bağdat Avenue in Göztepe (Kadıköy) is the dental hospital of Yeditepe University\'s Faculty of Dentistry. Around 200 staff work in 120 treatment units, and three operating theatres are available for procedures under general anaesthesia.', mi('d_card'))
        + section('About the hospital', para('The Dental Hospital is accredited by Joint Commission International (JCI); the accreditation was renewed in 2012, 2015, 2018 and 2022.') + gallery(['d1', 'd2', 'd3']))
        + section('Departments', ul(['Oral and Maxillofacial Surgery', 'Oral and Maxillofacial Radiology', 'Paediatric Dentistry', 'Endodontics', 'Oral Implantology',
                                    'Orthodontics', 'Periodontology', 'Prosthodontics', 'Restorative Dentistry'], 'medlux-chips'))
        + addr('Caddebostan Mah. Bağdat Cad. No: 238, 34728 Göztepe, Kadıköy / İstanbul', None) + CTA, ('partners', Y, 'hospitals'))
    P[('partners', Y, 'hospitals', 'eye-center')] = ('Yeditepe University Eye Center', intro(
        'Yeditepe University Eye Center in Beşiktaş, on the European side of Istanbul, opened on 17 January 2007 on 2,250 m². As part of Yeditepe University Hospitals it diagnoses and treats eye diseases in 15 specialist areas and trains eye specialists.', mi('e_card'))
        + section('About the centre', para('The centre is in the Balmumcu district, close to Barbaros Boulevard and Büyükdere Avenue.') + gallery(['e1', 'e2', 'e3']))
        + section('Departments', chips(svc('eye-center')))
        + addr('Balmumcu Mah. Şakir Kesebir Cad. Gazi Umur Paşa Sok. No: 28, 34349 Beşiktaş / İstanbul',
               'Fulya Darphane metro station (M7) is about a 7-minute walk away, Gayrettepe (M2) about 9 minutes.')
        + doc_btn('eye', 'Yeditepe University Eye Center') + stay_section('hospital') + CTA, ('partners', Y, 'hospitals'))
    P[('partners', Y, 'doctors')] = ('Doctors', doctors_html('yeditepe')
        + para('Information as published by Yeditepe University Hospitals. Which doctor treats you is agreed during your consultation.', 'medlux-doc-source') + CTA, ('partners', Y))

    # Celyxmed
    hub = [c for c in re.split(r'(?=<!-- wp:group \{"className":"medlux-card medlux-card\\u002d\\u002dphoto")', CLIN_HUB) if 'medlux-card--photo' in c]
    want = ('Plastic Surgery', 'Hair Transplantation', 'Dental and Oral Health', 'Medical Aesthetics')
    area_cards = []
    for w in want:
        for c in hub:
            if '<h3 class="wp-block-heading">%s</h3>' % w in c:
                area_cards.append(c[:c.rfind('<!-- /wp:group -->') + len('<!-- /wp:group -->')] + '\n\n')
    P[('partners', C)] = ('Celyxmed', intro(
        'Celyxmed is a clinic in Ataşehir, Istanbul, for plastic surgery, hair transplantation, dental treatments and medical aesthetics. Surgical procedures take place in JCI-accredited partner hospitals. MedLuxLife coordinates clinical treatments with Celyxmed.', C_IMG)
        + section('Certificates', ul(['USHAŞ certificate for international health tourism (Turkish Ministry of Health)', 'ISO 9001:2015 – quality management system',
                                      'ISO 13485:2016 – quality management for medical devices'], 'medlux-facts'))
        + section('Clinic and doctors', grid([
            photo_card(mi('c1'), 'Clinic', 'Location, facilities and photos of the Celyxmed clinic in Ataşehir.', [('Learn more', url(C, 'clinic'))]),
            photo_card(mi('c_team'), 'Doctors', 'The doctors and dentists of Celyxmed with their education and areas of interest.', [('Meet the doctors', url(C, 'doctors'))])]))
        + stay_section('clinic') + CTA, ('partners',))
    P[('partners', C, 'clinic')] = ('Clinic', intro(
        'The Celyxmed clinic is located in Ataşehir, on the Asian side of Istanbul. Consultations, dental treatments, hair transplants and medical aesthetic treatments take place here; surgical procedures are performed in JCI-accredited partner hospitals.', mi('c1'))
        + section('Facilities', ul(['Treatment rooms for medical aesthetics and dental treatment units',
                                    '3D imaging (VECTRA H2) for planning aesthetic treatments and HairMetrix™ hair analysis',
                                    'Two cafeteria areas – one for hair transplant patients and one for all other guests',
                                    'A lounge that also serves as a library', 'Valet service and on-site parking'], 'medlux-facts')
                  + gallery(['c2', 'c3', 'c4']))
        + section('Address', para('Atatürk Mahallesi, Girne Caddesi No: 31, 34758 Ataşehir / İstanbul', 'medlux-address'))
        + section('Doctors', para('The doctors and dentists of Celyxmed with their education and areas of interest.')
                  + buttons([('Meet the doctors', url(C, 'doctors'), 'medlux-btn-primary')]))
        + CTA, ('partners', C))
    P[('partners', C, 'doctors')] = ('Doctors', doctors_html('celyxmed')
        + para('Information as published by Celyxmed. Which doctor treats you is agreed during your consultation.', 'medlux-doc-source') + CTA, ('partners', C))
    for d in DOCS:
        pp = ('partners', PARTNER_PATH[d['partner']], 'doctors')
        P[pp + (d['slug'],)] = (doctor_title(d), doctor_page(d), pp)

    # Travel partner
    P[('partners', 'travel-partner')] = ('Travel partner', intro(
        'Flights, hotels, transfers and holiday packages are booked with our travel partner, a tour operator based in Germany. MedLuxLife acts as an intermediary: your travel contract is concluded with the tour operator named in your offer.', T_IMG)
        + section('What our travel partner books for you', ul([
            '<a href="https://medluxlife.de/travel/flight-tickets/">Flight Tickets</a>', '<a href="https://medluxlife.de/travel/hotel-reservation/">Hotel Reservation</a>',
            '<a href="https://medluxlife.de/travel/airport-transfer/">Airport Transfer</a>', '<a href="https://medluxlife.de/travel/holiday-packages/">Holiday Packages</a>',
            '<a href="https://medluxlife.de/travel/hajj-umrah/">Hajj &amp; Umrah</a>'], 'medlux-chips'))
        + section('Coming soon', para('We will introduce our travel partner on this page shortly.'))
        + CTA, ('partners',))
    return P


def api(method, url, data=None):
    a = ['curl', '-sS', '-X', method, url, '-H', 'Content-Type: application/json']
    r = subprocess.run(a + (['--data-binary', '@-'] if data else []), input=json.dumps(data).encode() if data else None, capture_output=True).stdout
    return json.loads(r)


def main(dry):
    global CLIN_HUB
    CLIN_HUB = api('GET', API + '/258?context=edit&_fields=content')['content']['raw']
    P = build()
    ids_f = ROOT / 'content/partners/pages.json'
    ids = json.load(open(ids_f)) if ids_f.exists() else {}
    import concurrent.futures as cf

    def post(path):
        title, content, parent = P[path]
        key = '/'.join(path)
        body = {'title': title, 'content': content, 'slug': path[-1], 'status': 'publish', 'template': 'page-with-title'}
        if parent:
            body['parent'] = ids['/'.join(parent)]
        r = api('POST', API + ('/%d' % ids[key] if ids.get(key) else ''), body)
        return key, r
    only = sys.argv[sys.argv.index('--only') + 1] if '--only' in sys.argv else ''
    for depth in sorted({len(p) for p in P}):
        level = [p for p in P if len(p) == depth and '/'.join(p).startswith(only) and (not only or '/'.join(p).count('/') == only.count('/') or '--sub' in sys.argv)]
        print('depth', depth, len(level), 'pages')
        if dry:
            continue
        with cf.ThreadPoolExecutor(4) as ex:
            for key, r in ex.map(post, level):
                if 'id' not in r:
                    print('  ERROR', key, str(r)[:300])
                    continue
                if not ids.get(key):
                    print('  new', r['id'], r['link'])
                ids[key] = r['id']
    if not dry:
        json.dump(ids, open(ids_f, 'w'), indent=1)
        import cache_clear
        print('page cache cleared:', cache_clear.clear())


if __name__ == '__main__':
    main('--dry' in sys.argv)
