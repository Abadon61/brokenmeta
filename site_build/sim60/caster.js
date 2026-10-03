// Generic caster kit used by the Priest, Shaman and Druid casters: a spell table built from the client's rank records, a
// priority function and a few modifier hooks. Mana, the five-second rule, spell hit/crit/mitigation, crit-capable damage over
// time and channels come from spells.js. ASSUMED values are flagged where the kits define them.
import { setupMana, gainMana, spendMana, spiritRegenPerSec, beginCast, resolveSpell, applyDotCrit, SPELL_GCD, SPELL_CRIT_MULT } from './spells.js';

// ---- rank record (data/spells60.json: top / extra) -> spell definition ----
export function levelPoints(e, rec) {
  const lvl = rec.max_level ? Math.min(60, rec.max_level) : 60;
  return e.base + e.per_level * Math.max(0, lvl - rec.spell_level);
}
export function fromRank(rec, over = {}) {
  const s = { cost: rec.cost ? rec.cost.amount : 0, cast: rec.cast_ms / 1000, cd: rec.cooldown_ms / 1000, duration: rec.duration_ms / 1000 };
  const d = rec.effects.find((e) => e.effect === 2 && e.base > 0);
  if (d) { const mid = levelPoints(d, rec); s.direct = { min: mid * (1 - d.variance / 2), max: mid * (1 + d.variance / 2), coeff: d.sp_coeff }; }
  const p = rec.effects.find((e) => e.effect === 6 && (e.aura === 3 || e.aura === 53) && e.period_ms > 0);
  if (p && rec.duration_ms > 0) { s.dot = { perTick: levelPoints(p, rec), ticks: Math.max(1, Math.round(rec.duration_ms / p.period_ms)), interval: p.period_ms / 1000, coeff: p.sp_coeff }; }
  return Object.assign(s, over);
}
export function pickRank(data, cls, key, name) {
  const g = data && data[cls];
  return (g && ((key && g.top && g.top[key]) || (name && g.extra && g.extra[name]))) || null;
}

// ---- helpers shared by the kits ----
export function spellHit(sim, m) {
  const t = sim.target;
  return sim.rng() < Math.min(0.99, 1 - t.spellMiss + sim.stats.hit + (m.hit || 0));
}
export function tickDamage(sim, name, raw, m) {
  const t = sim.target, c = Math.max(0, Math.min(1, sim.stats.crit + (m.crit || 0))), crit = sim.rng() < c;
  const d = raw * (m.dmg || 1) * (1 - t.spellMitigation) * t.spellTaken * (crit ? 1 + (SPELL_CRIT_MULT - 1) * (1 + (m.critBonus || 0)) : 1);
  sim.record(name, d, crit ? 'crit' : 'hit');
  if (sim.spellProcs.length) for (let i = 0; i < sim.spellProcs.length; i++) sim.spellProcs[i](sim, name, crit ? 'crit' : 'hit');
  return { crit, dmg: d };
}

/**
 * def: {
 *   name, build, S: spell table, baseMana(sim) -> max mana, keep: share of spirit regen kept while casting,
 *   setup(sim), mods(sim, s, kind) -> {hit,crit,dmg,critBonus} (kind: 'direct' | 'dot' | 'channel'),
 *   castTime(sim, s) -> seconds, cost(sim, s) -> mana, beforeCast(sim, s), afterHit(sim, s, outcome, dmg), onTick(sim, s, tick),
 *   choose(sim) -> spell | null, offGcd(sim) (cooldowns that cost no global cooldown), items: { potion, gem }
 * }
 */
