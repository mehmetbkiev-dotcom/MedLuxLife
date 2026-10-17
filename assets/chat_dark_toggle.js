(function () {
  var fab = document.querySelector('.mlx-a-fab'), box = document.getElementById('mlx-assistant');
  if (!fab) return;
  var root = document.documentElement, busy = 0;
  // first solid colour behind the point decides: dark navy (or a photo/gradient background) = glass, light = solid badge
  function isDark(el) {
    while (el) {
      var cs = getComputedStyle(el), m = cs.backgroundColor.match(/[\d.]+/g);
      if (m) {
        var a = m.length > 3 ? +m[3] : 1;
        if (a > 0.5) return 90 > 0.2126 * m[0] + 0.7152 * m[1] + 0.0722 * m[2];
      }
      var g = cs.backgroundImage;
      if (g !== 'none') {
        var c = g.match(/rgba?\([^)]*\)/);
        if (!c) return true;
        m = c[0].match(/[\d.]+/g);
        return 90 > 0.2126 * m[0] + 0.7152 * m[1] + 0.0722 * m[2];
      }
      el = el.parentElement;
    }
    return false;
  }
  function upd() {
    busy = 0;
    var r = fab.getBoundingClientRect(), on = false;
    if (r.width) {
      var list = document.elementsFromPoint(r.left + r.width / 2, r.top + r.height / 2);
      for (var i = 0; list.length > i; i++) {
        if (box ? !box.contains(list[i]) : list[i] !== fab) { on = isDark(list[i]); break; }
      }
    }
    root.classList.toggle('mlx-chat-on-dark', on);
  }
  function req() { if (!busy) { busy = 1; requestAnimationFrame(upd); } }
  addEventListener('scroll', req, { passive: true });
  addEventListener('resize', req);
  addEventListener('load', req);
  req();
})();
