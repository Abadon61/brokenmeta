"""Rotation section of the specialization guides (level 60): our simulated priority list (wow_rank_texts.ROTATION) set against what the Icy Veins
Forever guides recommend. The Icy Veins guides are written for the level-30 beta and for leveling, so the comparison keeps what both agree on,
adopts what the simulator confirmed at level 60 and says where the two differ and why. Icy Veins' advice is paraphrased, never copied.
Keys are "class/spec" as in data/wow_guides/content.json. HEALER_MAIN: healing specs are not simulated, their list is Icy Veins' healing rotation."""

# What the Icy Veins guide recommends (level 30 beta, paraphrased)
IV = {
    "warrior/fury": {
        "fr": ["Battle Shout toujours actif, Bloodrage entre les combats, Charge pour ouvrir, Demoralizing Shout sur la cible.", "Victory Rush après une mort, Rend tôt, Overpower après une esquive, Sunder Armor une ou deux fois.", "Execute déconseillé pendant la montée en niveau."],
        "en": ["Keep Battle Shout up, Bloodrage between pulls, Charge to open, Demoralizing Shout on the target.", "Victory Rush after a kill, Rend early, Overpower after a dodge, Sunder Armor once or twice.", "Execute is not recommended while leveling."]},
    "warrior/arms": {
        "fr": ["Battle Shout, Bloodrage entre les combats, Charge pour ouvrir, Demoralizing Shout.", "Rend tôt, Overpower après une esquive ou un déclenchement de Bloodthrill, Slam juste après un coup automatique, Sunder Armor une ou deux fois.", "Spearing Strike comme dépense de rage (dégâts triplés contre les Géants et les Dragonnets), Execute déconseillé en montée de niveau."],
        "en": ["Battle Shout, Bloodrage between pulls, Charge to open, Demoralizing Shout.", "Rend early, Overpower after a dodge or a Bloodthrill proc, Slam right after an auto-attack, Sunder Armor once or twice.", "Spearing Strike as a rage dump (triple damage against Giants and Dragonkin), Execute not recommended while leveling."]},
    "warrior/protection": {
        "fr": ["La rage vient des attaques automatiques, des dégâts subis et des techniques ; Bloodrage pour la maintenir.", "Heroic Strike transforme un coup blanc en coup spécial qui ne génère pas de rage : c'est surtout une dépense de fin de jeu quand il y a trop de rage."],
        "en": ["Rage comes from auto-attacks, damage taken and abilities; Bloodrage keeps it up.", "Heroic Strike turns a white hit into a special attack that generates no rage: it is mostly an end-game dump when you have too much rage."]},
    "rogue/combat": {
        "fr": ["Ouvrir par Ambush depuis le camouflage, Backstab si vous êtes derrière la cible, sinon Sinister Strike.", "Eviscerate ou Slice and Dice à 5 points de combo ; Instant Poison sur les deux armes."],
        "en": ["Open with Ambush from stealth, Backstab if you are behind the target, otherwise Sinister Strike.", "Eviscerate or Slice and Dice at 5 combo points; Instant Poison on both weapons."]},
    "rogue/assassination": {
        "fr": ["Camouflage puis Ambush ; Mutilate pour construire les points de combo.", "Eviscerate ou Slice and Dice à 5 points ; Instant Poison sur les deux armes."],
        "en": ["Stealth then Ambush; Mutilate to build combo points.", "Eviscerate or Slice and Dice at 5 points; Instant Poison on both weapons."]},
    "rogue/subtlety": {
        "fr": ["Hemorrhage comme générateur de points de combo en permanence (pas besoin d'être derrière la cible) ; Ambush depuis le camouflage.", "Eviscerate ou Slice and Dice à 5 points ; Rupture sur les cibles qui vivent toute la durée, meilleur que Slice and Dice au niveau 30."],
        "en": ["Hemorrhage as the combo builder at all times (no need to be behind the target); Ambush from stealth.", "Eviscerate or Slice and Dice at 5 points; Rupture on targets that live the full duration, better than Slice and Dice at level 30."]},
    "mage/fire": {
        "fr": ["Ouvrir par Pyroblast, Fireball comme sort de base (Frostfire Bolt le remplace à partir du niveau 40), Fire Blast pour finir.", "Zone : Flamestrike, Blast Wave, Arcane Explosion."],
        "en": ["Open with Pyroblast, Fireball as the filler (Frostfire Bolt replaces it from level 40), Fire Blast to finish.", "Area: Flamestrike, Blast Wave, Arcane Explosion."]},
    "mage/frost": {
        "fr": ["Frostbolt en continu ; annuler l'incantation pour un Ice Lance quand Fingers of Frost se déclenche.", "Mettre un Ice Lance en file après Frostbite, et continuer tant que la cible est gelée."],
        "en": ["Frostbolt continuously; cancel the cast for an Ice Lance when Fingers of Frost procs.", "Queue an Ice Lance after Frostbite, and keep casting it while the target is frozen."]},
    "mage/arcane": {
        "fr": ["Arcane Blast comme sort principal : 1 à 2 lancers au début de chaque combat, Arcane Missiles quand Missile Barrage se déclenche.", "Vider les charges avec Fire Blast après 2 à 3 Arcane Blast ; Arcane Explosion contre 3 ennemis ou plus."],
        "en": ["Arcane Blast as the main filler: 1-2 casts at the start of each fight, Arcane Missiles on a Missile Barrage proc.", "Dump the stacks with Fire Blast after 2-3 Arcane Blasts; Arcane Explosion against 3+ enemies."]},
    "warlock/affliction": {
        "fr": ["Démon envoyé en premier, une malédiction (Recklessness ou Elements) sur les boss.", "Immolate (lancé avant le combat), Bane of Agony si la cible vit assez longtemps, Siphon Life (cible de 20 s ou plus), Corruption (instantanée), Drain Life quand vous êtes blessé.", "Shadow Bolt quand Nightfall le rend instantané, baguette pour finir, Life Tap pour la mana."],
        "en": ["Send the demon in first, a curse (Recklessness or Elements) on bosses.", "Immolate (pre-cast), Bane of Agony if the target lives long enough, Siphon Life (20 s or more), Corruption (instant), Drain Life when hurt.", "Shadow Bolt when Nightfall makes it instant, wand to finish, Life Tap for mana."]},
    "warlock/destruction": {
        "fr": ["Démon envoyé en premier, malédiction sur les boss ; un Shadow Bolt avant le combat puis Immolate (les deux arrivent ensemble).", "Immolate est le seul effet sur la durée à gérer ; Shadow Bolt comme sort de base (Searing Pain pour un lancer plus rapide).", "Conflagrate vers la fin d'Immolate, Shadowburn pour finir, Life Tap pour la mana."],
        "en": ["Send the demon in first, a curse on bosses; pre-cast one Shadow Bolt then Immolate (the two land together).", "Immolate is the only damage-over-time to manage; Shadow Bolt as the filler (Searing Pain for a faster cast).", "Conflagrate near the end of Immolate, Shadowburn to finish, Life Tap for mana."]},
    "warlock/demonology": {
        "fr": ["Le démon attaque en permanence (Demonic Energies le soigne), Soul Link actif.", "Immolate, Bane of Agony, Corruption ; Drain Life (qui soigne aussi le démon), baguette pour finir."],
        "en": ["The demon attacks throughout (Demonic Energies heals it), Soul Link active.", "Immolate, Bane of Agony, Corruption; Drain Life (it heals the demon too), wand to finish."]},
    "hunter/beast-mastery": {
        "fr": ["Hunter's Mark et Serpent Sting avant tout, familier envoyé en premier ; Summon Hawk dès qu'il est prêt pour garder 2 faucons.", "Aimed Shot dès qu'il est prêt, Auto Shot entre deux ; Arcane Shot si la mana est pleine ; Multi-Shot à la place d'Aimed Shot contre plusieurs ennemis."],
        "en": ["Hunter's Mark and Serpent Sting first, pet sent in first; Summon Hawk on cooldown to keep 2 hawks out.", "Aimed Shot on cooldown, Auto Shot in between; Arcane Shot if mana is capped; Multi-Shot instead of Aimed Shot against several enemies."]},
    "hunter/marksmanship": {
        "fr": ["Hunter's Mark et Serpent Sting avant tout, familier envoyé en premier.", "Aimed Shot dès qu'il est prêt, Auto Shot entre deux ; Arcane Shot si la mana est pleine."],
        "en": ["Hunter's Mark and Serpent Sting first, pet sent in first.", "Aimed Shot on cooldown, Auto Shot in between; Arcane Shot if mana is capped."]},
    "hunter/survival": {
        "fr": ["À distance : Hunter's Mark, Serpent Sting, Aimed Shot dès qu'il est prêt, Auto Shot, Arcane Shot en surplus de mana.", "Au corps à corps : Serpent Sting, Raptor Strike dès qu'il est prêt, Mongoose Bite dès qu'il est disponible, Strider Kick dès qu'il est prêt. Au niveau 30, le corps à corps commence à dépasser la distance sur une cible pour un build Survie complet."],
        "en": ["Ranged: Hunter's Mark, Serpent Sting, Aimed Shot on cooldown, Auto Shot, Arcane Shot with spare mana.", "Melee: Serpent Sting, Raptor Strike on cooldown, Mongoose Bite whenever available, Strider Kick on cooldown. At level 30, melee starts to pass ranged on one target for a full Survival build."]},
    "priest/shadow": {
        "fr": ["Power Word: Shield et Inner Fire, Mind Blast pour engager, puis Devouring Plague, Shadow Word: Pain et Mind Flay (attention à la mana).", "Finir à la baguette pour économiser la mana ; Smite à la place de Mind Flay avant de l'apprendre."],
        "en": ["Power Word: Shield and Inner Fire, Mind Blast to pull, then Devouring Plague, Shadow Word: Pain and Mind Flay (watch your mana).", "Finish with the wand to save mana; Smite instead of Mind Flay before it is learned."]},
    "shaman/elemental": {
        "fr": ["Poser tous les totems avant le combat, Searing Totem en dernier (durée plus courte).", "Lightning Bolt pour engager, Flame Shock puis le rafraîchir, Lightning Bolt jusqu'à la mort de la cible.", "Fire Nova à chaque fois qu'il est prêt, seulement contre 3 ennemis ou plus."],
        "en": ["Put every totem down before the pull, Searing Totem last (shorter duration).", "Lightning Bolt to pull, Flame Shock then refresh it, Lightning Bolt until the target dies.", "Fire Nova on cooldown, only against 3 or more enemies."]},
    "shaman/enhancement": {
        "fr": ["Windfury Weapon en permanence, Mana Spring Totem pour la mana.", "Stormstrike dès qu'il est prêt, puis Earth Shock (Flame Shock en alternance en groupe, Frost Shock si la menace pose problème).", "Fire Nova avec un totem de feu actif si la mana le permet ; Maelstrom Weapon demande ses 5 points pour s'intégrer à la rotation."],
        "en": ["Windfury Weapon at all times, Mana Spring Totem for mana.", "Stormstrike on cooldown, then Earth Shock (Flame Shock alternating in groups, Frost Shock if threat is a problem).", "Fire Nova with an active Fire Totem if mana allows; Maelstrom Weapon needs all 5 points to fit the rotation."]},
    "druid/balance": {
        "fr": ["Moonfire toujours actif, puis Wrath ; Insect Swarm après Moonfire à partir du niveau 25.", "Hurricane (zone) n'est pas disponible dans la bêta."],
        "en": ["Keep Moonfire up, then Wrath; Insect Swarm after Moonfire from level 25.", "Hurricane (area) is not available in the beta."]},
    "druid/feral-combat": {
        "fr": ["Chat : Shred pour construire les points de combo (Claw si vous ne pouvez pas être derrière), Rip quand la cible vit assez longtemps, Shifting Power dès qu'il est prêt ; Rake est secondaire.", "Ours : Primal Bite est la dépense de rage principale, Swipe contre plusieurs ennemis, Maul pour brûler l'excès de rage ; Enrage dès qu'il est prêt."],
        "en": ["Cat: Shred to build combo points (Claw if you cannot get behind), Rip when the target lives long enough, Shifting Power on cooldown; Rake is secondary.", "Bear: Primal Bite is the main rage spender, Swipe against several enemies, Maul to burn extra rage; Enrage on cooldown."]},
    "paladin/retribution": {
        "fr": ["Toujours un Sceau actif : Seal of Righteousness avec beaucoup de puissance des sorts et une arme rapide, Seal of Command avec une arme lente.", "Judgement et Holy Strike dès qu'ils sont prêts ; Seal of the Crusader avant un Judgement si la cible vit longtemps ; Holy Shock en priorité pour le « Shockadin » ; Exorcism seulement contre les morts-vivants et les démons."],
        "en": ["Always keep a Seal up: Seal of Righteousness with lots of spell power and a fast weapon, Seal of Command with a slow weapon.", "Judgement and Holy Strike on cooldown; Seal of the Crusader before a Judgement if the target lives long; Holy Shock on cooldown for the Shockadin build; Exorcism only against undead and demons."]},
    "paladin/protection": {
        "fr": ["Righteous Fury en permanence ; Seal of Fury actif (il permet aussi à Judgement de provoquer).", "Consecration tant que la mana le permet (menace de zone), Judgement pour la menace, Holy Strike dès qu'il est prêt ; Exorcism seulement contre les morts-vivants et les démons."],
        "en": ["Righteous Fury at all times; Seal of Fury up (it also lets Judgement taunt).", "Consecration as long as mana allows (area threat), Judgement for threat, Holy Strike on cooldown; Exorcism only against undead and demons."]},
}

