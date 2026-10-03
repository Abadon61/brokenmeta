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
    this.stats = cfg.player.stats;
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
    this.spec = cfg.spec; this.spec.setup(this);
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
  buffs: ['arcane_intellect', 'blessing_of_kings', 'mark_of_the_wild', 'moonkin_aura', 'dragonslayer', 'songflower'],
  consumables: ['flask_supreme_power', 'greater_arcane_elixir', 'brilliant_wizard_oil', 'mageblood_potion'],
  debuffs: ['curse_of_elements'],
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
  const rules = CLASS_RULES[cls];
  const base = spec.base || (() => {
    const h = BASE_L60_HUMAN[cls], m = RACE_MODS[race] || RACE_MODS.human, o = {};
    for (const k of PRIMARY) o[k] = h[k] + m[k];
    return o;
  })();
  const gear = sumGear(spec.gear || []);
  const allBuffs = [...(spec.buffs || []).map((id) => BUFFS[id]), ...(spec.consumables || []).map((id) => CONSUMABLES[id])].filter(Boolean);

  let statMult = 1, flatAp = gear.ap, buffCrit = 0, buffHit = 0, buffHaste = 1, apMult = 1, buffSp = 0, buffSpCrit = 0, buffMp5 = 0, buffSpHit = 0;
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

  if (rules.caster) return buildCaster(spec, rules, prim, gear, { buffCrit, buffHit, buffHaste, buffSp, buffSpCrit, buffSpHit, buffMp5 });

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

  return {
    player: {
      level: PLAYER_LEVEL, resource: rules.resource, dualWield: weapons.length > 1,
      stats: { ap, crit, hit, haste, weaponSkill, str: prim.str, agi: prim.agi },
      weapons,
    },
    target: { armor, defense: spec.targetDefense || BOSS_DEFENSE, executeFrac: spec.executeFrac ?? 0.2 },
    summary: { prim, ap, crit, hit, haste, weaponSkill, armor, gearArmor: gear.armor },
  };
}

// Caster stat block. Spell hit is a separate table from melee hit (Classic: 83% base against a level-63 boss,
// +1% per 1% hit up to 99%), applied by the kit; here `hit` is only the bonus from gear/buffs.
function buildCaster(spec, rules, prim, gear, b) {
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
    player: { level: PLAYER_LEVEL, resource: 'mana', dualWield: false, stats: { sp, crit, hit, haste, int: prim.int, spi: prim.spi, mana, mp5, weaponSkill: BASE_WEAPON_SKILL, ap: 0 }, weapons: [] },
    target: { armor: 0, defense: BOSS_DEFENSE, executeFrac: spec.executeFrac ?? 0.2, spellMitigation: Math.max(0, resist), spellMiss: TARGET_SPELL_MISS, spellTaken: taken },
    summary: { prim, sp, crit, hit, haste, mana, mp5, spirit: prim.spi, int: prim.int, spellMitigation: Math.max(0, resist) },
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
    const w = { oneHand: [], mainHand: [], offHand: [], twoHand: [] };
    for (const i of this.items) {
      if (!this.canEquip(i, cls, level)) continue;
      if (i.slot === 13) { w.oneHand.push(i); }
      else if (i.slot === 21) w.mainHand.push(i);
      else if (i.slot === 22) w.offHand.push(i);
      else if (i.slot === 17) w.twoHand.push(i);
    }
    return w;
  }
}

const TYPE_TO_ENGINE = { Swords: 'sword', Maces: 'mace', Axes: 'axe', Daggers: 'dagger', 'Fist Weapons': 'fist', 'Two-Handed Swords': 'two-handed sword', 'Two-Handed Maces': 'two-handed mace', 'Two-Handed Axes': 'two-handed axe', Polearms: 'polearm', Staves: 'staff' };

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

