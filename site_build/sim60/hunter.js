// Hunter kit (Marksmanship / Beast Mastery / Survival share one ranged rotation; the specs differ by talents).
// WoW: Forever's own numbers where the client tables have them (Aimed Shot, Arcane Shot, Serpent Sting, Rapid Fire,
// Sniper Shot, Viper Sting) and the talent tooltips. ASSUMED = Classic 1.12 value kept until Forever's table is
// sourced: Multi-Shot (the Forever cooldown is shared with Aimed Shot), Aspect of the Hawk, ammo damage, the pet's
// attacks and Claw, Bestial Wrath's cooldown, Summon Hawk (a new Forever spell: rate and cooldown guessed), quiver haste.
// Not simulated: melee weaving (Raptor Strike, Mongoose Bite), traps, Volley (area spell), Viper Sting, Aspect of the Viper.
import { yellowAttack } from './shared.js';
import { setupMana, gainMana, spendMana, spiritRegenPerSec } from './spells.js';

export const HUNTER = {
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

export const HUNTER_DEFAULT_BUILD = {
  lethalAttacks: 0, efficiency: 0, carefulAim: 0, rapidKilling: 0, improvedArcane: 0, loneWolf: 0, mortalShots: 0, barrage: 0, rangedSpec: 0, improvedStings: 0, sniperShot: 0,
  surefooted: 0, lightningReflexes: 0, unleashedFury: 0, ferocity: 0, frenzy: 0, bestialWrath: 0, focusedFire: 0, deadlyAspects: 0, summonHawk: 0, bestialDiscipline: 0,
  pet: 'cat', useCooldowns: true, usePotion: true, useGem: true, aspect: true, quiver: true, shots: 'auto',
};

const hunterParseCast = (c) => (typeof c === 'string' ? (c === 'instant' ? 0 : parseFloat(c)) : c);

export function hunterKit(build = {}, data = null) {
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
