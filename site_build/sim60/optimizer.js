// Gear optimizer: weight-based prefilter, then coordinate ascent with the real simulator using
// common random numbers (paired seeds => tiny noise on the DPS difference between two sets).
import { runBatch } from './run.js';
import { buildCharacter } from './character.js';
import { statWeights } from './weights.js';
import { EQUIP_SLOTS, toWeapon } from './items.js';

function evaluate(spec, kit, fightLen, iterations, seed) {
  const ch = buildCharacter(spec);
  const cfg = { fightLen, player: ch.player, target: ch.target, kitFactory: kit };
  return runBatch(cfg, iterations, seed).mean;
}

// Linear score of an item with stat weights expressed as AP-equivalents.
function score(item, w) {
  const s = item.st || {};
  return (s.str || 0) * 2 + (s.agi || 0) * w.agi + (s.atkpwr || 0)
    + (s.critstrkrtng || 0) / 14 * w.crit + (s.hitrtng || 0) / 10 * w.hit + (s.hastertng || 0) / 10 * w.haste;
}

export function optimizeGear({ pool, character, kit, fightLen = 180, iterations = 600, prefilter = 4, maxPasses = 3, seed = 11, weights, onProgress }) {
  const cls = character.class, base = Object.assign({}, character, { gear: [...(character.gear || [])] });
  const bySlot = {};
  for (const s of EQUIP_SLOTS) bySlot[s] = base.gear.find((g) => g.slot === s) || null;
  const w = weights || (() => {
    const ch = buildCharacter(base);
    const sw = statWeights({ fightLen, player: ch.player, target: ch.target, kitFactory: kit }, 1500, seed);
    const apPer = sw.perPoint.ap;
    return { agi: 0.05 * sw.normalizedToAp.crit, crit: sw.normalizedToAp.crit, hit: sw.normalizedToAp.hit, haste: sw.normalizedToAp.haste, apPer };
  })();

  const specOf = () => Object.assign({}, base, { gear: EQUIP_SLOTS.map((s) => bySlot[s]).filter(Boolean) });
  let best = evaluate(specOf(), kit, fightLen, iterations, seed);
  const log = [{ pass: 0, dps: best }];

  for (let pass = 1; pass <= maxPasses; pass++) {
    let improved = false;
    for (const slot of EQUIP_SLOTS) {
      const used = new Set(EQUIP_SLOTS.filter((s) => s !== slot && bySlot[s]).map((s) => bySlot[s].id));
      let cands = pool.forSlot(slot, cls, 60).filter((i) => !used.has(i.id) && i.from !== undefined);
      cands.sort((a, b) => score(b, w) - score(a, w));
      cands = cands.slice(0, prefilter);
      const current = bySlot[slot];
      if (current && !cands.find((c) => c.id === current.id)) cands.push(current);
      let bestItem = current, bestDps = best;
      for (const it of cands) {
        if (current && it.id === current.id) continue;
        bySlot[slot] = { slot, id: it.id, name: it.name, st: it.st };
        const d = evaluate(specOf(), kit, fightLen, iterations, seed);
        if (d > bestDps + 0.05) { bestDps = d; bestItem = bySlot[slot]; }
      }
      bySlot[slot] = bestItem;
      if (bestDps > best + 0.05) { best = bestDps; improved = true; log.push({ pass, slot, name: bestItem && bestItem.name, dps: best }); }
      if (onProgress) onProgress({ pass, slot, dps: best });
    }
    if (!improved) break;
  }
  return { dps: best, gear: EQUIP_SLOTS.map((s) => bySlot[s]).filter(Boolean), log, weights: w };
}
