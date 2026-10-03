(function (root) {
'use strict';
// ---- rng.js ----
// Small, fast, seedable PRNG (sfc32). Same seed -> same fight, which makes stat-weight and gear
// comparisons use common random numbers (far less noise than independent runs).
function makeRng(seed) {
  let a = 0x9e3779b9 | 0, b = 0x243f6a88 | 0, c = 0xb7e15162 | 0, d = seed | 0;
  function next() {
    a |= 0; b |= 0; c |= 0; d |= 0;
    const t = (((a + b) | 0) + d) | 0;
    d = (d + 1) | 0;
    a = b ^ (b >>> 9);
    b = (c + (c << 3)) | 0;
    c = (c << 21) | (c >>> 11);
    c = (c + t) | 0;
    return (t >>> 0) / 4294967296;
  }
  for (let i = 0; i < 12; i++) next();
  return next;
}

// ---- constants.js ----
// Mechanics constants for a level-60 character against a level-63 raid boss.
// WoW: Forever is Classic-derived (confirmed on every mechanic checked so far: Rage formula, 1.12
// attack table, +hit/+crit as ratings like TBC). Each value below says where it comes from;
// "ASSUMED" = Classic 1.12 value kept until a Forever source exists (flagged on the public page).

const PLAYER_LEVEL = 60;
const BOSS_LEVEL = 63;
const BOSS_DEFENSE = BOSS_LEVEL * 5;          // 315
const BASE_WEAPON_SKILL = PLAYER_LEVEL * 5;   // 300

// Rating conversions at level 60 (Forever items carry critstrkrtng/hitrtng/hastertng/defrtng;
// 14 crit rating = 1% and 10 hit rating = 1% match the beta's own level-20..60 items, e.g. "Quick
// Strike Ring: +14 crit rating", "Blackstone Ring: +10 hit rating"). Haste rating: ASSUMED 10 per 1%.
const RATING_PER_PCT = { crit: 14, hit: 10, haste: 10, defense: 4 };

// Rage conversion value c(level) (community-derived formula, lands on the known 230.6 at level 60).
function rageConversion(level) {
  return 0.0091107836 * level * level + 3.225598133 * level + 4.2652911;
}
const RAGE_CAP = 100;
const HIT_FACTOR = { mh: { normal: 3.5, crit: 7.0 }, oh: { normal: 1.75, crit: 3.5 } };

// Crit damage: Classic melee/ranged 200%, spells 150% (Wowhead "Stats and Attributes", Classic).
const CRIT_MULT_PHYSICAL = 2.0;
const CRIT_MULT_SPELL = 1.5;

// Armor mitigation: DR = armor / (armor + 400 + 85 * attackerLevel), 75% cap (Classic).
function armorDR(armor, attackerLevel = PLAYER_LEVEL) {
  const dr = armor / (armor + 400 + 85 * attackerLevel);
  return Math.max(0, Math.min(0.75, dr));
}

// Melee attack table vs a boss, Classic 1.12 (the formulas the previous level-60 engine of this
// site already used and sourced): with D = defense - weaponSkill (15 at skill 300 vs a lvl-63 boss):
//   miss  = 5% + D*0.1%   if D <= 10,  else 7% + (D-10)*0.4%      -> 9% at D = 15
//   dodge = 5% + D*0.1%                                           -> 6.5%
//   glance chance = 10% + D*2%                                    -> 40% (white swings only)
//   glance damage multiplier ~ U(low, high), low = min(0.91, 1.3-0.05D), high = min(0.99, 1.2-0.03D)
//   crit suppression = 0.2% * D + 1.8%  (ASSUMED Classic: 4.8% at D = 15)
// Dual-wield adds a flat 19% miss to WHITE swings only (specials are unaffected).
function meleeTable(weaponSkill, targetDefense = BOSS_DEFENSE) {
  const D = Math.max(0, targetDefense - weaponSkill);
  const miss = D <= 10 ? 0.05 + D * 0.001 : 0.07 + (D - 10) * 0.004;
  const dodge = 0.05 + D * 0.001;
  const glance = Math.max(0, 0.10 + D * 0.02);
  const low = Math.max(0.01, Math.min(0.91, 1.3 - 0.05 * D));
  const high = Math.max(low, Math.min(0.99, 1.2 - 0.03 * D));
  const critSuppression = D > 0 ? 0.002 * D + 0.018 : 0;
  return { miss, dodge, glance, glanceLow: low, glanceHigh: high, critSuppression };
}
const DUAL_WIELD_MISS_PENALTY = 0.19;
const OVERPOWER_WINDOW = 5.0;
const GCD = 1.5;

// ---- engine.js ----
// Event-driven combat engine (single target, one player). Spec-agnostic: a spec module supplies
// `setup(sim)` (auras, spells, procs) and `rotate(sim)` (priority list). Everything the engine
// models is Classic-derived and documented in constants.js.

// ---- binary min-heap of events ordered by (time, seq) ----
class Heap {
  constructor() { this.a = []; }
  get size() { return this.a.length; }
  push(e) {
    const a = this.a; let i = a.length; a.push(e);
    while (i > 0) {
      const p = (i - 1) >> 1, pe = a[p];
      if (pe.t < e.t || (pe.t === e.t && pe.s < e.s)) break;
      a[i] = pe; i = p;
    }
    a[i] = e;
  }
  pop() {
    const a = this.a, top = a[0], last = a.pop();
    if (a.length) {
      let i = 0; const n = a.length;
      for (;;) {
        let c = 2 * i + 1; if (c >= n) break;
        if (c + 1 < n && (a[c + 1].t < a[c].t || (a[c + 1].t === a[c].t && a[c + 1].s < a[c].s))) c++;
        const ce = a[c];
        if (last.t < ce.t || (last.t === ce.t && last.s < ce.s)) break;
        a[i] = ce; i = c;
      }
      a[i] = last;
    }
    return top;
  }
}

// ---- auras (buffs / debuffs) with stacks, refresh, uptime ----
class Aura {
  constructor(sim, def) {
    this.sim = sim; this.name = def.name; this.duration = def.duration; this.maxStacks = def.maxStacks || 1;
    // mods: additive keys (critBonus, hitBonus, apBonus, ...) scale per stack; multiplicative keys
    // (apMult, hasteMult, dmgMult, spellDmgMult) are raised to the stack count.
    this.mods = def.mods || null;
    this.onApply = def.onApply || null; this.onExpire = def.onExpire || null; this.onStack = def.onStack || null;
    this.stacks = 0; this.endsAt = -1; this.token = 0; this.active = false; this.since = 0; this.uptime = 0;
    this.applications = 0;
  }
  isActive() { return this.active; }
  apply(addStacks = 1, duration = this.duration) {
    const sim = this.sim, now = sim.now;
    const oldStacks = this.stacks;
    this.stacks = Math.min(this.maxStacks, (this.active ? this.stacks : 0) + addStacks);
    this.applications++;
    if (!this.active) { this.active = true; this.since = now; }
    this.endsAt = duration === Infinity ? Infinity : now + duration;
    const my = ++this.token;
    if (this.endsAt !== Infinity) sim.schedule(duration, () => { if (this.token === my) this.expire(); });
    this._applyMods(oldStacks, this.stacks);
    if (this.onApply && oldStacks === 0) this.onApply(this);
    if (this.onStack && this.stacks !== oldStacks) this.onStack(this, this.stacks);
  }
  consumeStack() {
    if (!this.active) return;
    if (this.stacks <= 1) this.expire(); else { const o = this.stacks; this.stacks--; this._applyMods(o, this.stacks); }
  }
  expire() {
    if (!this.active) return;
    const sim = this.sim, o = this.stacks;
    this.active = false; this.stacks = 0; this.token++; this.uptime += sim.now - this.since;
    this._applyMods(o, 0);
    if (this.onExpire) this.onExpire(this);
  }
  _applyMods(from, to) {
    const m = this.mods; if (!m) return;
    const sim = this.sim, hasteBefore = sim.hasteMult();
    for (const k in m) {
      if (k === 'hasteMult' || k === 'dmgMult' || k === 'spellDmgMult' || k === 'apMult') {
        const before = from > 0 ? Math.pow(m[k], from) : 1, after = to > 0 ? Math.pow(m[k], to) : 1;
        sim.mods[k] = sim.mods[k] / before * after;
      } else sim.mods[k] = (sim.mods[k] || 0) + m[k] * (to - from);
    }
    if (m.hasteMult !== undefined) sim.onHasteChange(hasteBefore);
  }
  finish() { if (this.active) { this.uptime += this.sim.now - this.since; this.since = this.sim.now; } }
}

class Sim {
  constructor(cfg) {
    this.cfg = cfg;
    this.fightLen = cfg.fightLen;
    this.rng = makeRng(cfg.seed | 0);
    this.now = 0; this.seq = 0; this.heap = new Heap();
    this.player = cfg.player;                       // {stats:{...}, weapons:[...], level, resource, dualWield}
    this.stats = Object.assign({}, cfg.player.stats);     // per-run copy: temporary buffs (item effects) adjust it
    this.level = cfg.player.level || PLAYER_LEVEL;
    this.target = cfg.target;                       // {armor, defense, executeFrac}
    this.table = meleeTable(this.stats.weaponSkill || 300, cfg.target.defense);
    this.dr = armorDR(cfg.target.armor);
    this.rageC = rageConversion(this.level);
    // dynamic modifiers (auras & talents write into this)
    this.mods = { critBonus: 0, hitBonus: 0, apBonus: 0, apMult: 1, hasteMult: 1, dmgMult: 1, spellDmgMult: 1, critDmgBonus: 0 };
    this.rage = 0; this.rageCap = RAGE_CAP; this.rageWasted = 0; this.rageGained = 0;
    this.gcdReadyAt = 0;
    this.dmg = Object.create(null); this.total = 0;
    this.swings = [];
    this.mhQueued = null;                           // on-next-swing ability (Heroic Strike / Cleave)
    this.overpowerUntil = -1;
    this.auras = []; this.spells = []; this.procs = [];
    this.rotateAt = Infinity; this.rotateToken = 0;
    this.spellProcs = [];
    this.spec = cfg.spec; this.spec.setup(this);
    attachEffects(this);
  }

  // -------- scheduling --------
  schedule(delay, fn) { const e = { t: this.now + delay, s: ++this.seq, fn }; if (e.t <= this.fightLen + 1e-9) this.heap.push(e); return e; }
  poke(delay = 0) {     // ask the rotation to run (deduped; keeps the earliest request)
    const t = this.now + delay;
    if (t >= this.rotateAt - 1e-12) return;
    this.rotateAt = t; const my = ++this.rotateToken;
    this.schedule(delay, () => { if (this.rotateToken === my) { this.rotateAt = Infinity; this._rotate(); } });
  }
  _rotate() {
    const wait = this.spec.rotate(this);
    if (wait !== undefined && wait !== null && wait < Infinity) this.poke(Math.max(1e-6, wait));
  }

  addAura(def) { const a = new Aura(this, def); this.auras.push(a); return a; }
  addSpell(def) { const s = Object.assign({ readyAt: 0, casts: 0 }, def); this.spells.push(s); return s; }

  // -------- derived stats --------
  hasteMult() { return (this.stats.haste || 1) * this.mods.hasteMult; }
  ap() { return (this.stats.ap + this.mods.apBonus) * this.mods.apMult; }
  critChance(extra = 0) {
    const c = this.stats.crit + this.mods.critBonus + extra - this.table.critSuppression;
    return c < 0 ? 0 : c > 1 ? 1 : c;
  }
  hitFrac() { return this.stats.hit + this.mods.hitBonus; }
  targetHealthPct() { return Math.max(0, 1 - this.now / this.fightLen); }
  inExecute() { return this.targetHealthPct() <= (this.target.executeFrac ?? 0.2); }

  // -------- resources --------
  gainRage(n) {
    this.rageGained += n;
    const room = this.rageCap - this.rage;
    if (n > room) { this.rageWasted += n - room; n = room; }
    this.rage += n;
    this.poke(0);
  }
  spendRage(n) { this.rage -= n; if (this.rage < 0) this.rage = 0; }

  // -------- damage bookkeeping --------
  entry(source) {
    let e = this.dmg[source];
    if (!e) e = this.dmg[source] = { dmg: 0, hits: 0, crits: 0, misses: 0, dodges: 0, glances: 0, casts: 0 };
    return e;
  }
  record(source, amount, kind) {
    const e = this.entry(source);
    e.dmg += amount; this.total += amount;
    if (kind === 'crit') { e.crits++; e.hits++; } else if (kind === 'glance') { e.glances++; e.hits++; } else e.hits++;
  }
  mitigate(raw, physical) { return physical ? raw * (1 - this.dr) : raw; }

  // -------- melee resolution --------
  // White swing: ONE roll against the table (miss, dodge, glance, crit, hit).
  resolveWhite(isOffHand, bonusCrit = 0) {
    const t = this.table, r = this.rng();
    // Dual-wield adds 19% to the white miss chance BEFORE +hit is subtracted (so the cap is 28%).
    let miss = t.miss - this.hitFrac();
    if (this.player.dualWield) miss += DUAL_WIELD_MISS_PENALTY - (isOffHand ? (this.mods.ohHitBonus || 0) : 0);
    if (miss < 0) miss = 0;
    if (r < miss) return 'miss';
    if (r < miss + t.dodge) return 'dodge';
    if (r < miss + t.dodge + t.glance) return 'glance';
    const crit = this.critChance(bonusCrit);
    if (r < miss + t.dodge + t.glance + crit) return 'crit';
    return 'hit';
  }
  // Special ("yellow") attack: roll 1 miss/dodge, roll 2 crit. Cannot glance.
  resolveYellow(bonusCrit = 0, canDodge = true) {
    const t = this.table;
    let miss = t.miss - this.hitFrac(); if (miss < 0) miss = 0;
    const r = this.rng();
    if (r < miss) return 'miss';
    if (canDodge && r < miss + t.dodge) return 'dodge';
    return this.rng() < this.critChance(bonusCrit) ? 'crit' : 'hit';
  }

  weaponRoll(w) { return w.min + (w.max - w.min) * this.rng(); }
  critMult(extra = 0) { return CRIT_MULT_PHYSICAL + this.mods.critDmgBonus + extra; }

  // A melee/ranged outcome hook: spec & procs react (Flurry, Unbridled Wrath, weapon enchants...).
  onMeleeHit(outcome, source, isOffHand, isWhite) {
    for (let i = 0; i < this.procs.length; i++) this.procs[i](this, outcome, source, isOffHand, isWhite);
  }

  // -------- auto attacks --------
  startAutoAttacks() {
    const ws = this.player.weapons;
    for (let i = 0; i < ws.length; i++) {
      const sw = { i, w: ws[i], next: 0, token: 0 };
      this.swings.push(sw);
      this._scheduleSwing(sw, ws[i].speed / this.hasteMult());
    }
  }
  _scheduleSwing(sw, delay) {
    sw.next = this.now + delay; const my = ++sw.token;
    this.schedule(delay, () => { if (sw.token === my) this._swing(sw); });
  }
  onHasteChange(oldMult) {
    const nm = this.hasteMult();
    if (nm === oldMult) return;
    for (const sw of this.swings) {
      if (sw.next > this.now) this._scheduleSwing(sw, (sw.next - this.now) * oldMult / nm);
    }
  }
  _swing(sw) {
    const isOH = !!sw.w.offHand;
    if (!isOH && this.mhQueued) {
      const spell = this.mhQueued; this.mhQueued = null;
      if (this.rage >= spell.cost()) spell.onSwing(this, sw); else this.whiteAttack(sw);
    } else this.whiteAttack(sw);
    this._scheduleSwing(sw, sw.w.speed / this.hasteMult());
    this.poke(0);
  }
  whiteAttack(sw) {
    const isOH = !!sw.w.offHand, w = sw.w, name = isOH ? 'White (off-hand)' : 'White (main hand)';
    const outcome = this.resolveWhite(isOH);
    const e = this.entry(name);
    if (outcome === 'miss') { e.misses++; this.onMeleeHit('miss', 'white', isOH, true); return; }
    if (outcome === 'dodge') { e.dodges++; this.overpowerUntil = this.now + OVERPOWER_WINDOW; this.onMeleeHit('dodge', 'white', isOH, true); return; }
    let raw = this.weaponRoll(w) + this.ap() / 14 * w.speed;
    if (isOH) raw *= 0.5 + (this.mods.ohDmgBonus || 0);
    let kind = 'hit';
    if (outcome === 'glance') { raw *= this.table.glanceLow + (this.table.glanceHigh - this.table.glanceLow) * this.rng(); kind = 'glance'; }
    else if (outcome === 'crit') { raw *= this.critMult(); kind = 'crit'; }
    const dmg = this.mitigate(raw * this.mods.dmgMult, true);
    this.record(name, dmg, kind);
    if (this.player.resource === 'rage') this.rageFromHit(dmg, w.speed, isOH, kind === 'crit');
    this.onMeleeHit(kind, 'white', isOH, true);
  }
  // Classic rage formula: R = 15*d/(4c) + f*s/2, capped at 15*d/c.
  rageFromHit(dmg, speed, isOH, crit) {
    const f = (isOH ? HIT_FACTOR.oh : HIT_FACTOR.mh)[crit ? 'crit' : 'normal'];
    const c = this.rageC;
    let r = 15 * dmg / (4 * c) + f * speed / 2;
    const cap = 15 * dmg / c; if (r > cap) r = cap;
    if (isOH && this.mods.ohRageMult) r *= this.mods.ohRageMult;
    this.gainRage(r);
  }

  // -------- spells --------
  canCast(s) {
    return this.now >= s.readyAt - 1e-9 && this.now >= this.gcdReadyAt - 1e-9 && this.rage >= s.cost();
  }
  startGcd() { this.gcdReadyAt = this.now + GCD; }

  // -------- run --------
  run() {
    this.startAutoAttacks();
    if (this.spec.start) this.spec.start(this);
    this.poke(0);
    const heap = this.heap;
    while (heap.size) {
      const e = heap.pop();
      if (e.t > this.fightLen) break;
      this.now = e.t; e.fn();
    }
    this.now = this.fightLen;
    for (const a of this.auras) a.finish();
    return this;
  }
}

// ---- run.js ----
// Batch runner: many fights with seeds base+i (common random numbers across configs).
// Split in two so Web Workers can each run a slice and the main thread merges the raw sums.

function runBatchRaw(cfg, iterations, seedBase = 1) {
  const acc = { n: 0, sum: 0, sumSq: 0, by: Object.create(null), up: Object.create(null), rageWasted: 0, rageGained: 0 };
  for (let i = 0; i < iterations; i++) {
    const sim = new Sim(Object.assign({}, cfg, { seed: seedBase + i, spec: cfg.kitFactory() }));
    sim.run();
    const dps = sim.total / cfg.fightLen;
    acc.n++; acc.sum += dps; acc.sumSq += dps * dps;
    for (const k in sim.dmg) {
      const e = sim.dmg[k], t = acc.by[k] || (acc.by[k] = { dmg: 0, hits: 0, crits: 0, misses: 0, dodges: 0, glances: 0, casts: 0 });
      t.dmg += e.dmg; t.hits += e.hits; t.crits += e.crits; t.misses += e.misses; t.dodges += e.dodges; t.glances += e.glances; t.casts += e.casts;
    }
    for (const a of sim.auras) acc.up[a.name] = (acc.up[a.name] || 0) + a.uptime / cfg.fightLen;
    acc.rageWasted += sim.rageWasted; acc.rageGained += sim.rageGained;
  }
  return acc;
}

function mergeRaw(parts) {
  const out = { n: 0, sum: 0, sumSq: 0, by: Object.create(null), up: Object.create(null), rageWasted: 0, rageGained: 0 };
  for (const p of parts) {
    out.n += p.n; out.sum += p.sum; out.sumSq += p.sumSq; out.rageWasted += p.rageWasted; out.rageGained += p.rageGained;
    for (const k in p.by) { const t = out.by[k] || (out.by[k] = { dmg: 0, hits: 0, crits: 0, misses: 0, dodges: 0, glances: 0, casts: 0 }); for (const f in p.by[k]) t[f] += p.by[k][f]; }
    for (const k in p.up) out.up[k] = (out.up[k] || 0) + p.up[k];
  }
  return out;
}

function finalize(raw, fightLen) {
  const n = raw.n, mean = raw.sum / n, variance = Math.max(0, raw.sumSq / n - mean * mean);
  const stdev = Math.sqrt(variance), sem = stdev / Math.sqrt(n);
  const breakdown = {};
  for (const k in raw.by) { const t = raw.by[k]; breakdown[k] = { dps: t.dmg / n / fightLen, hits: t.hits / n, crits: t.crits / n, misses: t.misses / n, dodges: t.dodges / n, glances: t.glances / n, casts: t.casts / n }; }
  const uptimes = {}; for (const k in raw.up) uptimes[k] = raw.up[k] / n;
  return { mean, stdev, sem, iterations: n, breakdown, uptimes, rageWastedPerFight: raw.rageWasted / n, rageGainedPerFight: raw.rageGained / n };
}

function runBatch(cfg, iterations, seedBase = 1) {
  return finalize(runBatchRaw(cfg, iterations, seedBase), cfg.fightLen);
}

// ---- presets.js ----
// Raid buffs, consumables and boss debuffs. Values are Classic 1.12 numbers (ASSUMED: WoW: Forever
// is Classic-derived and its level-60 tooltips are not available yet); the public page flags this.
// Each entry adds to the character through these keys (all optional):
//   str/agi/sta/int/spi  flat primary stats (before multipliers)
//   statMult             multiplies every primary stat (Blessing of Kings: 1.10)
//   ap                   flat attack power         apMult   multiplies final AP
//   crit                 flat crit chance (0.03 = 3%)   hit  flat hit chance
//   haste                haste multiplier (1.0x)        dmgMult  damage multiplier
const BUFFS = {
  battle_shout: { name: 'Battle Shout (rank 7)', ap: 232, assumed: true },
  blessing_of_might: { name: 'Blessing of Might', ap: 185, assumed: true },
  blessing_of_kings: { name: 'Blessing of Kings', statMult: 1.10, assumed: true },
  mark_of_the_wild: { name: 'Mark of the Wild', str: 12, agi: 12, sta: 12, int: 12, spi: 12, assumed: true },
  strength_of_earth: { name: 'Strength of Earth Totem', str: 77, assumed: true },
  grace_of_air: { name: 'Grace of Air Totem', agi: 77, assumed: true },
  leader_of_the_pack: { name: 'Leader of the Pack', crit: 0.03, meleeOnly: true, assumed: true },
  blessing_of_wisdom: { name: 'Greater Blessing of Wisdom', mp5: 40 },        // 40 mana per 5 s: Forever client value
  mana_spring_totem: { name: 'Mana Spring Totem', mp5: 62, assumed: true },                     // Classic rank 3 (25 per 2 s), ASSUMED
  arcane_intellect: { name: 'Arcane Brilliance (Arcane Intellect)', int: 31, assumed: true },
  moonkin_aura: { name: 'Moonkin Aura', spCrit: 0.03, assumed: true },
  trueshot_aura: { name: 'Trueshot Aura', ap: 100, assumed: true },
  dragonslayer: { name: 'Rallying Cry of the Dragonslayer', crit: 0.05, ap: 140, assumed: true },
  songflower: { name: 'Songflower Serenade', crit: 0.05, str: 15, agi: 15, assumed: true },
  dire_maul_tribute: { name: 'Fengus\' Ferocity', ap: 200, assumed: true },
};

const CONSUMABLES = {
  elixir_mongoose: { name: 'Elixir of the Mongoose', agi: 25, crit: 0.02, meleeOnly: true, assumed: true },
  greater_arcane_elixir: { name: 'Greater Arcane Elixir', sp: 35, assumed: true },
  flask_supreme_power: { name: 'Flask of Supreme Power', sp: 150, assumed: true },
  brilliant_wizard_oil: { name: 'Brilliant Wizard Oil', sp: 36, spCrit: 0.01, assumed: true },
  brilliant_mana_oil: { name: 'Brilliant Mana Oil', sp: 25, mp5: 12, assumed: true },
  mageblood_potion: { name: 'Mageblood Potion', mp5: 12, assumed: true },
  juju_power: { name: 'Juju Power', str: 30, assumed: true },
  juju_might: { name: 'Juju Might', ap: 40, assumed: true },
  roids: { name: 'R.O.I.D.S.', str: 25, assumed: true },
  ground_scorpok: { name: 'Ground Scorpok Assay', agi: 25, assumed: true },
  winterfall_firewater: { name: 'Winterfall Firewater', str: 35, assumed: true },
  smoked_dumplings: { name: 'Smoked Desert Dumplings', str: 20, assumed: true },
  dense_stone: { name: 'Dense Sharpening Stone', weaponDmg: 8, critMelee: 0, assumed: true },
};

// Boss debuffs: armor reductions (additive on the boss's armor, floor 0) and the ones that matter for damage.
const DEBUFFS = {
  sunder_armor_5: { name: 'Sunder Armor x5', armor: -2250, assumed: true },
  faerie_fire: { name: 'Faerie Fire', armor: -505, assumed: true },
  curse_of_recklessness: { name: 'Curse of Recklessness', armor: -640, assumed: true },
  curse_of_elements: { name: 'Curse of the Elements', spellTaken: 1.10, assumed: true },
  expose_armor: { name: 'Expose Armor (5 pts)', armor: -1700, assumed: true },
};

const PRESET_CASTER = {
  buffs: ['arcane_intellect', 'blessing_of_kings', 'blessing_of_wisdom', 'mana_spring_totem', 'mark_of_the_wild', 'moonkin_aura', 'dragonslayer', 'songflower'],
  consumables: ['flask_supreme_power', 'greater_arcane_elixir', 'brilliant_wizard_oil', 'mageblood_potion'],
  debuffs: ['curse_of_elements'],
};

const PRESET_HUNTER = {
  buffs: ['battle_shout', 'blessing_of_might', 'blessing_of_kings', 'mark_of_the_wild', 'grace_of_air', 'trueshot_aura', 'dragonslayer', 'songflower'],
  consumables: ['elixir_mongoose', 'ground_scorpok', 'brilliant_mana_oil'],
  debuffs: ['sunder_armor_5', 'faerie_fire'],
};

const PRESET_RAID = {
  buffs: ['battle_shout', 'blessing_of_might', 'blessing_of_kings', 'mark_of_the_wild', 'strength_of_earth', 'grace_of_air', 'leader_of_the_pack'],
  consumables: ['elixir_mongoose', 'juju_power', 'juju_might', 'roids'],
  debuffs: ['sunder_armor_5', 'faerie_fire'],
};

// Racial weapon-skill bonuses (+5 skill with the listed weapon types, Classic).
const RACIAL_SKILL = {
  human: ['sword', 'mace', 'two-handed sword', 'two-handed mace'],
  dwarf: ['mace', 'two-handed mace', 'gun'],
  orc: ['axe', 'two-handed axe', 'fist'],
  troll: ['bow', 'thrown'],
  gnome: ['dagger', 'sword'],
  nightelf: [],
  tauren: [],
  undead: [],
};

// ---- character.js ----
// Turns "base stats + gear + enchants + buffs + consumables + talents" into the player object the
// engine consumes. Also accepts a pre-computed stat block (addon export) via `totals`.

// Level-63 boss vs level-60 caster (Classic, ASSUMED): 17% base spell miss; average partial-resist loss 3.75%.
const TARGET_SPELL_MISS = 0.17, TARGET_SPELL_MITIGATION = 0.0375;

// Level-60 Human base stats per class (str/agi/sta/int/spi) + racial modifiers.
// warrior: Classic 1.12 values, kept as is. Every other class is an ESTIMATE (Classic-style, flagged
// assumed): the Forever planner's sourced LEVEL-30 base (data/wow_items/base_stats_level30.json, race
// removed to Human) pushed to level 60 with L60 = L30 + 1.5 * (L30 - L1). The 1.5 factor is calibrated on
// the Classic warrior (120/80/110/30/46 vs 120/80/110/30/50 known). Shaman has no L30 source: mean growth
// of paladin and druid. The sim page lets the user override them, and the addon import replaces them with
// the real in-game totals.
const BASE_L60_HUMAN = {
  warrior: { str: 120, agi: 80, sta: 110, int: 30, spi: 50 },
  rogue: { str: 79, agi: 131, sta: 74, int: 35, spi: 51 },
  hunter: { str: 55, agi: 126, sta: 89, int: 65, spi: 70 },
  mage: { str: 30, agi: 35, sta: 45, int: 126, spi: 126 },
  priest: { str: 35, agi: 40, sta: 50, int: 120, spi: 127 },
  warlock: { str: 45, agi: 50, sta: 64, int: 115, spi: 116 },
  paladin: { str: 105, agi: 65, sta: 100, int: 70, spi: 77 },
  druid: { str: 64, agi: 60, sta: 70, int: 100, spi: 111 },
  shaman: { str: 84, agi: 63, sta: 85, int: 85, spi: 94 },
};
const RACE_MODS = {
  human: { str: 0, agi: 0, sta: 0, int: 0, spi: 0 },
  dwarf: { str: 5, agi: -4, sta: 1, int: -1, spi: -1 },
  nightelf: { str: -4, agi: 4, sta: 0, int: 0, spi: 0 },
  orc: { str: 3, agi: -3, sta: 1, int: -3, spi: 2 },
  tauren: { str: 5, agi: -4, sta: 1, int: -4, spi: 2 },
  undead: { str: -1, agi: -2, sta: 0, int: -2, spi: 5 },
  gnome: { str: -5, agi: 2, sta: 0, int: 3, spi: 0 },
  troll: { str: 1, agi: 2, sta: 0, int: -4, spi: 1 },
};

const PRIMARY = ['str', 'agi', 'sta', 'int', 'spi'];

// Class formulas (Classic): AP from Strength/Agility, crit from Agility.
const CLASS_RULES = {
  warrior: { apPerStr: 2, apPerAgi: 0, apBase: PLAYER_LEVEL * 3 - 20, agiPerCrit: 20, baseCrit: 0, resource: 'rage' },
  rogue: { apPerStr: 1, apPerAgi: 1, apBase: PLAYER_LEVEL * 2 - 20, agiPerCrit: 29, baseCrit: 0, resource: 'energy' },
  // Casters (Classic): spell crit from Intellect, mana from Intellect. baseMana/intPerCrit are ASSUMED Classic values.
  // Hunter: ranged attack power = 2*level - 10 + Agility, crit from Agility (1 per 53), mana from Intellect (ASSUMED Classic values)
  hunter: { ranged: true, apPerStr: 0, apPerAgi: 1, apBase: PLAYER_LEVEL * 2 - 10, agiPerCrit: 53, baseCrit: 0, resource: 'mana', baseMana: 1300, manaPerInt: 15 },
  // Melee classes with mana (Paladin, Enhancement) and the cat: attack power 2 per Strength (+3 per level for the Paladin), crit from Agility 1/20
  paladin: { manaUser: true, apPerStr: 2, apPerAgi: 0, apBase: PLAYER_LEVEL * 3 - 20, agiPerCrit: 20, baseCrit: 0, resource: 'mana', baseMana: 1250, manaPerInt: 15 },
  shaman_enhancement: { manaUser: true, apPerStr: 2, apPerAgi: 0, apBase: PLAYER_LEVEL * 2 - 20, agiPerCrit: 20, baseCrit: 0, resource: 'mana', baseMana: 1250, manaPerInt: 15 },
  druid_feral: { stick: true, apPerStr: 2, apPerAgi: 1, apBase: PLAYER_LEVEL * 2 - 20, agiPerCrit: 20, baseCrit: 0, resource: 'energy' },
  priest: { caster: true, intPerCrit: 59.2, baseCrit: 0, baseMana: 1300, manaPerInt: 15, resource: 'mana' },       // ASSUMED Classic values
  shaman: { caster: true, intPerCrit: 59.5, baseCrit: 0, baseMana: 1250, manaPerInt: 15, resource: 'mana' },
  druid: { caster: true, intPerCrit: 60, baseCrit: 0, baseMana: 1300, manaPerInt: 15, resource: 'mana' },
  warlock: { caster: true, intPerCrit: 60.6, baseCrit: 0, baseMana: 1200, manaPerInt: 15, resource: 'mana' },   // ASSUMED Classic values
  mage: { caster: true, intPerCrit: 59.5, baseCrit: 0.002, baseMana: 1213, manaPerInt: 15, resource: 'mana' },
};

function sumGear(gear) {
  const t = { sp: 0, mp5: 0, str: 0, agi: 0, sta: 0, int: 0, spi: 0, ap: 0, critRating: 0, hitRating: 0, hasteRating: 0, armor: 0, weaponDmg: 0, skill: 0 };
  for (const it of gear) {
    const s = it.st || {};
    for (const k of PRIMARY) t[k] += s[k] || 0;
    t.ap += s.atkpwr || 0;
    t.critRating += s.critstrkrtng || 0;
    t.hitRating += s.hitrtng || 0;
    t.hasteRating += s.hastertng || 0;
    t.armor += s.armor || 0;
    t.skill += s.skill || 0;
    t.sp += (s.splpwr || 0) + (s.spldmg || 0);
    t.mp5 += s.manargn || 0;
  }
  return t;
}

/**
 * spec: { class:'warrior', race:'human', base?:{...}, gear:[item...], weapons:[{min,max,speed,offHand?,twoHand?,type?}],
 *         buffs:[ids], consumables:[ids], debuffs:[ids], flatCrit?, flatHit?, talentCrit?, talentHit?, totals? }
 */
function buildCharacter(spec) {
  const cls = spec.class || 'warrior', race = spec.race || 'human';
  const rules = CLASS_RULES[spec.variant ? cls + '_' + spec.variant : cls] || CLASS_RULES[cls];
  const base = spec.base || (() => {
    const h = BASE_L60_HUMAN[cls], m = RACE_MODS[race] || RACE_MODS.human, o = {};
    for (const k of PRIMARY) o[k] = h[k] + m[k];
    return o;
  })();
  const gear = sumGear(spec.gear || []);
  // item effects (spec.effects = data/effects.json): passive stats now, on-use buffs and procs handed to the engine
  const fxIds = [...(spec.gear || []).map((g) => g.id), ...(spec.weapons || []).map((w) => w.itemId)].filter(Boolean);
  const weaponOf = {};
  (spec.weapons || []).forEach((w, i) => { if (w.itemId) weaponOf[w.itemId] = rules.ranged ? 'ranged' : (w.offHand || i > 0 ? 'oh' : 'mh'); });
  const fxr = spec.effects ? resolveEffects(spec.effects, fxIds, rules.caster ? {} : weaponOf, !!rules.caster) : null;
  if (fxr) {
    const p = fxr.passive;
    gear.ap += p.ap; gear.sp += p.sp; gear.mp5 += p.mp5;
    for (const k of ['str', 'agi', 'sta', 'int', 'spi']) gear[k] += p[k];
  }
  const allBuffs = [...(spec.buffs || []).map((id) => BUFFS[id]), ...(spec.consumables || []).map((id) => CONSUMABLES[id])].filter(Boolean);

  let statMult = 1, flatAp = gear.ap, buffCrit = fxr ? fxr.passive.crit : 0, buffHit = fxr ? fxr.passive.hit : 0, buffHaste = 1, apMult = 1, buffSp = 0, buffSpCrit = 0, buffMp5 = 0, buffSpHit = 0;
  const prim = {};
  for (const k of PRIMARY) prim[k] = base[k] + gear[k];
  for (const b of allBuffs) {
    for (const k of PRIMARY) if (b[k]) prim[k] += b[k];
    if (b.statMult) statMult *= b.statMult;
    if (b.ap) flatAp += b.ap;
    if (b.crit && !(rules.caster && b.meleeOnly)) buffCrit += b.crit;
    if (b.sp) buffSp += b.sp;
    if (b.spCrit) buffSpCrit += b.spCrit;
    if (b.spHit) buffSpHit += b.spHit;
    if (b.mp5) buffMp5 += b.mp5;
    if (b.hit) buffHit += b.hit;
    if (b.haste) buffHaste *= b.haste;
    if (b.apMult) apMult *= b.apMult;
  }
  for (const k of PRIMARY) prim[k] = Math.floor(prim[k] * statMult);

  let ap, crit, hit, haste;
  if (spec.totals) {                      // pre-computed in game (addon export): trust it
    ({ ap, crit, hit } = spec.totals); haste = spec.totals.haste || 1;
  } else {
    ap = (rules.apBase + prim.str * rules.apPerStr + prim.agi * rules.apPerAgi + flatAp) * apMult;
    crit = prim.agi / rules.agiPerCrit / 100 + rules.baseCrit + gear.critRating / RATING_PER_PCT.crit / 100 + buffCrit + (spec.flatCrit || 0);
    hit = gear.hitRating / RATING_PER_PCT.hit / 100 + buffHit + (spec.flatHit || 0);
    haste = buffHaste * (1 + gear.hasteRating / RATING_PER_PCT.haste / 100);
  }

  if (rules.caster) return buildCaster(spec, rules, prim, gear, fxr, { buffCrit, buffHit, buffHaste, buffSp, buffSpCrit, buffSpHit, buffMp5 });

  const weapons = (spec.weapons || []).map((w) => Object.assign({}, w));
  for (const w of weapons) if (spec.weaponDmgBonus) { w.min += spec.weaponDmgBonus; w.max += spec.weaponDmgBonus; }
  const consDmg = allBuffs.reduce((a, b) => a + (b.weaponDmg || 0), 0);
  for (const w of weapons) { w.min += consDmg; w.max += consDmg; }

  // Weapon skill for the attack table: 300 + racial bonus for the main-hand weapon type + gear skill.
  const mh = weapons[0];
  const racial = (RACIAL_SKILL[race] || []).includes((mh && mh.type) || '') ? 5 : 0;
  const weaponSkill = BASE_WEAPON_SKILL + racial + gear.skill;

  let armor = spec.targetArmor !== undefined ? spec.targetArmor : 3731;
  for (const id of spec.debuffs || []) { const d = DEBUFFS[id]; if (d && d.armor) armor += d.armor; }
  armor = Math.max(0, armor);

  const extra = rules.ranged || rules.manaUser ? { int: prim.int, spi: prim.spi, mana: rules.baseMana + rules.manaPerInt * (prim.int - 20), mp5: gear.mp5 + buffMp5, sp: gear.sp + buffSp } : {};
  return {
    player: {
      level: PLAYER_LEVEL, resource: rules.resource, dualWield: rules.ranged || rules.stick ? false : weapons.length > 1,
      stats: { ap, crit, hit, haste, weaponSkill, str: prim.str, agi: prim.agi, ...extra },
      weapons: rules.ranged || rules.stick ? [] : weapons, ranged: rules.ranged ? weapons[0] : undefined,
      effects: fxr ? { uses: fxr.uses, procs: fxr.procs } : undefined,
    },
    target: { armor, defense: spec.targetDefense || BOSS_DEFENSE, executeFrac: spec.executeFrac ?? 0.2, spellMiss: TARGET_SPELL_MISS, spellMitigation: TARGET_SPELL_MITIGATION, spellTaken: 1 },
    summary: { prim, ap, crit, hit, haste, weaponSkill, armor, gearArmor: gear.armor, mana: extra.mana, mp5: extra.mp5, int: prim.int, effects: fxr ? fxr.applied : [] },
  };
}

// Caster stat block. Spell hit is a separate table from melee hit (Classic: 83% base against a level-63 boss,
// +1% per 1% hit up to 99%), applied by the kit; here `hit` is only the bonus from gear/buffs.
function buildCaster(spec, rules, prim, gear, fxr, b) {
  const totals = spec.totals;
  const sp = totals ? totals.sp : gear.sp + b.buffSp;
  const crit = totals ? totals.crit : prim.int / rules.intPerCrit / 100 + rules.baseCrit + gear.critRating / RATING_PER_PCT.crit / 100 + b.buffCrit + b.buffSpCrit + (spec.flatCrit || 0);
  const hit = totals ? totals.hit : gear.hitRating / RATING_PER_PCT.hit / 100 + b.buffHit + b.buffSpHit + (spec.flatHit || 0);
  const haste = totals ? (totals.haste || 1) : b.buffHaste * (1 + gear.hasteRating / RATING_PER_PCT.haste / 100);
  const mp5 = totals && totals.mp5 !== undefined ? totals.mp5 : gear.mp5 + b.buffMp5;
  const mana = totals && totals.mana ? totals.mana : rules.baseMana + rules.manaPerInt * (prim.int - 20);
  let resist = spec.targetSpellMitigation !== undefined ? spec.targetSpellMitigation : TARGET_SPELL_MITIGATION;
  let taken = 1;
  for (const id of spec.debuffs || []) { const d = DEBUFFS[id]; if (d && d.spellTaken) taken *= d.spellTaken; }
  return {
    player: { level: PLAYER_LEVEL, resource: 'mana', dualWield: false, stats: { sp, crit, hit, haste, int: prim.int, spi: prim.spi, mana, mp5, weaponSkill: BASE_WEAPON_SKILL, ap: 0 }, weapons: [], effects: fxr ? { uses: fxr.uses, procs: fxr.procs } : undefined },
    target: { armor: 0, defense: BOSS_DEFENSE, executeFrac: spec.executeFrac ?? 0.2, spellMitigation: Math.max(0, resist), spellMiss: TARGET_SPELL_MISS, spellTaken: taken },
    summary: { prim, sp, crit, hit, haste, mana, mp5, spirit: prim.spi, int: prim.int, spellMitigation: Math.max(0, resist), effects: fxr ? fxr.applied : [] },
  };
}

// ---- items.js ----
// Item pool helpers: slot mapping, class proficiency, weapon conversion.
// Data comes from data/items.json + data/proficiency.json (exported by wow_sim60_export.py from the
// beta client tables; weapons only carry DPS + speed there, so min/max use a +-25% spread, which
// changes variance but not the mean).

const ARMOR_SLOTS = { head: [1], neck: [2], shoulder: [3], back: [16], chest: [5, 20], wrist: [9], hands: [10], waist: [6], legs: [7], feet: [8] };
const EQUIP_SLOTS = ['head', 'neck', 'shoulder', 'back', 'chest', 'wrist', 'hands', 'waist', 'legs', 'feet', 'ring1', 'ring2', 'trinket1', 'trinket2'];
const SLOT_IDS = { ring1: [11], ring2: [11], trinket1: [12], trinket2: [12] };

const CLASS_KEY = { warrior: 'WARRIOR', paladin: 'PALADIN', hunter: 'HUNTER', rogue: 'ROGUE', priest: 'PRIEST', shaman: 'SHAMAN', mage: 'MAGE', warlock: 'WARLOCK', druid: 'DRUID' };
const ARMOR_TYPES = new Set(['Cloth', 'Leather', 'Mail', 'Plate Mail']);

class ItemPool {
  constructor(itemsJson, proficiencyJson) {
    this.items = itemsJson.items;
    this.byId = new Map(this.items.map((i) => [i.id, i]));
    this.prof = proficiencyJson.classes;
  }
  canEquip(item, cls, level = 60) {
    if ((item.req || 0) > level) return false;
    const p = this.prof[CLASS_KEY[cls]];
    if (!p) return false;
    if (ARMOR_TYPES.has(item.type) || (item.type && p[item.type] !== undefined)) {
      const min = p[item.type];
      return min !== undefined && min <= level;
    }
    return true;                       // rings, trinkets, necks, cloaks: no restriction
  }
  forSlot(slotKey, cls, level = 60) {
    const ids = ARMOR_SLOTS[slotKey] || SLOT_IDS[slotKey];
    return this.items.filter((i) => ids.includes(i.slot) && this.canEquip(i, cls, level));
  }
  weapons(cls, level = 60) {
    const w = { oneHand: [], mainHand: [], offHand: [], twoHand: [], ranged: [] };
    for (const i of this.items) {
      if (!this.canEquip(i, cls, level)) continue;
      if (i.slot === 13) { w.oneHand.push(i); }
      else if (i.slot === 21) w.mainHand.push(i);
      else if (i.slot === 22) w.offHand.push(i);
      else if (i.slot === 17) w.twoHand.push(i);
      else if ((i.slot === 15 || i.slot === 26) && /^(Bows|Guns|Crossbows)$/.test(i.type)) w.ranged.push(i);
    }
    return w;
  }
}

const TYPE_TO_ENGINE = { Swords: 'sword', Maces: 'mace', Axes: 'axe', Daggers: 'dagger', 'Fist Weapons': 'fist', 'Two-Handed Swords': 'two-handed sword', 'Two-Handed Maces': 'two-handed mace', 'Two-Handed Axes': 'two-handed axe', Polearms: 'polearm', Staves: 'staff', Bows: 'bow', Guns: 'gun', Crossbows: 'crossbow' };

// Item -> engine weapon: avg damage per hit = dps * speed, +-25% spread.
function toWeapon(item, offHand = false) {
  const st = item.st || {};
  const speed = st.speed || 2.6, avg = (st.dps || 0) * speed;
  return { min: avg * 0.75, max: avg * 1.25, speed, type: TYPE_TO_ENGINE[item.type] || '', offHand, twoHand: item.slot === 17, itemId: item.id, st };
}

// ---- talents.js ----
// Talent trees (data/talents.json, same data and ordering as the site's calculator) <-> simulator build.
// Only talents with a simulated effect appear in NAME_TO_KEY; everything else is ignored by the engine.

const NAME_TO_KEY = {
  warrior: {
    // Fury
    'Cruelty': 'cruelty', 'Unbridled Wrath': 'unbridledWrath', 'Boundless Rage': 'boundlessRage', 'Dual Wield Specialization': 'dualWieldSpec',
    'Raging Blows': 'ragingBlows', 'Enrage': 'enrage', 'Improved Execute': 'improvedExecute', 'Precision': 'precision', 'Death Wish': 'deathWish',
    'Improved Berserker Rage': 'improvedBerserkerRage', 'Flurry': 'flurry', 'Bloodthirst': 'bloodthirst',
    // Arms
    'Improved Heroic Strike': 'improvedHeroicStrike', 'Improved Rend': 'improvedRend', 'Improved Overpower': 'improvedOverpower',
    'Anger Management': 'angerManagement', 'Deep Wounds': 'deepWounds',
    'Two-Handed Weapon Specialization': 'twoHandSpec', 'Impale': 'impale', 'Weaponmaster': 'weaponmaster', 'Improved Slam': 'improvedSlam',
    'Mortal Strike': 'mortalStrike',
  },
  rogue: {
    'Malice': 'malice', 'Lethality': 'lethality', 'Precision': 'precision', 'Dual Wield Specialization': 'dualWieldSpec',
    'Improved Sinister Strike': 'improvedSinisterStrike', 'Improved Eviscerate': 'improvedEviscerate', 'Flawless Execution': 'flawlessExecution',
    'Blade Flurry': 'bladeFlurry', 'Hack and Slash': 'hackAndSlash', 'Weapon Expertise': 'weaponExpertise', 'Aggression': 'aggression',
    'Adrenaline Rush': 'adrenalineRush', 'Ruthlessness': 'ruthlessness', 'Relentless Strikes': 'relentlessStrikes',
    'Improved Slice and Dice': 'improvedSliceAndDice', 'Seal Fate': 'sealFate', 'Vigor': 'vigor', 'Cold Blood': 'coldBlood', 'Mutilate': 'mutilate',
    'Hemorrhage': 'hemorrhage', 'Opportunity': 'opportunity', 'Quietus': 'quietus', 'Serrated Blades': 'serratedBlades', 'Puncturing Wounds': 'puncturingWounds',
    'Improved Poisons': 'improvedPoisons', 'Vile Poisons': 'vilePoisons',
  },
  paladin: {
    'Conviction': 'conviction', 'Improved Judgement': 'improvedJudgement', 'Sanctified Judgement': 'sanctifiedJudgement', 'Two-Handed Weapon Specialization': 'twoHandSpec', 'Vindication': 'vindication',
    'Vengeance': 'vengeance', 'Seal of Command': 'sealOfCommand', 'Sacred Arbiter': 'sacredArbiter', 'Champion of the Light': 'championOfLight', 'Divine Strength': 'divineStrength',
    'Divine Intellect': 'divineIntellect', 'Benediction': 'benediction', 'Holy Power': 'holyPower', 'Improved Seals': 'improvedSeals', 'Instrument of Law': 'instrumentOfLaw', 'Twist of Light': 'twistOfLight',
  },
  priest: {
    'Shadow Focus': 'shadowFocus', 'Improved Shadow Word: Pain': 'improvedSwp', 'Improved Mind Blast': 'improvedMindBlast', 'Mind Flay': 'mindFlay', 'Improved Mind Flay': 'improvedMindFlay',
    'Shadow Weaving': 'shadowWeaving', 'Darkness': 'darkness', 'Shadowform': 'shadowform', 'Devouring Contagion': 'devouringContagion', 'Twin Disciplines': 'twinDisciplines',
    'Mental Agility': 'mentalAgility', 'Mental Strength': 'mentalStrength', 'Meditation': 'meditation', 'Power Infusion': 'powerInfusion', 'Inner Focus': 'innerFocus',
  },
  shaman: {
    'Convection': 'convection', 'Concussion': 'concussion', 'Reverberation': 'reverberation', 'Call of Flame': 'callOfFlame', 'Elemental Focus': 'elementalFocus',
    'Elemental Alacrity': 'elementalAlacrity', 'Call of Thunder': 'callOfThunder', 'Lightning Overload': 'lightningOverload', 'Elemental Fury': 'elementalFury', 'Lava Burst': 'lavaBurst',
    'Thundering Strikes': 'thunderingStrikes', 'Ancestral Knowledge': 'ancestralKnowledge', 'Flurry': 'flurry', 'Stormstrike': 'stormstrike', 'Maelstrom Weapon': 'maelstromWeapon',
    'Rage of the Farseer': 'rageOfTheFarseer', 'Mental Dexterity': 'mentalDexterity', 'Mental Quickness': 'mentalQuickness', 'Elemental Weapons': 'elementalWeapons',
  },
  druid: {
    'Improved Wrath': 'improvedWrath', 'Genesis': 'genesis', 'Moonglow': 'moonglow', 'Improved Moonfire': 'improvedMoonfire', "Nature's Majesty": 'naturesMajesty', "Nature's Reach": 'naturesReach',
    "Nature's Splendor": 'naturesSplendor', 'Insect Swarm': 'insectSwarm', 'Vengeance': 'vengeance', 'Improved Starfire': 'improvedStarfire', "Nature's Grace": 'naturesGrace', 'Eclipse': 'eclipse',
    'Moonfury': 'moonfury', 'Moonkin Form': 'moonkinForm', 'Naturalist': 'naturalist', 'Ferocity': 'ferocity', 'Shredding Attacks': 'shreddingAttacks', 'Savage Fury': 'savageFury',
    'Sharpened Claws': 'sharpenedClaws', 'Predatory Strikes': 'predatoryStrikes', 'Predatory Instincts': 'predatoryInstincts', 'Rend and Tear': 'rendAndTear', 'Heart of the Wild': 'heartOfTheWild',
    'Leader of the Pack': 'leaderOfThePack',
  },
  hunter: {
    'Lethal Attacks': 'lethalAttacks', 'Efficiency': 'efficiency', 'Careful Aim': 'carefulAim', 'Rapid Killing': 'rapidKilling', 'Improved Arcane Shot': 'improvedArcane', 'Lone Wolf': 'loneWolf',
    'Mortal Shots': 'mortalShots', 'Barrage': 'barrage', 'Ranged Weapon Specialization': 'rangedSpec', 'Improved Stings': 'improvedStings', 'Sniper Shot': 'sniperShot',
    'Surefooted': 'surefooted', 'Lightning Reflexes': 'lightningReflexes', 'Unleashed Fury': 'unleashedFury', 'Ferocity': 'ferocity', 'Frenzy': 'frenzy', 'Bestial Wrath': 'bestialWrath',
    'Focused Fire': 'focusedFire', 'Deadly Aspects': 'deadlyAspects', 'Summon Hawk': 'summonHawk', 'Bestial Discipline': 'bestialDiscipline',
  },
  warlock: {
    'Suppression': 'suppression', 'Improved Corruption': 'improvedCorruption', 'Malediction': 'malediction', 'Improved Life Tap': 'improvedLifeTap', 'Pandemic': 'pandemic',
    'Malevolence': 'malevolence', 'Nightfall': 'nightfall', 'Shadow Mastery': 'shadowMastery', 'Improved Bane of Agony': 'improvedBaneOfAgony', 'Siphon Life': 'siphonLife', 'Wrack': 'wrack',
    'Soul Siphon': 'soulSiphon', 'Improved Shadow Bolt': 'improvedShadowBolt', 'Bane': 'bane', 'Cataclysm': 'cataclysm', 'Aftermath': 'aftermath', 'Ruin': 'ruin', 'Shadowburn': 'shadowburn',
    'Agonizing Flames': 'agonizingFlames', 'Conflagrate': 'conflagrate', 'Fire and Brimstone': 'fireAndBrimstone', 'Shadow and Flame': 'shadowAndFlame', 'Incinerate': 'incinerate',
    'Decimation': 'decimation', 'Demonic Knowledge': 'demonicKnowledge', 'Master Demonologist': 'masterDemonologist', 'Unholy Power': 'unholyPower', 'Improved Imp': 'improvedImp',
    'Fel Vitality': 'felVitality', 'Demonic Sacrifice': 'demonicSacrifice',
  },
  mage: {
    'Arcane Focus': 'arcaneFocus', 'Arcane Concentration': 'arcaneConcentration', 'Arcane Impact': 'arcaneImpact', 'Arcane Meditation': 'arcaneMeditation',
    'Arcane Mind': 'arcaneMind', 'Arcane Instability': 'arcaneInstability', 'Arcane Power': 'arcanePower', 'Presence of Mind': 'presenceOfMind', 'Missile Barrage': 'missileBarrage',
    'Incineration': 'incineration', 'Improved Fireball': 'improvedFireball', 'Ignite': 'ignite', 'Improved Scorch': 'improvedScorch', 'Heating Up': 'heatingUp',
    'Master of Elements': 'masterOfElements', 'Critical Mass': 'criticalMass', 'Fire Power': 'firePower', 'Combustion': 'combustion', 'Pyroblast': 'pyroblast', 'Wake of Fire': 'wakeOfFire',
    'Improved Frostbolt': 'improvedFrostbolt', 'Elemental Precision': 'elementalPrecision', 'Ice Shards': 'iceShards', 'Piercing Ice': 'piercingIce', 'Frost Channeling': 'frostChanneling',
    'Ice Lance': 'iceLance', 'Shatter': 'shatter', 'Fingers of Frost': 'fingersOfFrost', "Winter's Chill": 'wintersChill',
  },
};
// Keys that default to "on" in a hand-made build only through the presets below; a talent absent from the ranks means rank 0.
const ALL_KEYS = (cls) => Object.values(NAME_TO_KEY[cls] || {});

const order = (spec) => spec.talents.slice().sort((a, b) => a.row - b.row || a.col - b.col);

// Same rules as the calculator (js/wow-talents.js): shared points, row gates, prerequisites.
function validateRanks(data, ranks) {
  const byId = {}, bySpec = [];
  data.specs.forEach((s, si) => s.talents.forEach((t) => { byId[t.id] = t; t._spec = si; }));
  const rank = (t) => ranks[t.id] || 0;
  const spentIn = (si, belowRow) => data.specs[si].talents.reduce((n, t) => n + (t.row < belowRow ? rank(t) : 0), 0);
  const gatesOf = (t) => (t.gates && t.gates.length ? t.gates : (t.row > 1 ? [{ through_row: t.row - 1, points: (t.row - 1) * data.rules.points_per_row }] : []));
  const asList = (v) => (!v ? [] : Array.isArray(v) ? v : [v]);
  let total = 0, ok = true; const errors = [];
  for (const id in ranks) {
    const t = byId[id];
    if (!t) { ok = false; errors.push('unknown talent ' + id); continue; }
    if (ranks[id] > t.max_rank) { ok = false; errors.push(t.name.en + ': above max rank'); }
    total += ranks[id];
  }
  data.specs.forEach((s, si) => { bySpec[si] = spentIn(si, 99); });
  for (const id in ranks) {
    const t = byId[id]; if (!t || !ranks[id]) continue;
    if (!gatesOf(t).every((g) => spentIn(t._spec, g.through_row + 1) >= g.points)) { ok = false; errors.push(t.name.en + ': row locked'); }
    const all = asList(t.requires), any = asList(t.requires_any);
    const met = (q) => (ranks[q.id] || 0) >= q.rank;
    if (!all.every(met) || (any.length && !any.some(met))) { ok = false; errors.push(t.name.en + ': prerequisite missing'); }
  }
  if (total > data.rules.total_points) { ok = false; errors.push('more than ' + data.rules.total_points + ' points'); }
  return { ok, total, bySpec, errors };
}

// Calculator share link "#b=<rev>.<tree1 ranks>.<tree2 ranks>.<tree3 ranks>" (one digit per talent, row-major order).
function parseShareHash(data, hash) {
  const m = /^#?b=([0-9a-f]{6})((?:\.[0-9]*)+)$/.exec((hash || '').trim().replace(/^.*#/, '#'));
  if (!m) return { error: 'format' };
  const parts = m[2].slice(1).split('.');
  if (parts.length !== data.specs.length) return { error: 'format' };
  const ranks = {};
  for (let i = 0; i < data.specs.length; i++) {
    const ord = order(data.specs[i]);
    if (parts[i].length !== ord.length) return { error: 'format' };
    for (let j = 0; j < ord.length; j++) { const r = +parts[i][j]; if (r > ord[j].max_rank) return { error: 'format' }; if (r) ranks[ord[j].id] = r; }
  }
  return { ranks, revMatches: m[1] === data.rev };
}

function ranksToBuild(cls, data, ranks) {
  const map = NAME_TO_KEY[cls] || {}, build = {};
  for (const k of Object.values(map)) build[k] = 0;
  data.specs.forEach((s) => s.talents.forEach((t) => { const k = map[t.name.en]; if (k) build[k] = ranks[t.id] || 0; }));
  return build;
}

function ranksFromNames(data, byName) {
  const ranks = {};
  data.specs.forEach((s) => s.talents.forEach((t) => { if (byName[t.name.en]) ranks[t.id] = byName[t.name.en]; }));
  return ranks;
}

// Typical raiding builds (51 points), by talent name. Checked against the tree rules in the tests.
const PRESETS = {
  rogue_combat: {
    'Improved Eviscerate': 3, 'Improved Sinister Strike': 2, 'Lightning Reflexes': 4, 'Precision': 3, 'Puncturing Wounds': 3, 'Flawless Execution': 1,
    'Dual Wield Specialization': 5, 'Blade Flurry': 1, 'Hack and Slash': 5, 'Weapon Expertise': 2, 'Aggression': 3, 'Adrenaline Rush': 1,
    'Malice': 5, 'Ruthlessness': 3, 'Improved Slice and Dice': 3, 'Murder': 2, 'Lethality': 5,
  },
  rogue_assassination: {
    'Malice': 5, 'Ruthlessness': 3, 'Improved Slice and Dice': 3, 'Murder': 2, 'Relentless Strikes': 1, 'Lethality': 5, 'Vile Poisons': 5, 'Cold Blood': 1,
    'Mutilate': 1, 'Vigor': 2, 'Seal Fate': 3,
    'Improved Eviscerate': 3, 'Improved Sinister Strike': 2, 'Lightning Reflexes': 4, 'Precision': 3, 'Puncturing Wounds': 3, 'Dual Wield Specialization': 5,
  },
  rogue_subtlety: {
    'Camouflage': 5, 'Opportunity': 2, 'Setup': 3, 'Improved Ambush': 3, 'Ghostly Strike': 1, 'Initiative': 3, 'Improved Distract': 2, 'Serrated Blades': 3,
    'Premeditation': 1, 'Hemorrhage': 1, 'Dirty Deeds': 2, 'Quietus': 5,
    'Improved Eviscerate': 3, 'Improved Sinister Strike': 2, 'Lightning Reflexes': 4, 'Precision': 3, 'Puncturing Wounds': 3, 'Dual Wield Specialization': 5,
  },
  mage_fire: {
    'Wake of Fire': 2, 'Incineration': 3, 'Improved Fireball': 5, 'Ignite': 5, 'Pyroblast': 1, 'Improved Scorch': 3, 'Heating Up': 1, 'Master of Elements': 3,
    'Critical Mass': 3, 'Fire Power': 5, 'Combustion': 1,
    'Elemental Precision': 5, 'Ice Shards': 5, 'Frost Channeling': 3, 'Piercing Ice': 3, 'Improved Frostbolt': 3,
  },
  mage_frost: {
    'Improved Frostbolt': 5, 'Elemental Precision': 5, 'Ice Shards': 5, 'Piercing Ice': 3, 'Frost Channeling': 3, 'Ice Lance': 1, 'Shatter': 3, 'Fingers of Frost': 2, "Winter's Chill": 5,
    'Wand Specialization': 1, 'Arcane Focus': 5, 'Arcane Subtlety': 2, 'Arcane Concentration': 5, 'Arcane Impact': 3, 'Arcane Meditation': 3,
  },
  mage_arcane: {
    'Arcane Focus': 5, 'Improved Channeling': 1, 'Arcane Concentration': 5, 'Arcane Subtlety': 2, 'Arcane Impact': 3, 'Arcane Blast': 1, 'Arcane Meditation': 3, 'Missile Barrage': 1,
    'Presence of Mind': 1, 'Arcane Mind': 5, 'Arcane Instability': 3, 'Arcane Power': 1,
    'Wake of Fire': 2, 'Incineration': 3, 'Improved Fireball': 5, 'Ignite': 5, 'Master of Elements': 3, 'Improved Scorch': 2,
  },
  warlock_affliction: {
    'Suppression': 5, 'Improved Corruption': 5, 'Malediction': 5, 'Pandemic': 3, 'Malevolence': 5, 'Nightfall': 2, 'Siphon Life': 1, 'Shadow Mastery': 5, 'Wrack': 1,
    'Improved Shadow Bolt': 5, 'Bane': 5, 'Cataclysm': 3, 'Ruin': 5, 'Shadowburn': 1,
  },
  warlock_destruction: {
    'Improved Shadow Bolt': 5, 'Bane': 5, 'Cataclysm': 3, 'Aftermath': 5, 'Ruin': 5, 'Shadowburn': 1, 'Agonizing Flames': 3, 'Conflagrate': 1, 'Fire and Brimstone': 3,
    'Shadow and Flame': 5, 'Bane of Havoc': 1, 'Incinerate': 1, 'Suppression': 5, 'Improved Corruption': 5, 'Malediction': 3,
  },
  warlock_demonology: {
    'Demonic Embrace': 5, 'Improved Imp': 3, 'Improved Health Funnel': 2, 'Fel Vitality': 3, 'Demonic Aegis': 2, 'Demonic Sacrifice': 1, 'Master Summoner': 2,
    'Improved Shadow Bolt': 5, 'Bane': 5, 'Cataclysm': 3, 'Aftermath': 5, 'Ruin': 5, 'Shadowburn': 1, 'Agonizing Flames': 3, 'Conflagrate': 1, 'Fire and Brimstone': 3, 'Shadow and Flame': 2,
  },
  hunter_marksmanship: {
    'Lethal Attacks': 5, 'Improved Stings': 3, 'Efficiency': 5, 'Careful Aim': 5, 'Rapid Killing': 2, 'Improved Arcane Shot': 5, 'Lone Wolf': 1, 'Trueshot Aura': 1, 'Mortal Shots': 5,
    'Barrage': 3, 'Ranged Weapon Specialization': 5, 'Sniper Shot': 1, 'Deadly Aspects': 5, 'Endurance Training': 5,
  },
  hunter_beastmastery: {
    'Deadly Aspects': 5, 'Endurance Training': 5, 'Focused Fire': 2, 'Bestial Swiftness': 1, 'Unleashed Fury': 5, 'Ferocity': 5, 'Summon Hawk': 1, 'Intimidation': 1,
    'Bestial Discipline': 2, 'Frenzy': 5, 'Bestial Wrath': 1, 'Lethal Attacks': 5, 'Efficiency': 5, 'Careful Aim': 5, 'Improved Stings': 3,
  },
  hunter_survival: {
    'Improved Tracking': 5, 'Savage Strikes': 2, 'Survivalist': 5, 'Surefooted': 3, 'Clever Traps': 2, "Predator's Edge": 5, 'Resourcefulness': 2, 'Expose Prey': 2,
    'Lightning Reflexes': 5, 'Lacerating Strikes': 1, 'Lethal Attacks': 5, 'Efficiency': 5, 'Careful Aim': 5, 'Improved Stings': 3, 'Hawk Eye': 1,
  },
  priest_shadow: {
    'Shadow Focus': 5, 'Spirit Tap': 5, 'Improved Shadow Word: Pain': 2, 'Improved Mind Blast': 5, 'Mind Flay': 1, 'Improved Mind Flay': 2, 'Vampiric Embrace': 1, 'Shadow Weaving': 3,
    'Devouring Contagion': 2, 'Darkness': 5, 'Shadowform': 1,
    'Twin Disciplines': 5, 'Power in Light': 5, 'Mental Agility': 3, 'Inner Focus': 1, 'Meditation': 3, 'Mental Strength': 2,
  },
  shaman_elemental: {
    'Convection': 5, 'Concussion': 5, 'Reverberation': 5, 'Call of Flame': 3, 'Elemental Focus': 1, 'Elemental Alacrity': 3, 'Call of Thunder': 1, 'Lightning Overload': 3,
    'Elemental Fury': 5, 'Lava Burst': 1, 'Thundering Strikes': 5, 'Ancestral Knowledge': 5, 'Mental Dexterity': 3, 'Guardian Totems': 2, 'Improved Ghost Wolf': 2, 'Improved Lightning Shield': 2,
  },
  druid_balance: {
    'Improved Wrath': 5, 'Genesis': 5, 'Moonglow': 3, 'Improved Moonfire': 2, "Nature's Majesty": 2, "Nature's Reach": 2, "Nature's Splendor": 1, 'Insect Swarm': 1, 'Vengeance': 5,
    'Improved Starfire': 5, "Nature's Grace": 1, 'Eclipse': 3, 'Moonfury': 5, 'Moonkin Form': 1, 'Furor': 5, 'Naturalist': 5,
  },
  paladin_retribution: {
    'Benediction': 5, 'Improved Judgement': 2, 'Conviction': 5, 'Vindication': 3, 'Sanctified Judgement': 3, 'Seal of Command': 1, 'Sacred Arbiter': 1, 'Two-Handed Weapon Specialization': 3,
    'Vengeance': 3, 'Champion of the Light': 3, 'Instrument of Law': 2, 'Twist of Light': 1,
    'Divine Strength': 5, 'Divine Intellect': 5, 'Improved Seals': 3, 'Healing Light': 3, 'Reverence': 3,
  },
  shaman_enhancement: {
    'Thundering Strikes': 5, 'Ancestral Knowledge': 5, 'Mental Dexterity': 3, 'Elemental Weapons': 3, 'Flurry': 5, 'Stormstrike': 1, 'Mental Quickness': 2, 'Improved Stormstrike': 2,
    'Maelstrom Weapon': 5, 'Rage of the Farseer': 1,
    'Convection': 5, 'Concussion': 5, 'Call of Flame': 3, 'Elemental Devastation': 3, 'Elemental Focus': 1, 'Elemental Alacrity': 2,
  },
  druid_feral: {
    'Ferocity': 5, 'Heart of the Wild': 5, 'Thick Hide': 3, 'Shredding Attacks': 3, 'Savage Fury': 2, 'Sharpened Claws': 2, 'Predatory Strikes': 3, 'Leader of the Pack': 1,
    'Predatory Instincts': 2, 'Rend and Tear': 5, 'Berserk': 1,
    'Improved Wrath': 5, 'Genesis': 5, "Nature's Majesty": 2, 'Moonglow': 3, 'Improved Moonfire': 2, "Nature's Reach": 2,
  },
  warrior_fury: {
    'Cruelty': 5, 'Unbridled Wrath': 5, 'Improved Cleave': 3, 'Boundless Rage': 3, 'Dual Wield Specialization': 5, 'Raging Blows': 1, 'Enrage': 5,
    'Improved Execute': 2, 'Precision': 3, 'Death Wish': 1, 'Improved Berserker Rage': 2, 'Flurry': 5, 'Bloodthirst': 1,
    'Improved Heroic Strike': 3, 'Improved Rend': 3, 'Improved Tactical Mastery': 4,
  },
  warrior_arms: {
    'Improved Heroic Strike': 3, 'Improved Rend': 3, 'Improved Overpower': 2, 'Improved Tactical Mastery': 5, 'Anger Management': 1, 'Deep Wounds': 3,
    'Two-Handed Weapon Specialization': 3, 'Impale': 2, 'Sweeping Strikes': 1, 'Weaponmaster': 5, 'Improved Slam': 2, 'Mortal Strike': 1,
    'Cruelty': 5, 'Unbridled Wrath': 5, 'Improved Cleave': 3, 'Boundless Rage': 3,
  },
};

// ---- shared.js ----
// Helpers shared by the class kits.

// Special ("yellow") melee attack: two rolls (miss/dodge, then crit), armor-mitigated, recorded under `name`.
function yellowAttack(sim, name, rawFn, opts = {}) {
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
function castGcd(sim, spell, fn, gcd = 1.5) {
  sim.gcdReadyAt = sim.now + gcd; spell.readyAt = sim.now + spell.cd; spell.casts++; sim.entry(spell.name).casts++; fn();
  return sim.gcdReadyAt - sim.now;
}

// ---- warrior.js ----
// Warrior spec kits: Fury (dual wield) and Arms (two-hander). Numbers come from WoW: Forever's own
// tables/tooltips (data/spells60.json, exported by wow_sim60_export.py) when `data` is passed, and from
// the constants below otherwise. Values marked ASSUMED are Classic 1.12 numbers kept until Forever's
// level-60 table for that spell is sourced.

const WARRIOR = {
  bloodthirst: { cost: 30, cd: 6, apCoeff: 0.35, flat: 48 },           // glossary at L60: 35% AP + 48
  whirlwind: { cost: 25, cd: 10, flat: 0, normSpeed1H: 2.4, normSpeed2H: 3.3 }, // 100% normalized weapon damage (normalization speeds ASSUMED Classic)
  heroicStrike: { cost: 15, flat: 157 },
  slam: { cost: 15, cd: 0, flat: 87, cast: 1.5 },
  overpower: { cost: 5, cd: 5, flat: 35 },
  rend: { cost: 10, total: 147, duration: 21, tick: 3 },
  mortalStrike: { cost: 30, cd: 6, flat: 160, normSpeed2H: 3.3 },      // client table (spell 21553 at L60): weapon damage + 160
  execute: { cost: 15, base: 600, perRage: 15 },                       // ASSUMED Classic rank 5 (600 + 15 per excess Rage)
  deathWish: { cost: 10, cd: 180, duration: 30, dmgMult: 1.2 },
  recklessness: { cd: 1800, duration: 15, crit: 1.0 },                 // ASSUMED Classic effect; cooldown from the client table
  bloodrage: { cd: 60, immediate: 10, overTime: 10, overTimeSec: 10 },
  flurry: { perRank: 0.05, charges: 3, expire: 15 },
  unbridledWrath: { chancePerRank: 0.12 },
  dualWieldSpec: { ohDmgPerRank: 0.05, ohHitPerRank: 0.02 },
  cruelty: { critPerRank: 0.01 },
  precision: { hitPerRank: 0.01 },
  improvedHeroicStrike: { costPerRank: 1 },
  improvedExecute: { cost: [0, 3, 5] },                                // Forever: -3 Rage at rank 1, -5 at rank 2
  improvedOverpower: { critPerRank: 0.25 },                            // Forever: +25% Overpower crit chance per rank
  improvedSlam: { castReductionPerRank: 0.25 },                        // Forever: -0.25 s cast time per rank; no swing delay at rank 2
  boundlessRage: { capPerRank: 10 },
  angerManagement: { interval: 3, amount: 1 },
  deepWounds: { pctPerRank: 0.20, duration: 12, tick: 3 },             // 3 ranks, 60% of average weapon damage over 12 s
  twoHandSpec: { dmgPerRank: 0.01 },
  impale: { critDmgPerRank: 0.10 },
  enrage: { dmgPerRank: 0.02 },                                        // Forever: 30% chance on being hit, +2% Physical damage per rank for 12 s
  weaponmaster: { axeCritPerRank: 0.01, maceArmorPerRank: 0.03, swordExtraAttackPerRank: 0.01 },
  improvedBerserkerRage: { ragePerRank: 5 },                           // Forever: Berserker Rage instantly generates 5 Rage per rank
  berserkerRage: { cd: 30 },
  improvedRend: { bleedPerRank: 0.12 },
};

// Overrides from the exported client data (spells60.json -> warrior.abilities), when available.
function warriorFromData(spells60) {
  const W = JSON.parse(JSON.stringify(WARRIOR));
  const a = spells60 && spells60.warrior && spells60.warrior.abilities;
  if (!a) return W;
  const eff = (id, kind) => (a[id] && a[id].effects || []).find((e) => e.kind === kind);
  const cost = (id) => a[id] && a[id].resource_cost && a[id].resource_cost.rage;
  const bt = eff('warrior_bloodthirst', 'direct_damage');
  if (bt) { W.bloodthirst.apCoeff = bt.ap_coeff; W.bloodthirst.flat = bt.flat || 0; }
  if (cost('warrior_bloodthirst')) W.bloodthirst.cost = cost('warrior_bloodthirst');
  const hs = eff('warrior_heroic_strike', 'flat_bonus_on_next_swing'); if (hs) W.heroicStrike.flat = hs.flat;
  const sl = eff('warrior_slam', 'normalized_weapon_damage'); if (sl) W.slam.flat = sl.flat;
  const op = eff('warrior_overpower', 'normalized_weapon_damage'); if (op) W.overpower.flat = op.flat;
  const rd = eff('warrior_rend', 'periodic_damage'); if (rd) { W.rend.total = rd.total_damage; W.rend.duration = rd.duration_sec; W.rend.tick = rd.tick_interval_sec; }
  const dw = eff('warrior_death_wish', 'self_buff'); if (dw) { W.deathWish.dmgMult = 1 + dw.physical_damage_done_pct; W.deathWish.duration = dw.duration_sec; }
  const fut = (spells60.warrior.future || []).find((f) => f.name === 'Mortal Strike');
  if (fut) {
    const e = fut.rank.effects.find((x) => x.effect === 121);
    if (e) W.mortalStrike.flat = e.base;
    W.mortalStrike.cost = fut.rank.cost.amount / 10; W.mortalStrike.cd = fut.rank.cooldown_ms / 1000;
  }
  const rk = (spells60.warrior.future || []).find((f) => f.name === 'Recklessness');
  if (rk) W.recklessness.cd = rk.rank.cooldown_ms / 1000;
  return W;
}

const FURY_DEFAULT_BUILD = {
  cruelty: 5, unbridledWrath: 5, dualWieldSpec: 5, flurry: 5, precision: 3, improvedHeroicStrike: 0,
  improvedExecute: 2, boundlessRage: 3, ragingBlows: 1, deathWish: 1, bloodthirst: 1, enrage: 5, improvedBerserkerRage: 2,
  enrageUptime: 0.0,            // Enrage needs incoming damage; 0 = off unless the user enters an expected uptime
  hsRageReserve: 0, useRecklessness: true, useDeathWish: true, executePhase: true,
};
const ARMS_DEFAULT_BUILD = {
  cruelty: 5, unbridledWrath: 5, improvedHeroicStrike: 3, improvedOverpower: 2, angerManagement: 1, deepWounds: 3,
  twoHandSpec: 3, impale: 2, weaponmaster: 5, improvedSlam: 2, improvedExecute: 0, boundlessRage: 0, precision: 0,
  mortalStrike: 1, useSlam: true, useRend: false, hsRageReserve: 20, useRecklessness: true, executePhase: true, flurry: 0,
};

// ---- shared helpers ----
function commonSetup(sim, b, W) {
  const mods = sim.mods;
  sim.kitBuild = b;
  sim.player.resource = 'rage';
  sim.rageCap = 100 + W.boundlessRage.capPerRank * (b.boundlessRage || 0);
  mods.critBonus += W.cruelty.critPerRank * (b.cruelty || 0);
  mods.hitBonus += W.precision.hitPerRank * (b.precision || 0);
  sim.reckAura = sim.addAura({ name: 'Recklessness', duration: W.recklessness.duration, mods: { critBonus: W.recklessness.crit } });
  sim.sRK = sim.addSpell({ name: 'Recklessness', cost: () => 0, cd: W.recklessness.cd });
  sim.sBR = sim.addSpell({ name: 'Bloodrage', cost: () => 0, cd: W.bloodrage.cd });
  sim.sEX = sim.addSpell({ name: 'Execute', cost: () => Math.max(0, W.execute.cost - W.improvedExecute.cost[b.improvedExecute || 0]), cd: 0 });
  sim.hsCost = () => Math.max(0, W.heroicStrike.cost - W.improvedHeroicStrike.costPerRank * (b.improvedHeroicStrike || 0));
  sim.sHS = sim.addSpell({
    name: 'Heroic Strike', cost: sim.hsCost,
    onSwing(s, sw) {            // replaces the main-hand white swing
      s.spendRage(s.hsCost()); s.entry('Heroic Strike').casts++;
      yellowAttack(s, 'Heroic Strike', () => s.weaponRoll(sw.w) + s.ap() / 14 * sw.w.speed + W.heroicStrike.flat);
    },
  });
}

// Bloodrage + Execute + Recklessness handled the same way in both kits.
function offGcd(sim, W) {
  const now = sim.now;
  const b = sim.kitBuild;
  if (b && b.improvedBerserkerRage > 0) {
    sim.sBZ = sim.sBZ || sim.addSpell({ name: 'Berserker Rage', cost: () => 0, cd: W.berserkerRage.cd });
    if (now >= sim.sBZ.readyAt) { sim.sBZ.readyAt = now + W.berserkerRage.cd; sim.entry('Berserker Rage').casts++; sim.gainRage(W.improvedBerserkerRage.ragePerRank * b.improvedBerserkerRage); }
  }
  if (now >= sim.sBR.readyAt) {
    sim.sBR.readyAt = now + W.bloodrage.cd; sim.entry('Bloodrage').casts++;
    sim.gainRage(W.bloodrage.immediate);
    const ticks = W.bloodrage.overTimeSec;
    for (let i = 1; i <= ticks; i++) sim.schedule(i, () => sim.gainRage(W.bloodrage.overTime / ticks));
  }
}

function executePhase(sim, W) {
  if (!sim.canCast(sim.sEX)) return null;
  return castGcd(sim, sim.sEX, () => {
    sim.spendRage(sim.sEX.cost());
    const extra = sim.rage; sim.rage = 0;
    yellowAttack(sim, 'Execute', () => W.execute.base + W.execute.perRage * extra);
  });
}

// =============================== FURY ===============================
function furyKit(build = {}, data = null) {
  const b = Object.assign({}, FURY_DEFAULT_BUILD, build), W = warriorFromData(data);
  return {
    name: 'warrior_fury', build: b, W,
    setup(sim) {
      commonSetup(sim, b, W);
      const mods = sim.mods;
      if (sim.player.dualWield) {
        mods.ohDmgBonus = W.dualWieldSpec.ohDmgPerRank * b.dualWieldSpec;
        mods.ohHitBonus = W.dualWieldSpec.ohHitPerRank * b.dualWieldSpec;
      }
      if (b.enrage > 0 && b.enrageUptime > 0) mods.dmgMult *= 1 + W.enrage.dmgPerRank * b.enrage * b.enrageUptime;
      const twoHanded = !sim.player.dualWield && sim.player.weapons[0] && sim.player.weapons[0].twoHand;
      sim._norm = twoHanded ? W.whirlwind.normSpeed2H : W.whirlwind.normSpeed1H;
      sim.twoHanded = twoHanded;

      sim.deathWishAura = sim.addAura({ name: 'Death Wish', duration: W.deathWish.duration, mods: { dmgMult: W.deathWish.dmgMult } });
      sim.flurryAura = sim.addAura({ name: 'Flurry', duration: W.flurry.expire, mods: { hasteMult: 1 + W.flurry.perRank * b.flurry } });
      sim.flurryAura.charges = 0;
      sim.sBT = sim.addSpell({ name: 'Bloodthirst', cost: () => W.bloodthirst.cost, cd: W.bloodthirst.cd });
      sim.sWW = sim.addSpell({ name: 'Whirlwind', cost: () => W.whirlwind.cost, cd: W.whirlwind.cd });
      sim.sDW = sim.addSpell({ name: 'Death Wish', cost: () => W.deathWish.cost, cd: W.deathWish.cd });

      const consume = (s) => { const a = s.flurryAura; if (a.active && --a.charges <= 0) a.expire(); };
      sim.procs.push((s, outcome, source, isOH, isWhite) => {
        if (isWhite) consume(s);
        if (outcome === 'miss' || outcome === 'dodge') return;
        if (outcome === 'crit' && b.flurry > 0) { s.flurryAura.charges = W.flurry.charges; s.flurryAura.apply(1); }
        if (isWhite && b.unbridledWrath > 0 && s.rng() < W.unbridledWrath.chancePerRank * b.unbridledWrath) s.gainRage(twoHanded ? 2 : 1);
      });
    },
    rotate(sim) {
      const now = sim.now;
      offGcd(sim, W);
      const gcdLeft = Math.max(0, sim.gcdReadyAt - now);
      if (gcdLeft > 0) return gcdLeft;
      if (b.useDeathWish && b.deathWish && sim.canCast(sim.sDW)) return castGcd(sim, sim.sDW, () => { sim.spendRage(W.deathWish.cost); sim.deathWishAura.apply(); });
      if (b.useRecklessness && now >= sim.sRK.readyAt) return castGcd(sim, sim.sRK, () => sim.reckAura.apply());
      if (b.executePhase && sim.inExecute()) { const w = executePhase(sim, W); if (w !== null) return w; }
      if (b.bloodthirst && sim.canCast(sim.sBT)) return castGcd(sim, sim.sBT, () => {
        sim.spendRage(W.bloodthirst.cost);
        yellowAttack(sim, 'Bloodthirst', () => sim.ap() * W.bloodthirst.apCoeff + W.bloodthirst.flat);
      });
      if (sim.canCast(sim.sWW)) return castGcd(sim, sim.sWW, () => {
        sim.spendRage(W.whirlwind.cost);
        const mh = sim.player.weapons[0];
        yellowAttack(sim, 'Whirlwind', () => sim.weaponRoll(mh) + sim.ap() / 14 * sim._norm + W.whirlwind.flat);
        if (b.ragingBlows && sim.player.dualWield) {
          const oh = sim.player.weapons[1];
          yellowAttack(sim, 'Whirlwind (Raging Blows)', () => (sim.weaponRoll(oh) + sim.ap() / 14 * sim._norm) * (0.5 + (sim.mods.ohDmgBonus || 0)));
        }
      });
      const reserve = ((sim.sBT.readyAt - now) < 1.5 ? W.bloodthirst.cost : 0) + ((sim.sWW.readyAt - now) < 1.5 ? W.whirlwind.cost : 0) + b.hsRageReserve;
      if (!sim.mhQueued && sim.rage >= sim.sHS.cost() + reserve && sim.player.weapons.length) sim.mhQueued = sim.sHS;
      return Math.max(0.05, Math.min(sim.sBT.readyAt, sim.sWW.readyAt, sim.sDW.readyAt, sim.sBR.readyAt) - now);
    },
  };
}

// =============================== ARMS ===============================
function armsKit(build = {}, data = null) {
  const b = Object.assign({}, ARMS_DEFAULT_BUILD, build), W = warriorFromData(data);
  return {
    name: 'warrior_arms', build: b, W,
    setup(sim) {
      commonSetup(sim, b, W);
      const mods = sim.mods, mh = sim.player.weapons[0] || {};
      sim.twoHanded = !!mh.twoHand;
      if (sim.twoHanded) mods.dmgMult *= 1 + W.twoHandSpec.dmgPerRank * b.twoHandSpec;
      mods.critDmgBonus += W.impale.critDmgPerRank * b.impale;
      // Weaponmaster (Forever): axe/polearm +5% crit; mace/staff ignore 15% armor; sword 5% extra attack.
      if (b.weaponmaster) {
        const t = mh.type || '', r = b.weaponmaster, wm = W.weaponmaster;
        if (/axe|polearm/.test(t)) mods.critBonus += wm.axeCritPerRank * r;
        if (/mace|staff/.test(t)) sim.dr = sim.dr * (1 - wm.maceArmorPerRank * r);   // approximation: x% less armor mitigation
        sim.swordExtraAttack = /sword/.test(t) ? wm.swordExtraAttackPerRank * r : 0;
      }
      if (b.enrage > 0 && b.enrageUptime > 0) mods.dmgMult *= 1 + W.enrage.dmgPerRank * b.enrage * b.enrageUptime;
      sim.sMS = sim.addSpell({ name: 'Mortal Strike', cost: () => W.mortalStrike.cost, cd: W.mortalStrike.cd });
      sim.sOP = sim.addSpell({ name: 'Overpower', cost: () => W.overpower.cost, cd: W.overpower.cd });
      sim.sSL = sim.addSpell({ name: 'Slam', cost: () => W.slam.cost, cd: 0 });
      sim.sRD = sim.addSpell({ name: 'Rend', cost: () => W.rend.cost, cd: 0 });
      sim.rendEndsAt = -1;
      sim.slamUntil = -1;
      // Deep Wounds: a crit applies a bleed worth (20% x ranks) of the average weapon damage over 12 s (refreshes, no stacking).
      sim.deepWoundsAt = -1; sim.deepWoundsTick = 0;
      const applyDeepWounds = (s) => {
        const total = (mh.min + mh.max) / 2 * W.deepWounds.pctPerRank * b.deepWounds * 1.0;
        const ticks = Math.round(W.deepWounds.duration / W.deepWounds.tick);
        const per = total / ticks; s.deepWoundsAt = s.now + W.deepWounds.duration;
        const my = ++s.deepWoundsTick;
        for (let i = 1; i <= ticks; i++) s.schedule(i * W.deepWounds.tick, () => { if (s.deepWoundsTick === my && s.now <= s.deepWoundsAt + 1e-9) s.record('Deep Wounds', per * s.mods.dmgMult, 'hit'); });
      };
      sim.procs.push((s, outcome, source, isOH, isWhite) => {
        if (outcome === 'miss' || outcome === 'dodge') return;
        if (outcome === 'crit' && b.deepWounds > 0) applyDeepWounds(s);
        if (isWhite && b.unbridledWrath > 0 && s.rng() < W.unbridledWrath.chancePerRank * b.unbridledWrath) s.gainRage(sim.twoHanded ? 2 : 1);
        if (isWhite && s.swordExtraAttack && outcome !== 'glance' && s.rng() < s.swordExtraAttack) s.whiteAttack(s.swings[0]);
      });
      if (b.angerManagement) {
        const tick = () => { sim.gainRage(W.angerManagement.amount); sim.schedule(W.angerManagement.interval, tick); };
        sim.schedule(W.angerManagement.interval, tick);
      }
    },
    rotate(sim) {
      const now = sim.now, mh = sim.player.weapons[0], norm = sim.twoHanded ? W.whirlwind.normSpeed2H : 2.4;
      offGcd(sim, W);
      const gcdLeft = Math.max(0, sim.gcdReadyAt - now);
      if (gcdLeft > 0) return gcdLeft;
      if (b.useRecklessness && now >= sim.sRK.readyAt) return castGcd(sim, sim.sRK, () => sim.reckAura.apply());
      if (b.executePhase && sim.inExecute()) { const w = executePhase(sim, W); if (w !== null) return w; }
      if (b.mortalStrike && sim.canCast(sim.sMS)) return castGcd(sim, sim.sMS, () => {
        sim.spendRage(W.mortalStrike.cost);
        yellowAttack(sim, 'Mortal Strike', () => sim.weaponRoll(mh) + sim.ap() / 14 * W.mortalStrike.normSpeed2H + W.mortalStrike.flat);
      });
      if (now <= sim.overpowerUntil && sim.canCast(sim.sOP)) return castGcd(sim, sim.sOP, () => {
        sim.spendRage(W.overpower.cost); sim.overpowerUntil = -1;
        yellowAttack(sim, 'Overpower', () => sim.weaponRoll(mh) + sim.ap() / 14 * norm + W.overpower.flat,
          { canDodge: false, bonusCrit: W.improvedOverpower.critPerRank * (b.improvedOverpower || 0) });
      });
      if (b.useRend && now >= sim.rendEndsAt && sim.canCast(sim.sRD)) return castGcd(sim, sim.sRD, () => {
        sim.spendRage(W.rend.cost); sim.rendEndsAt = now + W.rend.duration;
        const ticks = Math.round(W.rend.duration / W.rend.tick), per = W.rend.total * (1 + W.improvedRend.bleedPerRank * (b.improvedRend || 0)) / ticks, my = sim.rendEndsAt;
        for (let i = 1; i <= ticks; i++) sim.schedule(i * W.rend.tick, () => { if (sim.rendEndsAt === my) sim.record('Rend', per * sim.mods.dmgMult, 'hit'); });
      });
      // Slam: a cast that resets the swing timer; only worth it right after the main-hand swing (weaving).
      if (b.useSlam && sim.canCast(sim.sSL) && sim.swings[0] && sim.swings[0].next - now > mh.speed * 0.55) {
        const cast = Math.max(0.1, W.slam.cast - W.improvedSlam.castReductionPerRank * (b.improvedSlam || 0));
        return castGcd(sim, sim.sSL, () => {
          sim.spendRage(W.slam.cost);
          yellowAttack(sim, 'Slam', () => sim.weaponRoll(mh) + sim.ap() / 14 * norm + W.slam.flat);
          // the swing timer restarts after the cast (Improved Slam removes this penalty)
          if (!(b.improvedSlam >= 2)) sim._scheduleSwing(sim.swings[0], cast + mh.speed / sim.hasteMult());
        });
      }
      const reserve = ((sim.sMS.readyAt - now) < 1.5 ? W.mortalStrike.cost : 0) + b.hsRageReserve;
      if (!sim.mhQueued && sim.rage >= sim.sHS.cost() + reserve && mh) sim.mhQueued = sim.sHS;
      return Math.max(0.05, Math.min(sim.sMS.readyAt, sim.sBR.readyAt, sim.overpowerUntil > now ? sim.sOP.readyAt : Infinity) - now);
    },
  };
}

// ---- rogue.js ----
// Rogue kit (Combat / Assassination / Subtlety share one single-target rotation; the specs differ by
// talents and by the builder they use). Numbers are WoW: Forever's own where we have them (glossary at
// level 60 in data/spells60.json, talent tooltips in data/talents.json); ASSUMED = Classic value kept
// until Forever's table is sourced. Poisons: Forever has no poison table yet, so the damage, proc chances
// and the spell-hit roll are Classic 1.12 values (ASSUMED); only the talent effects come from Forever
// (Improved Poisons, Vile Poisons, Malice on poisons, Mutilate vs poisoned). Not modeled: poison charges,
// Venom, Improved Kidney Shot.

const ROGUE = {
  sinisterStrike: { cost: 45, flat: 68, pct: 1.0 },
  backstab: { cost: 60, flat: 150, pct: 1.5 },
  eviscerate: { cost: 35, table: { 1: [224, 332], 2: [394, 502], 3: [564, 672], 4: [734, 842], 5: [904, 1012] } },
  sliceAndDice: { cost: 25, base: 6, perPoint: 3, haste: 1.2 },
  hemorrhage: { cost: 35, pct: 1.0, pctDagger: 1.45 },          // cost ASSUMED (Classic); damage from the Forever talent tooltip
  mutilate: { cost: 60, pct: 0.75, flat: 17.2, cp: 2 },         // client table + talent tooltip
  bladeFlurry: { cost: 25, cd: 120, duration: 15, haste: 1.2 },  // cost/cooldown ASSUMED (Classic)
  adrenalineRush: { cd: 300, duration: 15, regenMult: 2 },      // cooldown ASSUMED (Classic)
  coldBlood: { cd: 180 },                                       // cooldown ASSUMED (Classic)
  energy: { cap: 100, tick: 2, perTick: 20 },
  normSpeed: { other: 2.4, dagger: 1.7 },                       // Classic weapon-speed normalization (ASSUMED)
  // talents (per rank, from the Forever tooltips)
  improvedSinisterStrike: { costPerRank: 3 }, improvedEviscerate: { perRank: 0.07 }, flawlessExecution: { cost: 10 },
  aggression: { perRank: 0.02 }, malice: { critPerRank: 0.01 }, lethality: { critDmgPerRank: 0.04 },
  precision: { hitPerRank: 0.01 }, dualWieldSpec: { ohPerRank: 0.05 }, relentlessStrikes: { chancePerCp: 0.2, energy: 25 },
  ruthlessness: { perRank: 0.2 }, sealFate: { perRank: 0.2 }, vigor: { perRank: 5 }, improvedSliceAndDice: { perRank: 0.15 },
  hackAndSlash: { perRank: 0.01, armorPerRank: 0.03 }, weaponExpertise: { dodgePerRank: 0.01 },
  opportunity: { perRank: 0.05 }, quietus: { perRank: 0.02, below: 0.35 }, serratedBlades: { armorPerRank: 0.03 },
  puncturingWounds: { bsCritPerRank: 0.10, mutCritPerRank: 0.05 },
  // poisons: Classic 1.12 rank VII / V (ASSUMED). Nature damage: no armor, no AP scaling, 1.5x on crit, resisted like a spell.
  poison: { resist: 0.17, critMult: 1.5, mutilateBonus: 1.2 },
  instantPoison: { min: 146, max: 194, chance: 0.20 },
  deadlyPoison: { total: 136, duration: 12, tick: 3, maxStacks: 5, chance: 0.30 },
  improvedPoisons: { chancePerRank: 0.02 }, vilePoisons: { dmgPerRank: 0.04 },
};

const ROGUE_DEFAULT_BUILD = {
  improvedSinisterStrike: 2, improvedEviscerate: 3, precision: 3, dualWieldSpec: 5, flawlessExecution: 1, bladeFlurry: 1, hackAndSlash: 5,
  weaponExpertise: 2, aggression: 3, adrenalineRush: 1, malice: 5, lethality: 5, ruthlessness: 3, relentlessStrikes: 1, improvedSliceAndDice: 3,
  sealFate: 0, vigor: 0, coldBlood: 0, mutilate: 0, hemorrhage: 0, opportunity: 0, quietus: 0, serratedBlades: 0, puncturingWounds: 0,
  improvedPoisons: 0, vilePoisons: 0, mhPoison: 'instant', ohPoison: 'deadly',   // 'instant' | 'deadly' | 'none'
  builder: 'auto', useCooldowns: true,
};

function rogueKit(build = {}, data = null) {
  const b = Object.assign({}, ROGUE_DEFAULT_BUILD, build), R = JSON.parse(JSON.stringify(ROGUE));
  const a = data && data.rogue && data.rogue.abilities;
  if (a) {
    const ss = a.rogue_sinister_strike, bs = a.rogue_backstab, ev = a.rogue_eviscerate, sd = a.rogue_slice_and_dice;
    const nw = (x) => (x && x.effects || []).find((e) => e.kind === 'normalized_weapon_damage');
    if (nw(ss)) { R.sinisterStrike.flat = nw(ss).flat; R.sinisterStrike.pct = nw(ss).pct; R.sinisterStrike.cost = ss.resource_cost.energy; }
    if (nw(bs)) { R.backstab.flat = nw(bs).flat; R.backstab.pct = nw(bs).pct; R.backstab.cost = bs.resource_cost.energy; }
    const et = ev && ev.effects.find((e) => e.table); if (et) { R.eviscerate.table = et.table; R.eviscerate.cost = ev.resource_cost.energy; }
    const st = sd && sd.effects.find((e) => e.base !== undefined); if (st) { R.sliceAndDice.base = st.base; R.sliceAndDice.perPoint = st.per_point; R.sliceAndDice.cost = sd.resource_cost.energy; }
    const mu = (data.rogue.future || []).find((f) => f.name === 'Mutilate'); if (mu) R.mutilate.cost = mu.rank.cost.amount;
  }
  return {
    name: 'rogue', build: b, R,
    setup(sim) {
      sim.player.resource = 'energy'; sim.kitBuild = b;
      const mods = sim.mods, mh = sim.player.weapons[0] || {}, oh = sim.player.weapons[1];
      sim.rageCap = R.energy.cap + R.vigor.perRank * (b.vigor || 0);
      mods.critBonus += R.malice.critPerRank * b.malice;
      mods.hitBonus += R.precision.hitPerRank * b.precision;
      mods.ohDmgBonus = R.dualWieldSpec.ohPerRank * b.dualWieldSpec;
      sim.table.dodge = Math.max(0, sim.table.dodge - R.weaponExpertise.dodgePerRank * b.weaponExpertise);
      const type = mh.type || '';
      sim.dagger = /dagger/.test(type);
      if (b.hackAndSlash) {
        if (/dagger|fist/.test(type)) mods.critBonus += R.hackAndSlash.perRank * b.hackAndSlash;
        if (/mace/.test(type)) sim.dr *= 1 - R.hackAndSlash.armorPerRank * b.hackAndSlash;
      }
      if (b.serratedBlades) sim.dr *= 1 - R.serratedBlades.armorPerRank * b.serratedBlades;
      sim.extraAttack = (/sword|axe/.test(type) ? R.hackAndSlash.perRank * b.hackAndSlash : 0);
      sim.cp = 0; sim.cbReady = false; sim.arUntil = -1;
      sim.sndAura = sim.addAura({ name: 'Slice and Dice', duration: 30, mods: { hasteMult: R.sliceAndDice.haste } });
      sim.bfAura = sim.addAura({ name: 'Blade Flurry', duration: R.bladeFlurry.duration, mods: { hasteMult: R.bladeFlurry.haste } });
      sim.arAura = sim.addAura({ name: 'Adrenaline Rush', duration: R.adrenalineRush.duration });
      sim.sBF = sim.addSpell({ name: 'Blade Flurry', cost: () => R.bladeFlurry.cost, cd: R.bladeFlurry.cd });
      sim.sAR = sim.addSpell({ name: 'Adrenaline Rush', cost: () => 0, cd: R.adrenalineRush.cd });
      sim.sCB = sim.addSpell({ name: 'Cold Blood', cost: () => 0, cd: R.coldBlood.cd });
      sim.cost = {
        ss: () => Math.max(0, R.sinisterStrike.cost - R.improvedSinisterStrike.costPerRank * b.improvedSinisterStrike),
        bs: () => R.backstab.cost, hemo: () => R.hemorrhage.cost, mut: () => R.mutilate.cost,
        ev: () => Math.max(0, R.eviscerate.cost - (b.flawlessExecution ? R.flawlessExecution.cost : 0)), snd: () => R.sliceAndDice.cost,
      };
      sim.procs.push((s, outcome, source, isOH, isWhite) => {
        if (outcome === 'miss' || outcome === 'dodge') return;
        if (isWhite && sim.extraAttack && outcome !== 'glance' && s.rng() < sim.extraAttack) s.whiteAttack(s.swings[0]);
      });
      // poisons: each landed weapon hit may apply the poison on that weapon
      const dk = sim.deadly = { stacks: 0, endsAt: 0, ticking: false };
      const pmult = () => (1 + R.vilePoisons.dmgPerRank * b.vilePoisons) * sim.mods.spellDmgMult;
      const pcrit = () => Math.min(1, Math.max(0, sim.stats.crit + sim.mods.critBonus));
      const pdmg = (name, base) => {
        const crit = sim.rng() < pcrit();
        const d = base * pmult() * (crit ? R.poison.critMult : 1);
        sim.record(name, d, crit ? 'crit' : 'hit');
      };
      const dkTick = () => {
        if (sim.now > dk.endsAt + 1e-9) { dk.stacks = 0; dk.ticking = false; return; }
        pdmg('Deadly Poison', dk.stacks * R.deadlyPoison.total / (R.deadlyPoison.duration / R.deadlyPoison.tick));
        sim.schedule(R.deadlyPoison.tick, dkTick);
      };
      const applyPoison = (kind) => {
        const p = kind === 'deadly' ? R.deadlyPoison : R.instantPoison;
        if (sim.rng() >= p.chance + R.improvedPoisons.chancePerRank * b.improvedPoisons) return;
        const name = kind === 'deadly' ? 'Deadly Poison' : 'Instant Poison';
        sim.entry(name).casts++;
        if (sim.rng() < R.poison.resist) { sim.entry(name).misses++; return; }
        if (kind === 'instant') { pdmg(name, p.min + (p.max - p.min) * sim.rng()); return; }
        dk.stacks = Math.min(p.maxStacks, dk.stacks + 1); dk.endsAt = sim.now + p.duration;
        if (!dk.ticking) { dk.ticking = true; sim.schedule(p.tick, dkTick); }
      };
      sim.procs.push((s, outcome, source, isOH, isWhite) => {
        if (outcome === 'miss' || outcome === 'dodge') return;
        if (source === 'Eviscerate') return;
        const kind = isOH ? b.ohPoison : b.mhPoison;
        if (kind === 'instant' || kind === 'deadly') applyPoison(kind);
        if (source === 'Mutilate' && b.ohPoison !== 'none' && b.ohPoison !== undefined) applyPoison(b.ohPoison);   // Mutilate hits both weapons
      });
      // energy: +20 every 2 s, doubled by Adrenaline Rush
      const tick = () => { sim.gainRage(R.energy.perTick * (sim.arAura.active ? R.adrenalineRush.regenMult : 1)); sim.nextTick = sim.now + R.energy.tick; sim.schedule(R.energy.tick, tick); };
      sim.nextTick = R.energy.tick; sim.schedule(R.energy.tick, tick);
    },
    start(sim) { sim.rage = sim.rageCap; },
    rotate(sim) {
      const now = sim.now, mh = sim.player.weapons[0], oh = sim.player.weapons[1];
      const gcdLeft = Math.max(0, sim.gcdReadyAt - now);
      const GCD = 1.0, energy = sim.rage;
      const nextTickWait = Math.max(0.05, sim.nextTick - now);
      // choose the builder
      const builder = (() => {
        if (b.builder && b.builder !== 'auto') return b.builder;
        if (b.mutilate && sim.dagger && oh && /dagger/.test(oh.type || '')) return 'mutilate';
        if (sim.dagger) return 'backstab';
        if (b.hemorrhage) return 'hemorrhage';
        return 'ss';
      })();
      const norm = sim.dagger ? R.normSpeed.dagger : R.normSpeed.other;
      const ohMult = () => 0.5 + (sim.mods.ohDmgBonus || 0);
      const nearEnd = (sim.fightLen - now) < 3;
      const qm = () => (sim.targetHealthPct() <= R.quietus.below ? 1 + R.quietus.perRank * (b.quietus || 0) : 1);
      const cbBonus = () => (sim.cbReady ? 1.0 : 0);
      const spendCb = () => { sim.cbReady = false; };
      const addCp = (n, crit, isBuilder) => {
        sim.cp = Math.min(5, sim.cp + n);
        if (crit && isBuilder && b.sealFate && sim.rng() < R.sealFate.perRank * b.sealFate) sim.cp = Math.min(5, sim.cp + 1);
      };
      const lethal = () => 1.0 * R.lethality.critDmgPerRank * b.lethality;

      // cooldowns that cost no GCD
      if (b.useCooldowns) {
        if (b.adrenalineRush && now >= sim.sAR.readyAt) { sim.sAR.readyAt = now + R.adrenalineRush.cd; sim.entry('Adrenaline Rush').casts++; sim.arAura.apply(); }
        if (b.coldBlood && now >= sim.sCB.readyAt && sim.cp >= 4) { sim.sCB.readyAt = now + R.coldBlood.cd; sim.entry('Cold Blood').casts++; sim.cbReady = true; }
      }
      if (gcdLeft > 0) return gcdLeft;
      if (b.useCooldowns && b.bladeFlurry && now >= sim.sBF.readyAt && energy >= R.bladeFlurry.cost) {
        return castGcd(sim, sim.sBF, () => { sim.spendRage(R.bladeFlurry.cost); sim.bfAura.apply(); }, GCD);
      }
      const sndLeft = sim.sndAura.active ? sim.sndAura.endsAt - now : 0;
      // Slice and Dice: keep it up (1+ combo points when down, 2+ to refresh early)
      if (!nearEnd && energy >= sim.cost.snd() && ((sndLeft <= 0 && sim.cp >= 1) || (sndLeft < 2 && sim.cp >= 2))) {
        return castGcd(sim, { name: 'Slice and Dice', cd: 0, readyAt: 0, casts: 0 }, () => {
          sim.spendRage(sim.cost.snd());
          const dur = (R.sliceAndDice.base + R.sliceAndDice.perPoint * sim.cp) * (1 + R.improvedSliceAndDice.perRank * b.improvedSliceAndDice);
          sim.sndAura.apply(1, dur); sim.cp = 0;
        }, GCD);
      }
      // Eviscerate at 5 combo points (or earlier at the very end of the fight)
      if ((sim.cp >= 5 || (nearEnd && sim.cp >= 2)) && energy >= sim.cost.ev()) {
        return castGcd(sim, { name: 'Eviscerate', cd: 0, readyAt: 0, casts: 0 }, () => {
          const cp = sim.cp; sim.spendRage(sim.cost.ev()); sim.cp = 0;
          const tb = R.eviscerate.table[cp];
          const bonus = cbBonus(); spendCb();
          yellowAttack(sim, 'Eviscerate', () => (tb[0] + (tb[1] - tb[0]) * sim.rng()) * (1 + R.improvedEviscerate.perRank * b.improvedEviscerate) * (1 + R.aggression.perRank * b.aggression), { bonusCrit: bonus });
          if (b.ruthlessness && sim.rng() < R.ruthlessness.perRank * b.ruthlessness) sim.cp = Math.min(5, sim.cp + 1);
          if (b.relentlessStrikes) for (let i = 0; i < cp; i++) if (sim.rng() < R.relentlessStrikes.chancePerCp) { sim.gainRage(R.relentlessStrikes.energy); break; }
        }, GCD);
      }
      // never build past 5 combo points, and never starve Slice and Dice: wait for the energy instead
      if (sim.cp >= 5 || (!nearEnd && ((sndLeft <= 0 && sim.cp >= 1) || (sndLeft < 2 && sim.cp >= 2)))) return nextTickWait;
      // builders
      const doBuilder = (name, cost, fn) => {
        if (energy < cost) return null;
        return castGcd(sim, { name, cd: 0, readyAt: 0, casts: 0 }, () => { sim.spendRage(cost); fn(); }, GCD);
      };
      let w = null;
      if (builder === 'ss') w = doBuilder('Sinister Strike', sim.cost.ss(), () => {
        const bonus = cbBonus(); spendCb();
        const o = yellowAttack(sim, 'Sinister Strike', () => (sim.weaponRoll(mh) + sim.ap() / 14 * norm + R.sinisterStrike.flat) * R.sinisterStrike.pct * (1 + R.aggression.perRank * b.aggression) * qm(),
          { bonusCrit: bonus, critDmgBonus: lethal() });
        if (o !== 'miss' && o !== 'dodge') addCp(1, o === 'crit', true);
      });
      else if (builder === 'backstab') w = doBuilder('Backstab', sim.cost.bs(), () => {
        const bonus = cbBonus() + R.puncturingWounds.bsCritPerRank * b.puncturingWounds; spendCb();
        const o = yellowAttack(sim, 'Backstab', () => ((sim.weaponRoll(mh) + sim.ap() / 14 * norm) * R.backstab.pct + R.backstab.flat) * (1 + R.aggression.perRank * b.aggression) * (1 + R.opportunity.perRank * b.opportunity),
          { bonusCrit: bonus, critDmgBonus: lethal() });
        if (o !== 'miss' && o !== 'dodge') addCp(1, o === 'crit', true);
      });
      else if (builder === 'hemorrhage') w = doBuilder('Hemorrhage', sim.cost.hemo(), () => {
        const bonus = cbBonus(); spendCb();
        const o = yellowAttack(sim, 'Hemorrhage', () => (sim.weaponRoll(mh) + sim.ap() / 14 * norm) * (sim.dagger ? R.hemorrhage.pctDagger : R.hemorrhage.pct) * qm(), { bonusCrit: bonus, critDmgBonus: lethal() });
        if (o !== 'miss' && o !== 'dodge') addCp(1, o === 'crit', true);
      });
      else if (builder === 'mutilate') w = doBuilder('Mutilate', sim.cost.mut(), () => {
        const bonus = cbBonus() + R.puncturingWounds.mutCritPerRank * b.puncturingWounds; spendCb();
        const o = yellowAttack(sim, 'Mutilate', () => {
          const mhPart = (sim.weaponRoll(mh) + sim.ap() / 14 * norm) * R.mutilate.pct + R.mutilate.flat;
          const ohPart = ((sim.weaponRoll(oh) + sim.ap() / 14 * norm) * R.mutilate.pct + R.mutilate.flat) * ohMult();
          return (mhPart + ohPart) * (1 + R.opportunity.perRank * b.opportunity) * (sim.deadly.stacks > 0 ? R.poison.mutilateBonus : 1);
        }, { bonusCrit: bonus, critDmgBonus: lethal() });
        if (o !== 'miss' && o !== 'dodge') addCp(R.mutilate.cp, o === 'crit', true);
      });
      if (w !== null) return w;
      // wait for energy: the next tick (or the global cooldown, whichever comes later)
      return nextTickWait;
    },
  };
}

// ---- spells.js ----
// Caster toolkit on top of the shared engine: mana pool and regeneration (five-second rule), timed casts
// with haste, a spell-hit/crit/damage resolver and snapshotting damage-over-time effects. Classic 1.12
// formulas where Forever has no table (ASSUMED, flagged in the kits that use them):
//   spirit regen per second (outside the five-second rule) = 0.009327 * sqrt(Int) * Spirit
//   spell crit multiplier 1.5, global cooldown 1.5 s (not reduced by haste), spell miss 17% vs a level-63 boss.
const SPELL_GCD = 1.5, SPELL_CRIT_MULT = 1.5, FSR = 5, REGEN_TICK = 2;

function spiritRegenPerSec(stats) { return 0.009327 * Math.sqrt(Math.max(0, stats.int || 0)) * (stats.spi || 0); }

// opts: { manaMax, mp5, spiritRegen, castingFraction }  (castingFraction = share of spirit regen kept inside the five-second rule)
function setupMana(sim, opts) {
  sim.manaMax = opts.manaMax; sim.mana = opts.manaMax; sim.lastCastAt = -100; sim.casting = null;
  sim.manaSpent = 0; sim.manaGained = 0; sim.manaOom = 0;
  const per = REGEN_TICK;
  const tick = () => {
    const inFsr = sim.casting !== null || sim.now - sim.lastCastAt < FSR;
    const spirit = opts.spiritRegen * (sim.regenMult || 1) * (inFsr && !(sim.regenMult > 1) ? (opts.castingFraction || 0) : 1);
    gainMana(sim, (opts.mp5 / 5 + spirit) * per);
    sim.schedule(per, tick);
  };
  sim.schedule(per, tick);
}
function gainMana(sim, n) {
  const room = sim.manaMax - sim.mana; if (n > room) n = room;
  if (n > 0) { sim.mana += n; sim.manaGained += n; }
}
function spendMana(sim, n) { sim.mana -= n; if (sim.mana < 0) sim.mana = 0; sim.manaSpent += n; }

function castHaste(sim) { return sim.hasteMult(); }

// Run a cast: global cooldown starts now, mana is spent now, the effect lands when the cast finishes.
// spell: { name, gcd?:false } ; castTime in seconds before haste.
function beginCast(sim, spell, castTime, cost, onFinish) {
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
function resolveSpell(sim, name, raw, m) {
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
function applyDot(sim, name, total, ticks, interval) {
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
function applyDotCrit(sim, name, perTick, ticks, interval, roll, onTick) {
  const dots = sim.dots || (sim.dots = Object.create(null));
  const ends = sim.dotEnds || (sim.dotEnds = Object.create(null));
  const my = (dots[name] = (dots[name] || 0) + 1);
  ends[name] = sim.now + ticks * interval;
  let n = 0;
  const step = () => {
    if (dots[name] !== my) return;
    const r = roll(n), d = perTick * r.mult;
    sim.record(name, d, r.crit ? 'crit' : 'hit'); n++;
    if (onTick) onTick(r);
    if (n < ticks) sim.schedule(interval, step); else ends[name] = 0;
  };
  sim.schedule(interval, step);
}
function dotActive(sim, name) { return !!(sim.dotEnds && sim.dotEnds[name] > sim.now + 1e-9); }
function dotLeft(sim, name) { return sim.dotEnds && sim.dotEnds[name] > sim.now ? sim.dotEnds[name] - sim.now : 0; }
function cancelDot(sim, name) { if (sim.dots && sim.dots[name] !== undefined) sim.dots[name]++; if (sim.dotEnds) sim.dotEnds[name] = 0; }

// ---- effects.js ----
// Item effects (data/effects.json, exported from the beta client tables by wow_sim60_effects.py): "Equip:" lines, set bonuses,
// on-use trinkets and "Chance on hit" procs. Two steps:
//   resolveEffects(...)  at character build time: equipped item ids -> flat passive stats (attack power, spell power, stats, mana
//                        per 5 s, hit, crit) plus a serialisable list of on-use buffs and procs for the engine;
//   attachEffects(sim)   at fight time: schedules the on-use effects and wires the procs.
// What is simulated: attack power / spell power / stat / mp5 / hit / crit passives, damage and damage-over-time procs, attack power,
// spell power and haste buffs, mana and energy restores, on-use buffs and damage. Everything else (resistances, defensive procs,
// movement, stuns, utility) is listed as ignored. ASSUMED: the client gives a proc chance for set bonuses only, so a weapon's
// "Chance on hit" uses PPM_ASSUMED procs per minute of weapon speed (Classic style), and a proc with no chance at all uses 5%.

const PPM_ASSUMED = 1.0, FALLBACK_CHANCE = 0.05;
const SCHOOL_RE = /Physical|Fire|Frost|Nature|Shadow|Arcane|Holy/;
const STAT_BY_MISC = { 0: 'str', 1: 'agi', 2: 'sta', 3: 'int', 4: 'spi' };
const HASTE_AURAS = new Set([138, 140, 319]);

const fire = (e) => e.effect === 6;

// what a spell does when it lands (first matching effect wins), or null
function payloadOf(spell) {
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
function resolveEffects(fx, ids, weaponOf, caster) {
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
function attachEffects(sim) {
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

// ---- caster.js ----
// Generic caster kit used by the Priest, Shaman and Druid casters: a spell table built from the client's rank records, a
// priority function and a few modifier hooks. Mana, the five-second rule, spell hit/crit/mitigation, crit-capable damage over
// time and channels come from spells.js. ASSUMED values are flagged where the kits define them.

// ---- rank record (data/spells60.json: top / extra) -> spell definition ----
function levelPoints(e, rec) {
  const lvl = rec.max_level ? Math.min(60, rec.max_level) : 60;
  return e.base + e.per_level * Math.max(0, lvl - rec.spell_level);
}
function fromRank(rec, over = {}) {
  const s = { cost: rec.cost ? rec.cost.amount : 0, cast: rec.cast_ms / 1000, cd: rec.cooldown_ms / 1000, duration: rec.duration_ms / 1000 };
  const d = rec.effects.find((e) => e.effect === 2 && e.base > 0);
  if (d) { const mid = levelPoints(d, rec); s.direct = { min: mid * (1 - d.variance / 2), max: mid * (1 + d.variance / 2), coeff: d.sp_coeff }; }
  const p = rec.effects.find((e) => e.effect === 6 && (e.aura === 3 || e.aura === 53) && e.period_ms > 0);
  if (p && rec.duration_ms > 0) { s.dot = { perTick: levelPoints(p, rec), ticks: Math.max(1, Math.round(rec.duration_ms / p.period_ms)), interval: p.period_ms / 1000, coeff: p.sp_coeff }; }
  return Object.assign(s, over);
}
function pickRank(data, cls, key, name) {
  const g = data && data[cls];
  return (g && ((key && g.top && g.top[key]) || (name && g.extra && g.extra[name]))) || null;
}

// ---- helpers shared by the kits ----
function spellHit(sim, m) {
  const t = sim.target;
  return sim.rng() < Math.min(0.99, 1 - t.spellMiss + sim.stats.hit + (m.hit || 0));
}
function tickDamage(sim, name, raw, m) {
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
function makeCaster(def) {
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

// ---- mage.js ----
// Mage kit (Fire / Frost / Arcane). Numbers are WoW: Forever's own where the level-60 glossary has them
// (Fireball, Fire Blast, Pyroblast, Frostbolt, Scorch, Frostfire Bolt, Combustion cooldown) and the talent
// tooltips; ASSUMED = Classic 1.12 value kept until Forever's table is sourced:
//   Arcane Missiles / Ice Lance / Arcane Blast damage and costs, Arcane Power and Presence of Mind cooldowns,
//   Evocation, mana potion, spell hit/crit/mana formulas (see spells.js and character.js).
// Simplifications: Arcane Blast is not rotated (the Forever tooltip is ambiguous about which spells its stacks
// boost); Frostfire Bolt takes both the fire and the frost damage modifiers; Ignite stacks are summed;
// no trinkets, set bonuses, Mana Gems, Innervate or movement.

const MAGE = {
  fireball: { name: 'Fireball', schools: ['fire'], cast: 3.5, cost: 410, min: 424.6, max: 541.4, coeff: 1, dot: { total: 60, ticks: 4, interval: 2, coeff: 0 }, heat: true },
  scorch: { name: 'Scorch', schools: ['fire'], cast: 1.5, cost: 150, min: 152, max: 207, coeff: 0.429, heat: true, incin: true },
  fireBlast: { name: 'Fire Blast', schools: ['fire'], cast: 0, cost: 340, min: 416.7, max: 489.3, coeff: 0.429, cd: 8, heat: true, incin: true },
  pyroblast: { name: 'Pyroblast', schools: ['fire'], cast: 6, cost: 440, min: 519.8, max: 646.2, coeff: 1, dot: { total: 212, ticks: 4, interval: 3, coeff: 0.15 } },
  frostbolt: { name: 'Frostbolt', schools: ['frost'], cast: 3, cost: 290, min: 457.2, max: 492.8, coeff: 0.814 },
  frostfireBolt: { name: 'Frostfire Bolt', schools: ['fire', 'frost'], cast: 3, cost: 370, min: 247, max: 337, coeff: 0.814, dot: { total: 57, ticks: 3, interval: 3, coeff: 0 }, heat: true },
  iceLance: { name: 'Ice Lance', schools: ['frost'], cast: 0, cost: 150, min: 173, max: 200, coeff: 0.143, incin: true },       // ASSUMED (Classic TBC-era value)
  arcaneMissiles: { name: 'Arcane Missiles', schools: ['arcane'], cast: 5, cost: 655, total: 1085, coeff: 0.714, ticks: 5 },     // ASSUMED (Classic rank 8)
  arcaneBlast: { name: 'Arcane Blast', schools: ['arcane'], cast: 2.5, cost: 195, min: 470, max: 540, coeff: 0.714, incin: true, stackDmg: 0.10, stackCost: 1.75, maxStacks: 4, dur: 8 },   // damage/cast/cost ASSUMED (TBC-style)
  combustion: { cd: 180 },
  manaGem: { cd: 120, min: 1073, max: 1127 },                                                                                    // ASSUMED (Mana Ruby)
  innervate: { cd: 360, dur: 20, mult: 5 },                                                                                      // ASSUMED (Classic, cast by a druid)
  movement: { period: 30 },
  arcanePower: { cd: 180, duration: 15, dmg: 1.3, cost: 1.3 },                                                                  // cooldown ASSUMED
  presenceOfMind: { cd: 180 },                                                                                                  // cooldown ASSUMED
  evocation: { cd: 480, restore: 0.6, duration: 8 },                                                                            // ASSUMED (Classic)
  manaPotion: { cd: 120, min: 1350, max: 2250 },                                                                                // ASSUMED (Major Mana Potion)
  // talents, per rank (Forever tooltips)
  arcaneFocus: { hit: 0.01 }, arcaneConcentration: { chance: 0.02 }, arcaneImpact: { crit: 0.02 }, arcaneMeditation: { keep: 1 / 6 },
  arcaneMind: { int: 0.02, critBonus: 0.2 }, arcaneInstability: { dmg: 0.01, crit: 0.01 }, missileBarrage: { am: 0.2, ab: 0.4 },
  incineration: { crit: 0.02 }, improvedFireball: { cast: 0.1 }, ignite: { frac: 0.08 }, improvedScorch: { chance: 0.33, perStack: 0.03, max: 5, dur: 30 },
  masterOfElements: { refund: 0.10 }, criticalMass: { crit: 0.02 }, firePower: { dmg: 0.02 }, wakeOfFire: { cd: 1 },
  improvedFrostbolt: { cast: 0.1 }, elementalPrecision: { hit: 0.01 }, iceShards: { critBonus: 0.2 }, piercingIce: { dmg: 0.02 },
  frostChanneling: { cost: 0.05 }, shatter: { crit: 0.5 / 3 }, fingersOfFrost: { chance: 0.15 }, wintersChill: { chance: 0.2, crit: 0.02, max: 5 },
  iceLanceFrozen: 4,
};

const MAGE_DEFAULT_BUILD = {
  arcaneFocus: 0, arcaneConcentration: 0, arcaneImpact: 0, arcaneMeditation: 0, arcaneMind: 0, arcaneInstability: 0, arcanePower: 0, presenceOfMind: 0, missileBarrage: 0,
  incineration: 0, improvedFireball: 0, ignite: 0, improvedScorch: 0, heatingUp: 0, masterOfElements: 0, criticalMass: 0, firePower: 0, combustion: 0, pyroblast: 0, wakeOfFire: 0,
  improvedFrostbolt: 0, elementalPrecision: 0, iceShards: 0, piercingIce: 0, frostChanneling: 0, iceLance: 0, shatter: 0, fingersOfFrost: 0, wintersChill: 0,
  rotation: 'fire', filler: 'auto', useCooldowns: true, usePotion: true, useEvocation: true, useGem: true, innervate: false, movement: 0, arcaneBlast: 0,
};

const mageParseCast = (c) => (typeof c === 'string' ? (c === 'instant' ? 0 : parseFloat(c)) : c);

function mageKit(build = {}, data = null) {
  const b = Object.assign({}, MAGE_DEFAULT_BUILD, build), M = JSON.parse(JSON.stringify(MAGE));
  const a = data && data.mage && data.mage.abilities;
  if (a) {
    const pull = (key, id, dotKey) => {
      const x = a[id]; if (!x) return;
      const d = (x.effects || []).find((e) => e.kind === 'direct_damage'), p = (x.effects || []).find((e) => e.kind === 'periodic_damage');
      const s = M[key];
      if (d) { s.min = d.dmg_range[0]; s.max = d.dmg_range[1]; s.coeff = d.sp_coeff; }
      if (p && s.dot) { s.dot.total = p.total_damage; s.dot.interval = p.tick_interval_sec; s.dot.ticks = Math.round(p.duration_sec / p.tick_interval_sec); if (p.sp_coeff !== undefined) s.dot.coeff = p.sp_coeff; }
      if (x.resource_cost && x.resource_cost.mana) s.cost = x.resource_cost.mana;
      s.cast = mageParseCast(x.cast_time); if (x.cooldown_sec) s.cd = x.cooldown_sec;
    };
    pull('fireball', 'mage_fireball'); pull('fireBlast', 'mage_fire_blast'); pull('pyroblast', 'mage_pyroblast'); pull('frostbolt', 'mage_frostbolt');
    const fut = (n) => (data.mage.future || []).find((f) => f.name === n);
    const range = (r) => { const e = r.effects.find((x) => x.effect === 2); const mid = e.base + e.per_level * Math.max(0, 60 - r.spell_level) + 1; return [mid * (1 - e.variance / 2), mid * (1 + e.variance / 2), e.sp_coeff]; };
    const sc = fut('Scorch'); if (sc) { const [lo, hi, co] = range(sc.rank); Object.assign(M.scorch, { min: lo, max: hi, coeff: co, cost: sc.rank.cost.amount, cast: sc.rank.cast_ms / 1000 }); }
    const ff = fut('Frostfire Bolt'); if (ff) { const [lo, hi, co] = range(ff.rank); Object.assign(M.frostfireBolt, { min: lo, max: hi, coeff: co, cost: ff.rank.cost.amount, cast: ff.rank.cast_ms / 1000 }); const dt = ff.rank.effects.find((x) => x.aura === 3); if (dt) M.frostfireBolt.dot.total = dt.base * 3; }
    const cb = fut('Combustion'); if (cb) M.combustion.cd = cb.rank.cooldown_ms / 1000;
  }

  return {
    name: 'mage', build: b, M,
    setup(sim) {
      sim.player.resource = 'mana'; sim.kitBuild = b;
      const st = sim.stats, intBonus = M.arcaneMind.int * b.arcaneMind;
      const extraInt = Math.floor((st.int || 0) * intBonus);
      sim.critBase = extraInt / 59.5 / 100;                                         // Arcane Mind's extra Intellect -> crit (ASSUMED Classic ratio)
      sim.manaMaxExtra = 15 * extraInt;
      setupMana(sim, { manaMax: st.mana + sim.manaMaxExtra, mp5: st.mp5 || 0, spiritRegen: spiritRegenPerSec({ int: (st.int || 0) + extraInt, spi: st.spi }), castingFraction: M.arcaneMeditation.keep * b.arcaneMeditation });
      sim.cd = { gem: 0, innervate: 0, fireBlast: 0, combustion: 0, arcanePower: 0, presenceOfMind: 0, evocation: 0, potion: 0 };
      sim.pom = false; sim.cc = false; sim.mb = false; sim.fof = 0; sim.combCrits = 0; sim.heatStacks = 0;
      sim.aScorch = sim.addAura({ name: 'Fire Vulnerability', duration: M.improvedScorch.dur, maxStacks: M.improvedScorch.max });
      sim.aHeat = sim.addAura({ name: 'Heating Up', duration: 20, maxStacks: 3 });
      sim.aComb = sim.addAura({ name: 'Combustion', duration: Infinity, maxStacks: 99 });
      sim.aAP = sim.addAura({ name: 'Arcane Power', duration: M.arcanePower.duration });
      sim.aWC = sim.addAura({ name: "Winter's Chill", duration: 15, maxStacks: M.wintersChill.max });
      sim.aFoF = sim.addAura({ name: 'Fingers of Frost', duration: 15 });
      sim.aCC = sim.addAura({ name: 'Clearcasting', duration: Infinity });
      sim.aAB = sim.addAura({ name: 'Arcane Blast', duration: M.arcaneBlast.dur, maxStacks: M.arcaneBlast.maxStacks });
      sim.aInn = sim.addAura({ name: 'Innervate', duration: M.innervate.dur, onApply: () => { sim.regenMult = M.innervate.mult; }, onExpire: () => { sim.regenMult = 1; } });
      sim.regenMult = 1; sim.moving = false;
      if (b.movement > 0) {
        const per = M.movement.period, len = Math.min(per * 0.9, per * b.movement);
        const go = () => { if (sim.casting) { sim.schedule(0.1, go); return; } sim.moving = true; sim.schedule(len, () => { sim.moving = false; sim.poke(0); }); sim.schedule(per, go); };
        sim.schedule(per / 2, go);
      }
      sim.aMB = sim.addAura({ name: 'Missile Barrage', duration: Infinity });
      const ab = M.arcaneBlast, am = M.arcaneMissiles;
      sim.est = (s) => {
        const mid = s.total !== undefined ? s.total : (s.min + s.max) / 2, sp = (st.sp || 0) * s.coeff;
        const dot = s.dot ? s.dot.total + (st.sp || 0) * (s.dot.coeff || 0) : 0;
        const m = specMods(sim, s, true);
        const hit = Math.min(0.99, 1 - sim.target.spellMiss + st.hit + m.hit), crit = Math.min(1, st.crit + sim.critBase + m.crit);
        return ((mid + sp) * (1 + crit * (0.5 * (1 + m.critBonus))) * hit + dot) * m.dmg / Math.max(mageCastTime(sim, s, true), SPELL_GCD);
      };
    },
    start(sim) { sim.arcaneBurst = arcaneBurstBetter(sim, M, b); },
    rotate(sim) { return mageRotate(sim, b, M); },
  };
}

// ---- modifiers ----
function schoolHas(s, x) { return s.schools.indexOf(x) >= 0; }
function specMods(sim, s, noAuras, extra = 1) {
  const b = sim.kitBuild, M = sim.spec.M;
  let hit = 0, crit = 0, dmg = extra, critBonus = 0;
  const fire = schoolHas(s, 'fire'), frost = schoolHas(s, 'frost'), arcane = schoolHas(s, 'arcane');
  if (fire || frost) hit += M.elementalPrecision.hit * b.elementalPrecision;
  if (arcane) { hit += M.arcaneFocus.hit * b.arcaneFocus; crit += M.arcaneImpact.crit * b.arcaneImpact; critBonus += M.arcaneMind.critBonus * b.arcaneMind; }
  if (fire) { crit += M.criticalMass.crit * b.criticalMass; dmg *= 1 + M.firePower.dmg * b.firePower; }
  if (frost) { dmg *= 1 + M.piercingIce.dmg * b.piercingIce; critBonus += M.iceShards.critBonus * b.iceShards; }
  if (s.incin) crit += M.incineration.crit * b.incineration;
  crit += M.arcaneInstability.crit * b.arcaneInstability; dmg *= 1 + M.arcaneInstability.dmg * b.arcaneInstability;
  if (!noAuras) {
    if (sim.aAP.active) dmg *= M.arcanePower.dmg;
    if (fire) { crit += sim.aComb.stacks * 0.10; if (sim.aScorch.active) dmg *= 1 + M.improvedScorch.perStack * sim.aScorch.stacks; }
    if (s === M.frostbolt || s === M.iceLance) crit += sim.aWC.stacks * M.wintersChill.crit;
    if (sim.aFoF.active) { crit += M.shatter.crit * b.shatter; if (s === M.iceLance) dmg *= M.iceLanceFrozen; }
  }
  return { hit, crit: crit + sim.critBase, dmg, critBonus };
}
function mageCastTime(sim, s, noAuras) {
  const b = sim.kitBuild, M = sim.spec.M;
  let t = s.cast;
  if (s === M.fireball || s === M.frostfireBolt) t -= M.improvedFireball.cast * b.improvedFireball;
  if (s === M.frostbolt) t -= M.improvedFrostbolt.cast * b.improvedFrostbolt;
  if (s === M.pyroblast && !noAuras && sim.aHeat.active) t *= 1 - 0.25 * sim.aHeat.stacks;
  return t;
}
function mageManaCost(sim, s) {
  const b = sim.kitBuild, M = sim.spec.M;
  if (sim.aCC.active) return 0;
  if (s === M.arcaneBlast) { let c = s.cost * (1 + s.stackCost * sim.aAB.stacks); if (sim.aAP.active) c *= M.arcanePower.cost; return Math.round(c); }
  if (s === M.arcaneMissiles && sim.aMB.active) return 0;
  let c = s.cost;
  if (schoolHas(s, 'frost')) c *= 1 - M.frostChanneling.cost * b.frostChanneling;
  if (sim.aAP.active) c *= M.arcanePower.cost;
  return Math.round(c);
}

// ---- casting a damage spell ----
function mageCast(sim, s, instant) {
  const b = sim.kitBuild, M = sim.spec.M, cost = mageManaCost(sim, s);
  const usedCC = sim.aCC.active; if (usedCC) sim.aCC.expire();
  const pomUsed = sim.pom && s.cast >= 1.5 && s !== M.arcaneMissiles; if (pomUsed) sim.pom = false;
  let ct = instant ? 0 : mageCastTime(sim, s);
  if (pomUsed) ct = 0;
  if (s === M.pyroblast) sim.aHeat.expire();
  let extra = 1;
  if (s !== M.arcaneBlast && sim.aAB.active) { extra = 1 + M.arcaneBlast.stackDmg * sim.aAB.stacks; sim.aAB.expire(); }
  if (s === M.arcaneMissiles) return channelMissiles(sim, s, cost, extra);
  const baseCost = s.cost;
  return beginCast(sim, s, ct, cost, () => {
    const m = specMods(sim, s, false, extra);
    const raw = s.min + (s.max - s.min) * sim.rng() + sim.stats.sp * s.coeff;
    const r = resolveSpell(sim, s.name, raw, m);
    afterHit(sim, s, r, m, baseCost);
    if (s === M.arcaneBlast && r.outcome !== 'miss') sim.aAB.apply(1);
    if (r.outcome !== 'miss' && s.dot) {
      const total = s.dot.total + sim.stats.sp * (s.dot.coeff || 0);
      applyDot(sim, s.name + ' (DoT)', total * m.dmg * (1 - sim.target.spellMitigation) * sim.target.spellTaken, s.dot.ticks, s.dot.interval);
    }
  });
}
function afterHit(sim, s, r, m, baseCost) {
  const b = sim.kitBuild, M = sim.spec.M;
  if (sim.aFoF.active && s !== M.arcaneMissiles && --sim.fof <= 0) sim.aFoF.expire();   // Fingers of Frost: each spell uses a charge
  if (r.outcome === 'miss') return;
  const crit = r.outcome === 'crit', fire = schoolHas(s, 'fire'), frost = schoolHas(s, 'frost');
  if (b.arcaneConcentration && sim.rng() < M.arcaneConcentration.chance * b.arcaneConcentration) sim.aCC.apply();
  if (crit && (fire || frost) && b.masterOfElements) gainMana(sim, baseCost * M.masterOfElements.refund * b.masterOfElements);
  if (fire) {
    if (sim.aComb.active) { sim.aComb.apply(1); if (crit && ++sim.combCrits >= 3) { sim.aComb.expire(); sim.combCrits = 0; } }
    if (crit && b.ignite) { const total = r.dmg * M.ignite.frac * b.ignite; applyDot(sim, 'Ignite', total, 2, 2); }
  }
  if (crit && s.heat && b.heatingUp) sim.aHeat.apply(1);
  if (s === M.scorch && b.improvedScorch && sim.rng() < Math.min(1, M.improvedScorch.chance * b.improvedScorch)) sim.aScorch.apply(1);
  if (frost && b.wintersChill && sim.rng() < M.wintersChill.chance * b.wintersChill) sim.aWC.apply(1);
  if (s === M.frostbolt && b.fingersOfFrost && sim.rng() < M.fingersOfFrost.chance) { sim.fof = b.fingersOfFrost; sim.aFoF.apply(); }
  if (b.missileBarrage && (s === M.fireball || s === M.frostbolt || s === M.frostfireBolt) && sim.rng() < M.missileBarrage.am) sim.aMB.apply();
}
function channelMissiles(sim, s, cost, extra = 1) {
  const M = sim.spec.M, barrage = sim.aMB.active; if (barrage) sim.aMB.expire();
  const total = s.total + sim.stats.sp * s.coeff, per = total / s.ticks, step = barrage ? 0.5 : 1;
  const dur = step * s.ticks / sim.hasteMult();
  const m0 = specMods(sim, s, false, extra);
  sim.gcdReadyAt = sim.now + SPELL_GCD; spendMana(sim, cost); sim.entry(s.name).casts++;
  sim.casting = { name: s.name, endsAt: sim.now + dur };
  for (let i = 1; i <= s.ticks; i++) sim.schedule(dur * i / s.ticks, () => {
    const r = resolveSpell(sim, s.name, per, specMods(sim, s, false, extra));
    afterHit(sim, s, r, m0, s.cost / s.ticks);
  });
  sim.schedule(dur, () => { sim.casting = null; sim.lastCastAt = sim.now; sim.poke(0); });
  return dur;
}

// ---- rotation ----
function mageRotate(sim, b, M) {
  const now = sim.now;
  if (sim.casting) return sim.casting.endsAt - now;
  const rem = sim.fightLen - now;
  // mana potion (off the global cooldown)
  if (b.usePotion && now >= sim.cd.potion && sim.mana <= sim.manaMax - (M.manaPotion.min + M.manaPotion.max) / 2 && rem > 20) {
    sim.cd.potion = now + M.manaPotion.cd; sim.entry('Mana Potion').casts++;
    gainMana(sim, M.manaPotion.min + (M.manaPotion.max - M.manaPotion.min) * sim.rng());
  }
  if (b.useGem && now >= sim.cd.gem && sim.mana <= sim.manaMax - (M.manaGem.min + M.manaGem.max) / 2 && rem > 15) {
    sim.cd.gem = now + M.manaGem.cd; sim.entry('Mana Gem').casts++;
    gainMana(sim, M.manaGem.min + (M.manaGem.max - M.manaGem.min) * sim.rng());
  }
  if (b.innervate && now >= sim.cd.innervate && sim.mana < 0.5 * sim.manaMax) { sim.cd.innervate = now + M.innervate.cd; sim.entry('Innervate').casts++; sim.aInn.apply(); }
  if (b.useCooldowns) {
    if (b.combustion && now >= sim.cd.combustion && !sim.aComb.active) { sim.cd.combustion = now + M.combustion.cd; sim.entry('Combustion').casts++; sim.aComb.apply(1); sim.combCrits = 0; }
    if (b.arcanePower && now >= sim.cd.arcanePower) { sim.cd.arcanePower = now + M.arcanePower.cd; sim.entry('Arcane Power').casts++; sim.aAP.apply(); }
    if (b.presenceOfMind && now >= sim.cd.presenceOfMind && !sim.pom && b.rotation !== 'arcane') { sim.cd.presenceOfMind = now + M.presenceOfMind.cd; sim.entry('Presence of Mind').casts++; sim.pom = true; }
  }
  const gcdLeft = sim.gcdReadyAt - now;
  if (gcdLeft > 1e-9) return gcdLeft;
  const rotation = b.rotation;
  const instantOnly = sim.moving;
  const pick = () => {
    if (rotation === 'frost') return (b.iceLance && sim.aFoF.active) ? M.iceLance : M.frostbolt;
    if (rotation === 'arcane') {
      // burst: stack Arcane Blast to the cap, then spend the stacks on one Arcane Missiles channel
      if (b.arcaneBlast && sim.arcaneBurst && sim.aAB.stacks < M.arcaneBlast.maxStacks) return M.arcaneBlast;
      return M.arcaneMissiles;
    }
    // fire
    if (b.improvedScorch && !sim.aScorch.active || (b.improvedScorch && sim.aScorch.stacks < M.improvedScorch.max) || (b.improvedScorch && sim.aScorch.endsAt - now < 6)) return M.scorch;
    if (now >= sim.cd.fireBlast) return M.fireBlast;
    if (b.pyroblast && (sim.pom || sim.aHeat.stacks >= 2)) return M.pyroblast;
    if (b.filler === 'fireball') return M.fireball;
    if (b.filler === 'frostfire') return M.frostfireBolt;
    return sim.est(M.frostfireBolt) > sim.est(M.fireball) ? M.frostfireBolt : M.fireball;
  };
  let s = pick();
  if (instantOnly && s.cast > 0 && !sim.pom) {      // moving: only instant spells
    const alt = (b.iceLance && sim.aFoF.active && rotation === 'frost') ? M.iceLance : (b.rotation === 'fire' && now >= sim.cd.fireBlast) ? M.fireBlast : null;
    if (!alt) return 0.25;
    s = alt;
  }
  // out of mana: Evocation, else wait for the regeneration
  if (mageManaCost(sim, s) > sim.mana) {
    if (b.useEvocation && now >= sim.cd.evocation && rem > 10) {
      sim.cd.evocation = now + M.evocation.cd; sim.entry('Evocation').casts++;
      sim.gcdReadyAt = now + SPELL_GCD; sim.casting = { name: 'Evocation', endsAt: now + M.evocation.duration };
      const per = M.evocation.restore * sim.manaMax / 4;
      for (let i = 1; i <= 4; i++) sim.schedule(2 * i, () => gainMana(sim, per));
      sim.schedule(M.evocation.duration, () => { sim.casting = null; sim.lastCastAt = sim.now; sim.poke(0); });
      return M.evocation.duration;
    }
    sim.manaOom += 0.5;
    return 0.5;
  }
  if (s === M.fireBlast) sim.cd.fireBlast = now + M.fireBlast.cd - M.wakeOfFire.cd * b.wakeOfFire;
  return mageCast(sim, s, s.cast === 0);
}

// Arcane: is "four Arcane Blasts, then one Arcane Missiles with the stacks" better than Arcane Missiles alone?
// Compared on damage per second with the mana cost folded in (damage per second of mana-limited play: dmg / max(time, mana / manaRate)).
function arcaneBurstBetter(sim, M, b) {
  if (!b.arcaneBlast || b.rotation !== 'arcane') return false;
  const st = sim.stats, ab = M.arcaneBlast, am = M.arcaneMissiles;
  const mA = specMods(sim, ab, true), mM = specMods(sim, am, true);
  const crit = (m) => 1 + Math.min(1, st.crit + m.crit) * 0.5 * (1 + m.critBonus), hit = (m) => Math.min(0.99, 1 - sim.target.spellMiss + st.hit + m.hit);
  const abHit = ((ab.min + ab.max) / 2 + st.sp * ab.coeff) * crit(mA) * hit(mA) * mA.dmg, amHit = (am.total + st.sp * am.coeff) * crit(mM) * hit(mM) * mM.dmg;
  let dmg = 0, mana = 0, time = 0;
  for (let i = 0; i < ab.maxStacks; i++) { dmg += abHit; mana += ab.cost * (1 + ab.stackCost * i); time += ab.cast / sim.hasteMult(); }
  dmg += amHit * (1 + ab.stackDmg * ab.maxStacks); mana += am.cost; time += am.cast / sim.hasteMult();
  const rate = (st.mp5 || 0) / 5 + 0.0;                       // mana regained per second while casting (gear only)
  const budget = sim.manaMax / 180 + rate + 8;                // rough sustainable mana per second over a 3-minute fight (pool + potions + regen)
  const burst = dmg / Math.max(time, mana / budget), plain = amHit / Math.max(am.cast / sim.hasteMult(), am.cost / budget);
  return burst > plain * 1.05;
}

// ---- warlock.js ----
// Warlock kit (Affliction / Destruction / Demonology-with-sacrifice share one priority list; the specs differ by
// talents). Numbers are WoW: Forever's own where the client tables have them (Corruption, Immolate, Shadow Bolt,
// Conflagrate, Incinerate, Soul Fire, Wrack, Siphon Life, Bane of Doom) and the talent tooltips; ASSUMED = Classic
// 1.12 value kept until Forever's table is sourced: Bane of Agony, Shadowburn, Life Tap, the Imp's Firebolt, Demonic Rune
// style mana items, spell hit/crit/mana formulas (character.js), Soul Shards (not limited: shards are assumed available).
// Periodic effects use the client's per-tick spell coefficient (sp_coeff x number of ticks) and can crit (can_crit).

const WARLOCK = {
  shadowBolt: { name: 'Shadow Bolt', schools: ['shadow'], destruction: true, cast: 3, cost: 380, min: 253.3, max: 282.7, coeff: 0.857 },
  incinerate: { name: 'Incinerate', schools: ['fire'], destruction: true, cast: 2.5, cost: 325, min: 190, max: 245, coeff: 0.714, immolateBonus: 1.25 },
  immolate: { name: 'Immolate', schools: ['fire'], destruction: true, cast: 2, cost: 380, flat: 158, coeff: 0.2, dot: { total: 275, ticks: 5, interval: 3, coeff: 0.13 } },
  conflagrate: { name: 'Conflagrate', schools: ['fire'], destruction: true, cast: 0, cost: 255, min: 220, max: 344, coeff: 0.429, cd: 10 },
  soulFire: { name: 'Soul Fire', schools: ['fire'], destruction: true, cast: 6, cost: 335, min: 334, max: 528, coeff: 1, cd: 60 },
  shadowburn: { name: 'Shadowburn', schools: ['shadow'], destruction: true, cast: 0, cost: 365, min: 450, max: 502, coeff: 0.429, cd: 15 },   // ASSUMED (Classic)
  corruption: { name: 'Corruption', schools: ['shadow'], cast: 2, cost: 340, dot: { total: 438, ticks: 6, interval: 3, coeff: 0.2 } },
  agony: { name: 'Bane of Agony', schools: ['shadow'], cast: 0, cost: 265, dot: { total: 1044, ticks: 12, interval: 2, coeff: 0.1 } },        // ASSUMED (Classic rank 6, coeff 1.2 over 12 ticks)
  doom: { name: 'Bane of Doom', schools: ['shadow'], cast: 0, cost: 300, cd: 60, dot: { total: 1742, ticks: 1, interval: 60, coeff: 4 } },
  siphonLife: { name: 'Siphon Life', schools: ['shadow'], cast: 0, cost: 365, dot: { total: 410, ticks: 10, interval: 3, coeff: 0.05 } },
  wrack: { name: 'Wrack', schools: ['shadow'], cast: 0, cost: 200, dot: { total: 216, ticks: 6, interval: 1, coeff: 0.143 }, vuln: 0.10, dur: 6 },
  lifeTap: { restore: 424 },                                                                                  // ASSUMED (Classic rank 6), health is assumed to be healed back
  manaPotion: { cd: 120, min: 1350, max: 2250 },                                                              // ASSUMED (Major Mana Potion)
  manaGem: { cd: 120, min: 1073, max: 1127 },
  imp: { cast: 2, min: 105, max: 115, spCoeff: 0.15, crit: 0.05, miss: 0.06 },                                  // ASSUMED (Classic Firebolt rank 7, pet scaling)
  sacrifice: 0.15,
  // talents, per rank (Forever tooltips; per-rank = last rank / max rank)
  suppression: { hit: 0.01 }, improvedCorruption: { cast: 0.4, dmg: 0.02 }, malediction: { dmg: 0.01 }, improvedLifeTap: { restore: 0.10 },
  pandemic: { critBonus: 1 / 3 }, malevolence: { crit: 0.01 }, nightfall: { chance: 0.02 }, shadowMastery: { dmg: 0.01 }, improvedBaneOfAgony: { dmg: 0.05 },
  improvedShadowBolt: { dmg: 0.04, dur: 12 }, bane: { cast: 0.1, soulFire: 0.4 }, cataclysm: { cost: 0.10 / 3 }, aftermath: { dmg: 0.10 }, ruin: { critBonus: 0.2 },
  agonizingFlames: { dmg: 0.10 / 3 }, fireAndBrimstone: { crit: 0.25 / 3 }, shadowAndFlame: { dmg: 0.02, dur: 20 }, decimation: { cd: 0.45 },
  demonicKnowledge: { sp: 20 }, masterDemonologist: { dmg: 0.02 }, unholyPower: { pet: 0.02 }, improvedImp: { pet: 0.10 }, felVitality: { mana: 0.05 },
  soulSiphon: { dmg: 0.12 },
};

const WARLOCK_DEFAULT_BUILD = {
  suppression: 0, improvedCorruption: 0, malediction: 0, improvedLifeTap: 0, pandemic: 0, malevolence: 0, nightfall: 0, shadowMastery: 0, improvedBaneOfAgony: 0,
  siphonLife: 0, wrack: 0, soulSiphon: 0,
  improvedShadowBolt: 0, bane: 0, cataclysm: 0, aftermath: 0, ruin: 0, shadowburn: 0, agonizingFlames: 0, conflagrate: 0, fireAndBrimstone: 0, shadowAndFlame: 0, incinerate: 0,
  decimation: 0, demonicKnowledge: 0, masterDemonologist: 0, unholyPower: 0, improvedImp: 0, felVitality: 0, demonicSacrifice: 0,
  rotation: 'affliction', curse: 'auto', filler: 'auto', pet: 'imp', sacrifice: 'none', useCooldowns: true, usePotion: true, useGem: true, immolate: 'auto',
};

const warlockParseCast = (c) => (typeof c === 'string' ? (c === 'instant' ? 0 : parseFloat(c)) : c);

function warlockKit(build = {}, data = null) {
  const b = Object.assign({}, WARLOCK_DEFAULT_BUILD, build), W = JSON.parse(JSON.stringify(WARLOCK));
  const a = data && data.warlock && data.warlock.abilities;
  if (a) {
    const pull = (key, id) => {
      const x = a[id]; if (!x) return;
      const d = (x.effects || []).find((e) => e.kind === 'direct_damage'), p = (x.effects || []).find((e) => e.kind === 'periodic_damage'), s = W[key];
      if (d && d.dmg_range) { s.min = d.dmg_range[0]; s.max = d.dmg_range[1]; s.coeff = d.sp_coeff; }
      if (d && d.flat !== undefined) { s.flat = d.flat; s.coeff = d.sp_coeff; }
      if (p && s.dot) { s.dot.total = p.total_damage; s.dot.interval = p.tick_interval_sec; s.dot.ticks = Math.round(p.duration_sec / p.tick_interval_sec); s.dot.coeff = p.sp_coeff || 0; }
      if (x.resource_cost && x.resource_cost.mana) s.cost = x.resource_cost.mana;
      s.cast = warlockParseCast(x.cast_time);
    };
    pull('shadowBolt', 'warlock_shadow_bolt'); pull('immolate', 'warlock_immolate'); pull('corruption', 'warlock_corruption');
    const fut = (n) => (data.warlock.future || []).find((f) => f.name === n);
    const range = (r) => { const e = r.effects.find((x) => x.effect === 2); const mid = e.base + e.per_level * Math.max(0, 60 - r.spell_level) + 1; return [mid * (1 - e.variance / 2), mid * (1 + e.variance / 2), e.sp_coeff]; };
    const direct = (key, name) => { const f = fut(name); if (!f) return; const [lo, hi, co] = range(f.rank); Object.assign(W[key], { min: lo, max: hi, coeff: co, cost: f.rank.cost.amount, cast: f.rank.cast_ms / 1000 }); if (f.rank.cooldown_ms) W[key].cd = f.rank.cooldown_ms / 1000; };
    direct('conflagrate', 'Conflagrate'); direct('incinerate', 'Incinerate'); direct('soulFire', 'Soul Fire');
    const dotOf = (key, name, aura) => { const f = fut(name); if (!f) return; const e = f.rank.effects.find((x) => x.aura === aura); if (!e) return; const ticks = Math.max(1, Math.round(f.rank.duration_ms / e.period_ms)); Object.assign(W[key].dot, { total: e.base * ticks, ticks, interval: e.period_ms / 1000, coeff: e.sp_coeff }); W[key].cost = f.rank.cost.amount; if (f.rank.cooldown_ms) W[key].cd = f.rank.cooldown_ms / 1000; };
    dotOf('siphonLife', 'Siphon Life', 53); dotOf('wrack', 'Wrack', 3); dotOf('doom', 'Bane of Doom', 3);
  }

  return {
    name: 'warlock', build: b, W,
    setup(sim) {
      sim.player.resource = 'mana'; sim.kitBuild = b;
      const st = sim.stats;
      sim.manaMaxExtra = Math.floor(st.mana * W.felVitality.mana * b.felVitality);
      setupMana(sim, { manaMax: st.mana + sim.manaMaxExtra, mp5: st.mp5 || 0, spiritRegen: spiritRegenPerSec({ int: st.int, spi: st.spi }), castingFraction: 0 });
      sim.critBase = 0; sim.regenMult = 1;
      sim.cd = { gem: 0, potion: 0, conflagrate: 0, soulFire: 0, shadowburn: 0, doom: 0 };
      sim.trance = false;
      const petOn = b.pet === 'imp' && !(b.sacrifice !== 'none' && b.demonicSacrifice);
      sim.petOn = petOn;
      sim.spBonus = petOn ? W.demonicKnowledge.sp * b.demonicKnowledge : 0;           // Demonic Knowledge: +33% of level per rank while a demon is out
      sim.sacrificed = b.sacrifice !== 'none' && b.demonicSacrifice ? b.sacrifice : null;
      sim.aISB = sim.addAura({ name: 'Shadow Vulnerability', duration: W.improvedShadowBolt.dur });
      sim.aSF = sim.addAura({ name: 'Shadow and Flame', duration: W.shadowAndFlame.dur });
      sim.aWrack = sim.addAura({ name: 'Wrack', duration: W.wrack.dur });
      sim.aTrance = sim.addAura({ name: 'Shadow Trance', duration: Infinity });
      sim.aDecim = sim.addAura({ name: 'Decimation', duration: 10 });
      // the Imp's Firebolt: independent cast loop, uses the warlock's spell power
      if (petOn) {
        const bolt = () => {
          const I = W.imp, e = sim.entry('Imp Firebolt'); e.casts++;
          if (sim.rng() < I.miss) { e.misses++; } else {
            const sp = ((st.sp || 0) + sim.spBonus) * I.spCoeff;
            let d = I.min + (I.max - I.min) * sim.rng() + sp;
            d *= (1 + W.improvedImp.pet * b.improvedImp) * (1 + W.unholyPower.pet * b.unholyPower) * (1 + W.masterDemonologist.dmg * b.masterDemonologist);
            const crit = sim.rng() < I.crit; if (crit) d *= SPELL_CRIT_MULT;
            sim.record('Imp Firebolt', d * (1 - sim.target.spellMitigation) * sim.target.spellTaken, crit ? 'crit' : 'hit');
          }
          sim.schedule(I.cast, bolt);
        };
        sim.schedule(0.5, bolt);
      }
      sim.est = (s) => {
        const sp = (st.sp || 0), m = mods(sim, s, true);
        const mid = s.min !== undefined ? (s.min + s.max) / 2 : s.flat;
        const bonus = s === W.incinerate && dotActive(sim, 'Immolate') ? W.incinerate.immolateBonus : 1;
        const hit = Math.min(0.99, 1 - sim.target.spellMiss + st.hit + m.hit), crit = Math.min(1, st.crit + m.crit);
        return ((mid + (sp + sim.spBonus) * s.coeff) * bonus * (1 + crit * 0.5 * (1 + m.critBonus)) * hit) * m.dmg / Math.max(warlockCastTime(sim, s), SPELL_GCD);
      };
    },
    start() {},
    rotate(sim) { return warlockRotate(sim, b, W); },
  };
}

// ---- modifiers ----
function has(s, x) { return s.schools.indexOf(x) >= 0; }
function mods(sim, s, noAuras, periodic) {
  const b = sim.kitBuild, W = sim.spec.W;
  let hit = W.suppression.hit * b.suppression, crit = 0, dmg = 1, critBonus = 0;
  const shadow = has(s, 'shadow'), fire = has(s, 'fire');
  if (shadow) { crit += W.malevolence.crit * b.malevolence; dmg *= 1 + W.shadowMastery.dmg * b.shadowMastery; if (sim.sacrificed === 'imp') dmg *= 1 + W.sacrifice; }
  if (fire && sim.sacrificed === 'succubus') dmg *= 1 + W.sacrifice;
  if (s.destruction) { critBonus += W.ruin.critBonus * b.ruin; dmg *= 1 + W.agonizingFlames.dmg * b.agonizingFlames; }
  if (periodic) { dmg *= 1 + W.malediction.dmg * b.malediction; if (shadow) critBonus += W.pandemic.critBonus * b.pandemic; }
  if (s === W.conflagrate) crit += W.fireAndBrimstone.crit * b.fireAndBrimstone;
  if (!noAuras) {
    if (shadow) {
      if (sim.aISB.active) dmg *= 1 + W.improvedShadowBolt.dmg * b.improvedShadowBolt;
      if (sim.aSF.active) dmg *= 1 + W.shadowAndFlame.dmg * b.shadowAndFlame;
      if (periodic && sim.aWrack.active && s !== W.wrack) dmg *= 1 + W.wrack.vuln;
    }
  }
  return { hit, crit, dmg, critBonus };
}
function warlockCastTime(sim, s) {
  const b = sim.kitBuild, W = sim.spec.W;
  let t = s.cast;
  if (s === W.shadowBolt || s === W.immolate || s === W.incinerate) t -= W.bane.cast * b.bane;
  if (s === W.soulFire) { t -= W.bane.soulFire * b.bane; if (sim.aDecim.active) t *= 1 - 0.2 * b.decimation; }
  if (s === W.corruption) t -= W.improvedCorruption.cast * b.improvedCorruption;
  if (s === W.shadowBolt && sim.aTrance.active) t = 0;
  return Math.max(0, t);
}
function warlockManaCost(sim, s) {
  const b = sim.kitBuild, W = sim.spec.W;
  let c = s.cost;
  if (s.destruction) c *= 1 - W.cataclysm.cost * b.cataclysm;
  if (s === W.soulFire && sim.aDecim.active) return 0;
  return Math.round(c);
}

// ---- cast a spell (direct part, then the periodic part when it landed) ----
function warlockCast(sim, s) {
  const b = sim.kitBuild, W = sim.spec.W, st = sim.stats;
  const cost = warlockManaCost(sim, s);
  const tranced = s === W.shadowBolt && sim.aTrance.active; if (tranced) sim.aTrance.expire();
  const ct = tranced ? 0 : warlockCastTime(sim, s);
  return beginCast(sim, s, ct, cost, () => {
    let landed = true;
    if (s.min !== undefined || s.flat !== undefined) {
      const m = mods(sim, s, false);
      let raw = (s.min !== undefined ? s.min + (s.max - s.min) * sim.rng() : s.flat * (s === W.immolate ? 1 + W.aftermath.dmg * b.aftermath : 1)) + (st.sp + sim.spBonus) * s.coeff;
      if (s === W.incinerate && dotActive(sim, 'Immolate')) raw *= W.incinerate.immolateBonus;
      const r = resolveSpell(sim, s.name, raw, m);
      landed = r.outcome !== 'miss';
      if (landed) afterDirect(sim, s, r);
    } else {
      // pure damage-over-time spells need a hit roll
      const m = mods(sim, s, false, true);
      const hit = Math.min(0.99, 1 - sim.target.spellMiss + st.hit + m.hit);
      const e = sim.entry(s.name);
      if (sim.rng() >= hit) { e.misses++; landed = false; }
    }
    if (landed && s.dot) startDot(sim, s);
  });
}
function afterDirect(sim, s, r) {
  const b = sim.kitBuild, W = sim.spec.W;
  if (s === W.shadowBolt && r.outcome === 'crit' && b.improvedShadowBolt) sim.aISB.apply();
  if (s === W.conflagrate) { if (b.shadowAndFlame) sim.aSF.apply(); if (!(b.shadowAndFlame && sim.rng() < 0.2 * b.shadowAndFlame)) cancelDot(sim, 'Immolate'); }
  if (s === W.shadowburn && b.shadowAndFlame) { /* fire bonus not tracked separately: Shadowburn's fire window is folded into Conflagrate's shadow window */ }
  if ((s === W.shadowBolt || s === W.incinerate) && b.decimation && sim.targetHealthPct() < 0.35) sim.aDecim.apply();
}
function startDot(sim, s) {
  const b = sim.kitBuild, W = sim.spec.W, st = sim.stats, d = s.dot;
  const m = mods(sim, s, false, true);
  let per = (d.total / d.ticks + (st.sp + sim.spBonus) * d.coeff) * m.dmg * (1 - sim.target.spellMitigation) * sim.target.spellTaken;
  if (s === W.corruption) per *= 1 + W.improvedCorruption.dmg * b.improvedCorruption;
  if (s === W.agony) per *= 1 + W.improvedBaneOfAgony.dmg * b.improvedBaneOfAgony;
  if (s === W.wrack) { sim.aWrack.apply(); if (b.soulSiphon) per *= 1 + Math.min(3, activeAfflictions(sim)) * W.soulSiphon.dmg * b.soulSiphon; }
  const critChance = Math.max(0, Math.min(1, st.crit + m.crit));
  const critMult = 1 + (SPELL_CRIT_MULT - 1) * (1 + m.critBonus);
  const onTick = (s === W.corruption || s === W.wrack) && b.nightfall ? () => { if (sim.rng() < W.nightfall.chance * b.nightfall) sim.aTrance.apply(); } : null;
  applyDotCrit(sim, s.name, per, d.ticks, d.interval, () => { const c = sim.rng() < critChance; return { crit: c, mult: c ? critMult : 1 }; }, onTick);
}
function activeAfflictions(sim) { return ['Corruption', 'Bane of Agony', 'Bane of Doom', 'Siphon Life'].filter((n) => dotActive(sim, n)).length; }

// ---- rotation ----
function warlockRotate(sim, b, W) {
  const now = sim.now, rem = sim.fightLen - now;
  if (sim.casting) return sim.casting.endsAt - now;
  if (b.usePotion && now >= sim.cd.potion && sim.mana <= sim.manaMax - (W.manaPotion.min + W.manaPotion.max) / 2 && rem > 20) {
    sim.cd.potion = now + W.manaPotion.cd; sim.entry('Mana Potion').casts++;
    gainMana(sim, W.manaPotion.min + (W.manaPotion.max - W.manaPotion.min) * sim.rng());
  }
  if (b.useGem && now >= sim.cd.gem && sim.mana <= sim.manaMax - (W.manaGem.min + W.manaGem.max) / 2 && rem > 15) {
    sim.cd.gem = now + W.manaGem.cd; sim.entry('Mana Gem').casts++;
    gainMana(sim, W.manaGem.min + (W.manaGem.max - W.manaGem.min) * sim.rng());
  }
  const gcdLeft = sim.gcdReadyAt - now;
  if (gcdLeft > 1e-9) return gcdLeft;
  const destro = b.rotation === 'destruction';
  const useDoom = b.curse === 'doom' || (b.curse === 'auto' && sim.fightLen >= 80);
  const filler = (() => {
    const cands = [W.shadowBolt];
    if (b.incinerate) cands.push(W.incinerate);
    if (b.filler === 'shadowBolt') return W.shadowBolt;
    if (b.filler === 'incinerate' && b.incinerate) return W.incinerate;
    return cands.sort((x, y) => sim.est(y) - sim.est(x))[0];
  })();
  const refresh = (s, margin) => dotLeft(sim, s.name) <= margin + warlockCastTime(sim, s) && (rem > 6);
  const wantImmolate = b.immolate === true || (b.immolate === 'auto' && (destro || b.conflagrate));
  let s = null;
  // the damage-over-time effects first
  {
    if (wantImmolate && refresh(W.immolate, 1.5) && rem > 8) s = W.immolate;
    else if (refresh(W.corruption, 1.0) && rem > 8) s = W.corruption;
    else if (useDoom ? (now >= sim.cd.doom && refresh(W.doom, 0) && rem > 62) : (refresh(W.agony, 1.5) && rem > 8)) s = useDoom ? W.doom : W.agony;
    else if (b.siphonLife && refresh(W.siphonLife, 1.5) && rem > 8) s = W.siphonLife;
    else if (b.wrack && refresh(W.wrack, 0.5)) s = W.wrack;
  }
  if (!s && b.conflagrate && now >= sim.cd.conflagrate && dotActive(sim, 'Immolate')) s = W.conflagrate;
  if (!s && b.shadowburn && now >= sim.cd.shadowburn && destro) s = W.shadowburn;
  if (!s && now >= sim.cd.soulFire && destro && sim.est(W.soulFire) > sim.est(filler) * 0.95) s = W.soulFire;
  if (!s) s = filler;
  // Life Tap when the next cast is not affordable (or the pool is nearly dry)
  const need = warlockManaCost(sim, s);
  if (need > sim.mana || sim.mana < 0.12 * sim.manaMax) {
    sim.gcdReadyAt = now + SPELL_GCD; sim.entry('Life Tap').casts++;
    gainMana(sim, W.lifeTap.restore * (1 + W.improvedLifeTap.restore * b.improvedLifeTap));
    return SPELL_GCD;
  }
  if (s === W.conflagrate) sim.cd.conflagrate = now + W.conflagrate.cd;
  if (s === W.shadowburn) sim.cd.shadowburn = now + W.shadowburn.cd;
  if (s === W.soulFire) sim.cd.soulFire = now + W.soulFire.cd * (1 - W.decimation.cd * b.decimation);
  if (s === W.doom) sim.cd.doom = now + W.doom.cd;
  return warlockCast(sim, s);
}

// ---- hunter.js ----
// Hunter kit (Marksmanship / Beast Mastery / Survival share one ranged rotation; the specs differ by talents).
// WoW: Forever's own numbers where the client tables have them (Aimed Shot, Arcane Shot, Serpent Sting, Rapid Fire,
// Sniper Shot, Viper Sting) and the talent tooltips. ASSUMED = Classic 1.12 value kept until Forever's table is
// sourced: Multi-Shot (the Forever cooldown is shared with Aimed Shot), Aspect of the Hawk, ammo damage, the pet's
// attacks and Claw, Bestial Wrath's cooldown, Summon Hawk (a new Forever spell: rate and cooldown guessed), quiver haste.
// Not simulated: melee weaving (Raptor Strike, Mongoose Bite), traps, Volley (area spell), Viper Sting, Aspect of the Viper.

const HUNTER = {
  autoShot: { name: 'Auto Shot' },
  aimed: { name: 'Aimed Shot', cost: 310, cast: 2, flat: 166, cd: 6 },
  arcane: { name: 'Arcane Shot', cost: 190, flat: 217, cd: 6 },
  multi: { name: 'Multi-Shot', cost: 275, flat: 150, cd: 6 },                         // ASSUMED (Classic rank 5; cooldown shared with Aimed Shot in Forever)
  serpent: { name: 'Serpent Sting', cost: 250, total: 555, ticks: 5, interval: 3 },
  sniper: { name: 'Sniper Shot', cost: 365, cast: 4, flat: 295, cd: 15 },
  rapidFire: { name: 'Rapid Fire', cost: 100, cd: 300, duration: 15, haste: 1.4 },
  aspectHawk: { rap: 155 },                                                         // ASSUMED (Classic rank 7)
  quiver: { haste: 1.15 },                                                          // ASSUMED (Classic quiver)
  ammoDps: 20.5,                                                                    // ASSUMED (Classic Thorium Headed Arrow class ammo)
  manaPotion: { cd: 120, min: 1350, max: 2250 }, manaGem: { cd: 120, min: 1073, max: 1127 },
  pet: { speed: 1.0, min: 44, max: 56, apFrac: 0.22, miss: 0.09, dodge: 0.05, crit: 0.05, special: { name: 'Claw', flat: 54, every: 2.0 } },   // ASSUMED (Classic cat)
  bestialWrath: { cd: 120, duration: 18, dmg: 1.5 },                                // cooldown ASSUMED
  hawk: { name: 'Summon Hawk', cost: 150, cd: 120, duration: 18, every: 1.5, flat: 32, rapFrac: 0.05 },   // rate and cooldown ASSUMED
  // talents, per rank (Forever tooltips; per-rank = last rank / max rank)
  lethalAttacks: { crit: 0.01 }, efficiency: { cost: 0.03 }, carefulAim: { intToAp: 0.2 }, rapidKilling: { cd: 60 }, improvedArcane: { cd: 0.3 },
  loneWolf: { dmg: 0.20 }, mortalShots: { critBonus: 0.06 }, barrage: { dmg: 0.10 / 3 }, rangedSpec: { dmg: 0.01 }, improvedStings: { dmg: 0.20 / 3 },
  surefooted: { hit: 0.01 }, lightningReflexes: { agi: 0.02 }, unleashedFury: { pet: 0.03 }, ferocity: { petCrit: 0.02 }, frenzy: { haste: 1.3, dur: 8 },
  focusedFire: { dmg: 0.01 }, deadlyAspects: { chance: 0.02, haste: 1.3, dur: 12 }, bestialDiscipline: { keep: 0.25 },
};

const HUNTER_DEFAULT_BUILD = {
  lethalAttacks: 0, efficiency: 0, carefulAim: 0, rapidKilling: 0, improvedArcane: 0, loneWolf: 0, mortalShots: 0, barrage: 0, rangedSpec: 0, improvedStings: 0, sniperShot: 0,
  surefooted: 0, lightningReflexes: 0, unleashedFury: 0, ferocity: 0, frenzy: 0, bestialWrath: 0, focusedFire: 0, deadlyAspects: 0, summonHawk: 0, bestialDiscipline: 0,
  pet: 'cat', useCooldowns: true, usePotion: true, useGem: true, aspect: true, quiver: true, shots: 'auto',
};

const hunterParseCast = (c) => (typeof c === 'string' ? (c === 'instant' ? 0 : parseFloat(c)) : c);

function hunterKit(build = {}, data = null) {
  const b = Object.assign({}, HUNTER_DEFAULT_BUILD, build), H = JSON.parse(JSON.stringify(HUNTER));
  const a = data && data.hunter && data.hunter.abilities;
  if (a) {
    const eff = (x, k) => (x && x.effects || []).find((e) => e.kind === k);
    const aim = a.hunter_aimed_shot, arc = a.hunter_arcane_shot, ser = a.hunter_serpent_sting;
    if (aim) { const e = eff(aim, 'normalized_weapon_damage'); if (e) H.aimed.flat = e.flat; H.aimed.cost = aim.resource_cost.mana; H.aimed.cast = hunterParseCast(aim.cast_time); if (aim.cooldown_sec) H.aimed.cd = aim.cooldown_sec; }
    if (arc) { const e = eff(arc, 'direct_damage'); if (e) H.arcane.flat = e.flat; H.arcane.cost = arc.resource_cost.mana; if (arc.cooldown_sec) H.arcane.cd = arc.cooldown_sec; }
    if (ser) { const e = eff(ser, 'periodic_damage'); if (e) { H.serpent.total = e.total_damage; H.serpent.interval = e.tick_interval_sec; H.serpent.ticks = Math.round(e.duration_sec / e.tick_interval_sec); } H.serpent.cost = ser.resource_cost.mana; }
    const fut = (n) => (data.hunter.future || []).find((f) => f.name === n);
    const rf = fut('Rapid Fire'); if (rf) { H.rapidFire.cost = rf.rank.cost.amount; H.rapidFire.cd = rf.rank.cooldown_ms / 1000; H.rapidFire.duration = rf.rank.duration_ms / 1000; const e = rf.rank.effects.find((x) => x.aura === 140); if (e) H.rapidFire.haste = 1 + e.base / 100; }
    const ss = fut('Sniper Shot'); if (ss) { H.sniper.cost = ss.rank.cost.amount; H.sniper.cast = ss.rank.cast_ms / 1000; H.sniper.cd = ss.rank.cooldown_ms / 1000; const e = ss.rank.effects.find((x) => x.effect === 121); if (e) H.sniper.flat = e.base; }
  }

  return {
    name: 'hunter', build: b, H,
    setup(sim) {
      sim.player.resource = 'mana'; sim.kitBuild = b;
      const st = sim.stats, rw = sim.player.ranged || { min: 50, max: 90, speed: 2.5 };
      sim.rw = rw;
      // Agility / Intellect talents
      const extraAgi = Math.floor((st.agi || 0) * H.lightningReflexes.agi * b.lightningReflexes);
      sim.mods.apBonus += extraAgi + (b.carefulAim ? Math.floor((st.int || 0) * H.carefulAim.intToAp * b.carefulAim) : 0) + (b.aspect ? H.aspectHawk.rap : 0);
      sim.mods.critBonus += extraAgi / 53 / 100 + H.lethalAttacks.crit * b.lethalAttacks;
      sim.mods.hitBonus += H.surefooted.hit * b.surefooted;
      sim.mods.critDmgBonus += H.mortalShots.critBonus * b.mortalShots;
      if (b.quiver) sim.mods.hasteMult *= H.quiver.haste;
      const petOn = b.pet !== 'none';
      sim.petOn = petOn;
      sim.dmgGlobal = (petOn ? 1 + H.focusedFire.dmg * b.focusedFire : 1) * (petOn ? 1 : 1 + H.loneWolf.dmg * b.loneWolf) * (1 + H.rangedSpec.dmg * b.rangedSpec);
      setupMana(sim, { manaMax: st.mana, mp5: st.mp5 || 0, spiritRegen: spiritRegenPerSec({ int: st.int, spi: st.spi }), castingFraction: H.bestialDiscipline.keep * b.bestialDiscipline });
      sim.cd = { shared: 0, arcane: 0, sniper: 0, rapid: 0, potion: 0, gem: 0, wrath: 0, hawk: 0 };
      sim.aRapid = sim.addAura({ name: 'Rapid Fire', duration: H.rapidFire.duration, mods: { hasteMult: H.rapidFire.haste } });
      sim.aDeadly = sim.addAura({ name: 'Deadly Aspects', duration: H.deadlyAspects.dur, mods: { hasteMult: H.deadlyAspects.haste } });
      sim.aWrath = sim.addAura({ name: 'Bestial Wrath', duration: H.bestialWrath.duration });
      sim.aFrenzy = sim.addAura({ name: 'Frenzy', duration: H.frenzy.dur });
      sim.serpentEnds = 0;
      // Auto Shot: its own timer, delayed while a cast is in progress (Classic), rescaled when haste changes
      sim.autoToken = 0; sim.autoNext = 0;
      const speed = () => rw.speed / sim.hasteMult();
      const fire = () => {
        if (sim.casting) { sim.autoToken++; const my = sim.autoToken; sim.autoNext = sim.casting.endsAt; sim.schedule(Math.max(1e-6, sim.casting.endsAt - sim.now), () => { if (sim.autoToken === my) fire(); }); return; }
        shot(sim, H.autoShot.name, 0, 1, 0, true);
        sim.autoToken++; const my = sim.autoToken; sim.autoNext = sim.now + speed();
        sim.schedule(speed(), () => { if (sim.autoToken === my) fire(); });
      };
      sim.fireAuto = fire;
      sim.onHasteChange = function (old) {
        const nm = this.hasteMult(); if (nm === old || this.autoNext <= this.now) return;
        this.autoToken++; const my = this.autoToken, rest = (this.autoNext - this.now) * old / nm;
        this.autoNext = this.now + rest; this.schedule(rest, () => { if (this.autoToken === my) fire(); });
      };
      sim.schedule(0.5, fire);
      if (petOn) startPet(sim, b, H);
    },
    start() {},
    rotate(sim) { return hunterRotate(sim, b, H); },
  };
}

// one ranged hit (Auto Shot or a shot): two rolls, no dodge, armor-mitigated; recorded under `name`
function shot(sim, name, flat, dmgMult, critBonus, isAuto) {
  const b = sim.kitBuild, H = sim.spec.H, rw = sim.rw;
  const rawFn = () => (sim.weaponRoll(rw) + H.ammoDps * rw.speed + sim.ap() / 14 * rw.speed + flat) * dmgMult * sim.dmgGlobal * (sim.aWrath.active ? 1 : 1);
  const o = yellowAttack(sim, name, rawFn, { canDodge: false, bonusCrit: critBonus || 0 });
  if (isAuto && b.deadlyAspects && b.aspect && o !== 'miss' && sim.rng() < H.deadlyAspects.chance * b.deadlyAspects) sim.aDeadly.apply();
  return o;
}

// ---- pet: melee swings and a periodic special, Bestial Wrath / Frenzy / talents ----
function startPet(sim, b, H) {
  const P = H.pet;
  const dmgMult = () => (1 + H.unleashedFury.pet * b.unleashedFury) * (1 + H.focusedFire.dmg * b.focusedFire) * (sim.aWrath.active ? H.bestialWrath.dmg : 1);
  const hasteNow = () => (sim.aFrenzy.active ? H.frenzy.haste : 1);
  const hit = (name, base) => {
    const e = sim.entry(name), r = sim.rng();
    if (r < P.miss) { e.misses++; return; }
    if (r < P.miss + P.dodge) { e.dodges++; return; }
    const apPet = sim.ap() * P.apFrac;
    let d = (base + apPet / 14 * P.speed) * dmgMult();
    const crit = sim.rng() < P.crit + H.ferocity.petCrit * b.ferocity;
    if (crit) { d *= 2; if (b.frenzy) sim.aFrenzy.apply(); }
    sim.record(name, sim.mitigate(d, true), crit ? 'crit' : 'hit');
  };
  const swing = () => { hit('Pet (melee)', P.min + (P.max - P.min) * sim.rng()); sim.schedule(P.speed / hasteNow(), swing); };
  const special = () => { hit('Pet (Claw)', P.special.flat); sim.schedule(P.special.every / hasteNow(), special); };
  sim.schedule(0.8, swing); sim.schedule(1.2, special);
}

// ---- rotation ----
function hunterRotate(sim, b, H) {
  const now = sim.now, rem = sim.fightLen - now;
  if (sim.casting) return sim.casting.endsAt - now;
  if (b.usePotion && now >= sim.cd.potion && sim.mana <= sim.manaMax - (H.manaPotion.min + H.manaPotion.max) / 2 && rem > 20) {
    sim.cd.potion = now + H.manaPotion.cd; sim.entry('Mana Potion').casts++;
    gainMana(sim, H.manaPotion.min + (H.manaPotion.max - H.manaPotion.min) * sim.rng());
  }
  if (b.useGem && now >= sim.cd.gem && sim.mana <= sim.manaMax - (H.manaGem.min + H.manaGem.max) / 2 && rem > 15) {
    sim.cd.gem = now + H.manaGem.cd; sim.entry('Mana Gem').casts++;
    gainMana(sim, H.manaGem.min + (H.manaGem.max - H.manaGem.min) * sim.rng());
  }
  const cost = (s) => Math.round(s.cost * (1 - H.efficiency.cost * b.efficiency));
  if (b.useCooldowns) {
    const rfCd = Math.max(60, H.rapidFire.cd - H.rapidKilling.cd * b.rapidKilling);
    if (now >= sim.cd.rapid && sim.mana >= H.rapidFire.cost) { sim.cd.rapid = now + rfCd; sim.entry('Rapid Fire').casts++; spendMana(sim, H.rapidFire.cost); sim.aRapid.apply(); }
    if (b.bestialWrath && sim.petOn && now >= sim.cd.wrath) { sim.cd.wrath = now + H.bestialWrath.cd; sim.entry('Bestial Wrath').casts++; sim.aWrath.apply(); }
    if (b.summonHawk && now >= sim.cd.hawk && sim.mana >= H.hawk.cost) {
      sim.cd.hawk = now + H.hawk.cd; sim.entry(H.hawk.name).casts++; spendMana(sim, H.hawk.cost);
      for (let i = 1; i <= Math.floor(H.hawk.duration / H.hawk.every); i++) sim.schedule(i * H.hawk.every, () => {
        const e = sim.entry('Hawk');
        const r = sim.resolveYellow(0, false);
        if (r === 'miss') { e.misses++; return; }
        let d = (H.hawk.flat + sim.ap() * H.hawk.rapFrac) * (1 + H.unleashedFury.pet * b.unleashedFury) * sim.dmgGlobal;
        if (r === 'crit') d *= sim.critMult();
        sim.record('Hawk', sim.mitigate(d, true), r);
      });
    }
  }
  const gcdLeft = sim.gcdReadyAt - now;
  if (gcdLeft > 1e-9) return gcdLeft;
  const mana = sim.mana, reserve = 0.05 * sim.manaMax;
  const afford = (s) => mana - cost(s) >= reserve;
  const cast = (s, flat, extraMult = 1, onLand) => {
    sim.gcdReadyAt = now + 1.5; spendMana(sim, cost(s)); sim.entry(s.name).casts++;
    const run = () => {
      const o = shot(sim, s.name, flat, extraMult, 0, false);
      if (onLand) onLand(o);
    };
    if (s.cast) {
      const t = s.cast / sim.hasteMult();
      sim.casting = { name: s.name, endsAt: now + t };
      sim.schedule(t, () => { sim.casting = null; run(); sim.poke(0); });
      return t;
    }
    run();
    return 1.5;
  };
  // the sting first
  if (sim.serpentEnds - now <= H.serpent.interval && rem > 8 && afford(H.serpent)) {
    sim.gcdReadyAt = now + 1.5; spendMana(sim, cost(H.serpent)); sim.entry(H.serpent.name).casts++;
    const o = sim.resolveYellow(0, false);
    if (o === 'miss') sim.entry(H.serpent.name).misses++;
    else {
      sim.serpentEnds = now + H.serpent.ticks * H.serpent.interval;
      const per = H.serpent.total / H.serpent.ticks * (1 + H.improvedStings.dmg * b.improvedStings) * sim.dmgGlobal;
      const critP = sim.critChance(0), cm = sim.critMult();
      const my = (sim.stingToken = (sim.stingToken || 0) + 1);
      let n = 0;
      const tick = () => { if (sim.stingToken !== my) return; const c = sim.rng() < critP; sim.record(H.serpent.name, per * (c ? cm : 1) * (1 - sim.dr), c ? 'crit' : 'hit'); if (++n < H.serpent.ticks) sim.schedule(H.serpent.interval, tick); };
      sim.schedule(H.serpent.interval, tick);
    }
    return 1.5;
  }
  const arcCd = Math.max(1.5, H.arcane.cd - H.improvedArcane.cd * b.improvedArcane);
  // Arcane Shot on its own cooldown, then the shared Multi-Shot / Aimed Shot slot (Multi-Shot unless Aimed Shot pays for its cast time)
  if (now >= sim.cd.arcane && afford(H.arcane)) { sim.cd.arcane = now + arcCd; return cast(H.arcane, H.arcane.flat, 1); }
  // Sniper Shot's 4 s cast stops Auto Shot: only worth it when its damage beats the shots it displaces
  const avgShot = (sim.rw.min + sim.rw.max) / 2 + H.ammoDps * sim.rw.speed + sim.ap() / 14 * sim.rw.speed;
  const sniperPays = H.sniper.flat + avgShot > (H.sniper.cast / sim.hasteMult()) / (sim.rw.speed / sim.hasteMult()) * avgShot * 1.05;
  if (b.sniperShot && sniperPays && now >= sim.cd.sniper && afford(H.sniper) && rem > 5) { sim.cd.sniper = now + H.sniper.cd; return cast(H.sniper, H.sniper.flat, 1); }
  if (now >= sim.cd.shared) {
    const useAimed = b.shots === 'aimed';
    const s = useAimed ? H.aimed : H.multi;
    if (afford(s)) { sim.cd.shared = now + s.cd; return cast(s, s.flat, 1 + (H.barrage.dmg * b.barrage)); }
  }
  // nothing to cast: wake up when the next ability comes off cooldown (Auto Shot keeps firing on its own)
  const next = Math.min(sim.cd.arcane, sim.cd.shared, b.sniperShot ? sim.cd.sniper : Infinity, Math.max(now + 0.5, sim.serpentEnds - H.serpent.interval));
  return Math.max(0.1, next - now);
}

// ---- priest.js ----
// Shadow Priest kit. Spell numbers come from the client tables (rank ladders in data/spells60.json: top / extra): Shadow Word: Pain,
// Mind Blast, Mind Flay, Shadow Word: Death, Devouring Plague. Talent numbers come from the Forever tooltips. ASSUMED (Classic
// style): Power Infusion and Inner Focus cooldowns, Smite as the filler of a build without Mind Flay, mana items, base mana.
// Periodic effects use the client's per-tick coefficient and can crit. Not simulated: Vampiric Embrace healing, Spirit Tap,
// Silence, the Holy and Discipline spells other than the ones listed.

const PRIEST = {
  shadowFocus: { hit: 0.01 }, improvedSwp: { ticks: 1 }, improvedMindBlast: { cd: 0.5 }, improvedMindFlay: { dmg: 0.10 }, shadowWeaving: { dmg: 0.02, max: 5, dur: 15 },
  darkness: { dmg: 0.02 }, shadowform: { dmg: 0.10, cost: 0.5, critBonus: 1 }, devouringContagion: { cost: 0.25 }, twinDisciplines: { dmg: 0.01 }, mentalAgility: { cost: 1 / 30 },
  mentalStrength: { int: 0.03 }, meditation: { keep: 1 / 6 }, powerInfusion: { dmg: 1.2, dur: 15, cd: 180 }, innerFocus: { crit: 0.25, cd: 180 },   // cooldowns ASSUMED
  manaPotion: { cd: 120, min: 1350, max: 2250 }, manaGem: { cd: 120, min: 1073, max: 1127 },
};

const PRIEST_DEFAULT_BUILD = {
  shadowFocus: 0, improvedSwp: 0, improvedMindBlast: 0, mindFlay: 0, improvedMindFlay: 0, shadowWeaving: 0, darkness: 0, shadowform: 0, devouringContagion: 0,
  twinDisciplines: 0, mentalAgility: 0, mentalStrength: 0, meditation: 0, powerInfusion: 0, innerFocus: 0,
  useCooldowns: true, usePotion: true, useGem: true, devouringPlague: true, shadowWordDeath: true,
};

function priestKit(build = {}, data = null) {
  const b = Object.assign({}, PRIEST_DEFAULT_BUILD, build), P = PRIEST;
  const sh = ['shadow'];
  const swp = pickRank(data, 'priest', 'priest_shadow_word_pain', 'Shadow Word: Pain'), mb = pickRank(data, 'priest', 'priest_mind_blast', 'Mind Blast');
  const mf = pickRank(data, 'priest', null, 'Mind Flay'), swd = pickRank(data, 'priest', null, 'Shadow Word: Death'), dp = pickRank(data, 'priest', null, 'Devouring Plague');
  const sm = pickRank(data, 'priest', 'priest_smite', 'Smite');
  const S = {};
  if (swp) S.swp = fromRank(swp, { name: 'Shadow Word: Pain', schools: sh, instant: true });
  if (mb) S.mb = fromRank(mb, { name: 'Mind Blast', schools: sh });
  if (mf) { const t = fromRank(mf); S.mf = { name: 'Mind Flay', schools: sh, cost: t.cost, cast: 0, channel: { perTick: t.dot.perTick, ticks: t.dot.ticks, interval: t.dot.interval, coeff: t.dot.coeff } }; }
  if (swd) S.swd = fromRank(swd, { name: 'Shadow Word: Death', schools: sh, instant: true });
  if (dp) S.dp = fromRank(dp, { name: 'Devouring Plague', schools: sh, instant: true });
  if (sm) S.smite = fromRank(sm, { name: 'Smite', schools: ['holy'] });
  const def = {
    name: 'priest', build: b, S,
    items: { potion: P.manaPotion, gem: P.manaGem },
    baseMana: (sim) => sim.stats.mana + Math.floor((sim.stats.int || 0) * P.mentalStrength.int * b.mentalStrength) * 15,
    keep: () => P.meditation.keep * b.meditation,
    setup(sim) {
      const extraInt = Math.floor((sim.stats.int || 0) * P.mentalStrength.int * b.mentalStrength);
      sim.critBase = extraInt / 59.2 / 100;
      sim.aWeave = sim.addAura({ name: 'Shadow Weaving', duration: P.shadowWeaving.dur, maxStacks: P.shadowWeaving.max });
      sim.aPI = sim.addAura({ name: 'Power Infusion', duration: P.powerInfusion.dur });
      sim.innerFocus = false;
      sim.est = (s) => 0;
    },
    mods(sim, s, kind) {
      let hit = 0, crit = sim.critBase, dmg = 1, critBonus = 0;
      if (s.schools[0] === 'shadow') {
        hit += P.shadowFocus.hit * b.shadowFocus;
        dmg *= (1 + P.darkness.dmg * b.darkness) * (b.shadowform ? 1 + P.shadowform.dmg : 1) * (1 + P.shadowWeaving.dmg * sim.aWeave.stacks);
        if (b.shadowform) critBonus += P.shadowform.critBonus;
      }
      if (s.instant) dmg *= 1 + P.twinDisciplines.dmg * b.twinDisciplines;
      if (s === def.S.mf) dmg *= 1 + P.improvedMindFlay.dmg * b.improvedMindFlay;
      if (sim.aPI.active) dmg *= P.powerInfusion.dmg;
      if (sim.innerFocus && s.direct) crit += P.innerFocus.crit;
      return { hit, crit, dmg, critBonus };
    },
    castTime: (sim, s) => s.cast,
    cost(sim, s) {
      if (sim.innerFocus) return 0;
      let c = s.cost;
      if (b.shadowform && s.schools[0] === 'shadow') c *= 1 - P.shadowform.cost;
      if (s.instant) c *= 1 - P.mentalAgility.cost * b.mentalAgility;
      if (s === def.S.dp) c *= 1 - P.devouringContagion.cost * b.devouringContagion;
      return Math.round(c);
    },
    beforeCast(sim, s) { if (sim.innerFocus) sim.innerFocus = false; },
    afterHit(sim, s, outcome) { if (outcome !== 'miss' && s.schools[0] === 'shadow' && !s.dot && b.shadowWeaving && sim.rng() < Math.min(1, b.shadowWeaving / 3)) sim.aWeave.apply(1); },
    offGcd(sim) {
      if (!b.useCooldowns) return;
      if (b.powerInfusion && sim.now >= (sim.cdAt.pi || 0)) { sim.cdAt.pi = sim.now + P.powerInfusion.cd; sim.entry('Power Infusion').casts++; sim.aPI.apply(); }
      if (b.innerFocus && sim.now >= (sim.cdAt.focus || 0) && !sim.innerFocus) { sim.cdAt.focus = sim.now + P.innerFocus.cd; sim.entry('Inner Focus').casts++; sim.innerFocus = true; }
    },
    choose(sim) {
      const now = sim.now, ready = (s) => now >= (sim.cdAt[s.name] || 0) - 1e-9, rem = sim.fightLen - now;
      if (S.swp && rem > 6 && dotLeft(sim, S.swp.name) < 0.6) return S.swp;
      if (S.dp && b.devouringPlague && ready(S.dp) && rem > 12 && !dotActive(sim, S.dp.name)) return S.dp;
      if (S.mb && ready(S.mb)) return S.mb;
      if (S.swd && b.shadowWordDeath && ready(S.swd)) return S.swd;
      if (S.mf && b.mindFlay) return S.mf;
      return b.shadowform ? S.mb : S.smite || S.mb;
    },
  };
  if (S.mb) S.mb.cdBase = S.mb.cd;
  const kit = makeCaster(def);
  const baseSetup = kit.setup;
  kit.setup = (sim) => { if (S.mb) S.mb.cd = S.mb.cdBase - P.improvedMindBlast.cd * b.improvedMindBlast; if (S.swp) S.swp.dotTicks = () => S.swp.dot.ticks + P.improvedSwp.ticks * b.improvedSwp; baseSetup(sim); };
  return kit;
}

// ---- shaman.js ----
// Shaman kits. Elemental: Lightning Bolt, Chain Lightning, Lava Burst, Flame Shock and Earth Shock from the client's rank ladders
// (data/spells60.json: top / extra) and the Forever talent tooltips. ASSUMED (Classic style): base mana, mana items; the Searing Totem
// (a few damage per second) and the elemental melee crit from Elemental Devastation are not simulated.

const SHAMAN = {
  convection: { cost: 0.02 }, concussion: { dmg: 0.01 }, reverberation: { cd: 0.2 }, callOfFlame: { dmg: 0.05 }, elementalFocus: { chance: 0.10 }, elementalAlacrity: { cast: 1 / 6 },
  thunderingStrikes: { crit: 0.01 }, ancestralKnowledge: { int: 0.02 }, callOfThunder: { crit: 0.03 }, lightningOverload: { chance: 0.10 / 3, dmg: 0.5 }, elementalFury: { critBonus: 0.2 }, lavaBurstFs: 1.2,
  manaPotion: { cd: 120, min: 1350, max: 2250 }, manaGem: { cd: 120, min: 1073, max: 1127 },
};

const SHAMAN_ELE_DEFAULT_BUILD = {
  convection: 0, concussion: 0, reverberation: 0, callOfFlame: 0, elementalFocus: 0, elementalAlacrity: 0, callOfThunder: 0, lightningOverload: 0, elementalFury: 0, lavaBurst: 0, thunderingStrikes: 0, ancestralKnowledge: 0,
  useCooldowns: true, usePotion: true, useGem: true, earthShock: false,
};

function shamanElementalKit(build = {}, data = null) {
  const b = Object.assign({}, SHAMAN_ELE_DEFAULT_BUILD, build), H = SHAMAN;
  const na = ['nature'], fi = ['fire'];
  const lb = pickRank(data, 'shaman', 'shaman_lightning_bolt', 'Lightning Bolt'), cl = pickRank(data, 'shaman', null, 'Chain Lightning'), lv = pickRank(data, 'shaman', null, 'Lava Burst');
  const fs = pickRank(data, 'shaman', 'shaman_flame_shock', 'Flame Shock'), es = pickRank(data, 'shaman', 'shaman_earth_shock', 'Earth Shock');
  const S = {};
  if (lb) S.lb = fromRank(lb, { name: 'Lightning Bolt', schools: na, bolt: true });
  if (cl) S.cl = fromRank(cl, { name: 'Chain Lightning', schools: na, bolt: true });
  if (lv) S.lvb = fromRank(lv, { name: 'Lava Burst', schools: fi, bolt: true });
  if (fs) S.fs = fromRank(fs, { name: 'Flame Shock', schools: fi, shock: true, instant: true });
  if (es) S.es = fromRank(es, { name: 'Earth Shock', schools: na, shock: true, instant: true });
  const def = {
    name: 'shaman_elemental', build: b, S,
    items: { potion: H.manaPotion, gem: H.manaGem },
    baseMana: (sim) => sim.stats.mana + 15 * Math.floor((sim.stats.int || 0) * H.ancestralKnowledge.int * b.ancestralKnowledge),
    keep: () => 0,
    setup(sim) {
      sim.aClear = sim.addAura({ name: 'Clearcasting', duration: Infinity });
      sim.spBonus = 0;
      sim.critBase = H.thunderingStrikes.crit * b.thunderingStrikes + Math.floor((sim.stats.int || 0) * H.ancestralKnowledge.int * b.ancestralKnowledge) / 59.5 / 100;
    },
    mods(sim, s, kind) {
      let hit = 0, crit = sim.critBase, dmg = 1, critBonus = H.elementalFury.critBonus * b.elementalFury;
      if (s === S.lb || s === S.cl) { dmg *= 1 + H.concussion.dmg * b.concussion; crit += H.callOfThunder.crit * b.callOfThunder; }
      if (s === S.es) dmg *= 1 + H.concussion.dmg * b.concussion;
      if (s.schools[0] === 'fire' && (s === S.fs || s === S.lvb)) dmg *= 1 + H.callOfFlame.dmg * b.callOfFlame;
      if (s === S.lvb && dotActive(sim, S.fs ? S.fs.name : '')) dmg *= H.lavaBurstFs;
      return { hit, crit, dmg, critBonus };
    },
    castTime: (sim, s) => (s.bolt ? Math.max(0.5, s.cast - H.elementalAlacrity.cast * b.elementalAlacrity) : s.cast),
    cost(sim, s) {
      if (sim.aClear.active) return 0;
      return Math.round(s.cost * (s.bolt || s.shock ? 1 - H.convection.cost * b.convection : 1));
    },
    beforeCast(sim, s) { if (sim.aClear.active) sim.aClear.expire(); if (s.shock) sim.cdAt.shock = sim.now + Math.max(1.5, 6 - H.reverberation.cd * b.reverberation * 5); },
    afterHit(sim, s, outcome) {
      if (outcome === 'miss') return;
      if (b.elementalFocus && !s.dot && sim.rng() < H.elementalFocus.chance) sim.aClear.apply();
      if (b.lightningOverload && (s === S.lb || s === S.cl) && sim.rng() < H.lightningOverload.chance * b.lightningOverload) {
        const e = sim.entry(s.name + ' (Overload)'), m = def.mods(sim, s, 'direct');
        const raw = (s.direct.min + (s.direct.max - s.direct.min) * sim.rng() + sim.stats.sp * s.direct.coeff) * H.lightningOverload.dmg;
        const c = sim.rng() < Math.max(0, Math.min(1, sim.stats.crit + m.crit));
        const d = raw * m.dmg * (1 - sim.target.spellMitigation) * sim.target.spellTaken * (c ? 1 + 0.5 * (1 + m.critBonus) : 1);
        e.casts++; sim.record(s.name + ' (Overload)', d, c ? 'crit' : 'hit');
      }
    },
    choose(sim) {
      const now = sim.now, ready = (s) => now >= (sim.cdAt[s.name] || 0) - 1e-9, rem = sim.fightLen - now;
      const shockReady = now >= (sim.cdAt.shock || 0) - 1e-9;
      if (S.fs && shockReady && rem > 6 && dotLeft(sim, S.fs.name) < 1.0) return S.fs;
      if (S.lvb && b.lavaBurst && ready(S.lvb)) return S.lvb;
      if (S.es && b.earthShock && shockReady) return S.es;
      if (S.cl && ready(S.cl)) return S.cl;
      return S.lb;
    },
  };
  return makeCaster(def);
}

// ---------------------------------------------------------------------------------------------------------------------------
// Enhancement: melee (dual wield or two-hand) with Stormstrike, Flurry, Maelstrom Weapon (instant Lightning Bolts) and Windfury Weapon.
// Numbers: Stormstrike and Lightning Bolt from the client's rank ladders, talents from the Forever tooltips. ASSUMED (Classic style):
// Windfury Weapon (20% per main-hand hit, one extra attack with +315 attack power), Rockbiter's +118 attack power kept on, Maelstrom
// Weapon's proc chance (3% per rank per melee hit), Rage of the Farseer's cooldown, melee crit used for the Lightning Bolt crit.

const SHAMAN_ENH = {
  stormstrike: { cost: 125, cd: 8, nature: 1.2, dur: 12 }, rockbiter: { ap: 118 }, windfury: { chance: 0.20, ap: 315 },
  flurry: { perRank: 0.05, charges: 3, expire: 15 }, maelstrom: { chancePerRank: 0.03, max: 5, dur: 30 }, farseer: { haste: 1.3, dur: 25, cd: 180 },
  thunderingStrikes: { crit: 0.01 }, ancestralKnowledge: { int: 0.02 }, mentalDexterity: { ap: 1 / 3 }, mentalQuickness: { sp: 0.15 }, elementalWeapons: { rock: 0.2 / 3, wf: 0.4 / 3 },
  manaPotion: { cd: 120, min: 1350, max: 2250 }, manaGem: { cd: 120, min: 1073, max: 1127 },
};

const SHAMAN_ENH_DEFAULT_BUILD = {
  thunderingStrikes: 0, ancestralKnowledge: 0, mentalDexterity: 0, mentalQuickness: 0, elementalWeapons: 0, flurry: 0, stormstrike: 0, maelstromWeapon: 0, rageOfTheFarseer: 0,
  windfuryWeapon: true, rockbiter: true, useCooldowns: true, usePotion: true, useGem: true,
};

function shamanEnhancementKit(build = {}, data = null) {
  const b = Object.assign({}, SHAMAN_ENH_DEFAULT_BUILD, build), E = JSON.parse(JSON.stringify(SHAMAN_ENH));
  const lb = pickRank(data, 'shaman', 'shaman_lightning_bolt', 'Lightning Bolt'), ss = pickRank(data, 'shaman', null, 'Stormstrike'), rb = pickRank(data, 'shaman', 'shaman_rockbiter_weapon', 'Rockbiter Weapon');
  const L = lb ? fromRank(lb) : null;
  if (ss) { E.stormstrike.cost = ss.cost.amount; E.stormstrike.cd = ss.cooldown_ms / 1000; }
  return {
    name: 'shaman_enhancement', build: b, E,
    setup(sim) {
      sim.player.resource = 'mana'; sim.kitBuild = b;
      const st = sim.stats, mods = sim.mods, mh = sim.player.weapons[0] || {};
      const extraInt = Math.floor((st.int || 0) * E.ancestralKnowledge.int * b.ancestralKnowledge), int = (st.int || 0) + extraInt;
      mods.apBonus += Math.floor(int * E.mentalDexterity.ap * b.mentalDexterity) + (b.rockbiter ? E.rockbiter.ap * (1 + E.elementalWeapons.rock * b.elementalWeapons) : 0);
      mods.critBonus += E.thunderingStrikes.crit * b.thunderingStrikes;
      sim.spBonus = Math.floor(int * E.mentalQuickness.sp * b.mentalQuickness);
      setupMana(sim, { manaMax: st.mana + 15 * extraInt, mp5: st.mp5 || 0, spiritRegen: spiritRegenPerSec({ int, spi: st.spi }), castingFraction: 0 });
      sim.cd = { ss: 0, farseer: 0, potion: 0, gem: 0 };
      sim.flurryAura = sim.addAura({ name: 'Flurry', duration: E.flurry.expire, mods: { hasteMult: 1 + E.flurry.perRank * b.flurry } });
      sim.flurryAura.charges = 0;
      sim.aMW = sim.addAura({ name: 'Maelstrom Weapon', duration: E.maelstrom.dur, maxStacks: E.maelstrom.max });
      sim.aSS = sim.addAura({ name: 'Stormstrike', duration: E.stormstrike.dur });
      sim.aFar = sim.addAura({ name: 'Rage of the Farseer', duration: E.farseer.dur, mods: { hasteMult: E.farseer.haste } });
      const consume = (s) => { const a = s.flurryAura; if (a.active && --a.charges <= 0) a.expire(); };
      sim.procs.push((s, outcome, source, isOH, isWhite) => {
        if (isWhite) consume(s);
        if (outcome === 'miss' || outcome === 'dodge') return;
        if (outcome === 'crit' && b.flurry > 0) { s.flurryAura.charges = E.flurry.charges; s.flurryAura.apply(1); }
        if (b.maelstromWeapon && s.rng() < E.maelstrom.chancePerRank * b.maelstromWeapon) s.aMW.apply(1);
        if (b.windfuryWeapon && !s.inWindfury && !isOH && (isWhite || source === 'Stormstrike') && s.rng() < E.windfury.chance) {
          const bonus = E.windfury.ap * (1 + E.elementalWeapons.wf * b.elementalWeapons);
          s.entry('Windfury').casts++;
          s.inWindfury = true; s.mods.apBonus += bonus; s.whiteAttack(s.swings[0]); s.mods.apBonus -= bonus; s.inWindfury = false;
        }
      });
    },
    rotate(sim) {
      const now = sim.now, rem = sim.fightLen - now;
      if (b.usePotion && now >= sim.cd.potion && sim.mana <= sim.manaMax - 1800 && rem > 20) { sim.cd.potion = now + E.manaPotion.cd; sim.entry('Mana Potion').casts++; gainMana(sim, E.manaPotion.min + (E.manaPotion.max - E.manaPotion.min) * sim.rng()); }
      if (b.useGem && now >= sim.cd.gem && sim.mana <= sim.manaMax - 1100 && rem > 15) { sim.cd.gem = now + E.manaGem.cd; sim.entry('Mana Gem').casts++; gainMana(sim, E.manaGem.min + (E.manaGem.max - E.manaGem.min) * sim.rng()); }
      if (b.useCooldowns && b.rageOfTheFarseer && now >= sim.cd.farseer) { sim.cd.farseer = now + E.farseer.cd; sim.entry('Rage of the Farseer').casts++; sim.aFar.apply(); }
      const gcdLeft = Math.max(0, sim.gcdReadyAt - now);
      if (gcdLeft > 0) return gcdLeft;
      // five Maelstrom Weapon stacks: an instant, free Lightning Bolt
      if (L && sim.aMW.active && sim.aMW.stacks >= E.maelstrom.max) {
        sim.aMW.expire(); sim.gcdReadyAt = now + 1.5; sim.entry('Lightning Bolt').casts++;
        const m = { hit: 0, crit: 0, dmg: sim.aSS.active ? E.stormstrike.nature : 1, critBonus: 0 };
        if (sim.aSS.active) sim.aSS.expire();
        const raw = L.direct.min + (L.direct.max - L.direct.min) * sim.rng() + (sim.stats.sp + sim.spBonus) * L.direct.coeff;
        resolveSpell(sim, 'Lightning Bolt', raw, { ...m, crit: sim.mods.critBonus });
        return 1.5;
      }
      if (b.stormstrike && now >= sim.cd.ss && sim.mana >= E.stormstrike.cost && sim.player.weapons.length) {
        sim.cd.ss = now + E.stormstrike.cd; spendMana(sim, E.stormstrike.cost); sim.lastCastAt = now; sim.gcdReadyAt = now + 1.5; sim.entry('Stormstrike').casts++;
        const norm = sim.player.dualWield ? 2.4 : 3.3, mh = sim.player.weapons[0], oh = sim.player.weapons[1];
        yellowAttack(sim, 'Stormstrike', () => sim.weaponRoll(mh) + sim.ap() / 14 * norm);
        if (oh) yellowAttack(sim, 'Stormstrike (off-hand)', () => (sim.weaponRoll(oh) + sim.ap() / 14 * norm) * 0.5);
        sim.aSS.apply();
        return 1.5;
      }
      const next = Math.min(b.stormstrike ? sim.cd.ss : Infinity, b.rageOfTheFarseer ? sim.cd.farseer : Infinity);
      return Math.max(0.1, Math.min(0.5, next - now));
    },
  };
}

// ---- druid.js ----
// Druid kits. Balance: Wrath, Starfire, Moonfire and Insect Swarm from the client's rank ladders (data/spells60.json: top / extra) and the
// Forever talent tooltips (Eclipse, Nature's Grace, Moonfury...). ASSUMED (Classic style): base mana, mana items, the Moonkin Aura crit
// applied to the druid itself. Not simulated: Omen of Clarity, Hurricane, Starfall-style effects.

const DRUID = {
  improvedWrath: { cast: 0.1, cost: 0.10 }, genesis: { dmg: 0.01 }, moonglow: { cost: 0.25 / 3 }, improvedMoonfire: { dmg: 0.05, crit: 0.05 }, naturesMajesty: { crit: 0.02 },
  naturesReach: { hit: 0.02 }, naturesSplendor: { moonfire: 1, swarm: 1 }, vengeance: { critBonus: 0.2 }, improvedStarfire: { cast: 0.1 }, naturesGrace: { haste: 1.1, dur: 3 },
  naturalist: { dmg: 0.01 }, eclipse: { cast: 0.5, charges: 2, max: 4, dur: 15 }, moonfury: { dmg: 0.02 }, moonkinAura: { crit: 0.03 },
  manaPotion: { cd: 120, min: 1350, max: 2250 }, manaGem: { cd: 120, min: 1073, max: 1127 },
};

const DRUID_BAL_DEFAULT_BUILD = {
  improvedWrath: 0, genesis: 0, moonglow: 0, improvedMoonfire: 0, naturesMajesty: 0, naturesReach: 0, naturesSplendor: 0, insectSwarm: 0, vengeance: 0, improvedStarfire: 0,
  naturesGrace: 0, eclipse: 0, moonfury: 0, moonkinForm: 0, naturalist: 0,
  useCooldowns: true, usePotion: true, useGem: true,
};

function druidBalanceKit(build = {}, data = null) {
  const b = Object.assign({}, DRUID_BAL_DEFAULT_BUILD, build), D = DRUID;
  const wr = pickRank(data, 'druid', 'druid_wrath', 'Wrath'), sf = pickRank(data, 'druid', null, 'Starfire'), mf = pickRank(data, 'druid', 'druid_moonfire', 'Moonfire'), isw = pickRank(data, 'druid', null, 'Insect Swarm');
  const S = {};
  if (wr) S.wrath = fromRank(wr, { name: 'Wrath', schools: ['nature'], wrath: true });
  if (sf) S.starfire = fromRank(sf, { name: 'Starfire', schools: ['arcane'], starfire: true });
  if (mf) S.moonfire = fromRank(mf, { name: 'Moonfire', schools: ['arcane'], instant: true, moonfire: true });
  if (isw) S.swarm = fromRank(isw, { name: 'Insect Swarm', schools: ['nature'], instant: true, swarm: true });
  const def = {
    name: 'druid_balance', build: b, S,
    items: { potion: D.manaPotion, gem: D.manaGem },
    baseMana: (sim) => sim.stats.mana,
    keep: () => 0,
    setup(sim) {
      sim.aGrace = sim.addAura({ name: "Nature's Grace", duration: D.naturesGrace.dur, mods: { hasteMult: D.naturesGrace.haste } });
      sim.aEclipse = sim.addAura({ name: 'Eclipse', duration: D.eclipse.dur, maxStacks: D.eclipse.max });
      sim.critBase = D.naturesMajesty.crit * b.naturesMajesty + (b.moonkinForm ? D.moonkinAura.crit : 0);
      sim.spBonus = 0;
    },
    mods(sim, s, kind) {
      let hit = D.naturesReach.hit * b.naturesReach, crit = sim.critBase, dmg = 1, critBonus = D.vengeance.critBonus * b.vengeance;
      dmg *= (1 + D.moonfury.dmg * b.moonfury) * (1 + D.naturalist.dmg * b.naturalist);
      if (kind === 'dot') dmg *= 1 + D.genesis.dmg * b.genesis;
      if (s.moonfire) { dmg *= 1 + D.improvedMoonfire.dmg * b.improvedMoonfire; crit += D.improvedMoonfire.crit * b.improvedMoonfire; }
      return { hit, crit, dmg, critBonus };
    },
    castTime(sim, s) {
      let t = s.cast;
      if (s.wrath) t -= D.improvedWrath.cast * b.improvedWrath;
      if (s.starfire) { t -= D.improvedStarfire.cast * b.improvedStarfire; if (sim.aEclipse.active) t -= D.eclipse.cast; }
      return Math.max(0.5, t);
    },
    cost(sim, s) {
      let c = s.cost;
      if (s.wrath) c *= 1 - D.improvedWrath.cost * b.improvedWrath;
      c *= 1 - D.moonglow.cost * b.moonglow;
      return Math.round(c);
    },
    beforeCast(sim, s) { if (s.starfire && sim.aEclipse.active) sim.aEclipse.consumeStack(); },
    afterHit(sim, s, outcome) {
      if (outcome === 'miss') return;
      if (s.wrath && b.eclipse) sim.aEclipse.apply(D.eclipse.charges);
      if (outcome === 'crit' && !s.dot && b.naturesGrace) sim.aGrace.apply();
    },
    choose(sim) {
      const now = sim.now, rem = sim.fightLen - now;
      if (S.swarm && b.insectSwarm && rem > 6 && dotLeft(sim, S.swarm.name) < 0.8) return S.swarm;
      if (S.moonfire && rem > 6 && dotLeft(sim, S.moonfire.name) < 0.8) return S.moonfire;
      if (sim.aEclipse.active && S.starfire) return S.starfire;
      return S.wrath;
    },
  };
  if (S.moonfire) S.moonfire.dotTicks = () => S.moonfire.dot.ticks + D.naturesSplendor.moonfire * b.naturesSplendor * 1;
  if (S.swarm) S.swarm.dotTicks = () => S.swarm.dot.ticks + b.naturesSplendor;
  return makeCaster(def);
}

// ---------------------------------------------------------------------------------------------------------------------------
// Feral (cat): energy and combo points like the Rogue, Claw / Shred / Rake as builders, Rip and Ferocious Bite as finishers. Numbers from
// the client's rank ladders (Claw, Shred, Rake, Rip, Ferocious Bite) and the Forever talent tooltips. ASSUMED (Classic style): the cat's
// natural weapon (speed 1.0, 17-25 damage), attack power from Strength and Agility (2 per Strength, 1 per Agility), 20 energy per 2 s,
// being behind the target for Shred. Not simulated: Berserk, Tiger's Fury, Primal Bite, Swipe, Ravage, feral weapon attack power.

const DRUID_FERAL = {
  energy: { cap: 100, tick: 2, perTick: 20 }, natural: { min: 17, max: 25, speed: 1.0 },
  claw: { cost: 45, flat: 115, pct: 1.10 }, shred: { cost: 60, flat: 80, pct: 1.55 }, rake: { cost: 40, direct: 61, tick: 34, ticks: 3, interval: 3 },
  rip: { cost: 30, base: 15, perCp: 25.5, ticks: 6, interval: 2 }, bite: { cost: 35, base: 82, var: 0.73, perCp: 147 },
  ferocity: { cost: 1 }, shreddingAttacks: { cost: 6 }, savageFury: { dmg: 0.05 }, sharpenedClaws: { crit: 0.03 }, predatoryStrikes: { ap: 30 }, predatoryInstincts: { critDmg: 0.1 },
  rendAndTear: { dmg: 0.02 }, heartOfTheWild: { str: 0.02 }, leaderOfThePack: { crit: 0.03 }, naturesMajesty: { crit: 0.02 },
};

const DRUID_FERAL_DEFAULT_BUILD = {
  ferocity: 0, shreddingAttacks: 0, savageFury: 0, sharpenedClaws: 0, predatoryStrikes: 0, predatoryInstincts: 0, rendAndTear: 0, heartOfTheWild: 0, leaderOfThePack: 0, naturesMajesty: 0,
  behind: true,
};

function druidFeralKit(build = {}, data = null) {
  const b = Object.assign({}, DRUID_FERAL_DEFAULT_BUILD, build), F = JSON.parse(JSON.stringify(DRUID_FERAL));
  const cl = pickRank(data, 'druid', 'druid_claw', 'Claw'), sh = pickRank(data, 'druid', null, 'Shred'), rk = pickRank(data, 'druid', null, 'Rake'), rp = pickRank(data, 'druid', 'druid_rip', 'Rip'), fb = pickRank(data, 'druid', null, 'Ferocious Bite');
  const eff = (r, e, a) => r && r.effects.find((x) => x.effect === e && (a === undefined || x.aura === a));
  if (cl) { F.claw.cost = cl.cost.amount; F.claw.flat = eff(cl, 58).base; F.claw.pct = eff(cl, 31).base / 100; }
  if (sh) { F.shred.cost = sh.cost.amount; F.shred.flat = eff(sh, 58).base; F.shred.pct = eff(sh, 31).base / 100; }
  if (rk) { F.rake.cost = rk.cost.amount; F.rake.direct = eff(rk, 2).base; const d = eff(rk, 6, 3); F.rake.tick = d.base; F.rake.interval = d.period_ms / 1000; F.rake.ticks = Math.round(rk.duration_ms / d.period_ms); }
  if (rp) { F.rip.cost = rp.cost.amount; const d = eff(rp, 6, 3); F.rip.base = d.base; F.rip.perCp = d.per_resource; F.rip.interval = d.period_ms / 1000; F.rip.ticks = Math.round(rp.duration_ms / d.period_ms); }
  if (fb) { F.bite.cost = fb.cost.amount; const d = eff(fb, 2); F.bite.base = d.base; F.bite.var = d.variance; F.bite.perCp = d.per_resource; }
  return {
    name: 'druid_feral', build: b, F,
    setup(sim) {
      sim.player.resource = 'energy'; sim.kitBuild = b;
      const mods = sim.mods;
      sim.player = Object.assign({}, sim.player, { weapons: [{ min: F.natural.min, max: F.natural.max, speed: F.natural.speed, type: '' }], dualWield: false });
      mods.apBonus += F.predatoryStrikes.ap * b.predatoryStrikes + Math.floor((sim.stats.str || 0) * F.heartOfTheWild.str * b.heartOfTheWild) * 2;
      mods.critBonus += F.sharpenedClaws.crit * b.sharpenedClaws + F.leaderOfThePack.crit * b.leaderOfThePack + F.naturesMajesty.crit * b.naturesMajesty;
      mods.critDmgBonus = F.predatoryInstincts.critDmg * b.predatoryInstincts;
      sim.rageCap = F.energy.cap; sim.cp = 0; sim.ripUntil = 0; sim.rakeUntil = 0;
      const tick = () => { sim.gainRage(F.energy.perTick); sim.nextTick = sim.now + F.energy.tick; sim.schedule(F.energy.tick, tick); };
      sim.nextTick = F.energy.tick; sim.schedule(F.energy.tick, tick);
      sim.bleeding = () => sim.now < sim.ripUntil || sim.now < sim.rakeUntil;
    },
    start(sim) { sim.rage = sim.rageCap; },
    rotate(sim) {
      const now = sim.now, rem = sim.fightLen - now, energy = sim.rage, gcd = 1.0;
      const gcdLeft = Math.max(0, sim.gcdReadyAt - now);
      if (gcdLeft > 0) return gcdLeft;
      const wait = Math.max(0.05, sim.nextTick - now);
      const dmg = (isBuilder) => (1 + (isBuilder ? F.savageFury.dmg * b.savageFury : 0)) * (1 + (sim.bleeding() ? F.rendAndTear.dmg * b.rendAndTear : 0));
      const spell = (name) => ({ name, cd: 0, readyAt: 0, casts: 0 });
      const addCp = (o) => { if (o !== 'miss' && o !== 'dodge') sim.cp = Math.min(5, sim.cp + 1); };
      const mh = sim.player.weapons[0];
      const nearEnd = rem < 4;
      // finishers at five combo points (or a few at the very end)
      if ((sim.cp >= 5 || (nearEnd && sim.cp >= 3)) && energy >= Math.min(F.rip.cost, F.bite.cost)) {
        const ripDown = now >= sim.ripUntil - 1.0;
        if (ripDown && rem > 8 && energy >= F.rip.cost) {
          return castGcd(sim, spell('Rip'), () => {
            const cp = sim.cp; sim.spendRage(F.rip.cost); sim.cp = 0;
            const e = sim.entry('Rip'), out = sim.resolveYellow(0, true);
            if (out === 'miss' || out === 'dodge') { e.misses++; return; }
            const per = F.rip.base + F.rip.perCp * cp;
            sim.ripUntil = now + F.rip.ticks * F.rip.interval;
            const my = (sim.ripToken = (sim.ripToken || 0) + 1); let n = 0;
            const critP = sim.critChance(0), cm = sim.critMult(sim.mods.critDmgBonus);
            const step = () => { if (sim.ripToken !== my) return; const c = sim.rng() < critP; sim.record('Rip', per * sim.mods.dmgMult * (c ? cm : 1) * (1 - sim.dr), c ? 'crit' : 'hit'); if (++n < F.rip.ticks) sim.schedule(F.rip.interval, step); };
            sim.schedule(F.rip.interval, step);
          }, gcd);
        }
        if (energy >= F.bite.cost) {
          return castGcd(sim, spell('Ferocious Bite'), () => {
            const cp = sim.cp; sim.spendRage(F.bite.cost); sim.cp = 0;
            yellowAttack(sim, 'Ferocious Bite', () => (F.bite.base * (1 + F.bite.var * (sim.rng() - 0.5)) + F.bite.perCp * cp) * dmg(false), { critDmgBonus: sim.mods.critDmgBonus });
          }, gcd);
        }
      }
      if (sim.cp >= 5) return wait;
      // builders: Rake when it is down, then Shred (behind the target) or Claw
      const rakeCost = Math.max(10, F.rake.cost - F.ferocity.cost * b.ferocity), clawCost = Math.max(10, F.claw.cost - F.ferocity.cost * b.ferocity), shredCost = Math.max(10, F.shred.cost - F.shreddingAttacks.cost * b.shreddingAttacks);
      if (now >= sim.rakeUntil - 0.5 && rem > 6 && energy >= rakeCost) {
        return castGcd(sim, spell('Rake'), () => {
          sim.spendRage(rakeCost);
          const o = yellowAttack(sim, 'Rake', () => F.rake.direct * dmg(true), { critDmgBonus: sim.mods.critDmgBonus });
          addCp(o);
          if (o !== 'miss' && o !== 'dodge') {
            sim.rakeUntil = now + F.rake.ticks * F.rake.interval;
            const my = (sim.rakeToken = (sim.rakeToken || 0) + 1); let n = 0;
            const step = () => { if (sim.rakeToken !== my) return; sim.record('Rake (bleed)', F.rake.tick * sim.mods.dmgMult * (1 - sim.dr) * (1 + F.savageFury.dmg * b.savageFury), 'hit'); if (++n < F.rake.ticks) sim.schedule(F.rake.interval, step); };
            sim.schedule(F.rake.interval, step);
          }
        }, gcd);
      }
      if (b.behind && energy >= shredCost) return castGcd(sim, spell('Shred'), () => { sim.spendRage(shredCost); addCp(yellowAttack(sim, 'Shred', () => (sim.weaponRoll(mh) + sim.ap() / 14 * F.natural.speed + F.shred.flat) * F.shred.pct * dmg(true), { critDmgBonus: sim.mods.critDmgBonus })); }, gcd);
      if (!b.behind && energy >= clawCost) return castGcd(sim, spell('Claw'), () => { sim.spendRage(clawCost); addCp(yellowAttack(sim, 'Claw', () => (sim.weaponRoll(mh) + sim.ap() / 14 * F.natural.speed + F.claw.flat) * F.claw.pct * dmg(true), { critDmgBonus: sim.mods.critDmgBonus })); }, gcd);
      return wait;
    },
  };
}

// ---- paladin.js ----
// Retribution Paladin kit (two-handed melee with Seal of Command, Judgement, Holy Strike and Hammer of Wrath). Numbers: Holy Strike,
// Hammer of Wrath and the Seal costs come from the client's rank ladders (data/spells60.json: top / extra); talent numbers from the
// Forever tooltips. ASSUMED (Classic style): Seal of Command's 7 procs per minute, Judgement of Command's damage (the client only
// points at another spell), Vindication's proc chance, mana items, base mana, two-handed weapon speed normalisation (3.3).
// Not simulated: Exorcism and Consecration (low value on one target), blessings, Divine Favor, Holy Shock.

const PALADIN = {
  sealOfCommand: { cost: 210, ppm: 7, wpn: 0.7, duration: 30 },                                    // PPM ASSUMED (Classic)
  judgement: { cd: 10, costPct: 0.06, dmg: 72, spCoeff: 0.43, baseMana: 1250 },                    // damage and coefficient ASSUMED (Judgement of Command)
  holyStrike: { cost: 20, cd: 10, wpnPct: 0.5, flat: 93, spCoeff: 0.429, norm: 3.3 },
  hammerOfWrath: { cost: 425, cd: 6, cast: 1, dmg: 498, spCoeff: 0.429 },
  conviction: { crit: 0.01 }, improvedJudgement: { cd: 1 }, sanctifiedJudgement: { mana: 0.2 }, twoHandSpec: { dmg: 0.02 }, vengeance: { dmg: 0.01, stacks: 3, dur: 30 },
  vindication: { ap: 0.01, chance: 0.10, dur: 30 }, sacredArbiter: { dmg: 0.2 }, championOfLight: { sp: 0.2 }, divineStrength: { str: 0.02 }, divineIntellect: { int: 0.02 },
  benediction: { cost: 0.02 }, holyPower: { hs: 0.03 }, improvedSeals: { dmg: 0.05 }, instrumentOfLaw: { cast: 0.5 }, twistOfLight: { cost: 0.2 },
  manaPotion: { cd: 120, min: 1350, max: 2250 }, manaGem: { cd: 120, min: 1073, max: 1127 },
};

const PALADIN_RET_DEFAULT_BUILD = {
  conviction: 0, improvedJudgement: 0, sanctifiedJudgement: 0, twoHandSpec: 0, vengeance: 0, vindication: 0, sealOfCommand: 0, sacredArbiter: 0, championOfLight: 0,
  divineStrength: 0, divineIntellect: 0, benediction: 0, holyPower: 0, improvedSeals: 0, instrumentOfLaw: 0, twistOfLight: 0,
  useCooldowns: true, usePotion: true, useGem: true, executePhase: true,
};

function paladinRetKit(build = {}, data = null) {
  const b = Object.assign({}, PALADIN_RET_DEFAULT_BUILD, build), P = JSON.parse(JSON.stringify(PALADIN));
  const hs = pickRank(data, 'paladin', 'paladin_holy_strike', 'Holy Strike'), how = pickRank(data, 'paladin', null, 'Hammer of Wrath'), soc = pickRank(data, 'paladin', null, 'Seal of Command'), sor = pickRank(data, 'paladin', 'paladin_seal_of_righteousness', 'Seal of Righteousness');
  if (hs) { P.holyStrike.cost = hs.cost.amount; P.holyStrike.cd = hs.cooldown_ms / 1000; const e = hs.effects.find((x) => x.effect === 121); if (e) { P.holyStrike.flat = e.base; P.holyStrike.var = e.variance; P.holyStrike.spCoeff = e.sp_coeff; } }
  if (how) { P.hammerOfWrath.cost = how.cost.amount; P.hammerOfWrath.cd = how.cooldown_ms / 1000; P.hammerOfWrath.cast = how.cast_ms / 1000; const e = how.effects.find((x) => x.effect === 2); if (e) { P.hammerOfWrath.dmg = e.base; P.hammerOfWrath.spCoeff = e.sp_coeff; } }
  if (soc) P.sealOfCommand.cost = soc.cost.amount;
  return {
    name: 'paladin_retribution', build: b, P,
    setup(sim) {
      sim.player.resource = 'mana'; sim.kitBuild = b;
      const st = sim.stats, mods = sim.mods;
      const extraStr = Math.floor((st.str || 0) * P.divineStrength.str * b.divineStrength), extraInt = Math.floor((st.int || 0) * P.divineIntellect.int * b.divineIntellect);
      mods.apBonus += 2 * extraStr;
      mods.critBonus += P.conviction.crit * b.conviction + extraInt / 54 / 100 * 0;
      mods.dmgMult *= 1 + P.twoHandSpec.dmg * b.twoHandSpec;
      sim.spBonus = Math.floor((st.int || 0) * P.championOfLight.sp * b.championOfLight);
      setupMana(sim, { manaMax: st.mana + 15 * extraInt, mp5: st.mp5 || 0, spiritRegen: spiritRegenPerSec({ int: st.int, spi: st.spi }), castingFraction: 0.1 * 0 });
      sim.cd = { judgement: 0, holyStrike: 0, how: 0, potion: 0, gem: 0 };
      sim.sealUntil = -1; sim.sealCommand = false;
      sim.aVeng = sim.addAura({ name: 'Vengeance', duration: P.vengeance.dur, maxStacks: P.vengeance.stacks, mods: { dmgMult: 1 + P.vengeance.dmg * b.vengeance } });
      sim.aVind = sim.addAura({ name: 'Vindication', duration: P.vindication.dur, mods: { apMult: 1 + P.vindication.ap * b.vindication } });
      const holyMult = () => (1 + P.improvedSeals.dmg * b.improvedSeals) * sim.mods.dmgMult / (1 + P.twoHandSpec.dmg * b.twoHandSpec) * (1 - sim.target.spellMitigation) * sim.target.spellTaken;
      sim.holyHit = (name, raw, bonusCrit = 0, critBonus = 0) => {
        const c = Math.max(0, Math.min(1, sim.stats.crit + sim.mods.critBonus + bonusCrit)), crit = sim.rng() < c;
        const d = raw * holyMult() * (crit ? 1 + (SPELL_CRIT_MULT - 1) * (1 + critBonus) : 1);
        sim.record(name, d, crit ? 'crit' : 'hit');
        return crit;
      };
      const twoH = sim.player.weapons[0] && sim.player.weapons[0].twoHand;
      sim.norm = twoH ? P.holyStrike.norm : 2.4;
      sim.procs.push((s, outcome, source, isOH, isWhite) => {
        if (outcome === 'miss' || outcome === 'dodge') return;
        if (outcome === 'crit' && b.vengeance) s.aVeng.apply(1);
        if (b.vindication && s.rng() < P.vindication.chance) s.aVind.apply();
        if (isWhite && s.sealCommand && s.now < s.sealUntil) {
          const w = s.player.weapons[0], chance = P.sealOfCommand.ppm * w.speed / 60;
          if (s.rng() < chance) { s.entry('Seal of Command').casts++; s.holyHit('Seal of Command', (s.weaponRoll(w) + s.ap() / 14 * w.speed) * P.sealOfCommand.wpn); }
        }
      });
    },
    rotate(sim) {
      const now = sim.now, rem = sim.fightLen - now;
      const st = sim.stats;
      if (b.usePotion && now >= sim.cd.potion && sim.mana <= sim.manaMax - 1800 && rem > 20) { sim.cd.potion = now + P.manaPotion.cd; sim.entry('Mana Potion').casts++; gainMana(sim, P.manaPotion.min + (P.manaPotion.max - P.manaPotion.min) * sim.rng()); }
      if (b.useGem && now >= sim.cd.gem && sim.mana <= sim.manaMax - 1100 && rem > 15) { sim.cd.gem = now + P.manaGem.cd; sim.entry('Mana Gem').casts++; gainMana(sim, P.manaGem.min + (P.manaGem.max - P.manaGem.min) * sim.rng()); }
      const cost = (c) => Math.round(c * (1 - P.benediction.cost * b.benediction));
      const judgeCost = Math.round(P.judgement.costPct * P.judgement.baseMana);
      // Judgement (no global cooldown): unleash the Seal of Command
      if (now >= sim.cd.judgement && sim.sealCommand && now < sim.sealUntil && sim.mana >= judgeCost) {
        sim.cd.judgement = now + P.judgement.cd - P.improvedJudgement.cd * b.improvedJudgement; spendMana(sim, judgeCost); sim.lastCastAt = now;
        sim.entry('Judgement of Command').casts++;
        const e = sim.entry('Judgement of Command');
        sim.holyHit('Judgement of Command', P.judgement.dmg + (st.sp + sim.spBonus) * P.judgement.spCoeff);
        if (b.sanctifiedJudgement) gainMana(sim, P.sealOfCommand.cost * P.sanctifiedJudgement.mana * b.sanctifiedJudgement);
      }
      const gcdLeft = Math.max(0, sim.gcdReadyAt - now);
      if (gcdLeft > 0) return gcdLeft;
      // keep the Seal up
      if (b.sealOfCommand && (!sim.sealCommand || sim.sealUntil - now < 1.5) && sim.mana >= cost(P.sealOfCommand.cost) && rem > 3) {
        spendMana(sim, cost(P.sealOfCommand.cost)); sim.lastCastAt = now; sim.gcdReadyAt = now + 1.5; sim.entry('Seal of Command').casts += 0;
        sim.sealCommand = true; sim.sealUntil = now + P.sealOfCommand.duration;
        return 1.5;
      }
      // Hammer of Wrath in the execute phase
      if (b.executePhase && sim.inExecute() && now >= sim.cd.how && sim.mana >= cost(P.hammerOfWrath.cost)) {
        sim.cd.how = now + P.hammerOfWrath.cd; spendMana(sim, cost(P.hammerOfWrath.cost)); sim.lastCastAt = now; sim.entry('Hammer of Wrath').casts++;
        sim.gcdReadyAt = now + 1.5;
        const t = Math.max(0.1, P.hammerOfWrath.cast - P.instrumentOfLaw.cast * b.instrumentOfLaw);
        sim.schedule(t, () => { sim.holyHit('Hammer of Wrath', P.hammerOfWrath.dmg + (sim.stats.sp + sim.spBonus) * P.hammerOfWrath.spCoeff); });
        return 1.5;
      }
      // Holy Strike on cooldown
      if (now >= sim.cd.holyStrike && sim.mana >= cost(P.holyStrike.cost) && sim.player.weapons.length) {
        sim.cd.holyStrike = now + P.holyStrike.cd; spendMana(sim, cost(P.holyStrike.cost)); sim.lastCastAt = now; sim.gcdReadyAt = now + 1.5; sim.entry('Holy Strike').casts++;
        const w = sim.player.weapons[0], v = P.holyStrike.var || 0;
        const out = sim.resolveYellow(P.holyStrike.holy ? 0 : 0, true);
        const e = sim.entry('Holy Strike');
        if (out === 'miss') { e.misses++; sim.onMeleeHit('miss', 'Holy Strike', false, false); }
        else if (out === 'dodge') { e.dodges++; sim.onMeleeHit('dodge', 'Holy Strike', false, false); }
        else {
          const flat = P.holyStrike.flat * (1 + v * (sim.rng() - 0.5));
          const raw = ((sim.weaponRoll(w) + sim.ap() / 14 * sim.norm) * P.holyStrike.wpnPct + flat + (sim.stats.sp + sim.spBonus) * P.holyStrike.spCoeff) * (1 + P.sacredArbiter.dmg * b.sacredArbiter);
          const crit = sim.holyHit('Holy Strike', raw, P.holyPower.hs * 0, 0);
          sim.onMeleeHit(crit ? 'crit' : 'hit', 'Holy Strike', false, false);
        }
        return 1.5;
      }
      const next = Math.min(sim.cd.holyStrike, sim.cd.how, sim.sealUntil - 1.4, sim.cd.judgement);
      return Math.max(0.1, Math.min(1.0, next - now));
    },
  };
}

// ---- kits.js ----
// Kit registry: a serializable {name, build} -> engine spec object (needed to cross the Worker boundary).

function makeKit(name, build, data) {
  switch (name) {
    case 'warrior_fury': return furyKit(build, data);
    case 'warrior_arms': return armsKit(build, data);
    case 'rogue_combat': case 'rogue_assassination': case 'rogue_subtlety': return rogueKit(build, data);
    case 'mage_fire': return mageKit(Object.assign({}, build, { rotation: 'fire' }), data);
    case 'mage_frost': return mageKit(Object.assign({}, build, { rotation: 'frost' }), data);
    case 'mage_arcane': return mageKit(Object.assign({}, build, { rotation: 'arcane' }), data);
    case 'warlock_affliction': return warlockKit(Object.assign({}, build, { rotation: 'affliction' }), data);
    case 'warlock_destruction': return warlockKit(Object.assign({}, build, { rotation: 'destruction' }), data);
    case 'warlock_demonology': return warlockKit(Object.assign({ sacrifice: 'imp' }, build, { rotation: 'destruction' }), data);
    case 'hunter_marksmanship': case 'hunter_beastmastery': case 'hunter_survival': return hunterKit(build, data);
    case 'priest_shadow': return priestKit(build, data);
    case 'shaman_elemental': return shamanElementalKit(build, data);
    case 'druid_balance': return druidBalanceKit(build, data);
    case 'paladin_retribution': return paladinRetKit(build, data);
    case 'shaman_enhancement': return shamanEnhancementKit(build, data);
    case 'druid_feral': return druidFeralKit(build, data);
    default: throw new Error('unknown kit ' + name);
  }
}
const KITS = { warrior_fury: 'Fury Warrior', warrior_arms: 'Arms Warrior', rogue_combat: 'Combat Rogue', rogue_assassination: 'Assassination Rogue', rogue_subtlety: 'Subtlety Rogue', mage_fire: 'Fire Mage', mage_frost: 'Frost Mage', mage_arcane: 'Arcane Mage', warlock_affliction: 'Affliction Warlock', warlock_destruction: 'Destruction Warlock', warlock_demonology: 'Demonology Warlock', hunter_marksmanship: 'Marksmanship Hunter', hunter_beastmastery: 'Beast Mastery Hunter', hunter_survival: 'Survival Hunter', priest_shadow: 'Shadow Priest', shaman_elemental: 'Elemental Shaman', druid_balance: 'Balance Druid', paladin_retribution: 'Retribution Paladin', shaman_enhancement: 'Enhancement Shaman', druid_feral: 'Feral Druid (cat)' };

// ---- weights.js ----
// Stat weights by central finite difference with common random numbers (same seeds on both sides),
// expressed in DPS per point of each stat, then normalised to Attack Power.

function withStats(cfg, delta) {
  const stats = Object.assign({}, cfg.player.stats);
  for (const k in delta) stats[k] = (stats[k] || 0) + delta[k];
  return Object.assign({}, cfg, { player: Object.assign({}, cfg.player, { stats }) });
}

function statWeights(cfg, iterations = 4000, seedBase = 1) {
  const caster = cfg.player.resource === 'mana';
  const probes = {
    ap: caster ? { sp: 40 } : { ap: 40 },       // main power stat: attack power or spell power
    crit: { crit: 0.01 },      // per 1%
    hit: { hit: 0.01 },        // per 1%
    haste: { haste: 0.01 },    // per 1% (multiplier 1 -> 1.01)
  };
  const out = {};
  for (const k in probes) {
    const d = probes[k];
    const up = {}, down = {};
    for (const s in d) { up[s] = d[s]; down[s] = -d[s]; }
    const hi = runBatch(withStats(cfg, up), iterations, seedBase).mean;
    const lo = runBatch(withStats(cfg, down), iterations, seedBase).mean;
    out[k] = (hi - lo) / 2;
  }
  const apPer = out.ap / 40;                      // DPS per AP (spell power for casters)
  return {
    perPoint: { ap: apPer, crit: out.crit, hit: out.hit, haste: out.haste },
    normalizedToAp: { ap: 1, crit: out.crit / apPer, hit: out.hit / apPer, haste: out.haste / apPer },  // "1% crit = X AP"
  };
}

// ---- optimizer.js ----
// Gear optimizer: weight-based prefilter, then coordinate ascent with the real simulator using
// common random numbers (paired seeds => tiny noise on the DPS difference between two sets).
// Armor/jewelry slots and weapons are optimized together; weapons follow the spec's weapon mode
// ('dw' = main hand + off hand, '2h' = one two-hander).

// Linear score of an item with stat weights expressed as AP-equivalents.
// Casters: spell power plus Intellect (crit + mana), spirit and mp5 at fixed Classic-style values (only a prefilter: the real simulator picks).
function casterScore(item, w) {
  const s = item.st || {};
  return (s.splpwr || 0) + (s.spldmg || 0) + (s.int || 0) * (w.crit / 59.5 + 0.2) + (s.critstrkrtng || 0) / 14 * w.crit + (s.hitrtng || 0) / 10 * w.hit + (s.hastertng || 0) / 10 * w.haste + (s.manargn || 0) * 0.8 + (s.spi || 0) * 0.1;
}
// Hunters: ranged attack power (Agility counts twice: attack power and crit), Intellect through Careful Aim, ranged weapon dps.
function hunterScore(item, w) {
  const s = item.st || {};
  return (s.agi || 0) * (1 + w.crit / 53) + (s.atkpwr || 0) + (s.int || 0) * 0.2 + (s.critstrkrtng || 0) / 14 * w.crit + (s.hitrtng || 0) / 10 * w.hit + (s.hastertng || 0) / 10 * w.haste + (s.dps || 0) * (w.dpsPerWeaponDps || 8) + (s.manargn || 0) * 0.5;
}
function score(item, w) {
  if (w.caster) return casterScore(item, w);
  if (w.hunter) return hunterScore(item, w);
  const s = item.st || {};
  return (s.str || 0) * 2 + (s.agi || 0) * w.agi + (s.atkpwr || 0)
    + (s.critstrkrtng || 0) / 14 * w.crit + (s.hitrtng || 0) / 10 * w.hit + (s.hastertng || 0) / 10 * w.haste
    + (s.dps || 0) * (w.dpsPerWeaponDps || 8);
}

const WEAPON_SLOTS = { dw: ['mh', 'oh'], '2h': ['th'], caster: ['th'], ranged: ['rng', 'th'], stick: ['th'] };

function weaponCandidates(pool, cls, slot, mode) {
  const w = pool.weapons(cls, 60);
  if (slot === 'rng') return w.ranged;
  if ((mode === 'ranged' || mode === 'stick') && slot === 'th') return w.twoHand.concat(w.oneHand, w.mainHand);   // melee weapon only lends its stats to a hunter
  if (slot === 'mh') return w.oneHand.concat(w.mainHand);
  if (slot === 'oh') return w.oneHand.concat(w.offHand);
  return w.twoHand;
}

// Generic async core. `evaluate(spec)` -> Promise<number> (mean DPS), `getWeights(spec)` -> Promise<{agi,crit,hit,haste}>.
async function optimizeGearAsync({ pool, character, evaluate, getWeights, prefilter = 4, weaponPrefilter = 6, maxPasses = 3, onProgress, weaponMode, caster, ranged }) {
  const cls = character.class, base = Object.assign({}, character, { gear: [], weapons: [] });
  const mode = caster ? 'caster' : ranged ? 'ranged' : weaponMode || ((character.weapons || []).length > 1 ? 'dw' : ((character.weapons || [])[0] && character.weapons[0].twoHand ? '2h' : 'dw'));
  const wslots = WEAPON_SLOTS[mode];
  const bySlot = {};
  for (const s of EQUIP_SLOTS) bySlot[s] = (character.gear || []).find((g) => g.slot === s) || null;
  // current weapons by role
  const wsel = {};
  const cw = character.weapons || [];
  if (mode === 'ranged') { wsel.rng = cw[0] ? pool.byId.get(cw[0].itemId) || null : null; wsel.th = null; }
  else if (mode === '2h' || mode === 'caster' || mode === 'stick') wsel.th = cw[0] ? pool.byId.get(cw[0].itemId) || null : null;
  else { wsel.mh = cw[0] ? pool.byId.get(cw[0].itemId) || null : null; wsel.oh = cw[1] ? pool.byId.get(cw[1].itemId) || null : null; }

  const specOf = () => {
    // casters have no swung weapon: the staff only contributes its stats, so it rides along with the gear
    const weapons = mode === 'caster' || mode === 'stick' ? [] : mode === 'ranged' ? (wsel.rng ? [toWeapon(wsel.rng, false)] : []) : mode === '2h'
      ? (wsel.th ? [toWeapon(wsel.th, false)] : [])
      : [wsel.mh && toWeapon(wsel.mh, false), wsel.oh && toWeapon(wsel.oh, true)].filter(Boolean);
    const gear = EQUIP_SLOTS.map((s) => bySlot[s]).filter(Boolean);
    if ((mode === 'caster' || mode === 'ranged' || mode === 'stick') && wsel.th) gear.push({ slot: 'th', id: wsel.th.id, name: wsel.th.name, st: wsel.th.st });
    return Object.assign({}, base, { gear, weapons });
  };
  // start from the best static pick when a weapon slot is empty (the engine needs a weapon to swing)
  const staticW = { agi: 0.3, crit: caster ? 6 : 28, hit: caster ? 8 : 22, haste: 20, dpsPerWeaponDps: 8, caster: !!caster, hunter: !!ranged };
  for (const slot of wslots) {
    if (wsel[slot]) continue;
    const taken = new Set(wslots.filter((x) => wsel[x]).map((x) => wsel[x].id));
    const c = weaponCandidates(pool, cls, slot, mode).filter((i) => !taken.has(i.id)).sort((x, y) => score(y, staticW) - score(x, staticW));
    wsel[slot] = c[0] || null;
  }
  // Items with a proc or an on-use effect have no stats to rank them by: always try a few of them next to the best-scoring ones.
  const fxItems = (character.effects && character.effects.items) || {};
  const withEffectItems = (top, all) => {
    const have = new Set(top.map((i) => i.id));
    const extra = all.filter((i) => fxItems[i.id] && !have.has(i.id)).slice(0, 6);
    return top.concat(extra);
  };
  const w = Object.assign({ caster: !!caster, hunter: !!ranged }, await getWeights(specOf()));
  let best = await evaluate(specOf());
  const log = [{ pass: 0, dps: best }];
  for (let pass = 1; pass <= maxPasses; pass++) {
    let improved = false;
    // weapons first: they dominate the result
    for (const slot of wslots) {
      const others = new Set(wslots.filter((s) => s !== slot && wsel[s]).map((s) => wsel[s].id));
      let cands = weaponCandidates(pool, cls, slot, mode).filter((i) => !others.has(i.id));
      cands.sort((a, b) => score(b, w) - score(a, w));
      cands = withEffectItems(cands.slice(0, weaponPrefilter), weaponCandidates(pool, cls, slot, mode).filter((i) => !others.has(i.id)));
      const current = wsel[slot];
      let bestItem = current, bestDps = best;
      for (const it of cands) {
        if (current && it.id === current.id) continue;
        wsel[slot] = it;
        const d = await evaluate(specOf());
        if (d > bestDps + 0.05) { bestDps = d; bestItem = it; }
      }
      wsel[slot] = bestItem;
      if (bestDps > best + 0.05) { best = bestDps; improved = true; log.push({ pass, slot, name: bestItem && bestItem.name, dps: best }); }
      if (onProgress) onProgress({ pass, slot, dps: best });
    }
    for (const slot of EQUIP_SLOTS) {
      const used = new Set(EQUIP_SLOTS.filter((s) => s !== slot && bySlot[s]).map((s) => bySlot[s].id));
      let cands = pool.forSlot(slot, cls, 60).filter((i) => !used.has(i.id));
      cands.sort((a, b) => score(b, w) - score(a, w));
      cands = withEffectItems(cands.slice(0, prefilter), pool.forSlot(slot, cls, 60).filter((i) => !used.has(i.id)));
      const current = bySlot[slot];
      let bestItem = current, bestDps = best;
      for (const it of cands) {
        if (current && it.id === current.id) continue;
        bySlot[slot] = { slot, id: it.id, name: it.name, st: it.st };
        const d = await evaluate(specOf());
        if (d > bestDps + 0.05) { bestDps = d; bestItem = bySlot[slot]; }
      }
      bySlot[slot] = bestItem;
      if (bestDps > best + 0.05) { best = bestDps; improved = true; log.push({ pass, slot, name: bestItem && bestItem.name, dps: best }); }
      if (onProgress) onProgress({ pass, slot, dps: best });
    }
    if (!improved) break;
  }
  const weapons = wslots.map((s) => wsel[s] && { slot: s, id: wsel[s].id, name: wsel[s].name, st: wsel[s].st }).filter(Boolean);
  return { dps: best, gear: EQUIP_SLOTS.map((s) => bySlot[s]).filter(Boolean), weapons, weaponMode: mode, log, weights: w };
}

// Synchronous-looking helper for node scripts and tests: evaluates on the current thread.
function optimizeGear({ pool, character, kit, fightLen = 180, iterations = 600, seed = 11, weights, ...rest }) {
  const evaluate = async (spec) => {
    const ch = buildCharacter(spec);
    return runBatch({ fightLen, player: ch.player, target: ch.target, kitFactory: kit }, iterations, seed).mean;
  };
  const getWeights = async (spec) => {
    if (weights) return weights;
    const ch = buildCharacter(spec);
    const sw = statWeights({ fightLen, player: ch.player, target: ch.target, kitFactory: kit }, 1500, seed);
    return { agi: 0.05 * sw.normalizedToAp.crit, crit: sw.normalizedToAp.crit, hit: sw.normalizedToAp.hit, haste: sw.normalizedToAp.haste };
  };
  return optimizeGearAsync({ pool, character, evaluate, getWeights, ...rest });
}

root.Sim60 = { Sim, Aura, runBatchRaw, mergeRaw, finalize, runBatch, buildCharacter, ItemPool, toWeapon, EQUIP_SLOTS, BUFFS, CONSUMABLES, DEBUFFS, PRESET_RAID, RACIAL_SKILL, RACE_MODS, BASE_L60_HUMAN, PRESET_CASTER, PRESET_HUNTER, resolveEffects, furyKit, armsKit, rogueKit, mageKit, warlockKit, hunterKit, priestKit, shamanElementalKit, shamanEnhancementKit, druidBalanceKit, druidFeralKit, paladinRetKit, makeKit, KITS, statWeights, optimizeGear, optimizeGearAsync, validateRanks, parseShareHash, ranksToBuild, ranksFromNames, PRESETS, NAME_TO_KEY, FURY_DEFAULT_BUILD, ARMS_DEFAULT_BUILD, WARRIOR, warriorFromData, meleeTable, armorDR };
})(typeof self !== 'undefined' ? self : this);
