"""FAQ section for the Contact page (26): HWG-safe, health and travel kept separate, no prices."""
import sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from blocks import B

FAQ = [
    ("How does the free consultation work?",
     "Send us your enquiry via the contact form, by email or on WhatsApp. We will get back to you, talk through your wishes and explain the next steps. The first consultation is free of charge and non-binding."),
    ("Does MedLuxLife carry out medical treatments itself?",
     "No. MedLuxLife informs, organises and coordinates. Treatments are carried out by qualified doctors at our partner hospital and partner clinics, and the treatment contract is concluded directly with them. Whether a treatment is suitable for you is decided by the treating doctor."),
    ("Where do the treatments take place?",
     "At our partner hospital and partner clinics in Türkiye. We coordinate your appointments, accommodation and transfers so that you can concentrate on your treatment."),
    ("Should I send medical documents with my first enquiry?",
     "Please do not send detailed medical information or documents via the contact form or WhatsApp. If documents are needed, we will ask you for them separately and only with your explicit consent."),
    ("How much does a treatment cost?",
     "Every treatment is planned individually, so we do not publish prices on our website. After the consultation you receive a personal written offer."),
    ("Can I book travel services without a treatment?",
     "Yes. Our travel services – holiday packages, hotel reservations, flight tickets, airport transfers and Hajj &amp; Umrah – are independent of our health services and can be booked on their own."),
    ("Do you arrange Hajj and Umrah trips?",
     "Yes. We arrange Hajj and Umrah trips together with licensed tour operators and inform you about the passport, visa and vaccination requirements."),
    ("Which languages do you speak?",
     "We are happy to assist you in German, English, Turkish, Ukrainian and Russian."),
    ("Where is MedLuxLife based?",
     "MedLuxLife is based in Aachen, Germany."),
    ("How can I cancel a booking?",
     f'Please send your cancellation to info@medluxlife.de. Details can be found in our <a href="{B}/stornierungsbedingungen/">cancellation policy</a> and our <a href="{B}/widerrufsbelehrung/">withdrawal information</a>.'),
]

def item(q, a, open_=False):
    attrs = '{"openByDefault":true,"style":{"spacing":{"blockGap":"0"}}}' if open_ else '{"style":{"spacing":{"blockGap":"0"}}}'
    cls = "wp-block-accordion-item is-open" if open_ else "wp-block-accordion-item"
    return (f'<!-- wp:accordion-item {attrs} -->\n<div class="{cls}"><!-- wp:accordion-heading -->\n'
            f'<h3 class="wp-block-accordion-heading"><button type="button" class="wp-block-accordion-heading__toggle"><span class="wp-block-accordion-heading__toggle-title">{q}</span><span class="wp-block-accordion-heading__toggle-icon" aria-hidden="true">+</span></button></h3>\n'
            '<!-- /wp:accordion-heading -->\n\n<!-- wp:accordion-panel -->\n<div role="region" class="wp-block-accordion-panel"><!-- wp:paragraph -->\n'
            f'<p>{a}</p>\n<!-- /wp:paragraph --></div>\n<!-- /wp:accordion-panel --></div>\n<!-- /wp:accordion-item -->')

def column(items):
    inner = "\n\n".join(items)
    return ('<!-- wp:column {"className":"ext-animate\\u002d\\u002don","style":{"spacing":{"blockGap":"var:preset|spacing|40"}}} -->\n'
            '<div class="wp-block-column ext-animate--on"><!-- wp:accordion {"className":"medlux-faq","style":{"spacing":{"blockGap":"var:preset|spacing|20"}},"layout":{"type":"default"}} -->\n'
            f'<div role="group" class="wp-block-accordion medlux-faq">{inner}</div>\n<!-- /wp:accordion --></div>\n<!-- /wp:column -->')

def faq_columns():
    its = [item(q, a, i == 0) for i, (q, a) in enumerate(FAQ)]
    half = (len(its) + 1) // 2
    return ('<!-- wp:columns {"align":"wide","style":{"spacing":{"blockGap":{"top":"var:preset|spacing|20","left":"var:preset|spacing|40"}}}} -->\n'
            '<div class="wp-block-columns alignwide">' + column(its[:half]) + "\n\n" + column(its[half:]) + '</div>\n<!-- /wp:columns -->')
