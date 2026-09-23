(function () {
  'use strict';
  // Minimal event-driven combat simulator (Fury Warrior, single target): Bloodthirst, Whirlwind,
  // Heroic Strike and Death Wish on a real Rage economy, real dual-wielding, real Fury-tree procs
  // (Flurry, Unbridled Wrath, Raging Blows) plus generic user-supplied weapon-proc/bleed slots.
  // Modeled on SimulationCraft's own architecture (event queue, priority check at every free moment,
  // per-swing hit/crit RNG, averaged over many iterations) but written from scratch for Forever's
  // real, much smaller Fury kit -- see /wow-forever/theorycraft/ for the exact values and sources.
  // This is NOT every Warrior spell: it only covers what a sustained single-target Fury DPS rotation
  // actually uses. Left out on purpose: Execute (only usable below 20% target health -- no execute
  // phase modeled), Overpower (requires the target to have just dodged -- no target defenses
  // modeled), Rend/Cleave (Arms/AoE tools, not part of a single-target Fury rotation), Recklessness
  // and Berserker Rage (utility/defensive, no sustained DPS contribution), Enrage (procs off taking
  // damage -- this simulator has no incoming-damage model), and Deep Wounds (a real bleed talent,
  // but from the Arms tree, not Fury).
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
  // Flurry (real Fury talent, Forever's own beta client data, 5 ranks): +5%/rank melee attack speed for
  // the next 3 swings after ANY melee critical strike (auto-attack or special ability -- confirmed on
  // WoW Classic's own Wowhead tooltip: "after dealing a melee critical strike", no restriction stated).
  // The speed bonus itself only ever speeds up normal swings (special abilities run on fixed cooldowns,
  // unaffected by attack speed); charges are consumed by a swing regardless of hit/miss, and a fresh
  // crit always resets the count back to a full 3, not additive. A charge window not fully spent within
  // 15 seconds expires. Simplification: the bonus applies starting from the NEXT scheduled swing after
  // the triggering crit, not by retroactively compressing a swing timer already in flight.
  var FLURRY_BONUS_PER_RANK = 0.05, FLURRY_CHARGES = 3, FLURRY_EXPIRE_SEC = 15;
  // Unbridled Wrath (real Fury talent, Forever's own beta client data, 5 ranks): +12%/rank chance to
  // generate 1 additional Rage (2 for two-handed weapons -- not modeled, this tool is dual-wield-only)
  // whenever you deal melee damage with a weapon.
  var UNBRIDLED_WRATH_CHANCE_PER_RANK = 0.12;
  // Death Wish (real Fury talent, Forever's own beta client data + its own Wowhead spell tooltip,
  // spell=12328): 10 Rage, instant, 3-minute cooldown, uses the GCD, +20% Physical damage for 30
  // seconds. Treated as top rotation priority (used the instant it's available) -- standard
  // "damage cooldown, use on cooldown" assumption for a sustained single-target fight, same spirit as
  // Bloodthirst/Whirlwind's "as soon as available" assumption already used elsewhere on this page.
  // Applied to every damage source in this simulator, since everything it currently models (weapon
  // swings, Bloodthirst, Whirlwind, Heroic Strike, and the generic proc/bleed slots) is Physical school.
  var DW_RAGE_COST = 10, DW_CD = 180, DW_DURATION = 30, DW_MULT = 1.20;
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

  function bool(id) {
    var el = document.getElementById(id);
    return !!(el && el.checked);
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
    var flurryBonus = FLURRY_BONUS_PER_RANK * Math.max(0, Math.min(5, p.flurryRank));
    var unbridledChance = UNBRIDLED_WRATH_CHANCE_PER_RANK * Math.max(0, Math.min(5, p.unbridledRank));

    var events = [{ time: p.weaponSpeed, type: 'mh_swing' }, { time: 0, type: 'decision' }];
    var nextMhAt = p.weaponSpeed, nextOhAt = Infinity;
    if (dualWield) { events.push({ time: p.ohWeaponSpeed, type: 'oh_swing' }); nextOhAt = p.ohWeaponSpeed; }
    var btReady = 0, wwReady = 0, dwReady = 0, gcdReady = 0;
    var rage = 0, hsQueued = false, dwActiveUntil = -1;
    var flurryCharges = 0, flurryExpireAt = -1;
    var bleedEndsAt = -1, bleedActive = false;
    var dmg = 0, btCasts = 0, wwCasts = 0, hsCasts = 0, dwCasts = 0, swings = 0;

    // Applies Death Wish's +20% Physical damage buff (if active at time t) to a damage instance.
    function addDmg(t, amount) { dmg += amount * (t <= dwActiveUntil ? DW_MULT : 1); }

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

    function onCrit(t) {
      if (flurryBonus > 0) { flurryCharges = FLURRY_CHARGES; flurryExpireAt = t + FLURRY_EXPIRE_SEC; }
    }

    // Consumes one Flurry charge (if any is active) and returns the speed multiplier to apply when
    // scheduling this hand's NEXT swing.
    function consumeFlurrySpeedMult(t) {
      if (flurryCharges > 0 && t <= flurryExpireAt) { flurryCharges--; return 1 / (1 + flurryBonus); }
      return 1;
    }

    function onMeleeWeaponDamage() {
      if (unbridledChance > 0 && Math.random() < unbridledChance) rage = Math.min(RAGE_CAP, rage + 1);
    }

    // Generic weapon proc ("chance on hit": a flat bonus hit, no separate crit roll) and generic bleed
    // (a refreshable, non-stacking DoT): both use real-world values the user enters from their own gear,
    // since we don't have per-item proc data catalogued for Forever yet. Fires on any landed weapon
    // damage, main or off hand, Bloodthirst or Whirlwind alike -- a simplification disclosed on the page.
    function onLandedWeaponHit(t) {
      if (p.procChance > 0 && Math.random() < p.procChance) addDmg(t, p.procDmg);
      if (p.bleedChance > 0 && Math.random() < p.bleedChance) {
        bleedEndsAt = t + p.bleedDuration;
        if (!bleedActive) { bleedActive = true; events.push({ time: t + p.bleedInterval, type: 'bleed_tick' }); }
      }
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
          addDmg(t, swingDmg);
          onMeleeWeaponDamage();
          onLandedWeaponHit(t);
        }
        if (empowered) {
          // Simplification: full Rage cost is charged whether the swing hits or misses (the real
          // "Discount Power On Miss" partial refund isn't modeled).
          hsQueued = false;
          rage = Math.max(0, rage - HS_RAGE_COST);
          hsCasts++;
        }
        if (m) rage = Math.min(RAGE_CAP, rage + gainRage(swingDmg, m === 2, false));
        var mhSpeedMult = consumeFlurrySpeedMult(t);
        if (m === 2) onCrit(t);
        checkHsQueue();
        swings++;
        nextMhAt = t + p.weaponSpeed * mhSpeedMult;
        events.push({ time: nextMhAt, type: 'mh_swing' });
      } else if (ev.type === 'oh_swing') {
        var mo = roll(ohWhiteHit);
        var ohDmg = 0;
        if (mo) {
          ohDmg = (p.ohWpnDmg + p.AP / 14) * ohDmgMult * mo;
          addDmg(t, ohDmg);
          rage = Math.min(RAGE_CAP, rage + gainRage(ohDmg, mo === 2, true));
          onMeleeWeaponDamage();
          onLandedWeaponHit(t);
        }
        var ohSpeedMult = consumeFlurrySpeedMult(t);
        if (mo === 2) onCrit(t);
        checkHsQueue();
        swings++;
        nextOhAt = t + p.ohWeaponSpeed * ohSpeedMult;
        events.push({ time: nextOhAt, type: 'oh_swing' });
      } else if (ev.type === 'bleed_tick') {
        if (t <= bleedEndsAt) {
          addDmg(t, p.bleedTick);
          events.push({ time: t + p.bleedInterval, type: 'bleed_tick' });
        } else {
          bleedActive = false;
        }
      } else { // decision point: can we cast something?
        if (t < gcdReady) { events.push({ time: gcdReady, type: 'decision' }); continue; }
        if (p.useDeathWish && rage >= DW_RAGE_COST && t >= dwReady) {
          // Top rotation priority: a damage cooldown is used the instant it's up.
          rage -= DW_RAGE_COST; dwReady = t + DW_CD; gcdReady = t + GCD; dwActiveUntil = t + DW_DURATION; dwCasts++;
          events.push({ time: gcdReady, type: 'decision' });
        } else if (rage >= BT_RAGE_COST && t >= btReady) {
          var mb = roll(p.hitFrac);
          if (mb) { addDmg(t, (BT_AP_COEFF * p.AP + BT_SP_COEFF * p.SP) * mb); onMeleeWeaponDamage(); if (mb === 2) onCrit(t); }
          rage -= BT_RAGE_COST; btReady = t + BT_CD; gcdReady = t + GCD; btCasts++;
          events.push({ time: gcdReady, type: 'decision' });
        } else if (rage >= WW_RAGE_COST && t >= wwReady) {
          // Whirlwind hits with the off-hand too only with the Raging Blows talent (real WoW: Forever
          // talent tree data -- NOT automatic from dual-wielding alone, unlike generic classic WoW).
          var mw = roll(p.hitFrac);
          if (mw) { addDmg(t, (p.wpnDmg + p.AP / 14) * mw); onMeleeWeaponDamage(); onLandedWeaponHit(t); if (mw === 2) onCrit(t); }
          if (dualWield && p.ragingBlows) {
            var mwOh = roll(p.hitFrac);
            if (mwOh) { addDmg(t, (p.ohWpnDmg + p.AP / 14) * ohDmgMult * mwOh); onMeleeWeaponDamage(); onLandedWeaponHit(t); if (mwOh === 2) onCrit(t); }
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
    return { dmg: dmg, btCasts: btCasts, wwCasts: wwCasts, hsCasts: hsCasts, dwCasts: dwCasts, swings: swings };
  }

  function run() {
    var p = {
      AP: num('tcAP'), SP: num('tcSP'),
      hitFrac: Math.max(0, num('tcHit')) / 100,
      critFrac: Math.max(0, num('tcCrit')) / 100,
      wpnDmg: num('tcWpnDmg'), weaponSpeed: Math.max(0.1, num('tcWpnSpeed')),
      ohWpnDmg: Math.max(0, num('tcOhDmg')), ohWeaponSpeed: Math.max(0.1, num('tcOhSpeed')),
      dwsRank: num('tcDws'), flurryRank: num('tcFlurry'), unbridledRank: num('tcUnbridled'),
      ragingBlows: bool('tcRagingBlows'), useDeathWish: bool('tcDeathWish'),
      procChance: Math.max(0, num('tcProcChance')) / 100, procDmg: Math.max(0, num('tcProcDmg')),
      bleedChance: Math.max(0, num('tcBleedChance')) / 100, bleedTick: Math.max(0, num('tcBleedTick')),
      bleedInterval: Math.max(0.5, num('tcBleedInterval') || 3), bleedDuration: Math.max(0, num('tcBleedDuration')),
      fightLen: Math.max(10, parseFloat(fightLenInput.value) || 300),
    };
    var iterations = Math.max(1, Math.min(20000, parseInt(iterInput.value, 10) || 2000));
    var dpsSamples = [];
    var totalBt = 0, totalWw = 0, totalHs = 0, totalDw = 0, totalSwings = 0;
    for (var i = 0; i < iterations; i++) {
      var r = simulateOnce(p);
      dpsSamples.push(r.dmg / p.fightLen);
      totalBt += r.btCasts; totalWw += r.wwCasts; totalHs += r.hsCasts; totalDw += r.dwCasts; totalSwings += r.swings;
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
    var dwUptimePct = 100 * Math.min(1, (totalDw * DW_DURATION) / (iterations * p.fightLen));
    var dwRow = document.getElementById('simDwUptime');
    if (dwRow) dwRow.textContent = (totalDw / iterations).toFixed(2) + ' (' + fmt(dwUptimePct) + '%)';
    document.getElementById('simResults').hidden = false;
  }

  runBtn.addEventListener('click', run);
})();
