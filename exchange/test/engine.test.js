'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const { openDb } = require('../src/db');
const { Engine } = require('../src/engine');
const cfg = require('../src/config');

function setup() {
  const db = openDb(':memory:');
  const e = new Engine(db, { ...cfg, bots: false });
  e.setFeeAccount(999);
  for (const uid of [1, 2, 3]) e.deposit(uid, { USDT: '100000', BTC: '2', ETH: '10' }, 'test');
  return { db, e };
}
const bal = (e, uid, a) => e.balances(uid)[a];

test('limit buy locks funds and cancel unlocks', () => {
  const { e } = setup();
  const r = e.placeOrder(1, { symbol: 'BTCUSDT', side: 'BUY', type: 'LIMIT', price: '50000', qty: '0.5' });
  assert.equal(r.order.status, 'NEW');
  assert.deepEqual(bal(e, 1, 'USDT'), { free: '75000', locked: '25000' });
  e.cancelOrder(1, r.order.id);
  assert.deepEqual(bal(e, 1, 'USDT'), { free: '100000', locked: '0' });
  assert.ok(e.audit().ok, JSON.stringify(e.audit()));
});

test('matching at maker price, fees, price improvement refund', () => {
  const { e } = setup();
  e.placeOrder(2, { symbol: 'BTCUSDT', side: 'SELL', type: 'LIMIT', price: '60000', qty: '1' });
  const r = e.placeOrder(1, { symbol: 'BTCUSDT', side: 'BUY', type: 'LIMIT', price: '61000', qty: '0.4' });
  assert.equal(r.order.status, 'FILLED');
  assert.equal(r.fills[0].price, '60000');
  // покупець: заплатив 24000, отримав 0.4 - 0.1% = 0.3996 BTC
  assert.deepEqual(bal(e, 1, 'USDT'), { free: '76000', locked: '0' });
  assert.deepEqual(bal(e, 1, 'BTC'), { free: '2.3996', locked: '0' });
  // продавець: 0.6 BTC ще заблоковано, отримав 24000 - 24 комісія
  assert.deepEqual(bal(e, 2, 'BTC'), { free: '1', locked: '0.6' });
  assert.deepEqual(bal(e, 2, 'USDT'), { free: '123976', locked: '0' });
  assert.deepEqual(bal(e, 999, 'BTC'), { free: '0.0004', locked: '0' });
  assert.deepEqual(bal(e, 999, 'USDT'), { free: '24', locked: '0' });
  assert.ok(e.audit().ok, JSON.stringify(e.audit()));
});

test('price-time priority and partial fills across levels', () => {
  const { e } = setup();
  const a = e.placeOrder(2, { symbol: 'BTCUSDT', side: 'SELL', type: 'LIMIT', price: '60010', qty: '0.1' }).order;
  const b = e.placeOrder(3, { symbol: 'BTCUSDT', side: 'SELL', type: 'LIMIT', price: '60000', qty: '0.1' }).order;
  const c = e.placeOrder(2, { symbol: 'BTCUSDT', side: 'SELL', type: 'LIMIT', price: '60000', qty: '0.1' }).order;
  const r = e.placeOrder(1, { symbol: 'BTCUSDT', side: 'BUY', type: 'MARKET', qty: '0.25' });
  assert.deepEqual(r.fills.map((f) => [f.price, f.qty]), [['60000', '0.1'], ['60000', '0.1'], ['60010', '0.05']]);
  assert.equal(r.order.status, 'FILLED');
  const open = Object.fromEntries(e.openOrders(2).map((o) => [o.id, o]));
  assert.equal(open[a.id].status, 'PARTIALLY_FILLED');
  assert.equal(open[c.id], undefined);
  assert.equal(e.openOrders(3).length, 0, String(b.id));
  assert.ok(e.audit().ok, JSON.stringify(e.audit()));
});

test('market buy by quoteQty, IOC, FOK, post-only, self-trade prevention', () => {
  const { e } = setup();
  e.placeOrder(2, { symbol: 'BTCUSDT', side: 'SELL', type: 'LIMIT', price: '60000', qty: '0.1' });
  const m = e.placeOrder(1, { symbol: 'BTCUSDT', side: 'BUY', type: 'MARKET', quoteQty: '3000' });
  assert.equal(m.order.filled, '0.05');
  assert.equal(m.order.status, 'FILLED');

  const fok = e.placeOrder(1, { symbol: 'BTCUSDT', side: 'BUY', type: 'LIMIT', tif: 'FOK', price: '60000', qty: '1' });
  assert.equal(fok.order.status, 'EXPIRED');
  assert.equal(fok.fills.length, 0);

  const ioc = e.placeOrder(1, { symbol: 'BTCUSDT', side: 'BUY', type: 'LIMIT', tif: 'IOC', price: '60000', qty: '1' });
  assert.equal(ioc.order.status, 'EXPIRED');
  assert.equal(ioc.order.filled, '0.05');
  assert.equal(bal(e, 1, 'USDT').locked, '0');

  e.placeOrder(2, { symbol: 'BTCUSDT', side: 'SELL', type: 'LIMIT', price: '60000', qty: '0.1' });
  assert.throws(() => e.placeOrder(1, { symbol: 'BTCUSDT', side: 'BUY', type: 'LIMIT_MAKER', price: '60000', qty: '0.1' }));
  assert.equal(e.placeOrder(1, { symbol: 'BTCUSDT', side: 'BUY', type: 'LIMIT_MAKER', price: '59990', qty: '0.1' }).order.status, 'NEW');
  e.cancelAll(1);
  e.cancelAll(2);
  e.placeOrder(3, { symbol: 'BTCUSDT', side: 'BUY', type: 'LIMIT', price: '59000', qty: '0.1' });
  e.placeOrder(3, { symbol: 'BTCUSDT', side: 'BUY', type: 'LIMIT', price: '58000', qty: '0.1' });
  const self = e.placeOrder(3, { symbol: 'BTCUSDT', side: 'SELL', type: 'LIMIT', price: '58000', qty: '0.1' });
  assert.equal(self.fills.length, 0); // власні ордери не торгуються між собою
  assert.equal(e.depth('BTCUSDT').bids.length, 0);
  assert.ok(e.audit().ok, JSON.stringify(e.audit()));
});

