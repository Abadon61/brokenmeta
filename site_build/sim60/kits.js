// Kit registry: a serializable {name, build} -> engine spec object (needed to cross the Worker boundary).
import { furyKit, armsKit } from './warrior.js';
import { rogueKit } from './rogue.js';
import { mageKit } from './mage.js';
import { warlockKit } from './warlock.js';
import { hunterKit } from './hunter.js';

export function makeKit(name, build, data) {
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
    default: throw new Error('unknown kit ' + name);
  }
}
export const KITS = { warrior_fury: 'Fury Warrior', warrior_arms: 'Arms Warrior', rogue_combat: 'Combat Rogue', rogue_assassination: 'Assassination Rogue', rogue_subtlety: 'Subtlety Rogue', mage_fire: 'Fire Mage', mage_frost: 'Frost Mage', mage_arcane: 'Arcane Mage', warlock_affliction: 'Affliction Warlock', warlock_destruction: 'Destruction Warlock', warlock_demonology: 'Demonology Warlock', hunter_marksmanship: 'Marksmanship Hunter', hunter_beastmastery: 'Beast Mastery Hunter', hunter_survival: 'Survival Hunter' };
