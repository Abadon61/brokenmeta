(function () {
  'use strict';
  // Minimal event-driven combat simulator for a REAL level-20 Fury Warrior (WoW: Forever's beta
  // cap), not the level-60 kit modeled by the earlier, now-unlinked wow-simulator.js. Bloodthirst
  // (level 60), Whirlwind (level 36) and Heroic Strike (max rank, level 60) are all removed since
  // none is trainable at level 20 -- see data/wow_spells/warrior.json for the real, sourced kit
  // this engine is built from. Modeled instead: Rend (a maintained bleed), Overpower (procs off the
  // target dodging a normal swing) and Bloodrage (a Rage-generation cooldown). Reuses the same
  // architecture as the removed level-60 engine (event queue, per-swing hit/crit RNG, dual-wielding,
  // per-source damage breakdown) but re-derived for what's actually usable at this level.
  var GCD = 1.5;
  // Rend (rank 3, exactly the level-20 cap): 10 Rage, no cooldown (just the GCD), 45 total damage
  // over 15s in 5 ticks of 9, and its own tooltip explicitly flags "Periodic Can Crit" -- a real
  // mechanic, not a generic bleed assumption. Refreshing it (recasting before it expires) replaces
  // the remaining duration outright; it never stacks (this project's standing non-stacking rule).
  var REND_RAGE_COST = 10, REND_DURATION = 15, REND_TICK_INTERVAL = 3, REND_TICK_DMG = 9;
  // Overpower (real WoW classic mechanic): 5 Rage, 5-second cooldown, 100% weapon damage + 5 flat,
  // usable only within a 5-second window after the CURRENT target dodges one of the player's normal
  // weapon swings (Vanilla WoW Wiki -- Overpower). Cannot itself be dodged, parried or blocked (its
  // own Wowhead tooltip), but can still miss.
  var OVERPOWER_RAGE_COST = 5, OVERPOWER_CD = 5, OVERPOWER_FLAT = 5, OVERPOWER_WINDOW = 5;
  // Bloodrage (WoW: Forever's own spell tooltip, spell=2687): 60-second cooldown, no GCD, +10 Rage
  // immediately plus 10 more over 10 seconds, for a real cost of 20% of max Health -- not modeled
  // here (no incoming damage/HP tracked), so enabling it assumes that cost is always affordable.
  var BLOODRAGE_CD = 60, BLOODRAGE_IMMEDIATE = 10, BLOODRAGE_OVER_TIME = 10, BLOODRAGE_OVER_TIME_SEC = 10;
  var RAGE_CAP_BASE = 100;
  var BOUNDLESS_RAGE_PER_RANK = 10;
  // Rage generation: the real classic-WoW formula, R = 15*damage/(4*c) + f*weaponSpeed/2, capped at
  // 15*damage/c. "c" (the Rage conversion value) depends on character level -- a community-derived
  // formula, c(level) = 0.0091107836*level^2 + 3.225598133*level + 4.2652911, that lands exactly on
  // the known level-60 value (230.6) used by this project's earlier level-60 engine. This tool uses
  // c(20) here, not the level-60 constant: at level 20 the same damage generates proportionally more
  // Rage than it would at 60.
  function rageConversionValue(level) { return 0.0091107836 * level * level + 3.225598133 * level + 4.2652911; }
  var RAGE_CONVERSION_L20 = rageConversionValue(20);
  var HIT_FACTOR_MH_NORMAL = 3.5, HIT_FACTOR_MH_CRIT = 7.0;
  var HIT_FACTOR_OH_NORMAL = 1.75, HIT_FACTOR_OH_CRIT = 3.5;
  // Dual-wielding (real WoW classic mechanics, still available exactly at level 20 per the glossary's
  // own notes): the off-hand weapon deals 50% of its damage, and dual-wielding adds a flat 19%
  // miss-chance penalty to both weapons' normal swings (never to special attacks like Rend/Overpower).
  // Dual Wield Specialization (real Fury talent, 5 ranks) reduces that per rank.
  var OH_DAMAGE_BASE = 0.5;
  var DUAL_WIELD_MISS_PENALTY = 0.19;
  var DWS_OH_DMG_PER_RANK = 0.05, DWS_OH_RAGE_PER_RANK = 0.20, DWS_OH_HIT_PER_RANK = 0.02;
  // Flurry (real Fury talent, 5 ranks): +5%/rank melee attack speed for the next 3 swings after ANY
  // melee critical strike. Disclosed simplification: a critical Rend TICK doesn't trigger this here,
  // since a DoT tick generally isn't treated as a "melee critical strike" under classic-era mechanics
  // (unlike a Rend or Overpower CAST landing a crit, which does trigger it).
  var FLURRY_BONUS_PER_RANK = 0.05, FLURRY_CHARGES = 3, FLURRY_EXPIRE_SEC = 15;
  // Unbridled Wrath (real Fury talent, 5 ranks): +12%/rank chance to generate 1 extra Rage on a
  // landed NORMAL weapon swing (not on Rend ticks, which aren't a "weapon swing").
  var UNBRIDLED_WRATH_CHANCE_PER_RANK = 0.12;
  // Cruelty (5 ranks, +1%/rank crit) and Precision (3 ranks, +1%/rank hit): both real Fury talents,
  // applied as flat additions on top of the player's own entered Crit/Hit stats.
  var CRUELTY_PER_RANK = 0.01, PRECISION_PER_RANK = 0.01;
  // Attack table against a same-level target (not the level-63 raid boss the earlier level-60 engine
  // assumed): base Dodge 5% and base Glancing Blow 10%/70% damage, i.e. the classic-WoW values at
  // zero attacker-skill/target-defense differential -- a more honest default for a level-20 fight
  // than reusing an end-game boss's defense value. Neither applies to Rend or Overpower ("yellow"
  // attacks), consistent with how Bloodthirst/Whirlwind/Heroic Strike were already treated before.
  var DODGE_CHANCE = 0.05, GLANCE_CHANCE = 0.10, GLANCE_DAMAGE_MULT = 0.70;

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
    var hitFrac = Math.min(1, p.hitFrac + PRECISION_PER_RANK * Math.max(0, Math.min(3, p.precisionRank)));
    var critFrac = Math.min(1, p.critFrac + CRUELTY_PER_RANK * Math.max(0, Math.min(5, p.crueltyRank)));
    var mhWhiteHit = Math.max(0, hitFrac - mhMissPenalty);
    var ohWhiteHit = Math.max(0, hitFrac - ohMissPenalty);
    var flurryBonus = FLURRY_BONUS_PER_RANK * Math.max(0, Math.min(5, p.flurryRank));
    var unbridledChance = UNBRIDLED_WRATH_CHANCE_PER_RANK * Math.max(0, Math.min(5, p.unbridledRank));
    var rageCap = RAGE_CAP_BASE + BOUNDLESS_RAGE_PER_RANK * Math.max(0, Math.min(3, p.boundlessRank));

    var events = [{ time: p.weaponSpeed, type: 'mh_swing' }, { time: 0, type: 'decision' }];
    var nextMhAt = p.weaponSpeed, nextOhAt = Infinity;
    if (dualWield) { events.push({ time: p.ohWeaponSpeed, type: 'oh_swing' }); nextOhAt = p.ohWeaponSpeed; }
    var opReady = 0, gcdReady = 0, bloodrageReady = 0;
    var rage = 0, opWindowUntil = -1;
    var flurryCharges = 0, flurryExpireAt = -1;
    var rendActive = false, rendEndsAt = -1;
    var dmg = 0, rendCasts = 0, opCasts = 0, bloodrageCasts = 0, swings = 0, rendTicks = 0;
    var dmgBy = { white: 0, rend: 0, op: 0, proc: 0, bleed: 0 };
    var bleedEndsAt = -1, bleedActive = false;

    function addDmg(t, amount, category) { dmg += amount; dmgBy[category] += amount; }

    // Returns a damage multiplier: 0 = miss, -1 = dodge (white swings only), GLANCE_DAMAGE_MULT =
    // glancing blow (white swings only), 1 = normal hit, 2 = critical hit (200% damage).
    function roll(hf, allowGlance, allowDodge) {
      if (Math.random() >= hf) return 0;
      if (allowDodge && Math.random() < DODGE_CHANCE) return -1;
      if (allowGlance && Math.random() < GLANCE_CHANCE) return GLANCE_DAMAGE_MULT;
      return Math.random() < critFrac ? 2 : 1;
    }

    function gainRage(dealt, isCrit, isOffHand) {
      var f = isOffHand ? (isCrit ? HIT_FACTOR_OH_CRIT : HIT_FACTOR_OH_NORMAL) : (isCrit ? HIT_FACTOR_MH_CRIT : HIT_FACTOR_MH_NORMAL);
      var speed = isOffHand ? p.ohWeaponSpeed : p.weaponSpeed;
      var raw = (15 * dealt) / (4 * RAGE_CONVERSION_L20) + (f * speed) / 2;
      var cap = (15 * dealt) / RAGE_CONVERSION_L20;
      var gained = Math.min(raw, cap);
      return isOffHand ? gained * ohRageMult : gained;
    }

    function onCrit(t) {
      if (flurryBonus > 0) { flurryCharges = FLURRY_CHARGES; flurryExpireAt = t + FLURRY_EXPIRE_SEC; }
    }

    function consumeFlurrySpeedMult(t) {
      if (flurryCharges > 0 && t <= flurryExpireAt) { flurryCharges--; return 1 / (1 + flurryBonus); }
      return 1;
    }

    function onMeleeWeaponSwing() {
      if (unbridledChance > 0 && Math.random() < unbridledChance) rage = Math.min(rageCap, rage + 1);
    }

    // Generic weapon proc/bleed slots (user-supplied real gear values) -- kept from the earlier
    // engine's design: fires on any landed weapon-based hit (white swings, Rend/Overpower casts),
    // never on a Rend DoT tick.
    function onLandedWeaponHit(t) {
      if (p.procChance > 0 && Math.random() < p.procChance) addDmg(t, p.procDmg, 'proc');
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
        var m = roll(mhWhiteHit, true, true);
        if (m > 0) {
          var swingDmg = (p.wpnDmg + p.AP / 14) * m;
          addDmg(t, swingDmg, 'white');
          onMeleeWeaponSwing();
          onLandedWeaponHit(t);
          rage = Math.min(rageCap, rage + gainRage(swingDmg, m === 2, false));
          if (m === 2) onCrit(t);
        } else if (m === -1) {
          opWindowUntil = t + OVERPOWER_WINDOW;
        }
        var mhSpeedMult = consumeFlurrySpeedMult(t);
        swings++;
        nextMhAt = t + p.weaponSpeed * mhSpeedMult;
        events.push({ time: nextMhAt, type: 'mh_swing' });
      } else if (ev.type === 'oh_swing') {
        var mo = roll(ohWhiteHit, true, true);
        if (mo > 0) {
          var ohDmg = (p.ohWpnDmg + p.AP / 14) * ohDmgMult * mo;
          addDmg(t, ohDmg, 'white');
          onMeleeWeaponSwing();
          onLandedWeaponHit(t);
          rage = Math.min(rageCap, rage + gainRage(ohDmg, mo === 2, true));
          if (mo === 2) onCrit(t);
        } else if (mo === -1) {
          opWindowUntil = t + OVERPOWER_WINDOW;
        }
        var ohSpeedMult = consumeFlurrySpeedMult(t);
        swings++;
        nextOhAt = t + p.ohWeaponSpeed * ohSpeedMult;
        events.push({ time: nextOhAt, type: 'oh_swing' });
      } else if (ev.type === 'rend_tick') {
        if (t <= rendEndsAt) {
          var tickMult = Math.random() < critFrac ? 2 : 1;
          addDmg(t, REND_TICK_DMG * tickMult, 'rend');
          rendTicks++;
          events.push({ time: t + REND_TICK_INTERVAL, type: 'rend_tick' });
        } else {
          rendActive = false;
        }
      } else if (ev.type === 'bleed_tick') {
        if (t <= bleedEndsAt) {
          addDmg(t, p.bleedTick, 'bleed');
          events.push({ time: t + p.bleedInterval, type: 'bleed_tick' });
        } else {
          bleedActive = false;
        }
      } else if (ev.type === 'bloodrage_tick') {
        rage = Math.min(rageCap, rage + BLOODRAGE_OVER_TIME);
      } else { // decision point: can we cast something?
        if (p.useBloodrage && t >= bloodrageReady) {
          rage = Math.min(rageCap, rage + BLOODRAGE_IMMEDIATE);
          bloodrageReady = t + BLOODRAGE_CD;
          bloodrageCasts++;
          events.push({ time: t + BLOODRAGE_OVER_TIME_SEC, type: 'bloodrage_tick' });
        }
        if (t < gcdReady) { events.push({ time: gcdReady, type: 'decision' }); continue; }
        if (rage >= OVERPOWER_RAGE_COST && t >= opReady && t <= opWindowUntil) {
          var mop = roll(hitFrac, false, false);
          if (mop > 0) { addDmg(t, ((p.wpnDmg + p.AP / 14) + OVERPOWER_FLAT) * mop, 'op'); onMeleeWeaponSwing(); onLandedWeaponHit(t); if (mop === 2) onCrit(t); }
          rage -= OVERPOWER_RAGE_COST; opReady = t + OVERPOWER_CD; gcdReady = t + GCD; opCasts++;
          events.push({ time: gcdReady, type: 'decision' });
        } else if (rage >= REND_RAGE_COST && (!rendActive || rendEndsAt - t <= GCD)) {
          var mr = roll(hitFrac, false, false);
          if (mr > 0) {
            if (!rendActive) events.push({ time: t + REND_TICK_INTERVAL, type: 'rend_tick' });
            rendActive = true;
            rendEndsAt = t + REND_DURATION;
            onMeleeWeaponSwing();
            onLandedWeaponHit(t);
            if (mr === 2) onCrit(t);
          }
          rage -= REND_RAGE_COST; gcdReady = t + GCD; rendCasts++;
          events.push({ time: gcdReady, type: 'decision' });
        } else {
          var retry = Math.min(nextMhAt, nextOhAt);
          if (retry <= t) retry = t + 0.01;
          events.push({ time: retry, type: 'decision' });
        }
      }
    }
    return { dmg: dmg, rendCasts: rendCasts, opCasts: opCasts, bloodrageCasts: bloodrageCasts, swings: swings, rendTicks: rendTicks, dmgBy: dmgBy };
  }

  function run() {
    var p = {
      AP: num('tcAP'), SP: num('tcSP'),
      hitFrac: Math.max(0, num('tcHit')) / 100,
      critFrac: Math.max(0, num('tcCrit')) / 100,
      wpnDmg: num('tcWpnDmg'), weaponSpeed: Math.max(0.1, num('tcWpnSpeed')),
      ohWpnDmg: Math.max(0, num('tcOhDmg')), ohWeaponSpeed: Math.max(0.1, num('tcOhSpeed')),
      dwsRank: num('tcDws'), flurryRank: num('tcFlurry'), unbridledRank: num('tcUnbridled'),
      crueltyRank: num('tcCruelty'), precisionRank: num('tcPrecision'),
      boundlessRank: num('tcBoundlessRage'), useBloodrage: bool('tcBloodrage'),
      procChance: Math.max(0, num('tcProcChance')) / 100, procDmg: Math.max(0, num('tcProcDmg')),
      bleedChance: Math.max(0, num('tcBleedChance')) / 100, bleedTick: Math.max(0, num('tcBleedTick')),
      bleedInterval: Math.max(0.5, num('tcBleedInterval') || 3), bleedDuration: Math.max(0, num('tcBleedDuration')),
      fightLen: Math.max(10, parseFloat(fightLenInput.value) || 300),
    };
    var iterations = Math.max(1, Math.min(20000, parseInt(iterInput.value, 10) || 2000));
    var dpsSamples = [];
    var totalRend = 0, totalOp = 0, totalBloodrage = 0, totalSwings = 0, totalRendTicks = 0;
    var totalDmgBy = { white: 0, rend: 0, op: 0, proc: 0, bleed: 0 };
    for (var i = 0; i < iterations; i++) {
      var r = simulateOnce(p);
      dpsSamples.push(r.dmg / p.fightLen);
      totalRend += r.rendCasts; totalOp += r.opCasts; totalBloodrage += r.bloodrageCasts;
      totalSwings += r.swings; totalRendTicks += r.rendTicks;
      for (var cat in totalDmgBy) totalDmgBy[cat] += r.dmgBy[cat];
    }
    var mean = dpsSamples.reduce(function (a, b) { return a + b; }, 0) / iterations;
    var variance = dpsSamples.reduce(function (a, b) { return a + (b - mean) * (b - mean); }, 0) / iterations;
    var stderr = Math.sqrt(variance / iterations);

    function fmt(n) { return (Math.round(n * 100) / 100).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }

    document.getElementById('simDps').textContent = fmt(mean);
    document.getElementById('simCi').textContent = '± ' + fmt(1.96 * stderr) + ' (95%)';
    document.getElementById('simCasts').textContent =
      (totalRend / iterations).toFixed(1) + ' / ' + (totalOp / iterations).toFixed(1) + ' / ' +
      (totalBloodrage / iterations).toFixed(1) + ' / ' + (totalSwings / iterations).toFixed(1);
    var rendUptimePct = 100 * Math.min(1, (totalRendTicks * REND_TICK_INTERVAL) / (iterations * p.fightLen));
    var rendRow = document.getElementById('simRendUptime');
    if (rendRow) rendRow.textContent = fmt(rendUptimePct) + '%';

    var totalDmgAll = 0;
    for (var catKey in totalDmgBy) totalDmgAll += totalDmgBy[catKey];
    var breakdownIds = { white: 'simDmgWhite', rend: 'simDmgRend', op: 'simDmgOp', proc: 'simDmgProc', bleed: 'simDmgBleed' };
    for (var bk in breakdownIds) {
      var bEl = document.getElementById(breakdownIds[bk]);
      if (!bEl) continue;
      var bDps = totalDmgBy[bk] / (iterations * p.fightLen);
      var bPct = totalDmgAll > 0 ? (100 * totalDmgBy[bk] / totalDmgAll) : 0;
      bEl.textContent = fmt(bDps) + ' (' + fmt(bPct) + '%)';
    }
    document.getElementById('simResults').hidden = false;
    document.getElementById('simBreakdownTitle').hidden = false;
    document.getElementById('simBreakdown').hidden = false;
  }

  runBtn.addEventListener('click', run);
})();
