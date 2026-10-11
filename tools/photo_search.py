"""Search Unsplash + Pixabay, save candidates JSON and a numbered contact sheet.
usage: photo_search.py OUTDIR "query" [n_each]   -> OUTDIR/<slug>.json + .jpg
Unsplash credential is injected by the proxy (no key needed here); Pixabay uses $PIXABAY_API_KEY."""
import json, os, re, subprocess, sys, urllib.parse
import cv2, numpy as np
out, q = sys.argv[1], sys.argv[2]; n = int(sys.argv[3]) if len(sys.argv) > 3 else 8
os.makedirs(out, exist_ok=True); slug = re.sub(r'[^a-z0-9]+', '-', q.lower()).strip('-')
def get(url, hdr=()):
    a = ['curl', '-sS', '--max-time', '30', url]
    for h in hdr: a += ['-H', h]
    r = subprocess.run(a, capture_output=True).stdout
    try: return json.loads(r)
    except Exception: return {}
c = []
u = get('https://api.unsplash.com/search/photos?' + urllib.parse.urlencode(dict(query=q, per_page=n, orientation='landscape', content_filter='high')), ['Accept-Version: v1'])
for r in u.get('results', []):
    c.append(dict(src='unsplash', id=r['id'], thumb=r['urls']['small'], full=r['urls']['raw'] + '&w=1600&q=80&fm=jpg&fit=max', dl=r['links']['download_location'], author=r['user']['name'], desc=(r.get('alt_description') or '')[:80]))
k = os.environ.get('PIXABAY_API_KEY')
if k:
    p = get('https://pixabay.com/api/?' + urllib.parse.urlencode(dict(key=k, q=q, image_type='photo', orientation='horizontal', safesearch='true', per_page=max(3, n))))
    for h in p.get('hits', [])[:n]:
        c.append(dict(src='pixabay', id=str(h['id']), thumb=h['webformatURL'], full=h['largeImageURL'], dl='', author=h['user'], desc=h['tags'][:80]))
tiles = []
for i, x in enumerate(c):
    f = os.path.join(out, 'th_%s_%s.jpg' % (x['src'], x['id']))
    if not os.path.exists(f): subprocess.run(['curl', '-sS', '--max-time', '30', '-o', f, x['thumb']])
    im = cv2.imread(f); im = np.zeros((200, 300, 3), np.uint8) if im is None else im
    h, w = im.shape[:2]; s = min(320 / w, 210 / h); im = cv2.resize(im, (int(w * s), int(h * s)))
    t = np.full((235, 320, 3), 255, np.uint8); t[:im.shape[0], :im.shape[1]] = im
    cv2.putText(t, '%d %s' % (i, x['src']), (4, 230), 0, 0.5, (0, 0, 190), 1); tiles.append(t)
json.dump(c, open(os.path.join(out, slug + '.json'), 'w'), indent=1)
if tiles:
    while len(tiles) % 4: tiles.append(np.full((235, 320, 3), 255, np.uint8))
    cv2.imwrite(os.path.join(out, slug + '.jpg'), np.vstack([np.hstack(tiles[i:i + 4]) for i in range(0, len(tiles), 4)]), [cv2.IMWRITE_JPEG_QUALITY, 72])
print(slug, len(c))
