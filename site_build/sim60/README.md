# sim60 -- level-60 DPS simulator engine (JavaScript, runs in node and in Web Workers)

Started 2026-10-02 for the Nov 4 launch. Separate from `wow_dps_sim.py` (Python, level-30 ranking and
addon weights). Classic-derived mechanics; every assumption is documented in `constants.js`.

- `engine.js`   event queue, auras, attack table (white = one roll, yellow = two rolls), auto attacks with haste rescaling, rage.
- `constants.js` attack table / armor / rage formulas, ratings (14 crit, 10 hit per 1%).
- `warrior.js`  Fury kit (Bloodthirst, Whirlwind, Heroic Strike, Execute, Death Wish, Recklessness, Bloodrage, Flurry, Unbridled Wrath, DW spec, ...). Forever-sourced numbers where we have them.
- `run.js`      batch runner (seed + i => common random numbers), aggregated breakdown and uptimes.
- `weights.js`  stat weights by central finite difference with common random numbers.
- `cli.mjs`     `node cli.mjs 5000 [weights]` benchmark / sanity run. `node --test test/engine.test.mjs` runs the checks.

Speed (node, one core): ~3600 fights/s of 180 s for Fury (Python engine: ~370/s).

Next: character builder (gear/base stats/buffs -> stats), talents for all Warrior specs, Arms kit, item data export
from Python, gear optimizer, Web Worker pool + UI page, then the other DPS classes.
