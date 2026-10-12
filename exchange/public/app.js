'use strict';
(() => {
  const $ = (s) => document.querySelector(s);
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
  const decimals = (step) => (step.includes('.') ? step.split('.')[1].length : 0);
  const fmtN = (v, d) =>
    v === null || v === undefined || v === '' ? '—' : Number(v).toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d });
  const time = (ts) => new Date(ts).toLocaleTimeString('uk-UA', { hour12: false });
  const dt = (ts) => new Date(ts).toLocaleString('uk-UA', { hour12: false });
  const floorTo = (x, d) => {
    const f = 10 ** d;
    return (Math.floor(x * f + 1e-9) / f).toFixed(d);
  };

  const STATUS = {
    NEW: 'Новий', PARTIALLY_FILLED: 'Частково', FILLED: 'Виконано', CANCELED: 'Скасовано',
    EXPIRED: 'Прострочено', EXPIRED_STP: 'Скасовано (STP)',
  };
  const TYPE = { LIMIT: 'Лімітний', MARKET: 'Ринковий', LIMIT_MAKER: 'Post-only', LIQUIDATION: 'Ліквідація' };

  const S = {
    markets: [], m: null, sym: localStorage.getItem('sym') || 'BTCUSDT', interval: localStorage.getItem('iv') || '1m',
    me: null, account: null, positions: [], leverages: {}, open: [], history: [], myTrades: [], tickers: {},
    depth: { bids: [], asks: [] }, trades: [], klines: [], type: 'LIMIT', tab: 'positions', es: null, hover: null, mode: 'sse', lastTradeId: 0,
    visible: 90,
  };

  async function api(method, path, body) {
    const r = await fetch(path, {
      method, credentials: 'same-origin',
      headers: body ? { 'Content-Type': 'application/json' } : {},
      body: body ? JSON.stringify(body) : undefined,
    });
    const data = await r.json().catch(() => ({}));
    if (!r.ok) {
      const e = new Error(data.message || `HTTP ${r.status}`);
      e.status = r.status;
      throw e;
    }
    return data;
  }

  function toast(msg, kind = '') {
    const el = document.createElement('div');
    el.className = `toast ${kind}`;
    el.textContent = msg;
    $('#toasts').appendChild(el);
    setTimeout(() => el.remove(), 4000);
    while ($('#toasts').children.length > 5) $('#toasts').firstChild.remove();
  }

  // ---------------- header ----------------
  function renderMarkets() {
    const m = S.markets.find((x) => x.symbol === S.sym);
    if (!m) return;
    $('#markets').innerHTML = `<button id="pair-btn" class="pair-btn" type="button" aria-haspopup="listbox">
      <b>${m.base}USDT</b> <span class="muted perp">Безстроковий</span> <span class="caret">▾</span></button>`;
    renderPairList();
  }

  // Випадаючий список пар з пошуком (як на Binance)
  function renderPairList() {
    if ($('#pair-panel').classList.contains('hidden')) return;
    const q = $('#pair-search').value.trim().toUpperCase().replace('/', '');
    const rows = S.markets.filter((m) => !q || m.base.includes(q) || m.symbol.includes(q));
    $('#pair-list').innerHTML = rows.length ? rows.map((m) => {
      const t = S.tickers[m.symbol];
      const ch = t ? t.changePct : 0;
      return `<div class="pair-row${m.symbol === S.sym ? ' active' : ''}" data-sym="${m.symbol}" role="option">
        <span><b>${m.base}</b><span class="muted">USDT</span> <span class="badge lev">${m.maxLeverage || 50}x</span></span>
        <span class="num r">${t ? fmtN(t.last, decimals(m.tick)) : '—'}</span>
        <span class="num r ${ch >= 0 ? 'green' : 'red'}">${ch >= 0 ? '+' : ''}${ch.toFixed(2)}%</span></div>`;
    }).join('') : '<div class="empty">Нічого не знайдено</div>';
  }
  function togglePairs(open) {
    const p = $('#pair-panel');
    p.classList.toggle('hidden', !open);
    if (open) {
      $('#pair-search').value = '';
      renderPairList();
      $('#pair-search').focus();
    }
  }

  function renderTicker() {
    const t = S.tickers[S.sym];
    if (!t || !S.m) return;
    const pd = decimals(S.m.tick);
    const up = t.changePct >= 0;
    $('#ticker').innerHTML = `
      <div><span class="big num ${up ? 'green' : 'red'}">${fmtN(t.last, pd)}</span></div>
      <div><small>Ціна маркування</small><span class="num">${fmtN(t.mark, pd)}</span></div>
      <div><small>Зміна 24г</small><span class="num ${up ? 'green' : 'red'}">${up ? '+' : ''}${t.changePct.toFixed(2)}%</span></div>
      <div class="hide-sm"><small>Макс 24г</small><span class="num">${fmtN(t.high, pd)}</span></div>
      <div class="hide-sm"><small>Мін 24г</small><span class="num">${fmtN(t.low, pd)}</span></div>
      <div class="hide-sm"><small>Обсяг 24г (${S.m.base})</small><span class="num">${fmtN(t.volume, 2)}</span></div>
      <div class="hide-sm"><small>Обсяг 24г (${S.m.quote})</small><span class="num">${fmtN(t.quoteVolume, 0)}</span></div>`;
    document.title = `${fmtN(t.last, pd)} | ${S.m.base}USDT безстроковий — Quite Harbor`;
  }

  function renderAccountBar() {
    const bar = $('#account-bar');
    if (!S.me) {
      bar.innerHTML = `<button class="btn" id="btn-login">Увійти</button><button class="btn primary" id="btn-register">Реєстрація</button>`;
      $('#btn-login').onclick = () => openModal('login');
      $('#btn-register').onclick = () => openModal('register');
      return;
    }
    const eq = S.account ? fmtN(S.account.equity, 2) : '—';
    bar.innerHTML = `<span class="muted">Капітал:</span> <b class="num">${eq} USDT</b>
      <span class="muted" id="uname"></span><button class="btn" id="btn-logout">Вийти</button>`;
    $('#uname').textContent = S.me.username;
    $('#btn-logout').onclick = async () => {
      await api('POST', '/api/logout').catch(() => {});
      S.me = null;
      S.account = null;
      S.positions = [];
      S.open = [];
      renderAll();
      connect();
    };
  }

  // ---------------- order book & trades ----------------
  function renderBook() {
    if (!S.m) return;
    const pd = decimals(S.m.tick), qd = decimals(S.m.step);
    const n = 16;
    const asks = S.depth.asks.slice(0, n), bids = S.depth.bids.slice(0, n);
    let max = 0;
    for (const [p, q] of [...asks, ...bids]) max = Math.max(max, p * q);
    const row = ([p, q], cls) => {
      const tot = p * q;
      return `<div class="row" data-price="${esc(p)}"><div class="bar" style="width:${max ? (tot / max) * 100 : 0}%"></div>
        <span class="${cls}">${fmtN(p, pd)}</span><span>${fmtN(q, qd)}</span><span>${fmtN(tot, 2)}</span></div>`;
    };
    $('#asks').innerHTML = asks.slice().reverse().map((l) => row(l, 'red')).join('');
    $('#bids').innerHTML = bids.map((l) => row(l, 'green')).join('');
    const last = S.tickers[S.sym]?.last;
    const lastTrade = S.trades[0];
    const bid = bids[0]?.[0], ask = asks[0]?.[0];
    const spread = bid && ask ? (((ask - bid) / ask) * 100).toFixed(3) + '%' : '';
    $('#mid').innerHTML = `<span class="num ${lastTrade?.side === 'SELL' ? 'red' : 'green'}">${fmtN(last, pd)}</span><small>спред ${spread}</small>`;
  }

  function renderTrades() {
    if (!S.m) return;
    const pd = decimals(S.m.tick), qd = decimals(S.m.step);
    $('#trades').innerHTML = S.trades
      .slice(0, 60)
      .map((t) => `<div class="row"><span class="${t.side === 'BUY' ? 'green' : 'red'}">${fmtN(t.price, pd)}</span><span>${fmtN(t.qty, qd)}</span><span class="muted">${time(t.ts)}</span></div>`)
      .join('');
  }

  // ---------------- chart ----------------
  const canvas = $('#canvas');
  const ctx = canvas.getContext('2d');
  const IV_MS = { '1m': 60e3, '5m': 300e3, '15m': 900e3, '1h': 3600e3, '4h': 14400e3, '1d': 86400e3 };

  function renderIntervals() {
    $('#intervals').innerHTML = Object.keys(IV_MS)
      .map((k) => `<button data-iv="${k}" class="${k === S.interval ? 'active' : ''}">${k}</button>`)
      .join('');
  }

  function drawChart() {
    const wrap = canvas.parentElement;
    const dpr = window.devicePixelRatio || 1;
    const W = wrap.clientWidth, H = wrap.clientHeight;
    if (!W || !H) return;
    if (canvas.width !== W * dpr || canvas.height !== H * dpr) {
      canvas.width = W * dpr;
      canvas.height = H * dpr;
    }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, W, H);
    const css = getComputedStyle(document.documentElement);
    const C = { green: css.getPropertyValue('--green'), red: css.getPropertyValue('--red'), muted: css.getPropertyValue('--muted'), line: css.getPropertyValue('--line') };
    const axisW = 70, axisH = 22;
    const plotW = W - axisW, plotH = H - axisH;
    const volH = plotH * 0.18;
    const priceH = plotH - volH - 8;
    const k = S.klines.slice(-Math.max(10, Math.min(S.visible, 400)));
    if (!k.length) {
      ctx.fillStyle = C.muted;
      ctx.fillText('Немає даних', 20, 30);
      return;
    }
    // Фіксована кількість "місць" під свічки (як на Binance): мало даних — свічки
    // стоять праворуч нормальної ширини, а не розтягуються на весь графік.
    const slots = Math.max(k.length, Math.min(S.visible, 400));
    const off = slots - k.length;
    const slot = plotW / slots;
    const xAt = (i) => (off + i) * slot + slot / 2;
    const bodyW = Math.max(1, Math.min(14, slot * 0.7));
    let hi = -Infinity, lo = Infinity, vmax = 0;
    for (const c of k) {
      hi = Math.max(hi, +c[2]);
      lo = Math.min(lo, +c[3]);
      vmax = Math.max(vmax, +c[5]);
    }
    if (hi === lo) { hi *= 1.001; lo *= 0.999; }
    const pad = (hi - lo) * 0.08;
    hi += pad; lo -= pad;
    const y = (p) => 6 + ((hi - p) / (hi - lo)) * (priceH - 6);
    const pd = decimals(S.m.tick);

    ctx.font = '11px -apple-system, Segoe UI, Roboto, sans-serif';
    ctx.strokeStyle = C.line;
    ctx.fillStyle = C.muted;
    ctx.lineWidth = 1;
    for (let i = 0; i <= 5; i++) {
      const p = lo + ((hi - lo) * i) / 5;
      const yy = Math.round(y(p)) + 0.5;
      ctx.beginPath(); ctx.moveTo(0, yy); ctx.lineTo(plotW, yy); ctx.stroke();
      ctx.fillText(fmtN(p, pd), plotW + 6, yy + 4);
    }
    const every = Math.max(1, Math.ceil(90 / slot));
    for (let i = 0; i < k.length; i += every) {
      const x = xAt(i);
      const d = new Date(k[i][0]);
      const label = IV_MS[S.interval] >= 86400e3 ? `${d.getDate()}.${d.getMonth() + 1}` : d.toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' });
      ctx.fillText(label, x - 14, H - 6);
    }
    k.forEach((c, i) => {
      const [, o, h, l, cl, v] = c.map(Number);
      const x = xAt(i);
      const up = cl >= o;
      ctx.strokeStyle = ctx.fillStyle = up ? C.green : C.red;
      ctx.beginPath(); ctx.moveTo(Math.round(x) + 0.5, y(h)); ctx.lineTo(Math.round(x) + 0.5, y(l)); ctx.stroke();
      const top = y(Math.max(o, cl)), bh = Math.max(1, Math.abs(y(o) - y(cl)));
      ctx.fillRect(x - bodyW / 2, top, bodyW, bh);
      ctx.globalAlpha = 0.35;
      const vh = vmax ? (v / vmax) * volH : 0;
      ctx.fillRect(x - bodyW / 2, plotH - vh, bodyW, vh);
      ctx.globalAlpha = 1;
    });
    // остання ціна
    const last = +k[k.length - 1][4];
    const ly = Math.round(y(last)) + 0.5;
    const lastUp = last >= +k[k.length - 1][1];
    ctx.setLineDash([3, 3]);
    ctx.strokeStyle = lastUp ? C.green : C.red;
    ctx.beginPath(); ctx.moveTo(0, ly); ctx.lineTo(plotW, ly); ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = lastUp ? C.green : C.red;
    ctx.fillRect(plotW, ly - 9, axisW, 18);
    ctx.fillStyle = '#fff';
    ctx.fillText(fmtN(last, pd), plotW + 6, ly + 4);
    // лінії позиції: ціна входу і ціна ліквідації
    const ps = S.positions.find((p) => p.symbol === S.sym);
    if (ps) {
      const level = (price, color, label) => {
        if (!(price > lo && price < hi)) return;
        const yy = Math.round(y(price)) + 0.5;
        ctx.setLineDash([6, 4]);
        ctx.strokeStyle = color;
        ctx.beginPath(); ctx.moveTo(0, yy); ctx.lineTo(plotW, yy); ctx.stroke();
        ctx.setLineDash([]);
        ctx.fillStyle = color;
        ctx.fillText(label, 8, yy - 4);
      };
      level(+ps.entry, ps.side === 'LONG' ? C.green : C.red, `${ps.side === 'LONG' ? 'Лонг' : 'Шорт'} ${Math.abs(+ps.size)} @ ${fmtN(ps.entry, pd)}`);
      if (+ps.liqPrice > 0) level(+ps.liqPrice, '#f0a020', `Ліквідація ${fmtN(ps.liqPrice, pd)}`);
    }
    // перехрестя
    if (S.hover) {
      const { mx, my } = S.hover;
      if (mx < plotW && my < plotH) {
        const i = Math.min(k.length - 1, Math.max(0, Math.floor(mx / slot) - off));
        const c = k[i];
        ctx.strokeStyle = C.muted;
        ctx.setLineDash([2, 4]);
        ctx.beginPath(); ctx.moveTo(xAt(i), 0); ctx.lineTo(xAt(i), plotH); ctx.moveTo(0, my); ctx.lineTo(plotW, my); ctx.stroke();
        ctx.setLineDash([]);
        if (my < priceH) {
          const p = hi - ((my - 6) / (priceH - 6)) * (hi - lo);
          ctx.fillStyle = '#2b3139';
          ctx.fillRect(plotW, my - 9, axisW, 18);
          ctx.fillStyle = '#fff';
          ctx.fillText(fmtN(p, pd), plotW + 6, my + 4);
        }
        showOhlc(c);
        return;
      }
    }
    showOhlc(k[k.length - 1]);
  }

  function showOhlc(c) {
    const pd = decimals(S.m.tick);
    const up = +c[4] >= +c[1];
    const cls = up ? 'green' : 'red';
    $('#ohlc').innerHTML = `${dt(c[0])} &nbsp; В <span class="${cls}">${fmtN(c[1], pd)}</span> &nbsp;М <span class="${cls}">${fmtN(c[2], pd)}</span>
      &nbsp;Мн <span class="${cls}">${fmtN(c[3], pd)}</span> &nbsp;З <span class="${cls}">${fmtN(c[4], pd)}</span> &nbsp;Об ${fmtN(c[5], 3)}`;
  }

  let drawQueued = false;
  function queueDraw() {
    if (drawQueued) return;
    drawQueued = true;
    requestAnimationFrame(() => {
      drawQueued = false;
      drawChart();
    });
  }

  function applyTradeToKlines(t) {
    const iv = IV_MS[S.interval];
    const bucket = t.ts - (t.ts % iv);
    const last = S.klines[S.klines.length - 1];
    if (last && last[0] === bucket) {
      last[2] = String(Math.max(+last[2], +t.price));
      last[3] = String(Math.min(+last[3], +t.price));
      last[4] = t.price;
      last[5] = String(+last[5] + +t.qty);
    } else if (!last || bucket > last[0]) {
      S.klines.push([bucket, t.price, t.price, t.price, t.price, t.qty]);
      if (S.klines.length > 1000) S.klines.shift();
    }
    queueDraw();
  }

  // ---------------- order form (ф'ючерси) ----------------
  const levOf = (sym) => S.leverages[sym] || 10;
  const posOf = (sym) => S.positions.find((p) => p.symbol === sym);
  const F = () => $('#order-form');

  function renderForms() {
    if (!S.m) return;
    const m = S.m;
    const f = F();
    $('#tif-wrap').classList.toggle('hidden', S.type !== 'LIMIT');
    const market = S.type === 'MARKET';
    const prev = { price: f.price?.value || '', qty: f.qty?.value || '', ro: f.reduceOnly?.checked || false };
    f.innerHTML = `
      <div class="fut-top"><span class="chip" title="Маржа кожної позиції окрема: втратити можна не більше за неї">Ізольована</span>
        <button type="button" class="chip lev-btn" id="lev-btn" title="Змінити плече">${levOf(S.sym)}x</button>
        <span class="spacer"></span><span class="avail">Доступно&nbsp;<b class="num" data-avail></b></span></div>
      <label class="field"><span>Ціна</span><input name="price" inputmode="decimal" ${market ? 'disabled placeholder="Ринкова"' : ''}><span>USDT</span></label>
      <label class="field"><span>Кількість</span><input name="qty" inputmode="decimal" placeholder="0"><span>${m.base}</span></label>
      <div class="pcts">${[25, 50, 75, 100].map((p) => `<button type="button" data-pct="${p}">${p}%</button>`).join('')}</div>
      <div class="fut-info"><span>Вартість <b class="num" data-notional>—</b> USDT · Маржа <b class="num" data-cost>—</b> USDT</span>
        <label class="chk" title="Ордер лише зменшує/закриває позицію і ніколи не відкриває нову"><input type="checkbox" name="reduceOnly"> Reduce-only</label></div>
      <div class="fut-btns">
        <button type="submit" class="btn buy" data-side="BUY">${S.me ? 'Купити / Лонг' : 'Увійдіть, щоб торгувати'}</button>
        <button type="submit" class="btn sell" data-side="SELL">${S.me ? 'Продати / Шорт' : 'Увійдіть, щоб торгувати'}</button>
      </div>`;
    if (!market) f.price.value = prev.price || S.tickers[S.sym]?.last || '';
    f.qty.value = prev.qty;
    f.reduceOnly.checked = prev.ro;
    renderAvail();
  }

  const refPrice = () => {
    const f = F();
    const p = S.type === 'MARKET' ? NaN : parseFloat(f.price?.value);
    return p > 0 ? p : +(S.tickers[S.sym]?.mark || S.tickers[S.sym]?.last || 0);
  };

  function renderAvail() {
    if (!S.m) return;
    const f = F();
    const el = f.querySelector('[data-avail]');
    if (el) el.textContent = S.me && S.account ? `${fmtN(S.account.available, 2)} USDT` : '—';
    const q = parseFloat(f.qty?.value);
    const px = refPrice();
    const notional = q > 0 && px > 0 ? q * px : 0;
    const n = f.querySelector('[data-notional]'), c = f.querySelector('[data-cost]');
    if (n) n.textContent = notional ? fmtN(notional, 2) : '—';
    if (c) c.textContent = notional ? fmtN(f.reduceOnly?.checked ? 0 : notional / levOf(S.sym), 2) : '—';
    const lb = $('#lev-btn');
    if (lb) lb.textContent = `${levOf(S.sym)}x`;
  }

  function onPct(pct) {
    if (!S.me) return openModal('login');
    const f = F();
    const qd = decimals(S.m.step);
    const r = pct / 100;
    const ps = posOf(S.sym);
    if (f.reduceOnly.checked && ps) f.qty.value = floorTo(Math.abs(+ps.size) * r, qd);
    else {
      const px = refPrice();
      // запас 0.3% на комісію і рух ціни
      if (px > 0) f.qty.value = floorTo((+(S.account?.available || 0) * levOf(S.sym) * r * 0.997) / px, qd);
    }
    renderAvail();
  }

  async function submitOrder(side, btn) {
    if (!S.me) return openModal('login');
    const f = F();
    const body = { symbol: S.sym, side, type: S.type, qty: f.qty.value.trim(), reduceOnly: f.reduceOnly.checked };
    if (S.type !== 'MARKET') {
      body.price = f.price.value.trim();
      if (S.type === 'LIMIT') body.tif = $('#tif').value;
    }
    btn.disabled = true;
    try {
      const r = await api('POST', '/api/order', body);
      const o = r.order;
      const label = `${side === 'BUY' ? 'Лонг' : 'Шорт'} ${S.m.base}${body.reduceOnly ? ' (reduce-only)' : ''}`;
      const pnl = +o.realizedPnl ? `, реалізований PnL ${+o.realizedPnl > 0 ? '+' : ''}${fmtN(o.realizedPnl, 2)} USDT` : '';
      if (o.status === 'FILLED') toast(`${label}: виконано ${o.filled} за ${fmtN(o.avgPrice, decimals(S.m.tick))}${pnl}`, 'ok');
      else if (o.status === 'EXPIRED') toast(`${label}: ${+o.filled ? `частково виконано ${o.filled}, решту скасовано` : 'не виконано (немає зустрічних ордерів)'}`, +o.filled ? 'ok' : 'err');
      else toast(`${label}: ордер #${o.id} розміщено${+o.filled ? `, виконано ${o.filled}` : ''}`, 'ok');
      f.qty.value = '';
      renderAvail();
      refreshPrivate();
    } catch (e) {
      toast(e.message, 'err');
      if (e.status === 401) openModal('login');
    } finally {
      btn.disabled = false;
    }
  }

  // ---------------- плече ----------------
  function openLeverage() {
    if (!S.me) return openModal('login');
    const max = S.m.maxLeverage || 50;
    const r = $('#lev-range');
    r.max = max;
    r.value = levOf(S.sym);
    $('#lev-sym').textContent = `${S.m.base}/USDT`;
    $('#lev-quick').innerHTML = [1, 5, 10, 20, 50, 100].filter((x) => x <= max).map((x) => `<button type="button" data-lev="${x}">${x}x</button>`).join('');
    syncLev();
    $('#lev-modal').classList.remove('hidden');
  }
  function syncLev() {
    const v = +$('#lev-range').value;
    $('#lev-val').textContent = `${v}x`;
    $('#lev-hint').textContent = `Макс. позиція при поточному балансі ≈ ${fmtN(+(S.account?.available || 0) * v, 0)} USDT. ` +
      (v >= 20 ? 'Високе плече — ліквідація навіть при невеликому русі ціни.' : '');
  }
  async function saveLeverage() {
    try {
      const r = await api('POST', '/api/leverage', { symbol: S.sym, leverage: +$('#lev-range').value });
      S.leverages[r.symbol] = r.leverage;
      $('#lev-modal').classList.add('hidden');
      toast(`Плече ${r.symbol}: ${r.leverage}x`, 'ok');
      renderAvail();
    } catch (e) {
      toast(e.message, 'err');
    }
  }

  // ---------------- account tables ----------------
  function renderAcc() {
    const body = $('#acc-body');
    $('#open-count').textContent = S.open.length ? `(${S.open.length})` : '';
    $('#pos-count').textContent = S.positions.length ? `(${S.positions.length})` : '';
    $('#cancel-all').classList.toggle('hidden', S.tab !== 'open' || !S.open.length);
    if (!S.me) {
      body.innerHTML = `<div class="empty">Увійдіть або зареєструйтесь, щоб торгувати — нові акаунти отримують демо-баланс.</div>`;
      return;
    }
    const mk = (sym) => S.markets.find((m) => m.symbol === sym);
    const pair = (sym) => { const m = mk(sym); return m ? `${m.base}USDT` : sym; };
    const pdOf = (sym) => decimals(mk(sym)?.tick || '0.01');
    const qdOf = (sym) => decimals(mk(sym)?.step || '0.0001');
    const cls = (v) => (+v >= 0 ? 'green' : 'red');
    const sign = (v) => (+v > 0 ? '+' : '');
    const sideCell = (s, ro) => `<td class="${s === 'BUY' ? 'green' : 'red'}">${s === 'BUY' ? 'Купівля' : 'Продаж'}${ro ? ' <span class="muted">RO</span>' : ''}</td>`;

    if (S.tab === 'positions') {
      if (!S.positions.length) {
        body.innerHTML = `<div class="empty">Немає відкритих позицій.<br><span class="muted">Відкрийте лонг (ставка на зростання) або шорт (на падіння) у формі вище.</span></div>`;
        return;
      }
      body.innerHTML = `<table><thead><tr><th>Пара</th><th class="r">Розмір</th><th class="r">Вартість</th><th class="r">Ціна входу</th>
        <th class="r">Ціна маркування</th><th class="r">Ціна ліквідації</th><th class="r">Маржа</th><th class="r">PnL (ROE%)</th><th></th></tr></thead><tbody>
        ${S.positions.map((p) => {
          const m = mk(p.symbol), pd = pdOf(p.symbol);
          return `<tr><td><b>${pair(p.symbol)}</b><span class="badge ${p.side === 'LONG' ? 'long' : 'short'}">${p.side === 'LONG' ? 'Лонг' : 'Шорт'}</span><span class="badge lev">${p.leverage}x</span></td>
            <td class="r ${p.side === 'LONG' ? 'green' : 'red'}">${fmtN(p.size, qdOf(p.symbol))} ${m?.base || ''}</td>
            <td class="r">${fmtN(p.notional, 2)}</td><td class="r">${fmtN(p.entry, pd)}</td><td class="r">${fmtN(p.mark, pd)}</td>
            <td class="r liq">${p.liqPrice ? fmtN(p.liqPrice, pd) : '—'}</td><td class="r">${fmtN(p.margin, 2)}</td>
            <td class="r ${cls(p.unrealized)}">${sign(p.unrealized)}${fmtN(p.unrealized, 2)} USDT<br><small>(${sign(p.roePct)}${p.roePct.toFixed(2)}%)</small></td>
            <td><button class="btn close-btn" data-close="${p.symbol}">Закрити</button></td></tr>`;
        }).join('')}</tbody></table>
        <p class="hint" style="padding:8px 16px">«Закрити» закриває всю позицію за ринковою ціною. Частково — reduce-only ордером у формі.
        Якщо ціна маркування дійде до ціни ліквідації, позицію буде закрито примусово, а маржу втрачено.</p>`;
    } else if (S.tab === 'open' || S.tab === 'history') {
      const list = S.tab === 'open' ? S.open : S.history;
      if (!list.length) {
        body.innerHTML = S.tab === 'open'
          ? `<div class="empty">Немає відкритих ордерів.<br><span class="muted">Ринкові ордери виконуються одразу — відкриті позиції у вкладці «Позиції».</span></div>`
          : `<div class="empty">Немає ордерів</div>`;
        return;
      }
      body.innerHTML = `<table><thead><tr><th>Час</th><th>Пара</th><th>Тип</th><th>Сторона</th><th class="r">Ціна</th><th class="r">Сер. ціна</th>
        <th class="r">Кількість</th><th class="r">Виконано</th><th class="r">PnL</th><th>Статус</th><th></th></tr></thead><tbody>
        ${list.map((o) => `<tr><td class="muted">${dt(o.created)}</td><td>${pair(o.symbol)} <span class="muted">${o.leverage}x</span></td>
          <td>${TYPE[o.type] || o.type}${o.tif && o.tif !== 'GTC' && o.type !== 'LIQUIDATION' ? ' ' + o.tif : ''}</td>
          ${sideCell(o.side, o.reduceOnly)}<td class="r">${o.price ? fmtN(o.price, pdOf(o.symbol)) : 'Ринкова'}</td><td class="r">${o.avgPrice ? fmtN(o.avgPrice, pdOf(o.symbol)) : '—'}</td>
          <td class="r">${fmtN(o.qty, qdOf(o.symbol))}</td><td class="r">${fmtN(o.filled, qdOf(o.symbol))}</td>
          <td class="r ${+o.realizedPnl ? cls(o.realizedPnl) : 'muted'}">${+o.realizedPnl ? sign(o.realizedPnl) + fmtN(o.realizedPnl, 2) : '—'}</td>
          <td>${STATUS[o.status] || o.status}</td>
          <td>${S.tab === 'open' ? `<button class="link-btn" data-cancel="${o.id}">Скасувати</button>` : ''}</td></tr>`).join('')}
        </tbody></table>`;
    } else if (S.tab === 'mytrades') {
      if (!S.myTrades.length) { body.innerHTML = `<div class="empty">Ще немає угод</div>`; return; }
      body.innerHTML = `<table><thead><tr><th>Час</th><th>Пара</th><th>Сторона</th><th class="r">Ціна</th><th class="r">Кількість</th>
        <th class="r">Вартість</th><th class="r">Комісія</th><th class="r">Реаліз. PnL</th><th>Роль</th></tr></thead><tbody>
        ${S.myTrades.map((t) => `<tr><td class="muted">${dt(t.ts)}</td><td>${pair(t.symbol)}</td>${sideCell(t.side)}
          <td class="r">${fmtN(t.price, pdOf(t.symbol))}</td><td class="r">${fmtN(t.qty, qdOf(t.symbol))}</td><td class="r">${fmtN(t.quoteQty, 2)}</td>
          <td class="r">${fmtN(t.fee, 4)} USDT</td><td class="r ${+t.realizedPnl ? cls(t.realizedPnl) : 'muted'}">${+t.realizedPnl ? sign(t.realizedPnl) + fmtN(t.realizedPnl, 2) : '—'}</td>
          <td class="muted">${t.maker ? 'Maker' : 'Taker'}</td></tr>`).join('')}
        </tbody></table>`;
    } else {
      const a = S.account;
      if (!a) { body.innerHTML = ''; return; }
      body.innerHTML = `<div class="summary">
          <div><small>Капітал (з нереаліз. PnL)</small><b class="num">${fmtN(a.equity, 2)}</b></div>
          <div><small>Баланс гаманця</small><b class="num">${fmtN(a.walletBalance, 2)}</b></div>
          <div><small>Доступно</small><b class="num">${fmtN(a.available, 2)}</b></div>
          <div><small>Нереалізований PnL</small><b class="num ${cls(a.unrealized)}">${sign(a.unrealized)}${fmtN(a.unrealized, 2)}</b></div>
          <div><small>Реалізований PnL</small><b class="num ${cls(a.realized)}">${sign(a.realized)}${fmtN(a.realized, 2)}</b></div>
          <div class="spacer"></div><button class="btn" id="faucet">+ Поповнити демо-USDT</button>
        </div>
        <div class="summary" style="padding-top:0">
          <div><small>Маржа позицій</small><span class="num">${fmtN(a.positionMargin, 2)}</span></div>
          <div><small>Маржа під ордери</small><span class="num">${fmtN(a.orderMargin, 2)}</span></div>
          <div><small>Сплачено комісій</small><span class="num">${fmtN(a.fees, 2)}</span></div>
        </div>`;
      $('#faucet').onclick = async () => {
        try {
          await api('POST', '/api/faucet');
          toast('Зараховано демо-USDT', 'ok');
          loadMe();
        } catch (e) { toast(e.message, 'err'); }
      };
    }
  }

  let accQueued = false;
  function queueAcc() {
    if (accQueued) return;
    accQueued = true;
    setTimeout(() => { accQueued = false; renderAcc(); }, 150);
  }

  async function refreshPrivate() {
    if (!S.me) return;
    try {
      const [open, history, my] = await Promise.all([
        api('GET', '/api/orders/open'),
        S.tab === 'history' ? api('GET', '/api/orders/history?limit=100') : S.history,
        S.tab === 'mytrades' ? api('GET', '/api/my-trades?limit=100') : S.myTrades,
      ]);
      S.open = open;
      S.history = history;
      S.myTrades = my;
      renderAcc();
    } catch (e) {
      if (e.status === 401) { S.me = null; renderAll(); }
    }
  }

  // Закрити позицію повністю ринковим reduce-only ордером
  async function closePosition(symbol, btn) {
    const p = posOf(symbol);
    if (!p) return;
    const m = S.markets.find((x) => x.symbol === symbol);
    if (!confirm(`Закрити ${p.side === 'LONG' ? 'лонг' : 'шорт'} ${Math.abs(+p.size)} ${m.base} за ринковою ціною?`)) return;
    btn.disabled = true;
    try {
      const r = await api('POST', '/api/position/close', { symbol });
      const o = r.order;
      if (+o.filled > 0)
        toast(`Позицію ${m.base} закрито за ${fmtN(o.avgPrice, decimals(m.tick))}: PnL ${+o.realizedPnl > 0 ? '+' : ''}${fmtN(o.realizedPnl, 2)} USDT`, +o.realizedPnl >= 0 ? 'ok' : 'err');
      else toast('Не вдалося закрити: немає зустрічних ордерів поблизу ціни', 'err');
      refreshPrivate();
    } catch (err) {
      toast(err.message, 'err');
    } finally {
      btn.disabled = false;
    }
  }

  // ---------------- auth modal ----------------
  let authMode = 'login';
  function openModal(mode) {
    authMode = mode;
    $('#modal').classList.remove('hidden');
    for (const b of document.querySelectorAll('#auth-tabs button')) b.classList.toggle('active', b.dataset.mode === mode);
    $('#auth-submit').textContent = mode === 'login' ? 'Увійти' : 'Створити акаунт';
    $('#auth-error').textContent = '';
    const bonus = S.config?.signupBonus;
    $('#auth-hint').textContent = mode === 'register' && bonus ? `Демо-баланс при реєстрації: ${Object.entries(bonus).map(([a, v]) => `${v} ${a}`).join(', ')}` : '';
    $('#auth-form').password.autocomplete = mode === 'login' ? 'current-password' : 'new-password';
    $('#auth-form').username.focus();
  }

  async function submitAuth(e) {
    e.preventDefault();
    const f = e.target;
    try {
      const r = await api('POST', `/api/${authMode}`, { username: f.username.value.trim(), password: f.password.value });
      f.reset();
      $('#modal').classList.add('hidden');
      S.me = { id: r.id, username: r.username };
      toast(authMode === 'login' ? `Вітаємо, ${r.username}!` : 'Акаунт створено, демо-баланс зараховано', 'ok');
      await loadMe();
      connect();
    } catch (err) {
      $('#auth-error').textContent = err.message;
    }
  }

  async function loadMe() {
    try {
      const me = await api('GET', '/api/me');
      S.me = { id: me.id, username: me.username };
      S.account = me.account;
      S.positions = me.positions;
      S.leverages = me.leverages || {};
    } catch {
      S.me = null;
    }
    renderAll();
    refreshPrivate();
  }

  // ---------------- streaming ----------------
  function onDepth(d) {
    if (d.symbol !== S.sym) return;
    S.depth = d;
    renderBook();
  }
  function onTrades(all) {
    const list = all.filter((t) => t.symbol === S.sym && t.id > S.lastTradeId);
    if (!list.length) return;
    for (const t of list) {
      S.trades.unshift(t);
      applyTradeToKlines(t);
    }
    S.lastTradeId = list[list.length - 1].id;
    S.trades.length = Math.min(S.trades.length, 100);
    if (S.tickers[S.sym]) S.tickers[S.sym].last = list[list.length - 1].price;
    renderTrades();
    renderTicker();
  }
  function onTickers(list) {
    for (const t of list) S.tickers[t.symbol] = t;
    renderMarkets();
    renderTicker();
    renderBook();
  }
  function onAccount(d) {
    const had = new Set(S.positions.map((p) => p.symbol));
    S.account = d.account;
    S.positions = d.positions;
    renderAvail();
    renderAccountBar();
    if (S.tab === 'positions' || S.tab === 'wallet' || had.size !== S.positions.length) queueAcc();
    queueDraw();
  }
  function onOrder(o) {
    if (o.type === 'LIQUIDATION' && o.status === 'FILLED')
      toast(`⚠ Позицію ${o.symbol} ліквідовано за ${fmtN(o.avgPrice, decimals(S.markets.find((m) => m.symbol === o.symbol)?.tick || '0.01'))}`, 'err');
    const i = S.open.findIndex((x) => x.id === o.id);
    const isOpen = o.status === 'NEW' || o.status === 'PARTIALLY_FILLED';
    if (i >= 0) {
      if (isOpen) S.open[i] = o;
      else S.open.splice(i, 1);
    } else if (isOpen) S.open.unshift(o);
    const h = S.history.findIndex((x) => x.id === o.id);
    if (h >= 0) S.history[h] = o;
    else S.history.unshift(o);
    queueAcc();
  }

  function stopRealtime() {
    if (S.es) S.es.close();
    S.es = null;
    clearTimeout(S.pollTimer);
    clearTimeout(S.sseWatchdog);
    S.pollGen = (S.pollGen || 0) + 1;
  }

  function connect() {
    stopRealtime();
    // Якщо стрім уже не пройшов у цій мережі — одразу опитування
    if (S.mode === 'poll') return startPolling();
    const es = new EventSource(`/api/stream?symbol=${S.sym}`);
    S.es = es;
    let alive = false;
    const on = (name, fn) => es.addEventListener(name, (e) => { alive = true; fn(JSON.parse(e.data)); });
    on('depth', onDepth);
    on('trades', onTrades);
    on('tickers', onTickers);
    on('account', onAccount);
    on('order', onOrder);
    let myTradeTimer = null;
    on('myTrade', () => {
      // повні дані угоди (комісія, роль) підтягуємо з API, не частіше ніж раз на 0.5 с
      if (S.tab !== 'mytrades' || myTradeTimer) return;
      myTradeTimer = setTimeout(() => { myTradeTimer = null; refreshPrivate(); }, 500);
    });
    // Сервер шле дані одразу після підключення; якщо за 6 с нічого — мережа (проксі/тунель)
    // не пропускає стрім, переходимо на опитування раз на секунду.
    S.sseWatchdog = setTimeout(() => {
      if (alive) return;
      S.mode = 'poll';
      connect();
    }, 6000);
  }

  function startPolling() {
    const gen = S.pollGen;
    let lastOpen = '';
    const tick = async () => {
      if (gen !== S.pollGen) return;
      try {
        const d = await api('GET', `/api/poll?symbol=${S.sym}&since=${S.lastTradeId}`);
        if (gen !== S.pollGen) return;
        onDepth(d.depth);
        onTickers(d.tickers);
        onTrades(d.trades);
        if (d.account) {
          onAccount(d);
          const sig = JSON.stringify(d.open);
          if (sig !== lastOpen) {
            lastOpen = sig;
            S.open = d.open;
            queueAcc();
          }
        }
      } catch {}
      if (gen === S.pollGen) S.pollTimer = setTimeout(tick, document.hidden ? 5000 : 1000);
    };
    tick();
  }

  // ---------------- market switching ----------------
  async function selectMarket(sym) {
    S.sym = sym;
    localStorage.setItem('sym', sym);
    S.m = S.markets.find((m) => m.symbol === sym);
    S.depth = { bids: [], asks: [] };
    S.trades = [];
    const [depth, trades, klines] = await Promise.all([
      api('GET', `/api/depth?symbol=${sym}&limit=20`),
      api('GET', `/api/trades?symbol=${sym}&limit=60`),
      api('GET', `/api/klines?symbol=${sym}&interval=${S.interval}&limit=400`),
    ]);
    S.depth = depth;
    S.trades = trades;
    S.lastTradeId = trades[0]?.id || 0;
    S.klines = klines;
    if (F().price) F().price.value = '';
    renderAll();
    connect();
  }

  async function loadKlines() {
    S.klines = await api('GET', `/api/klines?symbol=${S.sym}&interval=${S.interval}&limit=400`);
    renderIntervals();
    queueDraw();
  }

  function renderAll() {
    renderMarkets();
    renderTicker();
    renderAccountBar();
    renderBook();
    renderTrades();
    renderIntervals();
    renderForms();
    renderAcc();
    queueDraw();
  }

  // ---------------- events ----------------
  $('#markets').addEventListener('click', (e) => {
    if (e.target.closest('#pair-btn')) togglePairs($('#pair-panel').classList.contains('hidden'));
  });
  $('#pair-search').addEventListener('input', renderPairList);
  $('#pair-search').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      const first = $('#pair-list [data-sym]');
      if (first) first.click();
    }
  });
  $('#pair-list').addEventListener('click', (e) => {
    const r = e.target.closest('[data-sym]');
    if (!r) return;
    togglePairs(false);
    if (r.dataset.sym !== S.sym) selectMarket(r.dataset.sym);
  });
  document.addEventListener('click', (e) => {
    if (!e.target.closest('#pair-panel') && !e.target.closest('#pair-btn')) togglePairs(false);
  });
  $('#intervals').addEventListener('click', (e) => {
    const b = e.target.closest('[data-iv]');
    if (!b) return;
    S.interval = b.dataset.iv;
    localStorage.setItem('iv', S.interval);
    loadKlines();
  });
  $('#type-tabs').addEventListener('click', (e) => {
    const b = e.target.closest('[data-type]');
    if (!b) return;
    S.type = b.dataset.type;
    for (const x of document.querySelectorAll('#type-tabs [data-type]')) x.classList.toggle('active', x === b);
    renderForms();
  });
  $('#acc-tabs').addEventListener('click', (e) => {
    const b = e.target.closest('[data-tab]');
    if (!b) return;
    S.tab = b.dataset.tab;
    for (const x of document.querySelectorAll('#acc-tabs [data-tab]')) x.classList.toggle('active', x === b);
    renderAcc();
    refreshPrivate();
  });
  $('#cancel-all').addEventListener('click', async () => {
    try {
      const r = await api('DELETE', '/api/orders');
      toast(`Скасовано ордерів: ${r.canceled}`, 'ok');
      refreshPrivate();
    } catch (e) { toast(e.message, 'err'); }
  });
  $('#acc-body').addEventListener('click', async (e) => {
    const cl = e.target.closest('[data-close]');
    if (cl) return closePosition(cl.dataset.close, cl);
    const b = e.target.closest('[data-cancel]');
    if (!b) return;
    try {
      await api('DELETE', `/api/order?id=${b.dataset.cancel}`);
      toast(`Ордер #${b.dataset.cancel} скасовано`, 'ok');
    } catch (err) { toast(err.message, 'err'); }
    refreshPrivate();
  });
  for (const id of ['#asks', '#bids']) {
    $(id).addEventListener('click', (e) => {
      const r = e.target.closest('[data-price]');
      if (!r || S.type === 'MARKET') return;
      F().price.value = r.dataset.price;
      renderAvail();
    });
  }
  F().addEventListener('input', renderAvail);
  F().addEventListener('change', renderAvail);
  F().addEventListener('submit', (e) => {
    e.preventDefault();
    const btn = e.submitter && e.submitter.dataset.side ? e.submitter : null;
    if (btn) submitOrder(btn.dataset.side, btn);
  });
  F().addEventListener('click', (e) => {
    const b = e.target.closest('[data-pct]');
    if (b) onPct(+b.dataset.pct);
    if (e.target.closest('#lev-btn')) openLeverage();
  });
  $('#lev-range').addEventListener('input', syncLev);
  $('#lev-quick').addEventListener('click', (e) => {
    const b = e.target.closest('[data-lev]');
    if (b) { $('#lev-range').value = b.dataset.lev; syncLev(); }
  });
  for (const b of document.querySelectorAll('[data-lev-step]'))
    b.addEventListener('click', () => { const r = $('#lev-range'); r.value = +r.value + +b.dataset.levStep; syncLev(); });
  $('#lev-save').addEventListener('click', saveLeverage);
  $('#lev-close').addEventListener('click', () => $('#lev-modal').classList.add('hidden'));
  $('#lev-modal').addEventListener('click', (e) => { if (e.target.id === 'lev-modal') $('#lev-modal').classList.add('hidden'); });
  $('#auth-tabs').addEventListener('click', (e) => {
    const b = e.target.closest('[data-mode]');
    if (b) openModal(b.dataset.mode);
  });
  $('#auth-form').addEventListener('submit', submitAuth);
  $('#modal-close').onclick = () => $('#modal').classList.add('hidden');
  $('#modal').addEventListener('click', (e) => { if (e.target.id === 'modal') $('#modal').classList.add('hidden'); });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      $('#modal').classList.add('hidden');
      $('#lev-modal').classList.add('hidden');
      togglePairs(false);
    }
  });

  canvas.addEventListener('mousemove', (e) => {
    const r = canvas.getBoundingClientRect();
    S.hover = { mx: e.clientX - r.left, my: e.clientY - r.top };
    queueDraw();
  });
  canvas.addEventListener('mouseleave', () => { S.hover = null; queueDraw(); });
  canvas.addEventListener('wheel', (e) => {
    e.preventDefault();
    S.visible = Math.max(20, Math.min(400, Math.round(S.visible * (e.deltaY > 0 ? 1.15 : 0.87))));
    queueDraw();
  }, { passive: false });
  new ResizeObserver(queueDraw).observe(canvas.parentElement);
  setInterval(() => { if (S.me && S.tab === 'mytrades') refreshPrivate(); }, 5000);
  setInterval(() => { if (!document.hidden && S.m) loadKlines().catch(() => {}); }, 30000);

  // ---------------- boot ----------------
  (async () => {
    [S.markets, S.config] = await Promise.all([api('GET', '/api/markets'), api('GET', '/api/config')]);
    for (const t of await api('GET', '/api/ticker')) S.tickers[t.symbol] = t;
    if (!S.markets.some((m) => m.symbol === S.sym)) S.sym = S.markets[0].symbol;
    await loadMe();
    await selectMarket(S.sym);
  })().catch((e) => toast('Помилка завантаження: ' + e.message, 'err'));
})();
