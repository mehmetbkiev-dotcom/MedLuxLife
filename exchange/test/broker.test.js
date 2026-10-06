'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const cfg = require('../src/config');
const { createServer } = require('../src/server');
const { startMockBinance } = require('./mock-binance');

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function until(fn, ms = 5000) {
  const t0 = Date.now();
  while (Date.now() - t0 < ms) {
    if (await fn()) return true;
    await sleep(50);
  }
  return false;
}

async function boot(dbFile, mockUrl) {
  const srv = createServer({
    ...cfg, dbFile, bots: false,
    broker: { ...cfg.broker, name: 'binance', apiKey: 'k', apiSecret: 's', tradeUrl: mockUrl, priceUrl: mockUrl, allowLive: true, hedgeIntervalMs: 100 },
  });
  await new Promise((r) => srv.listen(0, '127.0.0.1', r));
  srv.url = `http://127.0.0.1:${srv.address().port}`;
  await until(() => srv.hedger.ready);
  return srv;
}

async function register(srv, name) {
  const r = await fetch(srv.url + '/api/register', {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username: name, password: 'secret123' }),
  });
  return (await r.json()).id;
}

let srv, mock;
test.after(() => {
  srv?.shutdown();
  mock?.server.close();
});

test('угоди користувачів дублюються у брокера, з неттінгом, без дублів після обриву і рестарту', async () => {
  mock = await startMockBinance();
  const dbFile = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'mx-')), 'x.db');
  srv = await boot(dbFile, mock.url);
  const e = srv.engine;
  const bot = srv.auth.ensureSystemUser('house', 'bot').id;
  e.deposit(bot, { USDT: '10000000', BTC: '100' }, 'test');
  const a = await register(srv, 'alice');
  const b = await register(srv, 'bob');

  e.placeOrder(bot, { symbol: 'BTCUSDT', side: 'SELL', type: 'LIMIT', price: '100001', qty: '1' });
  e.placeOrder(bot, { symbol: 'BTCUSDT', side: 'BUY', type: 'LIMIT', price: '99999', qty: '1' });

  // 1. Користувач купує в бота → біржа купує стільки ж у брокера
  e.placeOrder(a, { symbol: 'BTCUSDT', side: 'BUY', type: 'MARKET', qty: '0.03' });
  assert.ok(await until(() => mock.state.orders.length === 1));
  assert.equal(mock.state.orders[0].side, 'BUY');
  assert.equal(mock.state.orders[0].executedQty, '0.03000000');

  // 2. Дрібна угода нижче мінімуму брокера накопичується, а не губиться
  e.placeOrder(a, { symbol: 'BTCUSDT', side: 'SELL', type: 'MARKET', qty: '0.00005' });
  await sleep(400);
  assert.equal(mock.state.orders.length, 1);
  assert.equal(srv.hedger.status().markets.BTCUSDT.pendingToHedge, '-0.00005');

  // 3. Користувач ↔ користувач: позиція клієнтів не змінюється, хеджувати нічого
  e.placeOrder(b, { symbol: 'BTCUSDT', side: 'BUY', type: 'LIMIT', price: '99999.5', qty: '0.01' });
  e.placeOrder(a, { symbol: 'BTCUSDT', side: 'SELL', type: 'LIMIT', price: '99999.5', qty: '0.01' });
  await sleep(400);
  assert.equal(mock.state.orders.length, 1);

  // 4. Обрив зв'язку після прийому ордера: знаходимо його за clientOrderId, не дублюємо
  mock.state.dropNext = true;
  e.placeOrder(b, { symbol: 'BTCUSDT', side: 'BUY', type: 'MARKET', qty: '0.02' });
  assert.ok(await until(() => srv.hedger.status().recentOrders[0]?.status === 'FILLED' && mock.state.orders.length === 2));
  await sleep(400);
  assert.equal(mock.state.orders.length, 2);
  // накопичений залишок -0.00005 згорнувся з цією купівлею: 0.02 - 0.00005
  assert.equal(mock.state.orders[1].executedQty, '0.01995000');
  assert.equal(srv.hedger.status().markets.BTCUSDT.pendingToHedge, '0');

  // 5. Відмова брокера (напр. брак коштів) — кількість повертається в чергу і відправляється пізніше
  mock.state.rejectNext = 'Account has insufficient balance';
  e.placeOrder(a, { symbol: 'BTCUSDT', side: 'SELL', type: 'MARKET', qty: '0.01' });
  assert.ok(await until(() => srv.hedger.status().recentOrders[0]?.status === 'REJECTED'));
  assert.equal(srv.hedger.status().markets.BTCUSDT.pendingToHedge, '-0.01');
  srv.hedger.backoffUntil.clear();
  assert.ok(await until(() => mock.state.orders.length === 3));
  assert.equal(mock.state.orders[2].side, 'SELL');
  assert.equal(mock.state.orders[2].executedQty, '0.01000000');

  // 6. Рестарт: стан відновлюється з БД, нічого не відправляється повторно
  srv.shutdown();
  srv = await boot(dbFile, mock.url);
  await sleep(500);
  assert.equal(mock.state.orders.length, 3);
  assert.equal(srv.hedger.status().markets.BTCUSDT.pendingToHedge, '0');
  assert.ok(srv.engine.audit().ok);

  // Маркетмейкер бачить реальну ціну брокера
  assert.equal(srv.hedger.mid('BTCUSDT'), 100000.5);
});