# Our verdict: what both agree on, what the level-60 simulation changed, where they differ
VERDICT = {
    "warrior/fury": {
        "fr": "Sur un boss de niveau 60, ce sont Bloodthirst, Whirlwind, Heroic Strike et Execute (sous 20 % de vie) qui font les dégâts. Victory Rush (après une mort) et Demoralizing Shout ne servent pas contre un boss. Rend ne rapporte que pour les Armes avec Bloodthrill (mesuré).",
        "en": "Against a level-60 boss, Bloodthirst, Whirlwind, Heroic Strike and Execute (under 20% health) do the damage. Victory Rush (after a kill) and Demoralizing Shout do not apply to a boss. Rend only pays off for Arms with Bloodthrill (measured)."},
    "warrior/arms": {
        "fr": "D'accord : Rend pour nourrir Bloodthrill, Overpower, Slam après le coup (testés : Rend + Bloodthrill ajoutent 34 DPS, Rend seul fait perdre du DPS). Différent contre un boss : Execute est utile au niveau 60 sous 20 % de vie, et Spearing Strike (40 % des dégâts d'arme) reste de côté.",
        "en": "Agreed: Rend to feed Bloodthrill, Overpower, Slam after the swing (tested: Rend + Bloodthrill add 34 DPS, Rend alone loses DPS). Different against a boss: Execute is worth it at level 60 under 20% health, and Spearing Strike (40% weapon damage) stays out."},
    "warrior/protection": {
        "fr": "D'accord : Heroic Strike comme dépense de rage. Le simulateur le lance avant Sunder Armor, ce qui donne +13 % de menace par seconde par rapport à l'ordre inverse (mesuré), puis Shield Slam et Revenge sur leurs conditions.",
        "en": "Agreed: Heroic Strike as the rage dump. The simulator casts it before Sunder Armor, which gives +13% threat per second over the reverse order (measured), then Shield Slam and Revenge on their conditions."},
    "rogue/combat": {
        "fr": "D'accord : Sinister Strike, Slice and Dice, Eviscerate à 5 points. Le simulateur ajoute Adrenaline Rush et Blade Flurry dès qu'ils sont prêts. Poisons : Instant en main droite et Deadly en main gauche, valeurs de Classic (hypothèse).",
        "en": "Agreed: Sinister Strike, Slice and Dice, Eviscerate at 5 points. The simulator adds Adrenaline Rush and Blade Flurry on cooldown. Poisons: Instant on the main hand and Deadly on the off hand, Classic values (assumed)."},
    "rogue/assassination": {
        "fr": "D'accord : Mutilate (avec deux dagues), Slice and Dice, Eviscerate à 5 points. Les dagues sont rares dans le butin connu : l'optimiseur retient souvent une épée et une dague, et le simulateur joue alors Sinister Strike.",
        "en": "Agreed: Mutilate (with two daggers), Slice and Dice, Eviscerate at 5 points. Daggers are scarce in the known loot: the optimizer often keeps a sword and a dagger, and the simulator then plays Sinister Strike."},
    "rogue/subtlety": {
        "fr": "D'accord : Hemorrhage en permanence, Slice and Dice, Eviscerate. Rupture n'est pas encore simulée (ses chiffres dans le client sont faibles : 35 de base, +4,7 par point de combo, toutes les 2 secondes) : à confirmer en jeu.",
        "en": "Agreed: Hemorrhage at all times, Slice and Dice, Eviscerate. Rupture is not simulated yet (its client numbers are small: 35 base, +4.7 per combo point, every 2 seconds): to confirm in game."},
    "mage/fire": {
        "fr": "D'accord : Pyroblast (avec Heating Up), Fire Blast, Frostfire Bolt comme sort de base (il remplace bien Fireball), plus Scorch pour Improved Scorch et Combustion. Les sorts de zone ne comptent pas contre une seule cible.",
        "en": "Agreed: Pyroblast (with Heating Up), Fire Blast, Frostfire Bolt as the filler (it does replace Fireball), plus Scorch for Improved Scorch and Combustion. Area spells do not count against one target."},
    "mage/frost": {
        "fr": "D'accord : Frostbolt en continu et Ice Lance sur cible gelée. Frost Nova est un outil de contrôle, pas simulé.",
        "en": "Agreed: Frostbolt continuously and Ice Lance on a frozen target. Frost Nova is a control tool, not simulated."},
    "mage/arcane": {
        "fr": "Différent, et mesuré : sur un combat de boss de 3 minutes, les charges d'Arcane Blast coûtent trop de mana (+175 % par charge). Une rotation Arcane Blast puis Missiles tombe à 308 DPS, contre 452 pour Arcane Missiles + Arcane Power. Le conseil d'Icy Veins vaut pour la montée en niveau (combats courts, boisson libre). Les déclenchements de Missile Barrage ne sont pas simulés.",
        "en": "Different, and measured: over a 3-minute boss fight Arcane Blast stacks cost too much mana (+175% per stack). A rotation of Arcane Blast then Missiles drops to 308 DPS, against 452 for Arcane Missiles + Arcane Power. Icy Veins' advice fits leveling (short fights, free drinking). Missile Barrage procs are not simulated."},
    "warlock/affliction": {
        "fr": "D'accord, et adopté après mesure : Bane of Agony plutôt que Bane of Doom (+16 DPS sur un combat de 3 minutes) et Immolate dans la rotation (+3 DPS). Wrack est propre à Forever. Les malédictions de raid (Elements, Recklessness) sont comptées comme debuffs.",
        "en": "Agreed, and adopted after measuring: Bane of Agony instead of Bane of Doom (+16 DPS over a 3-minute fight) and Immolate in the rotation (+3 DPS). Wrack is Forever-specific. Raid curses (Elements, Recklessness) are counted as debuffs."},
    "warlock/destruction": {
        "fr": "D'accord : Immolate en premier, Conflagrate et Shadowburn dès qu'ils sont prêts, Incinerate comme sort de base au niveau 60. Ajouté après mesure : Bane of Agony (+6 DPS par rapport à Doom). Searing Pain donne beaucoup de menace pour peu de dégâts.",
        "en": "Agreed: Immolate first, Conflagrate and Shadowburn on cooldown, Incinerate as the filler at level 60. Added after measuring: Bane of Agony (+6 DPS over Doom). Searing Pain gives a lot of threat for little damage."},
    "warlock/demonology": {
        "fr": "D'accord : le diablotin reste en jeu avec Demonic Knowledge et Unholy Power (le sacrifier fait perdre environ 80 DPS dans le simulateur), Immolate, Corruption et Bane of Agony (+12 DPS par rapport à Doom, mesuré).",
        "en": "Agreed: the Imp stays out with Demonic Knowledge and Unholy Power (sacrificing it loses about 80 DPS in the simulator), Immolate, Corruption and Bane of Agony (+12 DPS over Doom, measured)."},
    "hunter/beast-mastery": {
        "fr": "D'accord, et ajouté : Hunter's Mark (+110 de puissance d'attaque à distance, valeur du client), Serpent Sting, Summon Hawk, les attaques du familier, Arcane Shot. Différent : au niveau 60 sur une cible, Multi-Shot fait environ 4 % de mieux qu'Aimed Shot (qui coûte une incantation de 2 s), donc le simulateur tire Multi-Shot.",
        "en": "Agreed, and added: Hunter's Mark (+110 ranged attack power, client value), Serpent Sting, Summon Hawk, the pet's attacks, Arcane Shot. Different: at level 60 on one target Multi-Shot does about 4% better than Aimed Shot (which costs a 2-second cast), so the simulator fires Multi-Shot."},
    "hunter/marksmanship": {
        "fr": "D'accord, et ajouté : Hunter's Mark (+110 de puissance d'attaque à distance, valeur du client), Serpent Sting, Arcane Shot. Différent : au niveau 60 sur une cible, Multi-Shot et Sniper Shot font environ 4 % de mieux qu'Aimed Shot (incantation de 2 s) dans le simulateur.",
        "en": "Agreed, and added: Hunter's Mark (+110 ranged attack power, client value), Serpent Sting, Arcane Shot. Different: at level 60 on one target Multi-Shot and Sniper Shot do about 4% better than Aimed Shot (2-second cast) in the simulator."},
    "hunter/survival": {
        "fr": "D'accord sur les deux variantes (Hunter's Mark ajouté à la version à distance). Différent : Icy Veins voit le corps à corps dépasser la distance au niveau 30 ; avec l'équipement connu au niveau 60, le simulateur garde la distance devant (environ 493 DPS contre 422), et Multi-Shot y fait 6 % de mieux qu'Aimed Shot.",
        "en": "Agreed on both variants (Hunter's Mark added to the ranged one). Different: Icy Veins sees melee passing ranged at level 30; with the known level-60 gear the simulator keeps ranged ahead (about 493 DPS against 422), and Multi-Shot does 6% better than Aimed Shot there."},
    "priest/shadow": {
        "fr": "D'accord : Mind Blast, Devouring Plague, Shadow Word: Pain, Mind Flay comme sort de base, plus Shadow Word: Death. Finir à la baguette est une habitude de montée en niveau, pas une partie de la rotation contre un boss.",
        "en": "Agreed: Mind Blast, Devouring Plague, Shadow Word: Pain, Mind Flay as the filler, plus Shadow Word: Death. Finishing with the wand is a leveling habit, not part of the rotation against a boss."},
    "shaman/elemental": {
        "fr": "D'accord : Searing Totem en ouverture, Flame Shock entretenu, Lightning Bolt comme sort de base. Le simulateur ajoute Lava Burst (+20 % sous Flame Shock) et Lightning Overload. Fire Nova et Chain Lightning sont des outils de zone : sur une cible, ils coûtent plus de mana qu'ils ne rapportent (mesuré).",
        "en": "Agreed: Searing Totem at the start, Flame Shock kept up, Lightning Bolt as the filler. The simulator adds Lava Burst (+20% under Flame Shock) and Lightning Overload. Fire Nova and Chain Lightning are area tools: on one target they cost more mana than they return (measured)."},
    "shaman/enhancement": {
        "fr": "D'accord : Windfury Weapon, Mana Spring Totem, Stormstrike dès qu'il est prêt, les chocs dans leur créneau, Maelstrom Weapon à 5 rangs. Corrigé après mesure : le +20 % de Stormstrike vaut plus sur un Lightning Bolt que sur Earth Shock (+12 DPS) ; Frost Shock fait comme Earth Shock ; Fire Nova ne rapporte rien sur une cible (outil de zone).",
        "en": "Agreed: Windfury Weapon, Mana Spring Totem, Stormstrike on cooldown, the shocks in their slot, Maelstrom Weapon at 5 ranks. Corrected after measuring: Stormstrike's +20% is worth more on a Lightning Bolt than on Earth Shock (+12 DPS); Frost Shock does the same as Earth Shock; Fire Nova adds nothing on one target (area tool)."},
    "druid/balance": {
        "fr": "D'accord sur Moonfire et Insect Swarm. Au niveau 60, le simulateur lance surtout Starfire (environ 210 DPS contre 56 pour Wrath, voir la page du classement), avec Wrath en complément.",
        "en": "Agreed on Moonfire and Insect Swarm. At level 60 the simulator mostly casts Starfire (about 210 DPS against 56 for Wrath, see the ranking page), with Wrath as a complement."},
    "druid/feral-combat": {
        "fr": "D'accord sur les deux formes. Ajouté après mesure : Primal Bite dans la rotation de l'ours (+9 % de menace par seconde, sans compter sa « haute menace » que le client ne chiffre pas). Chat : le simulateur entretient aussi Savage Roar et utilise Tiger's Fury et Berserk.",
        "en": "Agreed on both forms. Added after measuring: Primal Bite in the bear rotation (+9% threat per second, not counting its \"high threat\", which the client does not quantify). Cat: the simulator also keeps Savage Roar up and uses Tiger's Fury and Berserk."},
    "paladin/retribution": {
        "fr": "D'accord : Seal of Command (arme à deux mains), Judgement et Holy Strike dès qu'ils sont prêts. Exorcism reste de côté contre un boss (morts-vivants et démons seulement). Pas simulés : le changement de Sceau pour Seal of the Crusader et le bonus de Hammer of Justice.",
        "en": "Agreed: Seal of Command (two-hand weapon), Judgement and Holy Strike on cooldown. Exorcism stays out against a boss (undead and demons only). Not simulated: the Seal of the Crusader swap and the Hammer of Justice bonus."},
    "paladin/protection": {
        "fr": "D'accord : Righteous Fury, Judgement, Holy Strike, plus Holy Shield dans le simulateur. Différent : Consecration est un outil de zone ; sur un boss, ses dégâts dans le client sont faibles (16 sur 8 s à son premier rang) pour 565 de mana, donc il reste de côté. Les chiffres de Seal of Fury ne sont pas encore dans nos données.",
        "en": "Agreed: Righteous Fury, Judgement, Holy Strike, plus Holy Shield in the simulator. Different: Consecration is an area tool; on a boss its damage in the client is small (16 over 8 s at its first rank) for 565 mana, so it stays out. Seal of Fury's numbers are not in our data yet."},
}

