'use strict';
const fs = require('node:fs');
const path = require('node:path');
const { DatabaseSync } = require('node:sqlite');

function openDb(file) {
  if (file !== ':memory:') fs.mkdirSync(path.dirname(file), { recursive: true });
  const db = new DatabaseSync(file);
  db.exec(`
    PRAGMA journal_mode = WAL;
    PRAGMA synchronous = NORMAL;
    PRAGMA busy_timeout = 5000;

    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY,
      username TEXT NOT NULL UNIQUE COLLATE NOCASE,
      pass_hash TEXT NOT NULL,
      kind TEXT NOT NULL DEFAULT 'user',          -- user | system | bot
      created_at INTEGER NOT NULL
    );
    CREATE TABLE IF NOT EXISTS sessions (
      token_hash TEXT PRIMARY KEY,
      user_id INTEGER NOT NULL,
      expires_at INTEGER NOT NULL
    );
    CREATE TABLE IF NOT EXISTS balances (
      user_id INTEGER NOT NULL,
      asset TEXT NOT NULL,                       -- лише USDT (маржа)
      free TEXT NOT NULL,
      locked TEXT NOT NULL,                      -- заблоковано під відкриті ордери
      PRIMARY KEY (user_id, asset)
    );
    -- Ф'ючерсні позиції (one-way, ізольована маржа): size > 0 лонг, < 0 шорт
    CREATE TABLE IF NOT EXISTS fpositions (
      user_id INTEGER NOT NULL,
      symbol TEXT NOT NULL,
      size TEXT NOT NULL,
      entry TEXT NOT NULL,
      margin TEXT NOT NULL,
      leverage INTEGER NOT NULL,
      realized TEXT NOT NULL,
      fees TEXT NOT NULL,
      PRIMARY KEY (user_id, symbol)
    );
    CREATE TABLE IF NOT EXISTS orders (
      id INTEGER PRIMARY KEY,
      user_id INTEGER NOT NULL,
      symbol TEXT NOT NULL,
      side TEXT NOT NULL,
      type TEXT NOT NULL,                        -- LIMIT | MARKET | LIMIT_MAKER | LIQUIDATION
      tif TEXT,
      price TEXT,
      qty TEXT NOT NULL,
      filled TEXT NOT NULL,
      quote_filled TEXT NOT NULL,
      fee TEXT NOT NULL,
      reduce_only INTEGER NOT NULL,
      leverage INTEGER NOT NULL,
      lock TEXT NOT NULL,
      lock_released TEXT NOT NULL,
      realized TEXT NOT NULL,
      status TEXT NOT NULL,
      created_at INTEGER NOT NULL,
      updated_at INTEGER NOT NULL
    );
    CREATE INDEX IF NOT EXISTS orders_user ON orders(user_id, id);
    CREATE INDEX IF NOT EXISTS orders_open ON orders(status) WHERE status IN ('NEW','PARTIALLY_FILLED');
    CREATE TABLE IF NOT EXISTS trades (
      id INTEGER PRIMARY KEY,
      symbol TEXT NOT NULL,
      price TEXT NOT NULL,
      qty TEXT NOT NULL,
      quote_qty TEXT NOT NULL,
      buy_order_id INTEGER NOT NULL,
      sell_order_id INTEGER NOT NULL,
      buyer_id INTEGER NOT NULL,
      seller_id INTEGER NOT NULL,
      taker_side TEXT NOT NULL,
      buyer_fee TEXT NOT NULL,
      seller_fee TEXT NOT NULL,
      buyer_pnl TEXT NOT NULL,
      seller_pnl TEXT NOT NULL,
      ts INTEGER NOT NULL
    );
    CREATE INDEX IF NOT EXISTS trades_sym_ts ON trades(symbol, ts);
    CREATE INDEX IF NOT EXISTS trades_buyer ON trades(buyer_id, id);
    CREATE INDEX IF NOT EXISTS trades_seller ON trades(seller_id, id);
    CREATE TABLE IF NOT EXISTS ledger (
      id INTEGER PRIMARY KEY,
      user_id INTEGER NOT NULL,
      asset TEXT NOT NULL,
      amount TEXT NOT NULL,
      reason TEXT NOT NULL,
      ts INTEGER NOT NULL
    );
    CREATE INDEX IF NOT EXISTS ledger_user ON ledger(user_id, reason, ts);
  `);
  // База від спотової версії має іншу структуру — не змішуємо
  const cols = db.prepare('PRAGMA table_info(orders)').all().map((c) => c.name);
  if (!cols.includes('reduce_only'))
    throw new Error(`${file}: це база спотової версії біржі. Вкажіть інший файл (DB_FILE) — ф'ючерсна версія створить нову базу.`);
  return db;
}

module.exports = { openDb };
