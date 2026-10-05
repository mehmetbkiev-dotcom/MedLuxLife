"""Content for Hospital & Specialist Treatments (main page 259 and the seven featured specialty pages)."""
import json
from blocks import *

IMG = {k: tuple(v) for k, v in json.load(open(__file__.rsplit('/', 1)[0] + '/images.json')).items()}
H = B + "/health/hospital-specialist-treatments/"
C = B + "/health/clinical-treatments/"

FEATURED = [  # (page id, title, slug, one-line summary)
    (268, "Medical Oncology", "medical-oncology", "Diagnosis, second opinions and modern cancer treatment planned by multidisciplinary teams."),
    (269, "Cardiology", "cardiology", "Heart check-ups, diagnostics and interventional procedures for heart and vascular conditions."),
    (270, "Orthopedics and Traumatology", "orthopedics-and-traumatology", "Joint replacement, arthroscopy, spine and sports injuries, with rehabilitation."),
    (271, "In-Vitro Fertilization (IVF)", "in-vitro-fertilization-ivf", "Fertility assessment and assisted reproduction with personal, discreet care."),
    (272, "Neurosurgery", "neurosurgery", "Surgery of the brain, spine and nerves using modern, minimally invasive techniques."),
    (273, "Ophthalmology", "ophthalmology", "Cataract, refractive (laser) surgery, retina and other eye treatments."),
    (274, "Organ Transplantation Center", "organ-transplantation-center", "Kidney and liver transplantation, including living-donor programmes."),
]

def link(label, url):
    return f'<a href="{url}">{label}</a>'

def featured_card(pid, title, slug, summary):
    return card(title, [p(summary), p(link("Learn more →", H + slug + "/"), "medlux-more")])

GROUPS = [
    ("Cancer care", [link("Medical Oncology", H + "medical-oncology/"), "Gynaecological Oncology", "Haematology", "Adult Bone Marrow Transplantation", "Nuclear Medicine"]),
    ("Heart and vascular", [link("Cardiology", H + "cardiology/"), "Cardiovascular Surgery", "Interventional Radiology"]),
    ("Brain, nerves and mental health", [link("Neurosurgery", H + "neurosurgery/"), "Neurology", "Algology (Pain Medicine)", "Psychiatry", "Psychology"]),
    ("Bones, joints and rehabilitation", [link("Orthopedics and Traumatology", H + "orthopedics-and-traumatology/"), "Physical Therapy and Rehabilitation", "Rheumatology"]),
    ("Transplantation", [link("Organ Transplantation Center", H + "organ-transplantation-center/"), "Kidney Transplant Clinic", "Liver Transplant Clinic", "Parathyroid Transplant Clinic"]),
    ("Women's health and fertility", [link("In-Vitro Fertilization (IVF)", H + "in-vitro-fertilization-ivf/"), "Obstetrics and Gynaecology", "Perinatology", "Pelvic Pain and Endometriosis Clinic", "PCOS and Hirsutism Clinic", "Breast Surgery"]),
    ("Eye, ear, nose and throat", [link("Ophthalmology", H + "ophthalmology/"), "Otolaryngology (ENT)", "Audiology"]),
    ("Surgery", ["General Surgery", "Gastroenterological Surgery", "Endocrine Surgery", "Thoracic Surgery", "Urology",
                 link("Obesity Surgery", C + "bariatric-surgery/"), link("Plastic, Reconstructive and Aesthetic Surgery", C + "plastic-surgery/")]),
    ("Internal medicine", ["Internal Medicine", "Endocrinology and Metabolic Diseases", "Thyroid and Parathyroid Clinic", "Pituitary Clinic",
                           "Gastroenterology", "Nephrology", "Chest Diseases (Pulmonology)", "Infectious Diseases and Microbiology", "Immunology", "Dermatology", "Nutrition and Dietetics"]),
    ("Children's health", ["Paediatrics", "Paediatric Surgery", "Paediatric Cardiology", "Paediatric Oncology", "Paediatric Haematology",
                           "Paediatric Bone Marrow Transplantation", "Paediatric Neurology", "Paediatric Nephrology", "Paediatric Endocrinology",
                           "Paediatric Gastroenterology, Hepatology and Nutrition", "Paediatric Allergy and Immunology", "Paediatric Infectious Diseases",
                           "Paediatric Rheumatology", "Child and Adolescent Psychiatry", "Newborn Intensive Care (NICU)"]),
    ("Diagnostics, emergency and intensive care", ["Radiology and Imaging", "Medical Genetics", "Pathology", "Medical Biochemistry", "Medical Microbiology",
                                                  "Histology and Embryology", "Transfusion Centre", "Emergency Medicine", "Intensive Care", "Anaesthesiology and Reanimation"]),
]

