'use strict';
// Демо-боти, щоб у книзі завжди була ліквідність і графік рухався:
//  - market maker виставляє сітку лімітних ордерів навколо "справедливої" ціни;
//  - taker іноді робить невеликі ринкові угоди.
// Ціна маркетмейкера тягнеться до останньої угоди, тож користувачі реально рухають ринок.

const { toUnits, fmt } = require('./decimal');

function startBots(engine, auth, hedger = null) {
  const mm = auth.ensureSystemUser('market_maker', 'bot');
  const tk = auth.ensureSystemUser('taker_bot', 'bot');
  engine.noOrderLimit.add(mm.id); // 20 пар × 24 рівні — більше за ліміт для людей
  // Стартовий капітал ботів у кожній монеті (докладається і для щойно доданих пар)
  const seed = (uid, usdt, perCoinUsd) => {
    const add = {};
    if (engine._peekBal(uid, 'USDT').free + engine._peekBal(uid, 'USDT').locked === 0n) add.USDT = usdt;
    for (const m of engine.markets.values()) {
      const b = engine._peekBal(uid, m.base);
      if (b.free + b.locked > 0n) continue;
      const px = Number(fmt(engine.last.get(m.symbol)));
      const u = toUnits((perCoinUsd / px).toFixed(8));
      if (u) add[m.base] = fmt(u - (u % m.step));
    }
    if (Object.keys(add).length) engine.deposit(uid, add, 'bot_seed');
  };
  seed(mm.id, '50000000', 3000000);
  seed(tk.id, '2000000', 100000);

  const fair = new Map();
  for (const m of engine.markets.values()) fair.set(m.symbol, Number(fmt(engine.last.get(m.symbol))));

  const roundTo = (x, stepUnits, up = false) => {
    const u = toUnits(x.toFixed(8));
    const r = u % stepUnits;
    return fmt(up && r ? u - r + stepUnits : u - r);
  };

  function quote(m) {
    const real = hedger ? hedger.mid(m.symbol) : null;
    let f;
    if (real) {
      // Підключено брокера: котируємо навколо реальної ринкової ціни
      f = real;
    } else {
      const last = Number(fmt(engine.last.get(m.symbol)));
      f = fair.get(m.symbol);
      f = f + (last - f) * 0.3; // підтягуємось до ринку
      f *= 1 + (Math.random() - 0.5) * 0.002; // невеликий випадковий дрейф
    }
    fair.set(m.symbol, f);
    try {
      engine.cancelAll(mm.id, m.symbol);
      const notionalPerLevel = m.base === 'BTC' ? 15000 : 8000;
      for (let i = 1; i <= 12; i++) {
        // Перший рівень ~0.005% від ціни (як вузький спред на великій біржі), далі ширше
        const spread = 0.00004 + 0.00012 * (i - 1) + Math.random() * 0.00003;
        const size = (notionalPerLevel * (0.4 + Math.random())) / f;
        const qty = roundTo(size, m.step);
        for (const side of ['BUY', 'SELL']) {
          // купівлю округлюємо вниз, продаж — вгору, щоб на грубому кроці ціни вони не зійшлись
          const px = side === 'BUY' ? roundTo(f * (1 - spread), m.tick) : roundTo(f * (1 + spread), m.tick, true);
          try {
            engine.placeOrder(mm.id, { symbol: m.symbol, side, type: 'LIMIT_MAKER', price: px, qty });
          } catch {
            /* post-only відхилено або не вистачає балансу — пропускаємо рівень */
          }
        }
      }
    } catch (e) {
      console.error('mm error', e.message);
    }
  }

  function take(m) {
    if (Math.random() > 0.45) return;
    const side = Math.random() < 0.5 ? 'BUY' : 'SELL';
    const px = fair.get(m.symbol) || Number(fmt(engine.last.get(m.symbol)));
    const qty = roundTo((50 + Math.random() * 900) / px, m.step);
    try {
      engine.placeOrder(tk.id, { symbol: m.symbol, side, type: 'MARKET', qty });
    } catch {}
  }

  for (const m of engine.markets.values()) quote(m);
  const t1 = setInterval(() => engine.markets.forEach(quote), 2000);
  const t2 = setInterval(() => engine.markets.forEach(take), 1300);
  return () => {
    clearInterval(t1);
    clearInterval(t2);
  };
}

module.exports = { startBots };
