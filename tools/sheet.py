# usage: sheet.py OUTDIR NAME "query1" ["query2" ...]  -> OUTDIR/NAME.jpg contact sheet + NAME.json
import sys, json, subprocess, urllib.parse, io
from PIL import Image, ImageDraw, ImageFont
out, name, queries = sys.argv[1], sys.argv[2], sys.argv[3:]
def get(url):
    return subprocess.run(['curl', '-sS', '--max-time', '60', url], capture_output=True, check=True).stdout
seen, items = set(), []
for q in queries:
    u = 'https://api.unsplash.com/search/photos?' + urllib.parse.urlencode(
        {'query': q, 'per_page': 12, 'orientation': 'landscape', 'content_filter': 'high'})
    for r in json.loads(get(u))['results']:
        if r['id'] in seen or r['width'] < 1600: continue
        seen.add(r['id'])
        items.append({'id': r['id'], 'q': q, 'w': r['width'], 'h': r['height'],
                      'user': r['user']['name'], 'desc': r.get('alt_description'),
                      'raw': r['urls']['raw'], 'small': r['urls']['small'],
                      'dl': r['links']['download_location'], 'html': r['links']['html'],
                      'premium': r.get('premium', False) or bool(r.get('sponsorship'))})
items = [i for i in items if not i['premium']][:24]
W, H, cols = 400, 260, 4
rows = (len(items) + cols - 1) // cols
sheet = Image.new('RGB', (cols * W, rows * (H + 24)), 'white')
d = ImageDraw.Draw(sheet)
font = ImageFont.load_default(size=20)
for n, it in enumerate(items):
    im = Image.open(io.BytesIO(get(it['small']))).convert('RGB')
    im.thumbnail((W - 6, H - 6))
    x, y = (n % cols) * W, (n // cols) * (H + 24)
    sheet.paste(im, (x + 3, y + 3))
    d.text((x + 6, y + H), f"{n + 1}  {it['user'][:28]}", fill='black', font=font)
    d.rectangle([x + 3, y + 3, x + 60, y + 32], fill='black')
    d.text((x + 10, y + 6), str(n + 1), fill='yellow', font=font)
sheet.save(f'{out}/{name}.jpg', quality=82)
json.dump(items, open(f'{out}/{name}.json', 'w'), indent=1)
print(len(items))
