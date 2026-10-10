import json,subprocess,sys
W='https://medluxlife-6j8sz55bpn.live-website.com/wp-json'
base=json.load(open('backups/wp/gs5_before_banner_trial3.json'))['styles']
css0=base['css']; i=css0.index('/* Banner trial (Dental 260)'); css0=css0[:i].rstrip()+'\n'
P='body.page-id-260 main > .ext-hero-section .wp-block-cover'
common=f'''{P}__image-background {{ display: none !important; }}
{P}__background, {P}::after {{ display: none !important; }}
{P} .wp-block-post-title {{ text-align: center !important; margin-left: auto !important; margin-right: auto !important; }}
{P}::before {{ width: clamp(56px, 5.2vw, 72px) !important; height: clamp(48px, 4.6vw, 64px) !important; filter: none !important; }}
@media (max-width: 600px) {{ {P} {{ padding-top: 14px !important; padding-bottom: 14px !important; }} {P} .wp-block-post-title {{ padding-left: 44px; padding-right: 44px !important; }} {P}::before {{ width: 40px !important; height: 35px !important; top: 50% !important; transform: translateY(-50%) !important; }} }}
'''
dark_title=''
light_title=f'''{P} .wp-block-post-title, {P} .wp-block-post-title a {{ background: none !important; -webkit-text-fill-color: #2c2940 !important; color: #2c2940 !important; filter: none !important; text-shadow: none !important; }}'''
V={
 'v3':  f'{P} {{ min-height:0 !important; padding-top:16px !important; padding-bottom:16px !important; background: linear-gradient(90deg, #2c2940 0%, #3a3550 60%, #464258 100%) !important; border-top:1px solid rgba(212,162,76,.35); border-bottom:1px solid rgba(212,162,76,.55); }}',
 'ivory': f'{P} {{ min-height:0 !important; padding-top:16px !important; padding-bottom:16px !important; background: #faf6ee !important; border-top:3px solid #d4a24c; border-bottom:1px solid rgba(212,162,76,.55); }}\n'+light_title,
 'champagne': f'{P} {{ min-height:0 !important; padding-top:16px !important; padding-bottom:16px !important; background: linear-gradient(90deg, #f1e3c2 0%, #f8efdb 50%, #f1e3c2 100%) !important; border-top:1px solid #c9973f; border-bottom:1px solid #c9973f; }}\n'+light_title,
 'midnight': f'{P} {{ min-height:0 !important; padding-top:16px !important; padding-bottom:16px !important; background: radial-gradient(ellipse at 50% 0%, #2a2540 0%, #16141f 70%) !important; border-top:2px solid #d4a24c; border-bottom:1px solid rgba(212,162,76,.6); }}',
}
v=sys.argv[1]
tag=f'/* Banner trial (Dental 260): variant {v} */\n'
g2={'styles':{**base,'css':css0+'\n'+tag+V[v]+'\n'+common}}
r=json.loads(subprocess.run(['curl','-sS','-X','POST',W+'/wp/v2/global-styles/5','-H','Content-Type: application/json','-d',json.dumps(g2)],capture_output=True).stdout)
print(v,'ok' if f'variant {v}' in r['styles']['css'] else r)