# Healing specs: not simulated, so the list shown is Icy Veins' healing rotation (paraphrased) and the verdict says so
HEALER_MAIN = {
    "shaman/restoration": {
        "fr": ["Poser tous les totems avant le combat, Searing Totem en dernier.", "Healing Wave sur les blessés, en rang réduit quand les dégâts ne justifient pas le rang maximum.", "Fire Nova contre un groupe, ou Lightning Bolt sur une cible, quand aucun soin n'est urgent.", "Garder les totems de bonus en place : c'est votre meilleure contribution aux dégâts du groupe."],
        "en": ["Put every totem down before the pull, Searing Totem last.", "Healing Wave on injured targets, downranked when the damage does not justify the top rank.", "Fire Nova against a group, or Lightning Bolt on one target, when no heal is urgent.", "Keep the buff totems up: it is your best contribution to the party's damage."]},
    "druid/restoration": {
        "fr": ["Rejuvenation sur le tank et sur ceux qui subissent peu de dégâts, Healing Touch pour compléter.", "Swiftmend une seconde après un Rejuvenation quand une cible tombe bas.", "Thorns sur le tank avant le début ; Wrath ou Moonfire sur les ennemis quand il reste du temps."],
        "en": ["Rejuvenation on the tank and anyone taking light damage, Healing Touch to top up.", "Swiftmend one second after a Rejuvenation when a target drops low.", "Thorns on the tank before the run; Wrath or Moonfire on enemies when you have spare time."]},
    "paladin/holy": {
        "fr": ["Flash of Light comme soin principal (peu cher, rapide).", "Holy Light pour les gros soins quand la mana le permet ; Holy Shock instantané en urgence ; Lay on Hands en dernier recours.", "Blessing of Might sur le groupe et Devotion ou Retribution Aura en permanence ; Seal of Light pour soigner davantage."],
        "en": ["Flash of Light as the main heal (cheap, fast).", "Holy Light for big heals when mana allows; instant Holy Shock in emergencies; Lay on Hands as a last resort.", "Blessing of Might on the party and Devotion or Retribution Aura at all times; Seal of Light for extra healing."]},
    "priest/holy": {
        "fr": ["Power Word: Shield pour gagner du temps ; Heal pour un soin moyen ; Renew contre les dégâts légers.", "Flash Heal seulement en urgence (coûteux) ; Prayer of Healing quand le groupe est blessé.", "Holy Nova quand Searing Light se déclenche et que personne n'est en danger ; dissiper quand ça vaut la mana."],
        "en": ["Power Word: Shield to buy time; Heal for a moderate heal; Renew against chip damage.", "Flash Heal only in emergencies (costly); Prayer of Healing when the party is hurt.", "Holy Nova when Searing Light procs and nobody is in danger; cleanse when it is worth the mana."]},
    "priest/discipline": {
        "fr": ["Power Word: Shield au besoin ou pour gagner du temps ; Heal pour un soin moyen ; Renew contre les dégâts légers.", "Flash Heal seulement en urgence (coûteux) ; Prayer of Healing quand le groupe est blessé ; dissiper quand ça vaut la mana."],
        "en": ["Power Word: Shield as needed or to buy time; Heal for a moderate heal; Renew against chip damage.", "Flash Heal only in emergencies (costly); Prayer of Healing when the party is hurt; cleanse when it is worth the mana."]},
}
HEALER_NOTE = {
    "fr": "Les soins ne sont pas simulés : cette liste est celle d'Icy Veins (niveau 30), reformulée. Elle n'est pas validée par des mesures. Le build niveau 60 plus haut est lui aussi composé à la main.",
    "en": "Healing is not simulated: this list is Icy Veins' (level 30), reworded. It is not validated by measurements. The level-60 build above is also put together by hand.",
}

