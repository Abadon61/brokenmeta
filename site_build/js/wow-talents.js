/* World of Warcraft: Forever talent calculator -- data-driven, no talent is hard-coded here.
   Data comes from <script id="wowTalentData" type="application/json"> (see build_site.py / wow_talents.py).
   Rules (RULES in wow_talents.py): a fixed number of points shared by 3 trees, 7 rows, a row unlocks for every N points
   spent in the rows strictly below it (same tree), optional prerequisite talent, per-talent ranks. */
(function () {
  'use strict';
  var root = document.getElementById('wowTalents');
  var dataEl = document.getElementById('wowTalentData');
  if (!root || !dataEl) return;

  var data = JSON.parse(dataEl.textContent);
  var ui = data.ui, rules = data.rules, specs = data.specs;
  var ranks = {}, byId = {}, removeMode = false, tipTalent = null;

  specs.forEach(function (s, si) {
    s.order = s.talents.slice().sort(function (a, b) { return a.row - b.row || a.col - b.col; });
    s.talents.forEach(function (t) { t._spec = si; byId[t.id] = t; });
  });
  var all = [];
  specs.forEach(function (s) { all = all.concat(s.order); });

  function fmt(str, vars) { return str.replace(/\{(\w+)\}/g, function (_, k) { return vars[k] === undefined ? '' : vars[k]; }); }
  function el(tag, cls, text) { var n = document.createElement(tag); if (cls) n.className = cls; if (text !== undefined) n.textContent = text; return n; }

  /* ---------------------------------------------------------------- rules */
  function rank(t) { return ranks[t.id] || 0; }
  function spentIn(si, belowRow) {
    var n = 0;
    specs[si].talents.forEach(function (t) { if (t.row < belowRow) n += rank(t); });
    return n;
  }
  function specSpent(si) { return spentIn(si, 99); }
  function total() { var n = 0; all.forEach(function (t) { n += rank(t); }); return n; }
  /* gates: explicit per-talent list {through_row, points} (read from the game data); default = (row-1)*N points in the rows below */
  function gatesOf(t) { return t.gates && t.gates.length ? t.gates : (t.row > 1 ? [{ through_row: t.row - 1, points: (t.row - 1) * rules.points_per_row }] : []); }
  function gateOk(t) { return gatesOf(t).every(function (g) { return spentIn(t._spec, g.through_row + 1) >= g.points; }); }
  function rowOk(t) { return gateOk(t); }
  function asList(v) { return !v ? [] : (Array.isArray(v) ? v : [v]); }
  function reqMet(q) { return rank(byId[q.id]) >= q.rank; }
  function reqOk(t) {
    var all = asList(t.requires), any = asList(t.requires_any);
    return all.every(reqMet) && (!any.length || any.some(reqMet));
  }
  function canAdd(t) { return total() < rules.total_points && rank(t) < t.max_rank && rowOk(t) && reqOk(t); }
  function valid() { return all.every(function (t) { return rank(t) === 0 || (rowOk(t) && reqOk(t)); }); }
  function canRemove(t) {
    if (!rank(t)) return false;
    ranks[t.id] = rank(t) - 1;
    var ok = valid();
    ranks[t.id] = rank(t) + 1;
    return ok;
  }
  function add(t) { if (!canAdd(t)) return false; ranks[t.id] = rank(t) + 1; changed(); return true; }
  function remove(t) { if (!canRemove(t)) return false; ranks[t.id] = rank(t) - 1; if (!ranks[t.id]) delete ranks[t.id]; changed(); return true; }
  function levelFor(points) { return points > 0 ? rules.first_level - 1 + points : 0; }

  /* ---------------------------------------------------------------- share link */
  function encode() {
    return '#b=' + data.rev + specs.map(function (s) { return '.' + s.order.map(function (t) { return rank(t); }).join(''); }).join('');
  }
  function decode(hash) {
    var m = /^#b=([0-9a-f]{6})((?:\.[0-9]*)+)$/.exec(hash || '');
    if (!m) return null;
    if (m[1] !== data.rev) return 'rev';
    var parts = m[2].slice(1).split('.');
    if (parts.length !== specs.length) return 'bad';
    var next = {};
    for (var i = 0; i < specs.length; i++) {
      if (parts[i].length !== specs[i].order.length) return 'bad';
      for (var j = 0; j < parts[i].length; j++) {
        var r = +parts[i][j];
        if (r > specs[i].order[j].max_rank) return 'bad';
        if (r) next[specs[i].order[j].id] = r;
      }
    }
    var backup = ranks; ranks = next;
    if (!valid() || total() > rules.total_points) { ranks = backup; return 'bad'; }
    return 'ok';
  }

  /* ---------------------------------------------------------------- DOM */
  var bar = el('div', 'wt-bar'), trees = el('div', 'wt-trees'), tip = el('div', 'wt-tip');
  tip.setAttribute('role', 'tooltip'); tip.hidden = true;
  var pts = el('div', 'wt-stat'), left = el('div', 'wt-stat'), lvl = el('div', 'wt-stat'), split = el('div', 'wt-stat');
  var actions = el('div', 'wt-actions');
  var btnReset = el('button', 'wt-btn', ui.reset), btnShare = el('button', 'wt-btn wt-btn-main', ui.share), btnMode = el('button', 'wt-btn wt-mode', ui.removeMode);
  [btnReset, btnShare, btnMode].forEach(function (b) { b.type = 'button'; });
  btnMode.setAttribute('aria-pressed', 'false');
  actions.appendChild(btnMode); actions.appendChild(btnReset); actions.appendChild(btnShare);
  [pts, left, lvl, split].forEach(function (s) { bar.appendChild(s); });
  bar.appendChild(actions);
  var notice = el('p', 'wt-notice'); notice.hidden = true;
  var hint = el('p', 'wt-hint', ui.hint);
  root.appendChild(bar); root.appendChild(notice); root.appendChild(trees); root.appendChild(hint); root.appendChild(tip);

  function initials(name) {
    var w = name.split(/\s+/).filter(Boolean);
    return (w.length > 1 ? w[0][0] + w[1][0] : name.slice(0, 2)).toUpperCase();
  }

  var SVG_NS = 'http://www.w3.org/2000/svg';
  var nodeEls = {}, treeEls = [];
  specs.forEach(function (s, si) {
    var tree = el('section', 'wt-tree'); tree.setAttribute('aria-label', s.name);
    var head = el('header', 'wt-tree-head');
    var title = el('h3', 'wt-tree-title', s.name), count = el('span', 'wt-tree-count', '0');
    var reset = el('button', 'wt-tree-reset', ui.resetTree); reset.type = 'button';
    reset.addEventListener('click', function () { s.talents.forEach(function (t) { delete ranks[t.id]; }); changed(); });
    head.appendChild(title); head.appendChild(count); head.appendChild(reset);
    var grid = el('div', 'wt-grid');
    var rowLabels = [];
    var svg = document.createElementNS(SVG_NS, 'svg');
    svg.setAttribute('class', 'wt-arrows'); svg.setAttribute('aria-hidden', 'true');
    grid.appendChild(svg);
    for (var r = 1; r <= rules.rows; r++) {
      var lab = el('div', 'wt-row-label', r > 1 ? String((r - 1) * rules.points_per_row) : '');
      lab.style.gridRow = String(r); lab.style.gridColumn = '1';
      grid.appendChild(lab); rowLabels[r] = lab;
    }
    s.order.forEach(function (t) {
      var b = el('button', 'wt-node'); b.type = 'button';
      b.style.gridRow = String(t.row); b.style.gridColumn = String(t.col + 1);
      if (t.icon) {
        var img = el('img', 'wt-icon'); img.src = t.icon; img.alt = ''; img.width = 56; img.height = 56; img.loading = 'lazy';
        img.addEventListener('error', function () { img.replaceWith(el('span', 'wt-mark', initials(t.name))); });   /* broken image: fall back to initials */
        b.appendChild(img);
      } else b.appendChild(el('span', 'wt-mark', initials(t.name)));
      var badge = el('i', 'wt-rank', '0/' + t.max_rank); b.appendChild(badge);
      b.addEventListener('click', function (e) { if (e.shiftKey || removeMode) remove(t); else add(t); showTip(t, b); });
      b.addEventListener('contextmenu', function (e) { e.preventDefault(); remove(t); showTip(t, b); });
      b.addEventListener('keydown', function (e) { if (e.key === 'Backspace' || e.key === 'Delete') { e.preventDefault(); remove(t); showTip(t, b); } });
      b.addEventListener('mouseenter', function () { showTip(t, b); });
      b.addEventListener('focus', function () { showTip(t, b); });
      b.addEventListener('mouseleave', hideTip);
      b.addEventListener('blur', hideTip);
      grid.appendChild(b);
      nodeEls[t.id] = { btn: b, badge: badge };
    });
    tree.appendChild(head); tree.appendChild(grid); trees.appendChild(tree);
    treeEls.push({ count: count, rowLabels: rowLabels, grid: grid, svg: svg, arrows: [] });
  });

  /* ---------------------------------------------------------------- prerequisite arrows */
  function svgEl(tag, attrs) { var n = document.createElementNS(SVG_NS, tag); for (var k in attrs) n.setAttribute(k, attrs[k]); return n; }
  function box(t) { var b = nodeEls[t.id].btn; return { x: b.offsetLeft, y: b.offsetTop, w: b.offsetWidth, h: b.offsetHeight }; }
  function layoutArrows() {
    treeEls.forEach(function (te, si) {
      var svg = te.svg;
      svg.textContent = ''; te.arrows = [];
      svg.setAttribute('width', te.grid.clientWidth); svg.setAttribute('height', te.grid.clientHeight);
      svg.setAttribute('viewBox', '0 0 ' + te.grid.clientWidth + ' ' + te.grid.clientHeight);
      specs[si].talents.forEach(function (t) {
        var links = asList(t.requires).map(function (q) { return { q: q, any: false }; }).concat(asList(t.requires_any).map(function (q) { return { q: q, any: true }; }));
        links.forEach(function (lk) {
          var s = box(byId[lk.q.id]), d = box(t), pts, tip;
          var sameRow = byId[lk.q.id].row === t.row, gap = 6;
          if (sameRow) {                                           /* horizontal: side to side */
            var sy = s.y + s.h / 2, right = d.x > s.x;
            var x1 = right ? s.x + s.w : s.x, x2 = right ? d.x : d.x + d.w;
            pts = 'M' + x1 + ',' + sy + ' L' + x2 + ',' + sy;
            tip = right ? [[x2, sy], [x2 - 8, sy - 5], [x2 - 8, sy + 5]] : [[x2, sy], [x2 + 8, sy - 5], [x2 + 8, sy + 5]];
          } else {
            var cx1 = s.x + s.w / 2, cx2 = d.x + d.w / 2, y1 = s.y + s.h, y2 = d.y;
            if (Math.abs(cx1 - cx2) < 2) pts = 'M' + cx1 + ',' + y1 + ' L' + cx2 + ',' + y2;
            else { var my = y2 - gap; pts = 'M' + cx1 + ',' + y1 + ' L' + cx1 + ',' + my + ' L' + cx2 + ',' + my + ' L' + cx2 + ',' + y2; }
            tip = [[cx2, y2], [cx2 - 5, y2 - 8], [cx2 + 5, y2 - 8]];
          }
          var path = svgEl('path', { d: pts, 'class': 'wt-arrow' + (lk.any ? ' wt-arrow-any' : '') });
          var head = svgEl('polygon', { points: tip.map(function (p) { return p.join(','); }).join(' '), 'class': 'wt-arrowhead' });
          svg.appendChild(path); svg.appendChild(head);
          te.arrows.push({ q: lk.q, path: path, head: head });
        });
      });
    });
    updateArrows();
  }
  function updateArrows() {
    treeEls.forEach(function (te) {
      te.arrows.forEach(function (a) {
        var met = reqMet(a.q) ? 'true' : 'false';
        a.path.setAttribute('data-met', met); a.head.setAttribute('data-met', met);
      });
    });
  }

  /* ---------------------------------------------------------------- tooltip */
  function tipHtml(t) {
    var r = rank(t);
    var box = document.createDocumentFragment();
    box.appendChild(el('b', 'wt-tip-name', t.name));
    box.appendChild(el('div', 'wt-tip-rank', fmt(ui.rankOf, { r: r, max: t.max_rank })));
    box.appendChild(el('p', 'wt-tip-desc', t.desc[Math.max(0, r - 1)]));
    if (r > 0 && r < t.max_rank) {
      box.appendChild(el('div', 'wt-tip-next', ui.nextRank));
      box.appendChild(el('p', 'wt-tip-desc', t.desc[r]));
    }
    if (t.incomplete) box.appendChild(el('p', 'wt-tip-note', ui.incomplete));
    gatesOf(t).forEach(function (g) {
      var have = spentIn(t._spec, g.through_row + 1);
      if (have < g.points) box.appendChild(el('p', 'wt-tip-req', fmt(ui.needPoints, { n: g.points, rows: g.through_row, have: have, tree: specs[t._spec].name })));
    });
    if (!reqOk(t)) {
      var all = asList(t.requires).filter(function (q) { return !reqMet(q); }), any = asList(t.requires_any);
      all.forEach(function (q) { box.appendChild(el('p', 'wt-tip-req', fmt(ui.needTalent, { name: byId[q.id].name, r: q.rank }))); });
      if (any.length && !any.some(reqMet)) box.appendChild(el('p', 'wt-tip-req', fmt(ui.needAny, { names: any.map(function (q) { return byId[q.id].name; }).join(' / ') })));
    }
    return box;
  }
  function showTip(t, anchor) {
    tipTalent = t;
    tip.textContent = ''; tip.appendChild(tipHtml(t)); tip.hidden = false;
    var a = anchor.getBoundingClientRect(), w = tip.offsetWidth, h = tip.offsetHeight;
    var x = a.right + 10; if (x + w > window.innerWidth - 8) x = Math.max(8, a.left - w - 10);
    var y = Math.min(Math.max(8, a.top), window.innerHeight - h - 8);
    tip.style.left = x + 'px'; tip.style.top = y + 'px';
  }
  function hideTip() { tipTalent = null; tip.hidden = true; }

  /* ---------------------------------------------------------------- update */
  function update() {
    var n = total();
    pts.textContent = fmt(ui.points, { n: n, max: rules.total_points });
    left.textContent = fmt(ui.pointsLeft, { n: rules.total_points - n });
    lvl.textContent = n > 0 ? fmt(ui.level, { n: levelFor(n) }) : ui.levelNone;
    split.textContent = specs.map(function (s, i) { return specSpent(i); }).join(' / ');
    all.forEach(function (t) {
      var r = rank(t), st = r >= t.max_rank ? 'maxed' : r > 0 ? 'active' : canAdd(t) ? 'available' : 'locked';
      var n2 = nodeEls[t.id];
      n2.btn.setAttribute('data-state', st);
      n2.badge.textContent = r + '/' + t.max_rank;
      n2.btn.setAttribute('aria-label', t.name + ', ' + fmt(ui.rankOf, { r: r, max: t.max_rank }));
    });
    specs.forEach(function (s, si) {
      treeEls[si].count.textContent = fmt(ui.treePoints, { n: specSpent(si) });
      for (var r = 2; r <= rules.rows; r++) {
        var inRow = specs[si].talents.filter(function (x) { return x.row === r; });
        var open = inRow.length ? inRow.some(gateOk) : spentIn(si, r) >= (r - 1) * rules.points_per_row;
        treeEls[si].rowLabels[r].setAttribute('data-open', open ? 'true' : 'false');
      }
    });
    if (tipTalent && !tip.hidden) tip.replaceChildren(tipHtml(tipTalent));
    updateArrows();
  }
  function changed() {
    update();
    try { history.replaceState(null, '', total() ? encode() : location.pathname + location.search); } catch (e) { /* file:// or sandbox */ }
  }

  /* ---------------------------------------------------------------- actions */
  btnReset.addEventListener('click', function () { ranks = {}; changed(); });
  btnMode.addEventListener('click', function () {
    removeMode = !removeMode;
    btnMode.setAttribute('aria-pressed', String(removeMode));
    btnMode.textContent = removeMode ? ui.removeModeOn : ui.removeMode;
    btnMode.classList.toggle('wt-btn-on', removeMode);
  });
  btnShare.addEventListener('click', function () {
    var url = location.origin + location.pathname + encode();
    function done() { btnShare.textContent = ui.copied; setTimeout(function () { btnShare.textContent = ui.share; }, 1800); }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(url).then(done, function () { window.prompt(ui.share, url); });
    else window.prompt(ui.share, url);
  });

  layoutArrows();
  window.addEventListener('resize', layoutArrows);
  window.addEventListener('load', layoutArrows);
  if (window.ResizeObserver) { var ro = new ResizeObserver(layoutArrows); treeEls.forEach(function (te) { ro.observe(te.grid); }); }

  var loaded = decode(location.hash);
  if (loaded === 'rev' || loaded === 'bad') { notice.textContent = loaded === 'rev' ? ui.linkOld : ui.linkBad; notice.hidden = false; }
  update();

  /* small debug surface for the test build (no effect on visitors) */
  window.__wowTalents = { ranks: function () { return ranks; }, add: function (id) { return add(byId[id]); }, remove: function (id) { return remove(byId[id]); },
                          canAdd: function (id) { return canAdd(byId[id]); }, canRemove: function (id) { return canRemove(byId[id]); }, valid: valid, total: total, encode: encode, decode: decode, specs: specs };
})();
