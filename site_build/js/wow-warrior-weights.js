(function () {
  'use strict';
  // Analytical (formula-based) DPS/stat-weight calculator for the real level-20 Fury Warrior kit --
  // a quick estimate, not the full internal simulator (see the "how it's calculated" section below).
  // Strength -> Attack Power and Agility -> Critical Strike: RankedBoost WoW Classic Stats (already
  // used elsewhere on this site). Rend/Overpower values: WoW: Forever's own Wowhead tooltips.
  var AP_PER_STR = 2;
  var CRIT_PCT_PER_AGI = 1 / 20;
  var CRIT_RATING_PER_PCT = 14;
  var HIT_RATING_PER_PCT = 10;
  var REND_TOTAL_DMG = 45, REND_DURATION = 15;
  var OVERPOWER_FLAT = 5, OVERPOWER_CD = 5;
  var DODGE_CHANCE = 0.05;

  var ids = ['tcAP', 'tcAgi', 'tcSP', 'tcHit', 'tcCrit', 'tcWpnDmg', 'tcWpnSpeed', 'tcOhDmg', 'tcOhSpeed'];
  var inputs = {};
  ids.forEach(function (id) { inputs[id] = document.getElementById(id); });
  if (!inputs.tcAP) return;

  function num(id) {
    var v = parseFloat(inputs[id].value);
    return isFinite(v) ? v : 0;
  }

  function fmt(n) {
    return (Math.round(n * 100) / 100).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  function compute() {
    var AP = num('tcAP');
    var hitFrac = Math.max(0, num('tcHit')) / 100;
    var critFrac = Math.max(0, num('tcCrit')) / 100;
    var wpnDmg = num('tcWpnDmg'), wpnSpeed = Math.max(0.1, num('tcWpnSpeed'));
    var ohDmg = Math.max(0, num('tcOhDmg')), ohSpeed = Math.max(0.1, num('tcOhSpeed'));
    var critMult = 1 + critFrac;
    var dualWield = ohDmg > 0;

    var mhSwingsPerSec = 1 / wpnSpeed;
    var ohSwingsPerSec = dualWield ? 1 / ohSpeed : 0;
    var totalSwingsPerSec = mhSwingsPerSec + ohSwingsPerSec;

    var whiteMhBase = (wpnDmg + AP / 14) * mhSwingsPerSec;
    var whiteOhBase = dualWield ? (ohDmg + AP / 14) * 0.5 * ohSwingsPerSec : 0;
    var whiteBase = whiteMhBase + whiteOhBase;
    var whiteDps = whiteBase * hitFrac * critMult;

    // Rend: assumed maintained at ~100% uptime (cheap, 10 Rage, refresh-only). No AP/SP coefficient --
    // its real value is a flat rank-based total per WoW: Forever's own tooltip.
    var rendBase = REND_TOTAL_DMG / REND_DURATION;
    var rendDps = rendBase * hitFrac * critMult;

    // Overpower: usable only within 5s of a target Dodge against a normal swing, capped by its own
    // 5s cooldown -- steady-state rate estimate, not the exact per-swing timing the real simulator uses.
    var opRatePerSec = Math.min(1 / OVERPOWER_CD, DODGE_CHANCE * totalSwingsPerSec);
    var opBase = (wpnDmg + AP / 14 + OVERPOWER_FLAT) * opRatePerSec;
    var opDps = opBase * hitFrac * critMult;

    var totalDps = whiteDps + rendDps + opDps;

    document.getElementById('tcWhiteDps').textContent = fmt(whiteDps);
    document.getElementById('tcRendDps').textContent = fmt(rendDps);
    document.getElementById('tcOpDps').textContent = fmt(opDps);
    document.getElementById('tcTotalDps').textContent = fmt(totalDps);

    var baseSum = whiteBase + rendBase + opBase;
    var dDpsPerAp = hitFrac * critMult * (mhSwingsPerSec / 14 + (dualWield ? (0.5 * ohSwingsPerSec / 14) : 0) + opRatePerSec / 14);
    var dDpsPerStr = AP_PER_STR * dDpsPerAp;
    var dDpsPerCritPct = baseSum * hitFrac * 0.01;
    var dDpsPerAgi = dDpsPerCritPct * CRIT_PCT_PER_AGI;
    var dDpsPerHitPct = baseSum * critMult * 0.01;

    document.getElementById('tcWStr').textContent = '+' + fmt(dDpsPerStr);
    document.getElementById('tcWAgi').textContent = '+' + fmt(dDpsPerAgi);
    document.getElementById('tcWAp').textContent = '+' + fmt(dDpsPerAp);
    document.getElementById('tcWHit').textContent = '+' + fmt(dDpsPerHitPct);
    document.getElementById('tcWCrit').textContent = '+' + fmt(dDpsPerCritPct);
    var wCritRating = document.getElementById('tcWCritRating');
    var wHitRating = document.getElementById('tcWHitRating');
    if (wCritRating) wCritRating.textContent = '+' + fmt(dDpsPerCritPct / CRIT_RATING_PER_PCT);
    if (wHitRating) wHitRating.textContent = '+' + fmt(dDpsPerHitPct / HIT_RATING_PER_PCT);
  }

  ids.forEach(function (id) { if (inputs[id]) inputs[id].addEventListener('input', compute); });
  compute();
})();
