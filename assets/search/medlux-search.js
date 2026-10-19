/* MedLuxLife live search suggestions: as you type in any site search box, matching sections appear as links. */
(function () {
  var data = null, loading = null;
  var lang = (document.documentElement.lang || 'en').slice(0, 2).toLowerCase();
  if (['de', 'tr', 'ru', 'uk', 'ar'].indexOf(lang) < 0) lang = 'en';
  var prefix = (location.pathname.match(/^\/(de|tr|ru|uk|ar)(?=\/)/) || [''])[0];
  var TXT = { en: ['All results for', 'No matching section'], de: ['Alle Ergebnisse für', 'Kein passender Bereich'], tr: ['Tüm sonuçlar:', 'Eşleşen bölüm yok'], ru: ['Все результаты для', 'Ничего не найдено'], uk: ['Усі результати для', 'Нічого не знайдено'], ar: ['جميع النتائج لـ', 'لا توجد نتائج مطابقة'] }[lang];
  function norm(s) { return (s || '').toLowerCase().replace(/ı/g, 'i').replace(/ß/g, 'ss').normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/ё/g, 'е').replace(/[\u064B-\u065F\u0670\u0640]/g, '').replace(/ة/g, 'ه').replace(/ى/g, 'ي').replace(/[^\p{L}\p{N}]+/gu, ' ').trim(); } // Arabic: without short vowels, hamza signs and tatweel
  function load() {
    if (data) return Promise.resolve(data);
    if (!loading) loading = Promise.resolve().then(function () {
      var raw = JSON.parse(document.getElementById('mlx-search-index').textContent), d = raw.E;
      d.forEach(function (e) {
        e.b = raw.B[e.b] || {};
        e.nt = Object.keys(e.t).map(function (l) { return norm(e.t[l]); });
        // card names in the page language (cl) when there are any; both languages are searched
        e.cv = (e.cl ? e.cl[lang] : null) || e.c;
        e.nc = e.c.map(function (c, i) { return norm(c + ' ' + e.cv[i]); }); e.nk = norm(e.k);
      });
      return (data = d);
    }).catch(function () { loading = null; return []; });
    return loading;
  }
  function wordScore(hay, q) { // 3 = starts, 2 = word starts, 1 = contains
    if (!hay) return 0;
    if (hay.indexOf(q) === 0) return 3;
    if ((' ' + hay).indexOf(' ' + q) >= 0) return 2;
    return hay.indexOf(q) >= 0 ? 1 : 0;
  }
  function search(q) {
    var nq = norm(q); if (nq.length < 2) return [];
    var words = nq.split(' ');
    var res = [];
    data.forEach(function (e) {
      var best = 0, via = '';
      e.nt.forEach(function (t, i) { var s = wordScore(t, nq); if (s) best = Math.max(best, 100 + s * 10 - (i ? 1 : 0)); });
      // (no '<' before '>' on one line: WordPress would treat it as a tag and escape the code)
      if (!(best >= 120)) e.nc.forEach(function (c, i) {
        var v = wordScore(c, nq) ? 60 + wordScore(c, nq) * 10 : 0;
        if (v > best) { best = v; via = e.cv[i]; }
      });
      if (!best) {
        var all = e.nt.join(' ') + ' ' + e.nk + ' ' + e.nc.join(' ');
        if (words.every(function (w) { return wordScore(all, w) >= 2; })) best = 40;
        else if (words.every(function (w) { return all.indexOf(w) >= 0; })) best = 20;
      }
      if (best) res.push({ e: e, s: best - e.u.split('/').length * 0.1, via: via });
    });
    res.sort(function (a, b) { return b.s - a.s; });
    return res.slice(0, 7);
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function attach(form) {
    var input = form.querySelector('input[type="search"], input[name="s"]');
    if (!input || input.dataset.mlxSugg) return;
    input.dataset.mlxSugg = '1'; input.setAttribute('autocomplete', 'off');
    var box = document.createElement('div');
    box.className = 'mlx-sugg'; box.setAttribute('role', 'listbox'); box.hidden = true;
    box.setAttribute('data-no-translation', ''); box.setAttribute('data-no-dynamic-translation', ''); // titles are already in the page language
    var host = input.closest('.wp-block-search__inside-wrapper') || form;
    if (getComputedStyle(host).position === 'static') host.style.position = 'relative';
    host.appendChild(box);
    var active = -1, timer;
    function close() { box.hidden = true; active = -1; }
    function render(q) {
      var r = search(q), h = '';
      r.forEach(function (x, i) {
        h += '<a role="option" class="mlx-sugg-item" href="' + esc(location.origin + prefix + x.e.u) + '">' +
          '<span class="mlx-sugg-t">' + esc(x.e.t[lang] || x.e.t.en) + '</span>' +
          (x.via ? '<span class="mlx-sugg-v">' + esc(x.via) + '</span>' : '') +
          (x.e.b[lang] ? '<span class="mlx-sugg-b">' + esc(x.e.b[lang]) + '</span>' : '') + '</a>';
      });
      if (!r.length) h += '<div class="mlx-sugg-empty">' + esc(TXT[1]) + '</div>';
      h += '<button type="submit" class="mlx-sugg-all">' + esc(TXT[0]) + (lang === 'ar' ? ' «' + esc(q) + '» ←' : ' “' + esc(q) + '” →') + '</button>';
      box.innerHTML = h; box.hidden = false; active = -1;
      if (form.closest('header') && innerWidth > 600) { // align under the (expanding) header input
        var rc = input.getBoundingClientRect(), w = Math.min(420, innerWidth - 24);
        box.style.cssText = 'position:fixed;top:' + (rc.bottom + 8) + 'px;left:' + Math.max(12, rc.right - w) + 'px;right:auto;width:' + w + 'px';
      }
    }
    input.addEventListener('input', function () {
      clearTimeout(timer);
      var q = input.value.trim();
      if (norm(q).length < 2) return close();
      timer = setTimeout(function () { load().then(function () { if (input.value.trim() === q) render(q); }); }, 120);
    });
    input.addEventListener('focus', function () { load(); if (norm(input.value).length >= 2 && data) render(input.value.trim()); });
    input.addEventListener('keydown', function (ev) {
      var items = box.querySelectorAll('.mlx-sugg-item');
      if (box.hidden || !items.length) return;
      if (ev.key === 'ArrowDown' || ev.key === 'ArrowUp') {
        ev.preventDefault();
        active = (active + (ev.key === 'ArrowDown' ? 1 : -1) + items.length) % items.length;
        items.forEach(function (a, i) { a.classList.toggle('is-active', i === active); });
      } else if (ev.key === 'Enter' && active >= 0) { ev.preventDefault(); location.href = items[active].href; }
      else if (ev.key === 'Escape') close();
    });
    document.addEventListener('click', function (ev) { if (!form.contains(ev.target)) close(); });
  }
  function init() { document.querySelectorAll('form.wp-block-search, form[role="search"]').forEach(attach); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
