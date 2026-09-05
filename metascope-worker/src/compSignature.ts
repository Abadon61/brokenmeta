// Direct port of src/tft_tracker/comp_signature.py -- MUST stay byte-for-byte
// identical in behavior to the Python version, since a comp's `key` here has
// to match the same comp's `key` in the static site's own comp_index.json
// (built by the SAME derive_comp() logic in Python) for the "link to the
// real /compo/<slug>/ page" feature to work. If you change one, change both.

export interface Trait {
  name: string;
  tier_current?: number;
  style?: number;
  num_units?: number;
}

export interface Unit {
  character_id?: string;
  itemNames?: string[];
  tier?: number;
  rarity?: number;
}

export interface CompSignature {
  key: string;
  label: string;
  traits: string[];
  carry: string | null;
}

const PREFIX_RE = /^[A-Za-z]+_?\d*_/;
const DIGITS_RE = /\d+/g;
const JUNK_SUFFIX_RE = /_(AD|AP|Base)$/i;

export function cleanId(characterId: string): string {
  let name = characterId.replace(PREFIX_RE, "");
  if (!name) name = characterId;
  name = name.replace(DIGITS_RE, "");
  name = name.replace(JUNK_SUFFIX_RE, "");
  return name || characterId;
}

export function isCompleteItem(name: string): boolean {
  return !name.startsWith("Component_");
}

export function displayName(cleanChampId: string, nameMap: Record<string, string> | null | undefined): string {
  return (nameMap && nameMap[cleanChampId]) || cleanChampId;
}

function activeTraits(traits: Trait[]): Trait[] {
  return traits.filter((t) => (t.tier_current ?? 0) > 0);
}

export function deriveComp(
  participant: { traits?: Trait[]; units?: Unit[] },
  nameMap: Record<string, string> | null | undefined,
  itemOffense: Record<string, string> | null | undefined,
  identityTraitCount = 1,
  displayTraitCount = 3,
): CompSignature {
  const active = activeTraits(participant.traits || []);
  active.sort((a, b) => {
    const ka = [a.style ?? 0, a.tier_current ?? 0, a.num_units ?? 0];
    const kb = [b.style ?? 0, b.tier_current ?? 0, b.num_units ?? 0];
    for (let i = 0; i < 3; i++) if (ka[i] !== kb[i]) return kb[i] - ka[i]; // reverse=True
    return 0;
  });
  const identityTraits = active.slice(0, identityTraitCount).map((t) => cleanId(t.name));
  const displayTraits = active.slice(0, displayTraitCount).map((t) => cleanId(t.name));

  const units = participant.units || [];
  let carry: string | null = null;
  if (units.length) {
    const notFiveCost = units.filter((u) => (u.rarity ?? 0) !== 4);
    const pool1 = notFiveCost.length ? notFiveCost : units;

    const candidates = pool1.filter(
      (u) => !(u.itemNames || []).some((n) => cleanId(n) === "ThiefsGloves"),
    );
    const pool2 = candidates.length ? candidates : pool1;

    function carryScore(u: Unit): [number, number, number, number] {
      const itemNames = (u.itemNames || []).map(cleanId);
      const offensive = itemOffense
        ? itemNames.filter((n) => itemOffense[n] === "offensive").length
        : 0;
      const star = u.tier ?? 0;
      const items = itemNames.length;
      const rarity = u.rarity ?? 0;
      return [offensive, star, items, rarity];
    }

    let best = pool2[0];
    let bestScore = carryScore(best);
    for (const u of pool2.slice(1)) {
      const s = carryScore(u);
      for (let i = 0; i < 4; i++) {
        if (s[i] !== bestScore[i]) {
          if (s[i] > bestScore[i]) { best = u; bestScore = s; }
          break;
        }
      }
    }
    carry = displayName(cleanId(best.character_id || ""), nameMap);
  }

  const traitPart = identityTraits.length ? identityTraits.join("+") : "Generic";
  const key = traitPart + (carry ? `_${carry}` : "");
  const traitLabel = traitPart.replace(/\+/g, " ");
  const label = carry ? `${traitLabel} ${carry}` : traitLabel;
  return { key, label, traits: displayTraits, carry };
}
