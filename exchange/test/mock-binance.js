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
    const signed = ['/api/v3/order', '/api/v3/account'].includes(u.pathname);
    if (signed) {
      const qs = u.search.slice(1).replace(/&signature=[0-9a-f]+$/, '');
      const sig = crypto.createHmac('sha256', secret).update(qs).digest('hex');
      if (req.headers['x-mbx-apikey'] !== key || p.signature !== sig) return json(res, 401, { code: -1022, msg: 'Signature invalid' });
    }
    if (u.pathname === '/api/v3/time') return json(res, 200, { serverTime: Date.now() });
    if (u.pathname === '/api/v3/exchangeInfo')
      return json(res, 200, { symbols: JSON.parse(p.symbols).map((s) => ({ symbol: s, filters: [
        { filterType: 'LOT_SIZE', minQty: s === 'BTCUSDT' ? '0.00001000' : '0.00010000', stepSize: s === 'BTCUSDT' ? '0.00001000' : '0.00010000' },
        { filterType: 'NOTIONAL', minNotional: '5.00000000' }] })) });
    if (u.pathname === '/api/v3/ticker/bookTicker')
      return json(res, 200, JSON.parse(p.symbols).map((s) => ({ symbol: s, bidPrice: state.prices[s][0], askPrice: state.prices[s][1] })));
    if (u.pathname === '/api/v3/account') return json(res, 200, { balances: [{ asset: 'USDT', free: '10000.00', locked: '0.00' }] });
    if (u.pathname === '/api/v3/order' && req.method === 'GET') {
      const o = state.orders.find((x) => x.clientOrderId === p.origClientOrderId);
      return o ? json(res, 200, o) : json(res, 400, { code: -2013, msg: 'Order does not exist.' });
    }
    if (u.pathname === '/api/v3/order' && req.method === 'POST') {
      if (state.rejectNext) {
        const msg = state.rejectNext;
        state.rejectNext = null;
        return json(res, 400, { code: -2010, msg });
      }
      if (state.orders.some((x) => x.clientOrderId === p.newClientOrderId)) return json(res, 400, { code: -2010, msg: 'Duplicate order sent.' });
      const px = Number(state.prices[p.symbol][p.side === 'BUY' ? 1 : 0]);
      const o = { symbol: p.symbol, orderId: state.orders.length + 1, clientOrderId: p.newClientOrderId, side: p.side, status: 'FILLED',
        executedQty: Number(p.quantity).toFixed(8), cummulativeQuoteQty: (Number(p.quantity) * px).toFixed(8) };
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
