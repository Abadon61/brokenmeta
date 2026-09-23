(function () {
  'use strict';
  // Minimal event-driven combat simulator (Fury Warrior, single target, Bloodthirst + Whirlwind only --
  // no Heroic Strike/Rage economy, no procs, no DoTs yet). Modeled on SimulationCraft's own architecture
  // (an event queue, an action-priority check at every free moment, per-swing hit/crit RNG rolls, averaged
  // over many independent iterations) but written from scratch for WoW: Forever's real, much smaller Fury
  // kit -- see /wow-forever/theorycraft/ for the real spell values and their sources.
  // GCD = 1.5s, Bloodthirst CD = 6s, Whirlwind CD = 10s: all read from WoW: Forever's own Wowhead tooltips.
  var GCD = 1.5, BT_CD = 6, WW_CD = 10;
  var BT_AP_COEFF = 0.35, BT_SP_COEFF = 1.00;

  var ids = ['tcAP', 'tcSP', 'tcHit', 'tcCrit', 'tcWpnDmg', 'tcWpnSpeed'];
  var runBtn = document.getElementById('simRun');
  var fightLenInput = document.getElementById('simFightLen');
  var iterInput = document.getElementById('simIterations');
  if (!runBtn) return;

  function num(id) {
    var el = document.getElementById(id);
    var v = parseFloat(el && el.value);
    return isFinite(v) ? v : 0;
  }

  // One simulated fight: returns total damage dealt over fightLen seconds.
  function simulateOnce(p) {
    var events = [{ time: p.weaponSpeed, type: 'swing' }, { time: 0, type: 'decision' }];
    var btReady = 0, wwReady = 0, gcdReady = 0;
    var dmg = 0, btCasts = 0, wwCasts = 0, swings = 0;

    function roll(t) {
      // 0 = miss, 1 = normal hit, 2 = critical hit (200% damage, standard WoW mechanic)
      if (Math.random() >= p.hitFrac) return 0;
      return Math.random() < p.critFrac ? 2 : 1;
    }

    while (events.length) {
      events.sort(function (a, b) { return a.time - b.time; });
      var ev = events.shift();
      var t = ev.time;
      if (t > p.fightLen) continue;
      if (ev.type === 'swing') {
        var m = roll(t);
        if (m) dmg += (p.wpnDmg + p.AP / 14) * m;
        swings++;
        events.push({ time: t + p.weaponSpeed, type: 'swing' });
      } else { // decision point: can we cast something?
        if (t < gcdReady) { events.push({ time: gcdReady, type: 'decision' }); continue; }
        if (t >= btReady) {
          var mb = roll(t);
          if (mb) dmg += (BT_AP_COEFF * p.AP + BT_SP_COEFF * p.SP) * mb;
          btReady = t + BT_CD; gcdReady = t + GCD; btCasts++;
          events.push({ time: gcdReady, type: 'decision' });
        } else if (t >= wwReady) {
          var mw = roll(t);
          if (mw) dmg += (p.wpnDmg + p.AP / 14) * mw;
          wwReady = t + WW_CD; gcdReady = t + GCD; wwCasts++;
          events.push({ time: gcdReady, type: 'decision' });
        } else {
          events.push({ time: Math.min(btReady, wwReady), type: 'decision' });
        }
      }
    }
    return { dmg: dmg, btCasts: btCasts, wwCasts: wwCasts, swings: swings };
  }

  function run() {
    var p = {
      AP: num('tcAP'), SP: num('tcSP'),
      hitFrac: Math.max(0, num('tcHit')) / 100,
      critFrac: Math.max(0, num('tcCrit')) / 100,
      wpnDmg: num('tcWpnDmg'), weaponSpeed: Math.max(0.1, num('tcWpnSpeed')),
      fightLen: Math.max(10, parseFloat(fightLenInput.value) || 300),
    };
    var iterations = Math.max(1, Math.min(20000, parseInt(iterInput.value, 10) || 2000));
    var dpsSamples = [];
    var totalBt = 0, totalWw = 0, totalSwings = 0;
    for (var i = 0; i < iterations; i++) {
      var r = simulateOnce(p);
      dpsSamples.push(r.dmg / p.fightLen);
      totalBt += r.btCasts; totalWw += r.wwCasts; totalSwings += r.swings;
    }
    var mean = dpsSamples.reduce(function (a, b) { return a + b; }, 0) / iterations;
    var variance = dpsSamples.reduce(function (a, b) { return a + (b - mean) * (b - mean); }, 0) / iterations;
    var stderr = Math.sqrt(variance / iterations);

    function fmt(n) { return (Math.round(n * 100) / 100).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }

    document.getElementById('simDps').textContent = fmt(mean);
    document.getElementById('simCi').textContent = '± ' + fmt(1.96 * stderr) + ' (95%)';
    document.getElementById('simCasts').textContent =
      (totalBt / iterations).toFixed(1) + ' / ' + (totalWw / iterations).toFixed(1) + ' / ' + (totalSwings / iterations).toFixed(1);
    document.getElementById('simResults').hidden = false;
  }

  runBtn.addEventListener('click', run);
})();
