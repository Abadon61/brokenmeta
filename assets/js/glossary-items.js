
(function () {
  var tooltip = document.getElementById('tooltip');
  var itemData = null;
  var itemFile = document.documentElement.lang === 'fr' ? 'glossary-items_fr.json' : 'glossary-items.json';
  fetch((window.BM_ROOT || '') + 'assets/data/' + itemFile).then(function (r) { return r.json(); }).then(function (d) { itemData = d; }).catch(function () {});

  function showTooltip(icon, e) {
    if (!itemData || !tooltip) return;
    var d = itemData[icon.dataset.itemSlug];
    if (!d) return;
    var compHtml = (d.composition || []).map(function (c) {
      return '<span class="tt-trait-chip"><img src="' + (window.BM_ROOT || '') + 'assets/items/' + c.slug + '.png" alt="">' + c.name + '</span>';
    }).join('');
    tooltip.innerHTML = '<div class="tt-name">' + d.name + '</div>'
      + (compHtml ? '<div class="tt-traits">' + compHtml + '</div>' : '');
    tooltip.dataset.visible = 'true';
    moveTooltip(e);
  }
  function moveTooltip(e) {
    if (!tooltip) return;
    var pad = 14, x = e.clientX + pad, y = e.clientY + pad;
    if (x + 190 > window.innerWidth) x = e.clientX - 190 - pad;
    if (y + 130 > window.innerHeight) y = e.clientY - 130 - pad;
    tooltip.style.left = x + 'px';
    tooltip.style.top = y + 'px';
  }
  function hideTooltip() { if (tooltip) tooltip.dataset.visible = 'false'; }

  document.addEventListener('mouseover', function (e) {
    var icon = e.target.closest('.item-tt-icon');
    if (icon) showTooltip(icon, e);
  });
  document.addEventListener('mousemove', function (e) {
    if (e.target.closest('.item-tt-icon')) moveTooltip(e);
  });
  document.addEventListener('mouseout', function (e) {
    if (e.target.closest('.item-tt-icon')) hideTooltip();
  });
})();