const parseCast = (c) => (typeof c === 'string' ? (c === 'instant' ? 0 : parseFloat(c)) : c);

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
      s.cast = parseCast(x.cast_time); if (x.cooldown_sec) s.cd = x.cooldown_sec;
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
        return ((mid + sp) * (1 + crit * (0.5 * (1 + m.critBonus))) * hit + dot) * m.dmg / Math.max(castTime(sim, s, true), SPELL_GCD);
      };
    },
    start(sim) { sim.arcaneBurst = arcaneBurstBetter(sim, M, b); },
    rotate(sim) { return rotate(sim, b, M); },
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
function castTime(sim, s, noAuras) {
  const b = sim.kitBuild, M = sim.spec.M;
  let t = s.cast;
  if (s === M.fireball || s === M.frostfireBolt) t -= M.improvedFireball.cast * b.improvedFireball;
  if (s === M.frostbolt) t -= M.improvedFrostbolt.cast * b.improvedFrostbolt;
  if (s === M.pyroblast && !noAuras && sim.aHeat.active) t *= 1 - 0.25 * sim.aHeat.stacks;
  return t;
}
function manaCost(sim, s) {
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
function cast(sim, s, instant) {
  const b = sim.kitBuild, M = sim.spec.M, cost = manaCost(sim, s);
  const usedCC = sim.aCC.active; if (usedCC) sim.aCC.expire();
  const pomUsed = sim.pom && s.cast >= 1.5 && s !== M.arcaneMissiles; if (pomUsed) sim.pom = false;
  let ct = instant ? 0 : castTime(sim, s);
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
function rotate(sim, b, M) {
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
  if (manaCost(sim, s) > sim.mana) {
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
  return cast(sim, s, s.cast === 0);
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

const parseCast = (c) => (typeof c === 'string' ? (c === 'instant' ? 0 : parseFloat(c)) : c);

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
      s.cast = parseCast(x.cast_time);
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
        return ((mid + (sp + sim.spBonus) * s.coeff) * bonus * (1 + crit * 0.5 * (1 + m.critBonus)) * hit) * m.dmg / Math.max(castTime(sim, s), SPELL_GCD);
      };
    },
    start() {},
    rotate(sim) { return rotate(sim, b, W); },
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
function castTime(sim, s) {
  const b = sim.kitBuild, W = sim.spec.W;
  let t = s.cast;
  if (s === W.shadowBolt || s === W.immolate || s === W.incinerate) t -= W.bane.cast * b.bane;
  if (s === W.soulFire) { t -= W.bane.soulFire * b.bane; if (sim.aDecim.active) t *= 1 - 0.2 * b.decimation; }
  if (s === W.corruption) t -= W.improvedCorruption.cast * b.improvedCorruption;
  if (s === W.shadowBolt && sim.aTrance.active) t = 0;
  return Math.max(0, t);
}
function manaCost(sim, s) {
  const b = sim.kitBuild, W = sim.spec.W;
  let c = s.cost;
  if (s.destruction) c *= 1 - W.cataclysm.cost * b.cataclysm;
  if (s === W.soulFire && sim.aDecim.active) return 0;
  return Math.round(c);
}

// ---- cast a spell (direct part, then the periodic part when it landed) ----
function cast(sim, s) {
  const b = sim.kitBuild, W = sim.spec.W, st = sim.stats;
  const cost = manaCost(sim, s);
  const tranced = s === W.shadowBolt && sim.aTrance.active; if (tranced) sim.aTrance.expire();
  const ct = tranced ? 0 : castTime(sim, s);
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
function rotate(sim, b, W) {
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
  const refresh = (s, margin) => dotLeft(sim, s.name) <= margin + castTime(sim, s) && (rem > 6);
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
  const need = manaCost(sim, s);
  if (need > sim.mana || sim.mana < 0.12 * sim.manaMax) {
    sim.gcdReadyAt = now + SPELL_GCD; sim.entry('Life Tap').casts++;
    gainMana(sim, W.lifeTap.restore * (1 + W.improvedLifeTap.restore * b.improvedLifeTap));
    return SPELL_GCD;
  }
  if (s === W.conflagrate) sim.cd.conflagrate = now + W.conflagrate.cd;
  if (s === W.shadowburn) sim.cd.shadowburn = now + W.shadowburn.cd;
  if (s === W.soulFire) sim.cd.soulFire = now + W.soulFire.cd * (1 - W.decimation.cd * b.decimation);
  if (s === W.doom) sim.cd.doom = now + W.doom.cd;
  return cast(sim, s);
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
    default: throw new Error('unknown kit ' + name);
  }
}
const KITS = { warrior_fury: 'Fury Warrior', warrior_arms: 'Arms Warrior', rogue_combat: 'Combat Rogue', rogue_assassination: 'Assassination Rogue', rogue_subtlety: 'Subtlety Rogue', mage_fire: 'Fire Mage', mage_frost: 'Frost Mage', mage_arcane: 'Arcane Mage', warlock_affliction: 'Affliction Warlock', warlock_destruction: 'Destruction Warlock', warlock_demonology: 'Demonology Warlock' };

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
function score(item, w) {
  if (w.caster) return casterScore(item, w);
  const s = item.st || {};
  return (s.str || 0) * 2 + (s.agi || 0) * w.agi + (s.atkpwr || 0)
    + (s.critstrkrtng || 0) / 14 * w.crit + (s.hitrtng || 0) / 10 * w.hit + (s.hastertng || 0) / 10 * w.haste
    + (s.dps || 0) * (w.dpsPerWeaponDps || 8);
}

const WEAPON_SLOTS = { dw: ['mh', 'oh'], '2h': ['th'], caster: ['th'] };

function weaponCandidates(pool, cls, slot) {
  const w = pool.weapons(cls, 60);
  if (slot === 'mh') return w.oneHand.concat(w.mainHand);
  if (slot === 'oh') return w.oneHand.concat(w.offHand);
  return w.twoHand;
}

// Generic async core. `evaluate(spec)` -> Promise<number> (mean DPS), `getWeights(spec)` -> Promise<{agi,crit,hit,haste}>.
async function optimizeGearAsync({ pool, character, evaluate, getWeights, prefilter = 4, weaponPrefilter = 6, maxPasses = 3, onProgress, weaponMode, caster }) {
  const cls = character.class, base = Object.assign({}, character, { gear: [], weapons: [] });
  const mode = caster ? 'caster' : weaponMode || ((character.weapons || []).length > 1 ? 'dw' : ((character.weapons || [])[0] && character.weapons[0].twoHand ? '2h' : 'dw'));
  const wslots = WEAPON_SLOTS[mode];
  const bySlot = {};
  for (const s of EQUIP_SLOTS) bySlot[s] = (character.gear || []).find((g) => g.slot === s) || null;
  // current weapons by role
  const wsel = {};
  const cw = character.weapons || [];
  if (mode === '2h' || mode === 'caster') wsel.th = cw[0] ? pool.byId.get(cw[0].itemId) || null : null;
  else { wsel.mh = cw[0] ? pool.byId.get(cw[0].itemId) || null : null; wsel.oh = cw[1] ? pool.byId.get(cw[1].itemId) || null : null; }

  const specOf = () => {
    // casters have no swung weapon: the staff only contributes its stats, so it rides along with the gear
    const weapons = mode === 'caster' ? [] : mode === '2h'
      ? (wsel.th ? [toWeapon(wsel.th, false)] : [])
      : [wsel.mh && toWeapon(wsel.mh, false), wsel.oh && toWeapon(wsel.oh, true)].filter(Boolean);
    const gear = EQUIP_SLOTS.map((s) => bySlot[s]).filter(Boolean);
    if (mode === 'caster' && wsel.th) gear.push({ slot: 'th', id: wsel.th.id, name: wsel.th.name, st: wsel.th.st });
    return Object.assign({}, base, { gear, weapons });
  };
  // start from the best static pick when a weapon slot is empty (the engine needs a weapon to swing)
  const staticW = { agi: 0.3, crit: caster ? 6 : 28, hit: caster ? 8 : 22, haste: 20, dpsPerWeaponDps: 8, caster: !!caster };
  for (const slot of wslots) {
    if (wsel[slot]) continue;
    const taken = new Set(wslots.filter((x) => wsel[x]).map((x) => wsel[x].id));
    const c = weaponCandidates(pool, cls, slot).filter((i) => !taken.has(i.id)).sort((x, y) => score(y, staticW) - score(x, staticW));
    wsel[slot] = c[0] || null;
  }
  const w = Object.assign({ caster: !!caster }, await getWeights(specOf()));
  let best = await evaluate(specOf());
  const log = [{ pass: 0, dps: best }];
  for (let pass = 1; pass <= maxPasses; pass++) {
    let improved = false;
    // weapons first: they dominate the result
    for (const slot of wslots) {
      const others = new Set(wslots.filter((s) => s !== slot && wsel[s]).map((s) => wsel[s].id));
      let cands = weaponCandidates(pool, cls, slot).filter((i) => !others.has(i.id));
      cands.sort((a, b) => score(b, w) - score(a, w));
      cands = cands.slice(0, weaponPrefilter);
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
      cands = cands.slice(0, prefilter);
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

root.Sim60 = { Sim, Aura, runBatchRaw, mergeRaw, finalize, runBatch, buildCharacter, ItemPool, toWeapon, EQUIP_SLOTS, BUFFS, CONSUMABLES, DEBUFFS, PRESET_RAID, RACIAL_SKILL, RACE_MODS, BASE_L60_HUMAN, PRESET_CASTER, furyKit, armsKit, rogueKit, mageKit, warlockKit, makeKit, KITS, statWeights, optimizeGear, optimizeGearAsync, validateRanks, parseShareHash, ranksToBuild, ranksFromNames, PRESETS, NAME_TO_KEY, FURY_DEFAULT_BUILD, ARMS_DEFAULT_BUILD, WARRIOR, warriorFromData, meleeTable, armorDR };
})(typeof self !== 'undefined' ? self : this);
