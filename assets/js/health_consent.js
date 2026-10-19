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
        // message in the language of the page
        var L = (document.documentElement.lang || 'en').slice(0, 2); var M = { en: 'Please confirm both consents to send a health enquiry.', de: 'Bitte bestätigen Sie beide Einwilligungen, um eine Gesundheitsanfrage zu senden.', tr: 'Sağlıkla ilgili bir talep göndermek için lütfen her iki onayı da verin.', uk: 'Щоб надіслати запит щодо здоров’я, підтвердьте, будь ласка, обидві згоди.', ru: 'Чтобы отправить запрос по вопросам здоровья, пожалуйста, подтвердите оба согласия.', ar: 'لإرسال استفسار يتعلق بالصحة، يُرجى تأكيد الموافقتين.' }; msg.textContent = M[L] || M.en;
        box.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, true);
    form.addEventListener('wpcf7mailsent', function () { setTimeout(sync, 0); });
    sync();
  }
  function init() { document.querySelectorAll('form.wpcf7-form').forEach(setup); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
