// racials.js numbers against the beta client's racial texts (data/wow_racials.json, wow_racials_build.py)
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { FOREVER_RACIALS } from '../racials.js';

const R = JSON.parse(readFileSync(new URL('../../../data/wow_racials.json', import.meta.url))).races;
const spell = (race, id) => R[race].spells.find((s) => s.id === id);
const pct = (race, id) => +/(\d+)%/.exec(spell(race, id).desc.en)[1];
const r2 = (x) => Math.round(x * 100) / 100;   // 0.07 * 100 = 7.000000000000001

test('weapon specializations and passive racials', () => {
  assert.equal(r2(FOREVER_RACIALS.human.crit * 100), pct('human', 20597));             // Ruthless: +2% critical strike chance (no weapon condition since 1.60.1.70425)
  assert.equal(r2(FOREVER_RACIALS.orc.crit * 100), pct('orc', 20574));                 // Savage: +1%
  assert.equal(r2(FOREVER_RACIALS.dwarf.critDmg * 100), pct('dwarf', 1259719));        // Earth Fury: +2% critical damage
  assert.match(spell('human', 20597).desc.en, /critical strike chance with all spells and attacks/);
  assert.equal(r2((FOREVER_RACIALS.human.spiritMult - 1) * 100), pct('human', 20598));
  assert.equal(r2(FOREVER_RACIALS.tauren.critDmg * 100), 2);                   // Endurance: "critical strike bonus to damage and healing increased by 2%"
  assert.match(spell('tauren', 20550).desc.en, /critical strike bonus to damage and healing increased by 2%/);
  assert.equal(Math.round((FOREVER_RACIALS.skyborne.haste - 1) * 100), pct('skyborne-alliance', 1259710));
  assert.equal(r2((FOREVER_RACIALS.gnome.manaMult - 1) * 100), pct('gnome', 20591));
});

test('on-use racials: effect, duration and cooldown', () => {
  const bf = FOREVER_RACIALS.orc.use, bfs = spell('orc', 20572);
  assert.equal(r2((bf.apMult - 1) * 100), pct('orc', 20572)); assert.equal(bf.duration, bfs.duration_s); assert.equal(bf.cd, bfs.cooldown_s);
  const el = FOREVER_RACIALS.nightelf.use, els = spell('nightelf', 1259799);
  assert.equal(r2(el.crit * 100), pct('nightelf', 1259799)); assert.equal(el.duration, els.duration_s); assert.equal(el.cd, els.cooldown_s);
  const eu = FOREVER_RACIALS.gnome.use, eus = spell('gnome', 1259812);
  assert.equal(r2((eu.dmgMult - 1) * 100), pct('gnome', 1259812)); assert.equal(eu.duration, eus.duration_s); assert.equal(eu.cd, eus.cooldown_s);   // Eureka!: 8 s, +10% damage, 120 s
  const bz = FOREVER_RACIALS.troll.use, bzs = spell('troll', 20554);
  assert.equal(bz.duration, bzs.duration_s); assert.equal(bz.cd, bzs.cooldown_s);   // the +10% haste is in the spell effects (aura 140 / 65, base 10)
});
