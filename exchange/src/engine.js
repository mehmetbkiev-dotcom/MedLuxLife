'use strict';
// Матчинг-движок: книги ордерів у пам'яті, пріоритет ціна-час, баланси з блокуванням,
// облік PnL (середня ціна входу), свічки. Node однопотоковий, тому кожна команда
// (ордер / скасування) виконується атомарно, а її результат записується в SQLite
// однією транзакцією перед тим, як клієнт отримає відповідь.

const { SCALE, toUnits, fmt, min } = require('./decimal');

const BPS = 10000n;
const OPEN = new Set(['NEW', 'PARTIALLY_FILLED']);
const CANDLE_MS = 60_000;
const CANDLE_KEEP = 7 * 24 * 60; // 7 днів хвилинних свічок

class ApiError extends Error {
  constructor(status, code, message) {
    super(message);
    this.status = status;
    this.code = code;
  }
}
const bad = (code, msg) => new ApiError(400, code, msg);

class BookSide {
  constructor(isBid) {
    this.isBid = isBid;
    this.prices = []; // відсортовано від найкращої ціни
    this.levels = new Map(); // price -> { price, orders: [], qty }
  }
  best() {
    return this.prices.length ? this.prices[0] : null;
  }
  _idx(price) {
    let lo = 0, hi = this.prices.length;
    while (lo < hi) {
      const mid = (lo + hi) >> 1;
      const p = this.prices[mid];
      if (this.isBid ? p > price : p < price) lo = mid + 1;
      else hi = mid;
    }
    return lo;
  }
  add(o) {
    let lvl = this.levels.get(o.price);
    if (!lvl) {
      lvl = { price: o.price, orders: [], qty: 0n };
      this.levels.set(o.price, lvl);
      this.prices.splice(this._idx(o.price), 0, o.price);
    }
    lvl.orders.push(o);
    lvl.qty += o.qty - o.filled;
  }
  remove(o) {
    const lvl = this.levels.get(o.price);
    if (!lvl) return;
    const i = lvl.orders.indexOf(o);
    if (i < 0) return;
    lvl.orders.splice(i, 1);
    lvl.qty -= o.qty - o.filled;
    if (!lvl.orders.length) {
      this.levels.delete(o.price);
      const j = this._idx(o.price);
      if (this.prices[j] === o.price) this.prices.splice(j, 1);
    }
  }
  depth(n) {
    const out = [];
    for (let i = 0; i < this.prices.length && i < n; i++) {
      const l = this.levels.get(this.prices[i]);
      out.push([fmt(l.price), fmt(l.qty)]);
    }
    return out;
  }
}

class Engine {
  constructor(db, cfg) {
    this.db = db;
    this.cfg = cfg;
    this.markets = new Map();
    this.marketByBase = new Map();
    for (const m of cfg.markets) {
      const mk = {
        ...m,
        tick: toUnits(m.tick),
        step: toUnits(m.step),
        minNotional: toUnits(m.minNotional),
        refPrice: toUnits(m.refPrice),
      };
      // Гарантуємо точність: price*qty завжди ділиться на SCALE без залишку.
      if ((mk.tick * mk.step) % SCALE !== 0n) throw new Error(`tick*step of ${m.symbol} is not exact`);
      this.markets.set(m.symbol, mk);
      this.marketByBase.set(m.base, mk);
    }
    this.bal = new Map(); // `${uid}:${asset}` -> {uid, asset, free, locked}
    this.pos = new Map(); // `${uid}:${asset}` -> {uid, asset, qty, cost, realized, fees}
    this.open = new Map(); // id -> order (тільки відкриті)
    this.userOpen = new Map(); // uid -> Set(order)
    this.books = new Map();
    this.last = new Map();
    this.candles = new Map();
    this.lastFaucet = new Map();
    this.feeUid = null;
    this.onEvents = () => {};
    this._resetTx();
    this._prepare();
    this._load();
  }

