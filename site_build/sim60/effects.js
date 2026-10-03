// Item effects (data/effects.json, exported from the beta client tables by wow_sim60_effects.py): "Equip:" lines, set bonuses,
// on-use trinkets and "Chance on hit" procs. Two steps:
//   resolveEffects(...)  at character build time: equipped item ids -> flat passive stats (attack power, spell power, stats, mana
//                        per 5 s, hit, crit) plus a serialisable list of on-use buffs and procs for the engine;
//   attachEffects(sim)   at fight time: schedules the on-use effects and wires the procs.
// What is simulated: attack power / spell power / stat / mp5 / hit / crit passives, damage and damage-over-time procs, attack power,
// spell power and haste buffs, mana and energy restores, on-use buffs and damage. Everything else (resistances, defensive procs,
// movement, stuns, utility) is listed as ignored. ASSUMED: the client gives a proc chance for set bonuses only, so a weapon's
// "Chance on hit" uses PPM_ASSUMED procs per minute of weapon speed (Classic style), and a proc with no chance at all uses 5%.
import { gainMana, applyDot } from './spells.js';

export const PPM_ASSUMED = 1.0, FALLBACK_CHANCE = 0.05;
const SCHOOL_RE = /Physical|Fire|Frost|Nature|Shadow|Arcane|Holy/;
const STAT_BY_MISC = { 0: 'str', 1: 'agi', 2: 'sta', 3: 'int', 4: 'spi' };
const HASTE_AURAS = new Set([138, 140, 319]);

const fire = (e) => e.effect === 6;

// what a spell does when it lands (first matching effect wins), or null
export function payloadOf(spell) {
  const ef = spell.effects || [];
  const school = (SCHOOL_RE.exec(spell.desc || '') || ['Physical'])[0];
  const d = ef.find((e) => e.effect === 2 && e.base > 0);
  if (d) return { kind: 'damage', dmg: d.base, school, magic: school !== 'Physical' };
  const dot = ef.find((e) => fire(e) && e.aura === 3 && e.period_ms > 0 && e.base > 0);
  if (dot && spell.duration_ms > 0) { const ticks = Math.max(1, Math.round(spell.duration_ms / dot.period_ms)); return { kind: 'dot', perTick: dot.base, ticks, interval: dot.period_ms / 1000, school, magic: school !== 'Physical' }; }
  const buff = {};
  for (const e of ef) {
    if (!fire(e)) continue;
    if ((e.aura === 99 || e.aura === 124) && e.base > 0) buff.ap = Math.max(buff.ap || 0, e.base);
    else if (e.aura === 13 && e.misc[0] === 126 && e.base > 0) buff.sp = e.base;
    else if (HASTE_AURAS.has(e.aura) && e.base > 0) buff.haste = 1 + e.base / 100;
  }
  if (buff.ap || buff.sp || buff.haste) return { kind: 'buff', buff, duration: Math.max(1, spell.duration_ms / 1000) };
  const en = ef.find((e) => e.effect === 30 && e.base > 0);
  if (en) return { kind: 'energize', power: en.misc[0], amount: en.base };
  return null;
}

function passiveOf(spell, out, caster) {
  let any = false;
  const ef = spell.effects || [];
  const hasAp = ef.some((e) => e.aura === 99);
  for (const e of ef) {
    if (!fire(e)) continue;
    if (e.aura === 99 || (e.aura === 124 && !hasAp)) { out.ap += e.base; any = true; }
    else if (e.aura === 13 && e.misc[0] === 126) { out.sp += e.base; any = true; }
    else if (e.aura === 29 && STAT_BY_MISC[e.misc[0]]) { out[STAT_BY_MISC[e.misc[0]]] += e.base; any = true; }
    else if (e.aura === 29 && e.misc[0] === -1) { for (const k of ['str', 'agi', 'sta', 'int', 'spi']) out[k] += e.base; any = true; }
    else if (e.aura === 85) { out.mp5 += e.base; any = true; }
    else if ((e.aura === 54 && !caster) || (e.aura === 55 && caster)) { out.hit += e.base / 100; any = true; }
    else if (e.aura === 290) { out.crit += (e.base + 0.1) / 100; any = true; }
  }
  return any;
}

