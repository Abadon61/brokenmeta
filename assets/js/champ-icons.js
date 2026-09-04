
(function () {
  var icons = document.querySelectorAll('.champ-link-icon');
  if (!icons.length) return;
  var LABELS = {
    fr: {playrate: 'Popularité', avgplacement: 'Placement moyen', avgstar: 'Étoile moyenne',
         items: function (s) { return 'Objets fréquents : ' + s; }},
    en: {playrate: 'Play rate', avgplacement: 'Avg placement', avgstar: 'Avg star',
         items: function (s) { return 'Common items: ' + s; }}
  };
  var L = LABELS[document.documentElement.lang === 'en' ? 'en' : 'fr'];
  var tooltip = document.getElementById('tooltip');
  var dataPromise = fetch((window.BM_ROOT || '') + 'assets/data/champions.json').then(function (r) { return r.json(); }).catch(function () { return {}; });
  var champData = null;
  dataPromise.then(function (d) { champData = d; });

  function showTooltip(e) {
    if (!champData || !tooltip) return;
    var d = champData[e.currentTarget.dataset.champSlug];
    if (!d) return;
    tooltip.innerHTML = '<div class="tt-name">' + d.name + '</div>'
      + '<div class="tt-row"><span>' + L.playrate + '</span><b class="nums">' + d.pick_rate_pct + '</b></div>'
      + '<div class="tt-row"><span>' + L.avgplacement + '</span><b class="nums">' + d.avg_placement.toFixed(2) + '</b></div>'
      + '<div class="tt-row"><span>' + L.avgstar + '</span><b class="nums">' + d.avg_star_level.toFixed(1) + '\u2605</b></div>'
      + (d.top_items && d.top_items.length ? '<div class="tt-items">' + L.items(d.top_items.join(', ')) + '</div>' : '');
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

  icons.forEach(function (icon) {
    icon.addEventListener('mouseenter', showTooltip);
    icon.addEventListener('mousemove', moveTooltip);
    icon.addEventListener('mouseleave', hideTooltip);
    icon.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      var href = icon.dataset.champHref;
      if (href) location.href = href;
    });
  });
})();
