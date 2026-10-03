// node ranking.mjs [fightLen] [finalIterations]
// Builds data/wow_ranking60.json, the public DPS ranking of the hub page: every simulated specialization with the same rules:
// raid buffs of its family, the best gear the optimizer finds in the known beta item pool (dungeons + the few raid items), a standard
// race, item effects on, a single target for `fightLen` seconds. Tanks are listed apart with their threat per second.
import { readFileSync, writeFileSync } from 'node:fs';
import { ItemPool, toWeapon } from './items.js';
import { optimizeGear } from './optimizer.js';
import { runBatch } from './run.js';
import { buildCharacter } from './character.js';
import { makeKit, KITS } from './kits.js';
import { ranksToBuild, ranksFromNames, PRESETS } from './talents.js';
import { PRESET_RAID, PRESET_CASTER, PRESET_HUNTER } from './presets.js';

const FIGHT = +process.argv[2] || 180, FINAL = +process.argv[3] || 6000;
const here = new URL('.', import.meta.url);
const rd = (f) => JSON.parse(readFileSync(new URL('data/' + f, here)));
const pool = new ItemPool(rd('items.json'), rd('proficiency.json'));
const data = rd('spells60.json'), fx = rd('effects.json'), tal = rd('talents.json');

// spec -> { class, variant, mode, family, race, role }  (mode follows the page: dw / 2h / caster / ranged / stick / tank)
const SPECS = {
  warrior_fury: { cls: 'warrior', mode: 'dw' }, warrior_arms: { cls: 'warrior', mode: '2h' },
  rogue_combat: { cls: 'rogue', mode: 'dw' }, rogue_assassination: { cls: 'rogue', mode: 'dw' }, rogue_subtlety: { cls: 'rogue', mode: 'dw' },
  mage_fire: { cls: 'mage', mode: 'caster', family: 'caster' }, mage_frost: { cls: 'mage', mode: 'caster', family: 'caster' }, mage_arcane: { cls: 'mage', mode: 'caster', family: 'caster' },
  warlock_affliction: { cls: 'warlock', mode: 'caster', family: 'caster' }, warlock_destruction: { cls: 'warlock', mode: 'caster', family: 'caster' }, warlock_demonology: { cls: 'warlock', mode: 'caster', family: 'caster' },
  hunter_marksmanship: { cls: 'hunter', mode: 'ranged', family: 'hunter', build: { pet: 'none' } }, hunter_beastmastery: { cls: 'hunter', mode: 'ranged', family: 'hunter' },
  hunter_survival: { cls: 'hunter', mode: 'ranged', family: 'hunter' }, hunter_melee: { cls: 'hunter', variant: 'melee', mode: 'dw' },
  priest_shadow: { cls: 'priest', mode: 'caster', family: 'caster' }, shaman_elemental: { cls: 'shaman', mode: 'caster', family: 'caster', race: 'orc' },
  shaman_enhancement: { cls: 'shaman', variant: 'enhancement', mode: 'dw', race: 'orc' }, druid_balance: { cls: 'druid', mode: 'caster', family: 'caster' },
  druid_feral: { cls: 'druid', variant: 'feral', mode: 'stick' }, paladin_retribution: { cls: 'paladin', mode: '2h' },
  warrior_protection: { cls: 'warrior', variant: 'protection', mode: 'tank', tank: true }, paladin_protection: { cls: 'paladin', variant: 'protection', mode: 'tank', tank: true },
  druid_bear: { cls: 'druid', variant: 'bear', mode: 'stick', tank: true },
};
const FAMILY = { caster: PRESET_CASTER, hunter: PRESET_HUNTER };

const out = { generated: new Date().toISOString().slice(0, 10), fightLen: FIGHT, iterations: FINAL, build: rd('items.json').build, specs: [] };
const objectiveTank = (r, ch) => { const len = FIGHT, thr = r.counters.threat / len, dt = r.counters.dmgTaken / len, raw = ch.target.boss.dmg / ch.target.boss.speed; return Math.sqrt(Math.max(0, thr) * Math.max(0, raw - dt)); };

for (const [id, S] of Object.entries(SPECS)) {
  const t0 = Date.now();
  const family = FAMILY[S.family] || PRESET_RAID;
  const build = Object.assign(ranksToBuild(S.cls, tal[S.cls], ranksFromNames(tal[S.cls], PRESETS[id])), S.build || {});
  const kit = () => makeKit(id, build, data);
  const character = { class: S.cls, variant: S.variant, race: S.race || 'human', gear: [], weapons: [], buffs: family.buffs, consumables: family.consumables, debuffs: family.debuffs, effects: fx };
  const res = optimizeGear({
    pool, character, kit, fightLen: FIGHT, iterations: 500, prefilter: 4, maxPasses: 2, weaponMode: S.mode,
    caster: S.mode === 'caster', ranged: S.mode === 'ranged', stick: S.mode === 'stick', tank: !!S.tank, objective: S.tank ? objectiveTank : undefined,
  });
  const done = await res;
  // rebuild the final character the way the page applies an optimizer result
  const gear = done.gear.slice(), weapons = [];
  for (const w of done.weapons) {
    const it = pool.byId.get(w.id);
    if (w.slot === 'rng') weapons.push(toWeapon(it, false));
    else if (w.slot === 'th' && (S.mode === 'caster' || S.mode === 'ranged' || S.mode === 'stick')) gear.push({ slot: 'th', id: it.id, name: it.name, st: it.st });
    else weapons.push(toWeapon(it, w.slot === 'oh'));
  }
  const ch = buildCharacter({ ...character, gear, weapons });
  const r = runBatch({ fightLen: FIGHT, player: ch.player, target: ch.target, kitFactory: kit }, FINAL, 7);
  const row = { spec: id, class: S.cls, role: S.tank ? 'tank' : 'dps', dps: +r.mean.toFixed(1), sem: +r.sem.toFixed(2), name: KITS[id] };
  if (S.tank) { row.tps = +(r.counters.threat / FIGHT).toFixed(1); row.dtps = +(r.counters.dmgTaken / FIGHT).toFixed(1); row.health = Math.round(ch.summary.tank.health); }
  out.specs.push(row);
  console.log(id.padEnd(22), S.tank ? 'TPS ' + row.tps : 'DPS ' + row.dps, '±' + row.sem, ((Date.now() - t0) / 1000).toFixed(0) + 's');
}
writeFileSync(new URL('../../data/wow_ranking60.json', here), JSON.stringify(out, null, 1));
console.log('written', out.specs.length, 'specs');
