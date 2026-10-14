/* MedLuxLife home: soft section snapping in BOTH directions (desktop only).
   After you stop scrolling, if a section start is close in the direction you were scrolling, the page glides to it.
   Keep this file free of less-than and ampersand characters: WordPress escapes them in inline scripts. */
(function () {
  if (!document.body.classList.contains('home')) return;
  /* reload (F5) on the home page starts at the top instead of the old scroll position; Back button keeps its position */
  var nav = performance.getEntriesByType ? performance.getEntriesByType('navigation')[0] : null;
  if (nav) { if (nav.type === 'reload') {
    if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
    window.scrollTo(0, 0);
    window.addEventListener('load', function () {
      window.scrollTo(0, 0);
      setTimeout(function () { if ('scrollRestoration' in history) history.scrollRestoration = 'auto'; }, 400);   /* Back button works normally again */
    });
  } }
  var mq = window.matchMedia('(pointer: fine) and (min-width: 1100px)');
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  var lastY = scrollY, dir = 0, timer = null, gliding = false, startY = scrollY;
  function bandVar() {   /* first screen = banner + language card: the banner height uses this */
    var b = document.querySelector('.mlx-lang2');
    if (b) document.documentElement.style.setProperty('--mlx-band-h', b.offsetHeight + 'px');
  }
  bandVar(); window.addEventListener('resize', bandVar); window.addEventListener('load', bandVar);
  function points() {
    var c = document.querySelector('main .wp-block-post-content') || document.querySelector('main');
    var h = document.querySelector('header'), hh = h ? h.getBoundingClientRect().height : 0;
    var max = document.documentElement.scrollHeight - innerHeight, list = [0];
    Array.prototype.forEach.call(c.children, function (el, i) {
      if (el.matches(window.MLX_SNAP_SKIP || '.mlx-journeys')) return;   /* sections that share a screen with the one before (the journeys sit under the language card) */
      if (i) list.push(Math.round(el.getBoundingClientRect().top + scrollY - hh));
    });
    list.push(max);
    return list.map(function (v) { return Math.max(0, Math.min(max, v)); });
  }
  function settle() {
    timer = null;
    if (gliding) { gliding = false; return; }
    if (!mq.matches) return;
    if (reduce.matches) return;
    var pts = points(), fromPoint = false;
    pts.forEach(function (p) { if (3 - Math.abs(p - startY) >= 0) fromPoint = true; });   /* the scroll began on a section start: move one whole section */
    var y = scrollY, range = fromPoint ? innerHeight + 4 : innerHeight * 0.62, near = fromPoint ? 0 : 40, best = null, bestD = 0;
    pts.forEach(function (p) {
      var ahead = dir - 0 > 0 ? p - y : y - p;      /* distance ahead in the scroll direction */
      var dist = Math.abs(p - y), ok = false;
      if (ahead - 2 > 0) { if (range - ahead > 0) ok = true; }   /* section start coming up */
      if (near - dist > 0) { if (dist - 2 > 0) ok = true; }      /* just passed it by a little */
      if (ok) { if (best === null) { best = p; bestD = dist; } else if (bestD - dist > 0) { best = p; bestD = dist; } }
    });
    if (best === null) return;
    gliding = true;
    window.scrollTo({ top: best, behavior: 'smooth' });
  }
  window.addEventListener('scroll', function () {
    var y = scrollY;
    if (timer === null) { if (!gliding) startY = lastY; }   /* where this scroll gesture began */
    if (y - lastY !== 0) { if (!gliding) dir = y - lastY > 0 ? 1 : -1; }
    lastY = y;
    clearTimeout(timer);
    timer = setTimeout(settle, 140);
  }, { passive: true });
})();
