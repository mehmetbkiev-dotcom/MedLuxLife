"""Compress user-uploaded photos and swap them into every Health/hub page that uses them.
usage: compress_swap.py MID "alt text" [MID "alt text" ...]
Heavy files (PNG, >400 KB or >1800 px) become JPG q88, max 1600 px (new media '<stem>-opt.jpg');
alt text is set on the media and in the page. Pages are backed up to backups/wp/compress_swap/."""
import json, subprocess, re, html, os, sys
from PIL import Image
W = 'https://medluxlife-6j8sz55bpn.live-website.com/wp-json'; O = 'https://medluxlife-6j8sz55bpn.live-website.com'
CK = '/tmp/claude-0/-home-user-MedLuxLife/58e49045-1f3b-5625-b667-4a635b0b1d5b/check'
B = '/home/user/MedLuxLife/backups/wp/compress_swap'; os.makedirs(B, exist_ok=True); os.makedirs(CK, exist_ok=True)
def run(*a): return subprocess.run(a, capture_output=True).stdout
def get(u): return json.loads(run('curl', '-sS', u))
a = sys.argv[1:]; todo = {int(a[i]): a[i + 1] for i in range(0, len(a), 2)}
swap = {}
for mid, alt in todo.items():
    md = get(f'{W}/wp/v2/media/{mid}?_fields=source_url,mime_type,media_details'); d = md.get('media_details') or {}
    nid, nurl = mid, None
    if md['mime_type'] != 'image/jpeg' or (d.get('filesize') or 0) > 400_000 or (d.get('width') or 0) > 1800:
        src = f'{CK}/{mid}_orig'
        if not os.path.exists(src): run('curl', '-sS', '-o', src, md['source_url'].replace('https://medluxlife.de', O))
        im = Image.open(src).convert('RGB'); w0 = im.size[0]; im.thumbnail((1600, 1600), Image.LANCZOS)
        stem = re.sub(r'-scaled$', '', re.sub(r'[^a-z0-9]+', '-', os.path.splitext(md['source_url'].rsplit('/', 1)[1])[0].lower()).strip('-'))[:60]
        out = f'{CK}/{mid}_opt.jpg'; im.save(out, quality=88, optimize=True, progressive=True)
        up = json.loads(run('curl', '-sS', '-X', 'POST', W + '/wp/v2/media', '-H', f'Content-Disposition: attachment; filename={stem}-opt.jpg', '-H', 'Content-Type: image/jpeg', '--data-binary', '@' + out))
        nid, nurl = up['id'], up['source_url']
        print(f'{mid} -> {nid}  {w0}px -> {im.size[0]}px, {(d.get("filesize") or 0)//1024} KB -> {os.path.getsize(out)//1024} KB')
    run('curl', '-sS', '-o', '/dev/null', '-X', 'POST', f'{W}/wp/v2/media/{nid}', '-H', 'Content-Type: application/json', '-d', json.dumps({'alt_text': alt}))
    swap[mid] = (nid, nurl, alt)
ids = sorted(set(json.load(open('/home/user/MedLuxLife/content/health_page_ids.json'))) | set(json.load(open('/home/user/MedLuxLife/content/banner_page_ids.json'))))
for p in ids:
    dd = get(f'{W}/wp/v2/pages/{p}?context=edit&_fields=id,modified,content.raw'); c = dd['content']['raw']
    if not any(re.search(r'wp-image-%d\b' % m, c) for m in swap): continue
    json.dump(dd, open(f'{B}/page{p}_{dd["modified"].replace(":", "")}.json', 'w'))
    def sw(mm):
        t = mm.group(0); m2 = re.search(r'wp-image-(\d+)\b', t)
        if not m2 or int(m2.group(1)) not in swap: return t
        old = int(m2.group(1)); nid, nurl, alt = swap[old]
        if nurl: t = re.sub(r'src="[^"]+"', 'src="%s"' % nurl, t)
        t = re.sub(r'alt="[^"]*"', 'alt="%s"' % html.escape(alt), t) if 'alt="' in t else t.replace('<img ', '<img alt="%s" ' % html.escape(alt), 1)
        return re.sub(r'wp-image-%d\b' % old, 'wp-image-%d' % nid, t)
    n = re.sub(r'<img [^>]*>', sw, c)
    for old, (nid, _, _) in swap.items(): n = n.replace('"id":%d,' % old, '"id":%d,' % nid).replace('"id":%d}' % old, '"id":%d}' % nid)
    body = f'{CK}/body{p}.json'; open(body, 'w').write(json.dumps({'content': n}))
    r = json.loads(run('curl', '-sS', '-X', 'POST', f'{W}/wp/v2/pages/{p}', '-H', 'Content-Type: application/json', '--data-binary', '@' + body))
    raw = (r.get('content') or {}).get('raw', '')
    left = [o for o, (nid, _, _) in swap.items() if nid != o and re.search(r'wp-image-%d\b' % o, raw)]
    print('updated page', p, r.get('modified'), 'OK' if not left else f'STILL OLD {left}')