export function makeCaster(def) {
  const b = def.build, S = def.S;
  return {
    name: def.name, build: b, S,
    setup(sim) {
      sim.player.resource = 'mana'; sim.kitBuild = b;
      const st = sim.stats;
      setupMana(sim, { manaMax: def.baseMana(sim), mp5: st.mp5 || 0, spiritRegen: spiritRegenPerSec({ int: st.int, spi: st.spi }), castingFraction: def.keep ? def.keep(sim) : 0 });
      sim.critBase = 0; sim.regenMult = 1; sim.cdAt = Object.create(null);
      def.setup(sim);
    },
    start() {},
    rotate(sim) {
      const now = sim.now, rem = sim.fightLen - now;
      if (sim.casting) return sim.casting.endsAt - now;
      const it = def.items || {};
      if (b.usePotion && it.potion && now >= (sim.cdAt.potion || 0) && sim.mana <= sim.manaMax - (it.potion.min + it.potion.max) / 2 && rem > 20) {
        sim.cdAt.potion = now + it.potion.cd; sim.entry('Mana Potion').casts++; gainMana(sim, it.potion.min + (it.potion.max - it.potion.min) * sim.rng());
      }
      if (b.useGem && it.gem && now >= (sim.cdAt.gem || 0) && sim.mana <= sim.manaMax - (it.gem.min + it.gem.max) / 2 && rem > 15) {
        sim.cdAt.gem = now + it.gem.cd; sim.entry('Mana Gem').casts++; gainMana(sim, it.gem.min + (it.gem.max - it.gem.min) * sim.rng());
      }
      if (def.offGcd) def.offGcd(sim);
      const gcdLeft = sim.gcdReadyAt - now;
      if (gcdLeft > 1e-9) return gcdLeft;
      const s = def.choose(sim);
      if (!s) return 0.25;
      const cost = def.cost(sim, s);
      if (cost > sim.mana) return 0.5;               // out of mana: wait for the regeneration
      if (s.cd) sim.cdAt[s.name] = now + s.cd;
      if (def.beforeCast) def.beforeCast(sim, s);
      return cast(sim, def, s, cost);
    },
  };
}

function cast(sim, def, s, cost) {
  const ct = def.castTime(sim, s);
  if (s.channel) return channel(sim, def, s, cost);
  return beginCast(sim, s, ct, cost, () => {
    let landed = true, outcome = 'hit', dmg = 0;
    if (s.direct) {
      const m = def.mods(sim, s, 'direct');
      const raw = s.direct.min + (s.direct.max - s.direct.min) * sim.rng() + (sim.stats.sp + (sim.spBonus || 0)) * s.direct.coeff;
      const r = resolveSpell(sim, s.name, raw, m);
      landed = r.outcome !== 'miss'; outcome = r.outcome; dmg = r.dmg;
    } else if (s.dot) {
      const m = def.mods(sim, s, 'dot');
      const e = sim.entry(s.name);
      if (!spellHit(sim, m)) { e.misses++; landed = false; outcome = 'miss'; }
    }
    if (landed && s.dot) casterDot(sim, def, s);
    if (def.afterHit) def.afterHit(sim, s, outcome, dmg);
  });
}

function casterDot(sim, def, s) {
  const d = s.dot, m = def.mods(sim, s, 'dot');
  const per = (d.perTick * (s.dotScale || 1) + (sim.stats.sp + (sim.spBonus || 0)) * d.coeff) * m.dmg * (1 - sim.target.spellMitigation) * sim.target.spellTaken;
  const critChance = Math.max(0, Math.min(1, sim.stats.crit + (m.crit || 0)));
  const critMult = 1 + (SPELL_CRIT_MULT - 1) * (1 + (m.critBonus || 0));
  const ticks = s.dotTicks ? s.dotTicks(sim) : d.ticks;
  applyDotCrit(sim, s.name, per, ticks, d.interval, () => { const c = sim.rng() < critChance; return { crit: c, mult: c ? critMult : 1 }; }, def.onTick ? (r) => def.onTick(sim, s, r) : null);
}

function channel(sim, def, s, cost) {
  const ch = s.channel, m = def.mods(sim, s, 'channel');
  const total = def.channelTicks ? def.channelTicks(sim, s) : ch.ticks;
  const interval = ch.interval / sim.hasteMult();
  const dur = interval * total;
  sim.gcdReadyAt = sim.now + SPELL_GCD; spendMana(sim, cost); sim.entry(s.name).casts++;
  sim.casting = { name: s.name, endsAt: sim.now + dur };
  const hit = spellHit(sim, m);
  if (!hit) sim.entry(s.name).misses++;
  for (let i = 1; i <= total; i++) sim.schedule(interval * i, () => {
    if (!hit) return;
    const raw = ch.perTick + (sim.stats.sp + (sim.spBonus || 0)) * ch.coeff;
    const r = tickDamage(sim, s.name, raw, def.mods(sim, s, 'channel'));
    if (def.afterHit) def.afterHit(sim, s, r.crit ? 'crit' : 'hit', r.dmg);
  });
  sim.schedule(dur, () => { sim.casting = null; sim.lastCastAt = sim.now; sim.poke(0); });
  return dur;
}
