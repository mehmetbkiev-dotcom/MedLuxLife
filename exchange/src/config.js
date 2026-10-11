'use strict';
const path = require('node:path');

const env = process.env;
const m = (base, tick, step, refPrice) => ({ symbol: `${base}USDT`, base, quote: 'USDT', tick, step, minNotional: '5', refPrice });

const config = {
  port: Number(env.PORT) || 8080,
  host: env.HOST || '0.0.0.0',
  dbFile: env.DB_FILE || path.join(__dirname, '..', 'data', 'exchange.db'),

  // Комісії в базисних пунктах (10 bps = 0.1%)
  makerFeeBps: BigInt(env.MAKER_FEE_BPS || 10),
  takerFeeBps: BigInt(env.TAKER_FEE_BPS || 10),
  // Ринковий ордер не виконується далі ніж на 5% від найкращої ціни на момент подачі
  marketProtectionBps: BigInt(env.MARKET_PROTECTION_BPS || 500),
  maxOpenOrdersPerUser: 200,

  // 20 найпопулярніших монет до USDT. Крок ціни (tick) і кількості (step) — як на Binance.
  // refPrice — лише стартова ціна без брокера; з брокером береться реальна.
  markets: [
    m('BTC', '0.01', '0.00001', '85000'),
    m('ETH', '0.01', '0.0001', '2500'),
    m('BNB', '0.01', '0.001', '600'),
    m('SOL', '0.01', '0.001', '150'),
    m('XRP', '0.0001', '0.1', '2'),
    m('DOGE', '0.00001', '1', '0.15'),
    m('ADA', '0.0001', '0.1', '0.6'),
    m('TRX', '0.0001', '0.1', '0.25'),
    m('TON', '0.001', '0.01', '3'),
    m('AVAX', '0.01', '0.01', '20'),
    m('LINK', '0.01', '0.01', '15'),
    m('DOT', '0.001', '0.01', '4'),
    m('LTC', '0.01', '0.001', '80'),
    m('BCH', '0.1', '0.001', '400'),
    m('SHIB', '0.00000001', '1', '0.000012'),
    m('NEAR', '0.001', '0.1', '2.5'),
    m('UNI', '0.001', '0.01', '7'),
    m('APT', '0.001', '0.01', '5'),
    m('SUI', '0.0001', '0.1', '3'),
    m('PEPE', '0.00000001', '1', '0.00001'),
  ],

  // Демо-баланс при реєстрації і "кран" для поповнення
  signupBonus: { USDT: '10000', BTC: '0.1', ETH: '2' },
  faucet: { USDT: '1000' },
  faucetCooldownMs: 60 * 60 * 1000,

  bots: env.BOTS !== '0',

  // Брокер ліквідності. BROKER=binance вмикає реальні ціни; з ключами API — ще й
  // дублювання угод користувачів на демо-рахунок (Binance Spot Testnet).
  broker: {
    name: env.BROKER || null,
    apiKey: env.BINANCE_API_KEY || null,
    apiSecret: env.BINANCE_API_SECRET || null,
    tradeUrl: env.BINANCE_TRADE_URL || 'https://testnet.binance.vision',
    priceUrl: env.BINANCE_PRICE_URL || 'https://data-api.binance.vision',
    allowLive: env.BROKER_ALLOW_LIVE === '1', // захист від випадкової торгівлі реальними грошима
    priceIntervalMs: 1000,
    hedgeIntervalMs: Number(env.HEDGE_INTERVAL_MS) || 1000,
  },
  trustProxy: env.TRUST_PROXY === '1',
  // Ніколи не давати запитам з 127.0.0.1 привілеїв (адмінка без пароля, без лімітів).
  // Вмикається в беті: тунелі на кшталт ssh -R не завжди додають заголовки пересилання.
  noLocalTrust: env.NO_LOCAL_TRUST === '1',
  cookieSecure: env.COOKIE_SECURE === '1',
  adminToken: env.ADMIN_TOKEN || null,
  sessionTtlMs: 30 * 24 * 3600 * 1000,
};
config.assets = ['USDT', ...config.markets.map((x) => x.base)];

module.exports = config;
