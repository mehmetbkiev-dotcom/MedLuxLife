'use strict';
// Адаптер брокера ліквідності: Binance USDT-M Futures REST API.
//  - Ціни й історія свічок — з реального ф'ючерсного ринку (публічні дані, без ключів);
//    якщо fapi.binance.com недоступний, — зі спотового ринку (для 1000SHIB/1000PEPE
//    перераховуємо ціну спотової монети ×1000).
//  - Ордери (дублювання позицій користувачів) — на Binance Futures Testnet, де демо-кошти.
//    Ключі: https://testnet.binancefuture.com → API Key.
// Інший брокер підключається реалізацією тих самих методів.

const crypto = require('node:crypto');

// 1000SHIBUSDT (ф'ючерс) ↔ SHIBUSDT (спот) з множником 1000
const spotOf = (sym) => {
  const m = sym.match(/^(\d+)([A-Z]+USDT)$/);
  return m ? { symbol: m[2], mult: Number(m[1]) } : { symbol: sym, mult: 1 };
};

class BinanceBroker {
  constructor({ apiKey, apiSecret, tradeUrl, priceUrl, spotPriceUrl, timeoutMs = 8000 }) {
    this.name = 'binance-futures';
    this.apiKey = apiKey;
    this.apiSecret = apiSecret;
    this.tradeUrl = tradeUrl.replace(/\/$/, '');
    this.priceUrl = priceUrl.replace(/\/$/, '');
    this.spotPriceUrl = (spotPriceUrl || 'https://data-api.binance.vision').replace(/\/$/, '');
    this.useSpotPrices = false;
    this.timeoutMs = timeoutMs;
    this.timeOffset = 0;
    this.filters = new Map(); // symbol -> { step, minQty, minNotional }
  }

  get canTrade() {
    return Boolean(this.apiKey && this.apiSecret);
  }

  async _req(base, method, path, params = {}, signed = false) {
    const q = new URLSearchParams();
    for (const [k, v] of Object.entries(params)) if (v !== undefined && v !== null) q.set(k, String(v));
    const headers = {};
    if (signed) {
      q.set('recvWindow', '10000');
      q.set('timestamp', String(Date.now() + this.timeOffset));
      q.set('signature', crypto.createHmac('sha256', this.apiSecret).update(q.toString()).digest('hex'));
      headers['X-MBX-APIKEY'] = this.apiKey;
    }
    const qs = q.toString();
    const r = await fetch(`${base}${path}${qs ? '?' + qs : ''}`, { method, headers, signal: AbortSignal.timeout(this.timeoutMs) });
    const text = await r.text();
    let data;
    try {
      data = JSON.parse(text);
    } catch {
      data = { msg: text.slice(0, 200) };
    }
    if (!r.ok) {
      const e = new Error(`Binance ${r.status}: ${data.msg || text.slice(0, 200)}`);
      e.status = r.status;
      e.code = data.code;
      throw e;
    }
    return data;
  }

  // Синхронізація годинника і правил торгівлі (крок лоту, мін. обсяг) на ф'ючерсному тестнеті
  async init(symbols) {
    const t = await this._req(this.tradeUrl, 'GET', '/fapi/v1/time');
    this.timeOffset = t.serverTime - Date.now();
    const info = await this._req(this.tradeUrl, 'GET', '/fapi/v1/exchangeInfo');
    const want = new Set(symbols);
    for (const s of info.symbols) {
      if (!want.has(s.symbol) || (s.status && s.status !== 'TRADING')) continue;
      const f = Object.fromEntries(s.filters.map((x) => [x.filterType, x]));
      const lot = f.MARKET_LOT_SIZE || f.LOT_SIZE;
      this.filters.set(s.symbol, {
        step: lot?.stepSize || '0.001',
        minQty: lot?.minQty || '0',
        minNotional: f.MIN_NOTIONAL?.notional || f.MIN_NOTIONAL?.minNotional || '5',
      });
    }
  }

