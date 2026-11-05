# Fury Warrior: our simulator vs WoWSims Forever (2026-11-04)

Their engine: published lib.wasm of wowsims.com/forever (build served 2026-11-04), repo wowsims/forever at 48c77eb. Ours: site_build/sim60 on main 487e6e30ba6. 3000 iterations, 180 s, level-63 boss, 20 % execute phase, Human unless stated.

## 1. Their own p1 Fury gear, their APL, their current talents (30303213002-350530005122100231-1)

| Layer | WoWSims | Ours |
|---|---|---|
| Bare, no buffs | 234 | 177 |
| + Sunder / Faerie Fire / Curse of Recklessness | 300 | 245 |
| + blessings, Mark of the Wild, Strength of Earth, Grace of Air, Leader of the Pack | 407 | 348 (328 without Recklessness and Death Wish) |
| + Windfury Totem | 450 | not simulated |
| + consumables | 521 | n/a |
| + Expose Armor, Gift of Arthas | 541 | n/a |

Their APL weaves Overpower (36 DPS, 14.6 casts per fight), casts Whirlwind 15.9 times (ours 10.5) and gets 15.5 DPS from Deep Wounds (ours 8.2).
Windfury Totem alone adds 43 DPS (spell 10610, 27.5 DPS, plus extra white swings and Hamstring weaves).

## 2. Our published Fury build in both engines (same talents, enchants, buffs, consumables)

Five published items are missing from their database (Dark Warder's Pauldrons, Cape of the Black Baron, Blackstone Ring, Smokey's Lighter, Mirah's Song): in BOTH engines they were replaced by their p1 item of the same slot.

| Setup | WoWSims | Ours |
|---|---|---|
| Buffs and debuffs, no consumables | 521 | 496 |
| + published consumables | 580.5 | 579.9 (546.8 without Recklessness / Death Wish) |
| + Windfury Totem | 662.5 | not simulated |
| + Expose Armor and Gift of Arthas | 683.7 | |
| Mongoose + Ferocity + Firewater instead of Grizzly | 679.8 | |
| + Mighty Rage Potion | 679.4 | |
| Orc instead of Human | 657.3 | |

Published number on the site: 631 (real gear, no Windfury Totem).

Scripts (scratchpad of the session): wsforever/wasm/{layers,ours_layers,side,pub,pubrun,pubrun2,ourspub}.mjs
