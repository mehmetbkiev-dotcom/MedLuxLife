"""Content for the Clinical Treatments sub-pages (rewritten from the partner catalogue, clinic branding removed)."""
import json
from blocks import *

IMG = {k: tuple(v) for k, v in json.load(open(__file__.rsplit('/', 1)[0] + '/images.json')).items()}

def page(lead, intro_img, heading, cards, topic, extra=None, before=None):
    built = [card_img(t, body, IMG[i]) if i else card(t, body) for t, body, i in cards]
    photo = [c for c in built if "medlux-card--photo" in c]
    text = [c for c in built if "medlux-card--photo" not in c]
    section = [h(heading)] + ([grid(photo)] if photo else []) + ([grid(text)] if text else [])
    parts = [intro(lead, IMG[intro_img])] + ([before] if before else []) + [group(section, "medlux-section")]
    if extra:
        parts.append(extra)
    return "\n\n".join(parts + [process(), cta(topic)])

PAGES = {}

PAGES[261] = page(  # Hair Transplantation
    "Hair transplantation moves healthy hair follicles from areas where hair is resistant to thinning, usually the back and sides of the head, to areas with thinning or hair loss. It is one of the most requested aesthetic procedures for men and women with pattern hair loss, and the results grow naturally with your own hair.",
    "hair-transplant-surgery", "Hair transplantation treatments", [
    ("Hair and Scalp Analysis", [
        p("Before any treatment, an AI-supported digital analysis evaluates hair density and thickness, the health of individual follicles and whether they are in a growth or resting phase. This helps to choose the most suitable technique and to track your progress objectively over time."),
    ], "hair-analysis"),
    ("FUE (Follicular Unit Extraction)", [
        p("Individual follicles are taken one by one from the donor area with a fine, circular micro-punch and implanted into the thinning areas. No linear scar, and a comfortable recovery."),
    ], "hair-fue"),
    ("Beard and Moustache Transplant", [
        p("For a fuller, more defined beard or moustache. Follicles, usually from the back of the head, are transplanted into sparse areas. An effective option for uneven growth, scarring or hair loss caused by genetics, hormones or injury."),
    ], "hair-beard-transplant"),
    ("Eyebrow Transplant", [
        p("Reshapes and strengthens thin, sparse or over-plucked eyebrows with your own hair follicles. A permanent, natural-looking alternative to make-up or microblading."),
    ], "hair-eyebrow-transplant"),
    ("Sapphire FUE", [
        p("An advanced form of FUE in which the channels are opened with blades made of sapphire crystal instead of steel. The finer, sharper blades allow very precise incisions, with less tissue trauma and swelling."),
    ], None),
    ("DHI (Direct Hair Implantation)", [
        p("Follicles are implanted directly with a special implanter pen (Choi pen), without opening channels in advance. This allows precise control of angle, direction and depth."),
    ], None),
    ("FUT (Follicular Unit Transplantation)", [
        p("A strip of skin is taken from the donor area and divided into individual follicular units. FUT allows many grafts in one session but leaves a longer linear scar, so it is used today only in selected cases."),
    ], None),
    ], "hair transplant")

