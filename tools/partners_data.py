#!/usr/bin/env python3
"""Partner doctors → content/partners/doctors.json (one format for Yeditepe and Celyxmed, Emrah 2026-10-28).
Source: the partners' own websites (scraped HTML in the scratchpad, see PROJECT.md). Kept: title, name, departments, hospital,
education, specialisation / academic career, areas of interest, foreign languages, photo. Left out on purpose: e-mail addresses,
phone numbers, awards, publication counts, memberships, career narratives (privacy, HWG, volume). Research assistants are not listed.
usage: partners_data.py SCRAPED_JSON"""
import json, pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent

TITLE_TR = [('Doç. Dr. Doç. Dr.', 'assoc'), ('Prof. Dr.', 'prof'), ('Doç. Dr.', 'assoc'), ('Dr. Öğr. Ü.', 'asst'), ('Dr. Öğr. Üyesi', 'asst'),
            ('Uzm. Dr.', 'spec'), ('Op. Dr.', 'op'), ('Fizyoterapist', 'physio'), ('Odyolog', 'audio'),
            ('Uzm. Klinik Psikolog, Uzm. Dyt.', 'psydiet'), ('Uzm. Psikolog', 'psy'), ('Uzm. Dyt.', 'diet')]
HOSP = {'yeditepe-university-kozyatagi-hospital': 'kozyatagi', 'yeditepe-university-kosuyolu-hospital': 'kosuyolu',
        'yeditepe-university-eye-center': 'eye', 'yeditepe-university-genetic-diagnosis-center': 'genetic',
        'yeditepe-university-tissue-typing-laboratory': 'tissue', 'yeditepe-university-dental-hospital': 'dental'}
F = {'Faculty and Graduation Year': 'edu', 'Place and Year of Specialization': 'spec', 'Side Branch Specialization': 'side',
     'Place and Year of PhD Associate Professorship': 'assoc', 'Professorship Place and Year': 'prof', 'Foreign Languages': 'langs'}
# Yeditepe's department names → the names our own treatment pages use (British spelling), so the same translations apply
DEPT_MAP = {'Applications in Nuclear Medicine': 'Nuclear Medicine', 'Hematology': 'Haematology', 'Obstetrics and Gynecology': 'Obstetrics and Gynaecology',
            'Thyroid - Parathyroid Diseases and Surgery Clinic': 'Thyroid and Parathyroid Diseases and Surgery Clinic',
            'Endocrinology and Metabolism Diseases': 'Endocrinology and Metabolic Diseases', 'Anesthesiology and Reanimation': 'Anaesthesiology and Reanimation',
            'Obesity Surgery': 'Bariatric Surgery', 'Infectious Diseases and Microbiology': 'Infectious Diseases and Clinical Microbiology',
            'Gynecological Oncology': 'Gynaecological Oncology', 'Chest Diseases': 'Chest Diseases (Pulmonology)', 'Onkolojik Cerrahi': 'Surgical Oncology',
            'Newborn Intensive Care Unit (NICU)': 'Neonatal Intensive Care Unit (NICU)', 'Transfusion Center': 'Transfusion Centre', 'Algology': 'Algology (Pain Medicine)'}


# departments Yeditepe links only in Turkish (/tibbi-birimler/…) on some English doctor pages
TR_DEPT = {'Tıbbi Biyokimya': 'Medical Biochemistry'}


def dept(n):
    n = n.strip()
    n = DEPT_MAP.get(n, n)
    if n.startswith('Pediatric'):
        n = 'Paediatric' + n[len('Pediatric'):]
    return n.replace('Paediatric Hematology', 'Paediatric Haematology')


LANGS = {'english': 'English', 'german': 'German', 'french': 'French', 'spanish': 'Spanish', 'russian': 'Russian', 'azerbaijanese': 'Azerbaijani',
         'azerbaijani': 'Azerbaijani', 'bulgarian': 'Bulgarian', 'persian': 'Persian', 'japanese': 'Japanese', 'swahili': 'Swahili', 'arabic': 'Arabic', 'italian': 'Italian'}


def clean(s):
    s = re.sub(r'\s+', ' ', s or '').strip(' -–:;,')
    return '' if s in ('', '-', '.', 'None') else s


def slug(s):
    t = s.lower()
    for a, b in zip('çğıöşüâîû', 'cgiosuaiu'):
        t = t.replace(a, b)
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')


def yeditepe(rows):
    out = []
    for x in rows:
        tr = (x.get('tr') or {}).get('h1') or ''
        en = x['en']['h1'] or ''
        if en.startswith('Research Assistant') or tr.startswith('Tıpta Uzmanlık'):
            continue
        key, name = None, None
        for p, k in TITLE_TR:
            if tr.startswith(p):
                key, name = k, tr[len(p):].strip()
                break
        if not key:  # one doctor without a Turkish page
            key, name = 'spec', re.sub(r'^Specialist Doctor\s+|,?\s*M\.D\.?$', '', en).strip()
        d = {'partner': 'yeditepe', 'title': key, 'name': name, 'slug': slug(name),
             'depts': list(dict.fromkeys(dept(n) for n in ([n for _, n in x['deps']] or [n for _, n in x['en']['deps']]
                                                       or [TR_DEPT.get(n, n) for _, n in (x.get('tr') or {}).get('deps', [])]))),
             'hospitals': sorted({HOSP[h] for h, _ in x['en']['hospitals'] if h in HOSP}),
             'photo_src': 'https://yeditepehastaneleri.com' + (x.get('photo_big') or x['photo'])}
        for k, v in x['en']['fields']:
            if k in F and clean(v):
                d[F[k]] = clean(v)
        for k, v in x['en']['lists']:
            if k.rstrip(' :') in ('Fields of Study', 'İlgi Alanları'):
                d['interests'] = [clean(i) for i in v if clean(i)][:14]
        if d.get('langs'):
            d['langs'] = [LANGS[w.lower()] for w in re.split(r'[\s,/;]+|\band\b', d['langs']) if w.lower() in LANGS]
        out.append(d)
    return out


