// usage: node preview.mjs file.svg [title]  -> writes file.preview.png (big icon on banner colour + small banner mock) and file.png (transparent 400x350)
import { createRequire } from 'module'; import fs from 'fs';
const require = createRequire('/opt/node22/lib/node_modules/'); const { chromium } = require('playwright');
const f = process.argv[2]; const title = process.argv[3] || 'Page Title';
const svg = fs.readFileSync(f, 'utf8');
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const p = await b.newPage({ viewport: { width: 900, height: 520 } });
await p.setContent(`<html><body style="margin:0;background:#16141f;font-family:Georgia,serif">
<div style="display:flex;gap:30px;padding:20px;align-items:center">
 <div style="width:400px;height:350px;outline:1px dashed #333">${svg.replace('<svg ', '<svg style="width:400px;height:350px;display:block" ')}</div>
 <div style="width:72px;height:63px">${svg.replace('<svg ', '<svg style="width:72px;height:63px;display:block" ')}</div>
 <div style="width:40px;height:35px">${svg.replace('<svg ', '<svg style="width:40px;height:35px;display:block" ')}</div>
</div>
<div style="margin:0 20px;height:95px;background:radial-gradient(ellipse at 50% 0%,#2a2540 0%,#16141f 70%);border-top:2px solid #d4a24c;border-bottom:1px solid rgba(212,162,76,.6);position:relative;display:flex;align-items:center;justify-content:center">
 <span style="font-size:44px;color:#f2c46a">${title}</span>
 <div style="position:absolute;right:60px;top:16px;width:72px;height:63px">${svg.replace('<svg ', '<svg style="width:72px;height:63px;display:block" ')}</div>
</div></body></html>`);
await p.screenshot({ path: f.replace(/\.svg$/, '.preview.png') });
await p.setViewportSize({ width: 400, height: 350 });
await p.setContent('<html><body style="margin:0;background:transparent">' + svg.replace('<svg ', '<svg style="width:400px;height:350px;display:block" ') + '</body></html>');
await p.screenshot({ path: f.replace(/\.svg$/, '.png'), omitBackground: true, clip: { x: 0, y: 0, width: 400, height: 350 } });
await b.close();
