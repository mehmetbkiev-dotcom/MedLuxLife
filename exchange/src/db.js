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
      asset TEXT NOT NULL,
      free TEXT NOT NULL,
      locked TEXT NOT NULL,
      PRIMARY KEY (user_id, asset)
    );
    CREATE TABLE IF NOT EXISTS positions (
      user_id INTEGER NOT NULL,
      asset TEXT NOT NULL,
      qty TEXT NOT NULL,
      cost TEXT NOT NULL,
      realized TEXT NOT NULL,
      fees TEXT NOT NULL,
      PRIMARY KEY (user_id, asset)
    );
    CREATE TABLE IF NOT EXISTS orders (
      id INTEGER PRIMARY KEY,
      user_id INTEGER NOT NULL,
      symbol TEXT NOT NULL,
      side TEXT NOT NULL,
      type TEXT NOT NULL,
      tif TEXT,
      price TEXT,
      qty TEXT,
      quote_qty TEXT,
      filled TEXT NOT NULL,
      quote_filled TEXT NOT NULL,
      fee TEXT NOT NULL,
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
  return db;
}

module.exports = { openDb };
