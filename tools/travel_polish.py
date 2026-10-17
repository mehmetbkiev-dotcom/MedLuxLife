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
_HOTEL = '<rect x="12" y="6" width="24" height="36" rx="1"/><path d="M6 42h36"/><path d="M18 13h4M26 13h4M18 20h4M26 20h4M18 27h4M26 27h4"/><path d="M21 42v-7h6v7"/>'
_FAMILY = '<circle cx="17" cy="11" r="5"/><path d="M8 42V28a9 9 0 0 1 18 0v14"/><circle cx="34" cy="21" r="4"/><path d="M28 42v-9a6 6 0 0 1 12 0v9"/>'
_ROUTE = '<circle cx="10" cy="34" r="4"/><path d="M14 34h8a6 6 0 0 0 6-6v-8a6 6 0 0 1 6-6h4"/><path d="M35 10l4 4-4 4"/>'
_BUS = '<path d="M4 30V14a3 3 0 0 1 3-3h26l9 9v10a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2z"/><path d="M4 21h38M13 11v10M23 11v10"/><circle cx="13" cy="33" r="4"/><circle cx="33" cy="33" r="4"/>'
_SUITCASE = '<rect x="8" y="14" width="32" height="24" rx="3"/><path d="M18 14V9a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v5"/><path d="M8 24h32"/>'
_GLOBE = '<circle cx="24" cy="24" r="18"/><path d="M6 24h36M24 6c5 5 7.5 11 7.5 18S29 37 24 42M24 6c-5 5-7.5 11-7.5 18S19 37 24 42"/>'
_CHAT = '<circle cx="20" cy="18" r="8"/><path d="M4 42c0-8.8 7.2-15 16-15s16 6.2 16 15"/><path d="M31 4h13a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2h-8l-4 3v-3h-1a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z"/>'
ICONS.update({
    # Hotel Reservation
    'City hotels': svg(_HOTEL),
    'Resorts and five-star hotels': svg('<path d="M24 6l5.3 10.8 11.9 1.7-8.6 8.4 2 11.8L24 33.1l-10.6 5.6 2-11.8-8.6-8.4 11.9-1.7z"/>'),
    'Boutique hotels': svg('<path d="M10 34a14 14 0 0 1 28 0z"/><path d="M6 38h36"/><path d="M24 20v-4M21 16h6"/>'),
    'Families and groups': svg(_FAMILY),
    'Short and long stays': svg('<rect x="6" y="10" width="36" height="32" rx="3"/><path d="M6 20h36M16 6v8M32 6v8"/><path d="M14 28h4M22 28h4M30 28h4M14 35h4M22 35h4"/>'),
    'Special requests': svg('<path d="M8 10h32a3 3 0 0 1 3 3v17a3 3 0 0 1-3 3H20l-8 7v-7H8a3 3 0 0 1-3-3V13a3 3 0 0 1 3-3z"/><circle cx="16" cy="21.5" r="1.5"/><circle cx="24" cy="21.5" r="1.5"/><circle cx="32" cy="21.5" r="1.5"/>'),
    # Airport Transfer
    'Meet and greet': svg('<rect x="20" y="6" width="22" height="13" rx="2"/><path d="M25 12.5h12"/><circle cx="12" cy="14" r="5"/><path d="M4 42V31a8 8 0 0 1 16 0v11"/><path d="M18 25l5-6"/>'),
    'Airport to hotel': svg(_ROUTE),
    'City and excursion transfers': svg('<path d="M6 32v-6l4-9a3 3 0 0 1 3-2h22a3 3 0 0 1 3 2l4 9v6a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2z"/><path d="M8 26h32"/><circle cx="15" cy="34" r="4"/><circle cx="33" cy="34" r="4"/>'),
    'Return to the airport': svg(_SUITCASE),
    'Vehicles for every group': svg(_BUS),
    'Help on the way': svg('<rect x="14" y="4" width="20" height="40" rx="4"/><path d="M21 38h6"/>'),
    # Hajj & Umrah
    'Umrah': svg('<path d="M30 6a18 18 0 1 0 12 30A15 15 0 0 1 30 6z"/>'),
    'Hajj': svg('<path d="M24 6l16 7v20l-16 9-16-9V13z"/><path d="M8 13l16 7 16-7M24 20v22"/><path d="M8 19l16 7 16-7"/>'),
    'Visa guidance': svg('<rect x="10" y="4" width="28" height="40" rx="3"/><circle cx="24" cy="20" r="7"/><path d="M17 20h14M24 13c2.5 2 2.5 12 0 14M24 13c-2.5 2-2.5 12 0 14"/><path d="M17 34h14"/>'),
    'Flights': svg('<path d="M6 14h36v6a4 4 0 0 0 0 8v6H6v-6a4 4 0 0 0 0-8z"/><path d="M30 16v16" stroke-dasharray="3 3"/>'),
    'Hotels near the holy mosques': svg(_HOTEL),
    'Transfers and guidance': svg(_BUS),
    # Flight Tickets
    'International flights': svg(_GLOBE),
    'Domestic flights': svg('<path d="M24 44s14-13 14-24a14 14 0 0 0-28 0c0 11 14 24 14 24z"/><circle cx="24" cy="20" r="5"/>'),
    'One-way, return and multi-city': svg('<path d="M6 16h30"/><path d="M30 10l6 6-6 6"/><path d="M42 32H12"/><path d="M18 26l-6 6 6 6"/>'),
    'Economy, business and first class': svg('<path d="M16 6c-2 0-3 1.5-3 3l2 21a4 4 0 0 0 4 3.5h15"/><path d="M19 26h13a4 4 0 0 1 4 4v3.5"/><path d="M24 33.5V42M18 42h12"/>'),
    'Group and family bookings': svg(_FAMILY),
    'Baggage and seat selection': svg(_SUITCASE),
    'Changes and cancellations': svg('<path d="M38 18A15 15 0 0 0 10 16"/><path d="M10 8v8h8"/><path d="M10 30a15 15 0 0 0 28 2"/><path d="M38 40v-8h-8"/>'),
    'Personal advice': svg(_CHAT),
})