PAGES[262] = page(  # Restorative Hair Therapies
    "Not every case of thinning hair needs surgery. Restorative hair therapies nourish and stimulate the hair follicles, help to slow hair loss and improve hair density and quality. They can be used on their own or to support the results of a hair transplant.",
    "hair-mesotherapy", "Restorative hair therapies", [
    ("Exosome Therapy", [
        p("Exosomes are tiny vesicles released by cells that carry proteins, lipids and growth signals. For hair restoration they are usually derived from mesenchymal stem cells and injected into thinning areas of the scalp, where they stimulate the follicles, extend the growth phase and support a healthier scalp. Exosomes are often combined with PRP."),
    ], None),
    ("Red Light Therapy", [
        p("A non-invasive, low-level light treatment at wavelengths of around 600 to 650 nanometres. The light is absorbed by the follicle cells, stimulates their energy production, improves local circulation and supports healthy hair growth."),
    ], None),
    ("Hair Mesotherapy", [
        p("A tailored blend of vitamins, amino acids, plant extracts and other active ingredients is injected into the scalp to nourish the hair follicles. Usually performed as a series of sessions; many patients notice thicker, stronger hair over time."),
        p("A motorised mesotherapy device delivers even micro-injections at a controlled depth, which makes the treatment quicker and more comfortable than manual injections."),
    ], None),
    ("PRP (Platelet-Rich Plasma)", [
        p("A small amount of your own blood is processed in a centrifuge to obtain plasma rich in platelets. Injected into the scalp, it stimulates the hair follicles and supports cell renewal. PRP is a well-established option to reduce hair loss and improve hair density."),
    ], None),
    ], "hair therapy")

PAGES[263] = page(  # Plastic Surgery
    "Plastic and aesthetic surgery can restore harmony and proportion to the face and body. MedLuxLife connects you with experienced plastic surgeons and plans every step of your stay, from the first consultation to your recovery, so you can make your decision calmly and with full information.",
    "plastic-surgery", "Plastic surgery procedures", [
    ("Mommy Makeover", [
        p("A combination of procedures that addresses changes after pregnancy and childbirth, tailored to your needs. It may include:"),
        ul(["<strong>Tummy tuck</strong> to remove excess skin and tighten the abdominal muscles",
            "<strong>Breast lift or augmentation</strong> to restore shape and volume",
            "<strong>Liposuction</strong> for stubborn fat on the abdomen, hips or thighs",
            "<strong>Intimate rejuvenation</strong>, such as labiaplasty"]),
    ], "plastic-mommy-makeover"),
    ("Rhinoplasty", [
        p("Reshapes the nose to improve facial balance and, where needed, breathing."),
        ul(["<strong>Cosmetic rhinoplasty:</strong> changes size, tip shape or nostrils, or corrects asymmetry",
            "<strong>Functional rhinoplasty (septorhinoplasty):</strong> improves breathing, for example with a deviated septum"]),
    ], "plastic-rhinoplasty"),
    ("Abdominoplasty (Tummy Tuck)", [
        p("Removes excess skin and fat from the abdomen and tightens the underlying muscles for a flatter, firmer contour."),
        ul(["<strong>Full abdominoplasty:</strong> an incision from hip to hip, often with repositioning of the navel",
            "<strong>Mini abdominoplasty:</strong> a shorter incision for minor excess below the navel"]),
    ], "plastic-abdominoplasty"),
    ("Breast Augmentation", [
        p("Increases breast size and volume or restores volume lost after weight changes or pregnancy, using silicone implants or your own fat. Implant position (under or over the muscle, or dual plane) is chosen according to your anatomy and goals."),
    ], "plastic-breast-augmentation"),
    ("Breast Reduction", [
        p("Reduces the size and weight of very large breasts. It can relieve back and neck pain, restricted movement and skin irritation, and creates a more balanced silhouette."),
    ], "plastic-breast-reduction"),
    ("Gynecomastia Surgery", [
        p("Male breast reduction removes excess glandular tissue and fat, using liposuction, direct excision or both, for a flatter, more masculine chest."),
    ], "plastic-gynecomastia"),
    ("Brachioplasty (Arm Lift)", [
        p("Removes loose skin and fat from the upper arms, often after major weight loss or with age, through an incision on the inner or back of the arm."),
    ], "plastic-arm-lift"),
    ("Brazilian Butt Lift (BBL)", [
        p("Fat is removed by liposuction from areas such as the abdomen or flanks, purified and transferred to the buttocks for more volume and a natural, lifted shape."),
    ], "plastic-bbl"),
    ("Thigh Lift", [
        p("Removes excess skin and fat from the thighs and tightens the tissue for a smoother contour, typically after significant weight loss."),
    ], "plastic-thigh-lift"),
    ("Blepharoplasty (Eyelid Surgery)", [
        p("Corrects drooping upper eyelids and under-eye bags for a fresher, more youthful look. Upper eyelid surgery is usually done under local anaesthesia; lower eyelid surgery generally under general anaesthesia."),
    ], "plastic-blepharoplasty"),
    ("Facelift", [
        p("Reduces visible signs of ageing such as sagging skin and deep folds. Depending on your needs, the surgeon chooses a full, mini, mid-face or temporal lift."),
    ], "plastic-facelift"),
    ("Buccal Fat Removal", [
        p("Reduces the fat pads in the lower cheeks through small incisions inside the mouth, for more sculpted cheeks and a defined jawline. Usually performed under local anaesthesia."),
    ], "plastic-buccal-fat-removal"),
    ("Liposuction", [
        p("Removes stubborn fat deposits that do not respond to diet and exercise, for example on the abdomen, thighs, arms, back or waist, to sculpt the body contour."),
    ], None),
    ("Breast Lift (Mastopexy)", [
        p("Lifts and reshapes sagging breasts for a firmer, more youthful position. It can be combined with augmentation to add volume at the same time."),
    ], None),
    ("Otoplasty (Ear Correction)", [
        p("Reshapes or repositions prominent or asymmetric ears. Possible for adults and for children from about five years of age."),
    ], None),
    ("Neck Lift", [
        p("Tightens loose skin and reshapes the neck and jawline. Often combined with a facelift for a harmonious result."),
    ], None),
    ], "procedure")