  // ---------- персистентність ----------
  _prepare() {
    const d = this.db;
    this.st = {
      bal: d.prepare(`INSERT INTO balances(user_id, asset, free, locked) VALUES(?,?,?,?)
        ON CONFLICT(user_id, asset) DO UPDATE SET free=excluded.free, locked=excluded.locked`),
      pos: d.prepare(`INSERT INTO positions(user_id, asset, qty, cost, realized, fees) VALUES(?,?,?,?,?,?)
        ON CONFLICT(user_id, asset) DO UPDATE SET qty=excluded.qty, cost=excluded.cost,
        realized=excluded.realized, fees=excluded.fees`),
      order: d.prepare(`INSERT INTO orders(id, user_id, symbol, side, type, tif, price, qty, quote_qty,
        filled, quote_filled, fee, status, created_at, updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(id) DO UPDATE SET filled=excluded.filled, quote_filled=excluded.quote_filled,
        fee=excluded.fee, status=excluded.status, updated_at=excluded.updated_at`),
      trade: d.prepare(`INSERT INTO trades(id, symbol, price, qty, quote_qty, buy_order_id, sell_order_id,
        buyer_id, seller_id, taker_side, buyer_fee, seller_fee, ts) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)`),
      ledger: d.prepare('INSERT INTO ledger(user_id, asset, amount, reason, ts) VALUES(?,?,?,?,?)'),
    };
  }

  _resetTx() {
    this.tx = { bal: new Set(), pos: new Set(), orders: new Set(), trades: [], ledger: [], depth: new Set() };
  }

  _commit() {
    const tx = this.tx;
    const st = this.st;
    try {
      this.db.exec('BEGIN');
      for (const b of tx.bal) st.bal.run(b.uid, b.asset, b.free.toString(), b.locked.toString());
      for (const p of tx.pos)
        st.pos.run(p.uid, p.asset, p.qty.toString(), p.cost.toString(), p.realized.toString(), p.fees.toString());
      for (const o of tx.orders)
        st.order.run(o.id, o.uid, o.symbol, o.side, o.type, o.tif, s(o.price), s(o.qty), s(o.quoteQty),
          o.filled.toString(), o.quoteFilled.toString(), o.fee.toString(), o.status, o.created, o.updated);
      for (const t of tx.trades)
        st.trade.run(t.id, t.symbol, t.price.toString(), t.qty.toString(), t.quote.toString(), t.buyOrderId,
          t.sellOrderId, t.buyer, t.seller, t.takerSide, t.buyerFee.toString(), t.sellerFee.toString(), t.ts);
      for (const l of tx.ledger) st.ledger.run(l.uid, l.asset, l.amount.toString(), l.reason, l.ts);
      this.db.exec('COMMIT');
    } catch (e) {
      // Стан у пам'яті вже не збігається з диском: зупиняємось, після рестарту стан
      // відновиться з останньої успішної транзакції.
      console.error('FATAL: persist failed', e);
      try { this.db.exec('ROLLBACK'); } catch {}
      process.exit(1);
    }
    const events = [];
    const users = new Set();
    for (const b of tx.bal) users.add(b.uid);
    for (const uid of users) events.push({ type: 'balances', uid });
    for (const o of tx.orders) events.push({ type: 'order', uid: o.uid, order: this.orderJson(o) });
    for (const t of tx.trades) events.push({ type: 'trade', trade: t });
    for (const sym of tx.depth) events.push({ type: 'depth', symbol: sym });
    this._resetTx();
    if (events.length) this.onEvents(events);
  }

  _load() {
    const d = this.db;
    for (const r of d.prepare('SELECT * FROM balances').all())
      this.bal.set(`${r.user_id}:${r.asset}`, { uid: r.user_id, asset: r.asset, free: BigInt(r.free), locked: BigInt(r.locked) });
    for (const r of d.prepare('SELECT * FROM positions').all())
      this.pos.set(`${r.user_id}:${r.asset}`, {
        uid: r.user_id, asset: r.asset, qty: BigInt(r.qty), cost: BigInt(r.cost),
        realized: BigInt(r.realized), fees: BigInt(r.fees),
      });
    for (const m of this.markets.values()) {
      this.books.set(m.symbol, { bids: new BookSide(true), asks: new BookSide(false) });
      const t = d.prepare('SELECT price FROM trades WHERE symbol=? ORDER BY id DESC LIMIT 1').get(m.symbol);
      this.last.set(m.symbol, t ? BigInt(t.price) : m.refPrice);
      this.candles.set(m.symbol, []);
    }
    for (const r of d.prepare("SELECT * FROM orders WHERE status IN ('NEW','PARTIALLY_FILLED') ORDER BY id").all()) {
      const o = rowToOrder(r);
      if (!this.books.has(o.symbol)) continue;
      const b = this.books.get(o.symbol);
      (o.side === 'BUY' ? b.bids : b.asks).add(o);
      this._track(o);
    }
    this.nextOrderId = (d.prepare('SELECT MAX(id) AS m FROM orders').get().m || 0) + 1;
    this.nextTradeId = (d.prepare('SELECT MAX(id) AS m FROM trades').get().m || 0) + 1;
    const since = Date.now() - CANDLE_KEEP * CANDLE_MS;
    for (const r of d.prepare('SELECT symbol, price, qty, quote_qty, ts FROM trades WHERE ts>=? ORDER BY id').iterate(since))
      this._candle(r.symbol, BigInt(r.price), BigInt(r.qty), BigInt(r.quote_qty), r.ts);
  }

