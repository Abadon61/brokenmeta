"""BrokenMeta article on the class tuning hotfixes seen on live Forever servers on 30 Oct 2026 (Druid and Paladin talent
trees, plus smaller changes for Mage, Priest, Warlock and Warrior).

Facts rewritten from the cited Wowhead news. Nothing here is simulated: the talent trees were reorganised and the
engine does not model these changes yet, and the text says so. Format: see the module docstring of wow_articles.py.
"""

_SRC = ("Wowhead : Massive Talent Tree Changes to Druids and Paladins - Class Tuning for WoW: Forever (30 Oct. 2026)",
        "https://www.wowhead.com/forever/news/massive-talent-tree-changes-to-druids-and-paladins-class-tuning-for-wow-forever-383670")
_ZAM = "https://wow.zamimg.com/images/wow/icons/large/"

TUNING_1030 = {
    "slug": "druide-paladin-arbres-talents-reglage-wow-forever",
    "date": "2026-11-02",
    "updated": "2026-11-02",
    "draft": False,
    "tag": "tuning",
    "kind": "eq",
    "class": None,
    "image": _ZAM + "spell_arcane_arcane03.jpg",
    "sources": [_SRC],
    "fr": {
        "title": "Druide et Paladin WoW Forever : talents remaniés",
        "description": "Avant le lancement de WoW Forever, Druide et Paladin voient leurs arbres de talents remaniés : Genèse doublée, Shifting Power à 8 s, Holy Shield réduit.",
        "h1": "Druide et Paladin dans WoW Forever : les talents remaniés avant le lancement",
        "lede": "À quelques jours du lancement de **WoW Forever**, Blizzard a appliqué des correctifs à chaud sur les serveurs : les arbres de talents du **Druide** et du **Paladin** changent beaucoup, et le Mage, le Prêtre, le Démoniste et le Guerrier reçoivent des retouches plus légères. Ces modifications ont depuis été confirmées par les notes de développement officielles du 3 novembre, et elles sont [eq]dans notre simulateur niveau 60[/eq].",
        "body": [
            ("cards", [("spell_arcane_arcane03", "Genèse (Druide Équilibre)", "Bonus de 5 % → 10 % au rang max", "up"),
                       ("spell_druid_displacement", "Puissance fluctuante (Féral)", "Recharge de 16 s → 8 s", "up"),
                       ("spell_holy_blessingofprotection", "Bouclier sacré (Paladin Protection)", "Dégâts réduits de 32 %", "nerf"),
                       ("spell_holy_power", "Puissance sacrée (Paladin Sacré)", "Bonus des soins critiques de 10 à 50 %", "eq")]),
            ("h2", "Druide dans WoW Forever : buffs Équilibre, Féral et Restauration"),
            ("list", [
                "{eq} Plusieurs talents du Druide **changent de place** dans l'arbre : retrouve le détail dans notre calculateur de talents Druide (lien en bas de page).",
                "{up} {i:spell_arcane_arcane03} **Genèse** (Équilibre) : le bonus aux dégâts et aux soins périodiques passe à [up]2/4/6/8/10 %[/up] par rang, contre 1/2/3/4/5 % avant.",
                "{up} {i:spell_druid_displacement} **Puissance fluctuante** (Féral) : sa recharge tombe à [up]8 s[/up] (16 s avant). **Morsure primordiale** gagne en dégâts ([up]42/62/77[/up] au lieu de 26/38/59) et change de position.",
                "{up} {i:spell_nature_unyeildingstamina} **Chef de la meute** augmente maintenant tous les coups critiques, plus seulement les critiques de mêlée et à distance.",
                "{eq} {i:ability_druid_berserk} **Berserk** est retiré de l'arbre Féral et un nouveau talent, **Lacerate**, y apparaît.",
                "{up} {i:spell_nature_healingtouch} **Naturaliste** (Restauration) double son effet sur les dégâts ([up]2/4/6/8/10 %[/up]) et réduit aussi l'incantation de Croissance sauvage.",
                "{nerf} **Swiftmend** exige maintenant que la cible ait votre Rétablissement ou votre Récupération, pas n'importe quel effet. **Croissance sauvage** a un temps d'incantation de 3 s. Nouveau talent **Bloom** en Restauration.",
            ]),
            ("h2", "Paladin dans WoW Forever : un arbre de talents très remanié"),
            ("list", [
                "{eq} **Sacré** : nouveaux talents **Boundless Light** et **Oath of Light**. {i:spell_holy_healingfocus} **Précision divine** passe à 2 rangs (+8 % de toucher des sorts sacrés au max, contre 18 %) mais réduit la durée des silences de 20 %.",
                "{up} {i:spell_holy_power} **Puissance sacrée** augmente maintenant le **bonus** des soins critiques de [up]10 à 50 %[/up], et non plus la chance de critique. **Sceaux améliorés** monte jusqu'au rang 5 à 15 % (rang 3 à 9 % avant).",
                "{eq} {i:spell_arcane_blink} **Focalisation spirituelle** passe à 5 rangs (2 avant) avec 70 % de chance au max. **Réverence** n'a plus que 2 rangs pour la même régénération de mana (30 %).",
                "{nerf} {i:spell_holy_blessingofprotection} **Bouclier sacré** (Protection) inflige [nerf]32 % de dégâts en moins[/nerf], mais coûte 100 de mana au lieu de 150. **Credo de fer** perd des rangs (5 avant) : [up]30 % de menace[/up] au rang max au lieu de 15 %, contre 6 % de dégâts subis en moins au lieu de 10 %.",
                "{up} **Protection** : Fureur vertueuse s'apprend dès le niveau 10 (16 avant) et Fureur vertueuse améliorée réduit les dégâts subis de [up]3/6/9 %[/up] (2/4/6 % avant). Nouveaux talents **Shieldsworn** et **Stoicism**.",
                "{eq} **Vindicte** : {i:spell_holy_retributionaura} **Conviction** passe à 3 rangs et affecte tous les sorts de 6 % au max (5 rangs et 5 % avant). Vindication n'augmente plus la puissance d'attaque. Un nouveau sort, **Turn Evil**, apparaît.",
            ]),
            ("h2", "Mage, Prêtre, Démoniste, Guerrier : les autres retouches du patch"),
            ("list", [
                "{up} **Mage Givre** : **Lance de glace** inflige [up]300 % de dégâts bonus[/up] aux cibles gelées (200 % avant) mais a maintenant 8 s de recharge. **Barrière de glace** monte à 15 % de dégâts de givre (3 % avant) et **Winter's Chill** à 20 % pour le prochain Cône de froid (5 % avant).",
                "{eq} **Mage Feu** : **Masse critique** plafonne à 6 % de critique au rang 3 (10 % au rang 5 avant), tandis qu'**Incineration** monte à 10 % au rang 5 (6 % au rang 3 avant).",
                "{nerf} **Prêtre** : **Mot de l'ombre : Mort** inflige [nerf]30 % de dégâts de contrecoup[/nerf] à son lanceur, contre 10 % avant. Un talent **Holy Binding** est ajouté côté Sacré.",
                "{eq} **Démoniste** : **Drains améliorés** augmente la mana drainée par Drain de mana, et non plus un autre sort. **Guerrier** : **Revanche** utilise 25 % de la puissance d'attaque à tous les rangs.",
            ]),
            ("h2", "Ce que ça change pour ton Druide ou ton Paladin"),
            ("bars", {"unit": "%", "before": "Avant", "after": "Après", "rows": [("Genèse, rang max", 5, 10), ("Naturaliste, rang max", 5, 10), ("Fureur vertueuse améliorée", 6, 9)]}),
            ("list", [
                "**Druide Équilibre et Restauration** : deux talents de dégâts doublent, c'est le gain le plus net du patch pour ces spécialisations.",
                "**Druide Féral** : la recharge de Puissance fluctuante divisée par deux et la perte de Berserk changent la rotation, à tester en jeu.",
                "**Paladin Protection** : Bouclier sacré est plus faible mais moins cher, et Credo de fer donne plus de menace. Le gain de menace compense peut-être la perte de dégâts, rien n'est mesuré.",
                "**Paladin Sacré** : Puissance sacrée agit maintenant sur la puissance des critiques, pas sur leur fréquence, et Focalisation spirituelle devient un vrai talent à 5 rangs.",
                "Les Druides et Paladins devront **refaire leur build** : repasse par le calculateur de talents avant le lancement du 4 novembre.",
            ]),
            ("note", "Ces changements, vus d'abord sur les serveurs Forever, ont été confirmés par les notes de développement officielles du 3 novembre (voir notre article sur ces notes) et sont depuis dans notre simulateur niveau 60 ; cet article ne donne pas de chiffre de DPS, ils sont dans le classement."),
        ],
        "faq": [
            ("Le Druide a-t-il été buff dans WoW Forever avant le lancement ?", "Oui, plusieurs talents montent : Genèse (Équilibre) et Naturaliste (Restauration) doublent leur effet, la recharge de Puissance fluctuante (Féral) passe de 16 à 8 secondes. Ces changements ont été confirmés par les notes officielles du 3 novembre."),
            ("Que devient Bouclier sacré pour le Paladin Protection ?", "Il inflige 32 % de dégâts en moins mais coûte 100 de mana au lieu de 150. Credo de fer donne par ailleurs 30 % de menace en plus, pour 6 % de dégâts subis en moins. Ces valeurs sont dans notre simulateur depuis les notes du 3 novembre."),
        ],
        "links": [
            ("Calculateur de talents Druide", "wow-forever/talents/druid/"),
            ("Calculateur de talents Paladin", "wow-forever/talents/paladin/"),
            ("Guide Paladin Protection", "wow-forever/guides/paladin/protection/"),
            ("Tier list WoW Forever : meilleures classes", "wow-forever/tier-list/"),
        ],
    },
    "en": {
        "title": "Druid and Paladin WoW Forever: Talent Trees Reworked",
        "description": "Ahead of WoW Forever launch, Druid and Paladin talent trees are reworked: Genesis doubled, Shifting Power at 8 s, Holy Shield weakened.",
        "h1": "Druid and Paladin in WoW Forever: talent trees reworked before launch",
        "lede": "A few days before the **WoW Forever** launch, Blizzard applied hotfixes on live servers: the **Druid** and **Paladin** talent trees change a lot, and Mage, Priest, Warlock and Warrior get lighter touches. These changes have since been confirmed by the official development notes of November 3, and they are [eq]in our level-60 simulator[/eq].",
        "body": [
            ("cards", [("spell_arcane_arcane03", "Genesis (Balance Druid)", "Bonus from 5% to 10% at max rank", "up"),
                       ("spell_druid_displacement", "Shifting Power (Feral)", "Cooldown 16 s to 8 s", "up"),
                       ("spell_holy_blessingofprotection", "Holy Shield (Protection Paladin)", "Damage cut by 32%", "nerf"),
                       ("spell_holy_power", "Holy Power (Holy Paladin)", "Crit healing bonus of 10% to 50%", "eq")]),
            ("h2", "Druid in WoW Forever: Balance, Feral and Restoration buffs"),
            ("list", [
                "{eq} Several Druid talents **change position** in the tree: see the before/after in our Druid talent calculator (link at the bottom of the page).",
                "{up} {i:spell_arcane_arcane03} **Genesis** (Balance): the periodic damage and healing bonus is now [up]2/4/6/8/10%[/up] per rank, up from 1/2/3/4/5%.",
                "{up} {i:spell_druid_displacement} **Shifting Power** (Feral): its cooldown drops to [up]8 s[/up] (16 s before). **Primal Bite** deals more damage ([up]42/62/77[/up] instead of 26/38/59) and moves.",
                "{up} {i:spell_nature_unyeildingstamina} **Leader of the Pack** now boosts all critical strikes, not only melee and ranged crits.",
                "{eq} {i:ability_druid_berserk} **Berserk** is removed from the Feral tree and a new talent, **Lacerate**, appears.",
                "{up} {i:spell_nature_healingtouch} **Naturalist** (Restoration) doubles its damage effect ([up]2/4/6/8/10%[/up]) and also shortens the Wild Growth cast.",
                "{nerf} **Swiftmend** now requires the target to have your Regrowth or Rejuvenation, not just any effect. **Wild Growth** has a 3 s cast time. New Restoration talent **Bloom**.",
            ]),
            ("h2", "Paladin in WoW Forever: a heavily reworked talent tree"),
            ("list", [
                "{eq} **Holy**: new talents **Boundless Light** and **Oath of Light**. {i:spell_holy_healingfocus} **Divine Precision** drops to 2 ranks (+8% hit for Holy spells at max, was 18%) but cuts silence duration by 20%.",
                "{up} {i:spell_holy_power} **Holy Power** now raises the crit healing **bonus** by [up]10 to 50%[/up], not the crit chance. **Improved Seals** now goes to rank 5 at 15% (rank 3 at 9% before).",
                "{eq} {i:spell_arcane_blink} **Spiritual Focus** goes to 5 ranks (2 before) with 70% chance at max. **Reverence** has only 2 ranks for the same mana regeneration (30%).",
                "{nerf} {i:spell_holy_blessingofprotection} **Holy Shield** (Protection) deals [nerf]32% less damage[/nerf] but costs 100 mana instead of 150. **Iron Creed** loses ranks (5 before): [up]30% threat[/up] at max rank instead of 15%, for 6% less damage taken instead of 10%.",
                "{up} **Protection**: Righteous Fury is learned at level 10 (was 16) and Improved Righteous Fury cuts damage taken by [up]3/6/9%[/up] (2/4/6% before). New talents **Shieldsworn** and **Stoicism**.",
                "{eq} **Retribution**: {i:spell_holy_retributionaura} **Conviction** drops to 3 ranks and affects all spells by 6% at max (5 ranks and 5% before). Vindication no longer raises attack power. A new spell, **Turn Evil**, appears.",
            ]),
            ("h2", "Mage, Priest, Warlock, Warrior: the other tweaks in the patch"),
            ("list", [
                "{up} **Frost Mage**: **Ice Lance** deals [up]300% bonus damage[/up] to frozen targets (200% before) but now has an 8 s cooldown. **Ice Barrier** rises to 15% Frost damage (3% before) and **Winter's Chill** to 20% for the next Cone of Cold (5% before).",
                "{eq} **Fire Mage**: **Critical Mass** caps at 6% crit at rank 3 (10% at rank 5 before), while **Incineration** rises to 10% at rank 5 (6% at rank 3 before).",
                "{nerf} **Priest**: **Shadow Word: Death** deals [nerf]30% backlash damage[/nerf] to its caster, up from 10%. A **Holy Binding** talent is added on the Holy side.",
                "{eq} **Warlock**: **Improved Drains** now boosts the mana drained by Drain Mana, not another spell. **Warrior**: **Revenge** scales with 25% attack power at all ranks.",
            ]),
            ("h2", "What it means for your Druid or Paladin"),
            ("bars", {"unit": "%", "before": "Before", "after": "After", "rows": [("Genesis, max rank", 5, 10), ("Naturalist, max rank", 5, 10), ("Improved Righteous Fury", 6, 9)]}),
            ("list", [
                "**Balance and Restoration Druid**: two damage talents double, the clearest gain of the patch for these specs.",
                "**Feral Druid**: Shifting Power's cooldown cut in half and the loss of Berserk change the rotation, to be tested in game.",
                "**Protection Paladin**: Holy Shield is weaker but cheaper, and Iron Creed gives more threat. The threat gain may offset the lost damage, nothing is measured.",
                "**Holy Paladin**: Holy Power now acts on crit strength, not frequency, and Spiritual Focus becomes a real 5-rank talent.",
                "Druids and Paladins will need to **rebuild their talents**: go through the calculator again before the November 4 launch.",
            ]),
            ("note", "These changes, first seen on Forever servers, were confirmed by the official development notes of November 3 (see our article on those notes) and are now in our level-60 simulator; this article gives no DPS number, they are in the ranking."),
        ],
        "faq": [
            ("Was the Druid buffed in WoW Forever before launch?", "Yes, several talents go up: Genesis (Balance) and Naturalist (Restoration) double their effect, and Shifting Power's (Feral) cooldown drops from 16 to 8 seconds. These changes were confirmed by the official notes of November 3."),
            ("What happens to Holy Shield for Protection Paladin?", "It deals 32% less damage but costs 100 mana instead of 150. Iron Creed also gives 30% more threat, for 6% less damage taken. These values are in our simulator since the notes of November 3."),
        ],
        "links": [
            ("Druid talent calculator", "wow-forever/talents/druid/"),
            ("Paladin talent calculator", "wow-forever/talents/paladin/"),
            ("Protection Paladin guide", "wow-forever/guides/paladin/protection/"),
            ("WoW Forever tier list: best classes", "wow-forever/tier-list/"),
        ],
    },
}
