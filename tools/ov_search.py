"""Search Openverse (CC0 / public domain only) and build a numbered contact sheet.
usage: ov_search.py OUTDIR "query" [n] [source]
writes OUTDIR/<slug>.json (candidates) and OUTDIR/<slug>.jpg (contact sheet)"""
import json, os, re, subprocess, sys, urllib.parse
import cv2, numpy as np
out, q = sys.argv[1], sys.argv[2]
n = int(sys.argv[3]) if len(sys.argv) > 3 else 12
src = sys.argv[4] if len(sys.argv) > 4 else ''
os.makedirs(out, exist_ok=True)
slug = re.sub(r'[^a-z0-9]+', '-', q.lower()).strip('-') + (('-' + src) if src else '')
url = 'https://api.openverse.org/v1/images/?' + urllib.parse.urlencode(dict(q=q, license='cc0,pdm', page_size=20, mature='false', **({'source': src} if src else {})))
data = json.loads(subprocess.run(['curl', '-sS', '--max-time', '30', url], capture_output=True).stdout)
res = [r for r in data.get('results', []) if (r.get('width') or 0) >= 900][:n]
tiles = []
for i, r in enumerate(res):
    p = os.path.join(out, 'th_' + r['id'] + '.jpg')
    if not os.path.exists(p):
        subprocess.run(['curl', '-sS', '--max-time', '30', '-o', p, 'https://api.openverse.org/v1/images/%s/thumb/' % r['id']])
    im = cv2.imread(p)
    if im is None: im = np.zeros((200, 300, 3), np.uint8)
    h, w = im.shape[:2]; s = min(300 / w, 220 / h); im = cv2.resize(im, (int(w * s), int(h * s)))
    t = np.full((240, 300, 3), 255, np.uint8); t[:im.shape[0], :im.shape[1]] = im
    cv2.putText(t, '%d %s' % (i, r['source'][:10]), (4, 236), 0, 0.5, (0, 0, 200), 1)
    tiles.append(t)
json.dump(res, open(os.path.join(out, slug + '.json'), 'w'))
if tiles:
    while len(tiles) % 4: tiles.append(np.full((240, 300, 3), 255, np.uint8))
    rows = [np.hstack(tiles[i:i + 4]) for i in range(0, len(tiles), 4)]
    cv2.imwrite(os.path.join(out, slug + '.jpg'), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 70])
print(slug, len(res), data.get('result_count'))