TX = {
    "fr": {"h2": "Rotation niveau 60", "intro_sim": "Priorité de notre simulateur au niveau 60, comparée à ce que recommande Icy Veins. Leurs guides sont écrits pour la bêta niveau 30 et pour la montée en niveau : nous gardons ce sur quoi tout le monde s'accorde, nous adoptons ce que la simulation a confirmé au niveau 60 et nous disons où les deux diffèrent.",
           "intro_heal": "Les soins ne sont pas encore simulés : voici la rotation de soins recommandée par Icy Veins (niveau 30), reformulée.",
           "iv_h3": "Ce que recommande Icy Veins (niveau 30)", "verdict_h3": "Notre comparaison", "src_iv": "Icy Veins : guide de la spécialisation, bêta niveau 30 (reformulé)"},
    "en": {"h2": "Level 60 rotation", "intro_sim": "Our simulator's priority at level 60, set against what Icy Veins recommends. Their guides are written for the level-30 beta and for leveling: we keep what everyone agrees on, adopt what the simulation confirmed at level 60 and say where the two differ.",
           "intro_heal": "Healing is not simulated yet: this is the healing rotation Icy Veins recommends (level 30), reworded.",
           "iv_h3": "What Icy Veins recommends (level 30)", "verdict_h3": "Our comparison", "src_iv": "Icy Veins: the specialization's guide, level-30 beta (reworded)"},
}

