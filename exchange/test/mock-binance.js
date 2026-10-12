'use strict';
// Мінімальний мок Binance Spot API для тестів: перевіряє HMAC-підпис, виконує
// ринкові ордери повністю, вміє імітувати обрив з'єднання після прийому ордера.
const http = require('node:http');
const crypto = require('node:crypto');

function startMockBinance({ key = 'k', secret = 's' } = {}) {
  const state = { orders: [], dropNext: false, rejectNext: null, prices: { BTCUSDT: ['100000.00', '100001.00'], ETHUSDT: ['4000.00', '4000.50'] } };
  const json = (res, code, body) => res.writeHead(code, { 'Content-Type': 'application/json' }).end(JSON.stringify(body));
  const server = http.createServer((req, res) => {
    const u = new URL(req.url, 'http://x');
    const p = Object.fromEntries(u.searchParams);
    // ф'ючерсні шляхи (/fapi/v1/...) обробляємо тими самими гілками, що й спотові
    const futures = u.pathname.startsWith('/fapi/');
    const path = u.pathname.replace('/fapi/v2/balance', '/api/v3/account').replace('/fapi/v1/', '/api/v3/');
    const signed = ['/api/v3/order', '/api/v3/account'].includes(path);
    if (signed) {
      const qs = u.search.slice(1).replace(/&signature=[0-9a-f]+$/, '');
      const sig = crypto.createHmac('sha256', secret).update(qs).digest('hex');
      if (req.headers['x-mbx-apikey'] !== key || p.signature !== sig) return json(res, 401, { code: -1022, msg: 'Signature invalid' });
    }
    if (path === '/api/v3/time') return json(res, 200, { serverTime: Date.now() });
    if (path === '/api/v3/exchangeInfo')
      return json(res, 200, { symbols: (p.symbols ? JSON.parse(p.symbols) : Object.keys(state.prices)).map((s) => ({ symbol: s, status: 'TRADING', filters: [
        { filterType: 'LOT_SIZE', minQty: s === 'BTCUSDT' ? '0.00001000' : '0.00010000', stepSize: s === 'BTCUSDT' ? '0.00001000' : '0.00010000' },
        { filterType: 'NOTIONAL', minNotional: '5.00000000' }] })) });
    if (path === '/api/v3/ticker/bookTicker')
      return json(res, 200, (p.symbols ? JSON.parse(p.symbols) : Object.keys(state.prices)).map((s) => ({ symbol: s, bidPrice: (state.prices[s] || ['1.0000'])[0], askPrice: (state.prices[s] || [, '1.0001'])[1] })));
    if (path === '/api/v3/klines') {
      const ms = { '1m': 60e3, '5m': 300e3, '15m': 900e3, '1h': 3600e3, '4h': 14400e3, '1d': 86400e3 }[p.interval];
      const n = Number(p.limit) || 300;
      let px = Number((state.prices[p.symbol] || ['1'])[0]);
      const now = Date.now() - (Date.now() % ms);
      const out = [];
      for (let i = 0; i < n; i++) {
        const o = px;
        const c = o * (1 + (Math.random() - 0.5) * 0.004);
        out.unshift([now - i * ms, c.toFixed(2), (Math.max(o, c) * 1.001).toFixed(2), (Math.min(o, c) * 0.999).toFixed(2), o.toFixed(2), (Math.random() * 50).toFixed(5)]);
        px = c;
      }
      return json(res, 200, out.map((r) => [r[0], r[4], r[2], r[3], r[1], r[5], r[0] + ms - 1]));
    }
    if (path === '/api/v3/account')
      return futures
        ? json(res, 200, [{ asset: 'USDT', balance: '15000.00', availableBalance: '10000.00' }])
        : json(res, 200, { balances: [{ asset: 'USDT', free: '10000.00', locked: '0.00' }] });
    if (path === '/api/v3/order' && req.method === 'GET') {
      const o = state.orders.find((x) => x.clientOrderId === p.origClientOrderId);
      return o ? json(res, 200, o) : json(res, 400, { code: -2013, msg: 'Order does not exist.' });
    }
    if (path === '/api/v3/order' && req.method === 'POST') {
      if (state.rejectNext) {
        const msg = state.rejectNext;
        state.rejectNext = null;
        return json(res, 400, { code: -2010, msg });
      }
      if (state.orders.some((x) => x.clientOrderId === p.newClientOrderId)) return json(res, 400, { code: -2010, msg: 'Duplicate order sent.' });
      const px = Number(state.prices[p.symbol][p.side === 'BUY' ? 1 : 0]);
      const o = { symbol: p.symbol, orderId: state.orders.length + 1, clientOrderId: p.newClientOrderId, side: p.side, status: 'FILLED',
        executedQty: Number(p.quantity).toFixed(8), cummulativeQuoteQty: (Number(p.quantity) * px).toFixed(8),
        cumQuote: (Number(p.quantity) * px).toFixed(8) };
      state.orders.push(o);
      if (state.dropNext) {
        state.dropNext = false;
        return req.socket.destroy(); // ордер прийнято, але відповідь загубилась
      }
      return json(res, 200, o);
    }
    json(res, 404, { msg: 'not found' });
  });
  return new Promise((resolve) => server.listen(0, '127.0.0.1', () => resolve({ server, state, url: `http://127.0.0.1:${server.address().port}` })));
}

module.exports = { startMockBinance };
