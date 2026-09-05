
(function () {
  var LABELS = {
    fr: {playrate: 'Popularité', avgplacement: 'Placement moyen', avgstar: 'Étoile moyenne',
         items: function (s) { return 'Objets fréquents : ' + s; }},
    en: {playrate: 'Play rate', avgplacement: 'Avg placement', avgstar: 'Avg star',
         items: function (s) { return 'Common items: ' + s; }}
  };
  var L = LABELS[document.documentElement.lang === 'en' ? 'en' : 'fr'];
  var tooltip = document.getElementById('tooltip');
  var champData = null;
  fetch((window.BM_ROOT || '') + 'assets/data/champions.json').then(function (r) { return r.json(); }).then(function (d) { champData = d; }).catch(function () {});

  function showTooltip(icon, e) {
    if (!champData || !tooltip) return;
    var d = champData[icon.dataset.champSlug];
    if (!d) return;
    var traitsHtml = (d.traits || []).map(function (t) {
      return '<span class="tt-trait-chip"><img src="' + (window.BM_ROOT || '') + 'assets/traits/' + t.slug + '.png" alt="">' + t.name + '</span>';
    }).join('');
    tooltip.innerHTML = '<div class="tt-name">' + d.name + '</div>'
      + (traitsHtml ? '<div class="tt-traits">' + traitsHtml + '</div>' : '')
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

  document.addEventListener('mouseover', function (e) {
    var icon = e.target.closest('.champ-link-icon');
    if (icon) showTooltip(icon, e);
  });
  document.addEventListener('mousemove', function (e) {
    if (e.target.closest('.champ-link-icon')) moveTooltip(e);
  });
  document.addEventListener('mouseout', function (e) {
    if (e.target.closest('.champ-link-icon')) hideTooltip();
  });
  document.addEventListener('click', function (e) {
    var icon = e.target.closest('.champ-link-icon');
    if (!icon) return;
    e.preventDefault();
    e.stopPropagation();
    var href = icon.dataset.champHref;
    if (href) location.href = href;
  });
})();
