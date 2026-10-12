'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const { openDb } = require('../src/db');
const { Engine } = require('../src/engine');
const cfg = require('../src/config');

const FEE = 999; // рахунок комісій / страховий фонд

function setup() {
  const db = openDb(':memory:');
  const e = new Engine(db, { ...cfg, bots: false });
  e.setFeeAccount(FEE);
  for (const uid of [1, 2, 3]) e.deposit(uid, { USDT: '100000' }, 'test');
  return { db, e };
}
const acc = (e, uid) => e.account(uid);
const pos = (e, uid, sym = 'BTCUSDT') => e.positions(uid).find((p) => p.symbol === sym);
const ok = (e) => {
  const a = e.audit();
  assert.ok(a.ok, JSON.stringify(a.issues));
};
const L = (e, uid, side, price, qty, extra = {}) =>
  e.placeOrder(uid, { symbol: 'BTCUSDT', side, type: 'LIMIT', price, qty, ...extra });
const M = (e, uid, side, qty, extra = {}) => e.placeOrder(uid, { symbol: 'BTCUSDT', side, type: 'MARKET', qty, ...extra });

test('лонг з плечем: маржа = вартість / плече, комісія 0.1%', () => {
  const { e } = setup();
  L(e, 2, 'SELL', '80000', '1');
  const r = M(e, 1, 'BUY', '0.5');
  assert.equal(r.order.status, 'FILLED');
  const p = pos(e, 1);
  assert.equal(p.side, 'LONG');
  assert.equal(p.size, '0.5');
  assert.equal(p.entry, '80000');
  assert.equal(p.leverage, 10);
  assert.equal(p.margin, '4000'); // 40000 / 10
  assert.equal(acc(e, 1).available, '95960'); // 100000 - 4000 маржа - 40 комісія
  assert.equal(pos(e, 2).side, 'SHORT');
  ok(e);
});

test('закриття лонга з прибутком і шорта зі збитком', () => {
  const { e } = setup();
  L(e, 2, 'SELL', '80000', '1');
  M(e, 1, 'BUY', '1'); // 1: лонг 1 @ 80000, 2: шорт 1 @ 80000
  L(e, 3, 'BUY', '84000', '1');
  const r = M(e, 1, 'SELL', '1', { reduceOnly: true });
  assert.equal(r.fills[0].realizedPnl, '4000');
  assert.equal(pos(e, 1), undefined);
  // 100000 - 80 - 84 комісії + 4000 прибутку
  assert.equal(acc(e, 1).available, '103836');
  // у шорта нереалізований збиток за ціною маркування (остання угода 84000)
  assert.equal(pos(e, 2).unrealized, '-4000');
  ok(e);
});

test('часткове закриття і переворот позиції', () => {
  const { e } = setup();
  L(e, 2, 'SELL', '80000', '2');
  M(e, 1, 'BUY', '1');
  L(e, 3, 'BUY', '81000', '3');
  M(e, 1, 'SELL', '0.4');
  assert.equal(pos(e, 1).size, '0.6');
  assert.equal(pos(e, 1).margin, '4800'); // 8000 * 0.6
  M(e, 1, 'SELL', '1.6'); // закрити 0.6 і відкрити шорт 1
  const p = pos(e, 1);
  assert.equal(p.side, 'SHORT');
  assert.equal(p.size, '-1');
  assert.equal(p.entry, '81000');
  ok(e);
});

test('reduce-only не відкриває нову позицію; маржі не вистачає — відмова', () => {
  const { e } = setup();
  assert.throws(() => M(e, 1, 'SELL', '0.1', { reduceOnly: true }), /Reduce-only/);
  L(e, 2, 'SELL', '80000', '10'); // продавцю треба 80000 маржі — вистачає
  assert.throws(() => M(e, 1, 'BUY', '20'), /Недостатньо маржі/); // ~1.68M / 10 > 100k
  e.setLeverage(1, 'BTCUSDT', 20);
  assert.equal(M(e, 1, 'BUY', '10').order.status, 'FILLED'); // ~840k / 20 = 42k
  assert.throws(() => e.setLeverage(1, 'BTCUSDT', 5), /Закрийте позицію/);
  // reduce-only більше за позицію обрізається до розміру позиції
  L(e, 3, 'BUY', '80000', '12');
  const r = M(e, 1, 'SELL', '30', { reduceOnly: true });
  assert.equal(r.order.filled, '10');
  assert.equal(pos(e, 1), undefined);
  ok(e);
});

