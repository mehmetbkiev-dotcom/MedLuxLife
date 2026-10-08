import json, os, sys, subprocess, urllib.parse, concurrent.futures as cf
import cv2, numpy as np
S = sys.argv[1]; SL = sys.argv[2]; TAG = sys.argv[3]; slots = [l.strip().split('|') for l in open(S + '/' + SL) if l.strip()]
K = os.environ['PIXABAY_API_KEY']
def get(url, hdr=()):
    a = ['curl', '-sS', '--max-time', '30', url]
    for h in hdr: a += ['-H', h]
    try: return json.loads(subprocess.run(a, capture_output=True).stdout)
    except Exception: return {}
def search(key, q):
    c = []
    if key.startswith('u') or (key.startswith('c26') and not key.startswith('c261') and not key.startswith('c267')):
        u = get('https://api.unsplash.com/search/photos?' + urllib.parse.urlencode(dict(query=q, per_page=5, orientation='landscape', content_filter='high')), ['Accept-Version: v1'])
        for r in u.get('results', []):
            c.append(dict(src='unsplash', id=r['id'], thumb=r['urls']['thumb'], full=r['urls']['raw'] + '&w=1600&q=80&fm=jpg&fit=max', dl=r['links']['download_location'], author=r['user']['name']))
    p = get('https://pixabay.com/api/?' + urllib.parse.urlencode(dict(key=K, q=q, image_type='photo', orientation='horizontal', safesearch='true', per_page=20)))
    for h in p.get('hits', [])[:10 - len(c) // 2]:
        c.append(dict(src='pixabay', id=str(h['id']), thumb=h['previewURL'].replace('_150', '_340') if False else h['webformatURL'].replace('_640', '_340'), full=h['largeImageURL'], dl='', author=h['user']))
    c = c[:10]
    os.makedirs(f'{S}/th', exist_ok=True)
    for i, x in enumerate(c):
        f = f'{S}/th/{key}_{i}.jpg'
        if True: subprocess.run(['curl', '-sS', '--max-time', '30', '-o', f, x['thumb']])
    return key, q, c
res = {}
import time
for sl in slots:
    key, q, c = search(*sl); res[key] = dict(q=q, c=c); time.sleep(1.5)
json.dump(res, open(S + '/cands_' + TAG + '.json', 'w'), indent=1)
TW, TH = 170, 113
rows = []
for key, q in slots:
    row = np.full((TH + 18, 10 * TW + 150, 3), 255, np.uint8)
    cv2.putText(row, key, (4, 40), 0, 0.6, (0, 0, 0), 2); cv2.putText(row, q[:20], (4, 65), 0, 0.38, (60, 60, 60), 1); cv2.putText(row, q[20:40], (4, 82), 0, 0.38, (60, 60, 60), 1)
    for i, x in enumerate(res[key]['c']):
        im = cv2.imread(f'{S}/th/{key}_{i}.jpg')
        if im is None: continue
        h, w = im.shape[:2]; s = min(TW / w, TH / h); im = cv2.resize(im, (int(w * s) - 4, int(h * s) - 4))
        x0 = 150 + i * TW; row[2:2 + im.shape[0], x0:x0 + im.shape[1]] = im
        cv2.putText(row, '%d%s' % (i, 'u' if x['src'] == 'unsplash' else ''), (x0 + 2, TH + 14), 0, 0.45, (0, 0, 200), 1)
    rows.append(row)
for n in range(0, len(rows), 7):
    cv2.imwrite(f'{S}/{TAG}_{n // 7:02d}.jpg', np.vstack(rows[n:n + 7]), [cv2.IMWRITE_JPEG_QUALITY, 75])
print(len(res), sum(len(v['c']) for v in res.values()))
