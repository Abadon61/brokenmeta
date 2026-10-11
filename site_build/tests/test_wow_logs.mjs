// node test_wow_logs.mjs : checks the numbers BrokenLogs computes from hand-written combat log lines (the formulas of the page's "how the numbers are computed").
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { Parser, gearLevels } = require('../js/wow-logs-core.js');

const ADV = ',' + Array(17).fill('0').join(',');                       // 17 advanced-log fields (their values are not used for damage)
let sec = 0;
const ts = (s) => `10/9/2026 21:00:${String(Math.floor(s)).padStart(2, '0')}.${String(Math.round((s % 1) * 1000)).padStart(4, '0')}`;
const A = 'Player-1-0000000A', B = 'Player-1-0000000B', BOSS = 'Creature-0-1-2-3-4-0000000C', PET = 'Pet-0-1-2-3-5-0000000D';
const nm = (g, n) => (g.startsWith('Player') ? n + '-Realm-EU' : n);          // only players carry a realm in their name
const dmg = (s, src, sn, dst, dn, spell, amount, over = -1, absorbed = 0, crit = 'nil') =>
  `${ts(s)}  SPELL_DAMAGE,${src},"${nm(src, sn)}",0x511,0x0,${dst},"${dn}",0x10a48,0x0,100,"${spell}",0x4${ADV},${amount},${amount},${over},4,0,0,${absorbed},${crit},nil,nil,ST`;
const swing = (ev, s, src, sn, dst, dn, amount) => `${ts(s)}  ${ev},${src},"${sn}-Realm-EU",0x511,0x0,${dst},"${dn}",0x10a48,0x0${ADV},${amount},${amount},-1,1,0,0,0,nil,nil,nil`;
const heal = (s, src, sn, dst, dn, amount, over) => `${ts(s)}  SPELL_HEAL,${src},"${sn}-Realm-EU",0x511,0x0,${dst},"${dn}-Realm-EU",0x511,0x0,200,"Heal",0x2${ADV},${amount},${amount},${over},0,nil`;

function run(lines) { const p = new Parser(); lines.forEach((l) => p.line(l)); return p.finish(); }
const start = (s) => `${ts(s)}  ENCOUNTER_START,100,"Test Boss",8,5,1`;
const end = (s, ok) => `${ts(s)}  ENCOUNTER_END,100,"Test Boss",8,5,${ok},${(s - 1) * 1000}`;