  setFeeAccount(uid) {
    this.feeUid = uid;
  }

  // ---------- допоміжне ----------
  _b(uid, asset) {
    const k = `${uid}:${asset}`;
    let b = this.bal.get(k);
    if (!b) {
      b = { uid, asset, free: 0n, locked: 0n };
      this.bal.set(k, b);
    }
    this.tx.bal.add(b);
    return b;
  }
  _peekBal(uid, asset) {
    return this.bal.get(`${uid}:${asset}`) || { free: 0n, locked: 0n };
  }
  _p(uid, asset) {
    const k = `${uid}:${asset}`;
    let p = this.pos.get(k);
    if (!p) {
      p = { uid, asset, qty: 0n, cost: 0n, realized: 0n, fees: 0n };
      this.pos.set(k, p);
    }
    this.tx.pos.add(p);
    return p;
  }
  _track(o) {
    this.open.set(o.id, o);
    let s = this.userOpen.get(o.uid);
    if (!s) this.userOpen.set(o.uid, (s = new Set()));
    s.add(o);
  }
  _untrack(o) {
    this.open.delete(o.id);
    const s = this.userOpen.get(o.uid);
    if (s) s.delete(o);
  }
  _touch(o) {
    o.updated = Date.now();
    this.tx.orders.add(o);
    this.tx.depth.add(o.symbol);
  }

  // ---------- депозити ----------
  deposit(uid, amounts, reason) {
    const ts = Date.now();
    for (const [asset, v] of Object.entries(amounts)) {
      const amt = toUnits(v);
      if (!amt) continue;
      this._b(uid, asset).free += amt;
      this.tx.ledger.push({ uid, asset, amount: amt, reason, ts });
      const m = this.marketByBase.get(asset);
      if (m) {
        // Монети, що прийшли депозитом, отримують собівартість за поточною ціною,
        // щоб PnL рахувався від моменту зарахування.
        const p = this._p(uid, asset);
        p.qty += amt;
        p.cost += (amt * this.last.get(m.symbol)) / SCALE;
      }
    }
    this._commit();
  }

  faucet(uid) {
    let lastTs = this.lastFaucet.get(uid);
    if (lastTs === undefined) {
      const r = this.db.prepare("SELECT MAX(ts) AS t FROM ledger WHERE user_id=? AND reason='faucet'").get(uid);
      lastTs = r.t || 0;
    }
    const wait = lastTs + this.cfg.faucetCooldownMs - Date.now();
    if (wait > 0) throw new ApiError(429, 'FAUCET_COOLDOWN', `Кран доступний через ${Math.ceil(wait / 60000)} хв`);
    this.lastFaucet.set(uid, Date.now());
    this.deposit(uid, this.cfg.faucet, 'faucet');
  }