// event a proc listens to, from the spell's own text: 'hit' (melee/ranged attacks), 'cast' (spell casts) or null (defensive / not simulated)
function eventOf(text) {
  if (/struck|taking damage|when hit|below|at or below|health/i.test(text)) return null;
  if (/spellcast|spell cast|harmful spell|your spells/i.test(text)) return 'cast';
  if (/melee|ranged|autoattack|auto attack|chance on hit|on hit|attacks? /i.test(text)) return 'hit';
  return null;
}

/**
 * fx: effects.json; ids: equipped item ids; weaponOf: { itemId: 'mh' | 'oh' | 'ranged' } for the weapons the engine swings;
 * caster: spell-hit based class. Returns { passive, uses, procs, applied: [{ source, name, status }] }.
 */
export function resolveEffects(fx, ids, weaponOf, caster) {
  const passive = { ap: 0, sp: 0, str: 0, agi: 0, sta: 0, int: 0, spi: 0, mp5: 0, hit: 0, crit: 0 };
  const uses = [], procs = [], applied = [];
  if (!fx) return { passive, uses, procs, applied };
  const note = (source, name, status) => applied.push({ source, name, status });
  const held = new Set(ids);

  const handle = (source, spell, trigger, itemId, isWeapon, cdMs) => {
    if (trigger === 'use' || trigger === 'use_no_delay') {
      const p = payloadOf(spell);
      if (p && (p.kind === 'buff' || p.kind === 'damage')) { uses.push({ source, name: spell.name, payload: p, cd: Math.max(5, (Math.max(cdMs || 0, spell.cooldown_ms || 0) || 120000) / 1000) }); note(source, spell.name, 'simulated'); }
      else note(source, spell.name, 'ignored');
      return;
    }
    if (trigger === 'chance_on_hit') {
      const p = payloadOf(spell);
      const wp = weaponOf[itemId];
      if (!p || !wp) { note(source, spell.name, p ? 'inactive (the weapon does not swing for this class)' : 'ignored'); return; }
      procs.push({ source, name: spell.name, event: 'hit', weapon: wp, ppm: PPM_ASSUMED, payload: p }); note(source, spell.name, 'simulated');
      return;
    }
    // equip / set bonus
    if (passiveOf(spell, passive, caster)) { note(source, spell.name, 'simulated'); return; }
    for (const e of spell.effects || []) {
      if (!(fire(e) && e.aura === 42)) continue;
      const t = e.triggered; if (!t) continue;
      const p = payloadOf(t), ev = eventOf(spell.desc || t.desc || '');
      const wp = isWeapon ? weaponOf[itemId] : null;
      if (!p || !ev || (isWeapon && ev === 'hit' && !wp)) { note(source, t.name || spell.name, 'ignored'); continue; }
      const chance = spell.proc_chance > 1 && spell.proc_chance < 100 ? spell.proc_chance / 100 : null;
      procs.push({ source, name: t.name || spell.name, event: ev, weapon: ev === 'hit' && isWeapon ? wp : null, ppm: chance === null && ev === 'hit' && isWeapon ? PPM_ASSUMED : 0, chance: chance === null ? FALLBACK_CHANCE : chance, payload: p });
      note(source, t.name || spell.name, 'simulated');
    }
  };

  for (const [id, o] of Object.entries(fx.items || {})) {
    if (!held.has(+id)) continue;
    const isWeapon = [13, 15, 17, 21, 22, 26].includes(o.slot);
    for (const x of o.effects) handle('item ' + id, x.spell, x.trigger, +id, isWeapon, x.cooldown_ms);
  }
  for (const s of fx.sets || []) {
    const n = s.items.filter((i) => held.has(i)).length;
    for (const b of s.bonuses) if (b.pieces <= n) handle(s.name + ' (' + b.pieces + ')', b.spell, 'equip', 0, false);
  }
  return { passive, uses, procs, applied };
}

