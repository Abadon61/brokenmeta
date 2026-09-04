# CoreMeta v2 — Architecture

Statut : proposition de structure, pas encore implémentée. Écrit en réponse à la demande du 2026-09-01 ("CoreMeta Outrun 2" + specs MVP inspirées de TFTable). Complète [README.md](README.md) — n'y touche pas.

## 0. Blocage constaté avant toute chose : les augments

Vérifié deux fois sur ce projet (résumé de session initiale, puis re-testé le 2026-09-01 sur 480 participants frais du cache Set 18) : **le champ `augments` n'existe pas du tout** dans la réponse Match-V1 pour ce set — pas juste vide, absent du schéma retourné par Riot. Confirmé par recherche de toute clé contenant `"augment"` (insensible à la casse) → aucun résultat.

Conséquence directe sur les 4 fonctionnalités MVP demandées :

| # | Fonctionnalité demandée | Statut |
|---|---|---|
| 1 | Tier list Win Share / Top4 Share séparés + diversité du meta | ✅ Buildable aujourd'hui — toute la donnée existe déjà |
| 2 | Pipeline : augments par stage | ❌ **Bloqué** (voir ci-dessus) |
| 2 | Pipeline : board final, items, traits, placement, gold_left, level, last_round | ✅ Buildable — `gold_left`/`last_round`/`level` confirmés présents dans le JSON brut, juste jamais extraits jusqu'ici |
| 2 | Clustering en archétypes nommés | ✅ Buildable — on a déjà un système heuristique qui marche (`comp_signature.py`), voir §5 |
| 3 | Page comp : infos standard | ✅ Buildable — existe déjà dans CoreMeta Outrun |
| 3 | Page comp : arbre de décision augments (sankey) | ❌ **Bloqué**, même cause que #2 |
| 4 | Analyse de partie : gold non dépensé, courbe de niveau, items | ✅ Buildable |
| 4 | Analyse de partie : augment choisi vs winrate réel | ❌ **Bloqué**, même cause |

**Ce que ça veut dire concrètement** : le schéma ci-dessous garde des tables `augment_picks` / `augment_transition_stats` en dormance (prêtes, mais vides) plutôt que de les omettre — si Riot expose un jour ce champ (ou si on trouve une autre source, ex. scraping du client, API tierce non-officielle), on branche sans migration. Mais tant que ce n'est pas résolu, ni le pipeline ni les pages ne peuvent afficher de vrai arbre de décision par augment. Piste à explorer si tu veux vraiment cette fonctionnalité : demander explicitement sur le Discord développeurs tiers de Riot (mentionné dans la doc des "team planner codes" comme point de contact officiel) si `augments` est prévu ou s'il y a une raison qu'il soit absent pour ce set.

## 1. Vue d'ensemble

```
Riot API ──▶ pipeline Python (existant, étendu) ──▶ SQLite ──▶ Next.js (SSR/SSG) ──▶ visiteurs
                                                        ▲
                                    analyse de partie ──┘ (lookup live, backend Next.js, jamais côté client)
```

Principes :
- **On garde le pipeline Python existant** (`riot_client.py`, `collector.py`, `leaderboard.py`, `tierlist.py`, `comp_signature.py`, `champion_stats.py`, `champion_images.py`) — il est déjà rate-limité, mis en cache, testé sur ~2500 vrais matches ce mois-ci. On l'étend pour écrire dans une DB au lieu de (ou en plus de) JSON plat.
- **SQLite**, pas Postgres, pour l'instant : zéro infra à gérer, un seul writer (le pipeline, lancé à la demande), lecture intensive côté Next.js. Migration vers Postgres triviale plus tard si l'hébergement l'exige (Prisma gère les deux avec le même schéma à un provider près).
- **Next.js App Router**, pages de comp en SSG avec revalidation **à la demande** (`revalidatePath`/`revalidateTag`), déclenchée par un script à la fin de chaque run du pipeline — pas de revalidation par requête ni par timer, cohérent avec la décision "on rafraîchit seulement quand je le demande" prise hier.
- **Aucune clé Riot ni logique d'appel API côté client** — la page d'analyse de partie appelle Riot depuis une route serveur Next.js (`app/api/match-analysis/route.ts`), jamais depuis le navigateur.

## 2. Arborescence

