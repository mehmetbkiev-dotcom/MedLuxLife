/* MedLuxLife home, 2nd screen (desktop): the two journey columns side by side. Each pair (the two intro sentences, then card 1/1, 2/2, 3/3)
   gets the height of the taller one, so the dark step cards of both columns always start at the same height, whatever the browser,
   the screen size or (later) the language. Keep this file free of less-than and ampersand characters: WordPress escapes them in inline scripts. */
(function () {
  if (!document.body.classList.contains('home')) return;
  var mq = window.matchMedia('(min-width: 1100px)');
  function pairs() {
    var g = document.querySelector('.mlx-journeys'), out = [];
    if (!g) return out;
    var secs = Array.prototype.filter.call(g.children, function (el) { return !el.classList.contains('mlx-lang2'); });
    if (secs.length - 2 !== 0) return out;
    out.push([secs[0].querySelector('.ext-section-intro p'), secs[1].querySelector('.ext-section-intro p')]);
    var ca = secs[0].querySelectorAll('.ext-grid > .ext-card'), cb = secs[1].querySelectorAll('.ext-grid > .ext-card');
    for (var i = 0; ca.length - i > 0; i++) { if (cb[i]) out.push([ca[i], cb[i]]); }
    return out.filter(function (p) { return p[0] ? !!p[1] : false; });
  }
  function align() {
    var ps = pairs();
    ps.forEach(function (p) { p[0].style.removeProperty('min-height'); p[1].style.removeProperty('min-height'); });
    if (!mq.matches) return;
    var hs = ps.map(function (p) { return Math.max(p[0].getBoundingClientRect().height, p[1].getBoundingClientRect().height); });
    ps.forEach(function (p, i) { p[0].style.setProperty('min-height', hs[i] + 'px', 'important'); p[1].style.setProperty('min-height', hs[i] + 'px', 'important'); });   /* important: the cards carry min-height: 0 !important in the theme CSS */
  }
  var t = null;
  function later() { clearTimeout(t); t = setTimeout(align, 120); }
  align();
  window.addEventListener('load', align);
  window.addEventListener('resize', later);
  if (document.fonts) { if (document.fonts.ready) document.fonts.ready.then(align); }
})();
