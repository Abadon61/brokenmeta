// Port of src/tft_tracker/analysis.py -- kept in French to match the
// existing site's "insights are French-only for now" scoping decision (see
// build_site.py's game_analysis.html comment). Thresholds match the Python
// version exactly.
import { cleanId, deriveComp, displayName, isCompleteItem, type Unit } from "./compSignature";

const GOLD_DIFF_THRESHOLD = 10;
const LEVEL_DIFF_THRESHOLD = 1.0;
const ROUND_DIFF_THRESHOLD = 3;
const PLACEMENT_UNDERPERFORM_THRESHOLD = 1.0;
const COUNTER_RATE_THRESHOLD = 0.55;
const COUNTER_MIN_ENCOUNTERS = 4;

export interface Benchmark {
  avg_gold_left: number | null;
  avg_level: number | null;
  avg_last_round: number | null;
  avg_placement: number;
  top4_rate: number;
  core_units: { champion: string; items: string[] }[];
  item_combo_stats: { champion: string; items: string[]; avgPlacement: number; games: number }[];
}

export interface Insight {
  type: "good" | "warning" | "info";
  category: string;
  text: string;
}

export interface LobbyEntry {
  riotId: string;
  compLabel: string;
  compKey: string;
  carry: string | null;
  placement: number;
  counterRate: number | null;
  encounters: number;
}

export interface ExtractedUnit {
  champion: string;
  cost: number;
  star: number;
  items: string[];
}

function extractUnits(participant: any, nameMap: Record<string, string>): ExtractedUnit[] {
  const units: ExtractedUnit[] = [];
  for (const u of participant.units || []) {
    const champ = displayName(cleanId(u.character_id || ""), nameMap);
    if (!champ) continue;
    const items = (u.itemNames || []).map(cleanId).filter(isCompleteItem);
    units.push({ champion: champ, cost: (u.rarity || 0) + 1, star: u.tier || 1, items });
  }
  units.sort((a, b) => a.cost - b.cost);
  return units;
}

function analyzeItems(units: ExtractedUnit[], bench: Benchmark | null, expectedCarry: string | null): Insight[] {
  if (!bench) return [];
  const insights: Insight[] = [];
  const coreByChamp = new Map(bench.core_units.map((u) => [u.champion, u]));
  const expectedItemHolders = new Set(
    bench.core_units.filter((u) => u.items.some(isCompleteItem)).map((u) => u.champion),
  );
  const actualByChamp = new Map(units.map((u) => [u.champion, u]));

  if (expectedCarry) {
    const carryUnit = actualByChamp.get(expectedCarry);
    const carryItems = carryUnit ? carryUnit.items : [];
    if (!carryItems.length) {
      insights.push({ type: "warning", category: "Objets",
        text: `Ton carry principal (${expectedCarry}) n'a reçu aucun objet complet cette partie — un carry non stuff perd l'essentiel de son impact.` });
    } else if (carryItems.length < 3) {
      insights.push({ type: "warning", category: "Objets",
        text: `Ton carry principal (${expectedCarry}) n'a que ${carryItems.length} objet(s) complet(s) — en dessous d'un build complet à 3 objets.` });
    } else {
      insights.push({ type: "good", category: "Objets",
        text: `Ton carry principal (${expectedCarry}) est bien stuff (${carryItems.length} objets complets).` });
      const carryCombos = bench.item_combo_stats.filter((c) => c.champion === expectedCarry);
      const actualSet = new Set(carryItems.slice(0, 3));
      const match = carryCombos.find((c) => c.items.length === actualSet.size && c.items.every((i) => actualSet.has(i)));
      if (match) {
        insights.push({ type: "good", category: "Objets",
          text: `Cette combinaison précise sur ${expectedCarry} fait partie des builds déjà observés sur cette comp (placement moyen ${match.avgPlacement.toFixed(2)} sur ${match.games} parties).` });
      } else if (carryCombos.length) {
        insights.push({ type: "info", category: "Objets",
          text: `La combinaison construite sur ${expectedCarry} diffère des builds les plus fréquents observés pour cette comp — pas forcément une erreur, mais à comparer aux combinaisons connues sur sa fiche.` });
      }
    }
  }

  for (const [champ, u] of actualByChamp) {
    if (champ === expectedCarry || !u.items.length) continue;
    if (!expectedItemHolders.has(champ)) {
      insights.push({ type: "info", category: "Objets",
        text: `${u.items.length} objet(s) complet(s) sur ${champ}, qui n'est généralement pas un porteur d'objets dans cette comp — vérifie que c'était voulu (flex, adaptation à la partie) plutôt qu'un objet gâché.` });
    } else {
      insights.push({ type: "good", category: "Objets",
        text: `${u.items.length} objet(s) complet(s) sur ${champ} — c'est bien un porteur d'objets habituel de cette comp.` });
    }
  }
  return insights;
}

export function buildLobby(match: any, puuid: string, nameMap: Record<string, string>,
                            matchupLookup: Map<string, { aheadRate: number; encounters: number }>,
                            playerKey: string, itemOffense: Record<string, string>): LobbyEntry[] {
  const lobby: LobbyEntry[] = [];
  for (const p of match.info?.participants || []) {
    if (p.puuid === puuid || !p.placement) continue;
    const sig = deriveComp(p, nameMap, itemOffense);
    const gameName = p.riotIdGameName || "?";
    const tagLine = p.riotIdTagline || "";
    const m = matchupLookup.get(`${sig.key}|${playerKey}`);
    lobby.push({
      riotId: tagLine ? `${gameName}#${tagLine}` : gameName,
      compLabel: sig.label, compKey: sig.key, carry: sig.carry,
      placement: p.placement,
      counterRate: m ? m.aheadRate : null, encounters: m ? m.encounters : 0,
    });
  }
  lobby.sort((a, b) => a.placement - b.placement);
  return lobby;
}

