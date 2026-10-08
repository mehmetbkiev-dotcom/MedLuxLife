# usage: upload.py PICKS.json  — PICKS: [{"old":294,"sheet":"us/294.json","n":5,"stem":"...","alt":"..."}]
# downloads from Unsplash (1600px), triggers download_location, uploads to WP Media; writes result map to PICKS.out.json
import sys, json, subprocess, os
B = 'https://medluxlife-6j8sz55bpn.live-website.com/wp-json/wp/v2'
picks = json.load(open(sys.argv[1]))
def run(*a):
    return subprocess.run(['curl', '-sS', '--max-time', '120', *a], capture_output=True, check=True).stdout
out = []
for p in picks:
    it = json.load(open(p['sheet']))[p['n'] - 1]
    f = f"us/{p['stem']}.jpg"
    open(f, 'wb').write(run(it['raw'] + '&w=1600&q=80&fm=jpg'))
    run(it['dl'])  # Unsplash API guideline: count the download
    m = json.loads(run('-X', 'POST', f'{B}/media', '-H', 'Content-Type: image/jpeg',
                       '-H', f"Content-Disposition: attachment; filename={p['stem']}.jpg", '--data-binary', '@' + f))
    caption = f"Photo: {it['user']} / Unsplash ({it['html']})"
    m = json.loads(run('-X', 'POST', f"{B}/media/{m['id']}", '-H', 'Content-Type: application/json',
                       '--data', json.dumps({'alt_text': p['alt'], 'caption': caption, 'title': p['stem']})))
    sizes = m['media_details'].get('sizes', {})
    out.append({'old': p['old'], 'new': m['id'], 'full': m['source_url'],
                'large': sizes.get('large', {}).get('source_url', m['source_url']),
                'w': m['media_details']['width'], 'h': m['media_details']['height'], 'user': it['user']})
    print(out[-1])
json.dump(out, open(sys.argv[1].replace('.json', '.out.json'), 'w'), indent=1)
