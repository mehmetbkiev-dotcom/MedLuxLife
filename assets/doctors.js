/* MedLuxLife partner doctors (tools/build_partners.py puts this inside each doctors block): hospital / department filters,
   name search, "show more", profile dialog, consultation link with the doctor's name in the language of the page */
(function () {
  var roots = document.querySelectorAll('.mlx-doctors:not([data-ready])');
  if (!roots.length) return;
  var lang = (document.documentElement.lang || 'en').slice(0, 2).toLowerCase();
  var m = location.pathname.match(/^\/(de|tr|ru|uk|ar)\//);
  var prefix = m ? '/' + m[1] : '';
  var PAGE = 24;
  var hello = {
    en: ['Hello,', 'I would like a free consultation about a treatment with %s.'],
    de: ['Guten Tag,', 'ich interessiere mich für eine kostenlose Beratung zu einer Behandlung bei %s.'],
    tr: ['Merhaba,', '%s ile tedavi hakkında ücretsiz danışmanlık almak istiyorum.'],
    uk: ['Добрий день,', 'мене цікавить безкоштовна консультація щодо лікування у %s.'],
    ru: ['Здравствуйте,', 'меня интересует бесплатная консультация по лечению у %s.'],
    ar: ['مرحبًا،', 'أرغب في استشارة مجانية بخصوص العلاج لدى %s.']
  };
  // the word after the counter, with the plural form the number needs in each language
  var FORMS = {
    en: { one: 'doctor', other: 'doctors' }, de: { one: 'Arzt', other: 'Ärzte' }, tr: { other: 'doktor' },
    uk: { one: 'лікар', few: 'лікарі', many: 'лікарів', other: 'лікаря' }, ru: { one: 'врач', few: 'врача', many: 'врачей', other: 'врача' },
    ar: { zero: 'طبيب', one: 'طبيب', two: 'طبيبان', few: 'أطباء', many: 'طبيبًا', other: 'طبيب' }
  };
  function word(n) {
    var f = FORMS[lang] || FORMS.en, k = 'other';
    try { k = new Intl.PluralRules(lang).select(n); } catch (e) {}
    return f[k] || f.other;
  }
  function norm(s) {
    return (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/ı/g, 'i').replace(/[^a-z0-9]+/g, ' ').trim();
  }
  function text(el) { return el ? el.textContent.replace(/\s+/g, ' ').trim() : ''; }
  function local(href) {
    try { var u = new URL(href, location.href); return u.origin === location.origin || /medluxlife\.de$/.test(u.hostname) ? prefix + u.pathname : href; } catch (e) { return href; }
  }
  function askUrl(card) {
    var name = text(card.querySelector('.mlx-doc-name'));
    var dept = text(card.querySelector('.mlx-doc-depts span'));
    var hosp = text(card.querySelector('.mlx-doc-hosp span'));
    var who = name + ' (' + [dept, hosp].filter(Boolean).join(', ') + ')';
    var t = hello[lang] || hello.en;
    var u = new URL(prefix + '/contact/', location.href);
    u.searchParams.set('your-subject', 'Health');
    u.searchParams.set('msg', t[0] + '\n' + t[1].replace('%s', who) + '\n\n');
    u.hash = 'contact';
    return u.toString();
  }
  roots.forEach(function (root) {
    root.setAttribute('data-ready', '1');
    var cards = [].slice.call(root.querySelectorAll('.mlx-doc'));
    var sel = {};
    root.querySelectorAll('[data-f]').forEach(function (el) { sel[el.getAttribute('data-f')] = el; });
    var count = root.querySelector('.mlx-doc-n'), empty = root.querySelector('.mlx-doc-empty');
    var moreBtn = root.querySelector('.mlx-doc-showmore'), reset = root.querySelector('.mlx-doc-reset');
    var dlg = root.querySelector('.mlx-doc-dialog'), box = root.querySelector('.mlx-doc-dlg');
    var shown = PAGE, matches = cards;
    // departments in alphabetical order of the (translated) names
    if (sel.dept) {
      var opts = [].slice.call(sel.dept.options, 1);
      opts.sort(function (a, b) { return a.text.localeCompare(b.text, lang); });
      opts.forEach(function (o) { sel.dept.appendChild(o); });
    }
    var q = new URLSearchParams(location.search);
    ['hospital', 'dept', 'q'].forEach(function (k) { if (sel[k] && q.get(k)) sel[k].value = q.get(k); });
    cards.forEach(function (c) {
      c.querySelectorAll('.mlx-doc-ask').forEach(function (a) { a.href = askUrl(c); });
    });
    function apply(keep) {
      var h = sel.hospital ? sel.hospital.value : '', d = sel.dept ? sel.dept.value : '', n = norm(sel.q ? sel.q.value : '');
      if (!keep) shown = PAGE;
      matches = cards.filter(function (c) {
        return (!h || (' ' + c.dataset.hospital + ' ').indexOf(' ' + h + ' ') > -1) &&
          (!d || (' ' + c.dataset.dept + ' ').indexOf(' ' + d + ' ') > -1) &&
          (!n || c.dataset.name.indexOf(n) > -1);
      });
      cards.forEach(function (c) { c.hidden = true; });
      matches.slice(0, shown).forEach(function (c) { c.hidden = false; });
      count.textContent = matches.length;
      if (count.nextElementSibling) count.nextElementSibling.textContent = word(matches.length);
      empty.hidden = matches.length > 0;
      moreBtn.parentNode.hidden = !(matches.length > shown);
      if (reset) reset.hidden = !(h || d || n);
    }
    Object.keys(sel).forEach(function (k) { sel[k].addEventListener(k === 'q' ? 'input' : 'change', function () { apply(false); }); });
    moreBtn.addEventListener('click', function () { shown += PAGE; apply(true); });
    if (reset) reset.addEventListener('click', function () { Object.keys(sel).forEach(function (k) { sel[k].value = ''; }); apply(false); });
    function open(card) {
      box.innerHTML = '';
      var head = document.createElement('div');
      head.className = 'mlx-doc-dlg-head';
      var img = card.querySelector('img').cloneNode(true);
      img.removeAttribute('loading');
      head.appendChild(img);
      var info = document.createElement('div');
      info.appendChild(card.querySelector('.mlx-doc-name').cloneNode(true));
      var dep = card.querySelector('.mlx-doc-depts').cloneNode(true);
      dep.querySelectorAll('span[data-href]').forEach(function (s) {
        if (!s.dataset.href) return;
        var a = document.createElement('a');
        a.href = local(s.dataset.href); a.textContent = s.textContent; s.textContent = ''; s.appendChild(a);
      });
      info.appendChild(dep);
      info.appendChild(card.querySelector('.mlx-doc-hosp').cloneNode(true));
      var role = card.querySelector('.mlx-doc-role');
      if (role) info.appendChild(role.cloneNode(true));
      head.appendChild(info);
      box.appendChild(head);
      var more = card.querySelector('.mlx-doc-more').cloneNode(true);
      more.hidden = false;
      box.appendChild(more);
      dlg.querySelector('.mlx-doc-ask').href = askUrl(card);
      if (dlg.showModal) dlg.showModal(); else dlg.setAttribute('open', '');
    }
    root.addEventListener('click', function (e) {
      var b = e.target.closest('.mlx-doc-photo, .mlx-doc-more-btn');
      if (b && root.contains(b)) open(b.closest('.mlx-doc'));
    });
    dlg.querySelector('.mlx-doc-close').addEventListener('click', function () { dlg.close(); });
    dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });
    apply(false);
  });
})();
