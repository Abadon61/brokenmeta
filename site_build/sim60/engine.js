// Event-driven combat engine (single target, one player). Spec-agnostic: a spec module supplies
// `setup(sim)` (auras, spells, procs) and `rotate(sim)` (priority list). Everything the engine
// models is Classic-derived and documented in constants.js.
import { makeRng } from './rng.js';
import { attachEffects } from './effects.js';
import {
  GCD, RAGE_CAP, HIT_FACTOR, CRIT_MULT_PHYSICAL, DUAL_WIELD_MISS_PENALTY, OVERPOWER_WINDOW,
  meleeTable, armorDR, rageConversion, PLAYER_LEVEL,
} from './constants.js';

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
export class Aura {
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

export class Sim {
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
    // tanking: a per-run copy of the defensive stats, the counters the batch runner averages, a threat hook
    this.counters = Object.create(null); this.tank = cfg.player.tank ? Object.assign({}, cfg.player.tank) : null;
    this.threatMult = null; this.takenMult = 1; this.bossHooks = [];
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
    if (this.threatMult) this.counters.threat = (this.counters.threat || 0) + amount * this.threatMult(source);
    if (kind === 'crit') { e.crits++; e.hits++; } else if (kind === 'glance') { e.glances++; e.hits++; } else e.hits++;
  }
  addC(name, v = 1) { this.counters[name] = (this.counters[name] || 0) + v; }
  threat(n) { this.counters.threat = (this.counters.threat || 0) + n; }
  // The raid boss swings at the tank (Classic attack table of a level-63 mob against a level-60 player; ASSUMED where noted).
  _bossSwing(boss) {
    const t = this.tank, adj = (t.defense - 5 * boss.level) * 0.0004;       // each defense point above the boss skill: 0.04% on every roll
    const miss = Math.max(0, 0.05 + adj), dodge = Math.max(0, t.dodge + adj), parry = Math.max(0, t.parry + adj), block = t.shield ? Math.max(0, t.block + adj) : 0;
    const crush = Math.max(0, 0.15 * (415 - t.defense) / 115), crit = Math.max(0, 0.05 - adj);         // crushing blows ASSUMED: 15% at 300 defense, none from 415
    const r = this.rng(); let out = 'hit', c = miss;
    if (r < c) out = 'miss'; else if (r < (c += dodge)) out = 'dodge'; else if (r < (c += parry)) out = 'parry'; else if (r < (c += block)) out = 'block'; else if (r < (c += crush)) out = 'crush'; else if (r < (c += crit)) out = 'crit';
    let dmg = 0;
    if (out !== 'miss' && out !== 'dodge' && out !== 'parry') {
      dmg = boss.dmg * (1 + boss.var * (2 * this.rng() - 1));
      if (out === 'crit') dmg *= 2; else if (out === 'crush') dmg *= 1.5;
      dmg *= (1 - Math.min(0.75, t.armor / (t.armor + 400 + 85 * boss.level))) * this.takenMult;
      if (out === 'block') dmg = Math.max(0, dmg - t.blockValue);
    }
    this.addC('swings'); this.addC('dmgTaken', dmg); this.addC('boss_' + out);
    for (let i = 0; i < this.bossHooks.length; i++) this.bossHooks[i](this, out, dmg);
  }
  _startBoss() {
    const boss = this.target.boss, swing = () => { this._bossSwing(boss); this.schedule(boss.speed, swing); };
    this.schedule(boss.first === undefined ? 1.0 : boss.first, swing);
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
    if (this.tank && this.target.boss) this._startBoss();
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
