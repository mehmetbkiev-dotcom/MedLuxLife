'use strict';
const path = require('node:path');

const env = process.env;

module.exports = {
  port: Number(env.PORT) || 8080,
  host: env.HOST || '0.0.0.0',
  dbFile: env.DB_FILE || path.join(__dirname, '..', 'data', 'exchange.db'),

  // Комісії в базисних пунктах (10 bps = 0.1%)
  makerFeeBps: BigInt(env.MAKER_FEE_BPS || 10),
  takerFeeBps: BigInt(env.TAKER_FEE_BPS || 10),
  // Ринковий ордер не виконується далі ніж на 5% від найкращої ціни на момент подачі
  marketProtectionBps: BigInt(env.MARKET_PROTECTION_BPS || 500),
  maxOpenOrdersPerUser: 200,

  assets: ['USDT', 'BTC', 'ETH'],
  markets: [
    { symbol: 'BTCUSDT', base: 'BTC', quote: 'USDT', tick: '0.01', step: '0.00001', minNotional: '5', refPrice: '60000' },
    { symbol: 'ETHUSDT', base: 'ETH', quote: 'USDT', tick: '0.01', step: '0.0001', minNotional: '5', refPrice: '3000' },
  ],

  // Демо-баланс при реєстрації і "кран" для поповнення
  signupBonus: { USDT: '10000', BTC: '0.1', ETH: '2' },
  faucet: { USDT: '1000' },
  faucetCooldownMs: 60 * 60 * 1000,

  bots: env.BOTS !== '0',
  trustProxy: env.TRUST_PROXY === '1',
  cookieSecure: env.COOKIE_SECURE === '1',
  adminToken: env.ADMIN_TOKEN || null,
  sessionTtlMs: 30 * 24 * 3600 * 1000,
};
