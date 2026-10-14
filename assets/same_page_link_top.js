/* MedLuxLife: clicking a link to the page you are already on (Home, logo, menu item) scrolls smoothly to the top
   instead of reloading at the same scroll position. Keep this file free of less-than and ampersand characters. */
(function () {
  function norm(p) { return (p || '/').replace(/index\.php$/, '').replace(/\/+$/, '') || '/'; }
  document.addEventListener('click', function (e) {
    if (e.defaultPrevented) return;
    if (e.button !== 0) return;
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var a = e.target.closest ? e.target.closest('a[href]') : null;
    if (!a) return;
    if (a.target) { if (a.target !== '_self') return; }
    var u;
    try { u = new URL(a.href, location.href); } catch (err) { return; }
    if (u.origin !== location.origin) return;
    if (u.hash) return;
    if (u.search !== location.search) return;
    if (norm(u.pathname) !== norm(location.pathname)) return;
    e.preventDefault();
    var menu = document.querySelector('.wp-block-navigation__responsive-container.is-menu-open .wp-block-navigation__responsive-container-close');
    if (menu) menu.click();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
})();