MAIN = "\n\n".join([
    intro("Beyond our clinical treatments, MedLuxLife coordinates access to specialist hospital care across a wide range of medical fields, from cardiology and oncology to transplantation and fertility treatment. We help you obtain a medical opinion, plan your treatment with partner hospitals and organise your travel and stay.", IMG["check-up-women"]),
    group([h("Most requested specialties"), grid([featured_card(*f) for f in FEATURED])], "medlux-section"),
    group([h("All departments"),
           p("Our partner hospitals cover the following departments. If you do not find your condition here, contact us and we will check the options for you."),
           grid([card(title, [ul(items)]) for title, items in GROUPS], "medlux-treatment-grid medlux-dept-grid")], "medlux-section"),
    process(),
    cta("hospital treatment"),
])

def prepare(items):
    return group([h("Before you travel"), p("To get a reliable medical opinion quickly, please prepare:"), ul(items)], "medlux-section")

DOCS = ["Recent medical reports and discharge summaries", "Imaging (MRI, CT, X-ray) on CD or as DICOM files, with the radiology reports",
        "Recent laboratory results", "A list of your current medications and any allergies"]

def specialty(lead, heading, cards, docs, topic):
    return "\n\n".join([p(lead, "medlux-lead"), group([h(heading), grid([card(t, [p(d)]) for t, d in cards])], "medlux-section"),
                        prepare(docs), process(), cta(topic)])

PAGES = {259: MAIN}

PAGES[268] = specialty(
    "A cancer diagnosis raises many questions. MedLuxLife helps you obtain a specialist opinion and access modern cancer treatment at partner hospitals, where cases are discussed by multidisciplinary teams of oncologists, surgeons, radiation oncologists and other specialists.",
    "Treatments and services", [
    ("Second opinion", "An independent review of your diagnosis and treatment plan by experienced oncologists, based on your existing reports and images."),
    ("Diagnosis and staging", "Imaging such as PET-CT and MRI, biopsy and pathology to determine the exact type and stage of the disease."),
    ("Chemotherapy", "Drug treatments to destroy cancer cells or slow their growth, planned according to international treatment guidelines."),
    ("Targeted therapy and immunotherapy", "Modern treatments that act on specific features of cancer cells or help the immune system recognise them, where suitable."),
    ("Radiotherapy", "Precise radiation treatment coordinated with radiation oncology teams."),
    ("Surgical oncology", "Surgical removal of tumours, often in combination with other treatments."),
    ], DOCS + ["Pathology report and, if available, tissue blocks or slides"], "oncology consultation")

PAGES[269] = specialty(
    "Cardiology covers the diagnosis and treatment of heart and blood vessel conditions. Through our partner hospitals you can access comprehensive cardiac check-ups, advanced diagnostics and, where needed, interventional or surgical treatment.",
    "Treatments and services", [
    ("Cardiac check-up", "ECG, echocardiography, stress testing and blood tests to assess your heart health."),
    ("Advanced diagnostics", "Holter monitoring, cardiac CT and MRI, and coronary angiography where indicated."),
    ("Coronary interventions", "Balloon angioplasty and stent placement to treat narrowed coronary arteries."),
    ("Heart rhythm treatment", "Diagnosis of arrhythmias, pacemaker implantation and electrophysiology procedures."),
    ("Heart valve treatment", "Assessment and treatment of valve diseases, including catheter-based options where suitable."),
    ("Cardiovascular surgery", "Bypass surgery, valve surgery and vascular operations in cooperation with cardiovascular surgeons."),
    ], DOCS + ["Previous ECGs, echocardiography or angiography reports"], "cardiology consultation")

PAGES[270] = specialty(
    "Orthopaedics and traumatology treat conditions of the bones, joints, muscles and spine. Our partner hospitals offer modern surgical and non-surgical treatment, followed by physiotherapy and rehabilitation for a safe return to everyday life.",
    "Treatments and services", [
    ("Knee and hip replacement", "Partial or total joint replacement for advanced arthritis or joint damage."),
    ("Arthroscopic surgery", "Minimally invasive keyhole surgery of the knee, shoulder and other joints, for example for meniscus or ligament injuries."),
    ("Spine treatment", "Treatment of disc herniation, spinal stenosis and other spine conditions, conservative or surgical."),
    ("Sports injuries", "Diagnosis and treatment of ligament, tendon and cartilage injuries."),
    ("Trauma and fracture care", "Treatment of fractures and their consequences, including corrective surgery."),
    ("Physiotherapy and rehabilitation", "Personal rehabilitation programmes before and after surgery."),
    ], DOCS, "orthopaedic consultation")

