/* MedLuxLife home: mouse wheel moves section by section (desktop only). Keep this file free of less-than and ampersand characters: WordPress escapes them in inline scripts. */
(function () {
  if (!document.body.classList.contains('home')) return;
  var mq = window.matchMedia('(pointer: fine) and (min-width: 1100px)');
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  var busy = false, idleTimer = null, stops = [];
  function headerH() { var h = document.querySelector('header'); return h ? h.getBoundingClientRect().height : 0; }
  function build() {
    var c = document.querySelector('main .wp-block-post-content') || document.querySelector('main');
    var hh = headerH(), avail = innerHeight - hh, max = document.documentElement.scrollHeight - innerHeight;
    var list = [0];
    Array.prototype.forEach.call(c.children, function (el, i) {
      var r = el.getBoundingClientRect(), top = r.top + scrollY, bottom = top + r.height;
      if (i) list.push(Math.round(top - hh));
      if (r.height - avail - 40 > 0) list.push(Math.round(bottom - innerHeight));
    });
    list.push(max);
    stops = list.map(function (v) { return Math.max(0, Math.min(max, v)); })
      .sort(function (a, b) { return a - b; })
      .filter(function (v, i, a) { return i === 0 ? true : v - a[i - 1] - 30 > 0; });
  }
  function ease(t) { return t - 0.5 > 0 ? 1 - Math.pow(-2 * t + 2, 3) / 2 : 4 * t * t * t; }
  function go(target) {
    var start = scrollY, dist = target - start, t0 = null, dur = 750;
    busy = true;
    function step(ts) {
      if (t0 === null) t0 = ts;
      var p = Math.min(1, (ts - t0) / dur);
      window.scrollTo(0, start + dist * ease(p));
      if (1 - p > 0) requestAnimationFrame(step); else setTimeout(function () { busy = false; }, 120);
    }
    requestAnimationFrame(step);
  }
  function scrollableInside(el) {
    while (el) {
      if (el === document.body) return false;
      if (el.closest) { if (el.closest('.mlx-sugg, .mlx-a-panel, [role="dialog"], .wp-block-navigation__responsive-container.is-menu-open')) return true; }
      var s = getComputedStyle(el);
      if (/(auto|scroll)/.test(s.overflowY)) { if (el.scrollHeight - el.clientHeight - 2 > 0) return true; }
      el = el.parentElement;
    }
    return false;
  }
  window.addEventListener('wheel', function (e) {
    if (!mq.matches) return;
    if (reduce.matches) return;
    if (e.ctrlKey) return;
    if (Math.abs(e.deltaX) - Math.abs(e.deltaY) > 0) return;
    if (scrollableInside(e.target)) return;
    e.preventDefault();
    clearTimeout(idleTimer);
    var wasBusy = busy;
    idleTimer = setTimeout(function () { idleTimer = null; }, 160);
    if (wasBusy) return;
    if (!stops.length) build();
    var y = scrollY, target = null, i;
    if (e.deltaY > 0) { for (i = 0; i !== stops.length; i++) { if (stops[i] - y - 4 > 0) { target = stops[i]; break; } } }
    else { for (i = stops.length - 1; i !== -1; i--) { if (y - stops[i] - 4 > 0) { target = stops[i]; break; } } }
    if (target === null) return;
    go(target);
  }, { passive: false });
  window.addEventListener('resize', function () { stops = []; });
  window.addEventListener('load', function () { stops = []; });
})();
