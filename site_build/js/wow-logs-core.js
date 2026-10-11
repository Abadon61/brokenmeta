/* BrokenLogs: reads a World of Warcraft combat log (WoWCombatLog.txt, advanced logging, COMBAT_LOG_VERSION 22) line by line and builds a
 * report per fight: damage, healing, damage taken, per-spell breakdown, timeline, deaths. Pure JavaScript with no DOM, used by the worker
 * (browser) and by the Node tests. Nothing here talks to a server.
 *
 * Methodology (also shown on the page):
 *  - damage done = amount - overkill + absorbed (damage soaked by a shield still counts as done), pets and guardians merged into their owner;
 *  - healing done = amount - overhealing;
 *  - DPS = damage / fight duration (the "raid" figure); active DPS = damage / active time, where active time adds the gap to the previous
 *    damaging action when it is at most 3 s, so standing still for longer does not count as active;
 *  - *_DAMAGE_LANDED events are ignored (the game logs the same hit twice);
 *  - a fight is an ENCOUNTER_START..ENCOUNTER_END pair; outside of encounters a combat starts at the first damage between a player (or a
 *    player's pet) and a creature and ends after 12 s without any.
 */
(function (root) {
  'use strict';

  var BUCKET_MS = 5000, GAP_MS = 12000, ACTIVE_CAP_MS = 3000, MIN_FIGHT_MS = 6000;

  // retail spec ids (the modern client used by WoW: Forever reports the same ids when it fills currentSpecID)
  var SPECS = {
    250: ['deathknight', 'Blood'], 251: ['deathknight', 'Frost'], 252: ['deathknight', 'Unholy'], 577: ['demonhunter', 'Havoc'], 581: ['demonhunter', 'Vengeance'],
    102: ['druid', 'Balance'], 103: ['druid', 'Feral'], 104: ['druid', 'Guardian'], 105: ['druid', 'Restoration'], 1467: ['evoker', 'Devastation'], 1468: ['evoker', 'Preservation'],
    1473: ['evoker', 'Augmentation'], 253: ['hunter', 'Beast Mastery'], 254: ['hunter', 'Marksmanship'], 255: ['hunter', 'Survival'], 62: ['mage', 'Arcane'], 63: ['mage', 'Fire'],
    64: ['mage', 'Frost'], 268: ['monk', 'Brewmaster'], 269: ['monk', 'Windwalker'], 270: ['monk', 'Mistweaver'], 65: ['paladin', 'Holy'], 66: ['paladin', 'Protection'],
    70: ['paladin', 'Retribution'], 256: ['priest', 'Discipline'], 257: ['priest', 'Holy'], 258: ['priest', 'Shadow'], 259: ['rogue', 'Assassination'], 260: ['rogue', 'Outlaw'],
    261: ['rogue', 'Subtlety'], 262: ['shaman', 'Elemental'], 263: ['shaman', 'Enhancement'], 264: ['shaman', 'Restoration'], 265: ['warlock', 'Affliction'],
    266: ['warlock', 'Demonology'], 267: ['warlock', 'Destruction'], 71: ['warrior', 'Arms'], 72: ['warrior', 'Fury'], 73: ['warrior', 'Protection']
  };
  var HEALER_SPECS = { 105: 1, 1468: 1, 270: 1, 65: 1, 256: 1, 257: 1, 264: 1 };
  var TANK_SPECS = { 250: 1, 581: 1, 104: 1, 268: 1, 66: 1, 73: 1 };

  // ---- text helpers
  function splitFields(s) {
    var out = [], cur = '', q = false, depth = 0, i, ch;
    for (i = 0; i < s.length; i++) {
      ch = s.charCodeAt(i);
      if (ch === 34) { q = !q; cur += '"'; }                                   // "
      else if (!q && (ch === 40 || ch === 91)) { depth++; cur += s[i]; }       // ( [
      else if (!q && (ch === 41 || ch === 93)) { depth--; cur += s[i]; }       // ) ]
      else if (!q && depth === 0 && ch === 44) { out.push(cur); cur = ''; }    // ,
      else cur += s[i];
    }
    out.push(cur);
    return out;
  }
  function unq(s) { return s && s.charCodeAt(0) === 34 ? s.slice(1, -1) : s; }
  function num(s) { var v = +s; return v === v ? v : 0; }

  // "10/9/2026 21:23:47.2352  EVENT,..." -> [ms, event, rest]
  function head(line) {
    var sp = line.indexOf('  ');
    if (sp < 0) return null;
    var ts = line.slice(0, sp), p = ts.split(/[\/ :.]/);
    if (p.length < 7) return null;
    var ms = Date.UTC(+p[2], +p[0] - 1, +p[1], +p[3], +p[4], +p[5]) + Math.floor(+p[6] / 10);
    var c = line.indexOf(',', sp + 2);
    return { t: ms, ev: c < 0 ? line.slice(sp + 2) : line.slice(sp + 2, c), rest: c < 0 ? '' : line.slice(c + 1) };
  }

  // "[(itemID,itemLevel,(enchants),(bonuses),(gems)),...]" -> average item level of the worn pieces (top-level tuples only)
  function gearLevels(gear) {
    var depth = 0, start = -1, sum = 0, cnt = 0, i, ch, t, m;
    for (i = 0; i < gear.length; i++) {
      ch = gear.charCodeAt(i);
      if (ch === 40) { depth++; if (depth === 1) start = i; }
      else if (ch === 41) {
        if (depth === 1 && start >= 0) { t = gear.slice(start + 1, i); m = /^(\d+),(\d+),/.exec(t); if (m && +m[2] > 1) { sum += +m[2]; cnt++; } start = -1; }
        depth--;
      }
    }
    return cnt ? Math.round(sum / cnt * 10) / 10 : 0;
  }

  function isPlayer(g) { return g.charCodeAt(0) === 80 && g.charCodeAt(1) === 108; }                  // "Player-"
  function isPet(g) { return g.charCodeAt(0) === 80 && g.charCodeAt(1) === 101; }                     // "Pet-"
  function isCreature(g) { var c = g.charCodeAt(0); return (c === 67 && g.charCodeAt(1) === 114) || c === 86; }   // "Creature-", "Vehicle-"

  function splitName(full) {
    var n = unq(full || ''), i = n.indexOf('-');
    return i < 0 ? { name: n, realm: '' } : { name: n.slice(0, i), realm: n.slice(i + 1) };
  }

  // ---- fight
  function newActor(guid, name) {
    return { guid: guid, name: name, dmg: 0, heal: 0, over: 0, taken: 0, sp: {}, hsp: {}, tsp: {}, casts: {}, tl: [], first: 0, last: 0, active: 0, recent: [], deaths: [], pets: {} };
  }
  function newFight(kind, t, name, extra) {
    var f = { kind: kind, name: name, start: t, end: t, success: null, enc: 0, difficulty: 0, zone: '', actors: {}, targets: {}, lines: 0 };
    for (var k in extra) f[k] = extra[k];
    return f;
  }
  function bump(map, key, fn, init) { var o = map[key]; if (!o) o = map[key] = init(); fn(o); return o; }

  function Parser() {
    this.lines = 0; this.version = 0; this.build = ''; this.names = {}; this.info = {}; this.owner = {}; this.fights = []; this.cur = null; this.zone = '';
    this.firstT = 0; this.lastT = 0; this.lastActivity = 0; this.encounterOpen = false; this.errors = 0;
  }
  Parser.prototype.actor = function (f, guid, name) {
    var a = f.actors[guid];
    if (!a) a = f.actors[guid] = newActor(guid, name);
    return a;
  };
  Parser.prototype.closeCurrent = function (t) {
    var f = this.cur;
    if (!f) return;
    f.end = t || f.end;
    this.cur = null;
    this.fights.push(f);
  };

  // one damage/heal hit: only the parts a fight needs
  Parser.prototype.damage = function (t, p, kind) {
    // p = split fields (after the event name). Layout from the END: swing = [amount,base,overkill,school,resisted,blocked,absorbed,crit,glancing,crushing],
    // spell/range/periodic = same 10 + a trailing ST/AOE tag.
    var n = p.length, swing = kind === 'swing', o = swing ? n - 10 : n - 11;
    var src = p[0], dst = p[4];
    if (!src || !dst || o < 8) return;
    var amount = num(p[o]), overkill = num(p[o + 2]), school = num(p[o + 3]), absorbed = num(p[o + 6]), crit = p[o + 7] === '1';
    var spellId = swing ? 0 : num(p[8]), spellName = swing ? 'Mêlée' : unq(p[9]);
    var eff = amount - (overkill > 0 ? overkill : 0) + absorbed;
    if (eff < 0) eff = 0;
    var srcP = isPlayer(src), dstP = isPlayer(dst), srcPet = !srcP && (isPet(src) || (this.owner[src] !== undefined));
    var f = this.cur;
    var friendlyOwnerSrc = srcP || srcPet, hostileDst = !dstP && (isCreature(dst) || isPet(dst) && this.owner[dst] === undefined);
    if (!f) {
      // outside an encounter: a combat starts at the first player <-> creature damage
      if ((friendlyOwnerSrc && hostileDst) || (dstP && !srcP && !srcPet && isCreature(src))) {
        f = this.cur = newFight('combat', t, '', { zone: this.zone });
        this.lastActivity = t;
      } else return;
    }
    if (f.kind === 'combat') {
      if (t - this.lastActivity > GAP_MS) {            // gap: close and open a new one
        this.closeCurrent(this.lastActivity);
        f = this.cur = newFight('combat', t, '', { zone: this.zone });
      }
      this.lastActivity = t;
    }
    if (t > f.end) f.end = t;
    f.lines++;
    var sName = unq(p[1]), dName = unq(p[5]);
    if (friendlyOwnerSrc && hostileDst) {
      var a = this.actor(f, src, sName);
      a.dmg += eff;
      var s = bump(a.sp, spellId + ':' + spellName, function (x) { x.d += eff; x.h++; if (crit) x.c++; if (eff > x.max) x.max = eff; }, function () { return { id: spellId, n: spellName, sc: school, d: 0, h: 0, c: 0, max: 0 }; });
      s.sc = school;
      var b = Math.floor((t - f.start) / BUCKET_MS);
      if (b >= 0) a.tl[b] = (a.tl[b] || 0) + eff;
      if (a.last) { var gap = t - a.last; a.active += gap < ACTIVE_CAP_MS ? gap : 0; } else a.first = t;
      a.last = t;
      f.targets[dName] = (f.targets[dName] || 0) + eff;
    } else if (dstP) {
      var d = this.actor(f, dst, dName);
      d.taken += eff;
      bump(d.tsp, (srcP ? '' : sName + ': ') + spellName, function (x) { x.d += eff; x.h++; }, function () { return { n: (srcP ? '' : sName + ': ') + spellName, d: 0, h: 0 }; });
      d.recent.push({ t: t, k: 'd', who: sName, sp: spellName, v: eff, ab: absorbed, ok: overkill > 0 ? overkill : 0 });
      if (d.recent.length > 8) d.recent.shift();
    }
  };

  Parser.prototype.heal = function (t, p) {
    var n = p.length, o = n - 5;
    var src = p[0], dst = p[4];
    if (!src || !dst || o < 8 || !this.cur) return;
    var amount = num(p[o]), over = num(p[o + 2]), crit = p[o + 4] === '1';
    var eff = amount - over;
    if (eff < 0) eff = 0;
    var srcP = isPlayer(src) || this.owner[src] !== undefined;
    var f = this.cur;
    if (t > f.end) f.end = t;
    if (srcP) {
      var a = this.actor(f, src, unq(p[1])), spellName = unq(p[9]), id = num(p[8]);
      a.heal += eff; a.over += over > 0 ? over : 0;
      var s = bump(a.hsp, id + ':' + spellName, function (x) { x.d += eff; x.o += over > 0 ? over : 0; x.h++; if (crit) x.c++; }, function () { return { id: id, n: spellName, d: 0, o: 0, h: 0, c: 0 }; });
      s.id = id;
    }
    if (isPlayer(dst)) {
      var d = this.actor(f, dst, unq(p[5]));
      d.recent.push({ t: t, k: 'h', who: unq(p[1]), sp: unq(p[9]), v: eff });
      if (d.recent.length > 8) d.recent.shift();
    }
  };

  Parser.prototype.line = function (raw) {
    this.lines++;
    if (raw.charCodeAt(raw.length - 1) === 13) raw = raw.slice(0, -1);
    var h = head(raw);
    if (!h) return;
    var t = h.t, ev = h.ev;
    if (!this.firstT) this.firstT = t;
    this.lastT = t;
    switch (ev) {
      case 'SPELL_DAMAGE': case 'SPELL_PERIODIC_DAMAGE': case 'RANGE_DAMAGE': case 'DAMAGE_SHIELD': case 'DAMAGE_SPLIT':
        this.damage(t, splitFields(h.rest), 'spell'); break;
      case 'SWING_DAMAGE':
        this.damage(t, splitFields(h.rest), 'swing'); break;
      case 'SPELL_HEAL': case 'SPELL_PERIODIC_HEAL':
        this.heal(t, splitFields(h.rest)); break;
      case 'SPELL_CAST_SUCCESS': {
        var p = splitFields(h.rest), src = p[0];
        // advanced block of a cast describes the caster: ownerGUID tells whose pet it is
        if (src && !isPlayer(src) && p.length > 12 && p[11] === src && p[12] && p[12].charCodeAt(0) === 80 && p[12] !== '0000000000000000') this.owner[src] = p[12];
        if (this.cur && src && isPlayer(src)) {
          var a = this.actor(this.cur, src, unq(p[1]));
          var k = unq(p[9]);
          a.casts[k] = (a.casts[k] || 0) + 1;
        }
        break;
      }
      case 'SPELL_SUMMON': {
        var q = splitFields(h.rest);
        if (q[0] && q[4]) this.owner[q[4]] = this.owner[q[0]] || q[0];
        break;
      }
      case 'UNIT_DIED': {
        var u = splitFields(h.rest), dst = u[4];
        if (dst && isPlayer(dst) && this.cur && u[8] !== '1') {
          var d = this.actor(this.cur, dst, unq(u[5]));
          d.deaths.push({ t: t - this.cur.start, recap: d.recent.slice(-6).map(function (r) { return { dt: r.t - t, k: r.k, who: r.who, sp: r.sp, v: r.v, ab: r.ab || 0 }; }) });
          d.recent = [];
        }
        break;
      }
      case 'ENCOUNTER_START': {
        var e = splitFields(h.rest);
        if (this.cur) this.closeCurrent(this.cur.kind === 'combat' ? this.lastActivity : t);
        this.cur = newFight('boss', t, unq(e[1]), { enc: num(e[0]), difficulty: num(e[2]), size: num(e[3]), zone: this.zone });
        this.encounterOpen = true;
        break;
      }
      case 'ENCOUNTER_END': {
        var x = splitFields(h.rest);
        if (this.cur && this.cur.kind === 'boss') {
          this.cur.success = x[4] === '1';
          this.closeCurrent(t);
        }
        this.encounterOpen = false;
        break;
      }
      case 'COMBATANT_INFO': {
        var c = splitFields(h.rest), g = c[0];
        if (!g) break;
        var spec = num(c[24]), il = gearLevels(c[27] || '');
        this.info[g] = { spec: spec, ilvl: il };
        break;
      }
      case 'ZONE_CHANGE': { var z = splitFields(h.rest); this.zone = unq(z[1] || ''); break; }
      case 'COMBAT_LOG_VERSION': { var v = splitFields(h.rest); this.version = num(v[0]); this.build = v[4] || ''; break; }
      default: break;
    }
  };

  Parser.prototype.finish = function () {
    if (this.cur) this.closeCurrent(this.cur.kind === 'combat' ? this.lastActivity : this.lastT);
    var self = this, res = [], idx = 0;
    this.fights.forEach(function (f) {
      var pl = [], dur = f.end - f.start;
      if (f.kind === 'combat' && dur < MIN_FIGHT_MS) return;
      var raw = 0;
      Object.keys(f.actors).forEach(function (g) { raw += f.actors[g].dmg; });
      if (f.kind === 'combat' && raw / Math.max(1, dur / 1000) < 20) return;           // a few stray hits after a kill, not a fight
      // merge pets / guardians into their owner
      var actors = f.actors, merged = {};
      Object.keys(actors).forEach(function (g) {
        var a = actors[g], own = self.owner[g];
        if (!isPlayer(g)) {
          if (own && actors[own]) {
            var o = actors[own];
            o.dmg += a.dmg; o.pets[a.name] = (o.pets[a.name] || 0) + a.dmg;
            Object.keys(a.sp).forEach(function (k) {
              var s = a.sp[k], key = 'pet:' + a.name + ':' + k, t = o.sp[key] || (o.sp[key] = { id: s.id, n: a.name + ' : ' + s.n, sc: s.sc, d: 0, h: 0, c: 0, max: 0, pet: true });
              t.d += s.d; t.h += s.h; t.c += s.c; if (s.max > t.max) t.max = s.max;
            });
            a.tl.forEach(function (v, i) { if (v) o.tl[i] = (o.tl[i] || 0) + v; });
            o.heal += a.heal; o.over += a.over;
          }
          return;
        }
      });
      Object.keys(actors).forEach(function (g) {
        if (!isPlayer(g)) return;
        var a = actors[g];
        if (!a.dmg && !a.heal && !a.taken && !a.deaths.length) return;
        var nm = splitName(a.name), info = self.info[g] || {}, sp = SPECS[info.spec] || null;
        var spells = Object.keys(a.sp).map(function (k) { return a.sp[k]; }).sort(function (x, y) { return y.d - x.d; });
        var hsp = Object.keys(a.hsp).map(function (k) { return a.hsp[k]; }).sort(function (x, y) { return y.d - x.d; });
        var secs = Math.max(1, dur / 1000), act = Math.max(1000, a.active) / 1000;
        var nb = Math.ceil(dur / BUCKET_MS), tl = [], i;
        for (i = 0; i < nb; i++) tl.push(Math.round((a.tl[i] || 0) / (BUCKET_MS / 1000)));
        pl.push({
          guid: g, name: nm.name, realm: nm.realm, cls: sp ? sp[0] : '', spec: sp ? sp[1] : '', specId: info.spec || 0, ilvl: info.ilvl || 0,
          role: HEALER_SPECS[info.spec] ? 'heal' : TANK_SPECS[info.spec] ? 'tank' : (a.heal > a.dmg * 1.5 ? 'heal' : 'dps'),
          dmg: Math.round(a.dmg), heal: Math.round(a.heal), over: Math.round(a.over), taken: Math.round(a.taken),
          dps: Math.round(a.dmg / secs * 10) / 10, hps: Math.round(a.heal / secs * 10) / 10, adps: Math.round(a.dmg / act * 10) / 10,
          active: Math.round(act * 10) / 10, activePct: Math.round(Math.min(100, act / secs * 100)),
          spells: spells.slice(0, 40).map(function (s) { return { id: s.id, n: s.n, sc: s.sc, d: Math.round(s.d), h: s.h, c: s.c, max: Math.round(s.max), pet: !!s.pet }; }),
          heals: hsp.slice(0, 25).map(function (s) { return { id: s.id, n: s.n, d: Math.round(s.d), o: Math.round(s.o), h: s.h, c: s.c }; }),
          taken_by: Object.keys(a.tsp).map(function (k) { return a.tsp[k]; }).sort(function (x, y) { return y.d - x.d; }).slice(0, 12).map(function (s) { return { n: s.n, d: Math.round(s.d), h: s.h }; }),
          casts: Object.keys(a.casts).length ? Object.keys(a.casts).map(function (k) { return [k, a.casts[k]]; }).sort(function (x, y) { return y[1] - x[1]; }).slice(0, 25) : [],
          pets: Object.keys(a.pets).map(function (k) { return [k, Math.round(a.pets[k])]; }),
          deaths: a.deaths, tl: tl
        });
      });
      var players = pl;
      var tgt = Object.keys(f.targets).sort(function (x, y) { return f.targets[y] - f.targets[x]; });
      var name = f.name || (tgt[0] ? tgt[0] : 'Combat');
      var totalDmg = players.reduce(function (s, p) { return s + p.dmg; }, 0);
      res.push({
        id: ++idx, kind: f.kind, name: name, success: f.success, enc: f.enc, difficulty: f.difficulty, zone: f.zone, start: f.start, end: f.end, dur: Math.round(dur / 100) / 10,
        targets: tgt.slice(0, 3), totalDmg: totalDmg, totalHeal: players.reduce(function (s, p) { return s + p.heal; }, 0), deaths: players.reduce(function (s, p) { return s + p.deaths.length; }, 0),
        players: players.sort(function (x, y) { return y.dmg - x.dmg; })
      });
    });
    return { meta: { lines: this.lines, version: this.version, build: this.build, start: this.firstT, end: this.lastT, zones: [] }, fights: res };
  };

  var api = { gearLevels: gearLevels, Parser: Parser, SPECS: SPECS, BUCKET_MS: BUCKET_MS, splitFields: splitFields, head: head, splitName: splitName };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.WowLogs = api;
})(typeof self !== 'undefined' ? self : this);
