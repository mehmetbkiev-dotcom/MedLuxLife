'use strict';
// Адаптер брокера ліквідності для Binance Spot REST API.
// Ціни беруться з основного ринку (публічні дані, без ключів), а ордери
// відправляються на Spot Testnet — там демо-кошти (ключі: https://testnet.binance.vision).
// Інший брокер підключається реалізацією тих самих методів.

const crypto = require('node:crypto');

class BinanceBroker {
  constructor({ apiKey, apiSecret, tradeUrl, priceUrl, timeoutMs = 8000 }) {
    this.name = 'binance';
    this.apiKey = apiKey;
    this.apiSecret = apiSecret;
    this.tradeUrl = tradeUrl.replace(/\/$/, '');
    this.priceUrl = priceUrl.replace(/\/$/, '');
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
    const r = await fetch(`${base}${path}${qs ? '?' + qs : ''}`, {
      method, headers, signal: AbortSignal.timeout(this.timeoutMs),
    });
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

  // Синхронізація годинника і правил торгівлі (крок лоту, мін. сума)
  async init(symbols) {
    const t = await this._req(this.tradeUrl, 'GET', '/api/v3/time');
    this.timeOffset = t.serverTime - Date.now();
    const info = await this._req(this.tradeUrl, 'GET', '/api/v3/exchangeInfo', { symbols: JSON.stringify(symbols) });
    for (const s of info.symbols) {
      const f = Object.fromEntries(s.filters.map((x) => [x.filterType, x]));
      this.filters.set(s.symbol, {
        step: f.LOT_SIZE?.stepSize || '0.00001',
        minQty: f.LOT_SIZE?.minQty || '0',
        minNotional: (f.NOTIONAL || f.MIN_NOTIONAL)?.minNotional || '5',
      });
    }
  }

  // Найкращі bid/ask з реального ринку
  async bookTickers(symbols) {
    const rows = await this._req(this.priceUrl, 'GET', '/api/v3/ticker/bookTicker', { symbols: JSON.stringify(symbols) });
    const out = new Map();
    for (const r of rows) out.set(r.symbol, { bid: r.bidPrice, ask: r.askPrice });
    return out;
  }

  async marketOrder(symbol, side, qty, clientId) {
    try {
      return norm(await this._req(this.tradeUrl, 'POST', '/api/v3/order', {
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
      return norm(await this._req(this.tradeUrl, 'GET', '/api/v3/order', { symbol, origClientOrderId: clientId }, true));
    } catch (e) {
      if (e.code === -2013) return null; // ордер не існує
      throw e;
    }
  }

  async balances() {
    const a = await this._req(this.tradeUrl, 'GET', '/api/v3/account', { omitZeroBalances: 'true' }, true);
    return a.balances.map((b) => ({ asset: b.asset, free: b.free, locked: b.locked }));
  }
}

function norm(o) {
  return {
    brokerOrderId: String(o.orderId),
    status: o.status,
    executedQty: o.executedQty,
    quoteQty: o.cummulativeQuoteQty,
  };
}

module.exports = { BinanceBroker };
