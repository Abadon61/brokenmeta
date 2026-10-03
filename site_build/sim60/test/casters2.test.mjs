import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runBatch } from '../run.js';
import { priestKit } from '../priest.js';
import { shamanElementalKit } from '../shaman.js';
import { druidBalanceKit } from '../druid.js';
import { buildCharacter } from '../character.js';
import { SAMPLE_PRIEST, SAMPLE_SHAMAN_ELE, SAMPLE_DRUID_BAL } from '../samples.js';
import { ranksToBuild, ranksFromNames, PRESETS } from '../talents.js';

const rd = (f) => JSON.parse(readFileSync(new URL('../data/' + f, import.meta.url)));
const spells = rd('spells60.json'), tals = rd('talents.json');
const KITS = { priest_shadow: [priestKit, 'priest', SAMPLE_PRIEST], shaman_elemental: [shamanElementalKit, 'shaman', SAMPLE_SHAMAN_ELE], druid_balance: [druidBalanceKit, 'druid', SAMPLE_DRUID_BAL] };
const run = (k, over = {}, sample, len = 180, n = 600) => {
  const [kit, cls, smp] = KITS[k], tal = tals[cls];
  const build = Object.assign(ranksToBuild(cls, tal, ranksFromNames(tal, PRESETS[k])), over);
  const ch = buildCharacter(sample || smp);
  return runBatch({ fightLen: len, player: ch.player, target: ch.target, kitFactory: () => kit(build, spells) }, n, 1);
};

test('the rank ladders give the top-rank spells at level 60', () => {
  const s = spells.shaman.top.shaman_lightning_bolt;
  assert.equal(s.spell_level, 56); assert.equal(s.cost.amount, 220);
  assert.ok(spells.priest.extra['Mind Flay'] && spells.druid.extra['Starfire'] && spells.shaman.extra['Lava Burst']);
});

test('Shadow Priest: Shadow Word: Pain and Devouring Plague tick, Mind Blast on cooldown, Mind Flay fills', () => {
  const r = run('priest_shadow');
  for (const n of ['Shadow Word: Pain', 'Mind Blast', 'Mind Flay', 'Devouring Plague']) assert.ok(r.breakdown[n] && r.breakdown[n].dps > 0, n + ' ' + Object.keys(r.breakdown));
  assert.ok(r.uptimes['Shadow Weaving'] > 0.5, 'Shadow Weaving ' + r.uptimes['Shadow Weaving']);
  assert.ok(r.mean > 250 && r.mean < 3000, 'dps ' + r.mean);
});

test('Elemental Shaman: Flame Shock up, Lava Burst and Chain Lightning on cooldown, Lightning Bolt fills, Overload fires', () => {
  const r = run('shaman_elemental', { chainLightning: true });
  for (const n of ['Flame Shock', 'Lava Burst', 'Chain Lightning', 'Lightning Bolt']) assert.ok(r.breakdown[n] && r.breakdown[n].dps > 0, n + ' ' + Object.keys(r.breakdown));
  assert.ok(r.breakdown['Lightning Bolt (Overload)'], 'Lightning Overload');
  assert.ok(r.mean > 150 && r.mean < 3000, 'dps ' + r.mean);
  assert.ok(!run('shaman_elemental', { lavaBurst: 0 }, null, 60, 100).breakdown['Lava Burst'], 'Lava Burst needs the talent');
});

test('Balance Druid: Moonfire and Insect Swarm up, Eclipse speeds Starfire', () => {
  const r = run('druid_balance');
  for (const n of ['Moonfire', 'Insect Swarm', 'Wrath', 'Starfire']) assert.ok(r.breakdown[n] && r.breakdown[n].dps > 0, n + ' ' + Object.keys(r.breakdown));
  assert.ok(r.uptimes['Eclipse'] > 0.3, 'Eclipse ' + r.uptimes['Eclipse']);
  assert.ok(r.mean > 250 && r.mean < 3000, 'dps ' + r.mean);
});

test('talents and spell power move the DPS of the new casters', () => {
  for (const [k, talent] of [['priest_shadow', 'darkness'], ['shaman_elemental', 'concussion'], ['druid_balance', 'moonfury']]) {
    const base = run(k, {}, null, 180, 1500).mean;
    assert.ok(base > run(k, { [talent]: 0 }, null, 180, 1500).mean * 1.01, k + ' ' + talent);
    const [, , smp] = KITS[k], more = { ...smp, gear: smp.gear.concat([{ slot: 'neck', name: 'x', st: { splpwr: 100 } }]) };
    assert.ok(run(k, {}, more, 180, 1500).mean > base * 1.05, k + ' spell power');
  }
});
