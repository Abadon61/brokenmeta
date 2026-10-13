// "Je suis niveau X": which dungeons to run at a level, and the best item to look for in each for a spec (hub /wow-forever/dungeons/).
// Data (levels from the beta data, best items from the simulator) comes from the page's JSON (#dfdData), built by build_site.py.
(function () {
  'use strict';
  var root = document.getElementById('dfd');
  var dataEl = document.getElementById('dfdData');
  if (!root || !dataEl) return;
  var D;
  try { D = JSON.parse(dataEl.textContent); } catch (e) { return; }
  var lang = root.getAttribute('data-lang') || 'fr';
  var base = root.getAttribute('data-root') || '';
  var levelEl = document.getElementById('dfdLevel'), specEl = document.getElementById('dfdSpec'), out = document.getElementById('dfdOut');
  var T = D.i18n;

  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }

  function card(d, spec) {
    var a = el('a', 'dh-card'); a.href = base + d.path;
    a.appendChild(el('b', null, d.name));
    var chips = el('span', 'dh-chips');
    var lv = el('span', 'gh-chip is-gold', T.levels + ' '); lv.appendChild(el('b', 'nums', d.range || (d.lo + '-' + d.hi))); chips.appendChild(lv);
    if (d.loc) chips.appendChild(el('span', 'gh-chip', d.loc));
    if (d.thin) chips.appendChild(el('span', 'gh-chip', T.thin));
    a.appendChild(chips);
    if (spec) {
      var b = d.best[spec], line = el('span', 'dfd-best');
      line.appendChild(el('small', null, T.best + ' : '));
      if (b) {
        var it = el('span', 'dg-q' + (b.q || 1), b.name); line.appendChild(it);
        if (b.slot) line.appendChild(el('small', null, ' · ' + b.slot));
      } else line.appendChild(el('span', null, T.nobest));
      a.appendChild(line);
    }
    a.appendChild(el('span', 'dh-go', T.see + ' →'));
    return a;
  }

  function section(title, list, spec) {
    var wrap = el('div', 'dfd-sec'); wrap.appendChild(el('h3', 'gs-sub', title));
    var grid = el('div', 'dh-grid');
    list.forEach(function (d) { grid.appendChild(card(d, spec)); });
    wrap.appendChild(grid); return wrap;
  }

  function render() {
    var lv = parseInt(levelEl.value, 10);
    out.textContent = '';
    if (!(lv >= 1 && lv <= 60)) return;
    var spec = specEl.value;
    var now = D.d.filter(function (d) { return d.lo <= lv && lv <= d.hi; });
    var soon = D.d.filter(function (d) { return d.lo > lv && d.lo <= lv + 5; });
    if (!now.length && !soon.length) { out.appendChild(el('p', 'gs-lede', T.none)); return; }
    if (now.length) out.appendChild(section(T.now, now, spec));
    if (soon.length) out.appendChild(section(T.soon, soon, spec));
  }

  levelEl.addEventListener('input', render);
  specEl.addEventListener('change', render);
  try { var q = new URLSearchParams(location.search); if (q.get('niveau') || q.get('level')) levelEl.value = q.get('niveau') || q.get('level'); } catch (e) { /* no query string */ }
  render();
})();