test('лімітний ордер блокує маржу, скасування повертає', () => {
  const { e } = setup();
  const r = L(e, 1, 'BUY', '50000', '1');
  assert.equal(r.order.status, 'NEW');
  assert.equal(acc(e, 1).orderMargin, '5100'); // 5000 маржа + подвійний запас на комісію (2 × 50)
  e.cancelOrder(1, r.order.id);
  assert.equal(acc(e, 1).available, '100000');
  assert.equal(acc(e, 1).orderMargin, '0');
  assert.throws(() => e.setLeverage(1, 'BTCUSDT', 200), /від 1 до 100/);
  ok(e);
});

test('ліквідація: позиція закривається, маржа йде в страховий фонд', () => {
  const { e } = setup();
  e.setLeverage(1, 'BTCUSDT', 50);
  L(e, 2, 'SELL', '80000', '1');
  M(e, 1, 'BUY', '1'); // маржа 1600, ліквідація ~ на 1.5% нижче
  const liq = Number(pos(e, 1).liqPrice);
  assert.ok(liq > 78700 && liq < 78900, String(liq));
  L(e, 3, 'BUY', '78000', '5'); // покупець у книзі
  e.setMark('BTCUSDT', 78500n * 100000000n); // ціна маркування впала
  assert.equal(e.checkLiquidations(), 1);
  assert.equal(pos(e, 1), undefined);
  const hist = e.orderHistory(1);
  assert.equal(hist[0].type, 'LIQUIDATION');
  // користувач втратив маржу 1600 і комісію 80, більше — ні
  assert.equal(acc(e, 1).walletBalance, '98320');
  ok(e);
});

test('ліквідація без покупців: позицію бере страховий фонд', () => {
  const { e } = setup();
  e.setLeverage(1, 'BTCUSDT', 50);
  L(e, 2, 'SELL', '80000', '1');
  M(e, 1, 'BUY', '1');
  e.setMark('BTCUSDT', 70000n * 100000000n);
  assert.equal(e.checkLiquidations(), 1);
  assert.equal(pos(e, 1), undefined);
  assert.equal(pos(e, FEE).size, '1'); // страховий фонд тепер у лонгу
  assert.equal(acc(e, 1).walletBalance, '98320'); // збиток не більший за маржу
  ok(e);
});

test('стан відновлюється після рестарту', () => {
  const { db, e } = setup();
  L(e, 2, 'SELL', '80000', '1');
  M(e, 1, 'BUY', '0.5');
  const o = L(e, 1, 'BUY', '70000', '0.2').order;
  const e2 = new Engine(db, { ...cfg, bots: false });
  e2.setFeeAccount(FEE);
  assert.equal(e2.openOrders(1)[0].id, o.id);
  assert.deepEqual(e2.positions(1), e.positions(1));
  assert.deepEqual(e2.account(1), e.account(1));
  ok(e2);
});

test('випадковий потік ордерів і рухів ціни зберігає інваріанти', () => {
  const { e } = setup();
  let rnd = 42;
  const R = () => (rnd = (rnd * 1103515245 + 12345) % 2147483648) / 2147483648;
  let mid = 80000;
  for (let i = 0; i < 6000; i++) {
    const uid = 1 + Math.floor(R() * 3);
    try {
      const x = R();
      if (x < 0.1) {
        const open = e.openOrders(uid);
        if (open.length) e.cancelOrder(uid, open[Math.floor(R() * open.length)].id);
      } else if (x < 0.13) {
        if (pos(e, uid)) e.closePosition(uid, 'BTCUSDT');
      } else if (x < 0.15) {
        e.setLeverage(uid, 'BTCUSDT', 1 + Math.floor(R() * 100));
      } else if (x < 0.2) {
        mid *= 1 + (R() - 0.5) * 0.03;
        e.setMark('BTCUSDT', BigInt(Math.round(mid)) * 100000000n);
        e.checkLiquidations();
      } else {
        const side = R() < 0.5 ? 'BUY' : 'SELL';
        const qty = (Math.floor(R() * 50000) / 100000 + 0.001).toFixed(5);
        const px = Math.round(mid * (1 + (R() - 0.5) * 0.02)).toString();
        const extra = R() < 0.15 ? { reduceOnly: true } : {};
        if (R() < 0.25) M(e, uid, side, qty, extra);
        else L(e, uid, side, px, qty, { tif: R() > 0.9 ? 'IOC' : 'GTC', ...extra });
      }
    } catch (err) {
      if (!err.code) throw err;
    }
  }
  ok(e);
});
