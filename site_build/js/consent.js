/* Consent banner (2026-10-28). Google Consent Mode v2: analytics_storage, ad_storage, ad_user_data and ad_personalization start "denied" (set in the
   <head> of base.html, before gtag / GTM load) and are updated here from the visitor's choice, kept in localStorage for 6 months. Refusing is as easy as accepting.
   window.bmOpenConsent() reopens the choice (footer link). Other scripts listen to the "bm:consent" event (detail: {analytics, ads}). */
(function () {
  var KEY = 'bm_consent', TTL = 1000 * 60 * 60 * 24 * 180;
  var en = (document.documentElement.lang || 'fr').slice(0, 2) === 'en';
  var T = en ? {
    title: 'Your privacy choices',
    text: 'We use cookies to measure the audience of the site (Google Analytics) and, once ads are shown, to display advertising. You decide, and you can change your mind at any time from the "Manage cookies" link at the bottom of the page.',
    more: 'Privacy policy', accept: 'Accept all', refuse: 'Refuse all', custom: 'Customize', save: 'Save my choices', back: 'Back',
    an_t: 'Audience measurement', an_d: 'Google Analytics and Google Tag Manager: which pages are read, from where, on which device.',
    ad_t: 'Advertising', ad_d: 'Google AdSense: ads shown on the site, and the cookies they use to limit repeats and measure results.',
  } : {
    title: 'Tes choix de confidentialité',
    text: "Nous utilisons des cookies pour mesurer l'audience du site (Google Analytics) et, quand des publicités seront affichées, pour diffuser de la publicité. Tu décides, et tu peux changer d'avis à tout moment avec le lien « Gérer les cookies » en bas de page.",
    more: 'Politique de confidentialité', accept: 'Tout accepter', refuse: 'Tout refuser', custom: 'Personnaliser', save: 'Enregistrer mes choix', back: 'Retour',
    an_t: "Mesure d'audience", an_d: 'Google Analytics et Google Tag Manager : quelles pages sont lues, depuis où, sur quel appareil.',
    ad_t: 'Publicité', ad_d: 'Google AdSense : les publicités affichées sur le site, et les cookies qu\'elles utilisent pour limiter les répétitions et mesurer les résultats.',
  };
  var root = window.BM_ROOT || '/';

  function read() {
    try {
      var c = JSON.parse(localStorage.getItem(KEY));
      if (c && c.v === 1 && c.s && Date.now() - c.t < TTL) return c.s;
    } catch (e) {}
    return null;
  }
  function signals(s) {
    var a = s.analytics ? 'granted' : 'denied', d = s.ads ? 'granted' : 'denied';
    return { analytics_storage: a, ad_storage: d, ad_user_data: d, ad_personalization: d };
  }
  function apply(s) {
    window.bmConsent = { analytics: !!s.analytics, ads: !!s.ads };
    if (typeof window.gtag === 'function') window.gtag('consent', 'update', signals(s));
    try { document.dispatchEvent(new CustomEvent('bm:consent', { detail: window.bmConsent })); } catch (e) {}
  }
  function save(s) {
    try { localStorage.setItem(KEY, JSON.stringify({ v: 1, t: Date.now(), s: { analytics: !!s.analytics, ads: !!s.ads } })); } catch (e) {}
    apply(s);
  }

  var box = null;
  function css() {
    if (document.getElementById('bm-consent-css')) return;
    var st = document.createElement('style');
    st.id = 'bm-consent-css';
    st.textContent =
      '.bm-consent{position:fixed;left:16px;right:16px;bottom:16px;z-index:2147483000;max-width:760px;margin:0 auto;background:var(--bg-2,#0d1245);color:var(--cream,#e9eeff);' +
      'border:1px solid var(--border-bright,#34419f);border-radius:14px;box-shadow:0 12px 40px rgba(2,4,30,.7);padding:18px 20px;font:400 14px/1.5 "Afacad Flux",system-ui,sans-serif}' +
      '.bm-consent h2{margin:0 0 6px;font:600 16px/1.3 "Cal Sans","Afacad Flux",system-ui,sans-serif}' +
      '.bm-consent p{margin:0 0 12px;color:var(--text-dim,#a6b2e6)}' +
      '.bm-consent a{color:var(--cyan,#cfe0ff);text-decoration:underline}' +
      '.bm-consent-btns{display:flex;gap:10px;flex-wrap:wrap}' +
      '.bm-consent-btns button{flex:1 1 140px;min-height:42px;padding:9px 14px;border-radius:10px;border:1px solid var(--border-bright,#34419f);background:var(--row,#0d1245);' +
      'color:var(--cream,#e9eeff);font:600 14px "Afacad Flux",system-ui,sans-serif;cursor:pointer}' +
      '.bm-consent-btns button:hover,.bm-consent-btns button:focus-visible{background:var(--row-hover,#172073);outline:2px solid var(--magenta,#2a63ff);outline-offset:1px}' +
      '.bm-consent-opt{display:flex;gap:12px;align-items:flex-start;padding:10px 0;border-top:1px solid var(--border,#1e2772)}' +
      '.bm-consent-opt input{width:20px;height:20px;margin-top:2px;flex:none;accent-color:#2a63ff}' +
      '.bm-consent-opt b{display:block;color:var(--cream,#e9eeff)}' +
      '.bm-consent-opt span{color:var(--text-dim,#a6b2e6)}' +
      '@media (max-width:520px){.bm-consent{left:8px;right:8px;bottom:8px;padding:14px}}';
    document.head.appendChild(st);
  }
  function close() { if (box) { box.remove(); box = null; } }
  function mk(tag, props, html) { var e = document.createElement(tag); for (var k in props) e.setAttribute(k, props[k]); if (html) e.innerHTML = html; return e; }

  function main(cur) {
    close(); css();
    box = mk('div', { 'class': 'bm-consent', role: 'dialog', 'aria-labelledby': 'bm-consent-t', 'aria-modal': 'false' });
    box.innerHTML = '<h2 id="bm-consent-t">' + T.title + '</h2><p>' + T.text + ' <a href="' + root + 'confidentialite/">' + T.more + '</a>.</p>' +
      '<div class="bm-consent-btns"><button type="button" data-a="refuse">' + T.refuse + '</button><button type="button" data-a="custom">' + T.custom + '</button><button type="button" data-a="accept">' + T.accept + '</button></div>';
    box.addEventListener('click', function (ev) {
      var a = ev.target && ev.target.getAttribute && ev.target.getAttribute('data-a');
      if (a === 'accept') { save({ analytics: true, ads: true }); close(); }
      else if (a === 'refuse') { save({ analytics: false, ads: false }); close(); }
      else if (a === 'custom') custom(cur);
    });
    document.body.appendChild(box);
    var b = box.querySelector('button'); if (b) b.focus({ preventScroll: true });
  }
  function custom(cur) {
    cur = cur || { analytics: false, ads: false };
    close(); css();
    box = mk('div', { 'class': 'bm-consent', role: 'dialog', 'aria-labelledby': 'bm-consent-t', 'aria-modal': 'false' });
    box.innerHTML = '<h2 id="bm-consent-t">' + T.title + '</h2>' +
      '<label class="bm-consent-opt"><input type="checkbox" id="bm-c-an"' + (cur.analytics ? ' checked' : '') + '><div><b>' + T.an_t + '</b><span>' + T.an_d + '</span></div></label>' +
      '<label class="bm-consent-opt"><input type="checkbox" id="bm-c-ad"' + (cur.ads ? ' checked' : '') + '><div><b>' + T.ad_t + '</b><span>' + T.ad_d + '</span></div></label>' +
      '<div class="bm-consent-btns" style="margin-top:10px"><button type="button" data-a="back">' + T.back + '</button><button type="button" data-a="save">' + T.save + '</button></div>';
    box.addEventListener('click', function (ev) {
      var a = ev.target && ev.target.getAttribute && ev.target.getAttribute('data-a');
      if (a === 'save') { save({ analytics: box.querySelector('#bm-c-an').checked, ads: box.querySelector('#bm-c-ad').checked }); close(); }
      else if (a === 'back') main(cur);
    });
    document.body.appendChild(box);
    var i = box.querySelector('input'); if (i) i.focus({ preventScroll: true });
  }

  window.bmOpenConsent = function () { main(read() || { analytics: false, ads: false }); };
  document.addEventListener('click', function (ev) {
    var t = ev.target && ev.target.closest && ev.target.closest('[data-bm-consent]');
    if (t) { ev.preventDefault(); window.bmOpenConsent(); }
  });

  var saved = read();
  if (saved) apply(saved); else main(null);
})();
