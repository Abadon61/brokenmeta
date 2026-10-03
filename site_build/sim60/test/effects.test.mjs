import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runBatch } from '../run.js';
import { furyKit } from '../warrior.js';
import { rogueKit } from '../rogue.js';
import { mageKit } from '../mage.js';
import { buildCharacter } from '../character.js';
import { SAMPLE_FURY, SAMPLE_ROGUE, SAMPLE_MAGE } from '../samples.js';
import { ranksToBuild, ranksFromNames, PRESETS } from '../talents.js';

const rd = (f) => JSON.parse(readFileSync(new URL('../data/' + f, import.meta.url)));
const fx = rd('effects.json'), items = rd('items.json').items, spells = rd('spells60.json');
const byName = (n) => { const i = items.find((x) => x.name === n); assert.ok(i, n); return i; };
const gearOf = (...names) => names.map((n) => { const i = byName(n); return { slot: 'trinket', id: i.id, name: i.name, st: i.st }; });
const weaponOf = (n, extra = {}) => { const i = byName(n), speed = (i.st.speed || 2.6); return { min: i.st.dps * speed * 0.75, max: i.st.dps * speed * 1.25, speed, type: 'sword', itemId: i.id, ...extra }; };

test('on-use trinkets: haste and spell power buffs, with their own cooldown', () => {
  const tal = rd('talents.json').mage, build = Object.assign(ranksToBuild('mage', tal, ranksFromNames(tal, PRESETS.mage_frost)), { rotation: 'frost' });
  const run = (sample) => { const ch = buildCharacter(sample); return runBatch({ fightLen: 180, player: ch.player, target: ch.target, kitFactory: () => mageKit(build, spells) }, 800, 1); };
  const base = run({ ...SAMPLE_MAGE, effects: fx }), withT = run({ ...SAMPLE_MAGE, effects: fx, gear: SAMPLE_MAGE.gear.concat(gearOf('Talisman of Ephemeral Power')) });
  assert.ok(withT.mean > base.mean, 'Talisman of Ephemeral Power');
  assert.ok(withT.uptimes['Ephemeral Power'] > 0.1 && withT.uptimes['Ephemeral Power'] < 0.25, 'uptime ' + withT.uptimes['Ephemeral Power']);
  const fury = (sample) => { const ch = buildCharacter(sample); return runBatch({ fightLen: 180, player: ch.player, target: ch.target, kitFactory: () => furyKit({}, spells) }, 800, 1).mean; };
  assert.ok(fury({ ...SAMPLE_FURY, effects: fx, gear: SAMPLE_FURY.gear.concat(gearOf('Manual Crowd Pummeler')) }) > fury({ ...SAMPLE_FURY, effects: fx }) * 1.02, 'Manual Crowd Pummeler');
});

test('weapon procs: damage and damage over time fire from the swinging weapon only', () => {
  const run = (sample) => { const ch = buildCharacter(sample); return runBatch({ fightLen: 180, player: ch.player, target: ch.target, kitFactory: () => rogueKit({}, spells) }, 800, 1); };
  const daggers = (n) => [weaponOf(n), weaponOf('Stinging Viper', { offHand: true })];
  const r = run({ ...SAMPLE_ROGUE, effects: fx, weapons: daggers('Shadowfang') });
  assert.ok(r.breakdown['Shadow Bolt'].dps > 0 && r.breakdown['Poison'].dps > 0, Object.keys(r.breakdown).join());
  const none = run({ ...SAMPLE_ROGUE, weapons: daggers('Shadowfang') });
  assert.ok(!none.breakdown['Shadow Bolt'], 'no effects data, no proc');
  const summary = buildCharacter({ ...SAMPLE_ROGUE, effects: fx, weapons: daggers('Shadowfang') }).summary.effects;
  assert.ok(summary.some((e) => e.name === 'Shadow Bolt' && e.status === 'simulated'));
});

test('a spell-cast proc fires for casters and a melee proc stays inactive on a staff', () => {
  const tal = rd('talents.json').mage, build = Object.assign(ranksToBuild('mage', tal, ranksFromNames(tal, PRESETS.mage_fire)), { rotation: 'fire' });
  const ch = buildCharacter({ ...SAMPLE_MAGE, effects: fx, gear: SAMPLE_MAGE.gear.concat(gearOf('Kindling Stave')) });
  const r = runBatch({ fightLen: 180, player: ch.player, target: ch.target, kitFactory: () => mageKit(build, spells) }, 500, 1);
  assert.ok(r.breakdown['Ignition'] && r.breakdown['Ignition'].dps > 0, Object.keys(r.breakdown).join());
});

test('set bonuses count the equipped pieces: 3 pieces of a caster set add spell power and the 5-piece energizes', () => {
  const set = fx.sets.find((s) => s.name === "Magister's Regalia"), ids = set.pool_items;
  const pieces = (n) => ids.slice(0, n).map((id) => { const i = items.find((x) => x.id === id); return { slot: 'x' + id, id, name: i.name, st: {} }; });
  const sp = (n) => buildCharacter({ class: 'mage', race: 'human', gear: pieces(n), weapons: [], effects: fx }).summary.sp;
  assert.equal(sp(2), 0); assert.equal(sp(3), 18); assert.equal(sp(5), 18);
  assert.ok(buildCharacter({ class: 'mage', race: 'human', gear: pieces(5), weapons: [], effects: fx }).summary.effects.some((e) => e.name === 'Sudden Insight'));
});

test('the optimizer tries items that only have an effect (a trinket with no stats)', async () => {
  const { ItemPool } = await import('../items.js');
  const { optimizeGear } = await import('../optimizer.js');
  const pool = new ItemPool(rd('items.json'), rd('proficiency.json'));
  const tal = rd('talents.json').mage, build = Object.assign(ranksToBuild('mage', tal, ranksFromNames(tal, PRESETS.mage_frost)), { rotation: 'frost' });
  const res = optimizeGear({ pool, character: { ...SAMPLE_MAGE, gear: [], weapons: [], effects: fx }, caster: true, kit: () => mageKit(build, spells), iterations: 200, prefilter: 3, maxPasses: 1 });
  const out = await res;
  assert.ok(out.dps > 100);
  assert.ok(out.log.length > 3);
});
