"""Put a local photo as the intro photo of a page and swap the old intro media on every Health/hub page that uses it.
usage: place_intro.py PAGE_ID /path/to/image "alt text" [--only PAGE_ID,PAGE_ID]
--only limits the swap to those pages (when the old photo is shared with an unrelated page).
JPG q88, max 1600 px. Backups in backups/wp/hospital_photos/."""
import json, subprocess, re, html, os, sys
from PIL import Image
W = 'https://medluxlife-6j8sz55bpn.live-website.com/wp-json'
B = '/home/user/MedLuxLife/backups/wp/hospital_photos'; os.makedirs(B, exist_ok=True)
def run(*a): return subprocess.run(a, capture_output=True).stdout
def get(u): return json.loads(run('curl', '-sS', u))
pid, src, alt = int(sys.argv[1]), sys.argv[2], sys.argv[3]
only = {int(x) for x in sys.argv[sys.argv.index('--only') + 1].split(',')} if '--only' in sys.argv else None
pg = get(f'{W}/wp/v2/pages/{pid}?context=edit&_fields=slug,content.raw')
old = int(re.search(r'wp-image-(\d+)', re.search(r'<img [^>]*>', pg['content']['raw']).group(0)).group(1))
im = Image.open(src).convert('RGB'); im.thumbnail((1600, 1600), Image.LANCZOS)
name = f"{pg['slug']}-intro.jpg"; out = f'/tmp/claude-0/-home-user-MedLuxLife/58e49045-1f3b-5625-b667-4a635b0b1d5b/scratchpad/{name}'; im.save(out, quality=88, optimize=True, progressive=True)
up = json.loads(run('curl', '-sS', '-X', 'POST', W + '/wp/v2/media', '-H', f'Content-Disposition: attachment; filename={name}', '-H', 'Content-Type: image/jpeg', '--data-binary', '@' + out))
nid, nurl = up['id'], up['source_url']
run('curl', '-sS', '-o', '/dev/null', '-X', 'POST', f'{W}/wp/v2/media/{nid}', '-H', 'Content-Type: application/json', '-d', json.dumps({'alt_text': alt}))
print(f'old {old} -> new {nid} ({im.size[0]}x{im.size[1]}, {os.path.getsize(out)//1024} KB)')
ids = sorted(set(json.load(open('/home/user/MedLuxLife/content/health_page_ids.json'))) | set(json.load(open('/home/user/MedLuxLife/content/banner_page_ids.json'))))
for p in (sorted(only) if only else ids):
    d = get(f'{W}/wp/v2/pages/{p}?context=edit&_fields=id,modified,content.raw'); c = d['content']['raw']
    if not re.search(r'wp-image-%d\b' % old, c): continue
    json.dump(d, open(f'{B}/page{p}_before_{old}.json', 'w'))
    def sw(mm):
        t = mm.group(0)
        if not re.search(r'wp-image-%d\b' % old, t): return t
        t = re.sub(r'src="[^"]+"', 'src="%s"' % nurl, t)
        t = re.sub(r'alt="[^"]*"', 'alt="%s"' % html.escape(alt), t) if 'alt="' in t else t.replace('<img ', '<img alt="%s" ' % html.escape(alt), 1)
        return re.sub(r'wp-image-%d\b' % old, 'wp-image-%d' % nid, t)
    n = re.sub(r'<img [^>]*>', sw, c).replace('"id":%d,' % old, '"id":%d,' % nid).replace('"id":%d}' % old, '"id":%d}' % nid)
    body = f'/tmp/claude-0/-home-user-MedLuxLife/58e49045-1f3b-5625-b667-4a635b0b1d5b/scratchpad/body{p}.json'; open(body, 'w').write(json.dumps({'content': n}))
    r = json.loads(run('curl', '-sS', '-X', 'POST', f'{W}/wp/v2/pages/{p}', '-H', 'Content-Type: application/json', '--data-binary', '@' + body))
    print('updated page', p, r.get('modified'), 'OK' if not re.search(r'wp-image-%d\b' % old, r['content']['raw']) else 'FAIL')
