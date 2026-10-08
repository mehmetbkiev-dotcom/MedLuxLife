'use strict';
// Навантажувальний тест: N користувачів одночасно реєструються, відкривають real-time стрім
// і торгують (лімітні / ринкові ордери, скасування, перегляд PnL) протягом заданого часу.
// Наприкінці перевіряються інваріанти: сума всіх балансів = сума депозитів, блокування
// збігаються з відкритими ордерами, книга не перехрещена.
//
//   node loadtest.js [baseUrl] [users] [seconds]
//   node loadtest.js http://localhost:8080 100 30

const BASE = process.argv[2] || 'http://localhost:8080';
const USERS = Number(process.argv[3]) || 100;
const SECONDS = Number(process.argv[4]) || 30;

const lat = [];
const regLat = []; // реєстрація (scrypt) міряється окремо — це разова дія
const errors = new Map();
let requests = 0, orders = 0, fills = 0, sseEvents = 0;

async function call(token, method, path, body) {
  const t0 = performance.now();
  const r = await fetch(BASE + path, {
    method,
    headers: { Authorization: `Bearer ${token}`, ...(body ? { 'Content-Type': 'application/json' } : {}) },
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await r.json().catch(() => ({}));
  (path === '/api/register' ? regLat : lat).push(performance.now() - t0);
  requests++;
  if (!r.ok) {
    const k = `${r.status} ${data.error}`;
    errors.set(k, (errors.get(k) || 0) + 1);
    return null;
  }
  return data;
}

async function openStream(token, symbol, signal) {
  try {
    const r = await fetch(`${BASE}/api/stream?symbol=${symbol}`, { headers: { Authorization: `Bearer ${token}` }, signal });
    const reader = r.body.getReader();
    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      sseEvents += (Buffer.from(value).toString().match(/\nevent: /g) || []).length;
    }
  } catch {}
}

// LT_POLL=1 — як браузер за тунелем без стріму: опитування /api/poll раз на секунду
const POLL = process.env.LT_POLL === '1';
async function pollLoop(token, sym, deadline) {
  let since = 0;
  while (Date.now() < deadline) {
    const d = await call(token, 'GET', `/api/poll?symbol=${sym}&since=${since}`).catch(() => null);
    if (d?.trades?.length) since = d.trades[d.trades.length - 1].id;
    sseEvents += d ? 1 : 0;
    await new Promise((r) => setTimeout(r, 1000));
  }
}

const rnd = (a, b) => a + Math.random() * (b - a);

async function trader(i, deadline, ac) {
  const username = `lt${Date.now().toString(36).slice(-5)}_${i}`;
  const reg = await call('', 'POST', '/api/register', { username, password: 'password123' });
  if (!reg) return;
  const token = reg.token;
  const sym = i % 2 ? 'BTCUSDT' : 'ETHUSDT';
  const step = sym === 'BTCUSDT' ? 5 : 4;
  if (POLL) pollLoop(token, sym, deadline);
  else openStream(token, sym, ac.signal);
  while (Date.now() < deadline) {
    const ticker = (await call(token, 'GET', '/api/ticker'))?.find((t) => t.symbol === sym);
    if (!ticker) continue;
    const last = Number(ticker.last);
    const side = Math.random() < 0.5 ? 'BUY' : 'SELL';
    const x = Math.random();
    const qty = (rnd(20, 300) / last).toFixed(step);
    let res;
    if (x < 0.55) {
      const px = (last * (1 + (side === 'BUY' ? -1 : 1) * rnd(-0.001, 0.004))).toFixed(2);
      res = await call(token, 'POST', '/api/order', { symbol: sym, side, type: 'LIMIT', price: px, qty });
    } else if (x < 0.8) {
      res = await call(token, 'POST', '/api/order', side === 'BUY'
        ? { symbol: sym, side, type: 'MARKET', quoteQty: rnd(10, 200).toFixed(2) }
        : { symbol: sym, side, type: 'MARKET', qty });
    } else if (x < 0.93) {
      const open = await call(token, 'GET', '/api/orders/open');
      if (open?.length) await call(token, 'DELETE', `/api/order?id=${open[Math.floor(Math.random() * open.length)].id}`);
    } else {
      await call(token, 'GET', '/api/pnl');
      await call(token, 'GET', '/api/my-trades?limit=20');
    }
    if (res) {
      orders++;
      fills += res.fills.length;
    }
    await new Promise((r) => setTimeout(r, rnd(50, 400))); // "людська" пауза між діями
  }
}

(async () => {
  console.log(`Навантаження: ${USERS} користувачів × ${SECONDS} с → ${BASE}${POLL ? ' (режим опитування)' : ''}`);
  const ac = new AbortController();
  const deadline = Date.now() + SECONDS * 1000;
  const t0 = Date.now();
  await Promise.all(Array.from({ length: USERS }, (_, i) => trader(i, deadline, ac)));
  const secs = (Date.now() - t0) / 1000;
  ac.abort();
  lat.sort((a, b) => a - b);
  const p = (q) => lat[Math.min(lat.length - 1, Math.floor(lat.length * q))]?.toFixed(1);
  console.log(`\nЗапитів: ${requests} (${(requests / secs).toFixed(0)}/с)  ордерів: ${orders} (${(orders / secs).toFixed(0)}/с)  угод користувачів: ${fills}`);
  console.log(`Латентність торгових запитів, мс: p50=${p(0.5)}  p95=${p(0.95)}  p99=${p(0.99)}  max=${lat[lat.length - 1]?.toFixed(1)}`);
  regLat.sort((a, b) => a - b);
  console.log(`Реєстрація, мс: p50=${regLat[regLat.length >> 1]?.toFixed(0)}  max=${regLat[regLat.length - 1]?.toFixed(0)}`);
  console.log(`SSE-подій отримано: ${sseEvents}`);
  console.log('Відповіді з помилками (очікувані бізнес-відмови, напр. брак коштів):', Object.fromEntries(errors));
  const audit = await (await fetch(BASE + '/api/audit')).json();
  console.log('Аудит:', JSON.stringify(audit));
  const server5xx = [...errors.keys()].filter((k) => k.startsWith('5'));
  process.exit(audit.ok && !server5xx.length ? 0 : 1);
})();