function analyzeLobbyInsight(lobby: LobbyEntry[], bench: Benchmark | null, placement: number | null): Insight[] {
  const strongCounters = lobby.filter(
    (l) => l.counterRate !== null && l.counterRate >= COUNTER_RATE_THRESHOLD && l.encounters >= COUNTER_MIN_ENCOUNTERS,
  );
  if (!strongCounters.length) return [];
  const names = strongCounters.slice(0, 3).map((l) => `${l.compLabel} (${Math.round((l.counterRate as number) * 100)}% des rencontres)`).join(", ");
  const underperformed = !!(bench && placement && placement - bench.avg_placement >= PLACEMENT_UNDERPERFORM_THRESHOLD);
  if (underperformed) {
    return [{ type: "warning", category: "Adversaires",
      text: `Ton lobby comptait ${strongCounters.length} compo(s) qui prennent historiquement l'avantage sur la tienne dans les lobbies partagés : ${names} — un facteur possible dans ce placement en dessous de la moyenne de ta comp.` }];
  }
  return [{ type: "info", category: "Adversaires",
    text: `Présentes dans ton lobby malgré tout : ${names}, qui contrent historiquement ta comp dans les lobbies partagés.` }];
}

export interface Report {
  compLabel: string; compKey: string; carry: string | null;
  placement: number | null; level: number | null; goldLeft: number | null; lastRound: number | null;
  units: ExtractedUnit[]; insights: Insight[]; lobby: LobbyEntry[];
}

export function buildReport(participant: any, nameMap: Record<string, string>, benchmarks: Record<string, Benchmark>,
                             match: any, puuid: string,
                             matchupLookup: Map<string, { aheadRate: number; encounters: number }>,
                             itemOffense: Record<string, string>): Report {
  const sig = deriveComp(participant, nameMap, itemOffense);
  const bench = benchmarks[sig.key] || null;

  const placement = participant.placement ?? null;
  const level = participant.level ?? null;
  const goldLeft = participant.gold_left ?? null;
  const lastRound = participant.last_round ?? null;

  const insights: Insight[] = [];

  if (bench) {
    if (goldLeft !== null && bench.avg_gold_left !== null) {
      const diff = goldLeft - bench.avg_gold_left;
      if (diff >= GOLD_DIFF_THRESHOLD) {
        insights.push({ type: "warning", category: "Économie",
          text: `${goldLeft} or non dépensé en fin de partie, contre ${bench.avg_gold_left.toFixed(1)} en moyenne sur cette comp — cet or aurait pu financer des niveaux ou des rerolls supplémentaires.` });
      } else if (diff <= -GOLD_DIFF_THRESHOLD) {
        insights.push({ type: "info", category: "Économie",
          text: `Seulement ${goldLeft} or restant, nettement moins que la moyenne (${bench.avg_gold_left.toFixed(1)}) — dépense agressive, cohérent si ça a soutenu le placement.` });
      } else {
        insights.push({ type: "good", category: "Économie",
          text: `Gestion de l'or dans la moyenne de cette comp (${goldLeft} vs ${bench.avg_gold_left.toFixed(1)}).` });
      }
    }

    if (level !== null && bench.avg_level !== null) {
      const ldiff = level - bench.avg_level;
      if (ldiff <= -LEVEL_DIFF_THRESHOLD) {
        insights.push({ type: "warning", category: "Niveau",
          text: `Niveau ${level} en fin de partie, en retard sur la moyenne (${bench.avg_level.toFixed(1)}) pour cette comp — un retard de niveau limite souvent la taille du board en fin de partie.` });
      } else if (ldiff >= LEVEL_DIFF_THRESHOLD) {
        insights.push({ type: "good", category: "Niveau",
          text: `Niveau ${level} en fin de partie, au-dessus de la moyenne (${bench.avg_level.toFixed(1)}) — bonne courbe de leveling.` });
      } else {
        insights.push({ type: "good", category: "Niveau",
          text: `Niveau dans la moyenne de cette comp (${level} vs ${bench.avg_level.toFixed(1)}).` });
      }
    }

    if (lastRound !== null && bench.avg_last_round !== null) {
      const rdiff = lastRound - bench.avg_last_round;
      if (rdiff <= -ROUND_DIFF_THRESHOLD) {
        insights.push({ type: "warning", category: "Survie",
          text: `Sortie au round ${lastRound}, contre ${bench.avg_last_round.toFixed(1)} en moyenne sur cette comp — une élimination plus précoce qu'attendu.` });
      }
    }

    insights.push({ type: placement && placement <= 4 ? "good" : "warning", category: "Résultat",
      text: `Placement ${placement} — la moyenne pour cette comp est ${bench.avg_placement.toFixed(2)} (top 4 dans ${Math.round(bench.top4_rate * 100)}% des cas).` });
  } else {
    insights.push({ type: "info", category: "Échantillon",
      text: "Pas assez de données collectées sur cette comp précise pour établir des benchmarks fiables — voici les faits bruts de la partie, sans comparaison." });
  }

  const units = extractUnits(participant, nameMap);
  insights.push(...analyzeItems(units, bench, sig.carry));

  let lobby: LobbyEntry[] = [];
  if (match && puuid) {
    lobby = buildLobby(match, puuid, nameMap, matchupLookup, sig.key, itemOffense);
    insights.push(...analyzeLobbyInsight(lobby, bench, placement));
  }

  return { compLabel: sig.label, compKey: sig.key, carry: sig.carry, placement, level, goldLeft, lastRound, units, insights, lobby };
}
