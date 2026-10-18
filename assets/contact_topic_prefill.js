(function () {
  var path = location.pathname.replace(/^\/(de|tr|ru|uk|en)\//, '/');
  var m = path.match(/^\/(health|travel)\/(.*)$/);
  if (!m) return;
  var subject = m[1] === 'travel' ? 'Travel' : 'Health';
  var rest = m[2].replace(/\/$/, '');
  var hubs = ['', 'clinical-treatments', 'hospital-specialist-treatments'];
  var h1 = document.querySelector('main .wp-block-post-title') || document.querySelector('main h1');
  var topic = h1 ? h1.textContent.replace(/\s+/g, ' ').trim() : '';
  var withTopic = topic ? hubs.indexOf(rest) === -1 : false;
  var links = document.querySelectorAll('a.wp-block-button__link[href*="/contact/"], .medlux-mobile-only a[href*="/contact/"]');
  for (var i = 0; links.length > i; i++) {
    var u = new URL(links[i].href, location.href);
    u.searchParams.set('your-subject', subject);
    if (withTopic) u.searchParams.set('your-message', 'I am interested in: ' + topic + '.');
    links[i].href = u.toString();
  }
})();
