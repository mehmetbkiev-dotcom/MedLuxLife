export const meta = {
  name: 'medlux-banner-icons-travel-about-contact',
  description: 'Design gold line icons for the Travel, Travel sub-pages, About Us and Contact title banners: two concepts per page, judge picks and polishes, final set consistency check',
  phases: [
    { title: 'Design', detail: 'two designers per page, different concepts' },
    { title: 'Judge', detail: 'pick the better concept per page and list fixes' },
    { title: 'Polish', detail: 'apply fixes, write final SVG + PNG' },
    { title: 'Consistency', detail: 'whole-set review and fixes' },
  ],
}

const D = '/tmp/claude-0/-home-user-MedLuxLife/58e49045-1f3b-5625-b667-4a635b0b1d5b/icons2'
const PAGES = [
  { slug: 'travel', title: 'Travel', topic: 'overview of all travel services: holiday packages, hotels, flights, airport transfers, Hajj and Umrah trips', a: 'a globe with a small airplane flying along a curved orbit/route around it', b: 'a location pin standing on a simple globe or map horizon, with a dotted travel route' },
  { slug: 'holiday-packages', title: 'Holiday Packages', topic: 'all-inclusive holiday packages: seaside, city breaks, wellness, family trips', a: 'a travel suitcase with a small sun rising behind it', b: 'a palm tree with a sun and two simple wave lines' },
  { slug: 'hotel-reservation', title: 'Hotel Reservation', topic: 'booking city hotels, resorts and boutique hotels', a: 'a hotel bed seen from the side: headboard, pillow, mattress and legs', b: 'a classic concierge/reception bell on a small base' },
  { slug: 'airport-transfer', title: 'Airport Transfer', topic: 'private car transfers between airport, hotel and clinic', a: 'a car seen from the side with two short speed lines', b: 'a car front view with a small airplane flying above it' },
  { slug: 'hajj-umrah', title: 'Hajj & Umrah', topic: 'organised pilgrimage trips (visa, flights, hotels near the holy mosques, transfers)', a: 'a mosque silhouette: central dome with a small crescent finial and two slim minarets', b: 'an ornate pointed arch gateway (Islamic architecture) with a small crescent above it' },
  { slug: 'flight-tickets', title: 'Flight Tickets', topic: 'booking international and domestic flights', a: 'a boarding pass / ticket shape with a perforated tear line and a small airplane symbol on it (no text)', b: 'an airplane taking off diagonally with a dotted route line behind it' },
  { slug: 'about-us', title: 'About Us', topic: 'MedLuxLife, a German medical-travel agency in Aachen that personally guides international patients and travellers', a: 'two open hands gently holding a heart (care and trust)', b: 'a compass with a heart at its centre (guidance and care)' },
  { slug: 'contact', title: 'Contact', topic: 'contact page with form, e-mail, phone, WhatsApp and live chat', a: 'an envelope with a small speech bubble overlapping its corner', b: 'a phone handset with a small chat speech bubble' },
]

const STYLE = `
You are designing ONE gold line icon for the right side of a slim dark title banner (background #16141f, gold title text) on the website of MedLuxLife, a premium German medical-travel agency. It must belong to an existing set of ~80 icons.

EXACT SVG FORMAT (copy this wrapper verbatim; put only your shapes inside the <g>):
<svg xmlns="http://www.w3.org/2000/svg" viewBox="400 170 400 350" aria-hidden="true"><defs><linearGradient id="g" gradientUnits="userSpaceOnUse" x1="400" y1="170" x2="800" y2="520"><stop offset="0" stop-color="#f6d891"/><stop offset="1" stop-color="#d6a043"/></linearGradient></defs><g fill="none" stroke="url(#g)" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"> ... </g></svg>

STYLE RULES:
- Outline (line-art) only, single gold gradient stroke; stroke-width 9 for main lines, 6-7 allowed for small inner details; no fills except tiny dots (fill="url(#g)" stroke="none", r <= 12).
- Centre the drawing around (600,345); keep everything inside x 440-760, y 190-500 with breathing room.
- Must read clearly at 72x63 px and still be recognisable at 40x35 px: few, bold, simple shapes, no tiny details, no text, letters, numbers or flags; no human faces.
- Elegant, calm, premium; smooth curves (use cubic/arc paths), symmetric where natural.
- Match the existing set: look at examples by running the preview on copies of /home/user/MedLuxLife/assets/dept_icons/dept/urology.svg, /home/user/MedLuxLife/assets/dept_icons/dept/cardiology.svg and /home/user/MedLuxLife/assets/dept_icons/line/dental-and-oral-health.svg (copy them into your own folder first).

TOOLS: write your SVG file, then run
  cd ${D} && NODE_PATH=/opt/node22/lib/node_modules node preview.mjs <your.svg> "<Page Title>"
It writes <your>.preview.png (big icon, 72px and 40px sizes and a banner mock-up) and <your>.png. Read the preview image, critique it honestly (proportions, line weight, recognisability at small size, alignment, balance) and iterate at least twice until it looks professionally drawn.
`

