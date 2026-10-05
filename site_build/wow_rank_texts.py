"""Texts of the ranking detail pages (/wow-forever/classement/<spec>/): page strings and the written rotation of each spec.
The rotations describe what the simulator's kits do (site_build/sim60/*.js); the numbers on the page come from data/wow_ranking60.json."""

SLOTS = {
    "fr": {"head": "Tête", "neck": "Cou", "shoulder": "Épaules", "back": "Dos", "chest": "Torse", "wrist": "Poignets", "hands": "Mains", "waist": "Taille", "legs": "Jambes", "feet": "Pieds",
           "ring1": "Anneau 1", "ring2": "Anneau 2", "trinket1": "Bijou 1", "trinket2": "Bijou 2", "mh": "Main droite", "oh": "Main gauche", "th": "Deux mains", "rng": "Distance", "shield": "Bouclier", "held": "Tenu en main gauche"},
    "en": {"head": "Head", "neck": "Neck", "shoulder": "Shoulders", "back": "Back", "chest": "Chest", "wrist": "Wrists", "hands": "Hands", "waist": "Waist", "legs": "Legs", "feet": "Feet",
           "ring1": "Ring 1", "ring2": "Ring 2", "trinket1": "Trinket 1", "trinket2": "Trinket 2", "mh": "Main hand", "oh": "Off hand", "th": "Two-hand", "rng": "Ranged", "shield": "Shield", "held": "Held in off hand"},
}
SLOT_ORDER = ["head", "neck", "shoulder", "back", "chest", "wrist", "hands", "waist", "legs", "feet", "ring1", "ring2", "trinket1", "trinket2", "mh", "oh", "th", "shield", "held", "rng"]
STAT_LABELS = {
    "fr": {"str": "Force", "agi": "Agilité", "sta": "Endurance", "int": "Intelligence", "spi": "Esprit"},
    "en": {"str": "Strength", "agi": "Agility", "sta": "Stamina", "int": "Intellect", "spi": "Spirit"},
}

TX = {
    "fr": {
        "kicker": "CLASSEMENT NIVEAU 60", "h1": "{cls} {spec} : build niveau 60, talents, rotation et DPS",
        "title": "{cls} {spec} niveau 60 : build, rotation, DPS", "desc": "Build niveau 60 du {cls} {spec} dans WoW: Forever : talents, équipement, rotation et DPS par technique, calculés par simulation.",
        "intro": "Voici ce que notre simulateur obtient pour le {cls} {spec} au niveau 60 : l'équipement que l'optimiseur trouve parmi les objets connus de la bêta, les talents du préréglage, la rotation suivie et les dégâts de chaque technique sur un combat de 180 secondes contre un boss immobile.",
        "dps_label": "DPS moyen", "tps_label": "Menace par seconde", "rank_label": "Rang", "rank_of": "sur {n}", "dtps_label": "Dégâts subis / s", "health_label": "Santé",
        "sec_rotation": "Rotation", "sec_opening": "Ouverture observée", "opening_hint": "Les 14 premières secondes du combat simulé : les coups qui infligent des dégâts directs, dans l'ordre.",
        "sec_abilities": "Dégâts par technique", "col_ability": "Technique", "col_share": "Part", "col_dps": "DPS", "col_casts": "Lancers / min", "col_crit": "Critiques",
        "sec_talents": "Talents choisis", "points": "points", "sec_gear": "Équipement niveau 60", "col_slot": "Emplacement", "col_item": "Objet", "col_source": "Provenance",
        "sec_stats": "Statistiques du personnage", "st_ap": "Puissance d'attaque", "st_sp": "Puissance des sorts", "st_crit": "Critique", "st_hit": "Toucher", "st_haste": "Hâte", "st_mana": "Mana", "st_armor": "Armure",
        "sec_uptimes": "Bonus actifs", "sec_effects": "Effets d'objets simulés",
        "sec_assump": "Hypothèses", "assump": "Simulation sur 180 secondes, boss immobile de niveau 63, buffs et consommables de raid de la famille de la classe, race standard, effets d'objets activés. Les stats de base du niveau 60 et plusieurs valeurs de Classic sont des estimations signalées dans le simulateur. Les résultats bougeront avec le jeu.",
        "links": "Aller plus loin", "l_sim": "Ouvrir dans le simulateur", "l_guide": "Guide de la spécialisation", "l_calc": "Calculateur de talents", "l_rank": "Retour au classement",
        "prev": "Précédent", "next": "Suivant", "no_data": "Données indisponibles.", "dungeon": "Donjon", "raid": "Raid", "min": "min",
    },
    "en": {
        "kicker": "LEVEL 60 RANKING", "h1": "{cls} {spec}: level 60 build, talents, rotation and DPS",
        "title": "{cls} {spec} level 60: build, rotation, DPS", "desc": "Level 60 {cls} {spec} build in WoW: Forever: talents, gear, rotation and DPS by ability, computed by simulation.",
        "intro": "This is what our simulator gets for the {cls} {spec} at level 60: the gear the optimizer finds among the items known from the beta, the preset talents, the rotation followed and the damage of every ability over a 180-second fight against a stationary boss.",
        "dps_label": "Average DPS", "tps_label": "Threat per second", "rank_label": "Rank", "rank_of": "of {n}", "dtps_label": "Damage taken / s", "health_label": "Health",
        "sec_rotation": "Rotation", "sec_opening": "Observed opening", "opening_hint": "The first 14 seconds of the simulated fight: the hits that deal direct damage, in order.",
        "sec_abilities": "Damage by ability", "col_ability": "Ability", "col_share": "Share", "col_dps": "DPS", "col_casts": "Casts / min", "col_crit": "Crits",
        "sec_talents": "Talents chosen", "points": "points", "sec_gear": "Level 60 gear", "col_slot": "Slot", "col_item": "Item", "col_source": "Source",
        "sec_stats": "Character stats", "st_ap": "Attack power", "st_sp": "Spell power", "st_crit": "Crit", "st_hit": "Hit", "st_haste": "Haste", "st_mana": "Mana", "st_armor": "Armor",
        "sec_uptimes": "Active buffs", "sec_effects": "Item effects simulated",
        "sec_assump": "Assumptions", "assump": "A 180-second fight against a stationary level-63 boss, the raid buffs and consumables of the class's family, a standard race, item effects on. Level-60 base stats and several Classic values are estimates, flagged in the simulator. Results will move with the game.",
        "links": "Go further", "l_sim": "Open in the simulator", "l_guide": "Spec guide", "l_calc": "Talent calculator", "l_rank": "Back to the ranking",
        "prev": "Previous", "next": "Next", "no_data": "No data.", "dungeon": "Dungeon", "raid": "Raid", "min": "min",
    },
}

