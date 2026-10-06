'use strict';
// Демо-боти, щоб у книзі завжди була ліквідність і графік рухався:
//  - market maker виставляє сітку лімітних ордерів навколо "справедливої" ціни;
//  - taker іноді робить невеликі ринкові угоди.
// Ціна маркетмейкера тягнеться до останньої угоди, тож користувачі реально рухають ринок.

const { toUnits, fmt } = require('./decimal');

function startBots(engine, auth) {
  const mm = auth.ensureSystemUser('market_maker', 'bot');
  const tk = auth.ensureSystemUser('taker_bot', 'bot');
  if (mm.created) engine.deposit(mm.id, { USDT: '50000000', BTC: '500', ETH: '10000' }, 'bot_seed');
  if (tk.created) engine.deposit(tk.id, { USDT: '2000000', BTC: '20', ETH: '400' }, 'bot_seed');

  const fair = new Map();
  for (const m of engine.markets.values()) fair.set(m.symbol, Number(fmt(engine.last.get(m.symbol))));

  const roundTo = (x, stepUnits) => {
    const u = toUnits(x.toFixed(8));
    return fmt(u - (u % stepUnits));
  };

  function quote(m) {
    const last = Number(fmt(engine.last.get(m.symbol)));
    let f = fair.get(m.symbol);
    f = f + (last - f) * 0.3; // підтягуємось до ринку
    f *= 1 + (Math.random() - 0.5) * 0.002; // невеликий випадковий дрейф
    fair.set(m.symbol, f);
    try {
      engine.cancelAll(mm.id, m.symbol);
      const notionalPerLevel = m.base === 'BTC' ? 15000 : 8000;
      for (let i = 1; i <= 12; i++) {
        const spread = 0.0004 * i + Math.random() * 0.0002;
        const size = (notionalPerLevel * (0.4 + Math.random())) / f;
        const qty = roundTo(size, m.step);
        for (const side of ['BUY', 'SELL']) {
          const px = roundTo(side === 'BUY' ? f * (1 - spread) : f * (1 + spread), m.tick);
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
    const px = Number(fmt(engine.last.get(m.symbol)));
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