  // ---------- ордери ----------
  placeOrder(uid, req) {
    const m = this.markets.get(String(req.symbol || '').toUpperCase());
    if (!m) throw bad('BAD_SYMBOL', 'Невідома торгова пара');
    const side = String(req.side || '').toUpperCase();
    if (side !== 'BUY' && side !== 'SELL') throw bad('BAD_SIDE', 'side має бути BUY або SELL');
    const type = String(req.type || 'LIMIT').toUpperCase();
    if (!['LIMIT', 'MARKET', 'LIMIT_MAKER'].includes(type)) throw bad('BAD_TYPE', 'type: LIMIT | MARKET | LIMIT_MAKER');
    const buy = side === 'BUY';
    const book = this.books.get(m.symbol);
    const opp = buy ? book.asks : book.bids;
    const openCount = this.userOpen.get(uid)?.size || 0;

    let price = null, qty = null, quoteQty = null, tif = null;
    if (type === 'MARKET') {
      if (req.quoteQty !== undefined && req.quoteQty !== null && req.quoteQty !== '') {
        if (!buy) throw bad('BAD_PARAM', 'quoteQty підтримується лише для ринкової купівлі');
        quoteQty = toUnits(req.quoteQty);
        if (!quoteQty) throw bad('BAD_QTY', 'Некоректна сума');
        if (quoteQty < m.minNotional) throw bad('MIN_NOTIONAL', `Мінімальна сума ордера ${fmt(m.minNotional)} ${m.quote}`);
      } else {
        qty = this._qty(m, req.qty);
      }
      if (opp.best() === null) throw bad('NO_LIQUIDITY', 'Немає зустрічних ордерів');
    } else {
      price = toUnits(req.price);
      if (!price) throw bad('BAD_PRICE', 'Некоректна ціна');
      if (price % m.tick !== 0n) throw bad('BAD_PRICE', `Крок ціни ${fmt(m.tick)}`);
      qty = this._qty(m, req.qty);
      if ((price * qty) / SCALE < m.minNotional) throw bad('MIN_NOTIONAL', `Мінімальна сума ордера ${fmt(m.minNotional)} ${m.quote}`);
      tif = type === 'LIMIT_MAKER' ? 'GTC' : String(req.tif || 'GTC').toUpperCase();
      if (!['GTC', 'IOC', 'FOK'].includes(tif)) throw bad('BAD_TIF', 'tif: GTC | IOC | FOK');
      if (tif === 'GTC' && openCount >= this.cfg.maxOpenOrdersPerUser)
        throw bad('TOO_MANY_ORDERS', `Максимум ${this.cfg.maxOpenOrdersPerUser} відкритих ордерів`);
      if (type === 'LIMIT_MAKER') {
        const b = opp.best();
        if (b !== null && (buy ? b <= price : b >= price))
          throw bad('WOULD_TAKE', 'Post-only ордер виконався б одразу як taker — відхилено');
      }
    }

    // Перевірка коштів
    const qb = this._peekBal(uid, m.quote), bb = this._peekBal(uid, m.base);
    if (buy) {
      const need = price !== null ? (price * qty) / SCALE : quoteQty;
      if (need !== null && qb.free < need) throw bad('INSUFFICIENT_BALANCE', `Недостатньо ${m.quote}`);
      if (qb.free <= 0n) throw bad('INSUFFICIENT_BALANCE', `Недостатньо ${m.quote}`);
    } else if (bb.free < qty) throw bad('INSUFFICIENT_BALANCE', `Недостатньо ${m.base}`);

    const now = Date.now();
    const o = {
      id: this.nextOrderId++, uid, symbol: m.symbol, side, type, tif, price, qty, quoteQty,
      filled: 0n, quoteFilled: 0n, fee: 0n, status: 'NEW', created: now, updated: now,
    };
    const fills = [];

    // FOK: або повністю, або нічого — перевіряємо до будь-яких змін
    if (tif === 'FOK' && this._fillable(o, opp) < qty) {
      o.status = 'EXPIRED';
      this.tx.orders.add(o);
      this._commit();
      return { order: this.orderJson(o), fills };
    }

    if (price !== null) this._lock(o, m);
    this._match(o, m, opp, fills);

    if (price !== null) {
      if (o.filled === o.qty) o.status = 'FILLED';
      else if (tif === 'GTC') {
        o.status = o.filled > 0n ? 'PARTIALLY_FILLED' : 'NEW';
        (buy ? book.bids : book.asks).add(o);
        this._track(o);
      } else {
        this._unlockRemaining(o, m);
        o.status = 'EXPIRED';
      }
    } else if (qty !== null) {
      o.status = o.filled === qty ? 'FILLED' : 'EXPIRED';
    } else {
      o.status = o.filled > 0n && o._stop === 'funds' ? 'FILLED' : 'EXPIRED';
    }
    delete o._stop;
    this._touch(o);
    this._commit();
    return { order: this.orderJson(o), fills };
  }

