(function () {
  var path = location.pathname.replace(/^\/(de|tr|ru|uk|ar|en)\//, '/');
  // contact page: put the prepared message (with line breaks) into the empty message field
  if (/^\/contact\/?$/.test(path)) {
    var msg = new URLSearchParams(location.search).get('msg');
    var ta = document.querySelector('textarea[name="your-message"]');
    // Contact Form 7 empties the form on load when the page comes from the page cache: the text is also the field's default, which is cleared again after a successful send
    if (msg) { if (ta) { if (!ta.value) { ta.defaultValue = msg; ta.value = msg; } } }
    document.addEventListener('wpcf7mailsent', function (e) { var t = e.target.querySelector('textarea[name="your-message"]'); if (t) t.defaultValue = ''; });
    return;
  }
  var m = path.match(/^\/(health|travel)\/(.*)$/);
  if (!m) return;
  var subject = m[1] === 'travel' ? 'Travel' : 'Health';
  var rest = m[2].replace(/\/$/, '');
  var hubs = ['', 'clinical-treatments', 'hospital-specialist-treatments'];
  var h1 = document.querySelector('main .wp-block-post-title') || document.querySelector('main h1');
  var topic = h1 ? h1.textContent.replace(/\s+/g, ' ').trim() : '';
  var withTopic = topic ? hubs.indexOf(rest) === -1 : false;
  // greeting + topic in the language of the page
  var lang = (document.documentElement.lang || 'en').slice(0, 2).toLowerCase();
  // the two main hubs: a natural phrase instead of the bare title (used for WhatsApp only)
  var hubName = {
    en: ['a treatment', 'travel planning'], de: ['eine Behandlung', 'die Organisation einer Reise'],
    tr: ['tedavi', 'seyahat organizasyonu'], uk: ['лікування', 'організація подорожі'], ru: ['лечение', 'организация поездки'],
    ar: ['علاج', 'تنظيم رحلة']
  };
  if (rest === '') topic = (hubName[lang] || hubName.en)[subject === 'Travel' ? 1 : 0];
  function phrase(name) {
    var texts = {
      en: ['Hello,', 'I am interested in ' + name + '.'],
      de: ['Guten Tag,', 'ich interessiere mich für ' + name + '.'],
      tr: ['Merhaba,', name + ' ile ilgileniyorum.'],
      uk: ['Добрий день,', 'мене цікавить ' + name + '.'],
      ru: ['Здравствуйте,', 'меня интересует ' + name + '.'],
      ar: ['مرحبًا،', 'أرغب في الاستفسار عن ' + name + '.']
    };
    return texts[lang] || texts.en;
  }
  var t = phrase(topic);
  var message = t[0] + '\n' + t[1] + '\n\n';
  var links = document.querySelectorAll('a.wp-block-button__link[href*="/contact/"], .medlux-mobile-only a[href*="/contact/"]');
  for (var i = 0; links.length > i; i++) {
    var u = new URL(links[i].href, location.href);
    u.searchParams.set('your-subject', subject);
    if (withTopic) u.searchParams.set('msg', message);
    links[i].href = u.toString();
  }
  // cards without their own page ("Free consultation →", tools/card_consult_links.py): the form opens with this card's treatment as the topic
  var asks = document.querySelectorAll('main .medlux-ask a[href*="/contact/"]');
  for (var k = 0; asks.length > k; k++) {
    var card = asks[k].closest('.medlux-card');
    var head = card ? card.querySelector('h3') : null;
    var p2 = phrase(head ? head.textContent.replace(/\s+/g, ' ').trim() : topic);
    var u2 = new URL(asks[k].href, location.href);
    u2.searchParams.set('your-subject', subject);
    u2.searchParams.set('msg', p2[0] + '\n' + p2[1] + '\n\n');
    u2.hash = 'contact';
    asks[k].href = u2.toString();
  }
  // WhatsApp buttons next to the consultation button: the same greeting + topic as a ready message
  var wa = document.querySelectorAll('main a[href*="wa.me/"]');
  var waText = topic ? t[0] + '\n' + t[1] : t[0];
  for (var j = 0; wa.length > j; j++) {
    wa[j].href = wa[j].href.split('?')[0] + '?text=' + encodeURIComponent(waText);
  }
})();