CELYX = [  # hand-picked from celyxmed.com/doctor-detail/<id> (EN), photos /Uploads/photo/doktorlarimiz/
    dict(title='op', name='Kemal Aytuğlu', depts=['Plastic, Reconstructive and Aesthetic Surgery'], photo='op-dr-kemal-aytuglu__doktorlarimiz-55539_DesktopImage_b.webp',
         edu='Akdeniz University Faculty of Medicine, Antalya, 1993',
         spec='Haydarpaşa Numune Training and Research Hospital, Plastic and Reconstructive Surgery, 1999',
         interests=['Rhinoplasty (nose reshaping)', 'Liposuction', 'Breast aesthetics', 'Hair transplantation', 'Other plastic surgery procedures']),
    dict(title='dr', name='Damla Erdoğan', depts=['Medical Aesthetics'], photo='dr-damla-erdogan__doktorlarimiz-16698_DesktopImage_b.webp',
         edu='Yeditepe University Faculty of Medicine, Doctor of Medicine (M.D.), 2020',
         career=["St George's University of London, Master of Research in Biomedical Sciences (Infectious Diseases), 2012", 'Kingston University, London, B.Sc. Biomedical Sciences, 2011'],
         role='Medical Director of Celyxmed'),
    dict(title='drdt', name='Fikri Can Ayık', depts=['Oral and Maxillofacial Surgery'], photo='dr-dt-fikri-can-ayik__doktorlarimiz-68419_DesktopImage_b.webp',
         edu='Yeditepe University Faculty of Dentistry, 2017', career=['Yeditepe University Dental Hospital, surgical assistant, 2017–2021'],
         interests=['All-on-4', 'All-on-6', 'Implant treatments', 'Impacted tooth surgery', 'Soft and hard tissue surgery', 'Pink aesthetics', 'TMJ / jaw joint disorders',
                    'Medical aesthetics (Botox)', 'Jaw cyst and tumour surgery', 'Periodontal diseases and surgery', 'Endodontic surgery']),
    dict(title='dt', name='Elif Nil Ada', depts=['Dentistry'], photo='dt-elif-nil-ada__doktorlarimiz-23772_DesktopImage_b.webp',
         career=['Dentist at Celyxmed since 2025', 'Dentist at private oral and dental health polyclinics in Istanbul, 2023–2025']),
    dict(title='dt', name='Büşra Betül Öztürk', depts=['Prosthodontics'], photo='betül-hoca-500x500-2__doktorlarimiz-10114_DesktopImage_b.webp',
         career=['Dentist at private hospitals and oral and dental health polyclinics, 2021–2024'],
         interests=['Porcelain veneers', 'Zirconium crowns', 'E.max crowns', 'Metal-supported porcelain crowns', 'Implant-supported crowns', 'Removable prostheses (dentures)']),
    dict(title='drdt', name='Oğuzhan Tunç', depts=['Oral and Maxillofacial Surgery'], photo='oguzhoca__doktorlarimiz-54395_DesktopImage_b.webp',
         edu='Yeditepe University Faculty of Dentistry (English programme), 2018',
         spec='Doctoral programme in Oral and Maxillofacial Surgery, Yeditepe University Faculty of Dentistry',
         interests=['Surgical extraction of impacted wisdom teeth', 'Dental implant procedures', 'Treatment of cysts of the oral region', 'Hard and soft tissue surgery']),
    dict(title='dt', name='Selin Güzel', depts=['Prosthodontics'], photo='selin-hanim-1__doktorlarimiz-22058_DesktopImage_b.webp'),
    dict(title='dr', name='Cüneyt Çavdar', depts=['Hair Transplantation'], photo='cüneyt-hoca-2__doktorlarimiz-95657_DesktopImage_b.webp',
         edu='Uludağ University Faculty of Medicine, 1997', career=['Family medicine since 2008', 'Emergency medicine, 2001–2008'],
         role='Hair transplant coordinator',
         interests=['Hair transplant procedures', 'General health examinations', 'Preventive medicine']),
]


def celyx():
    out = []
    for c in CELYX:
        d = dict(c, partner='celyxmed', hospitals=['celyxmed'], slug=slug(c['name']),
                 photo_src='https://www.celyxmed.com/Uploads/photo/doktorlarimiz/' + c.pop('photo') if 'photo' in c else '')
        d.pop('photo', None)
        out.append(d)
    return out


if __name__ == '__main__':
    rows = json.load(open(sys.argv[1]))
    docs = celyx() + yeditepe(rows)
    old = {(o['partner'], o['slug']): o for o in json.load(open(ROOT / 'content/partners/doctors.json'))} if (ROOT / 'content/partners/doctors.json').exists() else {}
    for x in docs:  # keep the media ids of portraits uploaded earlier (tools/partners_photos.py)
        o = old.get((x['partner'], x['slug']), {})
        if o.get('photo_id'):
            x['photo_id'], x['photo_url'] = o['photo_id'], o['photo_url']
    json.dump(docs, open(ROOT / 'content/partners/doctors.json', 'w'), ensure_ascii=False, indent=1)
    import collections
    print(len(docs), collections.Counter(d['title'] for d in docs), collections.Counter(h for d in docs for h in d['hospitals']))
