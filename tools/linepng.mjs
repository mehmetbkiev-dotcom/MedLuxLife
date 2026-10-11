// usage: node linepng.mjs a.svg b.svg ...  -> transparent 400x350 PNG next to each SVG
import { createRequire } from 'module'; import fs from 'fs';
const require = createRequire('/opt/node22/lib/node_modules/'); const { chromium } = require('playwright');
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const p = await b.newPage({ viewport: { width: 400, height: 350 } });
for (const f of process.argv.slice(2)) { await p.setContent('<html><body style="margin:0;background:transparent">'+fs.readFileSync(f,'utf8').replace('<svg ','<svg style="width:400px;height:350px;display:block" ')+'</body></html>'); await p.screenshot({ path: f.replace('.svg','.png'), omitBackground: true, clip:{x:0,y:0,width:400,height:350} }); }
await b.close();
