// Gear optimizer: weight-based prefilter, then coordinate ascent with the real simulator using
// common random numbers (paired seeds => tiny noise on the DPS difference between two sets).
// Armor/jewelry slots and weapons are optimized together; weapons follow the spec's weapon mode
// ('dw' = main hand + off hand, '2h' = one two-hander).
import { runBatch } from './run.js';
import { buildCharacter } from './character.js';
import { statWeights } from './weights.js';
import { EQUIP_SLOTS, toWeapon } from './items.js';

// Linear score of an item with stat weights expressed as AP-equivalents.
// Casters: spell power plus Intellect (crit + mana), spirit and mp5 at fixed Classic-style values (only a prefilter: the real simulator picks).
function casterScore(item, w) {
  const s = item.st || {};
  return (s.splpwr || 0) + (s.spldmg || 0) + (s.int || 0) * (w.crit / 59.5 + 0.2) + (s.critstrkrtng || 0) / 14 * w.crit + (s.hitrtng || 0) / 10 * w.hit + (s.hastertng || 0) / 10 * w.haste + (s.manargn || 0) * 0.8 + (s.spi || 0) * 0.1;
}
// Hunters: ranged attack power (Agility counts twice: attack power and crit), Intellect through Careful Aim, ranged weapon dps.
function hunterScore(item, w) {
  const s = item.st || {};
  return (s.agi || 0) * (1 + w.crit / 53) + (s.atkpwr || 0) + (s.int || 0) * 0.2 + (s.critstrkrtng || 0) / 14 * w.crit + (s.hitrtng || 0) / 10 * w.hit + (s.hastertng || 0) / 10 * w.haste + (s.dps || 0) * (w.dpsPerWeaponDps || 8) + (s.manargn || 0) * 0.5;
}
function score(item, w) {
  if (w.caster) return casterScore(item, w);
  if (w.hunter) return hunterScore(item, w);
  const s = item.st || {};
  return (s.str || 0) * 2 + (s.agi || 0) * w.agi + (s.atkpwr || 0)
    + (s.critstrkrtng || 0) / 14 * w.crit + (s.hitrtng || 0) / 10 * w.hit + (s.hastertng || 0) / 10 * w.haste
    + (s.dps || 0) * (w.dpsPerWeaponDps || 8);
}

const WEAPON_SLOTS = { dw: ['mh', 'oh'], '2h': ['th'], caster: ['th'], ranged: ['rng', 'th'] };

function weaponCandidates(pool, cls, slot, mode) {
  const w = pool.weapons(cls, 60);
  if (slot === 'rng') return w.ranged;
  if (mode === 'ranged' && slot === 'th') return w.twoHand.concat(w.oneHand, w.mainHand);   // melee weapon only lends its stats to a hunter
  if (slot === 'mh') return w.oneHand.concat(w.mainHand);
  if (slot === 'oh') return w.oneHand.concat(w.offHand);
  return w.twoHand;
}

