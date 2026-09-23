(function () {
  'use strict';
  // Minimal event-driven combat simulator (Fury Warrior, single target): Bloodthirst, Whirlwind and
  // Heroic Strike on a real Rage economy, now with real dual-wielding (independent main-hand and
  // off-hand swing timers) -- still no procs, no DoTs. Modeled on SimulationCraft's own architecture
  // (event queue, priority check at every free moment, per-swing hit/crit RNG, averaged over many
  // iterations) but written from scratch for Forever's real, much smaller Fury kit -- see
  // /wow-forever/theorycraft/ for the spell/rage/dual-wield values and their sources.
  var GCD = 1.5, BT_CD = 6, WW_CD = 10;
  var BT_AP_COEFF = 0.35, BT_SP_COEFF = 1.00;
  // Rage costs and Heroic Strike's flat bonus damage: real values read from WoW: Forever's own
  // Wowhead spell tooltips (max rank, level 60) -- spell=23894, spell=1680, spell=25286. Heroic Strike
  // requires the main-hand weapon (its own tooltip flag), so it only ever empowers a main-hand swing.
  var BT_RAGE_COST = 30, WW_RAGE_COST = 25, HS_RAGE_COST = 15, HS_BONUS_DMG = 157;
  var RAGE_CAP = 100;
  // Rage generation: the real WoW classic-era formula (not Forever-specific -- rage generation isn't
  // shown in any tooltip, unlike Crit/Hit rating -- but every other confirmed Forever Warrior mechanic
  // points to a classic-style kit, so this is the best-sourced approximation available, not an invented
  // number). Special attacks (Bloodthirst, Whirlwind) generate no Rage; only landed weapon swings do:
  // R = 15*damage / (4*c) + f*weaponSpeed/2, capped at 15*damage/c, c = rage conversion value at level 60.
  var RAGE_CONVERSION_L60 = 230.6;
  var HIT_FACTOR_MH_NORMAL = 3.5, HIT_FACTOR_MH_CRIT = 7.0;
  var HIT_FACTOR_OH_NORMAL = 1.75, HIT_FACTOR_OH_CRIT = 3.5;
  // Dual-wielding (real WoW classic mechanics): the off-hand weapon deals 50% of its damage, and
  // dual-wielding adds a flat 19% miss-chance penalty to BOTH weapons' normal swings (never to special
  // attacks like Bloodthirst/Whirlwind/Heroic Strike). Dual Wield Specialization (Fury talent, 5 real
  // ranks in Forever's own beta client data) reduces that per rank: +5% off-hand damage, +20% off-hand
  // Rage generation, +2% off-hand hit chance -- applied additively on top of the 50% base.
  var OH_DAMAGE_BASE = 0.5;
  var DUAL_WIELD_MISS_PENALTY = 0.19;
  var DWS_OH_DMG_PER_RANK = 0.05, DWS_OH_RAGE_PER_RANK = 0.20, DWS_OH_HIT_PER_RANK = 0.02;
  // Priority heuristic (a rotation choice, not a game rule): only dump Rage into Heroic Strike once
  // above this threshold, so it never delays Bloodthirst or Whirlwind.
  var HS_QUEUE_THRESHOLD = 50;

  var runBtn = document.getElementById('simRun');
  var fightLenInput = document.getElementById('simFightLen');
  var iterInput = document.getElementById('simIterations');
  if (!runBtn) return;

  function num(id) {
    var el = document.getElementById(id);
    var v = parseFloat(el && el.value);
    return isFinite(v) ? v : 0;
  }

  // One simulated fight: returns total damage dealt over fightLen seconds plus cast counts.
  function simulateOnce(p) {
    var dualWield = p.ohWpnDmg > 0;
    var dwsRank = Math.max(0, Math.min(5, p.dwsRank));
    var ohDmgMult = OH_DAMAGE_BASE + DWS_OH_DMG_PER_RANK * dwsRank;
    var ohRageMult = 1 + DWS_OH_RAGE_PER_RANK * dwsRank;
    var mhMissPenalty = dualWield ? DUAL_WIELD_MISS_PENALTY : 0;
    var ohMissPenalty = Math.max(0, DUAL_WIELD_MISS_PENALTY - DWS_OH_HIT_PER_RANK * dwsRank);
    var mhWhiteHit = Math.max(0, p.hitFrac - mhMissPenalty);
    var ohWhiteHit = Math.max(0, p.hitFrac - ohMissPenalty);

    var events = [{ time: p.weaponSpeed, type: 'mh_swing' }, { time: 0, type: 'decision' }];
    var nextMhAt = p.weaponSpeed, nextOhAt = Infinity;
    if (dualWield) { events.push({ time: p.ohWeaponSpeed, type: 'oh_swing' }); nextOhAt = p.ohWeaponSpeed; }
    var btReady = 0, wwReady = 0, gcdReady = 0;
    var rage = 0, hsQueued = false;
    var dmg = 0, btCasts = 0, wwCasts = 0, hsCasts = 0, swings = 0;

    function roll(hitFrac) {
      // 0 = miss, 1 = normal hit, 2 = critical hit (200% damage, standard WoW mechanic)
      if (Math.random() >= hitFrac) return 0;
      return Math.random() < p.critFrac ? 2 : 1;
    }

    function gainRage(dealt, isCrit, isOffHand) {
      var f = isOffHand ? (isCrit ? HIT_FACTOR_OH_CRIT : HIT_FACTOR_OH_NORMAL) : (isCrit ? HIT_FACTOR_MH_CRIT : HIT_FACTOR_MH_NORMAL);
      var speed = isOffHand ? p.ohWeaponSpeed : p.weaponSpeed;
      var raw = (15 * dealt) / (4 * RAGE_CONVERSION_L60) + (f * speed) / 2;
      var cap = (15 * dealt) / RAGE_CONVERSION_L60;
      var gained = Math.min(raw, cap);
      return isOffHand ? gained * ohRageMult : gained;
    }

    function checkHsQueue() {
      if (!hsQueued && rage >= HS_QUEUE_THRESHOLD) hsQueued = true;
    }

    while (events.length) {
      events.sort(function (a, b) { return a.time - b.time; });
      var ev = events.shift();
      var t = ev.time;
      if (t > p.fightLen) continue;
      if (ev.type === 'mh_swing') {
        var empowered = hsQueued; // Heroic Strike requires the main hand: it only converts an MH swing
        var m = roll(mhWhiteHit);
        var swingDmg = 0;
        if (m) {
          swingDmg = (p.wpnDmg + p.AP / 14 + (empowered ? HS_BONUS_DMG : 0)) * m;
          dmg += swingDmg;
        }
        if (empowered) {
          // Simplification: full Rage cost is charged whether the swing hits or misses (the real
          // "Discount Power On Miss" partial refund isn't modeled).
          hsQueued = false;
          rage = Math.max(0, rage - HS_RAGE_COST);
          hsCasts++;
        }
        if (m) rage = Math.min(RAGE_CAP, rage + gainRage(swingDmg, m === 2, false));
        checkHsQueue();
        swings++;
        nextMhAt = t + p.weaponSpeed;
        events.push({ time: nextMhAt, type: 'mh_swing' });
      } else if (ev.type === 'oh_swing') {
        var mo = roll(ohWhiteHit);
        var ohDmg = 0;
        if (mo) {
          ohDmg = (p.ohWpnDmg + p.AP / 14) * ohDmgMult * mo;
          dmg += ohDmg;
          rage = Math.min(RAGE_CAP, rage + gainRage(ohDmg, mo === 2, true));
        }
        checkHsQueue();
        swings++;
        nextOhAt = t + p.ohWeaponSpeed;
        events.push({ time: nextOhAt, type: 'oh_swing' });
      } else { // decision point: can we cast something?
        if (t < gcdReady) { events.push({ time: gcdReady, type: 'decision' }); continue; }
        if (rage >= BT_RAGE_COST && t >= btReady) {
          var mb = roll(p.hitFrac);
          if (mb) dmg += (BT_AP_COEFF * p.AP + BT_SP_COEFF * p.SP) * mb;
          rage -= BT_RAGE_COST; btReady = t + BT_CD; gcdReady = t + GCD; btCasts++;
          events.push({ time: gcdReady, type: 'decision' });
        } else if (rage >= WW_RAGE_COST && t >= wwReady) {
          // Whirlwind hits with both weapons when dual-wielding (real classic mechanic), each its own
          // roll; neither contributes Rage (special attacks generate none).
          var mw = roll(p.hitFrac);
          if (mw) dmg += (p.wpnDmg + p.AP / 14) * mw;
          if (dualWield) {
            var mwOh = roll(p.hitFrac);
            if (mwOh) dmg += (p.ohWpnDmg + p.AP / 14) * ohDmgMult * mwOh;
          }
          rage -= WW_RAGE_COST; wwReady = t + WW_CD; gcdReady = t + GCD; wwCasts++;
          events.push({ time: gcdReady, type: 'decision' });
        } else {
          // On cooldown, or Rage-starved: retry once a cooldown is up, but never schedule a retry
          // in the past -- when Rage-starved with both off cooldown, wait for the next swing instead
          // (that's the only thing that can generate more Rage), which keeps simulated time moving.
          var retry = Math.min(btReady, wwReady);
          if (retry <= t) retry = Math.min(nextMhAt, nextOhAt) > t ? Math.min(nextMhAt, nextOhAt) : t + 0.01;
          events.push({ time: retry, type: 'decision' });
        }
        checkHsQueue();
      }
    }
    return { dmg: dmg, btCasts: btCasts, wwCasts: wwCasts, hsCasts: hsCasts, swings: swings };
  }

  function run() {
    var p = {
      AP: num('tcAP'), SP: num('tcSP'),
      hitFrac: Math.max(0, num('tcHit')) / 100,
      critFrac: Math.max(0, num('tcCrit')) / 100,
      wpnDmg: num('tcWpnDmg'), weaponSpeed: Math.max(0.1, num('tcWpnSpeed')),
      ohWpnDmg: Math.max(0, num('tcOhDmg')), ohWeaponSpeed: Math.max(0.1, num('tcOhSpeed')),
      dwsRank: num('tcDws'),
      fightLen: Math.max(10, parseFloat(fightLenInput.value) || 300),
    };
    var iterations = Math.max(1, Math.min(20000, parseInt(iterInput.value, 10) || 2000));
    var dpsSamples = [];
    var totalBt = 0, totalWw = 0, totalHs = 0, totalSwings = 0;
    for (var i = 0; i < iterations; i++) {
      var r = simulateOnce(p);
      dpsSamples.push(r.dmg / p.fightLen);
      totalBt += r.btCasts; totalWw += r.wwCasts; totalHs += r.hsCasts; totalSwings += r.swings;
    }
    var mean = dpsSamples.reduce(function (a, b) { return a + b; }, 0) / iterations;
    var variance = dpsSamples.reduce(function (a, b) { return a + (b - mean) * (b - mean); }, 0) / iterations;
    var stderr = Math.sqrt(variance / iterations);

    function fmt(n) { return (Math.round(n * 100) / 100).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }

    document.getElementById('simDps').textContent = fmt(mean);
    document.getElementById('simCi').textContent = '± ' + fmt(1.96 * stderr) + ' (95%)';
    document.getElementById('simCasts').textContent =
      (totalBt / iterations).toFixed(1) + ' / ' + (totalWw / iterations).toFixed(1) + ' / ' +
      (totalHs / iterations).toFixed(1) + ' / ' + (totalSwings / iterations).toFixed(1);
    document.getElementById('simResults').hidden = false;
  }

  runBtn.addEventListener('click', run);
})();
