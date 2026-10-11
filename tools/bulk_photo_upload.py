import json, re, subprocess, sys, os, concurrent.futures as cf
S, W = sys.argv[1], sys.argv[2]
C = {k: json.load(open(f'{S}/{f}')) for k, f in (('a', 'cands.json'), ('b', 'cands_b.json'), ('c', 'cands_c.json'))}
picks = {}
for l in open(S + '/picks.txt'):
    slot, ref = l.split(); f, k, i = ref.split(':'); picks[slot] = C[f][k]['c'][int(i)]
ids = [(c['src'], c['id']) for c in picks.values()]; assert len(ids) == len(set(ids)), 'dup'
media = {str(m['id']): m for m in json.load(open(S + '/media.json'))}
NEW = {  # slot: (page, heading, alt)
 'c263a': (263, 'Liposuction', 'Body contouring treatment on the abdomen'),
 'c263b': (263, 'Breast Lift (Mastopexy)', 'Woman in a white shirt, studio portrait'),
 'c263c': (263, 'Otoplasty (Ear Correction)', 'Side view of a woman’s ear and profile'),
 'c263d': (263, 'Neck Lift', 'Neck and jawline in soft light'),
 'c264a': (264, 'Skin Mesotherapy', 'Facial skin treatment in a clinic'),
 'c264b': (264, 'Exosome Skin Treatments', 'Skin care serum bottle'),
 'c260a': (260, 'Zirconium Veneers', 'Bright, natural smile'),
 'c260b': (260, 'Periodontology (Gum Treatment)', 'Dentist checking teeth and gums with a mirror'),
 'c260c': (260, 'Restorative Dental Treatments', 'Dentist examining a patient’s teeth'),
 'c260d': (260, 'Root Canal Treatment', 'Modern dental treatment room'),
 'c260e': (260, 'Masseter Botox (Jaw Botox)', 'Woman touching her jawline'),
 'c260f': (260, 'TMJ Treatment', 'Woman holding her jaw in discomfort'),
 'c260g': (260, 'Orthodontics', 'Smile with dental braces'),
 'c261a': (261, 'Sapphire FUE', 'Hair transplant procedure in a clinic'),
 'c261b': (261, 'DHI (Direct Hair Implantation)', 'Doctor reviewing treatment notes on a tablet'),
 'c261c': (261, 'FUT (Follicular Unit Transplantation)', 'Thinning hair on the back of the head'),
 'c261d': (261, 'Red Light Therapy', 'Red light device used during a skin treatment'),
 'c261e': (261, 'PRP (Platelet-Rich Plasma)', 'Syringe prepared for a treatment'),
 'c267a': (267, 'Glutathione', 'Fresh antioxidant-rich berries'),
}
def run(*a): return subprocess.run(a, capture_output=True).stdout
def upload(slot):
    c = picks[slot]; f = f'{S}/full/{slot}.jpg'; os.makedirs(f'{S}/full', exist_ok=True)
    if not os.path.exists(f) or os.path.getsize(f) < 5000: run('curl', '-sSL', '--max-time', '90', '-o', f, c['full'])
    if c.get('dl'): run('curl', '-sS', '-o', '/dev/null', c['dl'], '-H', 'Accept-Version: v1')
    alt = NEW[slot][2] if slot in NEW else media[slot]['alt_text']
    name = 'medluxlife-photo-%s.jpg' % slot
    r = json.loads(run('curl', '-sS', '-X', 'POST', W + '/wp/v2/media', '-H', 'Content-Disposition: attachment; filename=' + name, '-H', 'Content-Type: image/jpeg', '--data-binary', '@' + f))
    run('curl', '-sS', '-X', 'POST', f"{W}/wp/v2/media/{r['id']}", '-H', 'Content-Type: application/json', '-d', json.dumps({'alt_text': alt, 'caption': f"Photo: {c['author']} / {c['src'].title()}"}))
    return slot, dict(new=r['id'], url=r['source_url'], alt=alt, src=c['src'], pid=c['id'], author=c['author'])
out = json.load(open(S + '/uploaded.json')) if os.path.exists(S + '/uploaded.json') else {}
todo = [s for s in picks if s not in out]
with cf.ThreadPoolExecutor(4) as ex:
    for slot, v in ex.map(upload, todo): out[slot] = v; print(slot, '->', v['new'], flush=True)
json.dump(out, open(S + '/uploaded.json', 'w'), indent=1)
