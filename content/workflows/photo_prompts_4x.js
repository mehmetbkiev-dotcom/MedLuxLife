export const meta = {
  name: 'medlux-4variant-photo-prompts',
  description: 'Write 4 distinct photo ideas (still life / people / everyday life-concept / process-detail) for each of 122 MedLuxLife Health image slots with balanced casting, critique each variant type across the whole set, revise flagged ones',
  phases: [
    { title: 'Write', detail: 'creative directors, 4 slots each, 4 variants per slot' },
    { title: 'Critique', detail: 'one critic per variant type across all slots + casting stats' },
    { title: 'Revise', detail: 'rewrite flagged variants' },
    { title: 'Recheck', detail: 'second pass on must-fix issues' },
  ],
}

const DIR = '/tmp/claude-0/-home-user-MedLuxLife/58e49045-1f3b-5625-b667-4a635b0b1d5b/div'
const slots = args.slots.map(([code, page, card], i) => ({ code, page, card, i }))

function h(str) { let x = 2166136261; for (let k = 0; k < str.length; k++) { x ^= str.charCodeAt(k); x = Math.imul(x, 16777619) >>> 0 } return x }
// balanced, decorrelated assignment: order slots by a salted hash, then deal the list round-robin
function deal(list, salt) {
  const order = slots.slice().sort((a, b) => h(a.code + salt) - h(b.code + salt))
  const out = {}
  order.forEach((s, k) => { out[s.code] = list[k % list.length] })
  return out
}
const CAST = ['German', 'Northern European / Scandinavian', 'Ukrainian', 'Russian', 'Polish / Czech', 'Turkish', 'Gulf Arab', 'Levantine Arab (Lebanese/Syrian)', 'Persian', 'Italian / Greek / Spanish', 'Balkan', 'Georgian / Armenian', 'Black European', 'North African', 'Dutch / British', 'Kurdish']
const AGES = ['in their 20s', 'in their 30s', 'in their 40s', 'in their 50s', 'in their 60s', 'in their 70s']
const GENDER = ['woman', 'man', 'woman', 'man', 'couple or two people of different ages']
const PAL = ['sage green and white', 'navy and walnut', 'terracotta and sand', 'sky blue and silver', 'charcoal and brass', 'blush and ivory', 'forest green and oak', 'teal and white', 'black-and-white', 'olive and linen', 'burgundy and cream', 'ochre and slate', 'lavender and grey', 'coral and pale grey', 'mint and graphite', 'marigold and white', 'cobalt and sand', 'rust and denim blue']
const LIGHT = ['cool early-morning daylight', 'warm golden hour', 'soft overcast light', 'bright high-key daylight', 'warm evening lamps', 'cinematic low-key side light', 'blue-hour window light', 'dappled light through leaves or blinds', 'hard noon sun with crisp shadows', 'soft window light on a rainy day']
const SHOTS = ['macro detail', 'tight close-up', 'medium shot', 'wide environmental', 'overhead top-down', 'side profile', 'framed through foreground object/doorway/glass', 'low angle', 'candid documentary', 'back or three-quarter-back view', 'negative-space composition']

const castB = deal(CAST, 'castB'), castC = deal(CAST, 'castC#'), ageB = deal(AGES, 'ageB'), ageC = deal(AGES, 'ageC!'), genB = deal(GENDER, 'genB'), genC = deal(GENDER, 'genC?')
const palA = deal(PAL, 'pA'), palB = deal(PAL, 'pB'), palC = deal(PAL, 'pC'), palD = deal(PAL, 'pD')
const litA = deal(LIGHT, 'lA'), litB = deal(LIGHT, 'lB'), litC = deal(LIGHT, 'lC'), litD = deal(LIGHT, 'lD')
const shB = deal(SHOTS, 'sB'), shC = deal(SHOTS, 'sC'), shD = deal(SHOTS, 'sD')

function brief(s) {
  return `- ${s.code} | page: ${s.page} | card: ${s.card}
    A (still life, no people): palette ${palA[s.code]}, light ${litA[s.code]}
    B (people in a care/treatment/consultation context): cast ${genB[s.code]}, ${castB[s.code]}, ${ageB[s.code]} (staff any other look/gender); shot ${shB[s.code]}; palette ${palB[s.code]}; light ${litB[s.code]}
    C (everyday life / travel / concept, outside the clinic): cast ${genC[s.code]}, ${castC[s.code]}, ${ageC[s.code]}; shot ${shC[s.code]}; palette ${palC[s.code]}; light ${litC[s.code]}
    D (process, craft or place: hands, equipment, lab, architecture or a symbolic idea; people only partly visible if at all): shot ${shD[s.code]}; palette ${palD[s.code]}; light ${litD[s.code]}`
}

