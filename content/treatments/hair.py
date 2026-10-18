# Treatment detail pages – Hair Transplantation (parent page 261). Written in our own words from the partner clinic's pages
# (FUE, DHI, beard, moustache, eyebrow; general hair transplant FAQ); no names, no promises, no before/after, no prices (HWG).
PARENT = 261
STAY = ('pin', 'Stay in Türkiye', 'Planned individually with the clinic')
VOCAB = {'doctor': 'surgeon', 'proc_title': 'How the procedure works', 'step3_title': 'Arrival and procedure',
         'step3_lead': 'After an examination, the procedure takes place as planned. '}

TREATMENTS = [
 {'card': 'FUE (Follicular Unit Extraction)', 'title': 'FUE Hair Transplant', 'slug': 'fue-hair-transplant', 'short': 'FUE hair transplant',
  'intro': 'In an FUE hair transplant, individual hair follicles are taken one by one from the donor area – usually the back or sides '
           'of the head – with a fine micro-punch and implanted into thinning or bald areas. No linear incision and no stitches are '
           'needed. MedLuxLife arranges your online consultation with the surgeon in Istanbul and organises your stay.',
  'facts': [('moon', 'Anaesthesia', 'Local anaesthesia'), ('clock', 'Duration', 'About 6–8 hours'),
            ('calendar', 'Back to work', 'After about 2–3 days'), ('hourglass', 'Final result', 'After 12–18 months'), STAY],
  'suitable': ['You have male pattern baldness, thinning hair or a receding hairline.', 'You have enough healthy donor hair at the back or sides of the head.',
               'Your hair loss has stabilised.', 'You are in good general health.'],
  'options': [],
  'hospital': 'You return to your hotel on the same day.',
  'recovery': [('First days', 'Light activities after 1–2 days; most people return to work after about 2–3 days. Strenuous exercise should wait at least one month.'),
               ('Weeks 2–4', 'The transplanted hairs fall out temporarily ("shock loss") – a normal part of healing; the roots stay in place.'),
               ('Months 3–18', 'New hair grows from about month 3, density increases noticeably by month 6, and the final result shows after 12–18 months.')],
  'faq': [('Is an FUE hair transplant painful?', 'The donor and recipient areas are numbed with local anaesthesia before the procedure. Mild discomfort afterwards is treated with common painkillers.'),
          ('Will there be a scar?', 'FUE needs no linear incision and no stitches. The tiny, dot-like marks in the donor area are usually hard to see once healed.'),
          ('Why does the hair fall out after the transplant?', 'In the first weeks the transplanted hairs fall out temporarily ("shock loss"). The roots stay in the skin and grow new hair from about month 3.'),
          ('When can I do sport again?', 'Light activities are possible after a few days; strenuous exercise and heavy lifting should wait at least one month.')]},

 {'card': 'DHI (Direct Hair Implantation)', 'title': 'DHI Hair Transplant', 'slug': 'dhi-hair-transplant', 'short': 'DHI hair transplant',
  'intro': 'DHI (Direct Hair Implantation) is a further development of FUE: the follicles are taken individually and implanted directly '
           'with a special implanter pen (Choi pen), without opening channels in advance. This gives precise control over the depth, '
           'angle and direction of each hair – and DHI is also possible without shaving the head. MedLuxLife arranges your online '
           'consultation with the surgeon in Istanbul and organises your stay.',
  'facts': [('moon', 'Anaesthesia', 'Local anaesthesia'), ('calendar', 'Back to work', 'After about 2 days'),
            ('clock', 'Healing', 'About 7–10 days'), ('hourglass', 'Final result', 'After about 12 months'), STAY],
  'suitable': ['You have thinning hair, a receding hairline or bald patches.', 'You have enough healthy donor hair.',
               'You would like to keep your hair long – DHI is also possible without shaving.', 'You are in good general health.'],
  'options_title': 'Options',
  'options': [('lift', 'Classic DHI', 'Follicles are implanted directly with the Choi pen for a dense, natural hairline.'),
              ('care', 'Unshaven DHI', 'The recipient area does not have to be shaved – practical for women and for long hair.')],
  'hospital': 'You return to your hotel on the same day.',
  'recovery': [('Days 1–2', 'Most people return to light routines and to work after about 2 days.'),
               ('Days 7–10', 'Small scabs and redness go away.'),
               ('Months 3–12', 'The implanted hairs shed in the first weeks; new hair grows from about month 3–4, and the full result shows after about 12 months.')],
  'faq': [('How is DHI different from FUE?', 'With DHI the follicles are implanted directly with the Choi pen, without opening channels first – opening and implanting happen in one step.'),
          ('Can DHI be done without shaving?', 'Yes. The recipient area does not have to be shaved, which is practical for women and anyone who wants to keep their hair long.'),
          ('Is DHI painful?', 'It is performed under local anaesthesia; you are awake and comfortable during the procedure.'),
          ('How long is the recovery?', 'Scabs and redness go away within about 7–10 days; most people return to work after about 2 days.')]},

 {'card': 'Beard and Moustache Transplant', 'title': 'Beard and Moustache Transplant', 'slug': 'beard-and-moustache-transplant', 'short': 'beard or moustache transplant',
  'intro': 'A beard or moustache transplant gives a fuller, more defined beard or moustache. Follicles, usually from the back of the head, '
           'are transplanted into sparse or hairless areas of the face with the FUE or DHI technique, following the natural direction '
           'of growth. MedLuxLife arranges your online consultation with the surgeon in Istanbul and organises your stay.',
  'facts': [('moon', 'Anaesthesia', 'Local anaesthesia'), ('calendar', 'Daily activities', 'After a few days'),
            ('clock', 'First trim', 'With scissors after 1 month'), ('hourglass', 'Final result', 'After 9–12 months'), STAY],
  'suitable': ['Your beard or moustache grows patchy, thin or unevenly.', 'You have lost facial hair due to genetics, scars or an injury.',
               'You have enough healthy donor hair.', 'You are in good general health.'],
  'options_title': 'Options',
  'options': [('face', 'Beard transplant', 'For cheeks, jawline and chin – density and design are planned with you.'),
              ('lift', 'Moustache transplant', 'For the upper lip, symmetrical and in the natural direction of growth.')],
  'hospital': 'You return to your hotel on the same day.',
  'recovery': [('First week', 'Redness and slight swelling go down; most people are back to their routines within a week.'),
               ('Weeks 2–4', 'The transplanted hairs fall out temporarily ("shock loss"); the roots stay in place.'),
               ('Months 3–12', 'New growth starts around month 3, visible density at about 6 months, and the final result after 9–12 months.')],
  'faq': [('Is it painful?', 'The donor area and the face are numbed with local anaesthesia. Minor tightness afterwards is treated with common painkillers.'),
          ('When can I shave?', 'A first light trim with scissors after 1 month; razors or clippers should wait 3–6 months.'),
          ('Why do the hairs fall out after the transplant?', 'Between weeks 2 and 4 the transplanted hair shafts fall out temporarily. The roots stay in the skin and grow new hair.')]},

 {'card': 'Eyebrow Transplant', 'title': 'Eyebrow Transplant', 'slug': 'eyebrow-transplant', 'short': 'eyebrow transplant',
  'intro': 'An eyebrow transplant strengthens thin, sparse or missing eyebrows with your own hair. Single fine follicles from the back '
           'of the head are implanted with the DHI technique, following the natural growth pattern of the eyebrows. MedLuxLife '
           'arranges your online consultation with the surgeon in Istanbul and organises your stay.',
  'facts': [('moon', 'Anaesthesia', 'Local anaesthesia'), ('calendar', 'Daily activities', 'After a few days'),
            ('clock', 'Healing', 'About 7–10 days'), ('hourglass', 'Final result', 'After 8–12 months'), STAY],
  'suitable': ['Your eyebrows are thin, sparse or missing – for example due to genetics, over-plucking or an injury.',
               'You would like a fuller, more defined eyebrow shape.', 'You are in good general health.'],
  'options': [],
  'hospital': 'You return to your hotel on the same day.',
  'recovery': [('Days 7–10', 'Small scabs and redness go away; daily routines are possible within a few days.'),
               ('First month', 'The transplanted hairs fall out temporarily ("shock loss") – the roots stay in place.'),
               ('Months 3–12', 'New hairs grow from about month 3; the final result shows after 8–12 months.')],
  'faq': [('Is an eyebrow transplant painful?', 'It is performed under local anaesthesia, which numbs the donor and eyebrow areas.'),
          ('Do the transplanted eyebrows need trimming?', 'Yes. The hair comes from the scalp and keeps growing like scalp hair, so it needs regular trimming.'),
          ('When will I see the result?', 'New hairs grow from about month 3; the final result shows after 8–12 months.')]},
]

