"""Department pages for every entry of 'All departments' (content rewritten from the partner hospital's service pages)."""
import json, re, glob, os
from blocks import *
from hospital_pages import DOCS, prepare, H, C, link

HERE = os.path.dirname(os.path.abspath(__file__))
DEPTS = {}
for f in sorted(glob.glob(os.path.join(HERE, 'depts_part*.json'))):
    DEPTS.update(json.load(open(f)))
DIMG = {k: tuple(v) for k, v in json.load(open(os.path.join(HERE, 'dept_images.json'))).items()}

def slugify(t):
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', t.lower().replace('&', 'and'))).strip('-')

def page_slug(src_slug):
    return slugify(DEPTS[src_slug]['title'])

def build(src_slug):
    d = DEPTS[src_slug]
    parts = [intro(esc(d['lead']), DIMG[src_slug]),
             group([h("Treatments and services"), grid([card(esc(t), [p(esc(x))]) for t, x in d['cards']])], "medlux-section")]
    if d.get('list'):
        parts.append(group([h(esc(d.get('list_heading') or 'Conditions treated')), ul([esc(i) for i in d['list']])],
                           "medlux-section" + (" medlux-columns" if len(d['list']) > 8 else "")))
    parts += [prepare(DOCS + [esc(x) for x in d.get('docs_extra', [])]), process(), cta(esc(d['title']) + " consultation")]
    return "\n\n".join(parts)

# Category layout of the main page; values are hospital source slugs, or ('label', url) for pages that live elsewhere.
FEATURED_URL = {
    'medical-oncology': ("Medical Oncology", H + "medical-oncology/"), 'cardiology': ("Cardiology", H + "cardiology/"),
    'orthopedics-and-traumatology': ("Orthopedics and Traumatology", H + "orthopedics-and-traumatology/"),
    'vitro-fertilization-ivf': ("In-Vitro Fertilization (IVF)", H + "in-vitro-fertilization-ivf/"),
    'neurosurgery': ("Neurosurgery", H + "neurosurgery/"), 'ophthalmology': ("Ophthalmology", H + "ophthalmology/"),
    'organ-transplantation-center': ("Organ Transplantation Center", H + "organ-transplantation-center/"),
    'obesity-surgery': ("Obesity Surgery", C + "bariatric-surgery/"),
    'plastic-reconstructive-and-aesthetic-surgery': ("Plastic, Reconstructive and Aesthetic Surgery", C + "plastic-surgery/"),
}
CATEGORIES = [
    ("Cancer care", ['medical-oncology', 'gynecological-oncology', 'hematology', 'adult-bone-marrow-transplantation', 'applications-nuclear-medicine']),
    ("Heart and vascular", ['cardiology', 'cardiovascular-surgery', 'interventional-radiology']),
    ("Brain, nerves and mental health", ['neurosurgery', 'neurology', 'algology', 'psychiatry', 'psychology']),
    ("Bones, joints and rehabilitation", ['orthopedics-and-traumatology', 'physical-therapy-and-rehabilitation', 'rheumatology']),
    ("Transplantation", ['organ-transplantation-center', 'kidney-transplant-clinic', 'liver-transplant-clinic', 'parathyroid-transplant-clinic']),
    ("Women's health and fertility", ['vitro-fertilization-ivf', 'obstetrics-and-gynecology', 'perinatology', 'pelvic-pain-and-endometriosis-clinic',
                                      'pcos-and-hirsutism-clinic', 'hirsutism-clinic', 'breast-surgery']),
    ("Eye, ear, nose and throat", ['ophthalmology', 'otolaryngology-ent', 'audiology']),
    ("Surgery", ['general-surgery', 'gastroenterological-surgery', 'endocrine-surgery', 'thoracic-surgery', 'urology',
                 'obesity-surgery', 'plastic-reconstructive-and-aesthetic-surgery']),
    ("Internal medicine", ['internal-medicine', 'endocrinology-and-metabolism-diseases', 'thyroid-parathyroid-diseases-and-surgery-clinic', 'pituitary-clinic',
                           'gastroenterology', 'nephrology', 'chest-diseases', 'infectious-diseases-and-microbiology', 'immunology', 'dermatology', 'nutrition-and-dietetics']),
    ("Children's health", ['pediatrics', 'pediatric-surgery', 'pediatric-cardiology', 'pediatric-oncology', 'pediatric-hematology',
                           'pediatric-bone-marrow-transplantation', 'pediatric-neurology', 'pediatric-nephrology', 'pediatric-endocrinology',
                           'pediatric-gastroenterology-hepatology-and-nutrition', 'pediatric-allergy-and-immunology', 'pediatric-infectious-diseases',
                           'pediatric-rheumatology', 'child-and-adolescent-psychiatry', 'newborn-intensive-care-unit-nicu']),
    ("Diagnostics, emergency and intensive care", ['radiology', 'imaging-unit', 'medical-genetics', 'medical-pathology', 'medical-microbiology',
                                                  'medical-histology-and-embryology', 'transfusion-center', 'emergency-medicine', 'intensive-care-unit',
                                                  'anesthesiology-and-reanimation']),
]

def groups_with_links():
    out = []
    for title, slugs in CATEGORIES:
        items = []
        for s in slugs:
            if s in FEATURED_URL:
                items.append(link(*FEATURED_URL[s]))
            else:
                items.append(link(esc(DEPTS[s]['title']), H + page_slug(s) + "/"))
        out.append((title, items))
    return out
