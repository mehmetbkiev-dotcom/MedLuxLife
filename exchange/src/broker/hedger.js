'use strict';
// Дублювання угод користувачів у брокера (на демо-рахунку).
//
// Кожна угода, де бере участь реальний користувач (не бот), змінює "чисту позицію"
// клієнтів по парі: користувач купив 0.01 BTC → біржа має купити 0.01 BTC у брокера.
// Угоди накопичуються і раз на секунду відправляються одним ринковим ордером
// (так не впираємось у ліміти API, а дрібні угоди нижче мінімальної суми брокера
// не губляться — вони чекають, поки набереться мінімум).
//
// Стан відновлюється після рестарту з таблиць trades і broker_orders, тож жодна угода
// не буде продубльована двічі або пропущена.

const { toUnits, fmt, SCALE } = require('../decimal');

class Hedger {
  constructor(db, engine, broker, cfg) {
    this.db = db;
    this.engine = engine;
    this.broker = broker;
    this.cfg = cfg;
    this.symbols = [...engine.markets.values()].map((m) => ({ symbol: m.symbol, brokerSymbol: m.brokerSymbol || m.symbol }));
    this.pending = new Map(this.symbols.map((s) => [s.symbol, 0n])); // + купити у брокера, − продати
    // Для звірки: userNet (чиста позиція клієнтів) = hedged (виконано у брокера) + pending
    this.userNet = new Map(this.symbols.map((s) => [s.symbol, 0n]));
    this.hedged = new Map(this.symbols.map((s) => [s.symbol, 0n]));
    this.inflight = new Set();
    this.inflightIds = new Set();
    this.backoffUntil = new Map();
    this.prices = new Map(); // symbol -> { bid, ask, mid, ts }
    this.kinds = new Map();
    this.lastError = null;
    this.brokerBalances = null;
    this.ready = false;
    this.timers = [];

    db.exec(`
      CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS broker_orders (
        id INTEGER PRIMARY KEY,
        symbol TEXT NOT NULL,
        side TEXT NOT NULL,
        qty TEXT NOT NULL,
        status TEXT NOT NULL,            -- SENDING | FILLED | PARTIALLY_FILLED | REJECTED | UNKNOWN | ...
        executed_qty TEXT NOT NULL DEFAULT '0',
        quote_qty TEXT NOT NULL DEFAULT '0',
        broker_order_id TEXT,
        error TEXT,
        created_at INTEGER NOT NULL,
        updated_at INTEGER NOT NULL
      );`);
    this.st = {
      insert: db.prepare("INSERT INTO broker_orders(symbol, side, qty, status, created_at, updated_at) VALUES(?,?,?,'SENDING',?,?)"),
      update: db.prepare('UPDATE broker_orders SET status=?, executed_qty=?, quote_qty=?, broker_order_id=?, error=?, updated_at=? WHERE id=?'),
      recent: db.prepare('SELECT * FROM broker_orders ORDER BY id DESC LIMIT ?'),
      unresolved: db.prepare("SELECT * FROM broker_orders WHERE status IN ('SENDING','UNKNOWN')"),
    };

    // Хеджуються тільки угоди після першого ввімкнення брокера
    let start = db.prepare("SELECT v FROM kv WHERE k='hedge_start_trade_id'").get();
    if (!start) {
      const v = String(engine.nextTradeId - 1);
      db.prepare("INSERT INTO kv(k, v) VALUES('hedge_start_trade_id', ?)").run(v);
      start = { v };
    }
    this._rebuild(Number(start.v));
  }

  _rebuild(startId) {
    const userIds = new Set(this.db.prepare("SELECT id FROM users WHERE kind='user'").all().map((r) => r.id));
    for (const r of this.db.prepare('SELECT symbol, qty, buyer_id, seller_id FROM trades WHERE id>?').iterate(startId)) {
      if (!this.pending.has(r.symbol)) continue;
      const q = BigInt(r.qty);
      let d = 0n;
      if (userIds.has(r.buyer_id)) d += q;
      if (userIds.has(r.seller_id)) d -= q;
      this._add('pending', r.symbol, d);
      this._add('userNet', r.symbol, d);
    }
    // Відправлене брокеру (і ордери в невизначеному стані — вважаємо, що вони пройшли
    // на повну кількість, доки звірка не покаже інше)
    for (const r of this.db.prepare('SELECT symbol, side, qty, status, executed_qty FROM broker_orders').iterate()) {
      if (!this.pending.has(r.symbol)) continue;
      const q = r.status === 'SENDING' || r.status === 'UNKNOWN' ? BigInt(r.qty) : BigInt(r.executed_qty);
      const signed = r.side === 'BUY' ? q : -q;
      this._add('pending', r.symbol, -signed);
      this._add('hedged', r.symbol, signed);
    }
  }

