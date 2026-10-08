#!/usr/bin/env node
'use strict';
// Бета-запуск біржі на власному комп'ютері з публічною адресою в інтернеті.
//
//   node beta.js        (або подвійний клік: start-beta.bat / start-beta.command)
//
// 1. Запускає біржу на цьому комп'ютері (дані — у data/beta.db).
// 2. Відкриває безкоштовний Cloudflare Tunnel: користувачі заходять за адресою
//    https://<випадкові-слова>.trycloudflare.com. Роутер і порти налаштовувати не треба.
// 3. Якщо біржа або тунель впадуть — перезапускає їх.
// Налаштування — у файлі beta.env (створюється при першому запуску).

const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { spawn, spawnSync } = require('node:child_process');

const ROOT = __dirname;
const BIN = path.join(ROOT, 'bin');
const ENV_FILE = path.join(ROOT, 'beta.env');

const [maj, min] = process.versions.node.split('.').map(Number);
if (maj < 22 || (maj === 22 && min < 5)) {
  console.error(`Потрібен Node.js 22.5 або новіший (зараз ${process.versions.node}). Завантажте LTS з https://nodejs.org`);
  process.exit(1);
}

// ---------- налаштування ----------
if (!fs.existsSync(ENV_FILE)) {
  fs.writeFileSync(ENV_FILE, `# Налаштування бети. Після зміни перезапустіть start-beta.
PORT=8080

# Пароль для сторінки /admin.html
ADMIN_TOKEN=${crypto.randomBytes(18).toString('base64url')}

# Брокер ліквідності: реальні ціни Binance. З ключами — ще й дублювання угод
# на демо-рахунок (ключі: https://testnet.binance.vision -> Log in with GitHub -> Generate HMAC_SHA256 Key)
BROKER=binance
BINANCE_API_KEY=
BINANCE_API_SECRET=
`);
}
const fileEnv = {};
for (const line of fs.readFileSync(ENV_FILE, 'utf8').split(/\r?\n/)) {
  const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*?)\s*$/);
  if (m && m[2] !== '') fileEnv[m[1]] = m[2];
}
const PORT = Number(fileEnv.PORT) || 8080;
const env = {
  ...process.env,
  ...fileEnv,
  PORT: String(PORT),
  HOST: '127.0.0.1', // назовні — тільки через тунель
  TRUST_PROXY: '1',
  COOKIE_SECURE: '1',
  DB_FILE: fileEnv.DB_FILE || path.join(ROOT, 'data', 'beta.db'),
};

let stopping = false;
const children = new Set();
function run(cmd, args, opts) {
  const c = spawn(cmd, args, opts);
  children.add(c);
  c.on('exit', () => children.delete(c));
  return c;
}
function shutdown() {
  if (stopping) return;
  stopping = true;
  console.log('\nЗупинка бети...');
  for (const c of children) c.kill();
  setTimeout(() => process.exit(0), 1500);
}
process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);

// ---------- біржа ----------
function startExchange() {
  const c = run(process.execPath, ['--disable-warning=ExperimentalWarning', path.join(ROOT, 'src', 'server.js')], {
    cwd: ROOT, env, stdio: ['ignore', 'inherit', 'inherit'],
  });
  c.on('exit', (code) => {
    if (stopping) return;
    console.error(`Біржа зупинилась (код ${code}) — перезапуск через 2 с`);
    setTimeout(startExchange, 2000);
  });
}

async function waitHealthy() {
  for (let i = 0; i < 60; i++) {
    try {
      const r = await fetch(`http://127.0.0.1:${PORT}/api/health`);
      if (r.ok) return;
    } catch {}
    await new Promise((r) => setTimeout(r, 500));
  }
  throw new Error(`Біржа не відповідає на порту ${PORT}. Можливо, порт зайнятий — змініть PORT у beta.env`);
}

// ---------- cloudflared ----------
function assetName() {
  const arch = process.arch === 'arm64' ? 'arm64' : process.arch === 'ia32' ? '386' : 'amd64';
  if (process.platform === 'win32') return { file: `cloudflared-windows-${arch === 'arm64' ? 'amd64' : arch}.exe`, out: 'cloudflared.exe' };
  if (process.platform === 'darwin') return { file: `cloudflared-darwin-${arch === 'arm64' ? 'arm64' : 'amd64'}.tgz`, out: 'cloudflared', tgz: true };
  return { file: `cloudflared-linux-${arch}`, out: 'cloudflared' };
}

async function findCloudflared() {
  if (process.env.CLOUDFLARED) return process.env.CLOUDFLARED;
  const a = assetName();
  const local = path.join(BIN, a.out);
  if (fs.existsSync(local)) return local;
  const sys = spawnSync('cloudflared', ['--version'], { stdio: 'ignore' });
  if (sys.status === 0) return 'cloudflared';

  console.log(`Завантажую Cloudflare Tunnel (${a.file}, ~20-40 МБ, один раз)...`);
  const url = `https://github.com/cloudflare/cloudflared/releases/latest/download/${a.file}`;
  const r = await fetch(url);
  if (!r.ok) throw new Error(`Не вдалося завантажити ${url}: HTTP ${r.status}`);
  fs.mkdirSync(BIN, { recursive: true });
  const buf = Buffer.from(await r.arrayBuffer());
  if (a.tgz) {
    const tgz = path.join(BIN, a.file);
    fs.writeFileSync(tgz, buf);
    const t = spawnSync('tar', ['-xzf', tgz, '-C', BIN]);
    fs.rmSync(tgz);
    if (t.status !== 0) throw new Error('Не вдалося розпакувати cloudflared. Встановіть вручну: brew install cloudflared');
  } else fs.writeFileSync(local, buf);
  fs.chmodSync(local, 0o755);
  return local;
}

function startTunnel(bin) {
  const c = run(bin, ['tunnel', '--no-autoupdate', '--url', `http://127.0.0.1:${PORT}`], {
    cwd: ROOT, stdio: ['ignore', 'pipe', 'pipe'],
  });
  let shown = false;
  const onData = (d) => {
    const m = String(d).match(/https:\/\/[a-z0-9-]+\.trycloudflare\.com/);
    if (m && !shown) {
      shown = true;
      fs.writeFileSync(path.join(ROOT, 'beta-url.txt'), m[0] + '\n');
      banner(m[0]);
    }
  };
  c.stdout.on('data', onData);
  c.stderr.on('data', onData);
  c.on('exit', (code) => {
    if (stopping) return;
    console.error(`Тунель закрився (код ${code}) — перезапуск через 5 с (адреса зміниться!)`);
    setTimeout(() => startTunnel(bin), 5000);
  });
}

function banner(url) {
  const line = '═'.repeat(64);
  console.log(`\n${line}
  БЕТА ЗАПУЩЕНА — надішліть користувачам цю адресу:

     ${url}

  Адмінка:  ${url}/admin.html
  Пароль адмінки (ADMIN_TOKEN): ${env.ADMIN_TOKEN || '(не задано — адмінка лише з цього комп\'ютера)'}
  На цьому комп'ютері: http://localhost:${PORT}

  Не закривайте це вікно і не вимикайте/не присипляйте комп'ютер.
  Зупинка: Ctrl+C. Адреса також збережена у файлі beta-url.txt
${line}\n`);
}

(async () => {
  console.log('Запуск біржі...');
  startExchange();
  await waitHealthy();
  const bin = await findCloudflared();
  console.log('Відкриваю тунель Cloudflare...');
  startTunnel(bin);
})().catch((e) => {
  console.error('Помилка:', e.message);
  shutdown();
});