# "How the procedure works": the steps of each treatment as described on the partner clinic's page, in our words
STAGES = {
 'fue-hair-transplant': [('moon', 'Preparation and anaesthesia', 'The surgeon discusses your wishes, examines your hair and scalp and plans the hairline. Local anaesthesia is applied on the day of the procedure.'),
                         ('gem', 'Follicle extraction', 'With fine micro-punches, individual follicles are taken from the donor area at the back or sides of the head, where hair is most resistant to hair loss.'),
                         ('lift', 'Implantation', 'The follicles are implanted into the thinning or bald areas, following your natural direction of growth.'),
                         ('care', 'Closure and recovery', 'FUE needs no stitches. You receive personal aftercare instructions, for example on how to wash your hair.')],
 'dhi-hair-transplant': [('moon', 'Preparation and anaesthesia', 'The surgeon discusses your wishes and examines your scalp. On the day of the procedure you receive local anaesthesia.'),
                         ('gem', 'Follicle extraction', 'Individual follicles are taken from the donor area at the back or sides of the head.'),
                         ('lift', 'Direct implantation', 'The follicles are loaded into the Choi pen and placed directly into the recipient area, with precise control of depth, angle and direction.'),
                         ('care', 'Closure and recovery', 'DHI needs no stitches. You are monitored briefly and receive personal aftercare instructions.')],
 'beard-and-moustache-transplant': [('moon', 'Preparation and anaesthesia', 'After a detailed consultation about your wishes and the design, the procedure takes place under local anaesthesia.'),
                                    ('gem', 'Follicle harvesting', 'Follicles are taken from the donor area at the back of the head with the FUE or DHI technique.'),
                                    ('face', 'Implantation and design', 'The follicles are implanted into the beard or moustache area in the natural direction of growth; density and shape are planned with you.'),
                                    ('care', 'Closure and recovery', 'The donor area is cared for and you receive detailed aftercare instructions.')],
 'eyebrow-transplant': [('moon', 'Preparation and anaesthesia', 'After a detailed consultation about your wishes and the shape of your eyebrows, the procedure takes place under local anaesthesia.'),
                        ('gem', 'Follicle extraction', 'Single fine follicles are taken from the donor area at the back of the head.'),
                        ('eye', 'Implantation and shaping', 'The follicles are implanted with the DHI technique, following the natural growth pattern for an even, symmetrical shape.'),
                        ('care', 'Closure and recovery', 'You are monitored briefly and receive personal aftercare instructions.')],
}