  _qty(m, v) {
    const q = toUnits(v);
    if (!q) throw bad('BAD_QTY', 'Некоректна кількість');
    if (q % m.step !== 0n) throw bad('BAD_QTY', `Крок кількості ${fmt(m.step)}`);
    return q;
  }

  _fillable(o, opp) {
    let sum = 0n;
    for (const px of opp.prices) {
      if (o.side === 'BUY' ? px > o.price : px < o.price) break;
      for (const r of opp.levels.get(px).orders) if (r.uid !== o.uid) sum += r.qty - r.filled;
      if (sum >= o.qty) break;
    }
    return sum;
  }

  _lock(o, m) {
    if (o.side === 'BUY') {
      const b = this._b(o.uid, m.quote), amt = (o.price * o.qty) / SCALE;
      b.free -= amt;
      b.locked += amt;
    } else {
      const b = this._b(o.uid, m.base);
      b.free -= o.qty;
      b.locked += o.qty;
    }
  }

  _unlockRemaining(o, m) {
    const rem = o.qty - o.filled;
    if (rem <= 0n) return;
    if (o.side === 'BUY') {
      const b = this._b(o.uid, m.quote), amt = (o.price * rem) / SCALE;
      b.locked -= amt;
      b.free += amt;
    } else {
      const b = this._b(o.uid, m.base);
      b.locked -= rem;
      b.free += rem;
    }
  }

  _closeResting(o, status) {
    const m = this.markets.get(o.symbol);
    const book = this.books.get(o.symbol);
    (o.side === 'BUY' ? book.bids : book.asks).remove(o);
    this._untrack(o);
    this._unlockRemaining(o, m);
    o.status = status;
    this._touch(o);
  }

  _match(o, m, opp, fills) {
    const buy = o.side === 'BUY';
    let guard = null;
    if (o.type === 'MARKET') {
      const b = opp.best();
      const d = (b * this.cfg.marketProtectionBps) / BPS;
      guard = buy ? b + d : b - d;
    }
    o._stop = 'book';
    for (;;) {
      const px = opp.best();
      if (px === null) { o._stop = 'book'; break; }
      if (o.price !== null && (buy ? px > o.price : px < o.price)) { o._stop = 'price'; break; }
      if (guard !== null && (buy ? px > guard : px < guard)) { o._stop = 'protection'; break; }
      const lvl = opp.levels.get(px);
      const mk = lvl.orders[0];
      if (mk.uid === o.uid) {
        // Self-trade prevention: власний зустрічний ордер скасовується (як EXPIRE_MAKER у Binance)
        this._closeResting(mk, 'EXPIRED_STP');
        continue;
      }
      let q = mk.qty - mk.filled;
      if (o.qty !== null) q = min(q, o.qty - o.filled);
      if (o.type === 'MARKET' && buy) {
        let budget = this._peekBal(o.uid, m.quote).free;
        if (o.quoteQty !== null) budget = min(budget, o.quoteQty - o.quoteFilled);
        const maxQ = (budget * SCALE) / px;
        q = min(q, maxQ - (maxQ % m.step));
      }
      if (q <= 0n) { o._stop = 'funds'; break; }
      fills.push(this._fill(o, mk, px, q, m, lvl, opp));
      if (o.qty !== null && o.filled === o.qty) { o._stop = 'done'; break; }
    }
  }

