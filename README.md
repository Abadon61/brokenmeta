# Comp Tracker — TFT tier list engine

Pipeline Python qui se connecte à l'API Riot Games, échantillonne de vrais
matchs classés TFT par région/rang, et calcule une tier list S/A/B/C à
partir de statistiques réelles (pas de guide écrit à la main).

## Setup

```bash
py -m pip install -r requirements.txt
```

La clé API vit dans `.env` (jamais dans le code) :
```
RIOT_API_KEY=RGAPI-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```
Clé de dev actuelle : limites basses (20 req/s, 100 req/2min), expire sous 24h.
Le client (`src/tft_tracker/riot_client.py`) respecte ces deux fenêtres et
retry/backoff sur 429 et 5xx.

## Lancer une collecte

```bash
py run.py                                    # défaut : EUW,NA,BR,KR / PLATINUM
py run.py --regions EUW --tiers PLATINUM,DIAMOND
py run.py --all-tiers --regions EUW          # IRON -> CHALLENGER
py run.py --regions EUW,NA,BR,KR --matchups  # + proxy de matchups
```

Sortie : `data/output/tierlist.json` (et `matchups.json` avec `--matchups`).
Les matchs bruts sont mis en cache disque dans `data/raw/` (un match ne
change jamais une fois joué, donc on ne le re-télécharge pas).

## Régions

CN n'est pas accessible via l'API publique Riot (serveur opéré par Tencent,
aucune route régionale ne le couvre) — remplacé par BR dans l'échantillon
par défaut.

| Code | Plateforme | Cluster régional |
|------|-----------|-------------------|
| EUW  | euw1      | europe |
| NA   | na1       | americas |
| BR   | br1       | americas |
| KR   | kr        | asia |

## Rangs

`IRON, BRONZE, SILVER, GOLD, PLATINUM, EMERALD, DIAMOND, MASTER, GRANDMASTER, CHALLENGER`.
Sélecteur par défaut : **PLATINUM** (`config.DEFAULT_TIERS`).

**Limitation connue côté Riot** : les endpoints apex (`MASTER`/`GRANDMASTER`/
`CHALLENGER`) renvoient actuellement `entries: []` sur EUW/NA/KR (endpoint
flaky documenté côté Riot, pas un souci de requête). Le pipeline détecte
l'échec et bascule automatiquement sur `DIAMOND I` comme proxy haut-elo,
en le signalant explicitement dans `sample.brackets[].fallback_note` du
JSON de sortie.

## Méthodologie

**Signature de comp** : Riot ne publie pas d'identifiant de composition. On
utilise une heuristique (comme les trackers publics type tactics.tools) :
les 2 traits actifs les plus "poussés" (style/tier le plus haut) + le
champion portant le plus d'objets (carry). Ex : `Elderwood Solar — Rakan`.

**Force brute vs performance réelle** : une comp très jouée devient plus
dure à réussir (copies d'unités/items contestées). On n'a pas accès aux
données de shop/round par round, donc on utilise le *play rate* comme proxy
de contestation : régression linéaire pondérée de `avg_placement` sur
`play_rate` à travers toute la méta échantillonnée (comps avec ≥5
observations). La pente positive mesure combien de placement une comp perd
juste parce qu'elle est populaire.

```
brute_force_placement = avg_placement - regression_slope * play_rate
```

Une comp dont `brute_force_placement` est nettement meilleur que
`avg_placement` est **contestée** (forte en théorie, dure à obtenir en
pratique). Une comp où les deux se rejoignent est **non contestée**.

**Tier S/A/B/C** : comps triées par top4_rate puis avg_placement, coupées en
percentiles (S = top 12%, A = 12-40%, B = 40-75%, C = 75-100%), uniquement
parmi les comps avec ≥5 observations (`min_sample_for_tier`). En dessous,
tier `"?"` (pas assez de données).

**Matchups (bonus)** : l'API `Match-V1` ne donne pas qui affronte qui à
chaque round (pas de données de combat publiques). Proxy retenu : dans
chaque lobby réel (8 joueurs), pour chaque paire de comps différentes
présentes, celle qui place mieux est comptée "devant" l'autre. Agrégé sur
beaucoup de lobbies, ça révèle des tendances de contre — pas un vrai combat
log.

## Limitation actuelle : taille d'échantillon

Avec une clé dev, un run raisonnable (~150-200 requêtes, 2-3 min) ramène
quelques centaines de matchs. Comme la signature de comp est assez fine (2
traits + carry), la plupart des combinaisons distinctes n'apparaissent que
1-2 fois — normal, seules les comps réellement méta se répètent assez pour
franchir le seuil de 5 observations. Le dernier run (240 matchs réels,
4 régions, Platine) a peuplé 78 comps sur 883 en tier S/A/B/C. Une tier
list plus dense demandera soit une clé de prod (limites bien plus hautes),
soit des runs répétés qui s'accumulent dans le cache.

## Envoyer les données vers Wix

Le front est prévu sur Wix. Le pipeline peut pousser directement les
résultats dans des **Wix Data Collections** (Content Manager) via l'API
Wix Data (upsert par lot, idempotent — relancer ne duplique rien).

**1. Créer les collections dans le Content Manager Wix** (Editor -> Content
Manager -> Add Collection), avec ces Collection ID et champs exacts :

| Collection ID | Champs |
|---|---|
| `Comps` | `label`(Text), `traits`(Array), `carry`(Text), `tier`(Text), `playCount`(Number), `playRate`(Number), `contestationLevel`(Text), `contestationIndex`(Number), `avgPlacement`(Number), `top4Rate`(Number), `winRate`(Number), `hasEnoughData`(Boolean) |
| `Matchups` | `compA`(Text), `compALabel`(Text), `compB`(Text), `compBLabel`(Text), `encounters`(Number), `aAheadRate`(Number), `bAheadRate`(Number) |
| `Champions` | `pickCount`(Number), `pickRate`(Number), `avgPlacement`(Number), `top4Rate`(Number), `avgStarLevel`(Number), `threeStarRate`(Number), `topItems`(Array of Object: `item`,`count`,`rate`) |

(`_id` est un champ système Wix — pas besoin de le créer, on lui donne
directement la clé de la comp/du champion au moment du push.)

**2. Générer une clé API Wix** : Dashboard Wix -> Settings -> API Keys ->
Generate API Key, scope **Write Data Items**. Copier la clé immédiatement
(affichée une seule fois).

**3. Récupérer le Site ID** : Dashboard Wix -> Settings -> général du site.

**4. Ajouter les deux dans `.env`** (idéalement en les tapant toi-même
directement dans le fichier, pour que la clé ne transite jamais ailleurs) :
```
WIX_API_KEY=...
WIX_SITE_ID=...
```

**5. Pousser les données** :
```bash
py sync_wix.py                  # les trois collections
py sync_wix.py --only comps     # une seule
```
Peut aussi être enchaîné après une collecte (`run.py` génère les JSON,
`sync_wix.py` les pousse).

## Prochaines étapes

- Page web (thème sombre "board hexagonal", accents dorés, tier-colors
  S=rouge/A=or/B=teal/C=gris) consommant `tierlist.json` — HTML/CSS/JS
  autonome pour rester embeddable dans Wix.
- Demander la clé de prod à Riot une fois le prototype validé.
- Agréger les runs dans le temps (le cache `data/raw/` s'y prête déjà).
