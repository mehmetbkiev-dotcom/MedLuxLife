/* MedLuxLife home: soft section snapping in BOTH directions (desktop only).
   After you stop scrolling, if a section start is close in the direction you were scrolling, the page glides to it.
   Keep this file free of less-than and ampersand characters: WordPress escapes them in inline scripts. */
(function () {
  if (!document.body.classList.contains('home')) return;
  var mq = window.matchMedia('(pointer: fine) and (min-width: 1100px)');
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  var lastY = scrollY, dir = 0, timer = null, gliding = false;
  function points() {
    var c = document.querySelector('main .wp-block-post-content') || document.querySelector('main');
    var h = document.querySelector('header'), hh = h ? h.getBoundingClientRect().height : 0;
    var max = document.documentElement.scrollHeight - innerHeight, list = [0];
    Array.prototype.forEach.call(c.children, function (el, i) {
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
    var y = scrollY, range = innerHeight * 0.4, near = 40, best = null, bestD = 0;
    points().forEach(function (p) {
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
    if (y - lastY !== 0) { if (!gliding) dir = y - lastY > 0 ? 1 : -1; }
    lastY = y;
    clearTimeout(timer);
    timer = setTimeout(settle, 140);
  }, { passive: true });
})();