  _fill(taker, maker, px, q, m, lvl, opp) {
    const cfg = this.cfg;
    const quote = (px * q) / SCALE;
    const takerBuys = taker.side === 'BUY';
    const buyO = takerBuys ? taker : maker;
    const sellO = takerBuys ? maker : taker;
    const buyerFee = (q * (takerBuys ? cfg.takerFeeBps : cfg.makerFeeBps)) / BPS; // в базовій монеті
    const sellerFee = (quote * (takerBuys ? cfg.makerFeeBps : cfg.takerFeeBps)) / BPS; // в котируваній

    // Покупець платить quote
    const bq = this._b(buyO.uid, m.quote);
    if (buyO.type === 'MARKET') bq.free -= quote;
    else {
      const lk = (buyO.price * q) / SCALE;
      bq.locked -= lk;
      bq.free += lk - quote; // повертаємо різницю, якщо виконалось краще за ліміт
    }
    // Продавець віддає base
    const sb = this._b(sellO.uid, m.base);
    if (sellO.type === 'MARKET') sb.free -= q;
    else sb.locked -= q;

    this._b(buyO.uid, m.base).free += q - buyerFee;
    this._b(sellO.uid, m.quote).free += quote - sellerFee;
    this._b(this.feeUid, m.base).free += buyerFee;
    this._b(this.feeUid, m.quote).free += sellerFee;

    for (const o of [taker, maker]) {
      o.filled += q;
      o.quoteFilled += quote;
    }
    buyO.fee += buyerFee;
    sellO.fee += sellerFee;
    lvl.qty -= q;
    if (maker.filled === maker.qty) {
      maker.status = 'FILLED';
      opp.remove(maker);
      this._untrack(maker);
    } else maker.status = 'PARTIALLY_FILLED';
    this._touch(maker);
    this._touch(taker);

    // PnL по базовій монеті (метод середньої ціни)
    const pb = this._p(buyO.uid, m.base);
    pb.qty += q - buyerFee;
    pb.cost += quote;
    pb.fees += (buyerFee * px) / SCALE;
    const ps = this._p(sellO.uid, m.base);
    const portion = ps.qty > 0n ? (ps.cost * min(q, ps.qty)) / ps.qty : 0n;
    ps.cost -= portion;
    ps.qty -= q;
    if (ps.qty < 0n) ps.qty = 0n;
    if (ps.qty === 0n) ps.cost = 0n;
    ps.realized += quote - sellerFee - portion;
    ps.fees += sellerFee;

    const ts = Date.now();
    const t = {
      id: this.nextTradeId++, symbol: m.symbol, price: px, qty: q, quote,
      buyOrderId: buyO.id, sellOrderId: sellO.id, buyer: buyO.uid, seller: sellO.uid,
      takerSide: taker.side, buyerFee, sellerFee, ts,
    };
    this.tx.trades.push(t);
    this.last.set(m.symbol, px);
    this._candle(m.symbol, px, q, quote, ts);
    return { tradeId: t.id, price: fmt(px), qty: fmt(q), quoteQty: fmt(quote), fee: fmt(takerBuys ? buyerFee : sellerFee) };
  }

  cancelOrder(uid, id) {
    const o = this.open.get(Number(id));
    if (!o || o.uid !== uid) throw new ApiError(404, 'NOT_FOUND', 'Відкритий ордер не знайдено');
    this._closeResting(o, 'CANCELED');
    this._commit();
    return this.orderJson(o);
  }

  cancelAll(uid, symbol) {
    const set = this.userOpen.get(uid);
    const list = set ? [...set].filter((o) => !symbol || o.symbol === symbol) : [];
    for (const o of list) this._closeResting(o, 'CANCELED');
    this._commit();
    return list.length;
  }

  // ---------- свічки / ринкові дані ----------
  _candle(symbol, px, q, quote, ts) {
    const arr = this.candles.get(symbol);
    if (!arr) return;
    const t = ts - (ts % CANDLE_MS);
    const c = arr[arr.length - 1];
    if (c && c.t === t) {
      if (px > c.h) c.h = px;
      if (px < c.l) c.l = px;
      c.c = px;
      c.v += q;
      c.qv += quote;
    } else {
      arr.push({ t, o: px, h: px, l: px, c: px, v: q, qv: quote });
      if (arr.length > CANDLE_KEEP + 100) arr.splice(0, arr.length - CANDLE_KEEP);
    }
  }

  klines(symbol, intervalMs, limit) {
    const arr = this.candles.get(symbol) || [];
    const out = [];
    for (let i = arr.length - 1; i >= 0; i--) {
      const c = arr[i];
      const t = c.t - (c.t % intervalMs);
      let cur = out[out.length - 1];
      if (!cur || cur.t !== t) {
        if (out.length >= limit) break;
        cur = { t, o: c.o, h: c.h, l: c.l, c: c.c, v: 0n };
        out.push(cur);
      }
      cur.o = c.o; // йдемо назад у часі, тому open — від найранішої
      if (c.h > cur.h) cur.h = c.h;
      if (c.l < cur.l) cur.l = c.l;
      cur.v += c.v;
    }
    return out.reverse().map((c) => [c.t, fmt(c.o), fmt(c.h), fmt(c.l), fmt(c.c), fmt(c.v)]);
  }

