"""Helpers that emit valid Gutenberg block markup for MedLuxLife treatment pages."""
import html, json

B = "https://medluxlife.de"
WHATSAPP = "https://wa.me/380979092326"

def esc(t): return html.escape(t, quote=False)

def p(text, cls=None):
    if cls:
        return f'<!-- wp:paragraph {{"className":"{cls}"}} -->\n<p class="{cls}">{text}</p>\n<!-- /wp:paragraph -->'
    return f'<!-- wp:paragraph -->\n<p>{text}</p>\n<!-- /wp:paragraph -->'

def h(text, level=2):
    attrs = '' if level == 2 else f' {{"level":{level}}}'
    return f'<!-- wp:heading{attrs} -->\n<h{level} class="wp-block-heading">{text}</h{level}>\n<!-- /wp:heading -->'

def ul(items):
    lis = "".join(f'<!-- wp:list-item -->\n<li>{i}</li>\n<!-- /wp:list-item -->' for i in items)
    return f'<!-- wp:list -->\n<ul class="wp-block-list">{lis}</ul>\n<!-- /wp:list -->'

def group(inner, cls, layout=None):
    layout = layout or {"type": "constrained"}
    a = json.dumps({"className": cls, "layout": layout}, separators=(',', ':'))
    return f'<!-- wp:group {a} -->\n<div class="wp-block-group {cls}">' + "\n\n".join(inner) + '</div>\n<!-- /wp:group -->'

def grid(cards, cls="medlux-treatment-grid"):
    return group(cards, cls, {"type": "grid", "minimumColumnWidth": "20rem"})

def card(title, body):
    return group([h(title, 3)] + body, "medlux-card")

def buttons(items):
    bs = "".join(
        f'<!-- wp:button {{"className":"{c}"}} -->\n<div class="wp-block-button {c}"><a class="wp-block-button__link wp-element-button" href="{u}"{t}>{l}</a></div>\n<!-- /wp:button -->'
        for l, u, c, t in items)
    return f'<!-- wp:buttons -->\n<div class="wp-block-buttons">{bs}</div>\n<!-- /wp:buttons -->'

def process():
    steps = [
        ("1. Free consultation", "Share your wishes and, if available, recent X-rays or photos. We answer your questions and explain the options."),
        ("2. Personal treatment plan", "Our partner specialists prepare a treatment plan and an estimated timeline tailored to you."),
        ("3. Travel &amp; treatment", "We coordinate your appointments, hotel and airport transfers, so you can focus on your treatment."),
        ("4. Aftercare", "We stay in touch after you return home and help with follow-up questions."),
    ]
    return group([h("How MedLuxLife supports you")] + [grid([card(t, [p(d)]) for t, d in steps], "medlux-steps")], "medlux-section")

def cta(topic):
    return group([
        h(f"Plan your {topic} with confidence"),
        p("Every treatment begins with a personal, no-obligation consultation. Contact us and we will get back to you as soon as possible."),
        buttons([
            ("Request a Free Consultation", B + "/contact/", "medlux-btn-primary", ""),
            ("WhatsApp", WHATSAPP, "medlux-btn-whatsapp", ' target="_blank" rel="noreferrer noopener"'),
        ]),
        p("The information on this page is for general guidance only and does not replace a medical consultation. Suitability for any treatment is assessed individually by a qualified doctor.", "medlux-disclaimer"),
    ], "medlux-cta")

def img(media_id, url, alt, cls="medlux-card-img"):
    a = json.dumps({"id": media_id, "sizeSlug": "large", "linkDestination": "none", "className": cls}, separators=(',', ':'))
    return (f'<!-- wp:image {a} -->\n<figure class="wp-block-image size-large {cls}">'
            f'<img src="{url}" alt="{html.escape(alt)}" class="wp-image-{media_id}"/></figure>\n<!-- /wp:image -->')

def card_img(title, body, image):
    """Card with a photo on top; image = (media_id, url, alt)."""
    return group([img(*image)] + [h(title, 3)] + body, "medlux-card medlux-card--photo")

def intro(lead_html, image):
    col = lambda inner: ('<!-- wp:column {"verticalAlignment":"center"} -->\n<div class="wp-block-column is-vertically-aligned-center">'
                         + inner + '</div>\n<!-- /wp:column -->')
    return ('<!-- wp:columns {"verticalAlignment":"center","className":"medlux-intro"} -->\n'
            '<div class="wp-block-columns are-vertically-aligned-center medlux-intro">'
            + col(p(lead_html, "medlux-lead")) + "\n\n" + col(img(*image, cls="medlux-intro-img"))
            + '</div>\n<!-- /wp:columns -->')
