// Caster toolkit on top of the shared engine: mana pool and regeneration (five-second rule), timed casts
// with haste, a spell-hit/crit/damage resolver and snapshotting damage-over-time effects. Classic 1.12
// formulas where Forever has no table (ASSUMED, flagged in the kits that use them):
//   spirit regen per second (outside the five-second rule) = 0.009327 * sqrt(Int) * Spirit
//   spell crit multiplier 1.5, global cooldown 1.5 s (not reduced by haste), spell miss 17% vs a level-63 boss.
export const SPELL_GCD = 1.5, SPELL_CRIT_MULT = 1.5, FSR = 5, REGEN_TICK = 2;

export function spiritRegenPerSec(stats) { return 0.009327 * Math.sqrt(Math.max(0, stats.int || 0)) * (stats.spi || 0); }

// opts: { manaMax, mp5, spiritRegen, castingFraction }  (castingFraction = share of spirit regen kept inside the five-second rule)
export function setupMana(sim, opts) {
  sim.manaMax = opts.manaMax; sim.mana = opts.manaMax; sim.lastCastAt = -100; sim.casting = null;
  sim.manaSpent = 0; sim.manaGained = 0; sim.manaOom = 0;
  const per = REGEN_TICK;
  const tick = () => {
    const inFsr = sim.casting !== null || sim.now - sim.lastCastAt < FSR;
    const keep = typeof opts.castingFraction === 'function' ? opts.castingFraction(sim) : (opts.castingFraction || 0);     // a function: Improved Stormstrike keeps 50% for a while
    const spirit = opts.spiritRegen * (sim.regenMult || 1) * (inFsr && !(sim.regenMult > 1) ? keep : 1);
    gainMana(sim, (opts.mp5 / 5 + spirit) * per);
    sim.schedule(per, tick);
  };
  sim.schedule(per, tick);
}
// Demonic / Dark Rune (a raid consumable, ASSUMED Classic values): 900-1500 mana every 2 minutes, its own cooldown apart from the potion and the gem.
// The health it costs is not modelled. Used as soon as it restores its full average.
export const MANA_RUNE = { cd: 120, min: 900, max: 1500 };
export function useRune(sim, b) {
  if (b.useRune === false) return;
  const rem = sim.fightLen - sim.now;
  if (sim.now >= (sim.runeAt || 0) && sim.mana <= sim.manaMax - (MANA_RUNE.min + MANA_RUNE.max) / 2 && rem > 15) {
    sim.runeAt = sim.now + MANA_RUNE.cd; sim.entry('Demonic Rune').casts++;
    gainMana(sim, MANA_RUNE.min + (MANA_RUNE.max - MANA_RUNE.min) * sim.rng());
  }
}
export function gainMana(sim, n) {
  const room = sim.manaMax - sim.mana; if (n > room) n = room;
  if (n > 0) { sim.mana += n; sim.manaGained += n; }
}
export function spendMana(sim, n) { sim.mana -= n; if (sim.mana < 0) sim.mana = 0; sim.manaSpent += n; }

export function castHaste(sim) { return sim.hasteMult(); }

// Run a cast: global cooldown starts now, mana is spent now, the effect lands when the cast finishes.
// spell: { name, gcd?:false } ; castTime in seconds before haste.
export function beginCast(sim, spell, castTime, cost, onFinish) {
  const t = castTime / castHaste(sim);
  if (spell.gcd !== false) sim.gcdReadyAt = sim.now + SPELL_GCD;
  spendMana(sim, cost);
  sim.entry(spell.name).casts++;
  if (t <= 1e-9) { sim.lastCastAt = sim.now; onFinish(); return Math.max(0, sim.gcdReadyAt - sim.now); }
  sim.casting = { name: spell.name, endsAt: sim.now + t };
  sim.schedule(t, () => { sim.casting = null; sim.lastCastAt = sim.now; onFinish(); sim.poke(0); });
  return t;
}

// Direct spell: hit roll, crit roll, mitigation, record. `raw` is the pre-modifier damage.
// m = { hit, crit, dmg, critBonus } supplied by the kit (school talents, auras).
export function resolveSpell(sim, name, raw, m) {
  const t = sim.target, e = sim.entry(name);
  const hit = Math.min(0.99, 1 - t.spellMiss + sim.stats.hit + (m.hit || 0));
  if (sim.rng() >= hit) { e.misses++; return { outcome: 'miss', dmg: 0 }; }
  const c = Math.max(0, Math.min(1, sim.stats.crit + (m.crit || 0)));
  const crit = sim.rng() < c;
  let d = raw * (m.dmg || 1) * (1 - t.spellMitigation) * t.spellTaken;
  if (crit) d *= 1 + (SPELL_CRIT_MULT - 1) * (1 + (m.critBonus || 0));
  sim.record(name, d, crit ? 'crit' : 'hit');
  if (sim.spellProcs.length) for (let i = 0; i < sim.spellProcs.length; i++) sim.spellProcs[i](sim, name, crit ? 'crit' : 'hit');
  return { outcome: crit ? 'crit' : 'hit', dmg: d };
}

// Damage over time: `ticks` equal ticks, snapshotted. A new application of the same effect replaces the old one.
export function applyDot(sim, name, total, ticks, interval) {
  const dots = sim.dots || (sim.dots = Object.create(null));
  const my = (dots[name] = (dots[name] || 0) + 1);
  const per = total / ticks;
  let n = 0;
  const step = () => {
    if (dots[name] !== my) return;
    sim.record(name, per, 'hit'); n++;
    if (n < ticks) sim.schedule(interval, step);
  };
  sim.schedule(interval, step);
}

// Damage over time whose ticks can crit (Forever periodic effects carry can_crit). `perTick` is the snapshot damage of a tick;
// `roll(i)` -> { crit: bool, mult: number } is evaluated at each tick; `onTick(res)` lets a kit react (Nightfall...).
export function applyDotCrit(sim, name, perTick, ticks, interval, roll, onTick) {
  const dots = sim.dots || (sim.dots = Object.create(null));
  const ends = sim.dotEnds || (sim.dotEnds = Object.create(null));
  const my = (dots[name] = (dots[name] || 0) + 1);
  ends[name] = sim.now + ticks * interval;
  let n = 0;
  const step = () => {
    if (dots[name] !== my) return;
    const r = roll(n), d = perTick * r.mult;
    sim.record(name, d, r.crit ? 'crit' : 'hit', true); n++;
    if (onTick) onTick(r);
    if (n < ticks) sim.schedule(interval, step); else ends[name] = 0;
  };
  sim.schedule(interval, step);
}
export function dotActive(sim, name) { return !!(sim.dotEnds && sim.dotEnds[name] > sim.now + 1e-9); }
export function dotLeft(sim, name) { return sim.dotEnds && sim.dotEnds[name] > sim.now ? sim.dotEnds[name] - sim.now : 0; }
export function cancelDot(sim, name) { if (sim.dots && sim.dots[name] !== undefined) sim.dots[name]++; if (sim.dotEnds) sim.dotEnds[name] = 0; }
