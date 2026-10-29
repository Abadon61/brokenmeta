/* Consent banner (2026-10-28). Google Consent Mode v2: analytics_storage, ad_storage, ad_user_data and ad_personalization start "denied" (set in the
   <head> of base.html, before gtag / GTM load) and are updated here from the visitor's choice, kept in localStorage for 6 months. Refusing is as easy as accepting.
   window.bmOpenConsent() reopens the choice (footer link). Other scripts listen to the "bm:consent" event (detail: {analytics, ads}). */
(function () {
  var KEY = 'bm_consent', TTL = 1000 * 60 * 60 * 24 * 180;
  var en = (document.documentElement.lang || 'fr').slice(0, 2) === 'en';
  var T = en ? {
    title: 'Cookies: your call',
    text: 'BrokenMeta.gg is free. Measurement cookies tell us which pages to improve, and ads fund the site. You choose, and you can change your mind at the bottom of any page.',
    more: 'Details', accept: 'Accept all', refuse: 'Refuse all', custom: 'Customize', save: 'Save my choices', back: 'Back',
    an_t: 'Audience measurement', an_d: 'Google Analytics: which pages are read and from where. It helps us fix and improve the pages that matter.',
    ad_t: 'Advertising', ad_d: 'Google AdSense: the ads that pay for the site, and the cookies they use to limit repeats and measure results.',
  } : {
    title: 'Cookies : tu décides',
    text: "BrokenMeta.gg est gratuit. Les cookies de mesure nous disent quelles pages améliorer, et les pubs financent le site. Tu choisis, et tu peux changer d'avis en bas de n'importe quelle page.",
    more: 'Détails', accept: 'Tout accepter', refuse: 'Tout refuser', custom: 'Personnaliser', save: 'Enregistrer mes choix', back: 'Retour',
    an_t: "Mesure d'audience", an_d: 'Google Analytics : quelles pages sont lues et depuis où. Ça nous aide à corriger et améliorer les pages qui comptent.',
    ad_t: 'Publicité', ad_d: 'Google AdSense : les publicités qui financent le site, et les cookies qu\'elles utilisent pour limiter les répétitions et mesurer les résultats.',
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
      '.bm-consent{position:fixed;left:16px;bottom:16px;z-index:2147483000;width:min(380px,calc(100vw - 32px));background:var(--bg-2,#0d1245);color:var(--cream,#e9eeff);' +
      'border:1px solid var(--border-bright,#34419f);border-radius:14px;box-shadow:0 12px 40px rgba(2,4,30,.7);padding:14px 16px;font:400 13px/1.45 "Afacad Flux",system-ui,sans-serif}' +
      '.bm-consent h2{margin:0 0 4px;font:600 15px/1.3 "Cal Sans","Afacad Flux",system-ui,sans-serif}' +
      '.bm-consent p{margin:0 0 10px;color:var(--text-dim,#a6b2e6)}' +
      '.bm-consent a{color:var(--cyan,#cfe0ff);text-decoration:underline}' +
      '.bm-consent-btns{display:flex;gap:8px}' +
      '.bm-consent-btns button{flex:1 1 0;min-width:0;min-height:40px;padding:8px 6px;border-radius:10px;border:1px solid var(--border-bright,#34419f);background:var(--row,#0d1245);' +
      'color:var(--cream,#e9eeff);font:600 13px "Afacad Flux",system-ui,sans-serif;cursor:pointer}' +
      '.bm-consent-btns button:hover,.bm-consent-btns button:focus-visible{background:var(--row-hover,#172073);outline:2px solid var(--magenta,#2a63ff);outline-offset:1px}' +
      '.bm-consent-opt{display:flex;gap:12px;align-items:flex-start;padding:10px 0;border-top:1px solid var(--border,#1e2772)}' +
      '.bm-consent-opt input{width:20px;height:20px;margin-top:2px;flex:none;accent-color:#2a63ff}' +
      '.bm-consent-opt b{display:block;color:var(--cream,#e9eeff)}' +
      '.bm-consent-opt span{color:var(--text-dim,#a6b2e6)}' +
      '@media (max-width:520px){.bm-consent{left:8px;bottom:8px;width:calc(100vw - 16px);padding:12px}}';
    document.head.appendChild(st);
  }
  function close() { if (box) { box.remove(); box = null; } }
  function mk(tag, props, html) { var e = document.createElement(tag); for (var k in props) e.setAttribute(k, props[k]); if (html) e.innerHTML = html; return e; }

  function main(cur) {
    close(); css();
    box = mk('div', { 'class': 'bm-consent', role: 'dialog', 'aria-labelledby': 'bm-consent-t', 'aria-modal': 'false' });
    box.innerHTML = '<h2 id="bm-consent-t">' + T.title + '</h2><p>' + T.text + ' <a href="' + root + 'confidentialite/#cookies">' + T.more + '</a>.</p>' +
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