PAGES[271] = specialty(
    "The wish to have a child is very personal. MedLuxLife connects you with experienced fertility specialists and supports you discreetly throughout every step, from the first assessment to treatment and follow-up.",
    "Treatments and services", [
    ("Fertility assessment", "Hormone tests, ultrasound and semen analysis to understand the causes and choose the right treatment."),
    ("In-vitro fertilisation (IVF)", "Eggs are fertilised in the laboratory and the embryo is transferred to the uterus."),
    ("ICSI", "A single sperm is injected directly into the egg, often used for male-factor infertility."),
    ("Intrauterine insemination (IUI)", "Prepared sperm are placed directly into the uterus around ovulation."),
    ("Egg and embryo freezing", "Preserving eggs or embryos for later use."),
    ("Genetic testing of embryos", "Where medically indicated, embryos can be tested for certain genetic conditions."),
    ], DOCS + ["Previous fertility treatments and their results", "Hormone and semen analysis results, if available"], "fertility consultation")

PAGES[272] = specialty(
    "Neurosurgery treats conditions of the brain, spinal cord and peripheral nerves. Partner hospitals use modern imaging, neuronavigation and minimally invasive techniques to plan and carry out each operation as safely as possible.",
    "Treatments and services", [
    ("Brain tumours", "Diagnosis and surgical treatment of benign and malignant brain tumours, in cooperation with oncology teams."),
    ("Spine surgery", "Treatment of disc herniation, spinal stenosis, instability and deformities, often with minimally invasive methods."),
    ("Vascular conditions of the brain", "Treatment of aneurysms and vascular malformations."),
    ("Functional neurosurgery", "Procedures such as deep brain stimulation for selected movement disorders."),
    ("Peripheral nerve surgery", "Treatment of nerve compression, for example carpal tunnel syndrome, and nerve injuries."),
    ("Hydrocephalus", "Shunt and endoscopic procedures to regulate cerebrospinal fluid."),
    ], DOCS + ["Brain or spine MRI/CT images"], "neurosurgery consultation")

PAGES[273] = specialty(
    "Ophthalmology covers the diagnosis and treatment of eye diseases and vision problems. At our partner clinics and hospitals you can access modern diagnostics and surgical treatment, often with a short stay.",
    "Treatments and services", [
    ("Cataract surgery", "The clouded lens is replaced with an artificial intraocular lens; premium lens options are available."),
    ("Refractive (laser) surgery", "Laser eye surgery such as LASIK, PRK or SMILE to reduce dependence on glasses or contact lenses."),
    ("Lens implants (ICL)", "An option for higher prescriptions or when laser surgery is not suitable."),
    ("Retina treatments", "Diagnosis and treatment of retinal diseases such as diabetic retinopathy, macular degeneration or retinal detachment."),
    ("Glaucoma", "Medication, laser and surgical treatment to protect the optic nerve."),
    ("Cornea and keratoconus", "Corneal cross-linking and corneal transplantation where needed."),
    ], DOCS + ["Your current glasses or contact lens prescription"], "eye consultation")

PAGES[274] = specialty(
    "Organ transplantation can offer a new perspective to patients with end-stage organ failure. Our partner transplant centres carry out kidney and liver transplants, including living-donor transplants, and follow strict medical, ethical and legal procedures.",
    "Treatments and services", [
    ("Kidney transplantation", "For patients with end-stage kidney disease, from a living related donor where possible."),
    ("Liver transplantation", "For patients with end-stage liver disease or selected liver tumours, including living-donor liver transplantation."),
    ("Donor and recipient evaluation", "Comprehensive medical and psychological assessment of both recipient and donor before transplantation."),
    ("Legal and ethical approval", "Living donation is only possible within the legal framework, including proof of the relationship between donor and recipient."),
    ("Post-transplant care", "Monitoring, immunosuppressive treatment and long-term follow-up after the transplant."),
    ("Dialysis coordination", "Coordination of dialysis during your stay, where needed."),
    ], DOCS + ["Documents for both recipient and potential donor", "Blood group and tissue typing results, if available"], "transplant consultation")
