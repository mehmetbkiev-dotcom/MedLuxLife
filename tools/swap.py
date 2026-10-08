# usage: swap.py PAGE_ID PICKS.out.json [--apply]  — swaps old media for new in page content (backup must exist in backup/)
import sys, json, re, subprocess
B = 'https://medluxlife-6j8sz55bpn.live-website.com/wp-json/wp/v2'
page, res, apply = sys.argv[1], json.load(open(sys.argv[2])), '--apply' in sys.argv
def curl(*a):
    return json.loads(subprocess.run(['curl', '-sS', '--max-time', '120', *a], capture_output=True, check=True).stdout)
c = json.load(open(f'backup/page{page}.json'))['content']['raw']
n0 = len(c)
for r in res:
    old = curl(f"{B}/media/{r['old']}?_fields=source_url,alt_text")
    stem = old['source_url'].rsplit('/', 1)[1].rsplit('.', 1)[0]
    new_alt = curl(f"{B}/media/{r['new']}?_fields=alt_text")['alt_text']
    cnt = {}
    c, cnt['id'] = re.subn(rf'"id":{r["old"]}(?=\D)', f'"id":{r["new"]}', c)
    c, cnt['cls'] = re.subn(rf'wp-image-{r["old"]}(?=\D)', f'wp-image-{r["new"]}', c)
    c, cnt['src'] = re.subn(rf'https?://[^"\s]*/{re.escape(stem)}(-\d+x\d+)?\.jpg', r['large'], c)
    if old['alt_text'] and old['alt_text'] != new_alt:
        c, cnt['alt'] = re.subn(re.escape(f'alt="{old["alt_text"]}"'), f'alt="{new_alt}"', c)
    print(r['old'], '->', r['new'], cnt)
print('len', n0, '->', len(c))
if apply:
    out = curl('-X', 'POST', f'{B}/pages/{page}', '-H', 'Content-Type: application/json', '--data', json.dumps({'content': c}))
    print('updated', out.get('id'), out.get('modified'))