// ---- fight time ----
export function attachEffects(sim) {
  const eff = sim.player.effects;
  if (!eff || (!eff.uses.length && !eff.procs.length)) return;
  const stats = sim.stats;
  const buffAura = (name, p) => {
    const mods = {};
    if (p.buff.ap) mods.apBonus = p.buff.ap;
    if (p.buff.haste) mods.hasteMult = p.buff.haste;
    const sp = p.buff.sp || 0;
    return sim.addAura({ name, duration: p.duration, mods, onApply: sp ? () => { stats.sp += sp; } : null, onExpire: sp ? () => { stats.sp -= sp; } : null });
  };
  const mit = (p, d) => (p.magic ? d * (1 - (sim.target.spellMitigation || 0)) * (sim.target.spellTaken || 1) : sim.mitigate(d, true));
  const landed = (p) => {
    if (p.magic) return sim.rng() < 1 - (sim.target.spellMiss !== undefined ? sim.target.spellMiss : 0.17) + (sim.player.resource === 'mana' ? stats.hit || 0 : 0);
    return sim.rng() >= Math.max(0, sim.table.miss - sim.hitFrac());
  };
  // returns a function that applies one payload
  const makeApply = (name, p) => {
    if (p.kind === 'buff') { const a = buffAura(name, p); return () => { sim.entry(name).casts++; a.apply(); }; }
    if (p.kind === 'damage') return () => { const e = sim.entry(name); e.casts++; if (!landed(p)) { e.misses++; return; } sim.record(name, mit(p, p.dmg), 'hit'); };
    if (p.kind === 'dot') return () => { const e = sim.entry(name); e.casts++; if (!landed(p)) { e.misses++; return; } applyDot(sim, name, mit(p, p.perTick * p.ticks), p.ticks, p.interval); };
    if (p.kind === 'energize') return () => {
      sim.entry(name).casts++;
      if (p.power === 0 && sim.manaMax) gainMana(sim, p.amount);
      else if ((p.power === 3 && sim.player.resource === 'energy') || (p.power === 1 && sim.player.resource === 'rage')) sim.gainRage(p.amount);
    };
    return () => {};
  };
  eff.uses.forEach((u, i) => {
    const run = makeApply(u.name, u.payload);
    const loop = () => { run(); sim.schedule(u.cd, loop); };
    sim.schedule(0.2 + 0.01 * i, loop);
  });
  const hitProcs = eff.procs.filter((p) => p.event === 'hit'), castProcs = eff.procs.filter((p) => p.event === 'cast');
  const compiled = (list) => list.map((p) => ({ p, run: makeApply(p.name, p.payload) }));
  const hp = compiled(hitProcs), cp = compiled(castProcs);
  const speedOf = (w) => (w === 'ranged' ? (sim.rw && sim.rw.speed) : w === 'oh' ? (sim.player.weapons[1] && sim.player.weapons[1].speed) : (sim.player.weapons[0] && sim.player.weapons[0].speed)) || 2.5;
  if (hp.length) sim.procs.push((s, outcome, source, isOH) => {
    if (outcome === 'miss' || outcome === 'dodge') return;
    for (const { p, run } of hp) {
      if (p.weapon === 'oh' && !isOH) continue;
      if (p.weapon === 'mh' && isOH) continue;
      const chance = p.ppm ? p.ppm * speedOf(p.weapon) / 60 : p.chance;
      if (s.rng() < chance) run();
    }
  });
  if (cp.length) sim.spellProcs.push((s, name, outcome) => {
    if (outcome === 'miss') return;
    for (const { p, run } of cp) if (s.rng() < p.chance) run();
  });
}
