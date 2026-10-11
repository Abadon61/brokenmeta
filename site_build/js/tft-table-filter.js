(function () {
  'use strict';
  // TFT ranking tables (champions, items, item combos, sleepers): a sticky bar above the table with tier chips and a search box.
  // The rows already carry data-tier; nothing else about the page is touched, so without JavaScript the full table stays as it was.
  var fr = (document.documentElement.lang || 'fr').slice(0, 2) === 'fr';
  var T = fr ? { all: 'Tous', search: 'Rechercher…', none: 'Aucun résultat.', tier: 'Tier ', of: ' / ' } : { all: 'All', search: 'Search…', none: 'No result.', tier: 'Tier ', of: ' / ' };
  var ORDER = ['S', 'A', 'B', 'C', 'D', 'HM'];

  function norm(s) { return (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }

  Array.prototype.forEach.call(document.querySelectorAll('.champ-table-wrap'), function (wrap) {
    var table = wrap.querySelector('table.champ-table');
    if (!table || !table.tBodies[0]) return;
    var rows = Array.prototype.slice.call(table.tBodies[0].rows);
    if (rows.length < 12) return;
    var counts = {};
    rows.forEach(function (r) {
      var t = r.getAttribute('data-tier') || '';
      counts[t] = (counts[t] || 0) + 1;
      var extra = Array.prototype.map.call(r.querySelectorAll('img[alt],img[title]'), function (i) { return (i.getAttribute('alt') || '') + ' ' + (i.getAttribute('title') || ''); }).join(' ');
      r._q = norm(r.textContent + ' ' + extra);
    });
    var tiers = ORDER.filter(function (t) { return counts[t]; });
    if (tiers.length < 2 && rows.length < 20) return;

    var bar = document.createElement('div');
    bar.className = 'tf-bar';
    var chips = document.createElement('div');
    chips.className = 'tf-chips';
    chips.setAttribute('role', 'group');
    var tag = '';
    function chip(label, t, n) {
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'tf-chip' + (t === '' ? ' is-on' : ''); b.setAttribute('data-tier', t);
      b.innerHTML = label + ' <span class="nums">' + n + '</span>';
      b.addEventListener('click', function () {
        tag = t;
        Array.prototype.forEach.call(chips.children, function (x) { x.classList.toggle('is-on', x === b); });
        apply();
      });
      chips.appendChild(b);
    }
    chip(T.all, '', rows.length);
    tiers.forEach(function (t) { chip(t === 'HM' ? 'Hors Meta' : T.tier + t, t, counts[t]); });
    var box = document.createElement('input');
    box.type = 'search'; box.className = 'tf-search'; box.placeholder = T.search; box.setAttribute('aria-label', T.search); box.autocomplete = 'off';
    var count = document.createElement('span');
    count.className = 'tf-count nums';
    bar.appendChild(chips); bar.appendChild(box); bar.appendChild(count);
    wrap.parentNode.insertBefore(bar, wrap);
    var none = document.createElement('p');
    none.className = 'tf-none'; none.hidden = true; none.textContent = T.none;
    wrap.parentNode.insertBefore(none, wrap.nextSibling);

    function apply() {
      var q = norm(box.value.trim()), shown = 0;
      rows.forEach(function (r) {
        var ok = (!tag || r.getAttribute('data-tier') === tag) && (!q || r._q.indexOf(q) > -1);
        r.hidden = !ok;
        if (ok) shown++;
      });
      count.textContent = shown + T.of + rows.length;
      none.hidden = shown > 0;
    }
    box.addEventListener('input', apply);
    apply();
  });
})();
