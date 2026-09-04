
(function () {
  var bar = document.getElementById('typeFilterBar');
  if (!bar) return;
  var rows = document.querySelectorAll('#rows .comp-row');
  bar.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-filter-type]');
    if (!btn) return;
    [].forEach.call(bar.querySelectorAll('[data-filter-type]'), function (b) { b.dataset.active = String(b === btn); });
    var cat = btn.dataset.filterType;
    rows.forEach(function (row) {
      row.style.display = (cat === 'ALL' || row.dataset.playstyleCat === cat) ? '' : 'none';
    });
  });
})();
