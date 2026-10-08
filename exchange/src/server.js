'use strict';
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');

const cfg = require('./config');
const { openDb } = require('./db');
const { Engine, ApiError } = require('./engine');
const { Auth } = require('./auth');
const { startBots } = require('./bots');
const { BinanceBroker } = require('./broker/binance');
const { Hedger } = require('./broker/hedger');
const { fmt } = require('./decimal');

const PUBLIC_DIR = path.join(__dirname, '..', 'public');
const INTERVALS = { '1m': 60e3, '5m': 300e3, '15m': 900e3, '1h': 3600e3, '4h': 14400e3, '1d': 86400e3 };

function createServer(options = {}) {
  const conf = { ...cfg, ...options };
  const db = openDb(conf.dbFile);
  const engine = new Engine(db, conf);
  const auth = new Auth(db, conf);

  const fee = auth.ensureSystemUser('fees', 'system');
  engine.setFeeAccount(fee.id);
  let hedger = null;
  if (conf.broker.name === 'binance') {
    if (!/testnet/.test(conf.broker.tradeUrl) && !conf.broker.allowLive)
      throw new Error('BINANCE_TRADE_URL не тестнет: для реальної торгівлі потрібно явно задати BROKER_ALLOW_LIVE=1');
    hedger = new Hedger(db, engine, new BinanceBroker(conf.broker), conf.broker);
    hedger.start().catch((e) => console.error('Брокер:', e.message));
  } else if (conf.broker.name) throw new Error(`Невідомий брокер: ${conf.broker.name}`);
  const stopBots = conf.bots ? startBots(engine, auth, hedger) : () => {};

  // ---------- rate limiting (token bucket) ----------
  const buckets = new Map();
  function allow(key, rate, burst) {
    const now = Date.now();
    let b = buckets.get(key);
    if (!b) buckets.set(key, (b = { t: burst, at: now }));
    b.t = Math.min(burst, b.t + ((now - b.at) / 1000) * rate);
    b.at = now;
    if (b.t < 1) return false;
    b.t -= 1;
    return true;
  }
  const gcBuckets = setInterval(() => {
    const cut = Date.now() - 60e3;
    for (const [k, b] of buckets) if (b.at < cut) buckets.delete(k);
  }, 30e3);

  // ---------- SSE ----------
  const clients = new Set(); // { res, uid, symbol }
  const byUser = new Map();
  const dirtyDepth = new Set();
  const dirtyUsers = new Set();

  const frame = (event, data) => `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`;
  function send(c, event, data) {
    c.res.write(frame(event, data));
  }
  // Публічні дані серіалізуються один раз і розсилаються всім підписникам пари
  function broadcast(symbol, event, data) {
    const msg = frame(event, data);
    for (const c of clients) if (symbol === null || c.symbol === symbol) c.res.write(msg);
  }
  const pendingTrades = new Map(); // symbol -> [trade]
  const recentTrades = new Map(); // symbol -> останні 200 угод (для режиму опитування)

  engine.onEvents = (events) => {
    for (const e of events) {
      if (e.type === 'depth') dirtyDepth.add(e.symbol);
      else if (e.type === 'balances') dirtyUsers.add(e.uid);
      else if (e.type === 'order') {
        const set = byUser.get(e.uid);
        if (set) for (const c of set) send(c, 'order', e.order);
      } else if (e.type === 'trade') {
        const t = e.trade;
        if (hedger) hedger.onTrade(t);
        const pub = { id: t.id, symbol: t.symbol, price: fmt(t.price), qty: fmt(t.qty), side: t.takerSide, ts: t.ts };
        if (!pendingTrades.has(t.symbol)) pendingTrades.set(t.symbol, []);
        pendingTrades.get(t.symbol).push(pub);
        if (!recentTrades.has(t.symbol)) recentTrades.set(t.symbol, []);
        const rt = recentTrades.get(t.symbol);
        rt.push(pub);
        if (rt.length > 250) rt.splice(0, rt.length - 200);
        for (const uid of new Set([t.buyer, t.seller])) {
          const set = byUser.get(uid);
          if (set) for (const c of set) send(c, 'myTrade', { ...pub, mySide: uid === t.buyer ? 'BUY' : 'SELL' });
        }
      }
    }
  };

  // Угоди, стакан і баланси розсилаються пачками раз на 100 мс — під навантаженням це
  // різко зменшує трафік.
  const flush = setInterval(() => {
    for (const [sym, list] of pendingTrades) broadcast(sym, 'trades', list.slice(-100));
    pendingTrades.clear();
    for (const sym of dirtyDepth) broadcast(sym, 'depth', engine.depth(sym, 20));
    dirtyDepth.clear();
    for (const uid of dirtyUsers) {
      const set = byUser.get(uid);
      if (set && set.size) {
        const msg = frame('account', { balances: engine.balances(uid), pnl: engine.pnl(uid) });
        for (const c of set) c.res.write(msg);
      }
    }
    dirtyUsers.clear();
  }, 100);

  const tickers = setInterval(() => {
    if (!clients.size) return;
    broadcast(null, 'tickers', [...engine.markets.keys()].map((s) => engine.ticker(s)));
    // PnL залежить від ринкової ціни, тож оновлюємо його всім залогіненим раз на 2 с
    for (const [uid, set] of byUser) {
      const msg = frame('account', { balances: engine.balances(uid), pnl: engine.pnl(uid) });
      for (const c of set) c.res.write(msg);
    }
  }, 2000);

  const heartbeat = setInterval(() => {
    for (const c of clients) c.res.write(': ping\n\n');
  }, 15000);

  // ---------- helpers ----------
  function clientIp(req) {
    if (conf.trustProxy) {
      const cf = req.headers['cf-connecting-ip']; // Cloudflare Tunnel
      if (cf) return String(cf).trim();
      const xff = req.headers['x-forwarded-for'];
      if (xff) return xff.split(',')[0].trim();
    }
    return req.socket.remoteAddress || '';
  }
  const LOOPBACK = new Set(['127.0.0.1', '::1', '::ffff:127.0.0.1']);
  // "Локальний" = справді з цього комп'ютера. Запити через тунель/проксі теж приходять
  // з 127.0.0.1, але несуть заголовки пересилання — їм привілеї localhost не даються.
  function isLocalReq(req) {
    const h = req.headers;
    if (h['cf-connecting-ip'] || h['x-forwarded-for'] || h['x-real-ip'] || h['forwarded']) return false;
    return LOOPBACK.has(req.socket.remoteAddress);
  }

  function getToken(req) {
    const h = req.headers.authorization;
    if (h && h.startsWith('Bearer ')) return h.slice(7);
    const c = req.headers.cookie;
    if (!c) return null;
    for (const part of c.split(';')) {
      const [k, ...v] = part.trim().split('=');
      if (k === 'sid') return v.join('=');
    }
    return null;
  }

  function json(res, status, body, headers = {}) {
    const s = JSON.stringify(body);
    res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', ...headers });
    res.end(s);
  }

  function readBody(req) {
    return new Promise((resolve, reject) => {
      if (req.method === 'GET' || req.method === 'HEAD') return resolve({});
      const ct = req.headers['content-type'] || '';
      if (req.method === 'POST' && !ct.startsWith('application/json'))
        return reject(new ApiError(415, 'BAD_CONTENT_TYPE', 'Очікується application/json'));
      let size = 0;
      const chunks = [];
      req.on('data', (c) => {
        size += c.length;
        if (size > 16 * 1024) {
          reject(new ApiError(413, 'TOO_LARGE', 'Запит завеликий'));
          req.destroy();
        } else chunks.push(c);
      });
      req.on('end', () => {
        if (!chunks.length) return resolve({});
        try {
          const v = JSON.parse(Buffer.concat(chunks).toString('utf8'));
          resolve(v && typeof v === 'object' ? v : {});
        } catch {
          reject(new ApiError(400, 'BAD_JSON', 'Некоректний JSON'));
        }
      });
      req.on('error', reject);
    });
  }

  function sessionCookie(token, maxAgeSec) {
    return `sid=${token}; HttpOnly; SameSite=Strict; Path=/; Max-Age=${maxAgeSec}${conf.cookieSecure ? '; Secure' : ''}`;
  }

  function requireUser(ctx) {
    if (!ctx.session) throw new ApiError(401, 'UNAUTHORIZED', 'Потрібно увійти');
    return ctx.session.uid;
  }

  function requireAdmin(ctx) {
    const t = ctx.req.headers['x-admin-token'];
    const okAdmin = conf.adminToken && typeof t === 'string' && t.length === conf.adminToken.length &&
      require('node:crypto').timingSafeEqual(Buffer.from(t), Buffer.from(conf.adminToken));
    if (!okAdmin && !ctx.local) throw new ApiError(403, 'FORBIDDEN', 'Тільки для адміністратора');
  }

  function tradeLimit(ctx) {
    if (!allow(`u:${ctx.session.uid}`, 20, 40)) throw new ApiError(429, 'RATE_LIMIT', 'Забагато запитів, спробуйте пізніше');
  }

  function symbolParam(v) {
    const s = String(v || '').toUpperCase();
    if (!engine.markets.has(s)) throw new ApiError(400, 'BAD_SYMBOL', 'Невідома торгова пара');
    return s;
  }

  // ---------- routes ----------
  const routes = {
    'GET /api/markets': () =>
      [...engine.markets.values()].map((m) => ({
        symbol: m.symbol, base: m.base, quote: m.quote, tick: fmt(m.tick), step: fmt(m.step), minNotional: fmt(m.minNotional),
      })),
    'GET /api/config': () => ({
      makerFeePct: Number(conf.makerFeeBps) / 100, takerFeePct: Number(conf.takerFeeBps) / 100,
      faucet: conf.faucet, signupBonus: conf.signupBonus,
    }),
    'GET /api/ticker': () => [...engine.markets.keys()].map((s) => engine.ticker(s)),
    'GET /api/depth': (ctx) => engine.depth(symbolParam(ctx.q.get('symbol')), clampInt(ctx.q.get('limit'), 1, 200, 20)),
    'GET /api/trades': (ctx) => engine.recentTrades(symbolParam(ctx.q.get('symbol')), clampInt(ctx.q.get('limit'), 1, 500, 50)),
    'GET /api/klines': (ctx) => {
      const iv = INTERVALS[ctx.q.get('interval') || '1m'];
      if (!iv) throw new ApiError(400, 'BAD_INTERVAL', 'interval: ' + Object.keys(INTERVALS).join(', '));
      return engine.klines(symbolParam(ctx.q.get('symbol')), iv, clampInt(ctx.q.get('limit'), 1, 1000, 300));
    },

    'POST /api/register': async (ctx) => {
      if (!ctx.local && !allow(`reg:${ctx.ip}`, 5 / 60, 5))
        throw new ApiError(429, 'RATE_LIMIT', 'Забагато реєстрацій з цієї IP');
      const { username, password } = ctx.body;
      const err = auth.validate(username, password);
      if (err) throw new ApiError(400, 'BAD_CREDENTIALS', err);
      const uid = await auth.register(username, password);
      if (!uid) throw new ApiError(409, 'USERNAME_TAKEN', 'Такий логін вже зайнятий');
      engine.deposit(uid, conf.signupBonus, 'signup_bonus');
      const token = auth.createSession(uid);
      ctx.setHeader('Set-Cookie', sessionCookie(token, conf.sessionTtlMs / 1000));
      return { id: uid, username, token };
    },
    'POST /api/login': async (ctx) => {
      if (!ctx.local && !allow(`login:${ctx.ip}`, 10 / 60, 10))
        throw new ApiError(429, 'RATE_LIMIT', 'Забагато спроб входу');
      const { username, password } = ctx.body;
      if (typeof username !== 'string' || typeof password !== 'string' || password.length > 100)
        throw new ApiError(400, 'BAD_CREDENTIALS', 'Вкажіть логін і пароль');
      const u = await auth.login(username, password);
      if (!u) throw new ApiError(401, 'BAD_CREDENTIALS', 'Невірний логін або пароль');
      const token = auth.createSession(u.id);
      ctx.setHeader('Set-Cookie', sessionCookie(token, conf.sessionTtlMs / 1000));
      return { id: u.id, username: u.username, token };
    },
    'POST /api/logout': (ctx) => {
      auth.destroy(ctx.token);
      ctx.setHeader('Set-Cookie', sessionCookie('', 0));
      return { ok: true };
    },
    'GET /api/me': (ctx) => {
      const uid = requireUser(ctx);
      return { id: uid, username: ctx.session.username, balances: engine.balances(uid), pnl: engine.pnl(uid) };
    },
    'GET /api/balances': (ctx) => engine.balances(requireUser(ctx)),
    'GET /api/pnl': (ctx) => engine.pnl(requireUser(ctx)),
    'POST /api/faucet': (ctx) => {
      const uid = requireUser(ctx);
      engine.faucet(uid);
      return engine.balances(uid);
    },

    'POST /api/order': (ctx) => {
      const uid = requireUser(ctx);
      tradeLimit(ctx);
      return engine.placeOrder(uid, ctx.body);
    },
    'DELETE /api/order': (ctx) => {
      const uid = requireUser(ctx);
      tradeLimit(ctx);
      return engine.cancelOrder(uid, ctx.q.get('id'));
    },
    'DELETE /api/orders': (ctx) => {
      const uid = requireUser(ctx);
      tradeLimit(ctx);
      const sym = ctx.q.get('symbol');
      return { canceled: engine.cancelAll(uid, sym ? symbolParam(sym) : null) };
    },
    'GET /api/orders/open': (ctx) => {
      const sym = ctx.q.get('symbol');
      return engine.openOrders(requireUser(ctx), sym ? symbolParam(sym) : null);
    },
    'GET /api/orders/history': (ctx) => engine.orderHistory(requireUser(ctx), clampInt(ctx.q.get('limit'), 1, 500, 100)),
    'GET /api/my-trades': (ctx) => engine.myTrades(requireUser(ctx), clampInt(ctx.q.get('limit'), 1, 500, 100)),

    'GET /api/audit': (ctx) => {
      requireAdmin(ctx);
      return { ...engine.audit(), sseClients: clients.size, memMB: Math.round(process.memoryUsage().rss / 1048576) };
    },
    'GET /api/admin/broker': (ctx) => {
      requireAdmin(ctx);
      return hedger ? hedger.status() : { broker: null, message: 'Брокер не підключено (BROKER не задано)' };
    },
    // Запасний канал для мереж, де стрім (SSE) не проходить (напр. швидкий тунель Cloudflare):
    // клієнт раз на секунду забирає все одним запитом.
    'GET /api/poll': (ctx) => {
      const symbol = symbolParam(ctx.q.get('symbol'));
      const since = Number(ctx.q.get('since')) || 0;
      const out = {
        depth: engine.depth(symbol, 20),
        tickers: [...engine.markets.keys()].map((s) => engine.ticker(s)),
        trades: (recentTrades.get(symbol) || []).filter((t) => t.id > since).slice(-100),
      };
      if (ctx.session) {
        const uid = ctx.session.uid;
        out.account = { balances: engine.balances(uid), pnl: engine.pnl(uid) };
        out.open = engine.openOrders(uid);
      }
      return out;
    },
    'GET /api/health': () => ({ ok: true, uptime: Math.round(process.uptime()) }),
  };

  function openStream(ctx) {
    const symbol = symbolParam(ctx.q.get('symbol') || 'BTCUSDT');
    if (clients.size >= 5000) throw new ApiError(503, 'BUSY', 'Сервер перевантажений');
    const uid = ctx.session?.uid || null;
    let set = uid ? byUser.get(uid) : null;
    if (uid && set && set.size >= 10) throw new ApiError(429, 'TOO_MANY_STREAMS', 'Забагато відкритих вкладок');
    const res = ctx.res;
    res.writeHead(200, {
      'Content-Type': 'text/event-stream; charset=utf-8',
      'Cache-Control': 'no-store',
      Connection: 'keep-alive',
      'X-Accel-Buffering': 'no',
    });
    res.write('retry: 2000\n\n');
    ctx.req.socket.setNoDelay(true);
    const c = { res, uid, symbol };
    clients.add(c);
    if (uid) {
      if (!set) byUser.set(uid, (set = new Set()));
      set.add(c);
    }
    send(c, 'depth', engine.depth(symbol, 20));
    send(c, 'tickers', [...engine.markets.keys()].map((s) => engine.ticker(s)));
    if (uid) send(c, 'account', { balances: engine.balances(uid), pnl: engine.pnl(uid) });
    ctx.req.on('close', () => {
      clients.delete(c);
      if (uid) {
        set.delete(c);
        if (!set.size) byUser.delete(uid);
      }
    });
  }

  function serveStatic(req, res, pathname) {
    let p = pathname === '/' ? '/index.html' : pathname;
    const file = path.normalize(path.join(PUBLIC_DIR, p));
    if (!file.startsWith(PUBLIC_DIR + path.sep)) {
      res.writeHead(403).end();
      return;
    }
    fs.readFile(file, (err, data) => {
      if (err) {
        res.writeHead(404, { 'Content-Type': 'text/plain' }).end('Not found');
        return;
      }
      const types = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.svg': 'image/svg+xml' };
      res.writeHead(200, { 'Content-Type': types[path.extname(file)] || 'application/octet-stream', 'Cache-Control': 'no-cache' });
      res.end(data);
    });
  }

  const server = http.createServer(async (req, res) => {
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('X-Frame-Options', 'DENY');
    res.setHeader('Referrer-Policy', 'same-origin');
    res.setHeader('Content-Security-Policy', "default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:");
    const url = new URL(req.url, 'http://x');
    const ctx = {
      req, res, q: url.searchParams, ip: clientIp(req), local: isLocalReq(req), token: getToken(req), session: null, body: {},
      setHeader: (k, v) => res.setHeader(k, v),
    };
    try {
      if (!url.pathname.startsWith('/api/')) {
        if (req.method !== 'GET' && req.method !== 'HEAD') throw new ApiError(405, 'METHOD', 'Method not allowed');
        return serveStatic(req, res, url.pathname);
      }
      if (!ctx.local && !allow(`ip:${ctx.ip}`, 50, 100)) throw new ApiError(429, 'RATE_LIMIT', 'Забагато запитів');
      ctx.session = auth.resolve(ctx.token);
      if (url.pathname === '/api/stream' && req.method === 'GET') return openStream(ctx);
      const handler = routes[`${req.method} ${url.pathname}`];
      if (!handler) throw new ApiError(404, 'NOT_FOUND', 'Невідомий endpoint');
      ctx.body = await readBody(req);
      const result = await handler(ctx);
      json(res, 200, result);
    } catch (e) {
      if (e instanceof ApiError) json(res, e.status, { error: e.code, message: e.message });
      else {
        console.error(e);
        json(res, 500, { error: 'INTERNAL', message: 'Внутрішня помилка' });
      }
    }
  });
  server.keepAliveTimeout = 65000;
  server.headersTimeout = 66000;

  server.shutdown = () => {
    stopBots();
    if (hedger) hedger.stop();
    for (const t of [flush, tickers, heartbeat, gcBuckets]) clearInterval(t);
    for (const c of clients) c.res.end();
    server.close();
    server.closeAllConnections();
    db.close();
  };
  server.engine = engine;
  server.hedger = hedger;
  server.auth = auth;
  return server;
}

function clampInt(v, lo, hi, def) {
  const n = parseInt(v, 10);
  if (!Number.isFinite(n)) return def;
  return Math.max(lo, Math.min(hi, n));
}

if (require.main === module) {
  const server = createServer();
  server.listen(cfg.port, cfg.host, () => {
    console.log(`Біржа запущена: http://localhost:${cfg.port}  (БД: ${cfg.dbFile}, боти: ${cfg.bots ? 'увімк' : 'вимк'})`);
  });
  const stop = () => {
    console.log('Зупинка...');
    server.shutdown();
    process.exit(0);
  };
  process.on('SIGINT', stop);
  process.on('SIGTERM', stop);
}

module.exports = { createServer };
