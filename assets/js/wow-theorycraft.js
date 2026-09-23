(function () {
  'use strict';
  // Real, sourced constants -- see the page's own "How this is calculated" section for the exact citations.
  // Bloodthirst / Whirlwind: WoW: Forever's own Wowhead tooltips (spell=23894, spell=1680), max rank, level 60.
  // Strength -> Attack Power and Agility -> Critical Strike: RankedBoost WoW Classic Stats (already used by the optimizer).
  var BT_AP_COEFF = 0.35, BT_SP_COEFF = 1.00, BT_CD = 6;
  var WW_CD = 10;
  var AP_PER_STR = 2;          // Warrior melee Attack Power per point of Strength
  var CRIT_PCT_PER_AGI = 1 / 20; // 1% critical strike per 20 Agility (Warrior)
  // Rating -> percent at level 60, read directly off real WoW: Forever item tooltips (Wowhead shows the exact
  // conversion in parentheses, e.g. "+28 Critical Strike (2.00% @ L60)"), cross-checked on 2 items each:
  // Ragefury Eyepatch (item=11735, +28 -> 2.00%) and Illusionary Rod (item=7713, +14 -> 1.00%) for crit;
  // Blackstone Ring (item=17713, +10 -> 1.00%) and Magister's Leggings (item=16687, +9 -> 0.90%) for hit.
  var CRIT_RATING_PER_PCT = 14;
  var HIT_RATING_PER_PCT = 10;

  var ids = ['tcAP', 'tcAgi', 'tcSP', 'tcHit', 'tcCrit', 'tcWpnDmg', 'tcWpnSpeed'];
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
    var AP = num('tcAP'), SP = num('tcSP');
    var hitFrac = Math.max(0, num('tcHit')) / 100;
    var critFrac = Math.max(0, num('tcCrit')) / 100;
    var wpnDmg = num('tcWpnDmg'), wpnSpeed = Math.max(0.1, num('tcWpnSpeed'));
    var critMult = 1 + critFrac;

    var whiteBase = (wpnDmg + AP / 14) / wpnSpeed;
    var btBase = (BT_AP_COEFF * AP + BT_SP_COEFF * SP) / BT_CD;
    var wwBase = (wpnDmg + AP / 14) / WW_CD;
    var baseSum = whiteBase + btBase + wwBase;

    var whiteDps = whiteBase * hitFrac * critMult;
    var btDps = btBase * hitFrac * critMult;
    var wwDps = wwBase * hitFrac * critMult;
    var totalDps = whiteDps + btDps + wwDps;

    document.getElementById('tcWhiteDps').textContent = fmt(whiteDps);
    document.getElementById('tcBtDps').textContent = fmt(btDps);
    document.getElementById('tcWwDps').textContent = fmt(wwDps);
    document.getElementById('tcTotalDps').textContent = fmt(totalDps);

    var dDpsPerAp = hitFrac * critMult * (1 / (14 * wpnSpeed) + BT_AP_COEFF / BT_CD + (1 / 14) / WW_CD);
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

  ids.forEach(function (id) { inputs[id].addEventListener('input', compute); });
  compute();
})();
