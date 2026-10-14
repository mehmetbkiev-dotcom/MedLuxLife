"""Turn the home "first screen = banner + language card" layout off/on.
usage: python3 tools/first_screen_toggle.py off|on
off: removes the FIRST-SCREEN CSS block from global styles (banner goes back to its old height, 750px).
on:  adds it again from assets/home_first_screen.css.
The snapping script keeps working either way."""
import json, subprocess, sys
W = 'https://medluxlife-6j8sz55bpn.live-website.com/wp-json'
TMP = '/tmp/claude-0/-home-user-MedLuxLife/58e49045-1f3b-5625-b667-4a635b0b1d5b/scratchpad/gs5_body.json'
run = lambda *a: subprocess.run(a, capture_output=True).stdout
g = json.loads(run('curl', '-sS', f'{W}/wp/v2/global-styles/5?context=edit')); css = g['styles']['css']
A, B = '\n/* >>> FIRST-SCREEN START', '/* <<< FIRST-SCREEN END */\n'
if sys.argv[1] == 'off':
    i = css.find(A)
    if i == -1: sys.exit('already off')
    css = css[:i] + css[css.find(B, i) + len(B):]
else:
    if A in css: sys.exit('already on')
    css += A + ' (banner + language card; remove this block to go back) */\n' + open('/home/user/MedLuxLife/assets/home_first_screen.css').read() + B
g['styles']['css'] = css
open(TMP, 'w').write(json.dumps({'settings': g['settings'], 'styles': g['styles']}))
r = json.loads(run('curl', '-sS', '-X', 'POST', f'{W}/wp/v2/global-styles/5', '-H', 'Content-Type: application/json', '--data-binary', '@' + TMP))
print('first screen is now', 'ON' if A in r['styles']['css'] else 'OFF')
