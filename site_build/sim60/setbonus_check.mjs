// node setbonus_check.mjs spec_id [iterations]   — final gear of the spec in data/wow_ranking60.json, simulated with 0 / 2 / 4 / 6 / 8 pieces counted for its class set(s):
// shows how much each Sanctified bonus adds (the gear itself is unchanged; only player.sets differs).
import { readFileSync } from 'node:fs';
import { ItemPool, toWeapon } from './items.js';
import { runBatch } from './run.js';
import { buildCharacter } from './character.js';
import { makeKit } from './kits.js';
import { ranksToBuild, ranksFromNames, PRESETS } from './talents.js';
import { PRESET_RAID, PRESET_CASTER, PRESET_HUNTER } from './presets.js';
const here = new URL('.', import.meta.url), rd = (f) => JSON.parse(readFileSync(new URL('data/' + f, here)));
const id = process.argv[2], N = +process.argv[3] || 3000;
const SETS = { warrior_fury: [1932], warrior_arms: [1932], rogue_combat: [1934], rogue_assassination: [1934], rogue_subtlety: [1934], hunter_melee: [1936], hunter_marksmanship: [1937], hunter_beastmastery: [1937],
  priest_shadow: [1938], paladin_retribution: [1940], mage_fire: [1943, 1944], mage_frost: [1943, 1944], mage_arcane: [1943, 1944], druid_feral: [1945], druid_balance: [1946], shaman_elemental: [1952], shaman_enhancement: [1951],
  warlock_affliction: [1954], warlock_destruction: [1954], warlock_demonology: [1954], warrior_protection: [1933], paladin_protection: [1942], druid_bear: [1948] };
const META = { warrior_fury: ['warrior'], warrior_arms: ['warrior'], rogue_combat: ['rogue'], rogue_assassination: ['rogue'], rogue_subtlety: ['rogue'], hunter_melee: ['hunter', 'melee'], hunter_marksmanship: ['hunter', , 'hunter', { pet: 'none' }], hunter_beastmastery: ['hunter', , 'hunter'],
  priest_shadow: ['priest', , 'caster'], paladin_retribution: ['paladin'], mage_fire: ['mage', , 'caster'], mage_frost: ['mage', , 'caster'], mage_arcane: ['mage', , 'caster'], druid_feral: ['druid', 'feral'], druid_balance: ['druid', , 'caster'],
  shaman_elemental: ['shaman', , 'caster'], shaman_enhancement: ['shaman', 'enhancement'], warlock_affliction: ['warlock', , 'caster'], warlock_destruction: ['warlock', , 'caster'], warlock_demonology: ['warlock', , 'caster'],
  warrior_protection: ['warrior', 'protection'], paladin_protection: ['paladin', 'protection'], druid_bear: ['druid', 'bear'] };
const [cls, variant, fam, extra] = META[id];
const family = fam === 'caster' ? PRESET_CASTER : fam === 'hunter' ? PRESET_HUNTER : PRESET_RAID;
const pool = new ItemPool(rd('items.json'), rd('proficiency.json'));
const row = JSON.parse(readFileSync(new URL('../../data/wow_ranking60.json', here))).specs.find((s) => s.spec === id);
const data = rd('spells60.json'), fx = rd('effects.json'), tal = rd('talents.json');
const build = Object.assign(ranksToBuild(cls, tal[cls], ranksFromNames(tal[cls], PRESETS[id])), extra || {});
const WSLOT = new Set(['mh', 'oh', 'th', 'rng']);
const gear = [], weapons = [];
for (const it of row.detail.items) {
  const p = pool.byId.get(it.id); if (!p) continue;
  if (it.slot === 'rng') weapons.push(toWeapon(p, false));
  else if (it.slot === 'th' && (fam === 'caster' || fam === 'hunter' || variant === 'feral' || variant === 'bear')) gear.push({ slot: 'th', id: p.id, name: p.name, st: p.st });
  else if (WSLOT.has(it.slot)) weapons.push(toWeapon(p, it.slot === 'oh'));
  else gear.push({ slot: it.slot, id: p.id, name: p.name, st: p.st, set: p.set });
}
const character = { class: cls, variant, race: 'human', gear, weapons, buffs: family.buffs, consumables: family.consumables, debuffs: family.debuffs, effects: fx };
const FIGHT = 180;
const run = (n) => {
  const ch = buildCharacter(character);
  ch.player.sets = n === null ? {} : Object.fromEntries(SETS[id].map((s) => [s, n]));
  const r = runBatch({ fightLen: FIGHT, player: ch.player, target: ch.target, kitFactory: () => makeKit(id, build, data) }, N, 7);
  return r;
};
const worn = {}; for (const g of gear) if (g.set) worn[g.set] = (worn[g.set] || 0) + 1;
console.log(id, 'worn by the ranking:', JSON.stringify(worn), 'ranking dps', row.dps);
for (const n of [null, 2, 4, 6, 8]) { const r = run(n); console.log(' pieces', n === null ? 0 : n, 'dps', r.mean.toFixed(1), '±' + r.sem.toFixed(2)); }