# Level-60 gear and stat-weight sections of the guides (data: data/wow_ranking60.json, written by sim60/ranking.mjs)
G60 = {
    "fr": {
        "gear_h2": "Équipement niveau 60", "gear_p": "L'équipement que notre optimiseur retient pour cette spécialisation parmi les objets connus de la bêta (donjons et les rares objets de raid déjà connus), avec les effets d'objets simulés. Aucun objet n'est choisi à la main : c'est le résultat du calcul du classement, et il changera quand de nouveaux objets seront découverts.",
        "gear_heal": "L'équipement de soin niveau 60 n'est pas encore calculé : le simulateur ne gère pas les soins. Les pages des donjons et des raids permettent de parcourir le butin par type d'objet et par statistique.",
        "col_slot": "Emplacement", "col_item": "Objet", "col_source": "Provenance",
        "w_h2": "Priorité de statistiques niveau 60", "w_p": "Mesurée par le simulateur sur le personnage ci-dessus : le DPS gagné par un point supplémentaire de chaque statistique, avec les mêmes tirages aléatoires de chaque côté. La valeur relative compare chaque statistique à un point de {main}. Critique, toucher et hâte sont comptés par point de score, comme la Force ou l'Agilité, pour être comparables ; ils tiennent compte des plafonds : un toucher au plafond ne rapporte plus rien. Une valeur proche de zéro ou négative est dans la marge d'erreur ou liée à une limite (mana, plafond).",
        "w_main_ap": "puissance d'attaque", "w_main_sp": "puissance des sorts", "w_stat": "Statistique", "w_per": "DPS gagné", "w_rel": "Valeur relative", "w_unit_pt": "par point", "w_unit_pct": "par 1 %", "w_unit_rating": "par point de score", "iv_stats_h3": "Icy Veins (niveau 30)", "w_none": "aucun effet",
        "stats": {"atkpwr": "Puissance d'attaque", "splpwr": "Puissance des sorts", "str": "Force", "agi": "Agilité", "int": "Intelligence", "spi": "Esprit", "critstrkrtng": "Critique", "hitrtng": "Toucher", "hastertng": "Hâte"},
        "note": "Les données de talents viennent du client bêta. Le build, l'équipement, les statistiques et la rotation niveau 60 viennent de notre simulateur et sont validés par des mesures de DPS ; la rotation est comparée à celle des guides Icy Veins, écrits pour la bêta niveau 30. Les soins ne sont pas simulés. Ces données évolueront avec la bêta et avec la sortie du jeu le 4 novembre 2026.",
        "w_tank": "Pour un tank, le simulateur ne chiffre pas encore les statistiques : la liste d'Icy Veins (niveau 30) ci-dessous reste la référence.",
    },
    "en": {
        "gear_h2": "Level 60 gear", "gear_p": "The gear our optimizer picks for this specialization among the items known from the beta (dungeons and the few raid items already known), with item effects simulated. Nothing is hand-picked: it is the result of the ranking's computation, and it will change as new items are discovered.",
        "gear_heal": "Level-60 healing gear is not computed yet: the simulator does not model healing. The dungeon and raid pages let you browse loot by item type and stat.",
        "col_slot": "Slot", "col_item": "Item", "col_source": "Source",
        "w_h2": "Level 60 stat priority", "w_p": "Measured by the simulator on the character above: the DPS gained by one more point of each stat, with the same random draws on both sides. The relative value compares each stat with one point of {main}. Crit, hit and haste are counted per rating point, like Strength or Agility, so they compare directly; they respect the caps: hit at the cap adds nothing. A value near zero or negative is within the margin of error or tied to a limit (mana, cap).",
        "w_main_ap": "attack power", "w_main_sp": "spell power", "w_stat": "Stat", "w_per": "DPS gained", "w_rel": "Relative value", "w_unit_pt": "per point", "w_unit_pct": "per 1%", "w_unit_rating": "per rating point", "iv_stats_h3": "Icy Veins (level 30)", "w_none": "no effect",
        "stats": {"atkpwr": "Attack power", "splpwr": "Spell power", "str": "Strength", "agi": "Agility", "int": "Intellect", "spi": "Spirit", "critstrkrtng": "Crit", "hitrtng": "Hit", "hastertng": "Haste"},
        "note": "Talent data comes from the beta client. The level-60 build, gear, stats and rotation come from our simulator and are validated by DPS measurements; the rotation is compared with the Icy Veins guides, written for the level-30 beta. Healing is not simulated. This data will change with the beta and with the game's launch on November 4, 2026.",
        "w_tank": "For a tank the simulator does not weigh stats yet: Icy Veins' list (level 30) below remains the reference.",
    },
}
