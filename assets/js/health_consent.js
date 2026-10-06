(function () {
  function setup(form) {
    var sel = form.querySelector('select[name="your-subject"]');
    var box = form.querySelector('.medlux-health-consent');
    if (!sel || !box) return;
    var checks = box.querySelectorAll('input[type="checkbox"]');
    var msg = document.createElement('p');
    msg.className = 'medlux-consent-error';
    msg.setAttribute('role', 'alert');
    box.appendChild(msg);
    function sync() {
      var health = sel.value === 'Health';
      box.classList.toggle('is-visible', health);
      if (!health) { checks.forEach(function (c) { c.checked = false; }); msg.textContent = ''; }
    }
    sel.addEventListener('change', sync);
    checks.forEach(function (c) { c.addEventListener('change', function () { msg.textContent = ''; }); });
    document.addEventListener('submit', function (e) {
      if (e.target !== form || sel.value !== 'Health') return;
      var ok = Array.prototype.every.call(checks, function (c) { return c.checked; });
      if (!ok) {
        e.preventDefault(); e.stopImmediatePropagation();
        msg.textContent = 'Bitte bestätigen Sie beide Einwilligungen, um eine Gesundheitsanfrage zu senden.';
        box.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, true);
    form.addEventListener('wpcf7mailsent', function () { setTimeout(sync, 0); });
    sync();
  }
  function init() { document.querySelectorAll('form.wpcf7-form').forEach(setup); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