  _add(map, symbol, d) {
    this[map].set(symbol, this[map].get(symbol) + d);
  }

  _isUser(uid) {
    let k = this.kinds.get(uid);
    if (k === undefined) {
      k = this.db.prepare('SELECT kind FROM users WHERE id=?').get(uid)?.kind || 'unknown';
      this.kinds.set(uid, k);
    }
    return k === 'user';
  }

  // Викликається для кожної угоди після запису в БД
  onTrade(t) {
    if (!this.pending.has(t.symbol)) return;
    let d = 0n;
    if (this._isUser(t.buyer)) d += t.qty;
    if (this._isUser(t.seller)) d -= t.qty;
    if (d) {
      this._add('pending', t.symbol, d);
      this._add('userNet', t.symbol, d);
    }
  }

  async start() {
    const loopPrices = async () => {
      try {
        const map = await this.broker.bookTickers(this.symbols.map((s) => s.brokerSymbol));
        for (const s of this.symbols) {
          const p = map.get(s.brokerSymbol);
          if (p) this.prices.set(s.symbol, { bid: p.bid, ask: p.ask, mid: (Number(p.bid) + Number(p.ask)) / 2, ts: Date.now() });
        }
      } catch (e) {
        this._err('prices', e);
      }
    };
    await loopPrices();
    this.timers.push(setInterval(loopPrices, this.cfg.priceIntervalMs));
    if (!this.broker.canTrade) {
      console.log('Брокер: ключі API не задані — лише ціни, без дублювання угод');
      return;
    }
    const init = async () => {
      try {
        await this.broker.init(this.symbols.map((s) => s.brokerSymbol));
        await this._reconcile();
        this.ready = true;
        console.log(`Брокер ${this.broker.name}: підключено, дублювання угод увімкнено (${this.broker.tradeUrl})`);
      } catch (e) {
        this._err('init', e);
        setTimeout(init, 10000);
      }
    };
    await init();
    this.timers.push(setInterval(() => this.ready && this.tick(), this.cfg.hedgeIntervalMs));
    const loadBal = async () => {
      try {
        this.brokerBalances = await this.broker.balances();
      } catch (e) {
        this._err('balances', e);
      }
    };
    loadBal();
    this.timers.push(setInterval(loadBal, 30000));
  }

  stop() {
    for (const t of this.timers) clearInterval(t);
  }

  _err(where, e) {
    const prev = this.lastError;
    this.lastError = { where, message: e.message, ts: Date.now() };
    // однакову помилку (напр. брокер недоступний) пишемо в лог не частіше ніж раз на хвилину
    if (prev && prev.where === where && prev.message === e.message && Date.now() - (this._loggedAt || 0) < 60000) return;
    this._loggedAt = Date.now();
    console.error(`Брокер [${where}]: ${e.message}`);
  }

  // Ордери, статус яких невідомий (обрив зв'язку / падіння процесу) — звіряємо з брокером
  async _reconcile() {
    for (const r of this.st.unresolved.all()) {
      const s = this.symbols.find((x) => x.symbol === r.symbol);
      if (!s || this.inflightIds.has(r.id)) continue; // ще чекаємо відповідь — не чіпаємо
      const o = await this.broker.findOrder(s.brokerSymbol, `mx${r.id}`);
      const pendingBefore = BigInt(r.qty);
      let executed = 0n;
      if (o) {
        executed = toUnits(o.executedQty) ?? 0n;
        this.st.update.run(o.status, executed.toString(), (toUnits(o.quoteQty) ?? 0n).toString(), o.brokerOrderId, null, Date.now(), r.id);
      } else {
        this.st.update.run('NOT_FOUND', '0', '0', null, 'ордер не дійшов до брокера', Date.now(), r.id);
      }
      // При rebuild ми вважали, що виконано pendingBefore; коригуємо на фактичне
      const corr = r.side === 'BUY' ? pendingBefore - executed : executed - pendingBefore;
      this._add('pending', r.symbol, corr);
      this._add('hedged', r.symbol, -corr);
    }
  }

