(function () {
  if (!document.body.classList.contains('home')) return;
  var hero = document.querySelector('main .wp-block-cover');
  function upd() {
    var lim = hero ? hero.getBoundingClientRect().bottom + scrollY - innerHeight * 0.6 : 400;
    var over = !(scrollY >= Math.max(lim, 120));
    document.documentElement.classList.toggle('mlx-over-hero', over);
  }
  addEventListener('scroll', upd, { passive: true }); addEventListener('resize', upd); upd();
})();