```
coremeta/
├── apps/
│   └── web/                              # Next.js
│       ├── app/
│       │   ├── comps/
│       │   │   ├── page.tsx              # tier list — SSG, revalidateTag('comps')
│       │   │   └── [slug]/page.tsx       # fiche comp — SSG, revalidateTag('comps')
│       │   ├── champions/[slug]/page.tsx # SSG, revalidateTag('champions')
│       │   ├── leaderboard/page.tsx      # SSG, revalidateTag('leaderboard')
│       │   ├── world-stat/page.tsx       # SSG, revalidateTag('leaderboard')
│       │   ├── analyze/
│       │   │   ├── page.tsx              # formulaire Riot ID — client component
│       │   │   └── [matchId]/page.tsx    # rapport — rendu serveur à la demande, pas de cache
│       │   └── api/
│       │       ├── revalidate/route.ts   # appelé par le pipeline après un refresh (secret partagé)
│       │       └── match-analysis/route.ts  # seule route qui parle à Riot en live
│       ├── lib/
│       │   ├── db.ts                     # client Prisma (singleton)
│       │   ├── riot-live.ts              # client Riot minimal, serveur uniquement, pour /analyze
│       │   └── benchmarks.ts             # requêtes d'agrégats meta pour comparer une partie
│       ├── prisma/
│       │   ├── schema.prisma
│       │   └── migrations/
│       └── components/
├── packages/
│   └── ingestion/                        # le pipeline Python actuel, promu en package versionné
│       ├── tft_tracker/                  # inchangé : riot_client, collector, tierlist,
│       │                                 # comp_signature, champion_stats, champion_images,
│       │                                 # leaderboard, matchup_proxy, config, pipeline
│       ├── db/
│       │   ├── writer.py                 # upsert matches/participants/units/comps → SQLite
│       │   └── schema.sql                # source de vérité, miroir de prisma/schema.prisma
│       ├── clustering/
│       │   └── archetypes.py             # signature heuristique + passe de fusion (§5)
│       └── run.py                        # étend le run.py actuel (ajoute --write-db, --revalidate)
├── data/
│   ├── coremeta.db                       # SQLite (gitignored)
│   └── raw/                              # cache matches/comptes/icônes existant (gitignored)
├── .env                                   # RIOT_API_KEY, REVALIDATE_SECRET (gitignored)
├── ARCHITECTURE_V2.md                     # ce fichier
└── README.md
```

Migration douce depuis l'existant : `src/tft_tracker/` déménage vers `packages/ingestion/tft_tracker/` sans changement de logique interne, seul `pipeline.py` gagne une option d'écriture DB en plus des JSON qu'il écrit déjà (on garde les deux tant que l'artifact CoreMeta Outrun reste en usage — il consomme les JSON, pas la DB).

## 3. Schéma de base de données