  // Найкращі bid/ask з реального ринку
  async bookTickers(symbols) {
    const out = new Map();
    if (!this.useSpotPrices) {
      try {
        const rows = await this._req(this.priceUrl, 'GET', '/fapi/v1/ticker/bookTicker');
        const want = new Set(symbols);
        for (const r of rows) if (want.has(r.symbol)) out.set(r.symbol, { bid: r.bidPrice, ask: r.askPrice });
        return out;
      } catch (e) {
        // ф'ючерсний API недоступний (обмеження за регіоном) — переходимо на спотові ціни
        if (e.status && e.status !== 451 && e.status !== 403) throw e;
        this.useSpotPrices = true;
        console.error(`Брокер: ф'ючерсні ціни недоступні (${e.message}) — беру ціни зі спотового ринку Binance`);
      }
    }
    const map = new Map(symbols.map((s) => [spotOf(s).symbol, s]));
    const rows = await this._req(this.spotPriceUrl, 'GET', '/api/v3/ticker/bookTicker', { symbols: JSON.stringify([...map.keys()]) });
    for (const r of rows) {
      const fut = map.get(r.symbol);
      const k = spotOf(fut).mult;
      out.set(fut, { bid: String(Number(r.bidPrice) * k), ask: String(Number(r.askPrice) * k) });
    }
    return out;
  }

  // Історія свічок з реального ринку: [[openTime, o, h, l, c, v], ...]
  async klines(symbol, interval, limit) {
    if (!this.useSpotPrices) {
      try {
        const rows = await this._req(this.priceUrl, 'GET', '/fapi/v1/klines', { symbol, interval, limit });
        return rows.map((r) => [r[0], strip(r[1]), strip(r[2]), strip(r[3]), strip(r[4]), strip(r[5])]);
      } catch (e) {
        if (e.status && e.status !== 451 && e.status !== 403) throw e;
        this.useSpotPrices = true;
      }
    }
    const { symbol: sp, mult } = spotOf(symbol);
    const rows = await this._req(this.spotPriceUrl, 'GET', '/api/v3/klines', { symbol: sp, interval, limit });
    const px = (v) => strip((Number(v) * mult).toFixed(10));
    return rows.map((r) => [r[0], px(r[1]), px(r[2]), px(r[3]), px(r[4]), strip((Number(r[5]) / mult).toFixed(8))]);
  }

  async marketOrder(symbol, side, qty, clientId) {
    try {
      return norm(await this._req(this.tradeUrl, 'POST', '/fapi/v1/order', {
        symbol, side, type: 'MARKET', quantity: qty, newClientOrderId: clientId, newOrderRespType: 'RESULT',
      }, true));
    } catch (e) {
      // Таймаут / обрив зв'язку: ордер міг дійти до біржі — перевіряємо за нашим id
      if (e.status) throw e;
      const found = await this.findOrder(symbol, clientId).catch(() => null);
      if (found) return found;
      throw e;
    }
  }

  async findOrder(symbol, clientId) {
    try {
      return norm(await this._req(this.tradeUrl, 'GET', '/fapi/v1/order', { symbol, origClientOrderId: clientId }, true));
    } catch (e) {
      if (e.code === -2013) return null; // ордер не існує
      throw e;
    }
  }

  async balances() {
    const rows = await this._req(this.tradeUrl, 'GET', '/fapi/v2/balance', {}, true);
    return rows
      .filter((b) => Number(b.balance) !== 0)
      .map((b) => ({ asset: b.asset, free: b.availableBalance, locked: String(Number(b.balance) - Number(b.availableBalance)) }));
  }
}

const strip = (v) => String(v).replace(/(\.\d*?)0+$/, '$1').replace(/\.$/, '');

function norm(o) {
  return {
    brokerOrderId: String(o.orderId),
    status: o.status,
    executedQty: o.executedQty,
    quoteQty: o.cumQuote ?? o.cummulativeQuoteQty ?? '0',
  };
}

module.exports = { BinanceBroker };
