from blocks import *

intro = [
    p("A healthy, natural-looking smile supports both your well-being and your confidence. MedLuxLife connects you with experienced dental specialists who combine modern digital diagnostics with proven treatment methods, from a single implant to a complete smile makeover.", "medlux-lead"),
    p("Treatment planning starts with high-resolution digital imaging, so every step can be planned precisely. Where a procedure requires it, treatment can also take place under general anaesthesia in a hospital setting with the support of maxillofacial surgeons."),
]

cards = [
    card("Hollywood Smile", [
        p("A complete smile makeover designed to create a bright, even and harmonious smile that suits your facial features. Depending on your needs, it can combine:"),
        ul(["<strong>Teeth whitening</strong> for an even, natural brightness",
            "<strong>Veneers</strong> in porcelain or zirconium to correct discolouration, chips or minor misalignment",
            "<strong>Dental bonding</strong> to repair small flaws or gaps",
            "<strong>Contouring and reshaping</strong> for symmetry and balance",
            "<strong>Gum contouring</strong> for an even gum line"]),
    ]),
    card("Dental Implants", [
        p("A permanent solution for missing or damaged teeth. A titanium or other biocompatible implant is placed in the jawbone, where it integrates over time and forms a stable base for a crown, bridge or denture."),
        ul(["Looks and feels like a natural tooth", "Restores full chewing function", "Long-lasting with proper care", "Helps preserve the jawbone"]),
    ]),
    card("All-on-4 and All-on-6", [
        p("Fixed full-arch solutions for patients who are missing most or all of their teeth. A complete set of upper or lower teeth is supported by four or six implants. In many cases temporary teeth can be fitted on the same day."),
        p("All-on-6 may be recommended where more stability is needed or bone loss is more advanced. Your dentist will advise which option suits you."),
    ]),
    card("Zirconium Veneers", [
        p("Custom-made restorations in zirconia ceramic that improve the shape and colour of your teeth while looking natural."),
        ul(["Very strong and resistant to chipping and staining", "Suitable for patients who grind their teeth", "Metal-free and hypoallergenic"]),
    ]),
    card("Periodontology (Gum Treatment)", [
        p("Healthy teeth need healthy gums. Gum inflammation (gingivitis) and advanced gum disease (periodontitis) are treated with professional cleaning, scaling and root planing and, where necessary, surgical procedures to protect the gums and bone."),
    ]),
    card("Prosthetic Dental Treatments", [
        p("Aesthetic and functional solutions for missing teeth, including fixed crowns and bridges placed over natural teeth."),
    ]),
    card("Implant-Supported Prostheses", [
        p("Fixed or removable prostheses attached to implants in the jawbone, offering better stability and comfort than conventional dentures."),
    ]),
    card("Restorative Dental Treatments", [
        p("Repair of damaged or decayed teeth, for example with fillings, to restore their function, structure and appearance."),
    ]),
    card("Root Canal Treatment", [
        p("Cleaning and sealing the inflamed or damaged nerve tissue inside a tooth, so the natural tooth can be saved instead of extracted."),
    ]),
    card("Teeth Whitening", [
        p("A cosmetic treatment that lightens the colour of the teeth and removes stains and discolouration."),
    ]),
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

content = "\n\n".join(intro + [group([h("Dental treatments"), grid(cards)], "medlux-section"), process(), cta("dental treatment")])