// Generic async core. `evaluate(spec)` -> Promise<number> (mean DPS), `getWeights(spec)` -> Promise<{agi,crit,hit,haste}>.
export async function optimizeGearAsync({ pool, character, evaluate, getWeights, prefilter = 4, weaponPrefilter = 6, maxPasses = 3, onProgress, weaponMode, caster, ranged }) {
  const cls = character.class, base = Object.assign({}, character, { gear: [], weapons: [] });
  const mode = caster ? 'caster' : ranged ? 'ranged' : weaponMode || ((character.weapons || []).length > 1 ? 'dw' : ((character.weapons || [])[0] && character.weapons[0].twoHand ? '2h' : 'dw'));
  const wslots = WEAPON_SLOTS[mode];
  const bySlot = {};
  for (const s of EQUIP_SLOTS) bySlot[s] = (character.gear || []).find((g) => g.slot === s) || null;
  // current weapons by role
  const wsel = {};
  const cw = character.weapons || [];
  if (mode === 'ranged') { wsel.rng = cw[0] ? pool.byId.get(cw[0].itemId) || null : null; wsel.th = null; }
  else if (mode === '2h' || mode === 'caster') wsel.th = cw[0] ? pool.byId.get(cw[0].itemId) || null : null;
  else { wsel.mh = cw[0] ? pool.byId.get(cw[0].itemId) || null : null; wsel.oh = cw[1] ? pool.byId.get(cw[1].itemId) || null : null; }

  const specOf = () => {
    // casters have no swung weapon: the staff only contributes its stats, so it rides along with the gear
    const weapons = mode === 'caster' ? [] : mode === 'ranged' ? (wsel.rng ? [toWeapon(wsel.rng, false)] : []) : mode === '2h'
      ? (wsel.th ? [toWeapon(wsel.th, false)] : [])
      : [wsel.mh && toWeapon(wsel.mh, false), wsel.oh && toWeapon(wsel.oh, true)].filter(Boolean);
    const gear = EQUIP_SLOTS.map((s) => bySlot[s]).filter(Boolean);
    if ((mode === 'caster' || mode === 'ranged') && wsel.th) gear.push({ slot: 'th', id: wsel.th.id, name: wsel.th.name, st: wsel.th.st });
    return Object.assign({}, base, { gear, weapons });
  };
  // start from the best static pick when a weapon slot is empty (the engine needs a weapon to swing)
  const staticW = { agi: 0.3, crit: caster ? 6 : 28, hit: caster ? 8 : 22, haste: 20, dpsPerWeaponDps: 8, caster: !!caster, hunter: !!ranged };
  for (const slot of wslots) {
    if (wsel[slot]) continue;
    const taken = new Set(wslots.filter((x) => wsel[x]).map((x) => wsel[x].id));
    const c = weaponCandidates(pool, cls, slot, mode).filter((i) => !taken.has(i.id)).sort((x, y) => score(y, staticW) - score(x, staticW));
    wsel[slot] = c[0] || null;
  }
  const w = Object.assign({ caster: !!caster, hunter: !!ranged }, await getWeights(specOf()));
  let best = await evaluate(specOf());
  const log = [{ pass: 0, dps: best }];
  for (let pass = 1; pass <= maxPasses; pass++) {
    let improved = false;
    // weapons first: they dominate the result
    for (const slot of wslots) {
      const others = new Set(wslots.filter((s) => s !== slot && wsel[s]).map((s) => wsel[s].id));
      let cands = weaponCandidates(pool, cls, slot, mode).filter((i) => !others.has(i.id));
      cands.sort((a, b) => score(b, w) - score(a, w));
      cands = cands.slice(0, weaponPrefilter);
      const current = wsel[slot];
      let bestItem = current, bestDps = best;
      for (const it of cands) {
        if (current && it.id === current.id) continue;
        wsel[slot] = it;
        const d = await evaluate(specOf());
        if (d > bestDps + 0.05) { bestDps = d; bestItem = it; }
      }
      wsel[slot] = bestItem;
      if (bestDps > best + 0.05) { best = bestDps; improved = true; log.push({ pass, slot, name: bestItem && bestItem.name, dps: best }); }
      if (onProgress) onProgress({ pass, slot, dps: best });
    }
    for (const slot of EQUIP_SLOTS) {
      const used = new Set(EQUIP_SLOTS.filter((s) => s !== slot && bySlot[s]).map((s) => bySlot[s].id));
      let cands = pool.forSlot(slot, cls, 60).filter((i) => !used.has(i.id));
      cands.sort((a, b) => score(b, w) - score(a, w));
      cands = cands.slice(0, prefilter);
      const current = bySlot[slot];
      let bestItem = current, bestDps = best;
      for (const it of cands) {
        if (current && it.id === current.id) continue;
        bySlot[slot] = { slot, id: it.id, name: it.name, st: it.st };
        const d = await evaluate(specOf());
        if (d > bestDps + 0.05) { bestDps = d; bestItem = bySlot[slot]; }
      }
      bySlot[slot] = bestItem;
      if (bestDps > best + 0.05) { best = bestDps; improved = true; log.push({ pass, slot, name: bestItem && bestItem.name, dps: best }); }
      if (onProgress) onProgress({ pass, slot, dps: best });
    }
    if (!improved) break;
  }
  const weapons = wslots.map((s) => wsel[s] && { slot: s, id: wsel[s].id, name: wsel[s].name, st: wsel[s].st }).filter(Boolean);
  return { dps: best, gear: EQUIP_SLOTS.map((s) => bySlot[s]).filter(Boolean), weapons, weaponMode: mode, log, weights: w };
}

// Synchronous-looking helper for node scripts and tests: evaluates on the current thread.
export function optimizeGear({ pool, character, kit, fightLen = 180, iterations = 600, seed = 11, weights, ...rest }) {
  const evaluate = async (spec) => {
    const ch = buildCharacter(spec);
    return runBatch({ fightLen, player: ch.player, target: ch.target, kitFactory: kit }, iterations, seed).mean;
  };
  const getWeights = async (spec) => {
    if (weights) return weights;
    const ch = buildCharacter(spec);
    const sw = statWeights({ fightLen, player: ch.player, target: ch.target, kitFactory: kit }, 1500, seed);
    return { agi: 0.05 * sw.normalizedToAp.crit, crit: sw.normalizedToAp.crit, hit: sw.normalizedToAp.hit, haste: sw.normalizedToAp.haste };
  };
  return optimizeGearAsync({ pool, character, evaluate, getWeights, ...rest });
}
