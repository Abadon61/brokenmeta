# Recalibration of the level-60 simulator (launch day, 4 November 2026)

Nothing in the beta client tables gives these numbers; they come from WoWSims (MIT) or from WoW Classic 1.12 and are **not confirmed for Forever**.
On launch day, read the real value in game (character sheet, combat log, tooltip) and change the constant listed here. Never edit a number to make a
spec rank higher: the ranking only moves because a measured input moves.

| # | Assumption | Where | What to read in game |
|---|---|---|---|
| 1 | Ranged attack power: 2 per Agility, base 100 (hunter) | `character.js` `CLASS_RULES.hunter` (`apPerAgi`, `apBase`) | Hunter sheet: ranged attack power before and after +10 Agility |
| 2 | Rage from a white hit: 3.46 x swing speed (off-hand halved, x4.5/3.46 two-hander, doubled on a crit) from WoWSims Forever `rage.go`; rage from damage taken 2.5 x damage / conversion (230.6 at level 60); a missed special refunds 80 % of its cost | `engine.js` `rageFromHit`, `refundRage` | Rage gained by one white hit of known damage and by a missed special |
| 3 | Level-60 base stats and race offsets | `character.js` `BASE_L60_HUMAN`, `RACE_MODS` | Naked level-60 character of each race/class (level 60 only exists on launch day) |
| 4 | Melee attack table: skill 300 vs boss defense 315 (level 63): miss 8 %, dodge 6.5 %, glance 40 %, crit suppression 3 % + up to 1.8 % of the crit beyond base and Agility crit (`table.auraCritSuppression`, `stats.critAura`) | `engine.js` `critChance`, `constants.js` | Combat log: miss / glancing / crit rates on a boss |
| 5 | Spell crit suppression 0 % (Forever has none), partial resist average 6 % (0.6 % pure DoT; Forever's boss has 0 resistance by default so this is OUR assumption), spell miss 17 % | `character.js` top (`SPELL_CRIT_SUPPRESSION`, `TARGET_SPELL_MITIGATION`, `TARGET_SPELL_MISS`) | Combat log against a boss: crit rate vs sheet crit, partial resists |
| 6 | Rage of the Farseer: 25 s, +30 % haste, 180 s cooldown | `shaman.js` `farseer` | Spell tooltip |
| 7 | Maelstrom Weapon: 10 % per hit, 5 stacks max | `shaman.js` `maelstrom` | Talent tooltip and proc rate over 200+ hits |
| 8 | Mana regeneration: `6.25 + spi/8` per second for every class, ticks every 0.1 s, any mana spend restarts the five-second rule (Forever `mana.go`) | `spells.js` `spiritRegenPerSec`, `REGEN_TICK`, `spendMana` | Mana regen out of combat at two spirit values |
| 9 | Windfury Weapon: 20 %, 1.5 s internal cooldown, two yellow extra attacks | `shaman.js` | Combat log |
| 10 | Items: stats come from the Wowhead Forever pages of 17 October (not the client) | `data/wow_wowhead_raw/`, `wow_crafted_build.py` | Spot-check ten items in the character screen |
| 11 | Caster spell ranks: Frostbolt rank 10 (cost 260), Fireball rank 11 (cost 395), Arcane Missiles rank 7 (cost 595), Backstab rank 8: the highest rank WoWSims Forever lets a trainer teach | `mage.js` (after the `pull` calls), `rogue.js` | Spellbook at level 60: which ranks a trainer sells |
| 12 | Tank threat: stance 1.3 x Defiance, bear 1.5, Revenge x2.25, Heroic Strike +152.4 flat, Sunder 206 + 5 % AP, 5 threat per rage not made by hitting or being hit | `tanks.js` | Threat meter on a boss, one ability at a time |
| 13 | Hunter pet: Raptor numbers for every family, creature dps 60.45, pet AP 10 % of the owner's, happiness x1.25, Cobra Reflexes +30 % speed x0.85 damage | `hunter.js` `startPetForever` | Pet sheet and combat log |
| 14 | Rogue poisons: Instant Poison VI 88 + 0.5 % AP, Deadly Poison V 23 a tick x 4 + 0.45 % AP per stack; Mutilate (67 + weapon) x 75 % | `rogue.js` | Combat log |

## Procedure

1. Change the constants above (one commit per assumption, with the in-game evidence in the message).
2. `cd site_build/sim60 && node --test test/*.test.mjs` (82 tests; update an expected value only when the changed input explains it).
3. Ranking, races and pre-raid gear in parallel (about 1 hour; do not build the site while `ranking.mjs` runs):
   `RANK_RACES=1 RACE_ITERS=20000 RANK_ONLY=<three specs> RANK_OUT=... RACE_OUT=... node ranking.mjs`, then `RANK_NORAID=1` for pre-raid, then the merge script.
4. `node guide_builds.mjs && cd ../.. && py -3.11 wow_guides_build60.py`, regenerate the talent notes, the BrokenDPS weights (`ADDON_WDPS=1 RANK_ONLY=hunter_melee ...`), then `py -3.11 wow_addon_build.py`.
5. Build, check in the browser (desktop and mobile), ask before commit / push / deploy, then regenerate `social_content/wow_digest.json` with `--source live` after the deploy.
