// Helpers shared by the class kits.
import { OVERPOWER_WINDOW } from './constants.js';

// Special ("yellow") melee attack: two rolls (miss/dodge, then crit), armor-mitigated, recorded under `name`.
export function yellowAttack(sim, name, rawFn, opts = {}) {
  const out = sim.resolveYellow(opts.bonusCrit || 0, opts.canDodge !== false);
  const e = sim.entry(name);
  if (out === 'miss') { e.misses++; if (opts.refund !== false) sim.refundRage(); sim.onMeleeHit('miss', name, false, false); return out; }
  if (out === 'dodge') { e.dodges++; if (opts.refund !== false) sim.refundRage(); sim.overpowerUntil = sim.now + OVERPOWER_WINDOW; sim.onMeleeHit('dodge', name, false, false); return out; }
  let raw = rawFn();
  if (out === 'crit') raw *= sim.critMult((opts.critDmgBonus || 0) + (sim.abilityCritDmg || 0));
  const dmg = sim.mitigate(raw * sim.mods.dmgMult * (opts.dmgMult || 1), !opts.magic);
  sim.record(name, dmg, out); sim.onMeleeHit(out, name, false, false);
  return out;
}

// Spend the global cooldown (1.5 s for rage/mana users, 1.0 s for energy users) and run the cast.
export function castGcd(sim, spell, fn, gcd = 1.5) {
  sim.gcdReadyAt = sim.now + gcd; spell.readyAt = sim.now + spell.cd; spell.casts++; sim.entry(spell.name).casts++; fn();
  return sim.gcdReadyAt - sim.now;
}

// Deep Wounds (Forever, talents_arms.go): a crit adds (share x the main hand's average weapon damage, no attack power) to what is still unticked and spreads the sum
// over a full set of four 3-second ticks; the tick timer of a running bleed is kept. Returns the function to call on every crit.
export function makeDeepWounds(sim, avgMh, share) {
  const st = { remaining: 0, per: 0 };
  const tick = () => {
    if (st.remaining <= 0) return;
    st.remaining--; sim.record('Deep Wounds', st.per * sim.mods.dmgMult, 'hit');
    if (st.remaining > 0) sim.schedule(3, tick);
  };
  return () => {
    const outstanding = st.remaining * st.per, wasActive = st.remaining > 0;
    st.remaining = 4; st.per = (outstanding + avgMh * share) / 4;
    if (!wasActive) sim.schedule(3, tick);
  };
}
