from blocks import *

U = "https://medluxlife.de/wp-content/uploads/2026/10/"
IMG = {
    "hero": (295, U + "medluxlife-dental-hero-1024x966.jpg", "Smiling patient during a dental check-up"),
    "hollywood": (296, U + "medluxlife-dental-hollywood-smile-1024x348.jpg", "Man with a bright, even smile at the dentist"),
    "implants": (298, U + "medluxlife-dental-implants-563x1024.jpg", "Dentist showing a dental implant model to a patient"),
    "allon4": (294, U + "medluxlife-dental-all-on-4-1024x920.jpg", "Illustration of dental implants supporting crowns"),
    "prosthetics": (299, U + "medluxlife-dental-prosthetics-1024x873.jpg", "Digitally produced dental prosthesis on a model"),
    "implant_prosth": (297, U + "medluxlife-dental-implant-supported-prostheses-1024x910.jpg", "Dentist explaining an implant to a patient in the treatment chair"),
    "whitening": (300, U + "medluxlife-dental-teeth-whitening-557x1024.jpg", "Professional teeth whitening with blue light"),
}

intro = [
    intro("A healthy, natural-looking smile supports both your well-being and your confidence. MedLuxLife connects you with experienced dental specialists who combine modern digital diagnostics with proven treatment methods, from a single implant to a complete smile makeover.", IMG["hero"]),
]

cards = [
    card_img("Hollywood Smile", [
        p("A complete smile makeover designed to create a bright, even and harmonious smile that suits your facial features. Depending on your needs, it can combine:"),
        ul(["<strong>Teeth whitening</strong> for an even, natural brightness",
            "<strong>Veneers</strong> in porcelain or zirconium to correct discolouration, chips or minor misalignment",
            "<strong>Dental bonding</strong> to repair small flaws or gaps",
            "<strong>Contouring and reshaping</strong> for symmetry and balance",
            "<strong>Gum contouring</strong> for an even gum line"]),
    ], IMG["hollywood"]),
    card_img("Dental Implants", [
        p("A permanent solution for missing or damaged teeth. A titanium or other biocompatible implant is placed in the jawbone, where it integrates over time and forms a stable base for a crown, bridge or denture."),
        ul(["Looks and feels like a natural tooth", "Restores full chewing function", "Long-lasting with proper care", "Helps preserve the jawbone"]),
    ], IMG["implants"]),
    card_img("All-on-4 and All-on-6", [
        p("Fixed full-arch solutions for patients who are missing most or all of their teeth. A complete set of upper or lower teeth is supported by four or six implants. In many cases temporary teeth can be fitted on the same day."),
        p("All-on-6 may be recommended where more stability is needed or bone loss is more advanced. Your dentist will advise which option suits you."),
    ], IMG["allon4"]),
    card("Zirconium Veneers", [
        p("Custom-made restorations in zirconia ceramic that improve the shape and colour of your teeth while looking natural."),
        ul(["Very strong and resistant to chipping and staining", "Suitable for patients who grind their teeth", "Metal-free and hypoallergenic"]),
    ]),
    card("Periodontology (Gum Treatment)", [
        p("Healthy teeth need healthy gums. Gum inflammation (gingivitis) and advanced gum disease (periodontitis) are treated with professional cleaning, scaling and root planing and, where necessary, surgical procedures to protect the gums and bone."),
    ]),
    card_img("Prosthetic Dental Treatments", [
        p("Aesthetic and functional solutions for missing teeth, including fixed crowns and bridges placed over natural teeth."),
    ], IMG["prosthetics"]),
    card_img("Implant-Supported Prostheses", [
        p("Fixed or removable prostheses attached to implants in the jawbone, offering better stability and comfort than conventional dentures."),
    ], IMG["implant_prosth"]),
    card("Restorative Dental Treatments", [
        p("Repair of damaged or decayed teeth, for example with fillings, to restore their function, structure and appearance."),
    ]),
    card("Root Canal Treatment", [
        p("Cleaning and sealing the inflamed or damaged nerve tissue inside a tooth, so the natural tooth can be saved instead of extracted."),
    ]),
    card_img("Teeth Whitening", [
        p("A cosmetic treatment that lightens the colour of the teeth and removes stains and discolouration."),
    ], IMG["whitening"]),
    card("Masseter Botox (Jaw Botox)", [
        p("Injections into the masseter muscle can ease teeth grinding (bruxism) and jaw tension and give the lower face a slimmer, more oval contour. A quick treatment whose effect typically lasts 4 to 6 months."),
    ]),
    card("TMJ Treatment", [
        p("Treatment of pain, clicking or locking of the jaw joint, which is often linked to teeth grinding. Night guards (splints) protect the joint and relax the muscles; surgical options are available where needed."),
    ]),
    card("Orthodontics", [
        p("Braces and clear aligners correct crooked, crowded or gapped teeth. Options for all ages include metal or tooth-coloured brackets and discreet clear aligner systems."),
    ]),
]

photo_cards = [c for c in cards if "medlux-card--photo" in c]
text_cards = [c for c in cards if "medlux-card--photo" not in c]
content = "\n\n".join(intro + [group([h("Dental treatments"), grid(photo_cards), grid(text_cards)], "medlux-section"), process(), cta("dental treatment")])
