// Helpers shared by the class kits.
import { OVERPOWER_WINDOW } from './constants.js';

// Special ("yellow") melee attack: two rolls (miss/dodge, then crit), armor-mitigated, recorded under `name`.
export function yellowAttack(sim, name, rawFn, opts = {}) {
  const out = sim.resolveYellow(opts.bonusCrit || 0, opts.canDodge !== false);
  const e = sim.entry(name);
  if (out === 'miss') { e.misses++; sim.onMeleeHit('miss', name, false, false); return out; }
  if (out === 'dodge') { e.dodges++; sim.overpowerUntil = sim.now + OVERPOWER_WINDOW; sim.onMeleeHit('dodge', name, false, false); return out; }
  let raw = rawFn();
  if (out === 'crit') raw *= sim.critMult(opts.critDmgBonus || 0);
  const dmg = sim.mitigate(raw * sim.mods.dmgMult * (opts.dmgMult || 1), true);
  sim.record(name, dmg, out); sim.onMeleeHit(out, name, false, false);
  return out;
}

// Spend the global cooldown (1.5 s for rage/mana users, 1.0 s for energy users) and run the cast.
export function castGcd(sim, spell, fn, gcd = 1.5) {
  sim.gcdReadyAt = sim.now + gcd; spell.readyAt = sim.now + spell.cd; spell.casts++; sim.entry(spell.name).casts++; fn();
  return sim.gcdReadyAt - sim.now;
}
