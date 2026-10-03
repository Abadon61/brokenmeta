// Shaman kits. Elemental: Lightning Bolt, Chain Lightning, Lava Burst, Flame Shock and Earth Shock from the client's rank ladders
// (data/spells60.json: top / extra) and the Forever talent tooltips. ASSUMED (Classic style): base mana, mana items; the Searing Totem
// (a few damage per second) and the elemental melee crit from Elemental Devastation are not simulated.
import { makeCaster, fromRank, pickRank } from './caster.js';
import { dotActive, dotLeft } from './spells.js';

export const SHAMAN = {
  convection: { cost: 0.02 }, concussion: { dmg: 0.01 }, reverberation: { cd: 0.2 }, callOfFlame: { dmg: 0.05 }, elementalFocus: { chance: 0.10 }, elementalAlacrity: { cast: 1 / 6 },
  thunderingStrikes: { crit: 0.01 }, ancestralKnowledge: { int: 0.02 }, callOfThunder: { crit: 0.03 }, lightningOverload: { chance: 0.10 / 3, dmg: 0.5 }, elementalFury: { critBonus: 0.2 }, lavaBurstFs: 1.2,
  manaPotion: { cd: 120, min: 1350, max: 2250 }, manaGem: { cd: 120, min: 1073, max: 1127 },
};

export const SHAMAN_ELE_DEFAULT_BUILD = {
  convection: 0, concussion: 0, reverberation: 0, callOfFlame: 0, elementalFocus: 0, elementalAlacrity: 0, callOfThunder: 0, lightningOverload: 0, elementalFury: 0, lavaBurst: 0, thunderingStrikes: 0, ancestralKnowledge: 0,
  useCooldowns: true, usePotion: true, useGem: true, earthShock: false,
};

export function shamanElementalKit(build = {}, data = null) {
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
import { yellowAttack } from './shared.js';
import { setupMana, gainMana, spendMana, spiritRegenPerSec, resolveSpell } from './spells.js';

export const SHAMAN_ENH = {
  stormstrike: { cost: 125, cd: 8, nature: 1.2, dur: 12 }, rockbiter: { ap: 118 }, windfury: { chance: 0.20, ap: 315 },
  flurry: { perRank: 0.05, charges: 3, expire: 15 }, maelstrom: { chancePerRank: 0.03, max: 5, dur: 30 }, farseer: { haste: 1.3, dur: 25, cd: 180 },
  thunderingStrikes: { crit: 0.01 }, ancestralKnowledge: { int: 0.02 }, mentalDexterity: { ap: 1 / 3 }, mentalQuickness: { sp: 0.15 }, elementalWeapons: { rock: 0.2 / 3, wf: 0.4 / 3 },
  manaPotion: { cd: 120, min: 1350, max: 2250 }, manaGem: { cd: 120, min: 1073, max: 1127 },
};

export const SHAMAN_ENH_DEFAULT_BUILD = {
  thunderingStrikes: 0, ancestralKnowledge: 0, mentalDexterity: 0, mentalQuickness: 0, elementalWeapons: 0, flurry: 0, stormstrike: 0, maelstromWeapon: 0, rageOfTheFarseer: 0,
  windfuryWeapon: true, rockbiter: true, useCooldowns: true, usePotion: true, useGem: true,
};

export function shamanEnhancementKit(build = {}, data = null) {
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