const DESIGN = { type: 'object', properties: {
  file: { type: 'string', description: 'absolute path of the final SVG' },
  concept: { type: 'string' },
  self_review: { type: 'string', description: 'honest assessment, weaknesses included' },
}, required: ['file', 'concept', 'self_review'] }
const VERDICT = { type: 'object', properties: {
  winner: { type: 'string', enum: ['a', 'b'] },
  reason: { type: 'string' },
  fixes: { type: 'array', items: { type: 'string' }, description: 'concrete changes to make the winner production-ready (may be empty)' },
}, required: ['winner', 'reason', 'fixes'] }
const FINAL = { type: 'object', properties: {
  svg: { type: 'string', description: 'absolute path of final SVG in final/ folder' },
  png: { type: 'string' },
  summary: { type: 'string' },
}, required: ['svg', 'png', 'summary'] }
const SET = { type: 'object', properties: {
  issues: { type: 'array', items: { type: 'object', properties: { slug: { type: 'string' }, problem: { type: 'string' }, fix: { type: 'string' } }, required: ['slug', 'problem', 'fix'] } },
  summary: { type: 'string' },
}, required: ['issues', 'summary'] }

function designStage(pg) {
  return parallel(['a', 'b'].map(v => () => agent(
    `${STYLE}\nPAGE: "${pg.title}" — ${pg.topic}.\nYOUR CONCEPT: ${pg[v]}.\nWork in folder ${D}/${pg.slug}/ (create it). Name your file ${D}/${pg.slug}/${v}.svg. If the concept turns out weak, you may adapt it, but keep it clearly related to the page topic.${pg.slug === 'hajj-umrah' ? ' Be respectful: do NOT depict the Kaaba, people praying or Arabic calligraphy; architecture only.' : ''}\nReturn the file path, concept and an honest self-review.`,
    { label: `design:${pg.slug}-${v}`, phase: 'Design', schema: DESIGN })))
}

async function judgeStage(designs, pg) {
  const ok = designs.filter(Boolean)
  if (!ok.length) return null
  const v = await agent(
    `${STYLE}\nYou are the art director. Page: "${pg.title}" (${pg.topic}). Two candidate icons:\n` +
    ok.map(d => `- ${d.file.endsWith('/a.svg') ? 'a' : 'b'}: ${d.file} (preview: ${d.file.replace(/\.svg$/, '.preview.png')}) — concept: ${d.concept}. Designer self-review: ${d.self_review}`).join('\n') +
    `\nRead both preview images (re-run preview if a PNG is missing). Pick the one that best (1) says "${pg.title}" instantly to a layperson, (2) reads at 72px and 40px, (3) looks elegant and consistent with the existing medical icon set. List concrete fixes for the winner.`,
    { label: `judge:${pg.slug}`, phase: 'Judge', schema: VERDICT })
  return { designs: ok, verdict: v }
}

async function polishStage(j, pg) {
  if (!j || !j.verdict) return null
  const src = `${D}/${pg.slug}/${j.verdict.winner}.svg`
  const fixes = j.verdict.fixes.map(f => '- ' + f).join('\n') || '- none; just verify and clean up'
  const r = await agent(
    `${STYLE}\nPolish the chosen icon for page "${pg.title}". Source: ${src}. Art director's reason: ${j.verdict.reason}\nFixes to apply:\n${fixes}\nWrite the result to ${D}/final/${pg.slug}.svg (create the folder), keep the exact wrapper format, run the preview with title "${pg.title}", read it, iterate until clean. The preview also writes ${D}/final/${pg.slug}.png. Return paths and a short summary.`,
    { label: `polish:${pg.slug}`, phase: 'Polish', schema: FINAL })
  return r ? { ...r, slug: pg.slug, winner: j.verdict.winner, reason: j.verdict.reason } : null
}

const results = await pipeline(PAGES, designStage, judgeStage, polishStage)

phase('Consistency')
const finals = results.filter(Boolean)
const set = await agent(
  `${STYLE}\nThe final icons are in ${D}/final/ (${finals.map(f => f.slug + '.svg').join(', ')}). Build a contact sheet with Python/PIL: composite each ${D}/final/<slug>.png at 160x140 and at 72x63 on #16141f, labelled, into ${D}/final/_sheet.png, and also look at the existing set by previewing copies of /home/user/MedLuxLife/assets/dept_icons/dept/urology.svg and cardiology.svg. Read the sheet. Check the 8 icons as ONE family: equal visual weight and size, consistent stroke widths, similar level of detail, nothing off-style, crowded or unclear at 40px. Report only real issues with concrete fixes.`,
  { label: 'set-review', phase: 'Consistency', schema: SET })

let fixed = []
if (set && set.issues.length) {
  const bySlug = {}
  set.issues.forEach(i => { (bySlug[i.slug] = bySlug[i.slug] || []).push(`${i.problem} -> ${i.fix}`) })
  const titles = {}
  PAGES.forEach(p => { titles[p.slug] = p.title })
  fixed = await parallel(Object.keys(bySlug).map(slug => () => agent(
    `${STYLE}\nFix the final icon ${D}/final/${slug}.svg for set consistency:\n${bySlug[slug].map(x => '- ' + x).join('\n')}\nOverwrite the same file, re-run the preview with title "${titles[slug] || slug}", read it, iterate until clean.`,
    { label: `fix:${slug}`, phase: 'Consistency', schema: FINAL })))
}
return { finals, set_review: set, fixed: fixed.filter(Boolean) }