const BIBLE = `
CONTEXT: MedLuxLife is a German medical-travel agency. Each treatment card / department page on its website needs ONE photo. The owner generates photos with ChatGPT and now asks for FOUR clearly different ideas per card in one prompt, then picks the best: (A) a still life without people, (B) a scene with people, (C) another idea telling the same topic differently, (D) yet another idea. The owner complained that earlier prompts always produced the same patient, same doctor and same scene.

BANNED DEFAULT LOOKS (never reproduce): woman 30-45 with long wavy brown/blonde hair in a beige/cream knit sweater; white-and-gold luxury clinic with marble, orchids, huge windows and potted plants; masked stubbled male doctor or dark-haired female doctor with stethoscope + tablet/clipboard at a desk; a South Asian woman with a long or silver-streaked braid and gold nose stud (overused in a previous draft); recurring "series" of the same character across cards.

VARIANT TYPES:
A = still life / product / object photography, no people at all. Make it about the card topic (instruments, models, natural symbols, materials) - vary surfaces and set-ups (stone, wood, fabric, glass, paper, water, plants, metal, coloured seamless paper, outdoor surfaces).
B = people in a care context (consultation, preparation, treatment moment, aftercare, recovery) - specific, human, NOT the banned desk scene. Use the assigned cast for the main person; staff can be any other gender/age/look, wearing varied scrub colours, caps, glasses.
C = everyday life, travel or a conceptual idea outside the clinic that conveys the benefit or theme of the card (active life, home, city, nature, family, travel to the clinic) without claiming results.
D = process/craft/place: hands at work, equipment, laboratory, architecture of a hospital, an overhead layout, or a symbolic/metaphorical image. People at most partly visible (hands, back, silhouette).
Each of the four must differ from the others in subject, setting, composition, palette and light. Follow the assigned palette/light/shot/cast unless it truly cannot fit the topic or rules - then pick another unusual option and note it.

HARD RULES (German health-advertising law HWG + brand):
- No text, letters, numbers, logos, labels, signage, readable screens or brand names (screens may show only abstract medical images without UI text).
- No before/after, split images, results claims, scales or numbers.
- No blood, wounds, incisions, stitches, needles piercing skin in close-up, surgical sites; operating rooms show team/equipment only.
- No nudity, lingerie, bikinis; body-contouring topics use clothing, silhouettes, fabric, movement, hands, symbolic objects.
- No real/recognisable people, celebrities, real hospitals/brands; no flags or religious symbols.
- Children: clothed, calm or happy, with a parent or friendly staff.
- No cure/success promises. Calm, competent, human.
- AI-feasibility: one clear focal subject, no tiny instruments inside mouths, no mirrors with face reflections, no text-prone props (packaging, documents, monitors with UI).
Respect topic constraints (e.g. gynecomastia/beard = men; breast/obstetrics = women; paediatric = children with parent).
`

const VAR = {
  type: 'object',
  properties: {
    type: { type: 'string', enum: ['A', 'B', 'C', 'D'] },
    title: { type: 'string', description: '3-6 words' },
    scene: { type: 'string', description: '55-90 words, concrete and visual: subject/objects, action/moment, setting, wardrobe/props, composition, lens, light, palette, mood. No rule text.' },
    people: { type: 'string', description: 'main person: gender, age band, appearance (e.g. "man, 50s, Turkish") or "none"' },
    setting: { type: 'string' },
    palette: { type: 'string' },
    light: { type: 'string' },
    shot: { type: 'string' },
  },
  required: ['type', 'title', 'scene', 'people', 'setting', 'palette', 'light', 'shot'],
}
const SLOT = {
  type: 'object',
  properties: {
    code: { type: 'string' },
    variants: { type: 'array', items: VAR, minItems: 4, maxItems: 4 },
    avoid: { type: 'string', description: 'slot-specific extra things the image model must avoid, max 25 words' },
  },
  required: ['code', 'variants', 'avoid'],
}
const GROUP = { type: 'object', properties: { slots: { type: 'array', items: SLOT } }, required: ['slots'] }
const FLAGS = {
  type: 'object',
  properties: {
    flags: { type: 'array', items: { type: 'object', properties: {
      code: { type: 'string' }, type: { type: 'string', enum: ['A', 'B', 'C', 'D'] }, problem: { type: 'string' },
      similar_to: { type: 'array', items: { type: 'string' } }, fix: { type: 'string' }, severity: { type: 'string', enum: ['must-fix', 'should-fix'] },
    }, required: ['code', 'type', 'problem', 'similar_to', 'fix', 'severity'] } },
    summary: { type: 'string' },
  },
  required: ['flags', 'summary'],
}

// ---------- Write ----------
phase('Write')
const groups = []
for (let k = 0; k < slots.length; k += 4) groups.push(slots.slice(k, k + 4))
log(`${slots.length} slots, ${groups.length} writer groups`)
const written = await parallel(groups.map((g, gi) => () => agent(
  `${BIBLE}\n\nRead card texts from ${DIR}/slots.json (code, page, card, card_text). A previous single-scene draft for each slot is in ${DIR}/v1.json (items[].code/scene) - you may reuse a good idea from it for ONE variant if it fits that variant type and the assigned cast, but rewrite it to the new constraints; do not copy its recurring characters.\n\nYOUR SLOTS with assigned diversity briefs:\n${g.map(brief).join('\n')}\n\nReturn 4 variants (A, B, C, D in that order) per slot.`,
  { label: `write:${g.map(s => s.code).join(',')}`, phase: 'Write', schema: GROUP }
)))
const items = {}
written.filter(Boolean).forEach(r => r.slots.forEach(s => { if (s.variants && s.variants.length === 4) items[s.code] = s }))
const miss = slots.filter(s => !items[s.code])
if (miss.length) {
  log(`re-writing ${miss.length} missing slots`)
  const again = await parallel(miss.map(s => () => agent(`${BIBLE}\n\nRead card texts from ${DIR}/slots.json.\n\nSLOT:\n${brief(s)}\n\nReturn 4 variants (A,B,C,D).`, { label: `write:${s.code}`, phase: 'Write', schema: GROUP })))
  again.filter(Boolean).forEach(r => r.slots.forEach(s => { if (s.variants && s.variants.length === 4) items[s.code] = s }))
}

