import { createRequire } from 'module';
import { execFileSync } from 'child_process';
import fs from 'fs';
const require = createRequire('/opt/node22/lib/node_modules/');
const { chromium } = require('playwright');
const pages = JSON.parse(fs.readFileSync('pages.json', 'utf8'));
const W = +(process.argv[2] || 1440), OUT = process.argv[3] || 'audit.json';
const extra = process.env.CSS ? fs.readFileSync(process.env.CSS, 'utf8') : '';
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const ctx = await b.newContext({ viewport: { width: W, height: 900 } });
await ctx.route('**/*', async (route) => {
  let u = route.request().url();
  if (u.startsWith('https://medluxlife.de')) u = 'https://medluxlife-6j8sz55bpn.live-website.com' + u.slice('https://medluxlife.de'.length);
  if (!u.startsWith('https://medluxlife-6j8sz55bpn.live-website.com')) return route.abort();
  const t = route.request().resourceType(); if (t === 'image' || t === 'media' || t === 'font') { if (!u.includes('.woff')) return route.abort(); }
  try { const raw = execFileSync('curl', ['-sS', '-L', '-i', '--max-time', '30', u], { maxBuffer: 64 << 20 });
    const sep = raw.indexOf('\r\n\r\n', raw.lastIndexOf(Buffer.from('HTTP/'))); const head = raw.slice(0, sep).toString(); const body = raw.slice(sep + 4);
    const status = +head.split('\r\n').filter(l => l.startsWith('HTTP/')).pop().split(' ')[1]; const ct = (head.match(/content-type:\s*([^\r\n]+)/i) || [])[1] || '';
    await route.fulfill({ status, body, headers: ct ? { 'content-type': ct } : {} }); } catch (e) { await route.abort(); } });
const results = [];
let idx = 0;
async function worker() {
  const p = await ctx.newPage();
  while (idx < pages.length) {
    const pg = pages[idx++];
    try {
      await p.goto('https://medluxlife-6j8sz55bpn.live-website.com' + (pg.path === '/' ? '/index.php' : pg.path), { waitUntil: 'domcontentloaded', timeout: 90000 });
      await p.waitForTimeout(800);
      if (extra) await p.addStyleTag({ content: extra });
      const r = await p.evaluate(() => {
        const out = [];
        const root = document.querySelector('main') || document.body;
        for (const e of root.querySelectorAll('p, li')) {
          if (e.closest('header, footer, #mlx-assistant, .wp-block-buttons, figcaption, nav')) continue;
          const r = e.getBoundingClientRect(); if (!r.height || !r.width) continue;
          const cs = getComputedStyle(e); const lh = parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.5;
          const lines = Math.round(r.height / lh);
          if (lines < 2) continue;
          if (e.querySelector('p, li, ul')) continue;
          let a = e.parentElement, sig = [];
          while (a && a !== root && sig.length < 3) { const c = [...a.classList].filter(x => /^(medlux|ext-|wp-block-(accordion|cover|column|media-text|group|details|quote|list))/.test(x) && !/is-layout|wp-container|wp-block-group-is/.test(x)); if (c.length) sig.push(c.slice(0, 2).join('.')); a = a.parentElement; }
          out.push({ align: cs.textAlign, last: cs.textAlignLast, lines, cls: [...e.classList].filter(x => !/wp-block-paragraph/.test(x)).join('.'), sig: sig.join(' < '), text: e.textContent.trim().slice(0, 60) });
        }
        return out;
      });
      results.push({ id: pg.id, path: pg.path, template: pg.template, items: r });
    } catch (e) { results.push({ id: pg.id, path: pg.path, error: String(e).slice(0, 100) }); }
  }
  await p.close();
}
await Promise.all(Array.from({ length: 6 }, worker));
fs.writeFileSync(OUT, JSON.stringify(results));
await b.close();
console.log('done', results.length, 'errors', results.filter(r => r.error).length);
