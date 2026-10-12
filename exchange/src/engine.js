'use strict';
// Ф'ючерсний матчинг-движок (USDT-M безстрокові контракти, як на Binance Futures):
//  - книги ордерів у пам'яті, пріоритет ціна-час;
//  - позиції one-way (лонг або шорт по парі), ізольована маржа, плече 1..maxLeverage;
//  - маржа під ордери блокується, PnL реалізується при зменшенні позиції;
//  - ціна маркування (від брокера або остання угода), ліквідація при падінні маржі
//    до підтримуючої; збитки понад маржу покриває страховий фонд;
//  - кожна команда виконується атомарно і записується в SQLite однією транзакцією.
// Усі суми — BigInt з 8 знаками (1 = 100_000_000), жодних float у грошах.

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
const abs = (v) => (v < 0n ? -v : v);
const sgn = (v) => (v > 0n ? 1n : v < 0n ? -1n : 0n);
const ceilDiv = (a, b) => (a <= 0n ? 0n : (a + b - 1n) / b);

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
    for (const m of cfg.markets) {
      const mk = {
        ...m,
        tick: toUnits(m.tick),
        step: toUnits(m.step),
        minNotional: toUnits(m.minNotional),
        refPrice: toUnits(m.refPrice),
        maxLeverage: m.maxLeverage || 50,
      };
      // Гарантуємо точність: price*qty завжди ділиться на SCALE без залишку.
      if ((mk.tick * mk.step) % SCALE !== 0n) throw new Error(`tick*step of ${m.symbol} is not exact`);
      this.markets.set(m.symbol, mk);
    }
    this.mmBps = cfg.maintenanceMarginBps ?? 50n;
    this.defaultLeverage = cfg.defaultLeverage || 10;
    this.bal = new Map(); // uid -> {uid, asset:'USDT', free, locked}
    this.pos = new Map(); // `${uid}:${symbol}` -> позиція
    this.open = new Map(); // id -> order (тільки відкриті)
    this.userOpen = new Map(); // uid -> Set(order)
    this.books = new Map();
    this.last = new Map();
    this.mark = new Map(); // ціна маркування від брокера (якщо є)
    this.traded = new Set(); // пари, де вже були угоди
    this.noOrderLimit = new Set(); // системні акаунти без ліміту відкритих ордерів
    this.noLiquidation = new Set(); // системні акаунти (боти), яких не ліквідуємо
    this.candles = new Map();
    this.lastFaucet = new Map();
    this.feeUid = null; // рахунок комісій і страхового фонду
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
      pos: d.prepare(`INSERT INTO fpositions(user_id, symbol, size, entry, margin, leverage, realized, fees)
        VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(user_id, symbol) DO UPDATE SET size=excluded.size, entry=excluded.entry,
        margin=excluded.margin, leverage=excluded.leverage, realized=excluded.realized, fees=excluded.fees`),
      order: d.prepare(`INSERT INTO orders(id, user_id, symbol, side, type, tif, price, qty, filled, quote_filled, fee,
        reduce_only, leverage, lock, lock_released, realized, status, created_at, updated_at)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(id) DO UPDATE SET filled=excluded.filled, quote_filled=excluded.quote_filled, fee=excluded.fee,
        lock_released=excluded.lock_released, realized=excluded.realized, status=excluded.status,
        updated_at=excluded.updated_at`),
      trade: d.prepare(`INSERT INTO trades(id, symbol, price, qty, quote_qty, buy_order_id, sell_order_id, buyer_id,
        seller_id, taker_side, buyer_fee, seller_fee, buyer_pnl, seller_pnl, ts) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`),
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
      for (const b of tx.bal) st.bal.run(b.uid, 'USDT', b.free.toString(), b.locked.toString());
      for (const p of tx.pos)
        st.pos.run(p.uid, p.symbol, p.size.toString(), p.entry.toString(), p.margin.toString(), p.leverage,
          p.realized.toString(), p.fees.toString());
      for (const o of tx.orders)
        st.order.run(o.id, o.uid, o.symbol, o.side, o.type, o.tif, s(o.price), o.qty.toString(), o.filled.toString(),
          o.quoteFilled.toString(), o.fee.toString(), o.reduceOnly ? 1 : 0, o.leverage, o.lock.toString(),
          o.lockRel.toString(), o.realized.toString(), o.status, o.created, o.updated);
      for (const t of tx.trades)
        st.trade.run(t.id, t.symbol, t.price.toString(), t.qty.toString(), t.quote.toString(), t.buyOrderId,
          t.sellOrderId, t.buyer, t.seller, t.takerSide, t.buyerFee.toString(), t.sellerFee.toString(),
          t.buyerPnl.toString(), t.sellerPnl.toString(), t.ts);
      for (const l of tx.ledger) st.ledger.run(l.uid, 'USDT', l.amount.toString(), l.reason, l.ts);
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
    for (const p of tx.pos) users.add(p.uid);
    for (const uid of users) events.push({ type: 'balances', uid });
    for (const o of tx.orders) events.push({ type: 'order', uid: o.uid, order: this.orderJson(o) });
    for (const t of tx.trades) events.push({ type: 'trade', trade: t });
    for (const sym of tx.depth) events.push({ type: 'depth', symbol: sym });
    this._resetTx();
    if (events.length) this.onEvents(events);
  }

  _load() {
    const d = this.db;
    for (const r of d.prepare("SELECT * FROM balances WHERE asset='USDT'").all())
      this.bal.set(r.user_id, { uid: r.user_id, free: BigInt(r.free), locked: BigInt(r.locked) });
    for (const r of d.prepare('SELECT * FROM fpositions').all())
      this.pos.set(`${r.user_id}:${r.symbol}`, {
        uid: r.user_id, symbol: r.symbol, size: BigInt(r.size), entry: BigInt(r.entry), margin: BigInt(r.margin),
        leverage: r.leverage, realized: BigInt(r.realized), fees: BigInt(r.fees),
      });
    for (const m of this.markets.values()) {
      this.books.set(m.symbol, { bids: new BookSide(true), asks: new BookSide(false) });
      const t = d.prepare('SELECT price FROM trades WHERE symbol=? ORDER BY id DESC LIMIT 1').get(m.symbol);
      this.last.set(m.symbol, t ? BigInt(t.price) : m.refPrice);
      if (t) this.traded.add(m.symbol);
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
  _b(uid) {
    let b = this.bal.get(uid);
    if (!b) {
      b = { uid, free: 0n, locked: 0n };
      this.bal.set(uid, b);
    }
    this.tx.bal.add(b);
    return b;
  }
  _peekBal(uid) {
    return this.bal.get(uid) || { free: 0n, locked: 0n };
  }
  _p(uid, symbol) {
    const k = `${uid}:${symbol}`;
    let p = this.pos.get(k);
    if (!p) {
      p = { uid, symbol, size: 0n, entry: 0n, margin: 0n, leverage: this.defaultLeverage, realized: 0n, fees: 0n };
      this.pos.set(k, p);
    }
    this.tx.pos.add(p);
    return p;
  }
  _peekPos(uid, symbol) {
    return this.pos.get(`${uid}:${symbol}`) || { size: 0n, entry: 0n, margin: 0n, leverage: this.defaultLeverage };
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
  // скільки позиції можна закрити ордером на цю сторону
  _reducible(uid, symbol, side) {
    const sz = this._peekPos(uid, symbol).size;
    return (side === 'BUY' && sz < 0n) || (side === 'SELL' && sz > 0n) ? abs(sz) : 0n;
  }
  markPrice(symbol) {
    return this.mark.get(symbol) ?? this.last.get(symbol);
  }
  setMark(symbol, units) {
    if (units && units > 0n) this.mark.set(symbol, units);
  }

  // ---------- депозити ----------
  deposit(uid, amounts, reason) {
    const ts = Date.now();
    const amt = toUnits(amounts.USDT);
    if (amt) {
      this._b(uid).free += amt;
      this.tx.ledger.push({ uid, amount: amt, reason, ts });
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

  // ---------- плече ----------
  setLeverage(uid, symbol, leverage) {
    const m = this.markets.get(String(symbol || '').toUpperCase());
    if (!m) throw bad('BAD_SYMBOL', 'Невідома торгова пара');
    const lev = Number(leverage);
    if (!Number.isInteger(lev) || lev < 1 || lev > m.maxLeverage)
      throw bad('BAD_LEVERAGE', `Плече для ${m.symbol}: від 1 до ${m.maxLeverage}`);
    if (this._peekPos(uid, m.symbol).size !== 0n) throw bad('HAS_POSITION', 'Закрийте позицію, щоб змінити плече');
    if ([...(this.userOpen.get(uid) || [])].some((o) => o.symbol === m.symbol))
      throw bad('HAS_ORDERS', 'Скасуйте відкриті ордери по цій парі, щоб змінити плече');
    this._p(uid, m.symbol).leverage = lev;
    this._commit();
    return { symbol: m.symbol, leverage: lev };
  }

  // ---------- ордери ----------
  placeOrder(uid, req, opts = {}) {
    const m = this.markets.get(String(req.symbol || '').toUpperCase());
    if (!m) throw bad('BAD_SYMBOL', 'Невідома торгова пара');
    const side = String(req.side || '').toUpperCase();
    if (side !== 'BUY' && side !== 'SELL') throw bad('BAD_SIDE', 'side має бути BUY або SELL');
    const type = String(req.type || 'LIMIT').toUpperCase();
    if (!['LIMIT', 'MARKET', 'LIMIT_MAKER'].includes(type)) throw bad('BAD_TYPE', 'type: LIMIT | MARKET | LIMIT_MAKER');
    const reduceOnly = req.reduceOnly === true || req.reduceOnly === 'true';
    const buy = side === 'BUY';
    const book = this.books.get(m.symbol);
    const opp = buy ? book.asks : book.bids;
    const pos = this._peekPos(uid, m.symbol);
    const lev = BigInt(pos.leverage);
    const closable = this._reducible(uid, m.symbol, side);

    let qty = this._qty(m, req.qty);
    if (reduceOnly) {
      if (closable === 0n) throw bad('REDUCE_ONLY', 'Reduce-only: немає позиції, яку цей ордер зменшив би');
      if (qty > closable) qty = closable;
    }

    let price = null, tif = null, est;
    if (type === 'MARKET') {
      const b = opp.best();
      if (b === null) throw bad('NO_LIQUIDITY', 'Немає зустрічних ордерів');
      const d = (b * this.cfg.marketProtectionBps) / BPS;
      est = buy ? b + d : b; // для оцінки маржі беремо гіршу можливу ціну
    } else {
      price = toUnits(req.price);
      if (!price) throw bad('BAD_PRICE', 'Некоректна ціна');
      if (price % m.tick !== 0n) throw bad('BAD_PRICE', `Крок ціни ${fmt(m.tick)}`);
      est = price;
      tif = type === 'LIMIT_MAKER' ? 'GTC' : String(req.tif || 'GTC').toUpperCase();
      if (!['GTC', 'IOC', 'FOK'].includes(tif)) throw bad('BAD_TIF', 'tif: GTC | IOC | FOK');
      const openCount = this.userOpen.get(uid)?.size || 0;
      if (tif === 'GTC' && openCount >= this.cfg.maxOpenOrdersPerUser && !this.noOrderLimit.has(uid))
        throw bad('TOO_MANY_ORDERS', `Максимум ${this.cfg.maxOpenOrdersPerUser} відкритих ордерів`);
      if (type === 'LIMIT_MAKER') {
        const b = opp.best();
        if (b !== null && (buy ? b <= price : b >= price))
          throw bad('WOULD_TAKE', 'Post-only ордер виконався б одразу як taker — відхилено');
      }
    }
    if (!reduceOnly && (est * qty) / SCALE < m.minNotional)
      throw bad('MIN_NOTIONAL', `Мінімальний обсяг ордера ${fmt(m.minNotional)} USDT`);

    // Маржа: лише під частину, що відкриває/збільшує позицію (закриття маржі не потребує),
    // плюс запас на комісію. Для лімітних — блокується, для ринкових — лише перевіряється.
    const openQty = reduceOnly ? 0n : qty > closable ? qty - closable : 0n;
    const feeLock = (((est * qty) / SCALE) * this.cfg.takerFeeBps * 2n) / BPS;
    const need = ceilDiv((est * openQty) / SCALE, lev) + feeLock;
    const free = this._peekBal(uid).free;
    if (need > free)
      throw bad('INSUFFICIENT_MARGIN', `Недостатньо маржі: потрібно ${fmt(need)} USDT, доступно ${fmt(free)} USDT`);

    const now = Date.now();
    const o = {
      id: this.nextOrderId++, uid, symbol: m.symbol, side, type: opts.liquidation ? 'LIQUIDATION' : type, tif, price, qty,
      filled: 0n, quoteFilled: 0n, fee: 0n, reduceOnly, leverage: Number(lev), lock: 0n, lockRel: 0n, realized: 0n,
      status: 'NEW', created: now, updated: now,
    };
    const fills = [];

    if (tif === 'FOK' && this._fillable(o, opp) < qty) {
      o.status = 'EXPIRED';
      this.tx.orders.add(o);
      this._commit();
      return { order: this.orderJson(o), fills };
    }

    if (price !== null) {
      const b = this._b(uid);
      b.free -= need;
      b.locked += need;
      o.lock = need;
    }
    this._match(o, m, opp, fills, opts);

    if (price !== null) {
      if (o.filled === o.qty) o.status = 'FILLED';
      else if (tif === 'GTC' && !(reduceOnly && this._reducible(uid, m.symbol, side) === 0n)) {
        o.status = o.filled > 0n ? 'PARTIALLY_FILLED' : 'NEW';
        (buy ? book.bids : book.asks).add(o);
        this._track(o);
      } else o.status = 'EXPIRED';
    } else o.status = o.filled === qty ? 'FILLED' : 'EXPIRED';
    if (!OPEN.has(o.status)) this._releaseLock(o);
    this._touch(o);
    this._afterPositionChange(uid, m.symbol);
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

  _releaseLock(o) {
    const rest = o.lock - o.lockRel;
    if (rest <= 0n) return;
    const b = this._b(o.uid);
    b.locked -= rest;
    b.free += rest;
    o.lockRel = o.lock;
  }

  _closeResting(o, status) {
    const book = this.books.get(o.symbol);
    (o.side === 'BUY' ? book.bids : book.asks).remove(o);
    this._untrack(o);
    this._releaseLock(o);
    o.status = status;
    this._touch(o);
  }

  // Reduce-only ордери, які вже нічого не зменшать (позицію закрито/перевернуто), скасовуються
  _afterPositionChange(uid, symbol) {
    const set = this.userOpen.get(uid);
    if (!set) return;
    for (const o of [...set])
      if (o.symbol === symbol && o.reduceOnly && this._reducible(uid, symbol, o.side) === 0n) this._closeResting(o, 'EXPIRED');
  }

  _match(o, m, opp, fills, opts = {}) {
    const buy = o.side === 'BUY';
    let guard = null;
    if (o.type === 'MARKET') {
      const b = opp.best();
      const d = (b * this.cfg.marketProtectionBps) / BPS;
      guard = buy ? b + d : b - d;
    }
    for (;;) {
      const px = opp.best();
      if (px === null) break;
      if (o.price !== null && (buy ? px > o.price : px < o.price)) break;
      if (guard !== null && (buy ? px > guard : px < guard)) break;
      const lvl = opp.levels.get(px);
      const mk = lvl.orders[0];
      if (mk.uid === o.uid) {
        // Self-trade prevention: власний зустрічний ордер скасовується
        this._closeResting(mk, 'EXPIRED_STP');
        continue;
      }
      let q = min(mk.qty - mk.filled, o.qty - o.filled);
      if (o.reduceOnly) {
        const cap = this._reducible(o.uid, o.symbol, o.side);
        if (cap === 0n) break;
        q = min(q, cap);
      }
      if (mk.reduceOnly) {
        const cap = this._reducible(mk.uid, mk.symbol, mk.side);
        if (cap === 0n) {
          this._closeResting(mk, 'EXPIRED');
          continue;
        }
        q = min(q, cap);
      }
      fills.push(this._fill(o, mk, px, q, m, lvl, opp, opts));
      if (o.filled === o.qty) break;
    }
  }

  _fill(taker, maker, px, q, m, lvl, opp, opts = {}) {
    const cfg = this.cfg;
    const takerFee = opts.liquidation ? 0n : cfg.takerFeeBps;
    const t = this._settle(taker, taker.side, q, px, takerFee, opts);
    const k = this._settle(maker, maker.side, q, px, cfg.makerFeeBps);
    const quote = (px * q) / SCALE;
    for (const o of [taker, maker]) {
      o.filled += q;
      o.quoteFilled += quote;
    }
    lvl.qty -= q;
    if (maker.filled === maker.qty) {
      maker.status = 'FILLED';
      opp.remove(maker);
      this._untrack(maker);
      this._releaseLock(maker);
    } else maker.status = 'PARTIALLY_FILLED';
    this._touch(maker);
    this._touch(taker);
    this._afterPositionChange(maker.uid, maker.symbol);

    const buyO = taker.side === 'BUY' ? taker : maker;
    const tr = this._recordTrade(m.symbol, px, q, buyO === taker ? taker : maker, buyO === taker ? maker : taker,
      taker.side, buyO === taker ? t : k, buyO === taker ? k : t);
    return { tradeId: tr.id, price: fmt(px), qty: fmt(q), fee: fmt(t.fee), realizedPnl: fmt(t.pnl) };
  }

  // Застосувати виконання q за ціною px до рахунку власника ордера o (або системного uid)
  _settle(o, side, q, px, feeBps, opts = {}, uidOverride = null) {
    const uid = o ? o.uid : uidOverride;
    const b = this._b(uid);
    const p = this._p(uid, o ? o.symbol : opts.symbol);
    const ins = this._b(this.feeUid);
    // 1. частка заблокованої під ордер суми повертається у вільні кошти
    if (o && o.lock > 0n) {
      const share = o.filled + q === o.qty ? o.lock - o.lockRel : (o.lock * q) / o.qty;
      const real = min(share, o.lock - o.lockRel);
      b.locked -= real;
      b.free += real;
      o.lockRel += real;
    }
    const d = side === 'BUY' ? 1n : -1n;
    let rem = q;
    let pnl = 0n;
    // 2. закриття (повне або часткове) протилежної позиції — реалізація PnL
    if (p.size !== 0n && sgn(p.size) !== d) {
      const a = abs(p.size);
      const cq = min(rem, a);
      pnl = (((px - p.entry) * cq) / SCALE) * sgn(p.size);
      const rel = cq === a ? p.margin : (p.margin * cq) / a;
      p.margin -= rel;
      p.size += d * cq;
      rem -= cq;
      p.realized += pnl;
      if (o) o.realized += pnl;
      let ret = rel + pnl;
      if (opts.liquidation) {
        // при ліквідації залишок маржі йде в страховий фонд, а збиток понад маржу — з нього
        ins.free += ret;
        ret = 0n;
      } else if (ret < 0n) {
        ins.free += ret; // збиток більший за маржу покриває страховий фонд
        ret = 0n;
      }
      b.free += ret;
      if (p.size === 0n) p.entry = 0n;
    }
    // 3. комісія (не більше, ніж є вільних коштів)
    let fee = (((px * q) / SCALE) * feeBps) / BPS;
    if (fee > b.free) fee = b.free > 0n ? b.free : 0n;
    b.free -= fee;
    ins.free += fee;
    p.fees += fee;
    if (o) o.fee += fee;
    // 4. відкриття/збільшення позиції — маржа = вартість / плече
    if (rem > 0n) {
      let im = ceilDiv((px * rem) / SCALE, BigInt(p.leverage));
      if (im > b.free) im = b.free > 0n ? b.free : 0n;
      b.free -= im;
      p.margin += im;
      const a = abs(p.size);
      p.entry = (a * p.entry + rem * px) / (a + rem);
      p.size += d * rem;
    }
    return { fee, pnl };
  }

  _recordTrade(symbol, px, q, buyO, sellO, takerSide, buyRes, sellRes, ids = {}) {
    const ts = Date.now();
    const t = {
      id: this.nextTradeId++, symbol, price: px, qty: q, quote: (px * q) / SCALE,
      buyOrderId: buyO ? buyO.id : 0, sellOrderId: sellO ? sellO.id : 0,
      buyer: buyO ? buyO.uid : ids.buyer, seller: sellO ? sellO.uid : ids.seller, takerSide,
      buyerFee: buyRes.fee, sellerFee: sellRes.fee, buyerPnl: buyRes.pnl, sellerPnl: sellRes.pnl, ts,
    };
    this.tx.trades.push(t);
    this.last.set(symbol, px);
    this.traded.add(symbol);
    this._candle(symbol, px, q, t.quote, ts);
    return t;
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

  // Закрити позицію повністю ринковим reduce-only ордером
  closePosition(uid, symbol) {
    const m = this.markets.get(String(symbol || '').toUpperCase());
    if (!m) throw bad('BAD_SYMBOL', 'Невідома торгова пара');
    const sz = this._peekPos(uid, m.symbol).size;
    if (sz === 0n) throw bad('NO_POSITION', 'Немає відкритої позиції');
    return this.placeOrder(uid, { symbol: m.symbol, side: sz > 0n ? 'SELL' : 'BUY', type: 'MARKET', qty: fmt(abs(sz)), reduceOnly: true });
  }

  // ---------- ліквідація ----------
  _liqCheck(p) {
    if (p.size === 0n || this.noLiquidation.has(p.uid) || p.uid === this.feeUid) return false;
    const mark = this.markPrice(p.symbol);
    const equity = p.margin + ((mark - p.entry) * p.size) / SCALE;
    const maint = (((abs(p.size) * mark) / SCALE) * this.mmBps) / BPS;
    return equity <= maint;
  }

  // Викликається періодично (раз на секунду) і після оновлення ціни маркування
  checkLiquidations() {
    const victims = [...this.pos.values()].filter((p) => this._liqCheck(p));
    for (const p of victims) this._liquidate(p);
    return victims.length;
  }

  _liquidate(p) {
    const m = this.markets.get(p.symbol);
    // 1. скасовуємо ордери користувача по цій парі
    for (const o of [...(this.userOpen.get(p.uid) || [])]) if (o.symbol === p.symbol) this._closeResting(o, 'CANCELED');
    const side = p.size > 0n ? 'SELL' : 'BUY';
    const qty = abs(p.size);
    const now = Date.now();
    const o = {
      id: this.nextOrderId++, uid: p.uid, symbol: p.symbol, side, type: 'LIQUIDATION', tif: 'IOC', price: null, qty,
      filled: 0n, quoteFilled: 0n, fee: 0n, reduceOnly: true, leverage: p.leverage, lock: 0n, lockRel: 0n,
      realized: 0n, status: 'NEW', created: now, updated: now,
    };
    const book = this.books.get(p.symbol);
    // 2. закриваємо позицію в книгу (до 10% від ціни маркування)
    const mark = this.markPrice(p.symbol);
    const band = (mark * 1000n) / BPS;
    o.price = side === 'SELL' ? mark - band - ((mark - band) % m.tick) : mark + band - ((mark + band) % m.tick);
    this._match(o, m, side === 'SELL' ? book.bids : book.asks, [], { liquidation: true });
    o.price = null;
    // 3. залишок, якого не взяла книга, переходить у страховий фонд за ціною маркування
    const rest = abs(this._peekPos(p.uid, p.symbol).size);
    if (rest > 0n) {
      const px = mark - (mark % m.tick) || m.tick;
      const ur = this._settle(o, side, rest, px, 0n, { liquidation: true });
      const ir = this._settle(null, side === 'SELL' ? 'BUY' : 'SELL', rest, px, 0n, { symbol: p.symbol }, this.feeUid);
      o.filled += rest;
      o.quoteFilled += (px * rest) / SCALE;
      if (side === 'SELL') this._recordTrade(p.symbol, px, rest, null, o, side, ir, ur, { buyer: this.feeUid });
      else this._recordTrade(p.symbol, px, rest, o, null, side, ur, ir, { seller: this.feeUid });
    }
    o.status = 'FILLED';
    this._touch(o);
    this._commit();
  }

  liquidationPrice(p) {
    if (p.size === 0n) return null;
    const a = Number(fmt(abs(p.size)));
    const e = Number(fmt(p.entry));
    const mg = Number(fmt(p.margin));
    const mmr = Number(this.mmBps) / 10000;
    const liq = p.size > 0n ? (e * a - mg) / (a * (1 - mmr)) : (e * a + mg) / (a * (1 + mmr));
    return liq > 0 ? liq : 0;
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
      symbol, last: fmt(last), mark: fmt(this.markPrice(symbol)), open: fmt(open ?? last), high: fmt(high ?? last),
      low: fmt(low ?? last), volume: fmt(vol), quoteVolume: fmt(qvol), changePct: change,
      bid: fmt(book.bids.best()), ask: fmt(book.asks.best()),
    };
  }

  depth(symbol, n = 20) {
    const b = this.books.get(symbol);
    return { symbol, bids: b.bids.depth(n), asks: b.asks.depth(n) };
  }

  // ---------- дані користувача ----------
  positions(uid) {
    const out = [];
    for (const m of this.markets.values()) {
      const p = this.pos.get(`${uid}:${m.symbol}`);
      if (!p || p.size === 0n) continue;
      const mark = this.markPrice(m.symbol);
      const unreal = ((mark - p.entry) * p.size) / SCALE;
      const notional = (abs(p.size) * mark) / SCALE;
      const liq = this.liquidationPrice(p);
      out.push({
        symbol: m.symbol, side: p.size > 0n ? 'LONG' : 'SHORT', size: fmt(p.size), entry: fmt(p.entry - (p.entry % m.tick)),
        mark: fmt(mark), liqPrice: liq === null ? null : liq.toFixed(8), margin: fmt(p.margin), leverage: p.leverage,
        notional: fmt(notional), unrealized: fmt(unreal), realized: fmt(p.realized),
        roePct: p.margin > 0n ? Number((unreal * 1000000n) / p.margin) / 10000 : 0,
        marginRatioPct: p.margin + unreal > 0n
          ? Number(((((notional * this.mmBps) / BPS) * 1000000n) / (p.margin + unreal))) / 10000 : 100,
      });
    }
    return out;
  }

  leverages(uid) {
    const out = {};
    for (const m of this.markets.values()) out[m.symbol] = this._peekPos(uid, m.symbol).leverage;
    return out;
  }

  account(uid) {
    const b = this._peekBal(uid);
    let margin = 0n, unreal = 0n, realized = 0n, fees = 0n;
    for (const m of this.markets.values()) {
      const p = this.pos.get(`${uid}:${m.symbol}`);
      if (!p) continue;
      margin += p.margin;
      realized += p.realized;
      fees += p.fees;
      if (p.size !== 0n) unreal += ((this.markPrice(m.symbol) - p.entry) * p.size) / SCALE;
    }
    const wallet = b.free + b.locked + margin;
    return {
      asset: 'USDT', walletBalance: fmt(wallet), available: fmt(b.free), orderMargin: fmt(b.locked),
      positionMargin: fmt(margin), unrealized: fmt(unreal), equity: fmt(wallet + unreal),
      realized: fmt(realized), fees: fmt(fees),
    };
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
        quoteQty: fmt(BigInt(r.quote_qty)), fee: fmt(BigInt(isBuyer ? r.buyer_fee : r.seller_fee)), feeAsset: 'USDT',
        realizedPnl: fmt(BigInt(isBuyer ? r.buyer_pnl : r.seller_pnl)),
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
      filled: fmt(o.filled), quoteFilled: fmt(o.quoteFilled),
      avgPrice: o.filled > 0n ? fmt((o.quoteFilled * SCALE) / o.filled) : null, fee: fmt(o.fee),
      reduceOnly: o.reduceOnly, leverage: o.leverage, realizedPnl: fmt(o.realized), status: o.status,
      created: o.created, updated: o.updated,
    };
  }

  // ---------- аудит інваріантів ----------
  audit() {
    const issues = [];
    // Гроші: вільні + заблоковані + маржа позицій = депозити + реалізований PnL усіх рахунків
    let cash = 0n, margins = 0n, realized = 0n;
    for (const b of this.bal.values()) {
      cash += b.free + b.locked;
      if ((b.free < 0n || b.locked < 0n) && b.uid !== this.feeUid) issues.push(`negative balance uid=${b.uid}`);
    }
    const sizes = new Map();
    for (const p of this.pos.values()) {
      margins += p.margin;
      realized += p.realized;
      sizes.set(p.symbol, (sizes.get(p.symbol) || 0n) + p.size);
      if (p.margin < 0n) issues.push(`negative margin uid=${p.uid} ${p.symbol}`);
      if (p.size === 0n && p.margin !== 0n) issues.push(`margin without position uid=${p.uid} ${p.symbol}`);
    }
    let deposits = 0n;
    for (const r of this.db.prepare("SELECT amount FROM ledger WHERE asset='USDT'").iterate()) deposits += BigInt(r.amount);
    if (cash + margins !== deposits + realized)
      issues.push(`USDT mismatch: cash+margins=${fmt(cash + margins)} deposits+realized=${fmt(deposits + realized)}`);
    // Ф'ючерси — гра з нульовою сумою: сума всіх позицій по парі = 0
    for (const [sym, total] of sizes) if (total !== 0n) issues.push(`open interest imbalance ${sym}: ${fmt(total)}`);
    // Заблоковане = незвільнений залишок блокувань відкритих ордерів
    const needLock = new Map();
    for (const o of this.open.values()) needLock.set(o.uid, (needLock.get(o.uid) || 0n) + o.lock - o.lockRel);
    for (const b of this.bal.values())
      if (b.locked !== (needLock.get(b.uid) || 0n))
        issues.push(`lock mismatch uid=${b.uid}: locked=${fmt(b.locked)} need=${fmt(needLock.get(b.uid) || 0n)}`);
    for (const [sym, b] of this.books) {
      const bid = b.bids.best(), ask = b.asks.best();
      if (bid !== null && ask !== null && bid >= ask) issues.push(`crossed book ${sym}`);
      for (const side of [b.bids, b.asks])
        for (const lvl of side.levels.values()) {
          const sum = lvl.orders.reduce((acc, o) => acc + o.qty - o.filled, 0n);
          if (sum !== lvl.qty) issues.push(`level qty mismatch ${sym} ${fmt(lvl.price)}`);
        }
    }
    return {
      ok: issues.length === 0, issues: issues.slice(0, 50), openOrders: this.open.size,
      supply: { USDT: fmt(cash + margins) }, insuranceFund: fmt(this._peekBal(this.feeUid).free),
    };
  }
}

function s(v) {
  return v === null || v === undefined ? null : v.toString();
}

function rowToOrder(r) {
  return {
    id: r.id, uid: r.user_id, symbol: r.symbol, side: r.side, type: r.type, tif: r.tif,
    price: r.price === null ? null : BigInt(r.price), qty: BigInt(r.qty), filled: BigInt(r.filled),
    quoteFilled: BigInt(r.quote_filled), fee: BigInt(r.fee), reduceOnly: !!r.reduce_only, leverage: r.leverage,
    lock: BigInt(r.lock), lockRel: BigInt(r.lock_released), realized: BigInt(r.realized), status: r.status,
    created: r.created_at, updated: r.updated_at,
  };
}

module.exports = { Engine, ApiError, OPEN };
