#!/usr/bin/env python3
"""Upload the prepared doctor portraits (320x400 webp, one crop for both partners) to the media library once;
media ids go into content/partners/doctors.json ("photo_id", "photo_url"). usage: partners_photos.py DIR_WITH_WEBP"""
import json, pathlib, subprocess, sys, concurrent.futures as cf
ROOT = pathlib.Path(__file__).resolve().parent.parent
W = 'https://medluxlife-6j8sz55bpn.live-website.com/wp-json/wp/v2/media'
TITLE = {'prof': 'Prof. Dr.', 'assoc': 'Assoc. Prof. Dr.', 'asst': 'Asst. Prof. Dr.', 'spec': 'Dr.', 'op': 'Op. Dr.', 'dr': 'Dr.', 'drdt': 'Dr. Dt.', 'dt': 'Dt.'}


def up(x, src):
    if x.get('photo_id'):
        return x
    f = pathlib.Path(src) / ('%s-%s.webp' % (x['partner'], x['slug']))
    name = 'medluxlife-doctor-%s-%s.webp' % (x['partner'], x['slug'])
    r = json.loads(subprocess.run(['curl', '-sS', '-X', 'POST', W, '-H', 'Content-Disposition: attachment; filename=' + name, '-H', 'Content-Type: image/webp',
                                   '--data-binary', '@' + str(f)], capture_output=True).stdout)
    alt = (TITLE.get(x['title'], '') + ' ' + x['name']).strip()
    src_site = 'Yeditepe University Hospitals' if x['partner'] == 'yeditepe' else 'Celyxmed'
    subprocess.run(['curl', '-sS', '-o', '/dev/null', '-X', 'POST', '%s/%d' % (W, r['id']), '-H', 'Content-Type: application/json',
                    '-d', json.dumps({'alt_text': alt, 'caption': 'Photo: ' + src_site})])
    x['photo_id'], x['photo_url'] = r['id'], r['source_url']
    return x


if __name__ == '__main__':
    p = ROOT / 'content/partners/doctors.json'
    d = json.load(open(p))
    d = list(cf.ThreadPoolExecutor(4).map(lambda x: up(x, sys.argv[1]), d))
    json.dump(d, open(p, 'w'), ensure_ascii=False, indent=1)
    print(sum(1 for x in d if x.get('photo_id')), 'of', len(d), 'uploaded')
