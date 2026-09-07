// gameplan.js — génère un plan de reroll/leveling textuel à partir d'une composition.
// Réutilise les mêmes données que le simulateur (Set 18 / patch 18.1).

const LEVEL_ODDS = {
  1: [100, 0, 0, 0, 0], 2: [100, 0, 0, 0, 0], 3: [75, 25, 0, 0, 0],
  4: [55, 30, 15, 0, 0], 5: [45, 33, 20, 2, 0], 6: [30, 40, 25, 5, 0],
  7: [16, 30, 43, 10, 1], 8: [15, 20, 32, 30, 3], 9: [10, 17, 25, 33, 15],
  10: [5, 10, 20, 40, 25], 11: [1, 2, 12, 50, 35],
};
const BAG_SIZE = { 1: 30, 2: 25, 3: 18, 4: 10, 5: 9 };
const UNIQUE_CHAMPS = { 1: 14, 2: 13, 3: 14, 4: 14, 5: 10 };
const TOTAL_IN_POOL = Object.fromEntries(Object.keys(BAG_SIZE).map((c) => [c, BAG_SIZE[c] * UNIQUE_CHAMPS[c]]));
const XP_STEP = { 1: 2, 2: 2, 3: 6, 4: 10, 5: 20, 6: 36, 7: 60, 8: 68, 9: 68, 10: 84 };

function levelUpCost(a, b) {
  if (b <= a) return 0;
  let c = 0;
  for (let l = a; l < b; l++) c += XP_STEP[l] || 0;
  return c;
}
function starToCopies(star) { return star === 1 ? 1 : star === 2 ? 3 : 9; }

// Meilleur niveau pour un groupe de cibles : on simule à chaque niveau candidat et on
// garde celui qui minimise l'or médian nécessaire pour tout obtenir. Plus lent qu'un
// simple calcul sur la table d'odds, mais c'est la seule façon d'être vraiment juste
// dès qu'il y a plusieurs coûts différents à faire progresser ensemble (cf. le cas
// Eclipse Kayle : un raccourci sans simulation donnait niveau 3 au lieu de 5, un
// résultat faux qui aurait mal orienté les joueurs).
function bestLevelForGroup(group, levelCandidates, trials = 400) {
  let best = { level: levelCandidates[0], median: Infinity };
  for (const level of levelCandidates) {
    const { median } = estimateGoldForTarget(group, level, trials);
    if (median < best.median) best = { level, median };
  }
  return best.level;
}

// Simulation légère pour estimer l'or nécessaire à un palier de réussite donné.
function sampleCost(level) {
  const odds = LEVEL_ODDS[level];
  let r = Math.random() * 100, cum = 0;
  for (let i = 0; i < 5; i++) { cum += odds[i]; if (r < cum) return i + 1; }
  return 5;
}
function estimateGoldForTarget(group, level, trials = 1500, maxRerolls = 150) {
  if (group.length === 0) return 0;
  const needed = {};
  group.forEach((t) => (needed[t.id] = starToCopies(t.star)));
  const rerollsToComplete = [];
  for (let trial = 0; trial < trials; trial++) {
    const owned = {};
    group.forEach((t) => (owned[t.id] = 0));
    let r = 0;
    for (; r < maxRerolls; r++) {
      let done = true;
      for (const t of group) if (owned[t.id] < needed[t.id]) { done = false; break; }
      if (done) break;
      for (let s = 0; s < 5; s++) {
        const cost = sampleCost(level);
        const cand = group.filter((t) => t.cost === cost && owned[t.id] < needed[t.id]);
        if (cand.length === 0) continue;
        const sub = group.filter((t) => t.cost === cost).reduce((a, t) => a + owned[t.id], 0);
        const tot = TOTAL_IN_POOL[cost] - sub;
        if (tot <= 0) continue;
        let roll = Math.random() * tot, picked = null;
        for (const c of cand) {
          const rem = BAG_SIZE[c.cost] - owned[c.id];
          if (roll < rem) { picked = c; break; }
          roll -= rem;
        }
        if (picked) owned[picked.id]++;
      }
    }
    rerollsToComplete.push(r);
  }
  rerollsToComplete.sort((a, b) => a - b);
  const pct = (p) => rerollsToComplete[Math.floor(p * (trials - 1))] * 2;
  return { p25: pct(0.25), median: pct(0.5), p75: pct(0.75) };
}

// targets: [{ id, name, cost, star }]
function generateGameplan(targets) {
  const priority = targets.filter((t) => t.star >= 2); // ce qui demande un vrai reroll dédié (3 ou 9 copies)
  const flex = targets.filter((t) => t.star === 1);     // ce qui s'obtient au fil de l'eau

  const steps = [];

  if (priority.length > 0) {
    const rerollLevel = bestLevelForGroup(priority, [3, 4, 5, 6, 7, 8, 9]);
    const gold = estimateGoldForTarget(priority, rerollLevel);

    steps.push({
      title: `Se poser au niveau ${rerollLevel} pour rerolls ${priority.map((t) => t.name || t.id).join(", ")}`,
      description: `Niveau qui minimise l'or nécessaire pour ${[...new Set(priority.map((t) => t.cost))].join("/")}-coût(s) en même temps. Compter environ ${gold.p25}-${gold.p75} or pour une chance de 25% à 75% d'obtenir toutes les copies visées (médiane ~${gold.median} or).`,
    });

    const finalLevel = flex.length > 0
      ? bestLevelForGroup(flex, [rerollLevel, rerollLevel + 1, rerollLevel + 2, 7, 8, 9, 10, 11].filter((l) => l >= rerollLevel))
      : rerollLevel;

    if (finalLevel > rerollLevel && flex.length > 0) {
      const lvlCost = levelUpCost(rerollLevel, finalLevel);
      steps.push({
        title: `Une fois les carries obtenus, monter au niveau ${finalLevel} (${lvlCost} or)`,
        description: `Passage direct sans s'arrêter aux niveaux intermédiaires : ils n'apportent rien de plus une fois qu'on a fini de rerolls les coûts ${[...new Set(priority.map((t) => t.cost))].join("/")}.`,
      });
    }

    if (flex.length > 0) {
      const goldFlex = estimateGoldForTarget(flex, finalLevel);
      steps.push({
        title: `Compléter ${flex.map((t) => t.name || t.id).join(", ")} (1★ chacun)`,
        description: `Peu de regards nécessaires : médiane ~${goldFlex.median} or pour tout obtenir à ce niveau.`,
      });
    }
  } else if (flex.length > 0) {
    const level = bestLevelForGroup(flex, [4, 5, 6, 7, 8, 9]);
    const gold = estimateGoldForTarget(flex, level);
    steps.push({
      title: `Niveau ${level}, quelques rerolls suffisent`,
      description: `Aucun carry à 2-3★ dans cette compo : médiane ~${gold.median} or pour compléter le board.`,
    });
  }

  steps.push({
    title: "Garder le reste de l'or pour les objets et la vie",
    description: "Une fois la compo posée, prioriser la sécurité du board plutôt que le sur-reroll.",
  });

  return steps;
}

module.exports = { generateGameplan };
