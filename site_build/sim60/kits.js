// Kit registry: a serializable {name, build} -> engine spec object (needed to cross the Worker boundary).
import { furyKit, armsKit } from './warrior.js';
import { rogueKit } from './rogue.js';

export function makeKit(name, build, data) {
  switch (name) {
    case 'warrior_fury': return furyKit(build, data);
    case 'warrior_arms': return armsKit(build, data);
    case 'rogue_combat': case 'rogue_assassination': case 'rogue_subtlety': return rogueKit(build, data);
    default: throw new Error('unknown kit ' + name);
  }
}
export const KITS = { warrior_fury: 'Fury Warrior', warrior_arms: 'Arms Warrior', rogue_combat: 'Combat Rogue', rogue_assassination: 'Assassination Rogue', rogue_subtlety: 'Subtlety Rogue' };