  ticker(symbol) {
    const arr = this.candles.get(symbol) || [];
    const since = Date.now() - 24 * 3600 * 1000;
    let open = null, high = null, low = null, vol = 0n, qvol = 0n;
    for (let i = arr.length - 1; i >= 0 && arr[i].t >= since; i--) {
      const c = arr[i];
      open = c.o;
      if (high === null || c.h > high) high = c.h;
      if (low === null || c.l < low) low = c.l;
      vol += c.v;
      qvol += c.qv;
    }
    const last = this.last.get(symbol);
    const book = this.books.get(symbol);
    const change = open ? Number(((last - open) * 1000000n) / open) / 10000 : 0;
    return {
      symbol, last: fmt(last), open: fmt(open ?? last), high: fmt(high ?? last), low: fmt(low ?? last),
      volume: fmt(vol), quoteVolume: fmt(qvol), changePct: change,
      bid: fmt(book.bids.best()), ask: fmt(book.asks.best()),
    };
  }

  depth(symbol, n = 20) {
    const b = this.books.get(symbol);
    return { symbol, bids: b.bids.depth(n), asks: b.asks.depth(n) };
  }

  // ---------- дані користувача ----------
  balances(uid) {
    const out = {};
    for (const a of this.cfg.assets) {
      const b = this._peekBal(uid, a);
      out[a] = { free: fmt(b.free), locked: fmt(b.locked) };
    }
    return out;
  }

  pnl(uid) {
    const rows = [];
    let totalUnreal = 0n, totalReal = 0n, equity = 0n;
    for (const a of this.cfg.assets) {
      const b = this._peekBal(uid, a);
      const m = this.marketByBase.get(a);
      if (!m) {
        equity += b.free + b.locked;
        continue;
      }
      const px = this.last.get(m.symbol);
      const p = this.pos.get(`${uid}:${a}`) || { qty: 0n, cost: 0n, realized: 0n, fees: 0n };
      const value = (p.qty * px) / SCALE;
      const unreal = value - p.cost;
      const avg = p.qty > 0n ? (p.cost * SCALE) / p.qty : 0n;
      totalUnreal += unreal;
      totalReal += p.realized;
      equity += ((b.free + b.locked) * px) / SCALE;
      rows.push({
        asset: a, symbol: m.symbol, qty: fmt(p.qty), avgPrice: fmt(avg - (avg % 1000n)), lastPrice: fmt(px),
        value: fmt(value), cost: fmt(p.cost), unrealized: fmt(unreal), realized: fmt(p.realized), fees: fmt(p.fees),
        unrealizedPct: p.cost > 0n ? Number((unreal * 1000000n) / p.cost) / 10000 : 0,
      });
    }
    return { quote: 'USDT', equity: fmt(equity), unrealized: fmt(totalUnreal), realized: fmt(totalReal), positions: rows };
  }

  openOrders(uid, symbol) {
    const set = this.userOpen.get(uid);
    if (!set) return [];
    return [...set].filter((o) => !symbol || o.symbol === symbol).sort((a, b) => b.id - a.id).map((o) => this.orderJson(o));
  }

  orderHistory(uid, limit = 100) {
    return this.db
      .prepare('SELECT * FROM orders WHERE user_id=? ORDER BY id DESC LIMIT ?')
      .all(uid, limit)
      .map((r) => this.orderJson(rowToOrder(r)));
  }

  myTrades(uid, limit = 100) {
    const rows = this.db
      .prepare(`SELECT * FROM (SELECT * FROM trades WHERE buyer_id=? ORDER BY id DESC LIMIT ?)
        UNION ALL SELECT * FROM (SELECT * FROM trades WHERE seller_id=? ORDER BY id DESC LIMIT ?)
        ORDER BY id DESC LIMIT ?`)
      .all(uid, limit, uid, limit, limit);
    return rows.map((r) => {
      const isBuyer = r.buyer_id === uid;
      return {
        id: r.id, symbol: r.symbol, side: isBuyer ? 'BUY' : 'SELL', price: fmt(BigInt(r.price)), qty: fmt(BigInt(r.qty)),
        quoteQty: fmt(BigInt(r.quote_qty)), fee: fmt(BigInt(isBuyer ? r.buyer_fee : r.seller_fee)),
        feeAsset: isBuyer ? this.markets.get(r.symbol).base : this.markets.get(r.symbol).quote,
        maker: (r.taker_side === 'BUY') !== isBuyer, orderId: isBuyer ? r.buy_order_id : r.sell_order_id, ts: r.ts,
      };
    });
  }

