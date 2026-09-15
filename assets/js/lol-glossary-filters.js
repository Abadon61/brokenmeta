
(function () {
  var grid = document.getElementById('lolGlossaryGrid');
  if (!grid) return;
  var items = Array.prototype.slice.call(grid.querySelectorAll('.glossary-icon-item'));
  var searchInput = document.getElementById('lolGlossarySearch');
  var filterBar = document.getElementById('lolClassFilterBar');
  var emptyState = document.getElementById('lolGlossaryEmpty');
  var activeClass = 'ALL';

  function apply() {
    var q = (searchInput ? searchInput.value.trim().toLowerCase() : '');
    var visible = 0;
    items.forEach(function (el) {
      var classOk = activeClass === 'ALL' || (el.dataset.classes || '').indexOf(activeClass) !== -1;
      var searchOk = !q || (el.dataset.search || '').indexOf(q) !== -1;
      var show = classOk && searchOk;
      el.style.display = show ? '' : 'none';
      if (show) visible++;
    });
    if (emptyState) emptyState.hidden = visible !== 0;
  }
  if (filterBar) {
    filterBar.addEventListener('click', function (e) {
      var btn = e.target.closest('[data-filter-class]');
      if (!btn) return;
      [].forEach.call(filterBar.querySelectorAll('[data-filter-class]'), function (b) { b.dataset.active = String(b === btn); });
      activeClass = btn.dataset.filterClass;
      apply();
    });
  }
  if (searchInput) searchInput.addEventListener('input', apply);
})();
