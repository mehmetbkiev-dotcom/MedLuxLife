"""Build ready-to-paste ChatGPT prompts (4 different images per card) from the 4-variant workflow result.
usage: build_4x_prompts.py RESULT.json SLOTS.json OUT.md"""
import json, sys
res, slots_f, out = sys.argv[1:4]
r = json.load(open(res)); r = json.loads(r) if isinstance(r, str) else r
meta = {s['code']: s for s in json.load(open(slots_f))}
LABEL = {'A': 'still life, no people', 'B': 'people', 'C': 'everyday life / another idea', 'D': 'process, detail or place'}
COMMON = '''FORMAT (each image): ONE full-frame landscape photo, 3:2, 1536 x 1024 px, edge to edge. No borders, bands, blurred fill, collage, multiple panels or mock-ups.

STYLE: High-end editorial photography, true-to-life colours, natural skin, realistic – not illustration, 3D or CGI. Follow each scene exactly. Do NOT default to a white-and-gold luxury clinic, marble, orchids, beige knitwear or a doctor-patient desk scene, and do not reuse the same person in two images.

RULES: No text, letters, numbers, logos, labels, signage, readable screens or brand names anywhere. No before/after comparison, no results claims, no blood, wounds, incisions or needles in skin, no nudity or lingerie; modest clothing. No real or recognisable people or places.'''
def prompt(s):
    m = meta[s['code']]; c = s['code']
    card = m['card'] if m['card'] != 'Intro' else m['page']
    head = (f"Create FOUR separate photorealistic photos for a premium German medical-travel website (MedLuxLife), "
            f"topic \"{card}\" ({m['page']}). Each image must be its OWN separate file, NOT a grid or collage, and the four images must show four clearly different ideas, people, settings, light and colours. "
            f"Name them {c}-1.png, {c}-2.png, {c}-3.png, {c}-4.png.")
    parts = [head]
    for n, v in enumerate(s['variants'], 1):
        parts.append(f"IMAGE {n} – {LABEL.get(v['type'], v['type'])}: {v['scene']}")
    parts.append(COMMON + (f" Also avoid: {s['avoid']}" if s.get('avoid') else ''))
    return '\n\n'.join(parts)
L = ['# MedLuxLife — ChatGPT prompts, 4 images per card\n',
     'Each card has a ready prompt for 4 different photos (1 = still life, 2 = people, 3 = everyday life / another idea, 4 = process / detail / place). Paste one prompt into ChatGPT, choose the best image and paste it into the Claude chat with its code.\n']
page = None
for s in r['slots']:
    m = meta[s['code']]
    if m['page'] != page:
        page = m['page']; L.append(f'\n## {page}\n')
    L.append(f"### {s['code']} — {m['card'] if m['card']!='Intro' else 'Intro photo'}\n\n```\n{prompt(s)}\n```\n")
open(out, 'w').write('\n'.join(L))
print(len(r['slots']), 'prompts ->', out)
