'use strict';
const crypto = require('node:crypto');
const { promisify } = require('node:util');

const scrypt = promisify(crypto.scrypt);
const USERNAME_RE = /^[a-zA-Z0-9_]{3,20}$/;

class Auth {
  constructor(db, cfg) {
    this.db = db;
    this.cfg = cfg;
    this.cache = new Map(); // token_hash -> { uid, username, exp }
    this.st = {
      insertUser: db.prepare('INSERT INTO users(username, pass_hash, kind, created_at) VALUES(?,?,?,?)'),
      byName: db.prepare('SELECT * FROM users WHERE username=?'),
      byId: db.prepare('SELECT id, username, kind, created_at FROM users WHERE id=?'),
      insertSession: db.prepare('INSERT INTO sessions(token_hash, user_id, expires_at) VALUES(?,?,?)'),
      getSession: db.prepare('SELECT s.user_id, s.expires_at, u.username FROM sessions s JOIN users u ON u.id=s.user_id WHERE token_hash=?'),
      delSession: db.prepare('DELETE FROM sessions WHERE token_hash=?'),
      purge: db.prepare('DELETE FROM sessions WHERE expires_at<?'),
    };
    this.st.purge.run(Date.now());
  }

  async hash(password) {
    const salt = crypto.randomBytes(16);
    const key = await scrypt(password, salt, 32);
    return `scrypt$${salt.toString('hex')}$${key.toString('hex')}`;
  }

  async verify(password, stored) {
    const [, saltHex, keyHex] = stored.split('$');
    const key = await scrypt(password, Buffer.from(saltHex, 'hex'), 32);
    return crypto.timingSafeEqual(key, Buffer.from(keyHex, 'hex'));
  }

  validate(username, password) {
    if (typeof username !== 'string' || !USERNAME_RE.test(username))
      return 'Логін: 3–20 символів, латиниця, цифри, _';
    if (typeof password !== 'string' || password.length < 6 || password.length > 100)
      return 'Пароль: від 6 до 100 символів';
    return null;
  }

  // Системні акаунти (комісії, боти) без можливості входу
  ensureSystemUser(username, kind) {
    const r = this.st.byName.get(username);
    if (r) return { id: r.id, created: false };
    const info = this.st.insertUser.run(username, '!', kind, Date.now());
    return { id: Number(info.lastInsertRowid), created: true };
  }

  async register(username, password) {
    const hash = await this.hash(password);
    try {
      const info = this.st.insertUser.run(username, hash, 'user', Date.now());
      return Number(info.lastInsertRowid);
    } catch (e) {
      if (String(e.message).includes('UNIQUE')) return null;
      throw e;
    }
  }

  async login(username, password) {
    const r = this.st.byName.get(username);
    if (!r || r.kind !== 'user') {
      await this.hash(password); // однаковий час відповіді
      return null;
    }
    return (await this.verify(password, r.pass_hash)) ? { id: r.id, username: r.username } : null;
  }

  createSession(uid) {
    const token = crypto.randomBytes(32).toString('base64url');
    this.st.insertSession.run(sha(token), uid, Date.now() + this.cfg.sessionTtlMs);
    return token;
  }

  resolve(token) {
    if (!token || token.length > 100) return null;
    const h = sha(token);
    let s = this.cache.get(h);
    if (!s) {
      const r = this.st.getSession.get(h);
      if (!r) return null;
      s = { uid: r.user_id, username: r.username, exp: r.expires_at };
      if (this.cache.size > 10000) this.cache.clear();
      this.cache.set(h, s);
    }
    if (s.exp < Date.now()) {
      this.destroy(token);
      return null;
    }
    return s;
  }

  destroy(token) {
    if (!token) return;
    const h = sha(token);
    this.cache.delete(h);
    this.st.delSession.run(h);
  }

  user(uid) {
    return this.st.byId.get(uid);
  }
}

function sha(t) {
  return crypto.createHash('sha256').update(t).digest('hex');
}

module.exports = { Auth };
