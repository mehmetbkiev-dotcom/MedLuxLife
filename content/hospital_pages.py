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

IMGKEY = {268: 'hospital-oncology', 269: 'hospital-cardiology', 270: 'hospital-orthopedics', 271: 'hospital-ivf', 272: 'hospital-neurosurgery', 273: 'hospital-ophthalmology', 274: 'hospital-organ-transplantation'}

def featured_card(pid, title, slug, summary):
    return card_img(title, [p(summary), p(link("Learn more →", H + slug + "/"), "medlux-more")], IMG[IMGKEY[pid]])

GROUPS = [
    ("Cancer care", [link("Medical Oncology", H + "medical-oncology/"), "Gynaecological Oncology", "Haematology", "Adult Bone Marrow Transplantation", "Applications in Nuclear Medicine"]),
    ("Heart and vascular", [link("Cardiology", H + "cardiology/"), "Cardiovascular Surgery", "Interventional Radiology"]),
    ("Brain, nerves and mental health", [link("Neurosurgery", H + "neurosurgery/"), "Neurology", "Algology (Pain Medicine)", "Psychiatry", "Psychology"]),
    ("Bones, joints and rehabilitation", [link("Orthopedics and Traumatology", H + "orthopedics-and-traumatology/"), "Physical Therapy and Rehabilitation", "Rheumatology"]),
    ("Transplantation", [link("Organ Transplantation Center", H + "organ-transplantation-center/"), "Kidney Transplant Clinic", "Liver Transplant Clinic", "Parathyroid Transplant Clinic"]),
    ("Women's health and fertility", [link("In-Vitro Fertilization (IVF)", H + "in-vitro-fertilization-ivf/"), "Obstetrics and Gynaecology", "Perinatology", "Pelvic Pain and Endometriosis Clinic", "PCOS and Hirsutism Clinic", "Hirsutism Clinic", "Breast Surgery"]),
    ("Eye, ear, nose and throat", [link("Ophthalmology", H + "ophthalmology/"), "Otolaryngology (ENT)", "Audiology"]),
    ("Surgery", ["General Surgery", "Gastroenterological Surgery", "Endocrine Surgery", "Thoracic Surgery", "Urology",
                 link("Obesity Surgery", C + "bariatric-surgery/"), link("Plastic, Reconstructive and Aesthetic Surgery", C + "plastic-surgery/")]),
    ("Internal medicine", ["Internal Medicine", "Endocrinology and Metabolic Diseases", "Thyroid and Parathyroid Clinic", "Pituitary Clinic",
                           "Gastroenterology", "Nephrology", "Chest Diseases (Pulmonology)", "Infectious Diseases and Microbiology", "Immunology", "Dermatology", "Nutrition and Dietetics"]),
    ("Children's health", ["Paediatrics", "Paediatric Surgery", "Paediatric Cardiology", "Paediatric Oncology", "Paediatric Haematology",
                           "Paediatric Bone Marrow Transplantation", "Paediatric Neurology", "Paediatric Nephrology", "Paediatric Endocrinology",
                           "Paediatric Gastroenterology, Hepatology and Nutrition", "Paediatric Allergy and Immunology", "Paediatric Infectious Diseases",
                           "Paediatric Rheumatology", "Child and Adolescent Psychiatry", "Newborn Intensive Care (NICU)"]),
    ("Diagnostics, emergency and intensive care", ["Radiology", "Imaging Unit", "Medical Genetics", "Pathology", "Medical Microbiology",
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

def specialty(lead, heading, cards, docs, topic, extra=None, image=None):
    parts = [intro(lead, IMG[image]) if image else p(lead, "medlux-lead"), group([h(heading), grid([card(t, [p(d)]) for t, d in cards])], "medlux-section")]
    if extra:
        parts.append(extra)
    return "\n\n".join(parts + [prepare(docs), process(), cta(topic)])

PAGES = {259: MAIN}

CANCERS = ["Lung cancer", "Head and neck tumours", "Brain tumours", "Kidney cancer", "Endometrial (uterine) cancer", "Liver cancer", "Lymphomas",
           "Malignant melanoma", "Breast cancer", "Bladder cancer", "Gastrointestinal cancers", "Multiple myeloma", "Osteosarcoma and soft tissue sarcomas",
           "Ovarian cancer", "Pancreatic cancer", "Prostate cancer", "Gallbladder and biliary tract cancer", "Cervical cancer", "Testicular cancer", "Thyroid cancer"]

PAGES[268] = specialty(
    "Cancer treatment is planned according to the type, stage and biological features of the disease and your personal situation. Through our partner hospital, your case is assessed by a multidisciplinary team in which medical oncologists work closely with surgeons, radiation oncologists and other specialists.",
    "Treatments and services", [
    ("Personal treatment planning", "A treatment plan tailored to the type and stage of the disease, agreed in cooperation with surgery, radiation oncology and other departments."),
    ("Chemotherapy", "Drug treatments that stop the growth of cancer cells or destroy them, planned individually."),
    ("Targeted therapy", "Medicines that act on specific features of cancer cells, used where the tumour biology makes them suitable."),
    ("Immunotherapy", "Treatments that help the immune system to recognise and fight cancer cells."),
    ("Hormone therapy", "Used for hormone-sensitive cancers, such as some breast and prostate cancers."),
    ("Follow-up and supportive care", "Regular follow-up, management of side effects, preserving quality of life and psychosocial support during treatment."),
    ], DOCS + ["Pathology report and, if available, tissue blocks or slides"], "oncology consultation",
    extra=group([h("Cancer types treated"), p("Our partner oncology team treats the following cancers, as well as many other cancer types:"), ul(CANCERS)], "medlux-section medlux-columns"),
    image="hospital-oncology")

PAGES[269] = specialty(
    "Cardiology covers the evaluation, diagnosis, treatment and follow-up of heart conditions. Our partner hospital's cardiology department includes a cardiology outpatient clinic, a coronary intensive care unit, cardiac catheterisation and angiography laboratories, an electrophysiology unit and cardiology laboratories, and works closely with cardiovascular surgery.",
    "Treatments and services", [
    ("Echocardiography", "Transthoracic and transoesophageal echocardiography to assess the structure and function of the heart."),
    ("Stress and rhythm tests", "Treadmill stress test, rhythm Holter, event recorder and tilt-table test."),
    ("Blood pressure monitoring", "24-hour ambulatory blood pressure monitoring."),
    ("Coronary angiography and catheterisation", "Coronary angiography, haemodynamic studies and right and left heart catheterisation."),
    ("Coronary angioplasty and stents", "Percutaneous transluminal coronary angioplasty (PTCA) and intracoronary stent placement."),
    ("Pacemakers and ICDs", "Implantation of permanent pacemakers and implantable cardioverter-defibrillators (ICD)."),
    ("Electrophysiology and RF ablation", "Electrophysiological studies and radiofrequency ablation to treat heart rhythm disorders."),
    ("Balloon valvuloplasty", "Mitral and pulmonary balloon valvuloplasty to widen narrowed heart valves."),
    ("Catheter closure of heart defects", "Percutaneous closure of atrial septal defects (ASD) and patent ductus arteriosus (PDA)."),
    ("Other interventional procedures", "Septal ablation, pericardiocentesis and endomyocardial biopsy."),
    ], DOCS + ["Previous ECGs, echocardiography or angiography reports"], "cardiology consultation", image="hospital-cardiology")

PAGES[270] = specialty(
    "Orthopaedics and traumatology deal with the diagnosis, treatment and rehabilitation of problems of the bones, joints, muscles and spine in adults and children, including injuries from daily life and sport. Our partner hospital combines experienced orthopaedic surgeons with robotic and navigation technology and works with physical therapy and rehabilitation for a quick return to daily life.",
    "Treatments and services", [
    ("Arthroscopic surgery", "Closed (keyhole) surgery of the knee, shoulder, hip, ankle, elbow and wrist. Recovery is quick and in many cases no hospital stay is needed."),
    ("Robotic joint replacement", "Joint replacement for arthritis performed with robotic technology, special navigation systems and computer assistance."),
    ("Knee, hip and shoulder replacement", "Joint prostheses for advanced joint wear, for pain-free movement."),
    ("Sports injuries", "Treatment of ligament, meniscus, tendon and cartilage injuries from sport."),
    ("Foot and ankle", "Treatment of foot and ankle injuries and conditions."),
    ("Shoulder surgery", "Surgical treatment of shoulder injuries, instability and wear."),
    ("Cartilage transplantation", "For extensive cartilage damage where other treatments have failed, to preserve the joint and prevent or delay the need for a prosthesis."),
    ("Biological cartilage treatments", "Biological (orthobiological) treatment of cartilage diseases."),
    ("Spine surgery", "Treatment of spinal fractures, infections, tumours and congenital or acquired curvatures."),
    ("Fracture and trauma care", "Treatment of fractures and injuries and their consequences."),
    ("Paediatric orthopaedics", "Diagnosis and treatment of orthopaedic problems in children."),
    ("Orthopaedic oncology", "Diagnosis and treatment of bone and soft tissue tumours."),
    ], DOCS, "orthopaedic consultation", image="hospital-orthopedics")

PAGES[271] = specialty(
    "The wish to have a child is very personal. Our partner IVF centre plans every treatment individually, based on current scientific evidence, and its experienced team of physicians and embryologists decides together on each case. The causes of infertility are investigated carefully first, so that you are spared unnecessary treatment.",
    "Treatments and services", [
    ("Fertility assessment", "Medical history, ultrasound, hormone tests, semen analysis and, if needed, hysteroscopy for both partners."),
    ("IVF treatment", "Ovarian stimulation over about 8 to 14 days, egg collection under anaesthesia, fertilisation in the laboratory and a painless embryo transfer."),
    ("Natural (drug-free) IVF", "IVF in your natural cycle without stimulating medication, for example for women who respond poorly to medication or prefer not to use hormones."),
    ("Intrauterine insemination (IUI)", "Prepared sperm are placed directly into the uterus around ovulation."),
    ("Microinjection (ICSI)", "A single sperm is injected into each egg; used for male-factor infertility, including cases with no sperm in the semen (azoospermia)."),
    ("Microchip sperm selection", "Sperm with better motility and quality are selected using a microfluidic chip before fertilisation."),
    ("Egg freezing (cryopreservation)", "Eggs or embryos are frozen for later use, for example before chemotherapy or radiotherapy or to postpone pregnancy."),
    ("Co-culture", "Embryos are cultured together with supporting cells to support their development in the laboratory."),
    ("Assisted hatching", "The outer shell of the embryo is gently thinned or opened to help implantation, for example after repeated unsuccessful transfers."),
    ("Preimplantation genetic diagnosis (PGD)", "Embryos can be tested when a parent carries a hereditary disease, so that healthy embryos are selected."),
    ("Ovarian rejuvenation (PRP)", "A treatment option that may be considered for selected women with low ovarian reserve."),
    ("Difficult cases", "Special protocols for advanced age, low ovarian reserve, PCOS, endometriosis and repeated IVF failure."),
    ], DOCS + ["Previous fertility treatments and their results", "Hormone and semen analysis results, if available"], "fertility consultation", image="hospital-ivf")

PAGES[272] = specialty(
    "Neurosurgery covers the surgical diagnosis and treatment of diseases of the brain, spine, spinal cord and nerves. At our partner hospital's neurological sciences centre, neurosurgeons work in a multidisciplinary team with neurologists, anaesthesiologists, intensive care specialists, radiologists, psychiatrists, psychologists and rehabilitation specialists, in specialised wards and intensive care units.",
    "Treatments and services", [
    ("Neuro-oncology", "Microsurgical treatment of tumours of the brain, spinal cord and nerve sheaths, pituitary tumours and skull base tumours."),
    ("Neurovascular surgery", "Treatment of aneurysms, subarachnoid haemorrhage, arteriovenous malformations of the brain and spinal cord and selected strokes, including bypass surgery for blocked brain vessels."),
    ("Epilepsy surgery", "Surgical treatment of epilepsy by a specialised neurology and neurosurgery team, including epilepsy monitoring."),
    ("Spine and spinal cord surgery", "Surgery for lumbar and cervical disc herniation, age-related spinal stenosis and wear, spinal and spinal cord tumours and congenital disorders."),
    ("Kyphoplasty and vertebroplasty", "Spine-strengthening procedures for fractures caused by osteoporosis or tumour metastases."),
    ("Pain and spasticity treatment", "Intrathecal drug pumps for spasticity and pain, and injection treatments for spine-related pain that does not need surgery."),
    ("Peripheral nerve surgery", "Microsurgical treatment of carpal tunnel syndrome, ulnar and peroneal nerve compression, meralgia paraesthetica and nerve or plexus injuries."),
    ("Stereotactic and functional neurosurgery", "Precise, image-guided procedures on the brain."),
    ("Neurospinal trauma", "Treatment of injuries of the brain, spine and spinal cord."),
    ("Paediatric neurosurgery", "Surgical treatment of brain and spine conditions in children."),
    ], DOCS + ["Brain or spine MRI/CT images"], "neurosurgery consultation", image="hospital-neurosurgery")

PAGES[273] = specialty(
    "Ophthalmology covers the diagnosis, treatment and follow-up of diseases of the eye and its surrounding structures. Our partner hospital's eye department offers a wide range of specialised units, combining modern technology with experienced specialists.",
    "Treatments and services", [
    ("Laser vision correction", "Treatment of refractive errors with PRK, LASIK, LASEK, Epi-LASIK and IntraLase (femtosecond) LASIK, as well as contact lenses."),
    ("Cataract surgery", "Sutureless phacoemulsification under eye-drop anaesthesia with implantation of an intraocular lens."),
    ("Glaucoma", "Diagnosis and treatment of glaucoma to protect the optic nerve."),
    ("Retinal diseases", "Diagnosis and treatment of diseases of the retina."),
    ("Macular diseases and surgery", "Diagnosis, treatment and surgery of macular diseases."),
    ("Diabetic retinopathy", "Diagnosis and treatment of eye damage caused by diabetes."),
    ("Corneal diseases", "Diagnosis and treatment of diseases of the cornea."),
    ("Contact lens and keratoconus unit", "Specialised care for keratoconus and fitting of special contact lenses."),
    ("Strabismus and children's eyes", "Treatment of squint and eye problems in children."),
    ("Oculoplastic and orbital surgery", "Surgery of the eyelids, tear ducts and eye socket, aesthetic surgery around the eyes, and Botox for squint, eyelid spasms or aesthetic purposes."),
    ("Neuro-ophthalmology", "Conditions affecting both the eye and the nervous system."),
    ("Ocular oncology", "Follow-up and treatment of tumours of the eye and its surrounding structures."),
    ("Uveitis and Behçet unit", "Diagnosis and treatment of inflammatory eye diseases, including Behçet's disease."),
    ("Eye trauma unit", "Treatment of functional and cosmetic damage after injuries to the eye and its surroundings."),
    ("Eye infection unit", "Diagnosis and treatment of eye infections."),
    ("Low vision rehabilitation", "Optics, refraction and rehabilitation for patients whose vision cannot be improved further."),
    ], DOCS + ["Your current glasses or contact lens prescription"], "eye consultation", image="hospital-ophthalmology")

PAGES[274] = specialty(
    "Organ transplantation can offer a new perspective to patients with end-stage organ failure. Our partner transplant centre works with a multidisciplinary team of transplant surgeons, nephrologists, infectious disease specialists and other physicians, and plans every step from pre-transplant evaluation to long-term follow-up.",
    "Treatments and services", [
    ("Kidney transplantation", "For patients with end-stage kidney disease. A two-stage evaluation checks suitability for transplantation and treats any accompanying problems first."),
    ("Liver transplantation", "For acute liver failure, end-stage liver disease (cirrhosis) and some liver cancers."),
    ("Pancreas and heart transplantation", "The centre has also performed pancreas and heart transplants; suitability is assessed individually."),
    ("Living-donor transplantation", "For international patients, transplantation is generally performed from a living donor, within the legal requirements, including proof of the relationship between donor and recipient."),
    ("Donor and recipient evaluation", "Comprehensive medical assessment of recipient and donor, with decisions taken by a multidisciplinary council."),
    ("Minimally invasive techniques", "Laparoscopic and minimally invasive transplant techniques, supported by advanced imaging such as multislice CT, 3 Tesla MRI, PET-CT, gamma camera and biplane angiography."),
    ("Post-transplant care", "Monitoring, immunosuppressive treatment and long-term follow-up after the transplant."),
    ("Infection prevention", "A strong focus on hygiene and infection prevention, which is particularly important for transplant patients."),
    ], DOCS + ["Documents for both recipient and potential donor", "Blood group and tissue typing results, if available"], "transplant consultation", image="hospital-organ-transplantation")
