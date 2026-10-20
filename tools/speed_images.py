#!/usr/bin/env python3
"""Lighter copies of heavy photos (same picture) and swap them into every page that uses them.
usage: speed_images.py MID [MID ...]   or   MID=/path/to/ready-file.png (an already optimised file, e.g. a logo with transparency)
Photo (PNG/JPG, any size) -> JPG q85, max 1200 px, new media '<stem>-opt.jpg' with the same alt text.
Every page whose content uses wp-image-MID (or the old file name) is backed up to backups/wp/speed_images/ and updated."""
import html, json, os, re, subprocess, sys
from PIL import Image
W = 'https://medluxlife-6j8sz55bpn.live-website.com'
CK = '/tmp/claude-0/-home-user-MedLuxLife/58e49045-1f3b-5625-b667-4a635b0b1d5b/check'
B = '/home/user/MedLuxLife/backups/wp/speed_images'
os.makedirs(B, exist_ok=True); os.makedirs(CK, exist_ok=True)
run = lambda *a: subprocess.run(a, capture_output=True).stdout
get = lambda u: json.loads(run('curl', '-sS', u))
swap = {}
for arg in sys.argv[1:]:
    mid, ready = (int(arg.split('=')[0]), arg.split('=', 1)[1]) if '=' in arg else (int(arg), None)
    md = get(f'{W}/wp-json/wp/v2/media/{mid}?context=edit&_fields=source_url,alt_text,media_details')
    src = f'{CK}/{mid}_orig'
    run('curl', '-sS', '-o', src, md['source_url'].replace('https://medluxlife.de', W))
    stem = re.sub(r'[^a-z0-9]+', '-', os.path.splitext(md['source_url'].rsplit('/', 1)[1])[0].lower()).strip('-')[:60]
    if ready:
        out, ext, ctype = ready, os.path.splitext(ready)[1].lstrip('.'), 'image/png' if ready.endswith('.png') else 'image/webp'
        im = Image.open(out); w0 = Image.open(src).size
    else:
        im = Image.open(src).convert('RGB'); w0 = im.size; im.thumbnail((1200, 1200), Image.LANCZOS)
        out, ext, ctype = f'{CK}/{mid}_speed.jpg', 'jpg', 'image/jpeg'
        im.save(out, quality=85, optimize=True, progressive=True)
    up = json.loads(run('curl', '-sS', '-X', 'POST', W + '/wp-json/wp/v2/media', '-H', f'Content-Disposition: attachment; filename={stem}-opt.{ext}',
                        '-H', 'Content-Type: ' + ctype, '--data-binary', '@' + out))
    run('curl', '-sS', '-o', '/dev/null', '-X', 'POST', f'{W}/wp-json/wp/v2/media/{up["id"]}', '-H', 'Content-Type: application/json', '-d', json.dumps({'alt_text': md['alt_text']}))
    swap[mid] = (up['id'], up['source_url'], os.path.splitext(md['source_url'].rsplit('/', 1)[1])[0])
    print(f'{mid} -> {up["id"]}  {w0[0]}x{w0[1]} {os.path.getsize(src) // 1024} KB -> {im.size[0]}x{im.size[1]} {os.path.getsize(out) // 1024} KB')
pages = []
for pg in (1, 2, 3):
    r = get(f'{W}/wp-json/wp/v2/pages?per_page=100&context=edit&_fields=id,modified,content&page={pg}')
    if not isinstance(r, list) or not r:
        break
    pages += r
for p in pages:
    c = p['content']['raw']
    if not any(re.search(r'wp-image-%d\b' % m, c) or stem in c for m, (_, _, stem) in swap.items()):
        continue
    json.dump(p, open(f'{B}/page{p["id"]}_{p["modified"].replace(":", "")}.json', 'w'))
    def sw(mm):
        t = mm.group(0); m2 = re.search(r'wp-image-(\d+)\b', t)
        if not m2 or int(m2.group(1)) not in swap:
            return t
        old = int(m2.group(1)); nid, nurl, _ = swap[old]
        t = re.sub(r'src="[^"]+"', 'src="%s"' % nurl, t)
        return re.sub(r'wp-image-%d\b' % old, 'wp-image-%d' % nid, t)
    n = re.sub(r'<img [^>]*>', sw, c)
    for old, (nid, _, _) in swap.items():
        n = re.sub(r'"id":%d([,}])' % old, r'"id":%d\1' % nid, n)
    r = json.loads(subprocess.run(['curl', '-sS', '-X', 'POST', f'{W}/wp-json/wp/v2/pages/{p["id"]}', '-H', 'Content-Type: application/json', '--data-binary', '@-'],
                                  input=json.dumps({'content': n}).encode(), capture_output=True).stdout)
    raw = (r.get('content') or {}).get('raw', '')
    left = [o for o in swap if re.search(r'wp-image-%d\b' % o, raw)]
    print('page', p['id'], 'updated' if not left else f'STILL OLD {left}')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import cache_clear; print('page cache cleared:', cache_clear.clear())
