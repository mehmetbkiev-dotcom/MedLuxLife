"""Put the live-search index + script into the footer template part (replaces the existing block)."""
import json, subprocess
W = 'https://medluxlife-6j8sz55bpn.live-website.com/wp-json'
TMP = '/tmp/claude-0/-home-user-MedLuxLife/58e49045-1f3b-5625-b667-4a635b0b1d5b/scratchpad/footer_body.json'
run = lambda *a: subprocess.run(a, capture_output=True).stdout
d = json.loads(run('curl', '-sS', f'{W}/wp/v2/template-parts/extendable//footer?context=edit')); c = d['content']['raw']
json.dump(d, open('/home/user/MedLuxLife/backups/wp/footer_tp_before_search_deploy_' + __import__('time').strftime('%Y%m%d_%H%M%S') + '.json', 'w'))
start = '<!-- wp:html -->\n<!-- MedLuxLife live search suggestions'
i = c.find(start)
idx = open('/home/user/MedLuxLife/content/search_index.json').read().replace('</', '<\\/')
js = open('/home/user/MedLuxLife/assets/search/medlux-search.js').read()
block = start + ' (index: content/search_index.json, script: assets/search/medlux-search.js) -->\n<script type="application/json" id="mlx-search-index">' + idx + '</script>\n<script>\n' + js + '\n</script>\n<!-- /wp:html -->'
c = (c[:i] + block + c[c.find('<!-- /wp:html -->', i) + len('<!-- /wp:html -->'):]) if i >= 0 else c + '\n\n' + block
open(TMP, 'w').write(json.dumps({'content': c}))
r = json.loads(run('curl', '-sS', '-X', 'POST', f'{W}/wp/v2/template-parts/extendable//footer', '-H', 'Content-Type: application/json', '--data-binary', '@' + TMP))
print('footer updated', 'mlx-search-index' in r['content']['raw'])
