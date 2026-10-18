(function () {
  var path = location.pathname.replace(/^\/(de|tr|ru|uk|en)\//, '/');
  // contact page: put the prepared message (with line breaks) into the empty message field
  if (/^\/contact\/?$/.test(path)) {
    var msg = new URLSearchParams(location.search).get('msg');
    var ta = document.querySelector('textarea[name="your-message"]');
    if (msg) { if (ta) { if (!ta.value) ta.value = msg; } }
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
    tr: ['tedavi', 'seyahat organizasyonu'], uk: ['лікування', 'організація подорожі'], ru: ['лечение', 'организация поездки']
  };
  if (rest === '') topic = (hubName[lang] || hubName.en)[subject === 'Travel' ? 1 : 0];
  var texts = {
    en: ['Hello,', 'I am interested in ' + topic + '.'],
    de: ['Guten Tag,', 'ich interessiere mich für ' + topic + '.'],
    tr: ['Merhaba,', topic + ' ile ilgileniyorum.'],
    uk: ['Добрий день,', 'мене цікавить ' + topic + '.'],
    ru: ['Здравствуйте,', 'меня интересует ' + topic + '.']
  };
  var t = texts[lang] || texts.en;
  var message = t[0] + '\n' + t[1] + '\n\n';
  var links = document.querySelectorAll('a.wp-block-button__link[href*="/contact/"], .medlux-mobile-only a[href*="/contact/"]');
  for (var i = 0; links.length > i; i++) {
    var u = new URL(links[i].href, location.href);
    u.searchParams.set('your-subject', subject);
    if (withTopic) u.searchParams.set('msg', message);
    links[i].href = u.toString();
  }
  // WhatsApp buttons next to the consultation button: the same greeting + topic as a ready message
  var wa = document.querySelectorAll('main a[href*="wa.me/"]');
  var waText = topic ? t[0] + '\n' + t[1] : t[0];
  for (var j = 0; wa.length > j; j++) {
    wa[j].href = wa[j].href.split('?')[0] + '?text=' + encodeURIComponent(waText);
  }
})();
