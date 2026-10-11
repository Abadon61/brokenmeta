(function () {
  'use strict';
  // TFT long pages: (1) augment glossary = rarity chips + search; (2) any page with 4+ sections (composition sheets, methodology...) = a
  // sticky shortcut bar to each section. Both only add elements around the existing content: without JavaScript the pages are unchanged.
  var fr = (document.documentElement.lang || 'fr').slice(0, 2) === 'fr';
  function norm(s) { return (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text) e.textContent = text; return e; }

  // ---- augment glossary
  var grids = document.querySelectorAll('.augment-grid');
  if (grids.length) {
    var titles = Array.prototype.slice.call(document.querySelectorAll('.augment-tier-title'));
    var cards = Array.prototype.slice.call(document.querySelectorAll('.augment-card'));
    cards.forEach(function (c) { c._q = norm(c.textContent); });
    var bar = el('div', 'tf-bar'), chips = el('div', 'tf-chips'), tier = '';
    function chip(label, t, n) {
      var b = el('button', 'tf-chip' + (t === '' ? ' is-on' : '')); b.type = 'button';
      b.innerHTML = label + ' <span class="nums">' + n + '</span>';
      b.addEventListener('click', function () {
        tier = t; Array.prototype.forEach.call(chips.children, function (x) { x.classList.toggle('is-on', x === b); }); apply();
      });
      chips.appendChild(b);
    }
    chip(fr ? 'Tous' : 'All', '', cards.length);
    titles.forEach(function (h) {
      var n = h.nextElementSibling ? h.nextElementSibling.querySelectorAll('.augment-card').length : 0;
      chip(h.firstChild.textContent.trim(), h.getAttribute('data-tier'), n);
    });
    var box = el('input', 'tf-search'); box.type = 'search'; box.placeholder = fr ? 'Rechercher un augment…' : 'Search an augment…'; box.autocomplete = 'off';
    box.setAttribute('aria-label', box.placeholder);
    var count = el('span', 'tf-count nums');
    bar.appendChild(chips); bar.appendChild(box); bar.appendChild(count);
    grids[0].parentNode.insertBefore(bar, titles[0] || grids[0]);
    var none = el('p', 'tf-none', fr ? 'Aucun augment ne correspond.' : 'No augment matches.'); none.hidden = true;
    grids[grids.length - 1].parentNode.insertBefore(none, grids[grids.length - 1].nextSibling);
    function apply() {
      var q = norm(box.value.trim()), shown = 0;
      titles.forEach(function (h) {
        var grid = h.nextElementSibling, inTier = !tier || h.getAttribute('data-tier') === tier, any = 0;
        Array.prototype.forEach.call(grid.querySelectorAll('.augment-card'), function (c) {
          var ok = inTier && (!q || c._q.indexOf(q) > -1); c.hidden = !ok; if (ok) any++;
        });
        h.hidden = grid.hidden = !any; shown += any;
      });
      count.textContent = shown + ' / ' + cards.length; none.hidden = shown > 0;
    }
    box.addEventListener('input', apply); apply();
    return;
  }

  // ---- long pages: shortcut bar to the sections
  var heads = Array.prototype.slice.call(document.querySelectorAll('.page h2.fiche-section-title')).filter(function (h) { return h.textContent.trim() && !h.closest('.faq-block'); });
  if (heads.length < 4 || document.querySelector('.tl-nav, .lb-nav, .tf-bar')) return;      // the tier list and the leaderboard have their own bar
  var nav = el('nav', 'tf-bar ts-bar'); nav.setAttribute('aria-label', fr ? 'Sections' : 'Sections');
  var links = [];
  heads.forEach(function (h, i) {
    if (!h.id) h.id = 'sec-' + (i + 1);
    h.style.scrollMarginTop = '130px';
    var a = el('a', 'tf-chip', h.textContent.replace(/\s+/g, ' ').trim()); a.href = '#' + h.id; nav.appendChild(a); links.push(a);
  });
  var anchor = heads[0].closest('section') || heads[0];
  anchor.parentNode.insertBefore(nav, anchor);
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) links.forEach(function (a, i) { a.classList.toggle('is-on', heads[i] === e.target); }); });
    }, { rootMargin: '-140px 0px -70% 0px' });
    heads.forEach(function (h) { io.observe(h); });
  }
})();
