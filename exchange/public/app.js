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
  const TYPE = { LIMIT: 'Лімітний', MARKET: 'Ринковий', LIMIT_MAKER: 'Post-only' };

  const S = {
    markets: [], m: null, sym: localStorage.getItem('sym') || 'BTCUSDT', interval: localStorage.getItem('iv') || '1m',
    me: null, balances: {}, pnl: null, open: [], history: [], myTrades: [], tickers: {},
    depth: { bids: [], asks: [] }, trades: [], klines: [], type: 'LIMIT', tab: 'open', es: null, hover: null, mode: 'sse', lastTradeId: 0,
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
    $('#markets').innerHTML = S.markets
      .map((m) => {
        const t = S.tickers[m.symbol];
        const ch = t ? t.changePct : 0;
        return `<button data-sym="${m.symbol}" class="${m.symbol === S.sym ? 'active' : ''}">${m.base}/${m.quote}
          <small class="${ch >= 0 ? 'green' : 'red'}">${t ? fmtN(t.last, decimals(m.tick)) : ''} ${ch >= 0 ? '+' : ''}${ch.toFixed(2)}%</small></button>`;
      })
      .join('');
  }

  function renderTicker() {
    const t = S.tickers[S.sym];
    if (!t || !S.m) return;
    const pd = decimals(S.m.tick);
    const up = t.changePct >= 0;
    $('#ticker').innerHTML = `
      <div><span class="big num ${up ? 'green' : 'red'}">${fmtN(t.last, pd)}</span></div>
      <div><small>Зміна 24г</small><span class="num ${up ? 'green' : 'red'}">${up ? '+' : ''}${t.changePct.toFixed(2)}%</span></div>
      <div class="hide-sm"><small>Макс 24г</small><span class="num">${fmtN(t.high, pd)}</span></div>
      <div class="hide-sm"><small>Мін 24г</small><span class="num">${fmtN(t.low, pd)}</span></div>
      <div class="hide-sm"><small>Обсяг 24г (${S.m.base})</small><span class="num">${fmtN(t.volume, 2)}</span></div>
      <div class="hide-sm"><small>Обсяг 24г (${S.m.quote})</small><span class="num">${fmtN(t.quoteVolume, 0)}</span></div>`;
    document.title = `${fmtN(t.last, pd)} | ${S.m.base}/${S.m.quote} — MiniEx`;
  }

  function renderAccountBar() {
    const bar = $('#account-bar');
    if (!S.me) {
      bar.innerHTML = `<button class="btn" id="btn-login">Увійти</button><button class="btn primary" id="btn-register">Реєстрація</button>`;
      $('#btn-login').onclick = () => openModal('login');
      $('#btn-register').onclick = () => openModal('register');
      return;
    }
    const eq = S.pnl ? fmtN(S.pnl.equity, 2) : '—';
    bar.innerHTML = `<span class="muted">Капітал:</span> <b class="num">${eq} USDT</b>
      <span class="muted" id="uname"></span><button class="btn" id="btn-logout">Вийти</button>`;
    $('#uname').textContent = S.me.username;
    $('#btn-logout').onclick = async () => {
      await api('POST', '/api/logout').catch(() => {});
      S.me = null;
      S.balances = {};
      S.pnl = null;
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
    const slot = plotW / k.length;
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
      const x = i * slot + slot / 2;
      const d = new Date(k[i][0]);
      const label = IV_MS[S.interval] >= 86400e3 ? `${d.getDate()}.${d.getMonth() + 1}` : d.toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' });
      ctx.fillText(label, x - 14, H - 6);
    }
    k.forEach((c, i) => {
      const [, o, h, l, cl, v] = c.map(Number);
      const x = i * slot + slot / 2;
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
    // перехрестя
    if (S.hover) {
      const { mx, my } = S.hover;
      if (mx < plotW && my < plotH) {
        const i = Math.min(k.length - 1, Math.max(0, Math.floor(mx / slot)));
        const c = k[i];
        ctx.strokeStyle = C.muted;
        ctx.setLineDash([2, 4]);
        ctx.beginPath(); ctx.moveTo(i * slot + slot / 2, 0); ctx.lineTo(i * slot + slot / 2, plotH); ctx.moveTo(0, my); ctx.lineTo(plotW, my); ctx.stroke();
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

  // ---------------- order forms ----------------
  function renderForms() {
    if (!S.m) return;
    const m = S.m;
    $('#tif-wrap').classList.toggle('hidden', S.type !== 'LIMIT');
    for (const side of ['BUY', 'SELL']) {
      const f = $(`#form-${side.toLowerCase()}`);
      const buy = side === 'BUY';
      const market = S.type === 'MARKET';
      const priceVal = f.price?.value || '';
      const qtyVal = f.qty?.value || '';
      const totalVal = f.total?.value || '';
      f.innerHTML = `
        <div class="avail"><span>Доступно</span><b class="num" data-avail></b></div>
        <label class="field"><span>Ціна</span><input name="price" inputmode="decimal" autocomplete="off" ${market ? 'disabled placeholder="Ринкова"' : ''}><span>${m.quote}</span></label>
        ${market && buy
          ? `<label class="field"><span>Сума</span><input name="total" inputmode="decimal" autocomplete="off" placeholder="0"><span>${m.quote}</span></label>`
          : `<label class="field"><span>Кількість</span><input name="qty" inputmode="decimal" autocomplete="off" placeholder="0"><span>${m.base}</span></label>`}
        <div class="pcts">${[25, 50, 75, 100].map((p) => `<button type="button" data-pct="${p}">${p}%</button>`).join('')}</div>
        ${market ? '' : `<label class="field"><span>Сума</span><input name="total" inputmode="decimal" autocomplete="off" placeholder="0"><span>${m.quote}</span></label>`}
        <button type="submit" class="btn ${buy ? 'buy' : 'sell'}">${S.me ? (buy ? 'Купити ' : 'Продати ') + m.base : 'Увійдіть, щоб торгувати'}</button>`;
      if (!market) f.price.value = priceVal || S.tickers[S.sym]?.last || '';
      if (f.qty) f.qty.value = qtyVal;
      if (f.total && market) f.total.value = totalVal;
      syncTotal(f);
    }
    renderAvail();
  }

  function renderAvail() {
    if (!S.m) return;
    for (const side of ['BUY', 'SELL']) {
      const asset = side === 'BUY' ? S.m.quote : S.m.base;
      const b = S.balances[asset];
      const el = $(`#form-${side.toLowerCase()} [data-avail]`);
      if (el) el.textContent = S.me ? `${fmtN(b?.free ?? 0, side === 'BUY' ? 2 : decimals(S.m.step))} ${asset}` : '—';
    }
  }

  function syncTotal(f) {
    if (S.type === 'MARKET' || !f.total) return;
    const p = parseFloat(f.price.value), q = parseFloat(f.qty.value);
    f.total.value = p > 0 && q > 0 ? (p * q).toFixed(2) : '';
  }

  function onFormInput(e) {
    const f = e.target.form;
    if (!f || S.type === 'MARKET') return;
    if (e.target.name === 'total') {
      const p = parseFloat(f.price.value), t = parseFloat(f.total.value);
      f.qty.value = p > 0 && t > 0 ? floorTo(t / p, decimals(S.m.step)) : '';
    } else syncTotal(f);
  }

  function onPct(f, pct) {
    if (!S.me) return openModal('login');
    const side = f.dataset.side;
    const qd = decimals(S.m.step);
    const r = pct / 100;
    if (side === 'BUY') {
      const free = +(S.balances[S.m.quote]?.free || 0) * r;
      if (S.type === 'MARKET') f.total.value = floorTo(free, 2);
      else {
        const p = parseFloat(f.price.value);
        if (p > 0) f.qty.value = floorTo(free / p, qd);
      }
    } else {
      f.qty.value = floorTo(+(S.balances[S.m.base]?.free || 0) * r, qd);
    }
    syncTotal(f);
  }

  async function submitOrder(f) {
    if (!S.me) return openModal('login');
    const side = f.dataset.side;
    const body = { symbol: S.sym, side, type: S.type };
    if (S.type === 'MARKET') {
      if (side === 'BUY') body.quoteQty = f.total.value.trim();
      else body.qty = f.qty.value.trim();
    } else {
      body.price = f.price.value.trim();
      body.qty = f.qty.value.trim();
      if (S.type === 'LIMIT') body.tif = $('#tif').value;
    }
    const btn = f.querySelector('button[type=submit]');
    btn.disabled = true;
    try {
      const r = await api('POST', '/api/order', body);
      const o = r.order;
      const label = `${side === 'BUY' ? 'Купівля' : 'Продаж'} ${S.m.base}`;
      if (o.status === 'FILLED') toast(`${label}: виконано ${o.filled} за ${fmtN(o.avgPrice, decimals(S.m.tick))}`, 'ok');
      else if (o.status === 'EXPIRED') toast(`${label}: ${+o.filled ? `частково виконано ${o.filled}, решту скасовано` : 'не виконано (немає зустрічних ордерів)'}`, +o.filled ? 'ok' : 'err');
      else toast(`${label}: ордер #${o.id} розміщено${+o.filled ? `, виконано ${o.filled}` : ''}`, 'ok');
      if (f.qty) f.qty.value = '';
      if (f.total) f.total.value = '';
      refreshPrivate();
    } catch (e) {
      toast(e.message, 'err');
      if (e.status === 401) openModal('login');
    } finally {
      btn.disabled = false;
    }
  }

  // ---------------- account tables ----------------
  function renderAcc() {
    const body = $('#acc-body');
    $('#open-count').textContent = S.open.length ? `(${S.open.length})` : '';
    $('#cancel-all').classList.toggle('hidden', S.tab !== 'open' || !S.open.length);
    if (!S.me) {
      body.innerHTML = `<div class="empty">Увійдіть або зареєструйтесь, щоб торгувати — нові акаунти отримують демо-баланс.</div>`;
      return;
    }
    const mk = (sym) => S.markets.find((m) => m.symbol === sym);
    const pair = (sym) => { const m = mk(sym); return m ? `${m.base}/${m.quote}` : sym; };
    const pdOf = (sym) => decimals(mk(sym)?.tick || '0.01');
    const qdOf = (sym) => decimals(mk(sym)?.step || '0.0001');
    const sideCell = (s) => `<td class="${s === 'BUY' ? 'green' : 'red'}">${s === 'BUY' ? 'Купівля' : 'Продаж'}</td>`;

    if (S.tab === 'open' || S.tab === 'history') {
      const list = S.tab === 'open' ? S.open : S.history;
      if (!list.length) { body.innerHTML = `<div class="empty">Немає ордерів</div>`; return; }
      body.innerHTML = `<table><thead><tr><th>Час</th><th>Пара</th><th>Тип</th><th>Сторона</th><th class="r">Ціна</th><th class="r">Сер. ціна</th>
        <th class="r">Кількість</th><th class="r">Виконано</th><th class="r">Сума</th><th>Статус</th><th></th></tr></thead><tbody>
        ${list.map((o) => `<tr><td class="muted">${dt(o.created)}</td><td>${pair(o.symbol)}</td><td>${TYPE[o.type] || o.type}${o.tif && o.tif !== 'GTC' ? ' ' + o.tif : ''}</td>
          ${sideCell(o.side)}<td class="r">${o.price ? fmtN(o.price, pdOf(o.symbol)) : 'Ринкова'}</td><td class="r">${o.avgPrice ? fmtN(o.avgPrice, pdOf(o.symbol)) : '—'}</td>
          <td class="r">${o.qty ? fmtN(o.qty, qdOf(o.symbol)) : (o.quoteQty ? fmtN(o.quoteQty, 2) + ' ' + (mk(o.symbol)?.quote || '') : '—')}</td>
          <td class="r">${fmtN(o.filled, qdOf(o.symbol))}</td><td class="r">${fmtN(o.quoteFilled, 2)}</td><td>${STATUS[o.status] || o.status}</td>
          <td>${S.tab === 'open' ? `<button class="link-btn" data-cancel="${o.id}">Скасувати</button>` : ''}</td></tr>`).join('')}
        </tbody></table>`;
    } else if (S.tab === 'mytrades') {
      if (!S.myTrades.length) { body.innerHTML = `<div class="empty">Ще немає угод</div>`; return; }
      body.innerHTML = `<table><thead><tr><th>Час</th><th>Пара</th><th>Сторона</th><th class="r">Ціна</th><th class="r">Кількість</th>
        <th class="r">Сума</th><th class="r">Комісія</th><th>Роль</th></tr></thead><tbody>
        ${S.myTrades.map((t) => `<tr><td class="muted">${dt(t.ts)}</td><td>${pair(t.symbol)}</td>${sideCell(t.side)}
          <td class="r">${fmtN(t.price, pdOf(t.symbol))}</td><td class="r">${fmtN(t.qty, qdOf(t.symbol))}</td><td class="r">${fmtN(t.quoteQty, 2)}</td>
          <td class="r">${t.fee} ${t.feeAsset}</td><td class="muted">${t.maker ? 'Maker' : 'Taker'}</td></tr>`).join('')}
        </tbody></table>`;
    } else {
      const p = S.pnl;
      if (!p) { body.innerHTML = ''; return; }
      const cls = (v) => (+v >= 0 ? 'green' : 'red');
      const sign = (v) => (+v > 0 ? '+' : '');
      const totalPnl = +p.realized + +p.unrealized;
      body.innerHTML = `<div class="summary">
          <div><small>Капітал (оцінка в USDT)</small><b class="num">${fmtN(p.equity, 2)}</b></div>
          <div><small>Загальний PnL</small><b class="num ${cls(totalPnl)}">${sign(totalPnl)}${fmtN(totalPnl, 2)}</b></div>
          <div><small>Реалізований PnL</small><b class="num ${cls(p.realized)}">${sign(p.realized)}${fmtN(p.realized, 2)}</b></div>
          <div><small>Нереалізований PnL</small><b class="num ${cls(p.unrealized)}">${sign(p.unrealized)}${fmtN(p.unrealized, 2)}</b></div>
          <div class="spacer"></div><button class="btn" id="faucet">+ Поповнити демо-USDT</button>
        </div>
        <table><thead><tr><th>Актив</th><th class="r">Доступно</th><th class="r">В ордерах</th><th class="r">Позиція</th><th class="r">Сер. ціна входу</th>
          <th class="r">Поточна ціна</th><th class="r">Вартість</th><th class="r">Нереаліз. PnL</th><th class="r">Реаліз. PnL</th><th class="r">Комісії</th></tr></thead><tbody>
        ${Object.entries(S.balances).map(([a, b]) => {
          const ps = p.positions.find((x) => x.asset === a);
          const d = a === 'USDT' ? 2 : 6;
          return `<tr><td><b>${a}</b></td><td class="r">${fmtN(b.free, d)}</td><td class="r">${fmtN(b.locked, d)}</td>
            ${ps ? `<td class="r">${fmtN(ps.qty, d)}</td><td class="r">${fmtN(ps.avgPrice, 2)}</td><td class="r">${fmtN(ps.lastPrice, 2)}</td>
              <td class="r">${fmtN(ps.value, 2)}</td><td class="r ${cls(ps.unrealized)}">${sign(ps.unrealized)}${fmtN(ps.unrealized, 2)} (${sign(ps.unrealizedPct)}${ps.unrealizedPct.toFixed(2)}%)</td>
              <td class="r ${cls(ps.realized)}">${sign(ps.realized)}${fmtN(ps.realized, 2)}</td><td class="r muted">${fmtN(ps.fees, 2)}</td>`
              : `<td class="r">—</td><td class="r">—</td><td class="r">—</td><td class="r">${fmtN(+b.free + +b.locked, 2)}</td><td class="r">—</td><td class="r">—</td><td class="r">—</td>`}</tr>`;
        }).join('')}</tbody></table>`;
      $('#faucet').onclick = async () => {
        try {
          S.balances = await api('POST', '/api/faucet');
          toast('Зараховано демо-USDT', 'ok');
          refreshPrivate();
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
      S.balances = me.balances;
      S.pnl = me.pnl;
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
    S.balances = d.balances;
    S.pnl = d.pnl;
    renderAvail();
    renderAccountBar();
    if (S.tab === 'assets') queueAcc();
  }
  function onOrder(o) {
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
          onAccount(d.account);
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
    for (const f of ['#form-buy', '#form-sell']) if ($(f).price) $(f).price.value = '';
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
    const b = e.target.closest('[data-sym]');
    if (b && b.dataset.sym !== S.sym) selectMarket(b.dataset.sym);
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
      for (const f of ['#form-buy', '#form-sell']) {
        $(f).price.value = r.dataset.price;
        syncTotal($(f));
      }
    });
  }
  for (const f of [$('#form-buy'), $('#form-sell')]) {
    f.addEventListener('input', onFormInput);
    f.addEventListener('submit', (e) => { e.preventDefault(); submitOrder(f); });
    f.addEventListener('click', (e) => {
      const b = e.target.closest('[data-pct]');
      if (b) onPct(f, +b.dataset.pct);
    });
  }
  $('#auth-tabs').addEventListener('click', (e) => {
    const b = e.target.closest('[data-mode]');
    if (b) openModal(b.dataset.mode);
  });
  $('#auth-form').addEventListener('submit', submitAuth);
  $('#modal-close').onclick = () => $('#modal').classList.add('hidden');
  $('#modal').addEventListener('click', (e) => { if (e.target.id === 'modal') $('#modal').classList.add('hidden'); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') $('#modal').classList.add('hidden'); });

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

  // ---------------- boot ----------------
  (async () => {
    [S.markets, S.config] = await Promise.all([api('GET', '/api/markets'), api('GET', '/api/config')]);
    for (const t of await api('GET', '/api/ticker')) S.tickers[t.symbol] = t;
    if (!S.markets.some((m) => m.symbol === S.sym)) S.sym = S.markets[0].symbol;
    await loadMe();
    await selectMarket(S.sym);
  })().catch((e) => toast('Помилка завантаження: ' + e.message, 'err'));
})();
