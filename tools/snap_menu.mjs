import { createRequire } from 'module';
import { execFileSync } from 'child_process';
const require = createRequire('/opt/node22/lib/node_modules/');
const { chromium } = require('playwright');
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const p = await b.newPage({ viewport: { width: 390, height: 844 } });
await p.route('**/*', async (route) => {
  const u = route.request().url();
  if (!u.startsWith('https://medluxlife-6j8sz55bpn.live-website.com')) return route.abort();
  try { const raw = execFileSync('curl', ['-sS','-L','-i','--max-time','30',u], { maxBuffer: 64<<20 });
    const sep = raw.indexOf('\r\n\r\n', raw.lastIndexOf(Buffer.from('HTTP/'))); const head = raw.slice(0, sep).toString();
    const status = +head.split('\r\n').filter(l=>l.startsWith('HTTP/')).pop().split(' ')[1]; const ct=(head.match(/content-type:\s*([^\r\n]+)/i)||[])[1]||'';
    await route.fulfill({ status, body: raw.slice(sep+4), headers: ct?{'content-type':ct}:{} }); } catch(e) { await route.abort(); }
});
await p.goto('https://medluxlife-6j8sz55bpn.live-website.com/?v=31', { waitUntil: 'load', timeout: 120000 });
await p.waitForTimeout(1500);
await p.click('.wp-block-navigation__responsive-container-open');
await p.waitForTimeout(1200);
await p.screenshot({ path: 'menu_mobile.png' });
await b.close();
