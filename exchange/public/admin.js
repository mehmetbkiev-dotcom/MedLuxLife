'use strict';
(() => {
  const $ = (s) => document.querySelector(s);
  const esc = (s) => String(s ?? '—').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
  let token = '';
  try { token = sessionStorage.getItem('adminToken') || ''; } catch {}

  async function get(path) {
    const r = await fetch(path, { headers: token ? { 'X-Admin-Token': token } : {} });
    if (r.status === 403) throw Object.assign(new Error('forbidden'), { forbidden: true });
    return r.json();
  }

  function render(b, a) {
    const st = !b.broker ? '<span class="muted">не підключено</span>'
      : b.connected ? '<span class="green">підключено, угоди дублюються</span>'
      : b.mirroring ? '<span class="red">немає з\'єднання</span>' : '<span class="muted">лише ціни (ключі API не задані)</span>';
    const markets = b.markets ? Object.entries(b.markets).map(([s, m]) => `<tr><td><b>${esc(s)}</b></td>
      <td class="r">${esc(m.brokerBid)} / ${esc(m.brokerAsk)}</td><td class="r">${esc(m.ourLast)}</td>
      <td class="r">${esc(m.clientsNetPosition)}</td><td class="r">${esc(m.hedgedAtBroker)}</td><td class="r">${esc(m.pendingToHedge)}</td>
      <td>${m.reconciled ? '<span class="green">✓ зійшлося</span>' : '<span class="red">розбіжність</span>'}</td>
      <td class="muted">${m.priceAgeSec ?? '—'} с</td></tr>`).join('') : '';
    const orders = (b.recentOrders || []).map((o) => `<tr><td class="muted">${new Date(o.ts).toLocaleString('uk-UA')}</td><td>${esc(o.symbol)}</td>
      <td class="${o.side === 'BUY' ? 'green' : 'red'}">${o.side === 'BUY' ? 'Купівля' : 'Продаж'}</td><td class="r">${esc(o.qty)}</td>
      <td class="r">${esc(o.executedQty)}</td><td class="r">${esc(o.avgPrice)}</td><td>${esc(o.status)}</td><td class="muted">${esc(o.brokerOrderId)}</td>
      <td class="red">${o.error ? esc(o.error) : ''}</td></tr>`).join('');
    const bal = (b.brokerBalances || []).filter((x) => +x.free || +x.locked).slice(0, 30)
      .map((x) => `<tr><td>${esc(x.asset)}</td><td class="r">${esc(x.free)}</td><td class="r">${esc(x.locked)}</td></tr>`).join('');
    $('#content').innerHTML = `
      <section class="panel"><div class="panel-title">Брокер ліквідності</div>
        <div class="kv"><div><small>Статус</small>${st}</div><div><small>Брокер</small>${esc(b.broker)}</div>
          <div><small>Ордери на</small>${esc(b.tradeUrl)}</div><div><small>Ціни з</small>${esc(b.priceUrl)}</div>
          ${b.lastError ? `<div><small>Остання помилка</small><span class="red">${esc(b.lastError.where)}: ${esc(b.lastError.message)}</span>
            <span class="muted">${new Date(b.lastError.ts).toLocaleTimeString('uk-UA')}</span></div>` : ''}</div>
        ${markets ? `<table><thead><tr><th>Пара</th><th class="r">Брокер bid / ask</th><th class="r">Наша ціна</th>
          <th class="r">Чиста позиція клієнтів</th><th class="r">Захеджовано у брокера</th><th class="r">В черзі</th><th>Звірка</th><th>Ціна</th></tr></thead>
          <tbody>${markets}</tbody></table>` : `<div class="empty">${esc(b.message)}</div>`}
      </section>
      <section class="panel"><div class="panel-title">Ордери у брокера (останні 30)</div>
        ${orders ? `<div class="acc-body"><table><thead><tr><th>Час</th><th>Пара</th><th>Сторона</th><th class="r">Кількість</th><th class="r">Виконано</th>
          <th class="r">Сер. ціна</th><th>Статус</th><th>ID у брокера</th><th>Помилка</th></tr></thead><tbody>${orders}</tbody></table></div>`
          : '<div class="empty">Ще немає</div>'}
      </section>
      <section class="panel"><div class="panel-title">Баланс демо-рахунку у брокера</div>
        ${bal ? `<table><thead><tr><th>Актив</th><th class="r">Доступно</th><th class="r">В ордерах</th></tr></thead><tbody>${bal}</tbody></table>`
          : '<div class="empty">Немає даних</div>'}
      </section>
      <section class="panel"><div class="panel-title">Аудит біржі</div>
        <div class="kv"><div><small>Інваріанти</small>${a.ok ? '<span class="green">✓ баланси зійшлися</span>' : `<span class="red">${esc(a.issues.join('; '))}</span>`}</div>
          <div><small>Відкритих ордерів</small>${esc(a.openOrders)}</div><div><small>Онлайн-з'єднань</small>${esc(a.sseClients)}</div>
          <div><small>Пам'ять</small>${esc(a.memMB)} МБ</div>
          ${Object.entries(a.supply || {}).map(([k, v]) => `<div><small>Усього ${esc(k)}</small>${esc(v)}</div>`).join('')}</div>
      </section>`;
  }

  async function refresh() {
    try {
      const [b, a] = await Promise.all([get('/api/admin/broker'), get('/api/audit')]);
      $('#login').classList.add('hidden');
      render(b, a);
    } catch (e) {
      if (e.forbidden) {
        $('#login').classList.remove('hidden');
        $('#content').innerHTML = '';
        if (token) $('#login-err').textContent = 'Невірний токен';
      }
    }
  }

  $('#login-form').addEventListener('submit', (e) => {
    e.preventDefault();
    token = e.target.token.value.trim();
    try { sessionStorage.setItem('adminToken', token); } catch {}
    refresh();
  });
  refresh();
  setInterval(refresh, 3000);
})();
