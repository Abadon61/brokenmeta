// Re-creates what sim60_bundle.py does (all modules in ONE scope) and runs every kit through it: a name declared twice, or a
// helper that is silently shadowed by another module's helper, only breaks in the bundle, never in the per-module tests.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const py = readFileSync(new URL('../../sim60_bundle.py', import.meta.url), 'utf8');
const ORDER = JSON.parse(py.match(/ORDER = (\[[^\]]*\])/)[1]);
const EXPORTS = py.match(/EXPORTS = \(([\s\S]*?)\)\n/)[1].split('\n').map((l) => l.trim().replace(/^"|"$/g, '').replace(/"\s*$/, '')).join('').replace(/"/g, '');
const strip = (s) => s.replace(/^import[\s\S]*?from\s+['"][^'"]+['"];?[ \t]*\n/gm, '').replace(/^export\s+(const|let|async function|function|class)\b/gm, '$1');
const src = ORDER.map((n) => strip(readFileSync(new URL('../' + n + '.js', import.meta.url), 'utf8').replace(/\r\n/g, '\n'))).join('\n');
const rd = (f) => JSON.parse(readFileSync(new URL('../data/' + f, import.meta.url)));

test('no top-level name is declared twice across the bundled modules', () => {
  const seen = new Map(), dup = [];
  ORDER.forEach((n) => {
    const body = strip(readFileSync(new URL('../' + n + '.js', import.meta.url), 'utf8').replace(/\r\n/g, '\n'));
    for (const m of body.matchAll(/^(?:async\s+)?(?:function|const|let|class)\s+([A-Za-z_$][\w$]*)/gm)) { if (seen.has(m[1])) dup.push(m[1] + ' (' + seen.get(m[1]) + ', ' + n + ')'); else seen.set(m[1], n); }
  });
  assert.deepEqual(dup, []);
});

test('every kit runs inside the single bundled scope', () => {
  const ctx = {}; ctx.self = ctx; vm.createContext(ctx);
  vm.runInContext('(function (root) {\n' + src + '\nroot.Sim60 = { ' + EXPORTS + ' };\n})(self);', ctx);
  const S = ctx.Sim60, data = rd('spells60.json'), fx = rd('effects.json'), tal = rd('talents.json');
  for (const k of Object.keys(S.KITS)) {
    const cls = k.split('_')[0], variant = { shaman_enhancement: 'enhancement', druid_feral: 'feral', warrior_protection: 'protection', paladin_protection: 'protection', druid_bear: 'bear', hunter_melee: 'melee' }[k];
    const casterLike = /^(mage|warlock|priest)_|shaman_elemental|druid_balance/.test(k), ranged = k.startsWith('hunter') && k !== 'hunter_melee', stick = k === 'druid_feral' || k === 'druid_bear';
    const w = casterLike || stick ? [] : ranged ? [{ min: 80, max: 150, speed: 2.6, type: 'gun' }] : k === 'warrior_arms' || k === 'paladin_retribution' ? [{ min: 200, max: 300, speed: 3.4, type: 'two-handed sword', twoHand: true }] : [{ min: 80, max: 150, speed: 2.6, type: 'sword' }, { min: 60, max: 120, speed: 2.4, type: 'sword', offHand: true }];
    const ch = S.buildCharacter({ class: cls, variant, race: 'human', gear: /protection/.test(k) ? [{ slot: 'shield', id: 1, name: 'shield', st: { armor: 1400 } }] : [], weapons: w, buffs: [], consumables: [], debuffs: [], effects: fx });
    const build = S.ranksToBuild(cls, tal[cls], S.ranksFromNames(tal[cls], S.PRESETS[k]));
    const r = S.runBatch({ fightLen: 60, player: ch.player, target: ch.target, kitFactory: () => S.makeKit(k, build, data) }, 20, 1);
    assert.ok(r.mean > 0, k + ' ' + r.mean);
  }
  assert.ok(Object.keys(S.KITS).length >= 20);
});