test('validation and insufficient funds', () => {
  const { e } = setup();
  const t = (req) => assert.throws(() => e.placeOrder(1, { symbol: 'BTCUSDT', ...req }));
  t({ side: 'BUY', type: 'LIMIT', price: '60000.001', qty: '0.1' });
  t({ side: 'BUY', type: 'LIMIT', price: '60000', qty: '0.000001' });
  t({ side: 'BUY', type: 'LIMIT', price: '60000', qty: '5' });
  t({ side: 'SELL', type: 'LIMIT', price: '60000', qty: '3' });
  t({ side: 'BUY', type: 'LIMIT', price: '1', qty: '1' }); // min notional
  t({ side: 'BUY', type: 'LIMIT', price: '-1', qty: '1' });
  t({ side: 'BUY', type: 'LIMIT', price: '1e5', qty: '1' });
  assert.throws(() => e.cancelOrder(2, 12345));
});

test('PnL: average cost, realized and unrealized', () => {
  const { e } = setup();
  // Користувач 1 вже має 2 BTC з собівартістю 60000 (ціна при депозиті)
  e.placeOrder(2, { symbol: 'BTCUSDT', side: 'BUY', type: 'LIMIT', price: '66000', qty: '1' });
  e.placeOrder(1, { symbol: 'BTCUSDT', side: 'SELL', type: 'MARKET', qty: '1' });
  const p = e.pnl(1).positions.find((x) => x.asset === 'BTC');
  // продали 1 BTC за 66000 - 66 комісія, собівартість 60000 => +5934
  assert.equal(p.realized, '5934');
  assert.equal(p.qty, '1');
  assert.equal(p.avgPrice, '60000');
  assert.equal(p.unrealized, '6000'); // остання ціна 66000
});

test('state survives restart', () => {
  const { db, e } = setup();
  const o = e.placeOrder(1, { symbol: 'ETHUSDT', side: 'BUY', type: 'LIMIT', price: '2900', qty: '1.5' }).order;
  const e2 = new Engine(db, { ...cfg, bots: false });
  e2.setFeeAccount(999);
  assert.equal(e2.openOrders(1)[0].id, o.id);
  assert.deepEqual(e2.balances(1).USDT, { free: '95650', locked: '4350' });
  const r = e2.placeOrder(2, { symbol: 'ETHUSDT', side: 'SELL', type: 'MARKET', qty: '1.5' });
  assert.equal(r.order.status, 'FILLED');
  assert.ok(e2.audit().ok, JSON.stringify(e2.audit()));
});

test('random fuzz keeps invariants', () => {
  const { e } = setup();
  let rnd = 42;
  const R = () => ((rnd = (rnd * 1103515245 + 12345) % 2147483648) / 2147483648);
  for (let i = 0; i < 5000; i++) {
    const uid = 1 + Math.floor(R() * 3);
    try {
      if (R() < 0.15) {
        const open = e.openOrders(uid);
        if (open.length) e.cancelOrder(uid, open[Math.floor(R() * open.length)].id);
        continue;
      }
      const side = R() < 0.5 ? 'BUY' : 'SELL';
      const kind = R();
      const px = (60000 + Math.floor((R() - 0.5) * 2000)).toString();
      const qty = (Math.floor(R() * 5000) / 100000 + 0.0001).toFixed(5);
      if (kind < 0.2) e.placeOrder(uid, { symbol: 'BTCUSDT', side, type: 'MARKET', qty });
      else if (kind < 0.25 && side === 'BUY') e.placeOrder(uid, { symbol: 'BTCUSDT', side, type: 'MARKET', quoteQty: '500' });
      else e.placeOrder(uid, { symbol: 'BTCUSDT', side, type: 'LIMIT', tif: kind > 0.9 ? 'IOC' : 'GTC', price: px, qty });
    } catch (err) {
      if (!err.code) throw err;
    }
  }
  const a = e.audit();
  assert.ok(a.ok, JSON.stringify(a));
});
