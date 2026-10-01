// Screenshot a page: every request is fetched with curl (which trusts the proxy CA) and handed to Chromium.
import { createRequire } from 'module';
import { execFileSync } from 'child_process';
const require = createRequire('/opt/node22/lib/node_modules/');
const { chromium } = require('playwright');
const [url, out, width = '1366', height = '900', scroll = '0', full = '0'] = process.argv.slice(2);
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const p = await b.newPage({ viewport: { width: +width, height: +height } });
await p.route('**/*', async (route) => {
  const u = route.request().url();
  if (!u.startsWith('https://medluxlife-6j8sz55bpn.live-website.com') && !u.includes('fonts.')) return route.abort();
  try {
    const raw = execFileSync('curl', ['-sS', '-L', '-i', '--max-time', '30', u], { maxBuffer: 64 << 20 });
    let i = raw.lastIndexOf('\r\n\r\n', raw.indexOf('\r\n\r\n', raw.lastIndexOf(Buffer.from('HTTP/'))) + 4);
    const sep = raw.indexOf('\r\n\r\n', raw.lastIndexOf(Buffer.from('HTTP/')));
    const head = raw.slice(0, sep).toString(); const body = raw.slice(sep + 4);
    const status = +head.split('\r\n').filter(l => l.startsWith('HTTP/')).pop().split(' ')[1];
    const ct = (head.match(/content-type:\s*([^\r\n]+)/i) || [])[1] || '';
    await route.fulfill({ status, body, headers: ct ? { 'content-type': ct } : {} });
  } catch (e) { await route.abort(); }
});
await p.goto(url, { waitUntil: 'load', timeout: 120000 });
if (process.env.EXTRA_CSS) { await p.addStyleTag({ content: require('fs').readFileSync(process.env.EXTRA_CSS, 'utf8') }); }
await p.waitForTimeout(1500);
if (full === '1') { for (let y = 0; y < 20000; y += 600) { await p.evaluate(v => window.scrollTo(0, v), y); await p.waitForTimeout(150); } await p.evaluate(() => window.scrollTo(0, 0)); await p.waitForTimeout(1500); }
if (+scroll) { await p.mouse.wheel(0, +scroll); await p.waitForTimeout(1200); }
await p.screenshot({ path: out, fullPage: full === '1' });
await b.close();