  recentTrades(symbol, limit = 50) {
    return this.db
      .prepare('SELECT id, price, qty, taker_side, ts FROM trades WHERE symbol=? ORDER BY id DESC LIMIT ?')
      .all(symbol, limit)
      .map((r) => ({ id: r.id, price: fmt(BigInt(r.price)), qty: fmt(BigInt(r.qty)), side: r.taker_side, ts: r.ts }));
  }

  orderJson(o) {
    return {
      id: o.id, symbol: o.symbol, side: o.side, type: o.type, tif: o.tif, price: fmt(o.price), qty: fmt(o.qty),
      quoteQty: fmt(o.quoteQty), filled: fmt(o.filled), quoteFilled: fmt(o.quoteFilled),
      avgPrice: o.filled > 0n ? fmt((o.quoteFilled * SCALE) / o.filled) : null, fee: fmt(o.fee), status: o.status,
      created: o.created, updated: o.updated,
    };
  }

  // ---------- аудит інваріантів ----------
  audit() {
    const issues = [];
    const totals = {};
    for (const b of this.bal.values()) {
      totals[b.asset] ??= 0n;
      totals[b.asset] += b.free + b.locked;
      if (b.free < 0n || b.locked < 0n) issues.push(`negative balance uid=${b.uid} ${b.asset}`);
    }
    const deposits = {};
    for (const r of this.db.prepare('SELECT asset, amount FROM ledger').iterate()) {
      deposits[r.asset] ??= 0n;
      deposits[r.asset] += BigInt(r.amount);
    }
    for (const a of new Set([...Object.keys(totals), ...Object.keys(deposits)]))
      if ((totals[a] || 0n) !== (deposits[a] || 0n))
        issues.push(`supply mismatch ${a}: balances=${fmt(totals[a] || 0n)} deposits=${fmt(deposits[a] || 0n)}`);
    // Заблоковане = сума потреб відкритих ордерів
    const needLock = new Map();
    for (const o of this.open.values()) {
      const m = this.markets.get(o.symbol);
      const asset = o.side === 'BUY' ? m.quote : m.base;
      const rem = o.qty - o.filled;
      const k = `${o.uid}:${asset}`;
      needLock.set(k, (needLock.get(k) || 0n) + (o.side === 'BUY' ? (o.price * rem) / SCALE : rem));
    }
    for (const b of this.bal.values())
      if (b.locked !== (needLock.get(`${b.uid}:${b.asset}`) || 0n))
        issues.push(`lock mismatch uid=${b.uid} ${b.asset}: locked=${fmt(b.locked)} need=${fmt(needLock.get(`${b.uid}:${b.asset}`) || 0n)}`);
    // Книга не перехрещена, рівні узгоджені
    for (const [sym, b] of this.books) {
      const bid = b.bids.best(), ask = b.asks.best();
      if (bid !== null && ask !== null && bid >= ask) issues.push(`crossed book ${sym}`);
      for (const side of [b.bids, b.asks])
        for (const lvl of side.levels.values()) {
          const s = lvl.orders.reduce((acc, o) => acc + o.qty - o.filled, 0n);
          if (s !== lvl.qty) issues.push(`level qty mismatch ${sym} ${fmt(lvl.price)}`);
        }
    }
    return {
      ok: issues.length === 0, issues: issues.slice(0, 50), openOrders: this.open.size,
      supply: Object.fromEntries(Object.entries(totals).map(([k, v]) => [k, fmt(v)])),
    };
  }
}

function s(v) {
  return v === null || v === undefined ? null : v.toString();
}

function rowToOrder(r) {
  const n = (v) => (v === null ? null : BigInt(v));
  return {
    id: r.id, uid: r.user_id, symbol: r.symbol, side: r.side, type: r.type, tif: r.tif, price: n(r.price),
    qty: n(r.qty), quoteQty: n(r.quote_qty), filled: BigInt(r.filled), quoteFilled: BigInt(r.quote_filled),
    fee: BigInt(r.fee), status: r.status, created: r.created_at, updated: r.updated_at,
  };
}

module.exports = { Engine, ApiError, OPEN };