```sql
-- Une ligne par cycle de collecte, pour que CHAQUE stat affichée soit traçable
-- à un patch/moment précis (exigence de transparence explicite du brief).
CREATE TABLE patches (
  id            INTEGER PRIMARY KEY,
  tft_set       TEXT NOT NULL,        -- ex. "TFTSet18"
  patch_label   TEXT,                 -- ex. "18.1", résolu si possible depuis les patch notes
  collected_at  TEXT NOT NULL         -- ISO 8601 UTC
);

CREATE TABLE matches (
  match_id      TEXT PRIMARY KEY,     -- ex. "EUW1_1234567890"
  patch_id      INTEGER NOT NULL REFERENCES patches(id),
  region        TEXT NOT NULL,        -- EUW / NA / BR / KR
  queue_id      INTEGER NOT NULL,
  game_datetime TEXT NOT NULL,
  ingested_at   TEXT NOT NULL
);

CREATE TABLE participants (
  id                   INTEGER PRIMARY KEY,
  match_id             TEXT NOT NULL REFERENCES matches(match_id),
  puuid                TEXT NOT NULL,
  placement            INTEGER NOT NULL,
  win                  INTEGER NOT NULL,   -- booléen brut Riot (placement=1)
  level                INTEGER,
  gold_left            INTEGER,
  last_round           INTEGER,
  archetype_id         INTEGER REFERENCES comp_archetypes(id),
  augments_available   INTEGER NOT NULL DEFAULT 0,  -- toujours 0 tant que le blocage §0 n'est pas levé
  UNIQUE(match_id, puuid)
);

CREATE TABLE participant_units (
  id               INTEGER PRIMARY KEY,
  participant_id   INTEGER NOT NULL REFERENCES participants(id),
  champion         TEXT NOT NULL,     -- nom d'affichage réel, déjà corrigé (cf. Pebbles/Sentry)
  cost             INTEGER,
  star_level       INTEGER,
  items            TEXT,              -- JSON array, objets complets uniquement
  slot_order       INTEGER            -- ordre d'apparition, pas la position hexagonale
);

-- Dormant tant que §0 n'est pas résolu -- présent pour éviter une migration plus tard.
CREATE TABLE augment_picks (
  participant_id   INTEGER NOT NULL REFERENCES participants(id),
  stage_label      TEXT NOT NULL,     -- '2-1' | '3-2' | '4-2'
  augment_id       TEXT NOT NULL,
  pick_order       INTEGER
);

CREATE TABLE comp_archetypes (
  id              INTEGER PRIMARY KEY,
  patch_id        INTEGER NOT NULL REFERENCES patches(id),
  key             TEXT NOT NULL,      -- identité stable (trait dominant + carry)
  label           TEXT NOT NULL,      -- nom affiché
  primary_trait   TEXT,
  carry_champion  TEXT,
  UNIQUE(patch_id, key)
);

-- Le coeur de la fonctionnalité #1 : Win Share ET Top4 Share séparés,
-- calculés par (archétype, patch, région, palier) -- jamais un seul "winrate" fourre-tout.
CREATE TABLE comp_archetype_stats (
  archetype_id      INTEGER NOT NULL REFERENCES comp_archetypes(id),
  patch_id          INTEGER NOT NULL REFERENCES patches(id),
  region            TEXT NOT NULL,     -- ou 'ALL'
  tier_bracket      TEXT NOT NULL,     -- ex. 'DIAMOND_PLUS'
  play_count        INTEGER NOT NULL,
  win_count         INTEGER NOT NULL,
  top4_count        INTEGER NOT NULL,
  avg_placement     REAL NOT NULL,
  play_rate         REAL NOT NULL,
  win_share         REAL NOT NULL,     -- win_count / play_count
  top4_share        REAL NOT NULL,     -- top4_count / play_count
  contestation_index REAL,
  computed_at       TEXT NOT NULL,
  PRIMARY KEY (archetype_id, patch_id, region, tier_bracket)
);

-- Indicateur de diversité/concentration du meta -- Herfindahl-Hirschman sur les
-- play_rate de comp_archetype_stats, + "nombre effectif de comps" (1/HHI),
-- une mesure standard et lisible ("le meta se joue en pratique autour de N
-- comps distinctes", pas juste "HHI = 0.14").
CREATE TABLE meta_diversity (
  patch_id                INTEGER NOT NULL REFERENCES patches(id),
  region                  TEXT NOT NULL,
  tier_bracket             TEXT NOT NULL,
  herfindahl_index        REAL NOT NULL,
  effective_archetype_count REAL NOT NULL,
  computed_at              TEXT NOT NULL,
  PRIMARY KEY (patch_id, region, tier_bracket)
);

-- Dormant tant que §0 n'est pas résolu.
CREATE TABLE augment_transition_stats (
  patch_id          INTEGER NOT NULL REFERENCES patches(id),
  path_signature    TEXT NOT NULL,     -- ex. augment 2-1 + augment 3-2 concaténés
  archetype_id      INTEGER NOT NULL REFERENCES comp_archetypes(id),
  count             INTEGER NOT NULL,
  win_rate          REAL NOT NULL
);

CREATE TABLE leaderboard_snapshots (
  id           INTEGER PRIMARY KEY,
  patch_id     INTEGER NOT NULL REFERENCES patches(id),
  region       TEXT NOT NULL,
  captured_at  TEXT NOT NULL
);

CREATE TABLE leaderboard_entries (
  snapshot_id     INTEGER NOT NULL REFERENCES leaderboard_snapshots(id),
  rank            INTEGER NOT NULL,
  riot_id         TEXT NOT NULL,
  tier            TEXT NOT NULL,
  league_points   INTEGER NOT NULL,
  wins            INTEGER NOT NULL,
  losses          INTEGER NOT NULL
);

-- Cache pour la fonctionnalité #4 -- évite de recalculer/rappeler Riot à
-- chaque fois que quelqu'un revisite le même rapport.
CREATE TABLE match_analysis_cache (
  puuid         TEXT NOT NULL,
  match_id      TEXT NOT NULL,
  computed_at   TEXT NOT NULL,
  report_json   TEXT NOT NULL,
  PRIMARY KEY (puuid, match_id)
);
```

`prisma/schema.prisma` est un miroir direct de ce fichier (Prisma pour les migrations + l'accès typé côté Next.js ; le pipeline Python écrit via `sqlite3` standard, pas besoin d'ORM côté Python).

## 4. Pipeline d'ingestion (extension de l'existant)

Ce qui existe déjà et qu'on garde tel quel : `RiotClient` (rate limiter à fenêtres glissantes, retry avec backoff sur 429/5xx, cache disque par match_id et par puuid), `collect_bracket()` (league-v1 → puuids → match-v1 → filtre `queueId == 1100`).

