"""Place AI photos uploaded as m<oldID>.png: convert to JPG, upload, copy alt, swap in all pages.
usage: place_ai_photos.py WORKDIR code1 code2 ...  (PNG files must already be in WORKDIR)"""
import json, re, subprocess, sys, os
from PIL import Image
W = 'https://medluxlife-6j8sz55bpn.live-website.com/wp-json'
D, codes = sys.argv[1], sys.argv[2:]
def run(*a): return subprocess.run(a, capture_output=True).stdout
pages = []
for pg in (1, 2):
    r = json.loads(run('curl', '-sS', f'{W}/wp/v2/pages?per_page=100&page={pg}&context=edit&_fields=id,content.raw'))
    if isinstance(r, list): pages += r
os.makedirs('backups/wp/ai_photos', exist_ok=True)
log = json.load(open('content/ai_photo_map.json')) if os.path.exists('content/ai_photo_map.json') else {}
changed = {}
for code in codes:
    old = int(code[1:])
    om = json.loads(run('curl', '-sS', f'{W}/wp/v2/media/{old}?_fields=id,alt_text,source_url'))
    jpg = f'{D}/{code}.jpg'
    Image.open(f'{D}/{code}.png').convert('RGB').save(jpg, quality=84, optimize=True, progressive=True)
    r = json.loads(run('curl', '-sS', '-X', 'POST', W + '/wp/v2/media', '-H', f'Content-Disposition: attachment; filename=medluxlife-ai-{code}.jpg', '-H', 'Content-Type: image/jpeg', '--data-binary', '@' + jpg))
    run('curl', '-sS', '-X', 'POST', f"{W}/wp/v2/media/{r['id']}", '-H', 'Content-Type: application/json', '-d', json.dumps({'alt_text': om['alt_text'], 'caption': 'AI-generated illustration photo'}))
    stem = om['source_url'].rsplit('/', 1)[1].rsplit('.', 1)[0]
    for p in pages:
        c = changed.get(p['id'], p['content']['raw'])
        if not re.search(r'wp-image-%d\b' % old, c): continue
        if p['id'] not in changed: json.dump(p, open(f"backups/wp/ai_photos/page{p['id']}_before_{code}.json", 'w'))
        c = re.sub(r'https?://[^"\s]*?/' + re.escape(stem) + r'(-\d+x\d+)?\.(jpe?g|png|webp)', r['source_url'], c)
        for a, b in ((f'"id":{old},', f'"id":{r["id"]},'), (f'"id":{old}}}', f'"id":{r["id"]}}}')):
            c = c.replace(a, b)
        c = re.sub(r'wp-image-%d\b' % old, 'wp-image-%d' % r['id'], c)
        changed[p['id']] = c
    log[code] = dict(old=old, new=r['id'], url=r['source_url'], kb=os.path.getsize(jpg) // 1024)
    print(code, old, '->', r['id'], log[code]['kb'], 'KB')
for pid, c in changed.items():
    r = json.loads(run('curl', '-sS', '-X', 'POST', f'{W}/wp/v2/pages/{pid}', '-H', 'Content-Type: application/json', '-d', json.dumps({'content': c})))
    print('page', pid, r.get('modified'))
json.dump(log, open('content/ai_photo_map.json', 'w'), indent=1)
