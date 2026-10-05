"""Health hub page (27) and Clinical Treatments overview page (258)."""
import json, os
from blocks import *
from hospital_pages import FEATURED, featured_card, H, C

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = {k: tuple(v) for k, v in json.load(open(os.path.join(HERE, 'images.json'))).items()}
IMG["dental-hero"] = (295, "https://medluxlife-6j8sz55bpn.live-website.com/wp-content/uploads/2026/10/medluxlife-dental-hero-1024x966.jpg", "Smiling patient during a dental check-up")

CLINICAL = [
    ("Dental and Oral Health", "dental-and-oral-health", "dental-hero", "Hollywood Smile, implants, zirconium veneers, orthodontics and complete dental care."),
    ("Hair Transplantation", "hair-transplantation", "hair-transplant-surgery", "FUE, Sapphire FUE and DHI hair, beard and eyebrow transplants, plus restorative hair therapies."),
    ("Plastic Surgery", "plastic-surgery", "plastic-surgery", "Face and body procedures, from rhinoplasty and facelift to mommy makeover and liposuction."),
    ("Medical Aesthetics", "medical-aesthetics", "aesthetics", "Botox, dermal fillers, mesotherapy and exosome treatments with little or no downtime."),
    ("Bariatric Surgery", "bariatric-surgery", "bariatric-surgery", "Gastric sleeve, gastric bypass and gastric balloon in a supportive, respectful setting."),
    ("Check-Up Packages", "check-up-packages", "check-up", "Comprehensive health check-ups for men and women, tailored to every stage of life."),
    ("IV Treatments", "iv-treatments", "iv-treatments", "Vitamin and nutrient infusions to support energy, regeneration and well-being."),
]

def clinical_card(title, slug, img, summary):
    return card_img(title, [p(summary), p(f'<a href="{C}{slug}/">Learn more →</a>', "medlux-more")], IMG[img])

def more_button(label, url):
    return buttons([(label, url, "medlux-btn-primary", "")])

WHY = [
    ("Personal coordinator", "One contact person who speaks your language and accompanies you from the first question to your return home."),
    ("Trusted partners", "Carefully selected clinics and hospitals with experienced specialists."),
    ("Treatment and travel in one plan", "Appointments, hotel, flights and airport transfers, coordinated for you."),
    ("Aftercare", "We stay in touch after your treatment and help with follow-up questions."),
]

def hub_box(img, title, text, links, all_label, all_url):
    items = [f'<a href="{u}">{l}</a>' for l, u in links]
    inner = [img_block(IMG[img]), h(title), p(text), ul(items), buttons([(all_label, all_url, "medlux-btn-primary", "")])]
    return ('<!-- wp:column {"className":"medlux-hub-box"} -->\n<div class="wp-block-column medlux-hub-box">'
            + "\n\n".join(inner) + '</div>\n<!-- /wp:column -->')

def img_block(image):
    return img(*image, cls="medlux-hub-img")

HUB = ('<!-- wp:columns {"className":"medlux-hub"} -->\n<div class="wp-block-columns medlux-hub">'
       + hub_box("aesthetics", "Clinical Treatments",
                 "Aesthetic, dental and hair treatments, weight-loss surgery, check-ups and IV therapies with experienced partner clinics.",
                 [(t, C + s + "/") for t, s, _, _ in CLINICAL], "View all clinical treatments", C)
       + "\n\n"
       + hub_box("check-up-women", "Hospital &amp; Specialist Treatments",
                 "Specialist hospital care across more than 70 departments, from oncology and cardiology to transplantation and fertility treatment.",
                 [(t, H + s + "/") for _, t, s, _ in FEATURED], "View all departments", H)
       + '</div>\n<!-- /wp:columns -->')

HEALTH = "\n\n".join([
    intro("MedLuxLife connects you with professional healthcare and carefully plans every step of your journey. Whether you are looking for an aesthetic or dental treatment or for specialist hospital care, we help you find the right specialists, prepare your treatment and organise your stay.", IMG["dental-hero"]),
    group([h("Our health services"), HUB], "medlux-section"),
    group([h("Why MedLuxLife"), grid([card(t, [p(d)]) for t, d in WHY], "medlux-steps")], "medlux-section"),
    process(),
    cta("treatment"),
])

CLINICAL_PAGE = "\n\n".join([
    intro("Our clinical treatments cover aesthetic, dental and hair treatments, weight-loss surgery, health check-ups and IV therapies. Experienced partner clinics carry out each treatment, while MedLuxLife plans your appointments, travel and stay and remains your point of contact throughout.", IMG["dental-hero"]),
    group([h("Our clinical treatments"), grid([clinical_card(*c) for c in CLINICAL])], "medlux-section"),
    process(),
    cta("treatment"),
])

PAGES = {27: HEALTH, 258: CLINICAL_PAGE}
