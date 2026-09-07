
(function () {
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.gameplan-tab-btn');
    if (!btn) return;
    var block = btn.closest('.gameplan-block');
    if (!block) return;
    var idx = btn.dataset.gameplanTab;
    block.querySelectorAll('.gameplan-tab-btn').forEach(function (b) {
      var active = b.dataset.gameplanTab === idx;
      b.dataset.active = String(active);
      b.setAttribute('aria-selected', String(active));
    });
    block.querySelectorAll('.gameplan-tab-panel').forEach(function (p) {
      p.hidden = p.dataset.gameplanPanel !== idx;
    });
  });
})();