// 1. damage = amount - overkill + absorbed
{
  const r = run([start(1), dmg(2, A, 'Alice', BOSS, 'Test Boss', 'Bolt', 1000, 200, 50), end(11, 1)]);
  const a = r.fights[0].players[0];
  assert.equal(a.dmg, 850, 'overkill removed, absorbed added');
  assert.equal(r.fights[0].kind, 'boss'); assert.equal(r.fights[0].success, true); assert.equal(r.fights[0].name, 'Test Boss');
  assert.equal(a.dps, 85, 'DPS = damage / encounter duration (10 s)');
}
// 2. a wipe is flagged
assert.equal(run([start(1), dmg(2, A, 'Alice', BOSS, 'Test Boss', 'Bolt', 100), end(5, 0)]).fights[0].success, false);
// 3. *_DAMAGE_LANDED events are ignored (the game logs every swing twice)
{
  const r = run([start(1), swing('SWING_DAMAGE', 2, A, 'Alice', BOSS, 'Test Boss', 500), swing('SWING_DAMAGE_LANDED', 2, A, 'Alice', BOSS, 'Test Boss', 500), end(11, 1)]);
  assert.equal(r.fights[0].players[0].dmg, 500);
}
// 4. pets are merged into their owner (owner learned from SPELL_SUMMON)
{
  const r = run([`${ts(0.5)}  SPELL_SUMMON,${A},"Alice-Realm-EU",0x511,0x0,${PET},"Wolf",0x1112,0x0,200,"Call Pet",0x1`, start(1), dmg(2, A, 'Alice', BOSS, 'Test Boss', 'Bolt', 1000), dmg(3, PET, 'Wolf', BOSS, 'Test Boss', 'Bite', 400), end(11, 1)]);
  const a = r.fights[0].players.find((p) => p.name === 'Alice');
  assert.equal(r.fights[0].players.length, 1, 'the pet is not a player');
  assert.equal(a.dmg, 1400); assert.deepEqual(a.pets, [['Wolf', 400]]);
}
// 5. effective healing = amount - overhealing
{
  const r = run([start(1), heal(2, B, 'Bob', A, 'Alice', 1000, 300), end(11, 1)]);
  const b = r.fights[0].players.find((p) => p.name === 'Bob');
  assert.equal(b.heal, 700); assert.equal(b.over, 300); assert.equal(b.role, 'heal');
}
// 6. a death keeps the recap of what hit the player; a feigned death is not a death
{
  const hit = (s, n) => `${ts(s)}  SPELL_DAMAGE,${BOSS},"Test Boss",0x10a48,0x0,${A},"Alice-Realm-EU",0x511,0x0,300,"Slam",0x1${ADV},${n},${n},-1,1,0,0,0,nil,nil,nil,ST`;
  const died = (s, flag) => `${ts(s)}  UNIT_DIED,0000000000000000,nil,0x80000000,0x80000000,${A},"Alice-Realm-EU",0x511,0x0,${flag}`;
  const r = run([start(1), dmg(2, A, 'Alice', BOSS, 'Test Boss', 'Bolt', 100), hit(3, 400), hit(4, 600), died(5, 1), died(6, 0), end(11, 0)]);
  const a = r.fights[0].players[0];
  assert.equal(a.deaths.length, 1, 'feign death ignored');
  assert.equal(a.deaths[0].recap.length, 2); assert.equal(a.deaths[0].recap[1].v, 600); assert.equal(a.taken, 1000);
  assert.equal(r.fights[0].deaths, 1);
}
// 7. active time ignores gaps longer than 3 s
{
  const r = run([start(1), dmg(2, A, 'Alice', BOSS, 'Test Boss', 'Bolt', 100), dmg(3, A, 'Alice', BOSS, 'Test Boss', 'Bolt', 100), dmg(4, A, 'Alice', BOSS, 'Test Boss', 'Bolt', 100), dmg(12, A, 'Alice', BOSS, 'Test Boss', 'Bolt', 100), end(13, 1)]);
  const a = r.fights[0].players[0];
  assert.equal(a.active, 2, 'only the 1 s gaps count, the 8 s gap does not');
  assert.ok(a.adps > a.dps, 'active DPS is higher than raid DPS when the player was idle');
}
// 8. a combat without ENCOUNTER_START starts at the first player <-> creature hit and ends after 12 s of silence
{
  const r = run([dmg(2, A, 'Alice', BOSS, 'Orc', 'Bolt', 5000), dmg(8, A, 'Alice', BOSS, 'Orc', 'Bolt', 5000), dmg(40, A, 'Alice', BOSS, 'Orc', 'Bolt', 5000), dmg(46, A, 'Alice', BOSS, 'Orc', 'Bolt', 5000)]);
  assert.equal(r.fights.length, 2, 'two combats separated by 32 s of silence');
  assert.equal(r.fights[0].kind, 'combat'); assert.equal(r.fights[0].name, 'Orc');
}
// 9. the average item level only looks at the worn pieces, not at enchants or gems
assert.equal(gearLevels('[(100,300,(7961,0,0),(13333,13692,6652),()),(101,310,(),(),(5555,0))]'), 305);
// 10. Windows line endings are accepted
{
  const r = run([start(1) + '\r', dmg(2, A, 'Alice', BOSS, 'Test Boss', 'Bolt', 700) + '\r', end(11, 1) + '\r']);
  assert.equal(r.fights[0].players[0].dmg, 700);
}
console.log('BrokenLogs parser: all checks passed');
