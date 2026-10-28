/* Ad loader (2026-10-28). Does nothing unless the build rendered ad slots (build_site.py: BM_ADS=1 and a slot id per placement), and loads the AdSense script only after
   the visitor accepted advertising (consent.js, event "bm:consent"). Slots are <aside class="bm-ad" data-client data-slot> with a reserved height, so the page does not jump. */
(function () {
  var slots = document.querySelectorAll('.bm-ad[data-slot]');
  if (!slots.length) return;
  var loaded = false;
  function fill() {
    if (loaded) return;
    var client = slots[0].getAttribute('data-client');
    if (!client) return;
    loaded = true;
    var s = document.createElement('script');
    s.async = true; s.crossOrigin = 'anonymous';
    s.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=' + encodeURIComponent(client);
    s.onload = function () {
      slots.forEach(function (el) {
        el.style.display = 'block';          // hidden until the visitor accepted ads, so a refusal leaves no empty gap
        var ins = document.createElement('ins');
        ins.className = 'adsbygoogle'; ins.style.display = 'block';
        ins.setAttribute('data-ad-client', client);
        ins.setAttribute('data-ad-slot', el.getAttribute('data-slot'));
        ins.setAttribute('data-ad-format', 'auto');
        ins.setAttribute('data-full-width-responsive', 'true');
        el.appendChild(ins);
        try { (window.adsbygoogle = window.adsbygoogle || []).push({}); } catch (e) {}
      });
    };
    document.head.appendChild(s);
  }
  function check() { if (window.bmConsent && window.bmConsent.ads) fill(); }
  document.addEventListener('bm:consent', check);
  check();
})();