  async tick() {
    for (const s of this.symbols) {
      if (this.inflight.has(s.symbol) || (this.backoffUntil.get(s.symbol) || 0) > Date.now()) continue;
      const f = this.broker.filters.get(s.brokerSymbol);
      const px = this.prices.get(s.symbol);
      if (!f || !px) continue;
      const net = this.pending.get(s.symbol);
      const step = toUnits(f.step) || 1n;
      let qty = net < 0n ? -net : net;
      qty -= qty % step;
      if (qty === 0n || qty < (toUnits(f.minQty) || 0n)) continue;
      if (Number(fmt(qty)) * px.mid < Number(f.minNotional) * 1.05) continue; // ще замало — чекаємо
      this._send(s, net > 0n ? 'BUY' : 'SELL', qty);
    }
  }

  async _send(s, side, qty) {
    this.inflight.add(s.symbol);
    const signed = side === 'BUY' ? qty : -qty;
    // Спершу фіксуємо намір у БД, потім шлемо — так після падіння нічого не задублюється
    const now = Date.now();
    const id = Number(this.st.insert.run(s.symbol, side, qty.toString(), now, now).lastInsertRowid);
    this.inflightIds.add(id);
    this._add('pending', s.symbol, -signed);
    this._add('hedged', s.symbol, signed); // вважаємо виконаним, коригуємо за фактом
    try {
      const o = await this.broker.marketOrder(s.brokerSymbol, side, fmt(qty), `mx${id}`);
      const executed = toUnits(o.executedQty) ?? 0n;
      this.st.update.run(o.status, executed.toString(), (toUnits(o.quoteQty) ?? 0n).toString(), o.brokerOrderId, null, Date.now(), id);
      if (executed !== qty) {
        const rest = side === 'BUY' ? qty - executed : executed - qty; // невиконане повертаємо в чергу
        this._add('pending', s.symbol, rest);
        this._add('hedged', s.symbol, -rest);
      }
    } catch (e) {
      if (e.status) {
        // Брокер однозначно відхилив (брак коштів, ліміти...) — повертаємо в чергу і чекаємо
        this.st.update.run('REJECTED', '0', '0', null, e.message.slice(0, 300), Date.now(), id);
        this._add('pending', s.symbol, signed);
        this._add('hedged', s.symbol, -signed);
        this.backoffUntil.set(s.symbol, Date.now() + 15000);
      } else {
        // Зв'язок обірвався і ордер не знайдено — статус невідомий, звіримо пізніше
        this.st.update.run('UNKNOWN', '0', '0', null, e.message.slice(0, 300), Date.now(), id);
        this.backoffUntil.set(s.symbol, Date.now() + 10000);
        setTimeout(() => this._reconcile().catch((err) => this._err('reconcile', err)), 10000);
      }
      this._err('order', e);
    } finally {
      this.inflight.delete(s.symbol);
      this.inflightIds.delete(id);
    }
  }

  // Ціна з реального ринку для маркетмейкера (null, якщо дані застарілі)
  mid(symbol) {
    const p = this.prices.get(symbol);
    return p && Date.now() - p.ts < 15000 ? p.mid : null;
  }

  status() {
    const o = {};
    for (const s of this.symbols) {
      const p = this.prices.get(s.symbol);
      o[s.symbol] = {
        brokerSymbol: s.brokerSymbol,
        brokerBid: p?.bid ?? null, brokerAsk: p?.ask ?? null, priceAgeSec: p ? Math.round((Date.now() - p.ts) / 1000) : null,
        ourLast: fmt(this.engine.last.get(s.symbol)),
        pendingToHedge: fmt(this.pending.get(s.symbol)),
        clientsNetPosition: fmt(this.userNet.get(s.symbol)),
        hedgedAtBroker: fmt(this.hedged.get(s.symbol)),
        reconciled: this.userNet.get(s.symbol) === this.hedged.get(s.symbol) + this.pending.get(s.symbol),
        filters: this.broker.filters.get(s.brokerSymbol) || null,
      };
    }
    return {
      broker: this.broker.name, tradeUrl: this.broker.tradeUrl, priceUrl: this.broker.priceUrl,
      mirroring: this.broker.canTrade, connected: this.ready, lastError: this.lastError,
      markets: o, brokerBalances: this.brokerBalances,
      recentOrders: this.st.recent.all(30).map((r) => ({
        id: r.id, symbol: r.symbol, side: r.side, qty: fmt(BigInt(r.qty)), status: r.status,
        executedQty: fmt(BigInt(r.executed_qty)), quoteQty: fmt(BigInt(r.quote_qty)),
        avgPrice: BigInt(r.executed_qty) > 0n ? fmt((BigInt(r.quote_qty) * SCALE) / BigInt(r.executed_qty)) : null,
        brokerOrderId: r.broker_order_id, error: r.error, ts: r.created_at,
      })),
    };
  }
}

module.exports = { Hedger };