# What each kit does, in priority order (site_build/sim60/*.js)
ROTATION = {
    "warrior_fury": {
        "fr": ["Bloodthirst dès qu'il est disponible.", "Whirlwind (et le Whirlwind de Raging Blows) à chaque fois qu'il est prêt.", "Execute sous 20 % de vie de la cible.", "Heroic Strike sur la prochaine attaque avec le rage en surplus.", "Berserker Rage, Bloodrage, Death Wish et Recklessness à chaque fois qu'ils sont prêts."],
        "en": ["Bloodthirst whenever it is ready.", "Whirlwind (and Raging Blows' Whirlwind) on cooldown.", "Execute under 20% target health.", "Heroic Strike on the next swing with spare rage.", "Berserker Rage, Bloodrage, Death Wish and Recklessness on cooldown."]},
    "warrior_arms": {
        "fr": ["Mortal Strike dès qu'il est prêt.", "Overpower quand il s'allume : après une esquive de la cible, ou grâce à Bloodthrill.", "Rend toutes les 21 secondes pour nourrir Bloodthrill.", "Slam juste après le coup de la main droite, sans retarder le suivant (Improved Slam).", "Execute sous 20 % de vie, Heroic Strike avec le rage en surplus."],
        "en": ["Mortal Strike on cooldown.", "Overpower when it lights up: after a target dodge, or from Bloodthrill.", "Rend every 21 seconds to feed Bloodthrill.", "Slam right after the main-hand swing, without delaying the next one (Improved Slam).", "Execute under 20% health, Heroic Strike with spare rage."]},
    "warrior_protection": {
        "fr": ["Shield Slam dès qu'il est prêt.", "Revenge après une esquive, une parade ou un blocage.", "Heroic Strike avec le rage en surplus (il donne plus de menace par point de rage).", "Sunder Armor avec le reste du rage.", "Bloodrage à chaque fois qu'il est prêt."],
        "en": ["Shield Slam on cooldown.", "Revenge after a dodge, parry or block.", "Heroic Strike with spare rage (it gives more threat per rage point).", "Sunder Armor with the rest of the rage.", "Bloodrage on cooldown."]},
    "rogue_combat": {
        "fr": ["Garder Slice and Dice actif.", "Sinister Strike pour construire les points de combo.", "Eviscerate à 5 points de combo.", "Adrenaline Rush et Blade Flurry à chaque fois qu'ils sont prêts.", "Instant Poison en main droite, Deadly Poison en main gauche."],
        "en": ["Keep Slice and Dice up.", "Sinister Strike to build combo points.", "Eviscerate at 5 combo points.", "Adrenaline Rush and Blade Flurry on cooldown.", "Instant Poison on the main hand, Deadly Poison on the off hand."]},
    "rogue_assassination": {
        "fr": ["Garder Slice and Dice actif.", "Mutilate avec deux dagues, sinon Sinister Strike ou Backstab, pour construire les points de combo.", "Eviscerate à 5 points de combo, après Cold Blood.", "Instant Poison en main droite, Deadly Poison en main gauche (Mutilate profite de Deadly Poison)."],
        "en": ["Keep Slice and Dice up.", "Mutilate with two daggers, otherwise Sinister Strike or Backstab, to build combo points.", "Eviscerate at 5 combo points, after Cold Blood.", "Instant Poison on the main hand, Deadly Poison on the off hand (Mutilate benefits from Deadly Poison)."]},
    "rogue_subtlety": {
        "fr": ["Garder Slice and Dice actif.", "Hemorrhage (ou Backstab avec des dagues) pour construire les points de combo.", "Eviscerate à 5 points de combo.", "Instant Poison en main droite, Deadly Poison en main gauche."],
        "en": ["Keep Slice and Dice up.", "Hemorrhage (or Backstab with daggers) to build combo points.", "Eviscerate at 5 combo points.", "Instant Poison on the main hand, Deadly Poison on the off hand."]},
    "mage_fire": {
        "fr": ["Frostfire Bolt comme sort de base.", "Pyroblast quand Heating Up a réduit son incantation.", "Fire Blast à chaque fois qu'il est prêt.", "Scorch pour entretenir l'effet d'Improved Scorch.", "Combustion à chaque fois qu'elle est prête ; Evocation et gemme de mana pour la mana."],
        "en": ["Frostfire Bolt as the filler.", "Pyroblast when Heating Up has shortened its cast.", "Fire Blast on cooldown.", "Scorch to keep the Improved Scorch effect up.", "Combustion on cooldown; Evocation and the mana gem for mana."]},
    "mage_frost": {
        "fr": ["Frostbolt comme sort de base.", "Ice Lance sur une cible gelée (Fingers of Frost, Winter's Chill).", "Evocation et gemme de mana pour la mana."],
        "en": ["Frostbolt as the filler.", "Ice Lance on a Frozen target (Fingers of Frost, Winter's Chill).", "Evocation and the mana gem for mana."]},
    "mage_arcane": {
        "fr": ["Arcane Missiles (canalisé) comme sort principal.", "Arcane Power à chaque fois qu'il est prêt.", "Arcane Blast n'est pas lancé : ses charges coûtent trop de mana sur un combat de boss.", "Evocation et gemme de mana pour la mana."],
        "en": ["Arcane Missiles (channeled) as the main spell.", "Arcane Power on cooldown.", "Arcane Blast is not cast: its stacks cost too much mana over a boss fight.", "Evocation and the mana gem for mana."]},
    "warlock_affliction": {
        "fr": ["Corruption, Siphon Life et la malédiction (Bane of Doom) toujours actifs.", "Wrack à chaque fois qu'il est prêt.", "Shadow Bolt comme sort de base.", "Life Tap quand la mana baisse.", "Le diablotin lance son Firebolt en continu."],
        "en": ["Keep Corruption, Siphon Life and the curse (Bane of Doom) up.", "Wrack on cooldown.", "Shadow Bolt as the filler.", "Life Tap when mana runs low.", "The Imp casts Firebolt continuously."]},
    "warlock_destruction": {
        "fr": ["Immolate, Corruption et la malédiction toujours actifs.", "Conflagrate et Shadowburn à chaque fois qu'ils sont prêts.", "Incinerate comme sort de base.", "Life Tap quand la mana baisse.", "Le diablotin lance son Firebolt en continu."],
        "en": ["Keep Immolate, Corruption and the curse up.", "Conflagrate and Shadowburn on cooldown.", "Incinerate as the filler.", "Life Tap when mana runs low.", "The Imp casts Firebolt continuously."]},
    "warlock_demonology": {
        "fr": ["Le diablotin reste en jeu : Firebolt en continu, boosté par Demonic Knowledge, Unholy Power et Master Demonologist.", "Immolate, Corruption et la malédiction toujours actifs.", "Conflagrate et Shadowburn à chaque fois qu'ils sont prêts.", "Shadow Bolt comme sort de base ; Life Tap quand la mana baisse."],
        "en": ["The Imp stays out: Firebolt continuously, boosted by Demonic Knowledge, Unholy Power and Master Demonologist.", "Keep Immolate, Corruption and the curse up.", "Conflagrate and Shadowburn on cooldown.", "Shadow Bolt as the filler; Life Tap when mana runs low."]},
    "hunter_marksmanship": {
        "fr": ["Auto Shot en continu.", "Arcane Shot à chaque fois qu'il est prêt.", "Serpent Sting toujours actif.", "Multi-Shot et Sniper Shot à chaque fois qu'ils sont prêts.", "Rapid Fire à chaque fois qu'il est prêt."],
        "en": ["Auto Shot continuously.", "Arcane Shot on cooldown.", "Keep Serpent Sting up.", "Multi-Shot and Sniper Shot on cooldown.", "Rapid Fire on cooldown."]},
    "hunter_beastmastery": {
        "fr": ["Auto Shot en continu.", "Arcane Shot et Multi-Shot à chaque fois qu'ils sont prêts.", "Serpent Sting toujours actif.", "Bestial Wrath et Rapid Fire à chaque fois qu'ils sont prêts.", "Le familier attaque en continu (morsure et griffes)."],
        "en": ["Auto Shot continuously.", "Arcane Shot and Multi-Shot on cooldown.", "Keep Serpent Sting up.", "Bestial Wrath and Rapid Fire on cooldown.", "The pet attacks continuously (bite and claw)."]},
    "hunter_survival": {
        "fr": ["Auto Shot en continu.", "Arcane Shot et Multi-Shot à chaque fois qu'ils sont prêts.", "Serpent Sting toujours actif.", "Rapid Fire à chaque fois qu'il est prêt.", "Le familier attaque en continu."],
        "en": ["Auto Shot continuously.", "Arcane Shot and Multi-Shot on cooldown.", "Keep Serpent Sting up.", "Rapid Fire on cooldown.", "The pet attacks continuously."]},
    "hunter_melee": {
        "fr": ["Attaques de mêlée avec deux armes.", "Raptor Strike à chaque fois qu'il est prêt.", "Mongoose Bite juste après une esquive de la cible.", "Strider Kick à chaque fois qu'il est prêt.", "Le familier attaque en continu."],
        "en": ["Melee swings with two weapons.", "Raptor Strike on cooldown.", "Mongoose Bite right after a target dodge.", "Strider Kick on cooldown.", "The pet attacks continuously."]},
    "priest_shadow": {
        "fr": ["Shadow Word: Pain et Devouring Plague toujours actifs.", "Mind Blast à chaque fois qu'il est prêt.", "Shadow Word: Death quand il est prêt.", "Mind Flay comme sort de base.", "Inner Focus pour la mana."],
        "en": ["Keep Shadow Word: Pain and Devouring Plague up.", "Mind Blast on cooldown.", "Shadow Word: Death when ready.", "Mind Flay as the filler.", "Inner Focus for mana."]},
    "shaman_elemental": {
        "fr": ["Searing Totem posé toutes les 55 secondes.", "Flame Shock toujours actif.", "Lava Burst dès qu'il est prêt (+20 % de dégâts si Flame Shock est actif).", "Lightning Bolt comme sort de base ; Lightning Overload ajoute des éclairs gratuits.", "Chain Lightning, Earth Shock et Fire Nova coûtent trop de mana pour une seule cible et ne sont pas lancés."],
        "en": ["Searing Totem dropped every 55 seconds.", "Keep Flame Shock up.", "Lava Burst on cooldown (+20% damage if Flame Shock is up).", "Lightning Bolt as the filler; Lightning Overload adds free bolts.", "Chain Lightning, Earth Shock and Fire Nova cost too much mana for one target and are not cast."]},
    "shaman_enhancement": {
        "fr": ["Ouverture : Searing Totem, puis Flame Shock (Strength of Earth et Grace of Air déjà en place) ; le Totem est reposé toutes les 55 secondes.", "Stormstrike dès qu'il est prêt : il donne +20 % de dégâts de nature au prochain Lightning Bolt, Chain Lightning ou Earth Shock, et, avec Improved Stormstrike, rend la moitié de la régénération de mana pendant 15 secondes.", "Lightning Bolt juste après Stormstrike pour profiter du +20 % (il rapporte plus que sur Earth Shock) ; ensuite Lightning Bolt à partir de 3 piles de Maelstrom Weapon : chaque pile retire 4 % par rang au temps d'incantation et au coût, et les attaques de mêlée continuent pendant l'incantation.", "Earth Shock dans le créneau de choc (recharge partagée de 6 s), Flame Shock dès que son effet sur la durée va se terminer. Frost Shock donne le même résultat qu'Earth Shock, et Fire Nova ne rapporte rien de mesurable : le temps de sort limite, pas les recharges.", "Windfury Weapon sur l'arme à deux mains (2 attaques supplémentaires) ; Rage of the Farseer à chaque fois qu'elle est prête."],
        "en": ["Opening: Searing Totem, then Flame Shock (Strength of Earth and Grace of Air already up); the Totem is put down again every 55 seconds.", "Stormstrike on cooldown: it gives +20% nature damage to the next Lightning Bolt, Chain Lightning or Earth Shock and, with Improved Stormstrike, keeps half the mana regeneration while casting for 15 seconds.", "Lightning Bolt right after Stormstrike to take the +20% (it is worth more there than on Earth Shock); then Lightning Bolt from 3 Maelstrom Weapon stacks: each stack takes 4% per rank off its cast time and mana cost, and melee swings go on while it is cast.", "Earth Shock in the shock slot (shared 6 s cooldown), Flame Shock as soon as its damage over time is about to end. Frost Shock gives the same result as Earth Shock, and Fire Nova adds nothing measurable: casting time is the limit, not the cooldowns.", "Windfury Weapon on the two-hand weapon (2 extra attacks); Rage of the Farseer on cooldown."]},
    "druid_balance": {
        "fr": ["Moonfire et Insect Swarm toujours actifs.", "Starfire comme sort de base.", "Wrath pour alterner et profiter d'Eclipse.", "Potions et gemme de mana."],
        "en": ["Keep Moonfire and Insect Swarm up.", "Starfire as the filler.", "Wrath to alternate and benefit from Eclipse.", "Mana potions and the mana gem."]},
    "druid_feral": {
        "fr": ["Savage Roar et Rip toujours actifs.", "Shred pour construire les points de combo, Rake maintenu.", "Ferocious Bite à 5 points de combo.", "Tiger's Fury à chaque fois qu'il est prêt, Shifting Power pour récupérer de l'énergie, Berserk à chaque fois qu'il est prêt."],
        "en": ["Keep Savage Roar and Rip up.", "Shred to build combo points, keep Rake up.", "Ferocious Bite at 5 combo points.", "Tiger's Fury on cooldown, Shifting Power to regain energy, Berserk on cooldown."]},
    "paladin_retribution": {
        "fr": ["Seal of Command toujours actif ; Judgement of Command dès qu'il est prêt.", "Holy Strike dès qu'il est prêt.", "Hammer of Wrath dans la phase d'exécution.", "Les attaques de mêlée à deux mains font le reste des dégâts."],
        "en": ["Keep Seal of Command up; Judgement of Command on cooldown.", "Holy Strike on cooldown.", "Hammer of Wrath in the execute phase.", "Two-handed melee swings deal the rest of the damage."]},
    "paladin_protection": {
        "fr": ["Seal of Righteousness toujours actif ; Judgement dès qu'il est prêt.", "Holy Shield à chaque fois qu'il est prêt : plus de blocages et des dégâts sacrés à chaque blocage.", "Holy Strike dès qu'il est prêt.", "Reckoning : une attaque supplémentaire après chaque blocage."],
        "en": ["Keep Seal of Righteousness up; Judgement on cooldown.", "Holy Shield on cooldown: more blocks and holy damage on each block.", "Holy Strike on cooldown.", "Reckoning: an extra attack after each block."]},
    "druid_bear": {
        "fr": ["Lacerate entretenu à 5 charges.", "Maul sur chaque attaque avec le rage disponible.", "Swipe avec le reste du rage.", "Enrage à chaque fois qu'il est prêt."],
        "en": ["Keep Lacerate stacked to 5.", "Maul on every swing with the available rage.", "Swipe with the rest of the rage.", "Enrage on cooldown."]},
}
