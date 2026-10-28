#!/usr/bin/env python3
"""Emrah 2026-10-28: transfers in a black Mercedes Vito VIP; clinic treatments: Dedeman Kozyatağı (5*), accommodation for the
patient + one companion with breakfast, part of the treatment package (HWG §7: "included in the package", never "free");
hospital treatments: hotel options of different categories near the hospital, the patient chooses. Also the FAQ "no advance payment".
  - "Your stay and transfers" section before the CTA on the clinical (258) and hospital (259) hub pages (2 photo cards)
  - travel step 3: clinic variant on 258 + clinical category pages, hospital variant on 259 + hospital pages (Health hub 27 unchanged)
  - FAQ: home (23) and contact (26): stay, transfers, no advance payment; 25 clinical treatment pages: stay + transfers
Backups in backups/wp/stay/. usage: stay_transfer.py [--dry]"""
import json, pathlib, re, subprocess, sys, time
ROOT = pathlib.Path(__file__).resolve().parent.parent
W = 'https://medluxlife-6j8sz55bpn.live-website.com/wp-json/wp/v2/pages/'
HOTEL, VITO = 2605, 2951
UP = 'https://medluxlife.de/wp-content/uploads/2026/10/'
OLD_STEP = 'We coordinate your appointments, hotel and airport transfers, so you can focus on your treatment.'
STEP_CLINIC = 'We coordinate your appointments, your stay at the five-star Dedeman Kozyatağı and your transfers in a black Mercedes Vito VIP, so you can focus on your treatment.'
STEP_HOSPITAL = 'We coordinate your appointments, suggest hotels near your hospital and arrange your transfers in a black Mercedes Vito VIP, so you can focus on your treatment.'
CLINIC_HUBS = {258, 260, 261, 263, 264, 265, 266, 267}

Q1 = ('Where will I stay during my treatment?',
      'For clinic treatments you stay at the five-star Dedeman Kozyatağı hotel in Istanbul. Your treatment package includes accommodation for you and one companion, with breakfast. For hospital treatments we suggest hotels of different categories close to your hospital, and you choose the one that suits you.')
Q2 = ('How do I get to the hotel, the clinic or the hospital?',
      'All transfers during your treatment – from the airport to your hotel, to the clinic or hospital and back – are made in a black Mercedes Vito VIP vehicle.')
Q3 = ('Do I have to pay in advance for my treatment?',
      'No. MedLuxLife does not take any advance payment or deposit for treatments. You pay the full cost of your treatment directly at the clinic or hospital where you are treated.')
QC = ('Where will I stay, and how do I get to the clinic?',
      'You stay at the five-star Dedeman Kozyatağı hotel in Istanbul. Your treatment package includes accommodation for you and one companion, with breakfast. All transfers – airport, hotel and clinic – are made in a black Mercedes Vito VIP vehicle.')


def item(q, a, home=False):
    st = ' {"style":{"typography":{"fontSize":"1.5rem"}}}' if home else ''
    cls = ' has-icon has-icon-right" style="font-size:1.5rem' if home else ''
    return ('<!-- wp:accordion-item {"style":{"spacing":{"blockGap":"0"}}} -->\n<div class="wp-block-accordion-item"><!-- wp:accordion-heading%s -->\n'
            '<h3 class="wp-block-accordion-heading%s"><button type="button" class="wp-block-accordion-heading__toggle"><span class="wp-block-accordion-heading__toggle-title">%s</span>'
            '<span class="wp-block-accordion-heading__toggle-icon" aria-hidden="true">+</span></button></h3>\n<!-- /wp:accordion-heading -->\n\n'
            '<!-- wp:accordion-panel -->\n<div role="region" class="wp-block-accordion-panel"><!-- wp:paragraph -->\n<p>%s</p>\n<!-- /wp:paragraph --></div>\n'
            '<!-- /wp:accordion-panel --></div>\n<!-- /wp:accordion-item -->\n\n') % (st, cls, q, a)


def card(img_id, file, alt, h3, text, note=''):
    cap = '<figcaption class="wp-element-caption">%s</figcaption>' % note if note else ''
    return ('<!-- wp:group {"className":"medlux-card medlux-card\\u002d\\u002dphoto","layout":{"type":"constrained"}} -->\n'
            '<div class="wp-block-group medlux-card medlux-card--photo"><!-- wp:image {"id":%d,"sizeSlug":"large","linkDestination":"none","className":"medlux-card-img"} -->\n'
            '<figure class="wp-block-image size-large medlux-card-img"><img src="%s%s" alt="%s" class="wp-image-%d"/>%s</figure>\n<!-- /wp:image -->\n\n'
            '<!-- wp:heading {"level":3} -->\n<h3 class="wp-block-heading">%s</h3>\n<!-- /wp:heading -->\n\n'
            '<!-- wp:paragraph -->\n<p>%s</p>\n<!-- /wp:paragraph --></div>\n<!-- /wp:group -->\n\n') % (img_id, UP, file, alt, img_id, cap, h3, text)


