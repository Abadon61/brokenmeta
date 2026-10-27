// racials.js numbers against the beta client's racial texts (data/wow_racials.json, wow_racials_build.py)
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { FOREVER_RACIALS } from '../racials.js';

const R = JSON.parse(readFileSync(new URL('../../../data/wow_racials.json', import.meta.url))).races;
// the client tables (build 70425) plus the changes Blizzard announced on 2026-10-26/27 (data/wow_racials_announced.json), the way wow_racepick.load_racials() applies them
const OV = JSON.parse(readFileSync(new URL('../../../data/wow_racials_announced.json', import.meta.url))).races;
for (const [key, ch] of Object.entries(OV)) {
  for (const rk of Object.keys(R).filter((k) => k === key || k.startsWith(key + '-'))) {
    for (const [sid, f] of Object.entries(ch.set || {})) { const s = R[rk].spells.find((x) => x.id === +sid); if (s) Object.assign(s, f); }
    if (ch.remove) R[rk].spells = R[rk].spells.filter((s) => !ch.remove.includes(s.id));
    for (const s of ch.add || []) R[rk].spells.push({ ...s });
  }
}
const spell = (race, id) => R[race].spells.find((s) => s.id === id);
const pct = (race, id) => +/(\d+)%/.exec(spell(race, id).desc.en)[1];
const r2 = (x) => Math.round(x * 100) / 100;   // 0.07 * 100 = 7.000000000000001

test('weapon specializations and passive racials', () => {
  assert.equal(r2(FOREVER_RACIALS.human.crit * 100), pct('human', 20597));             // Ruthless: +1% critical strike chance since the 2026-10-26 tuning pass (2% in the client tables)
  assert.match(spell('human', 20597).desc.en, /critical strike chance with all spells and attacks/);
  assert.equal(r2((FOREVER_RACIALS.human.spiritMult - 1) * 100), pct('human', 20598)); // The Human Spirit: +10% (5% in the client tables)
  assert.equal(spell('orc', 20574), undefined); assert.equal(FOREVER_RACIALS.orc.crit, undefined);   // Savage removed
  assert.equal(spell('dwarf', 1259719), undefined); assert.equal(FOREVER_RACIALS.dwarf.critDmg, undefined);   // Earth Fury removed
  assert.equal(r2(FOREVER_RACIALS.dwarf.hit * 100), pct('dwarf', 9000002));            // Artisan's Precision: +1% hit chance with spells and attacks
  assert.equal(r2(FOREVER_RACIALS.orc.petDmg * 100), pct('orc', 9000001));             // Command: +5% damage of Warlock and Hunter pets
  assert.equal(FOREVER_RACIALS.tauren.critDmg, undefined);                              // Endurance: +5% health only, no critical damage any more
  assert.doesNotMatch(spell('tauren', 20550).desc.en, /critical/);
  assert.equal(Math.round((FOREVER_RACIALS.skyborne.haste - 1) * 100), pct('skyborne-alliance', 1259710));   // Wind Blessed: 2%
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
