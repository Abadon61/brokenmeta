/* BrokenMeta DPS simulator, WoWSims Forever engine (2026-11-26): the open-source engine (github.com/wowsims/forever, MIT)
   compiled to WebAssembly and run in the visitor's browser, on the builds WoWSims publishes for each spec (presets.json).
   Step 1: preset build, fight length and number of fights; our gear / talents / addon import come next.
   The work is split over several workers (iterations / N each, distinct seeds) and the means are combined. */
(function () {
  'use strict';
  const box = document.getElementById('wsSim');
  if (!box) return;
  const base = box.dataset.base, fr = box.dataset.lang === 'fr';
  const T = fr ? {
    load: 'Chargement du moteur WoWSims (6 Mo, une seule fois)…', run: 'Simulation en cours…', err: 'Erreur du moteur : ',
    dps: 'DPS moyen', fights: 'combats', sem: 'erreur standard', src: 'Principales sources de dégâts', share: 'part',
    build: 'Build WoWSims', race: 'Race', none: 'Aucun résultat.', melee: 'Attaque auto', time: 's de calcul'
  } : {
    load: 'Loading the WoWSims engine (6 MB, once)…', run: 'Simulating…', err: 'Engine error: ',
    dps: 'Mean DPS', fights: 'fights', sem: 'standard error', src: 'Main damage sources', share: 'share',
    build: 'WoWSims build', race: 'Race', none: 'No result.', melee: 'Auto attack', time: 's of computing'
  };
  const $ = (s) => box.querySelector(s);
  const sel = $('#wsPreset'), dur = $('#wsDur'), its = $('#wsIters'), btn = $('#wsRun'), out = $('#wsOut'), log = $('#wsLog');
  let DATA = null, module = null, pool = null;
  const fmt = (v, d = 0) => v.toLocaleString(fr ? 'fr-FR' : 'en-US', { minimumFractionDigits: d, maximumFractionDigits: d });

  fetch(base + 'presets.json').then(r => r.json()).then(d => {
    DATA = d;
    const want = new URLSearchParams(location.search).get('ws');
    let lastSpec = '';
    for (const p of d.presets) {
      const o = document.createElement('option');
      o.value = p.id;
      o.textContent = (fr ? p.fr : p.en) + ' — ' + (p.preset || 'Default') + (d.best[p.spec] === p.id ? ' ★' : '');
      sel.appendChild(o);
      if (want ? p.id === want : (!lastSpec && d.best[p.spec] === p.id && p.spec === 'hunter_melee')) sel.value = p.id;
      lastSpec = lastSpec || '';
    }
    btn.disabled = false;
  });

  async function engine() {
    if (pool) return pool;
    log.textContent = T.load;
    const buf = await (await fetch(base + 'lib.wasm.gz')).arrayBuffer();
    const gz = new Uint8Array(buf, 0, 2);          // a host may already serve it with Content-Encoding: gzip, then the bytes are the raw module
    const raw = (gz[0] === 0x1f && gz[1] === 0x8b) ? await new Response(new Blob([buf]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer() : buf;
    module = await WebAssembly.compile(raw);
    const n = Math.max(1, Math.min(8, (navigator.hardwareConcurrency || 4) - 1));
    pool = Array.from({ length: n }, () => {
      const w = new Worker(box.dataset.worker);
      w.postMessage({ init: true, module, execUrl: new URL(base + 'wasm_exec.js', location.href).href });
      return w;
    });
    return pool;
  }

  function runOn(w, req, id) {
    return new Promise((ok, ko) => {
      const h = (e) => { if (e.data.id !== id) return; w.removeEventListener('message', h); e.data.error ? ko(new Error(e.data.error)) : ok(JSON.parse(e.data.out)); };
      w.addEventListener('message', h);
      w.postMessage({ id, req });
    });
  }

  function name(id) {
    const n = DATA.names;
    if (id.spellId) return n.spell[id.spellId] || ('#' + id.spellId);
    if (id.itemId) return n.item[id.itemId] || ('#' + id.itemId);
    return id.otherId === 'OtherActionAttack' ? T.melee : (id.otherId || '?').replace('OtherAction', '');
  }

  btn.addEventListener('click', async () => {
    if (!DATA) return;
    btn.disabled = true; out.innerHTML = '';
    const t0 = performance.now();
    try {
      const workers = await engine();
      log.textContent = T.run;
      const p = DATA.presets.find(x => x.id === sel.value);
      const total = +its.value, n = workers.length, per = Math.ceil(total / n);
      const jobs = workers.map((w, i) => {
        const req = JSON.parse(JSON.stringify(p.request));
        req.encounter.duration = +dur.value;
        req.simOptions = { iterations: per, randomSeed: String(101 + i * 7919) };
        return runOn(w, req, Date.now() + '-' + i);
      });
      const res = await Promise.all(jobs);
      const bad = res.find(r => !r.raidMetrics);
      if (bad) throw new Error(JSON.stringify(bad.error || bad).slice(0, 300));
      // combine the workers' means and spreads (equal sample sizes)
      const means = res.map(r => r.raidMetrics.dps.avg), sds = res.map(r => r.raidMetrics.dps.stdev);
      const mean = means.reduce((a, b) => a + b, 0) / n;
      const varw = sds.reduce((a, s) => a + s * s, 0) / n + means.reduce((a, m) => a + (m - mean) ** 2, 0) / n;
      const sem = Math.sqrt(varw / (per * n));
      // damage sources over all workers
      const dmg = new Map();
      for (const r of res) for (const a of r.raidMetrics.parties[0].players[0].actions || []) {
        const d = (a.targets || []).reduce((s, t) => s + (t.damage || 0), 0);
        if (!d) continue;
        const k = name(a.id);
        dmg.set(k, (dmg.get(k) || 0) + d);
      }
      for (const r of res) for (const pet of r.raidMetrics.parties[0].players[0].pets || []) for (const a of pet.actions || []) {
        const d = (a.targets || []).reduce((s, t) => s + (t.damage || 0), 0);
        if (d) dmg.set(pet.name, (dmg.get(pet.name) || 0) + d);
      }
      const tot = [...dmg.values()].reduce((a, b) => a + b, 0) || 1;
      const top = [...dmg.entries()].sort((a, b) => b[1] - a[1]).slice(0, 10);
      out.innerHTML = '<div class="ws-big"><b class="nums">' + fmt(mean, 1) + '</b> ' + T.dps + ' <span class="ws-sem">± ' + fmt(sem, 1) + ' (' + T.sem + ')</span></div>'
        + '<p class="ws-meta">' + fmt(per * n) + ' ' + T.fights + ' · ' + dur.value + ' s · ' + T.race + ' : ' + p.race.replace('Race', '') + ' · ' + fmt((performance.now() - t0) / 1000, 1) + ' ' + T.time + '</p>'
        + '<h3>' + T.src + '</h3><table class="ws-src"><tbody>' + top.map(([k, v]) => '<tr><td>' + k.replace(/</g, '&lt;') + '</td><td class="nums">' + fmt(100 * v / tot, 1) + ' %</td></tr>').join('') + '</tbody></table>';
      log.textContent = '';
    } catch (e) {
      log.textContent = T.err + e.message;
      console.error(e);
    } finally { btn.disabled = false; }
  });
})();