def section(intro, c1, c2):
    return ('<!-- wp:group {"className":"medlux-section medlux-stay","layout":{"type":"constrained"}} -->\n<div class="wp-block-group medlux-section medlux-stay"><!-- wp:heading -->\n'
            '<h2 class="wp-block-heading">Your stay and transfers</h2>\n<!-- /wp:heading -->\n\n<!-- wp:paragraph {"className":"medlux-stay-intro"} -->\n'
            '<p class="medlux-stay-intro">%s</p>\n<!-- /wp:paragraph -->\n\n'
            '<!-- wp:group {"className":"medlux-treatment-grid medlux-stay-grid","layout":{"type":"grid","minimumColumnWidth":"20rem"}} -->\n'
            '<div class="wp-block-group medlux-treatment-grid medlux-stay-grid">%s%s</div>\n<!-- /wp:group --></div>\n<!-- /wp:group -->\n\n') % (intro, c1, c2)


HOTEL_ALT = 'Hotel room with a large bed and a city view at night (symbolic image)'
VITO_ALT = 'Black Mercedes van for VIP transfers in front of a modern building'
SEC_CLINIC = section('For clinic treatments, accommodation and transfers are part of your treatment package.',
                     card(HOTEL, 'medluxlife-hotel-room-symbolic.jpg', HOTEL_ALT, 'Five-star hotel: Dedeman Kozyatağı',
                          'You stay at the five-star Dedeman Kozyatağı hotel in Istanbul. Your treatment package includes accommodation for you and one companion, with breakfast.'),
                     card(VITO, 'medluxlife-vip-transfer-mercedes-side.jpg', VITO_ALT, 'VIP Transfer Service',
                          'All transfers – from the airport to your hotel, between the hotel and the clinic, and back to the airport – are made in a black Mercedes Vito VIP vehicle.'))
SEC_HOSPITAL = section('For hospital treatments, you choose your hotel and we arrange your transfers.',
                       card(HOTEL, 'medluxlife-hotel-room-symbolic.jpg', HOTEL_ALT, 'Hotels near your hospital',
                            'We suggest hotels of different categories close to the hospital where you are treated. You choose the hotel that suits your wishes.'),
                       card(VITO, 'medluxlife-vip-transfer-mercedes-side.jpg', VITO_ALT, 'VIP Transfer Service',
                            'All transfers – from the airport to your hotel, between the hotel and the hospital, and back to the airport – are made in a black Mercedes Vito VIP vehicle.'))


def item_start(c, question):
    """offset of the accordion item whose title is `question` (title may be wrapped in trp_language shortcodes)"""
    q = c.find(question)
    return -1 if q < 0 else c.rfind('<!-- wp:accordion-item', 0, q)


def item_end(c, question):
    s = item_start(c, question)
    e = c.find('<!-- /wp:accordion-item -->', s)
    return e + len('<!-- /wp:accordion-item -->\n\n')


def change(pid, c, link):
    new = c
    if pid in (258, 259) and 'medlux-stay' not in new:
        k = new.find('<!-- wp:group {"className":"medlux-cta"')
        new = new[:k] + (SEC_CLINIC if pid == 258 else SEC_HOSPITAL) + new[k:]
    if OLD_STEP in new and pid != 27:
        new = new.replace(OLD_STEP, STEP_CLINIC if (pid in CLINIC_HUBS or '/clinical-treatments/' in link) else STEP_HOSPITAL)
    if pid == 23 and Q1[0] not in new:
        e = item_end(new, 'Do you provide travel and accommodation services?')
        new = new[:e] + item(*Q1, home=True) + item(*Q2, home=True) + item(*Q3, home=True) + new[e:]
    if pid == 26 and Q1[0] not in new:
        e = item_end(new, 'Where do the treatments take place?')
        new = new[:e] + item(*Q1) + item(*Q2) + new[e:]
        e = item_end(new, 'How much does a treatment cost?')
        new = new[:e] + item(*Q3) + new[e:]
    if '/clinical-treatments/' in link and QC[0] not in new and 'Should I send photos or medical documents to MedLuxLife?' in new:
        s = item_start(new, 'Should I send photos or medical documents to MedLuxLife?')
        new = new[:s] + item(*QC) + new[s:]
    return new


def main(dry):
    pages = []
    for n in (1, 2):
        pages += json.loads(subprocess.run(['curl', '-sS', W + '?per_page=100&page=%d&context=edit&_fields=id,link,content,modified' % n], capture_output=True).stdout)
    stamp = time.strftime('%Y%m%d_%H%M%S')
    todo = []
    for p in pages:
        c = p['content']['raw']; new = change(p['id'], c, p['link'])
        if new != c:
            todo.append((p, new))
    print('pages to change:', len(todo))
    if dry:
        return todo
    json.dump([{'id': p['id'], 'link': p['link'], 'modified': p['modified'], 'content': p['content']['raw']} for p, _ in todo],
              open(ROOT / ('backups/wp/stay/pages_before_stay_%s.json' % stamp), 'w'), ensure_ascii=False)
    for p, new in todo:
        r = subprocess.run(['curl', '-sS', '-X', 'POST', W + str(p['id']), '-H', 'Content-Type: application/json', '--data-binary', '@-'],
                           input=json.dumps({'content': new}).encode(), capture_output=True).stdout
        ok = json.loads(r).get('id') == p['id']
        print(p['id'], p['link'].replace('https://medluxlife.de', ''), 'ok' if ok else r[:200])
    sys.path.insert(0, str(ROOT / 'tools')); import cache_clear; print('page cache cleared:', cache_clear.clear())


if __name__ == '__main__':
    main('--dry' in sys.argv)