def icon_block(uri):
    return ('<!-- wp:image {"className":"medlux-card-icon"} -->\n<figure class="wp-block-image medlux-card-icon"><img src="%s" alt=""/></figure>\n<!-- /wp:image -->\n\n' % uri)

# new intro texts in the spirit of About Us (Anna, 2026-10-17): we adapt to you, anywhere in the world, one personal contact
INTROS = {
    275: ('Your holiday should feel like yours. Tell us where you would like to go – to the coast, to a historic city or '
          'to a quiet resort, anywhere in the world – and we put together a package that fits your wishes, your budget '
          'and your schedule: flights, hotel, transfers and excursions in one plan. Whatever you have in mind, we find '
          'a way – and one personal contact takes care of everything.'),
    276: ('The right hotel makes all the difference. Tell us where you are going and what matters to you – a central city '
          'hotel, a resort by the sea or a small boutique hotel, for a few nights or a longer stay – and we find and book '
          'the place that suits your wishes, your budget and your schedule, with one personal contact for everything.'),
    277: ('Arrive relaxed: a private driver meets you at the airport and takes you directly to your hotel. We also arrange '
          'transfers for excursions, meetings and events and back to the airport – planned around your flights, your '
          'luggage and your group, with one personal contact for everything.'),
    278: ('Hajj and Umrah are journeys of the heart. We help you prepare calmly and organise the practical details – '
          'flights, hotels near the holy mosques, transfers and visa guidance – in cooperation with licensed partners and '
          'around your wishes, your budget and your dates, so that you can focus on your spiritual journey.'),
    283: ('Whether for a holiday, a business trip or a visit to family and friends – we find the flights that suit your '
          'dates, your budget and your plans, book them for you and stay by your side if plans change, just like a '
          'personal travel office.'),
}

# step 2 "Personal offer" written for each page (it said "flights, hotel and transfers" everywhere)
STEP2 = {
    276: 'We prepare a tailored hotel proposal for your dates and wishes, without obligation.',
    277: 'We prepare a tailored proposal for your transfers, without obligation.',
    278: 'We prepare a tailored proposal for your journey – flights, hotel and transfers – without obligation.',
    283: 'We prepare a tailored flight proposal for your dates and route, without obligation.',
}
# small text fixes
FIXES = {
    283: [('Domestic flights within Turkey and other countries.', 'Domestic flights within Türkiye and other countries.')],
}

def polish(pid):
    c = json.loads((ROOT / f'backups/wp/page{pid}_before_travel_polish.json').read_text())['content']['raw']
    if pid in INTROS:
        c, n_intro = re.subn(r'(<p class="medlux-lead">)[^<]*(</p>)', lambda m: m.group(1) + INTROS[pid] + m.group(2), c, count=1)
        assert n_intro == 1, 'intro not found'
    if pid in STEP2:
        old2 = 'We prepare a tailored proposal for flights, hotel and transfers, without obligation.'
        assert c.count(old2) == 1, 'step 2 text not found'
        c = c.replace(old2, STEP2[pid])
    for a, b in FIXES.get(pid, []):
        assert a in c, 'fix not found: ' + a
        c = c.replace(a, b)
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
