(function () {
  'use strict';
  var sel = document.getElementById('dgSpec');
  var table = document.getElementById('dgTable');
  if (!sel || !table) return;
  var rel = {};
  try { rel = JSON.parse(document.getElementById('dgRel').textContent); } catch (e) { return; }
  var tbody = table.querySelector('tbody');
  var rows = Array.prototype.slice.call(tbody.querySelectorAll('tr'));
  var impCells = table.querySelectorAll('.dg-imp');
  var none = document.getElementById('dgNone');

  function cmp(a, b) {
    for (var i = 0; i < 5; i++) { if (a[i] !== b[i]) return a[i] - b[i]; }
    return 0;
  }

  function apply(spec) {
    var i;
    for (i = 0; i < impCells.length; i++) impCells[i].hidden = !spec;
    if (!spec) {
      rows.sort(function (a, b) { return a.getAttribute('data-i') - b.getAttribute('data-i'); });
      rows.forEach(function (r) { r.hidden = false; tbody.appendChild(r); r.lastElementChild.textContent = ''; });
      none.hidden = true;
      return;
    }
    var list = [];
    rows.forEach(function (r) {
      var e = (rel[r.getAttribute('data-id')] || {})[spec];
      if (e) list.push([r, e]); else r.hidden = true;
    });
    list.sort(function (a, b) { return cmp(a[1], b[1]); });
    list.forEach(function (p) {
      var r = p[0], e = p[1];
      r.hidden = false;
      tbody.appendChild(r);
      var txt = e[0] === 1 ? table.getAttribute('data-t1') : table.getAttribute('data-t2');
      if (e[5] > 0) txt += ' (' + table.getAttribute('data-from').replace('{n}', e[5]) + ')';
      r.lastElementChild.textContent = txt;
      r.lastElementChild.className = 'dg-imp dg-t' + e[0];
    });
    none.hidden = list.length > 0;
  }

  function fromHash() {
    var m = /^#spec=([a-z\-]+\/[a-z\-]+)$/.exec(location.hash || '');
    return m ? m[1] : '';
  }

  sel.addEventListener('change', function () {
    var v = sel.value;
    if (window.history && history.replaceState) history.replaceState(null, '', v ? '#spec=' + v : location.pathname + location.search);
    apply(v);
  });
  var start = fromHash();
  if (start) {
    var ok = false;
    for (var i = 0; i < sel.options.length; i++) if (sel.options[i].value === start) ok = true;
    if (ok) { sel.value = start; apply(start); }
  }
})();
