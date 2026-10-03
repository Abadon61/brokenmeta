// Item pool helpers: slot mapping, class proficiency, weapon conversion.
// Data comes from data/items.json + data/proficiency.json (exported by wow_sim60_export.py from the
// beta client tables; weapons only carry DPS + speed there, so min/max use a +-25% spread, which
// changes variance but not the mean).

export const ARMOR_SLOTS = { head: [1], neck: [2], shoulder: [3], back: [16], chest: [5, 20], wrist: [9], hands: [10], waist: [6], legs: [7], feet: [8] };
export const EQUIP_SLOTS = ['head', 'neck', 'shoulder', 'back', 'chest', 'wrist', 'hands', 'waist', 'legs', 'feet', 'ring1', 'ring2', 'trinket1', 'trinket2'];
const SLOT_IDS = { ring1: [11], ring2: [11], trinket1: [12], trinket2: [12] };

const CLASS_KEY = { warrior: 'WARRIOR', paladin: 'PALADIN', hunter: 'HUNTER', rogue: 'ROGUE', priest: 'PRIEST', shaman: 'SHAMAN', mage: 'MAGE', warlock: 'WARLOCK', druid: 'DRUID' };
const ARMOR_TYPES = new Set(['Cloth', 'Leather', 'Mail', 'Plate Mail']);

export class ItemPool {
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
export function toWeapon(item, offHand = false) {
  const st = item.st || {};
  const speed = st.speed || 2.6, avg = (st.dps || 0) * speed;
  return { min: avg * 0.75, max: avg * 1.25, speed, type: TYPE_TO_ENGINE[item.type] || '', offHand, twoHand: item.slot === 17, itemId: item.id, st };
}