PAGES[264] = page(  # Medical Aesthetics
    "Medical aesthetics offers non-surgical treatments to smooth lines, restore volume and refresh the skin, with little or no downtime. Treatments are carried out by qualified doctors and planned to keep your natural expression.",
    "aesthetics", "Medical aesthetic treatments", [
    ("Botox (Botulinum Toxin)", [
        p("Relaxes the muscles that cause expression lines, such as forehead lines, frown lines and crow's feet, and can also be used for a subtle brow lift."),
        p("Medical uses include reducing excessive sweating (hyperhidrosis) and easing jaw tension related to teeth grinding."),
    ], "aesthetics-botox"),
    ("Dermal Fillers", [
        p("Injectable fillers restore volume and smooth folds. Common areas:"),
        ul(["Nasolabial folds (smile lines)", "Cheeks and temples", "Lips: volume, definition and hydration", "Chin and jawline contouring"]),
    ], "aesthetics-dermal-fillers"),
    ("Skin Mesotherapy", [
        p("Micro-injections deliver vitamins, minerals, amino acids and other nourishing substances directly into the skin, for skin rejuvenation, cellulite or localised fat. Several sessions give the best results; downtime is minimal."),
    ], None),
    ("Exosome Skin Treatments", [
        p("Exosomes deliver growth factors and proteins to skin cells to support regeneration and collagen production. Applied after microneedling, laser or radiofrequency treatments, they help the skin recover and look brighter, firmer and smoother."),
    ], None),
    ], "aesthetic treatment")

bariatric_intro = group([
    h("A supportive, respectful approach"),
    p("Deciding on weight-loss surgery is a big step, and you do not have to take it alone. We take your health, your dignity and your well-being seriously and work with experienced teams who offer evidence-based treatment in a supportive, judgement-free setting."),
], "medlux-section")

