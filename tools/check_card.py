"""Check / optimise the photo of one card (or the intro) on a page.
usage: check_card.py PAGE_ID "Card heading|Intro" [--fix "alt text"]
Prints media info and saves a preview; with --fix converts PNG/heavy files to JPG (max 1600px, q82),
uploads, swaps it into every page that uses it and sets the alt text."""
import json, subprocess, re, sys, os, html
from PIL import Image
W = 'https://medluxlife-6j8sz55bpn.live-website.com/wp-json'
OLD = 'https://medluxlife-6j8sz55bpn.live-website.com'
OUT = '/tmp/claude-0/-home-user-MedLuxLife/58e49045-1f3b-5625-b667-4a635b0b1d5b/check'
os.makedirs(OUT, exist_ok=True)
def run(*a): return subprocess.run(a, capture_output=True).stdout
def page(pid): return json.loads(run('curl', '-sS', f'{W}/wp/v2/pages/{pid}?context=edit&_fields=id,content.raw'))['content']['raw']
pid, card = int(sys.argv[1]), sys.argv[2]
fix = sys.argv[sys.argv.index('--fix') + 1] if '--fix' in sys.argv else None
c = page(pid)
target = None
for m in re.finditer(r'<img [^>]*>', c):
    after = c[m.end():m.end() + 900]; h = re.search(r'<h[23][^>]*>(.*?)</h[23]>', after)
    is_card = 'medlux-card-img' in c[max(0, m.start() - 400):m.start()]
    name = html.unescape(re.sub('<[^>]+>', '', h.group(1))) if (h and is_card) else 'Intro'
    if name.lower() == card.lower() and not m.group(0).count('data:image'):
        target = m.group(0); break
if not target: sys.exit('card not found')
mid = int(re.search(r'wp-image-(\d+)', target).group(1))
md = json.loads(run('curl', '-sS', f'{W}/wp/v2/media/{mid}?_fields=id,source_url,mime_type,media_details,alt_text'))
d = md.get('media_details') or {}
src = md['source_url']; f = f'{OUT}/{mid}_orig'
if not os.path.exists(f): run('curl', '-sS', '-o', f, src.replace('https://medluxlife.de', OLD))
im = Image.open(f).convert('RGB'); prev = im.copy(); prev.thumbnail((900, 600)); prev.save(f'{OUT}/{pid}_{re.sub("[^a-z0-9]+", "-", card.lower())}.jpg', quality=85)
alt_now = re.search(r'alt="([^"]*)"', target).group(1)
print(json.dumps(dict(mid=mid, file=src.rsplit('/', 1)[1], mime=md['mime_type'], w=d.get('width'), h=d.get('height'), kb=(d.get('filesize') or 0) // 1024, alt_in_page=alt_now)))
print('preview:', f'{OUT}/{pid}_{re.sub("[^a-z0-9]+", "-", card.lower())}.jpg')
if fix is None: sys.exit()
new_id, new_url = mid, src
if md['mime_type'] != 'image/jpeg' or (d.get('filesize') or 0) > 400_000 or (d.get('width') or 0) > 1800:
    im.thumbnail((1600, 1600), Image.LANCZOS); out = f'{OUT}/{mid}_opt.jpg'; im.save(out, quality=82, optimize=True, progressive=True)
    stem = re.sub(r'[^a-z0-9]+', '-', os.path.splitext(src.rsplit('/', 1)[1])[0].lower()).strip('-')[:60]
    up = json.loads(run('curl', '-sS', '-X', 'POST', W + '/wp/v2/media', '-H', f'Content-Disposition: attachment; filename={stem}-opt.jpg', '-H', 'Content-Type: image/jpeg', '--data-binary', '@' + out))
    new_id, new_url = up['id'], up['source_url']
    print('optimised', d.get('filesize', 0) // 1024, 'KB ->', os.path.getsize(out) // 1024, 'KB, media', new_id)
run('curl', '-sS', '-o', '/dev/null', '-X', 'POST', f'{W}/wp/v2/media/{new_id}', '-H', 'Content-Type: application/json', '-d', json.dumps({'alt_text': fix}))
ids = json.load(open('/home/user/MedLuxLife/content/banner_page_ids.json'))
for p in ids:
    cc = page(p)
    if not re.search(r'wp-image-%d\b' % mid, cc): continue
    os.makedirs('/home/user/MedLuxLife/backups/wp/card_checks', exist_ok=True)
    open(f'/home/user/MedLuxLife/backups/wp/card_checks/page{p}_before_{mid}.html', 'w').write(cc)
    def sw(mm):
        t = mm.group(0)
        if not re.search(r'wp-image-%d\b' % mid, t): return t
        t = re.sub(r'src="[^"]+"', 'src="%s"' % new_url, t)
        t = re.sub(r'alt="[^"]*"', 'alt="%s"' % html.escape(fix), t)
        return re.sub(r'wp-image-%d\b' % mid, 'wp-image-%d' % new_id, t)
    cc = re.sub(r'<img [^>]*>', sw, cc).replace('"id":%d,' % mid, '"id":%d,' % new_id)
    r = json.loads(run('curl', '-sS', '-X', 'POST', f'{W}/wp/v2/pages/{p}', '-H', 'Content-Type: application/json', '-d', json.dumps({'content': cc})))
    print('updated page', p, r.get('modified'))
