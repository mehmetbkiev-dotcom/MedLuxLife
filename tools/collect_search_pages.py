"""Collect page titles, parents and section (h3) names for the search index -> content/search_pages_raw.json.
Then: python3 tools/build_search_index.py content/search_pages_raw.json && python3 tools/deploy_search.py"""
import json, subprocess, re, html, concurrent.futures as cf
W='https://medluxlife-6j8sz55bpn.live-website.com'
S='/home/user/MedLuxLife/content'
def get(u): return subprocess.run(['curl','-sS','-L','--max-time','40',u],capture_output=True).stdout.decode('utf8','ignore')
ids=sorted(set(json.load(open('content/health_page_ids.json')))|set(json.load(open('content/banner_page_ids.json'))))
pages={}
for pg in (1,2,3):
    r=json.loads(get(f'{W}/wp-json/wp/v2/pages?per_page=100&_fields=id,title,link,parent,status&page={pg}'))
    if not isinstance(r,list): break
    pages.update({p['id']:p for p in r})
print('pages',len(pages),'ids',len(ids))
def txt(s): return html.unescape(re.sub(r'<[^>]+>','',s)).strip()
def parse(h):
    m=re.search(r'<main.*?</main>',h,re.S); body=m.group(0) if m else h
    h1=re.search(r'<h1[^>]*>(.*?)</h1>',body,re.S)
    h3=[txt(x) for x in re.findall(r'<h3[^>]*>(.*?)</h3>',body,re.S)]
    return (txt(h1.group(1)) if h1 else ''), [x for x in h3 if x and len(x)<80]
def one(pid):
    p=pages[pid]; path=p['link'].replace('https://medluxlife.de','')
    out={'id':pid,'path':path,'parent':p['parent'],'en_title':html.unescape(p['title']['rendered'])}
    for lang,pre in (('en',''),('de','/de'),('tr','/tr')):
        h=get(f'{W}{pre}{path}')
        t,c=parse(h); out[lang]={'h1':t,'cards':c}
    return out
with cf.ThreadPoolExecutor(8) as ex: res=list(ex.map(one,[i for i in ids if i in pages]))
json.dump({'pages':{str(k):{'title':html.unescape(v['title']['rendered']),'parent':v['parent']} for k,v in pages.items()},'items':res},open(f'{S}/search_pages_raw.json','w'),ensure_ascii=False,indent=1)
print(len(res))
for r in res[:6]: print(r['id'],r['path'],'|',r['en']['h1'],'|',r['de']['h1'],'|',r['tr']['h1'],'| cards',len(r['en']['cards']),len(r['de']['cards']))