PAGES[265] = page(  # Bariatric Surgery
    "Bariatric (obesity) surgery can lead to substantial, lasting weight loss and improve weight-related health problems and quality of life. The right procedure depends on your health, your weight and your goals, and is chosen together with your surgeon.",
    "bariatric-surgery", "Weight-loss treatments", [
    ("Gastric Sleeve", [
        p("Sleeve gastrectomy reduces the size of the stomach, which limits food intake and leads to significant, sustainable weight loss. One of the most widely performed weight-loss operations today."),
    ], "bariatric-gastric-sleeve"),
    ("Gastric Bypass", [
        p("The most common form, the Roux-en-Y gastric bypass, reduces food intake and limits calorie absorption by changing the route of the digestive tract. A proven option for long-term weight loss."),
    ], "bariatric-gastric-bypass"),
    ("Gastric Balloon", [
        p("A non-surgical option: a soft, saline-filled balloon in the stomach creates a feeling of fullness and helps to reduce food intake. Depending on the system, it stays for several months. On average it leads to a weight loss of about 10% of body weight and is often a first step on the weight-loss journey."),
    ], "bariatric-gastric-balloon"),
    ], "weight-loss treatment", before=bariatric_intro)

PAGES[266] = page(  # Check-Up Packages
    "Regular check-ups help healthy people stay healthy. Many conditions can be detected before they cause any symptoms, when treatment is often simpler and more effective. Our check-up packages are tailored to your age and the health needs of your stage of life and are carried out at partner hospitals.",
    "check-up", "Check-up packages", [
    ("Check-ups for Men", [
        p("Packages tailored to each stage of life:"),
        ul(["Under 40", "Over 40", "Over 50", "Over 65"]),
    ], "check-up-men"),
    ("Check-ups for Women", [
        p("Packages tailored to each stage of life:"),
        ul(["Under 40", "Over 40", "Over 50", "Over 65"]),
    ], "check-up-women"),
    ], "check-up", extra=group([
        p("The exact content of each package (laboratory tests, imaging and specialist consultations) is shared with you during your consultation, so you can choose the package that suits you best."),
    ], "medlux-section"))

PAGES[267] = page(  # IV Treatments
    "IV treatments deliver vitamins, minerals and other nutrients directly into the bloodstream, so they are fully available to the body. They are designed to support energy, regeneration and overall well-being, and every infusion is selected after a short medical assessment.",
    "iv-treatments", "Our IV treatments", [
    ("Myers' Cocktail", [
        p("A classic infusion with vitamin C, B vitamins, magnesium and calcium to support energy, immunity and general well-being."),
    ], "iv-myers-cocktail"),
    ("NAD+", [
        p("Nicotinamide adenine dinucleotide is a coenzyme involved in cellular energy production. The infusion is used to support energy, mental clarity and healthy ageing."),
    ], "iv-nad"),
    ("Hair and Nail Cocktail", [
        p("Supports stronger hair and nails and healthy hair growth, and nourishes the follicles, for example after a hair transplant."),
    ], "iv-hair-nail"),
    ("Beauty Cocktail", [
        p("Supports skin firmness, smoothness and moisture, promotes collagen production and complements facial mesotherapy."),
    ], "iv-beauty-cocktail"),
    ("Fat Burning Slim Boost", [
        p("With L-carnitine and other nutrients to support metabolism and fat burning as part of a weight-management programme."),
    ], "iv-fat-burning"),
    ("Vitamin C Megadose", [
        p("High-dose vitamin C with antioxidant properties that supports the immune system, tissue regeneration and collagen production."),
    ], "iv-vitamin-c"),
    ("Alpha Lipoic Acid", [
        p("A strong antioxidant that helps to regenerate other antioxidants such as vitamins C and E and supports nerve health and metabolism."),
    ], "iv-alpha-lipoic-acid"),
    ("Immune Plus", [
        p("Supports immune function, energy metabolism and antioxidant capacity."),
    ], "iv-immune-plus"),
    ("Anti-ageing Collagen Booster", [
        p("Amino acids, vitamins and minerals that support collagen production, skin health and overall vitality."),
    ], "iv-collagen-booster"),
    ("Glutathione", [
        p("A powerful antioxidant that supports the body's natural detoxification and the immune system and helps protect cells from oxidative stress."),
    ], None),
    ], "IV treatment")
