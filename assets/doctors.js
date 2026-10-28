/* MedLuxLife partner doctors (tools/build_partners.py puts this inside each doctors list and each doctor page):
   list: hospital / department filters, name search, "show more", counter word with the right plural;
   doctor page: consultation link with the doctor's name in the language of the page, "← All doctors" goes back to the filtered list */
(function () {
  var lists = document.querySelectorAll('.mlx-doctors:not([data-ready])');
  var details = document.querySelectorAll('.mlx-doc-detail:not([data-ready])');
  if (!lists.length && !details.length) return;
  var lang = (document.documentElement.lang || 'en').slice(0, 2).toLowerCase();
  var m = location.pathname.match(/^\/(de|tr|ru|uk|ar)\//);
  var prefix = m ? '/' + m[1] : '';
  var PAGE = 30;  // a multiple of 5, 3 and 2 columns (partner_pages.css) → full rows
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

  details.forEach(function (root) {
    root.setAttribute('data-ready', '1');
    var name = [text(root.querySelector('.mlx-doc-title')), text(root.querySelector('.mlx-doc-name'))].filter(Boolean).join(' ');
    var place = [text(root.querySelector('.mlx-doc-depts span')), text(root.querySelector('.mlx-doc-hosp span'))].filter(Boolean).join(', ');
    var t = hello[lang] || hello.en;
    var u = new URL(prefix + '/contact/', location.href);
    u.searchParams.set('your-subject', 'Health');
    u.searchParams.set('msg', t[0] + '\n' + t[1].replace('%s', name + (place ? ' (' + place + ')' : '')) + '\n\n');
    u.hash = 'contact';
    root.querySelectorAll('.mlx-doc-ask').forEach(function (a) { a.href = u.toString(); });
    // back to the list the visitor came from, with its filters and scroll position
    var back = root.querySelector('.mlx-doc-back');
    if (back && document.referrer) {
      try {
        var r = new URL(document.referrer), l = new URL(back.href, location.href);
        if (r.origin === location.origin && r.pathname.replace(/\/$/, '') === l.pathname.replace(/\/$/, '')) {
          back.addEventListener('click', function (e) { e.preventDefault(); history.back(); });
        }
      } catch (e) {}
    }
  });

  lists.forEach(function (root) {
    root.setAttribute('data-ready', '1');
    var cards = [].slice.call(root.querySelectorAll('.mlx-doc'));
    var sel = {};
    root.querySelectorAll('[data-f]').forEach(function (el) { sel[el.getAttribute('data-f')] = el; });
    var count = root.querySelector('.mlx-doc-n'), empty = root.querySelector('.mlx-doc-empty');
    var moreBtn = root.querySelector('.mlx-doc-showmore'), reset = root.querySelector('.mlx-doc-reset');
    var shown = PAGE, matches = cards;
    // departments in alphabetical order of the (translated) names
    if (sel.dept) {
      var opts = [].slice.call(sel.dept.options, 1);
      opts.sort(function (a, b) { return a.text.localeCompare(b.text, lang); });
      opts.forEach(function (o) { sel.dept.appendChild(o); });
    }
    var q = new URLSearchParams(location.search);
    ['hospital', 'dept', 'q'].forEach(function (k) { if (sel[k] && q.get(k)) sel[k].value = q.get(k); });
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
      if (count) {  // lists without filters (Celyxmed) have no counter
        count.textContent = matches.length;
        if (count.nextElementSibling) count.nextElementSibling.textContent = word(matches.length);
      }
      empty.hidden = matches.length > 0;
      moreBtn.parentNode.hidden = !(matches.length > shown);
      if (reset) reset.hidden = !(h || d || n);
    }
    Object.keys(sel).forEach(function (k) { sel[k].addEventListener(k === 'q' ? 'input' : 'change', function () { apply(false); }); });
    moreBtn.addEventListener('click', function () { shown += PAGE; apply(true); });
    if (reset) reset.addEventListener('click', function () { Object.keys(sel).forEach(function (k) { sel[k].value = ''; }); apply(false); });
    // coming back from a doctor's page: the browser restores the filters, show the same cards again
    window.addEventListener('pageshow', function () { apply(true); });
    apply(false);
  });
})();