function typeDigest(t) {
  return slots.filter(s => items[s.code]).map(s => {
    const v = items[s.code].variants.find(x => x.type === t) || items[s.code].variants['ABCD'.indexOf(t)]
    return `${s.code}-${t} [${s.page} / ${s.card}] ${v.title} :: ${v.scene} || people: ${v.people} || setting: ${v.setting} || palette: ${v.palette} || light: ${v.light} || shot: ${v.shot}`
  }).join('\n')
}
function castingStats() {
  const c = {}
  slots.forEach(s => (items[s.code] ? items[s.code].variants : []).forEach(v => { if (v.people && !/^none/i.test(v.people)) { const k = v.people.toLowerCase(); c[k] = (c[k] || 0) + 1 } }))
  return Object.entries(c).sort((a, b) => b[1] - a[1]).slice(0, 40).map(([k, n]) => `${n}x ${k}`).join('; ')
}

// ---------- Critique ----------
async function critique(round) {
  const stats = castingStats()
  const res = await parallel(['A', 'B', 'C', 'D'].map(t => () => agent(
    `${BIBLE}\n\nYou review ALL type-${t} variants across the ${slots.length} cards (round ${round}). Card texts: ${DIR}/slots.json. Imagine each image rendered. Flag: (1) SAMENESS - clusters of variants that would look alike across cards (same kind of person/wardrobe/setting/composition/props/palette), recurring characters, overused motifs; keep the best member of each cluster and flag the rest with a concrete different direction; (2) TOPIC FIT - would a layperson connect the image to THIS card? (3) RULE/AI RISKS - any HWG or brand rule violation or text-/anatomy-prone set-up; (4) any drift to the banned default looks. Severity must-fix for rule violations, banned looks, clear duplicates and off-topic images; should-fix for weaker issues.\n\nCasting frequency across all variants (people field): ${stats}\n\nTYPE-${t} VARIANTS:\n${typeDigest(t)}`,
    { label: `critic:${t} r${round}`, phase: round === 1 ? 'Critique' : 'Recheck', schema: FLAGS }
  )))
  return res.filter(Boolean)
}

async function revise(crits, phaseName, onlyMust) {
  const by = {}
  crits.forEach(c => c.flags.forEach(f => {
    if (!items[f.code]) return
    if (onlyMust && f.severity !== 'must-fix') return
    ;(by[f.code] = by[f.code] || []).push(`[${f.type}|${f.severity}] ${f.problem} -> FIX: ${f.fix}${f.similar_to.length ? ' (too similar to ' + f.similar_to.join(', ') + ')' : ''}`)
  }))
  const codes = Object.keys(by)
  log(`${phaseName}: ${codes.length} slots with flagged variants`)
  const res = await parallel(codes.map(code => () => {
    const s = slots.find(x => x.code === code)
    const types = [...new Set(by[code].map(l => l[1]))]
    return agent(`${BIBLE}\n\nCard text for ${code}: see ${DIR}/slots.json.\n\nRevise slot ${code} (${s.page} / ${s.card}). Rewrite ONLY the flagged variant types (${types.join(', ')}); keep the others exactly as they are. New versions must differ clearly from the same-type variants of other cards listed below.\n\nCURRENT:\n${JSON.stringify(items[code])}\n\nFEEDBACK:\n${by[code].join('\n')}\n\nOTHER CARDS, same types (avoid resembling):\n${types.map(t => typeDigest(t)).join('\n').slice(0, 60000)}\n\nReturn the full slot (code, 4 variants A-D in order, avoid).`,
      { label: `revise:${code}`, phase: phaseName, schema: SLOT })
  }))
  res.filter(Boolean).forEach(r => { if (items[r.code] && r.variants && r.variants.length === 4) items[r.code] = r })
  return codes.length
}

phase('Critique')
const c1 = await critique(1)
phase('Revise')
const n1 = await revise(c1, 'Revise', false)
phase('Recheck')
const c2 = await critique(2)
const n2 = await revise(c2, 'Recheck', true)

return {
  slots: slots.map(s => items[s.code]).filter(Boolean),
  stats: { total: slots.length, done: Object.keys(items).length, revised_r1: n1, revised_r2: n2 },
  casting: castingStats(),
  summaries: [...c1, ...c2].map(c => c.summary),
}