Ce qu'on ajoute :
1. **`db/writer.py`** — après chaque `collect_bracket()`, upsert idempotent (`INSERT OR REPLACE`, clé = `match_id`/`(match_id, puuid)`) des matches/participants/unités dans SQLite. Idempotent par construction puisque les matches sont immuables une fois joués — un re-run n'écrit jamais de doublon.
2. **Nouveaux champs extraits** : `gold_left`, `last_round`, `win` — présents dans le JSON brut, jamais lus jusqu'ici par `tierlist.py`/`champion_stats.py`. Simple ajout dans la boucle d'extraction existante.
3. **File d'attente / retry** : déjà couvert par `RateLimiter` (fenêtres 20/1s + 100/120s) et le retry avec backoff exponentiel sur `_get()`. Pas besoin d'une vraie queue (Celery/Redis) tant que la collecte reste sur une seule machine, à la demande, à ce volume (centaines à quelques milliers de requêtes par run) — à reconsidérer seulement si la clé de production permet/nécessite une collecte concurrente sur plusieurs workers.
4. **Clé de production Riot** : aucune ligne de code ne dépend de la clé dev vs prod (même header `X-Riot-Token`), donc c'est un pur changement de valeur dans `.env` le jour où elle est approuvée — mais **c'est un vrai prérequis avant mise en ligne réelle** (le brief le dit lui-même), pas juste "plus tard" : une clé dev expire toutes les 24h ([[riot-dev-key-24h-ttl]]), donc un site public avec régénération automatique est structurellement impossible sans elle.

## 5. Clustering des comps en archétypes

L'existant (`comp_signature.py`) : heuristique — trait dominant (par style/tier) + unité la plus itemisée comme carry. Rapide, déterministe, **déjà lisible/nommé nativement** (ex. "Riftbeast Pebbles") — ce qui correspond exactement à l'exigence "archétypes nommés et lisibles" du brief.

**Recommandation : ne pas jeter ça pour un clustering non-supervisé classique** (k-means/k-modes sur les boards). Un clustering pur donnerait des clusters numérotés qu'il faudrait ensuite nommer à la main pour rester lisible — on perdrait l'avantage actuel pour un gain incertain.

**Proposition hybride** à la place :
1. Garder la signature heuristique comme identité primaire (inchangé).
2. Ajouter une **passe de fusion** après coup : deux signatures dont les boards se recouvrent à ≥70% (indice de Jaccard sur l'ensemble des champions) ET qui partagent le même trait dominant sont fusionnées sous l'archétype le plus fréquent des deux. Ça répond directement à un souci déjà noté dans le code actuel (`comp_signature.py`, docstring) : des variantes quasi-identiques qui ne diffèrent que sur le 9e/10e slot flex se retrouvent aujourd'hui comptées comme des comps séparées, ce qui dilue l'échantillon — un vrai problème vu la taille des échantillons par région (ex. BR).
3. Le calcul de fusion tourne une fois par cycle de collecte (`clustering/archetypes.py`), sur les archétypes déjà présents dans `comp_archetypes` pour ce patch — pas en temps réel.

## 6. Endpoints API internes (Next.js Route Handlers)

Le contenu SEO-critique (tier list, fiche comp) est du SSG pur — pas d'appel API au chargement, tout est déjà dans le HTML initial. Les endpoints ci-dessous servent soit l'hydratation client (filtres interactifs sur la tier list déjà rendue), soit des besoins fondamentalement dynamiques :

| Route | Méthode | Usage |
|---|---|---|
| `/api/comps` | GET | Liste filtrable (région/palier/tri) — hydrate les filtres client sur la page SSG |
| `/api/comps/[slug]` | GET | JSON d'un comp — alimente le sankey interactif une fois §0 résolu |
| `/api/leaderboard` | GET | `?region=` |
| `/api/world-stats` | GET | Courbe elo, comparaison top 10, top comps par région |
| `/api/match-analysis` | POST | `{riotId, region}` → résout le puuid (Account-V1), retourne les parties récentes à choisir. **Seule route qui appelle Riot en live, jamais exposée côté client** |
| `/api/match-analysis/[matchId]` | POST | Calcule le rapport (comparaison aux benchmarks `comp_archetype_stats`), met en cache dans `match_analysis_cache` |
| `/api/revalidate` | POST | Appelée par le pipeline en fin de run (secret partagé côté serveur), déclenche `revalidateTag('comps')` etc. |

## 7. Ce qui reste ouvert

1. **Augments (§0)** — bloquant réel pour #2/#3/#4 tant que non résolu. À ta décision : abandonner cette partie, la remplacer par un arbre équivalent sur un autre signal disponible (ex. choix d'objet/trait plutôt qu'augment), ou creuser une source de données alternative.
2. **Hébergement** — le schéma DB/pipeline ne présuppose rien (SQLite tourne aussi bien en local qu'sur un petit serveur), mais Next.js SSR + une route qui parle à Riot en live veut dire un vrai serveur quelque part (Vercel, VPS, etc.) — pas juste un Artifact statique. Sujet à trancher avant mise en ligne réelle, comme convenu hier ("on verra avec une API plus longue et un site en ligne plus tard").
3. **Clé de production Riot** — prérequis avant toute régénération automatique en public.
