"""English guides, batch 13 (Aurora includes the extras: strengths / weaknesses / teamfight, and its 4th combo)."""

EN = {
    "Morgana": {
        "playstyle": (
            "Morgana is a control mage-support: Dark Binding roots, Tormented Shadow damages over time with damage that increases with the target's missing health, Black Shield protects an ally from magic damage and crowd control, and Soul Shackles stuns those who do not break them. "
            "Her passive heals her when she damages champions, large minions and monsters."
        ),
        "laning": (
            "Dark Binding is your main tool: every hit decides the trade. "
            "Keep Black Shield for an ally threatened by a control or magic damage."
        ),
        "combos": [
            {"name": "The pick", "when": "An enemy is within binding range.",
             "how": "Dark Binding roots and deals damage; place Tormented Shadow on them: its damage increases with their missing health."},
            {"name": "Protection", "when": "An ally is about to take a crowd control effect.",
             "how": "Black Shield absorbs magic damage and crowd control until it breaks: place it before the enemy's engage."},
            {"name": "The team ultimate", "when": "Enemies are grouped around you.",
             "how": "Soul Shackles slow and damage nearby enemy champions; after a delay, those who have not broken the chains are stunned."},
        ],
        "mistakes": [
            "Using Black Shield on an ally who is not the target of crowd control.",
            "Casting the ultimate without being close to the enemies.",
            "Missing Dark Binding because of a minion.",
        ],
    },
    "Brand": {
        "playstyle": (
            "Brand is a flame burst mage: his abilities set targets ablaze (3 stacks), and at max the Blaze explodes after 2 seconds. "
            "Sear stuns a burning target, Pillar of Flame deals 25% more damage to burning targets, Conflagration doubles its spread range, and Pyroclasm bounces up to 5 times."
        ),
        "laning": (
            "Ignite first, then stun with Sear. "
            "Your passive restores your mana if you kill a burning enemy."
        ),
        "combos": [
            {"name": "The stun", "when": "An enemy is within range.",
             "how": "Conflagration ignites the target, Sear stuns them since they are burning, Pillar of Flame deals 25% bonus damage."},
            {"name": "The full burst", "when": "A carry is within range.",
             "how": "Pillar of Flame then Conflagration and Sear; Pyroclasm bounces in priority onto affected champions that have not reached the max stacks and slows them."},
            {"name": "The Blaze explosion", "when": "A champion is approaching max stacks.",
             "how": "At max stacks on a champion, the Blaze becomes unstable and explodes after 2 seconds, dealing huge damage around the victim."},
        ],
        "mistakes": [
            "Casting Sear with no burning target: you lose the stun.",
            "Forgetting Conflagration's doubled range on a burning target.",
            "Casting the ultimate without several targets to bounce onto.",
        ],
    },
    "Mordekaiser": {
        "playstyle": (
            "Mordekaiser is a fighter-mage who plays with his shield: Indestructible stores part of the damage dealt and taken as a shield, which can be consumed to heal. "
            "His passive gives a damage aura after 3 attacks or abilities, Death's Grasp pulls enemies in, and Realm of Death drags him into a duel with his victim while stealing part of their stats."
        ),
        "laning": (
            "Obliterate deals more damage if only one enemy is hit: aim at a lone champion. "
            "Chain 3 attacks or abilities to trigger your passive's aura."
        ),
        "combos": [
            {"name": "The trade", "when": "An enemy is alone within range.",
             "how": "Obliterate deals more damage on a single target, Indestructible converts damage into a shield, the third attack or ability triggers the aura."},
            {"name": "The pull", "when": "Several enemies are scattered.",
             "how": "Death's Grasp pulls every enemy in an area toward you; follow with Obliterate."},
            {"name": "The duel", "when": "A carry is identified.",
             "how": "Realm of Death drags you and your victim into another dimension and steals part of their stats; if you kill them, you keep those stats until they respawn."},
        ],
        "mistakes": [
            "Casting the ultimate on a target who can beat you in a duel.",
            "Using Obliterate when several enemies are hit without need.",
            "Not consuming your shield to heal.",
        ],
    },
    "Warwick": {
        "playstyle": (
            "Warwick is a hunting jungler: his attacks deal bonus magic damage, and below 50% health they heal him (tripled below 25%). "
            "Blood Hunt gives him speed against enemies below 50% health, Jaws of the Beast bites based on max health, Primal Howl makes enemies flee, and Infinite Duress suppresses a champion."
        ),
        "laning": (
            "Jaws of the Beast deals damage based on the target's max health and heals you. "
            "Blood Hunt flags enemies below 50% health and gives you speed against them."
        ),
        "combos": [
            {"name": "The trade", "when": "An enemy is within range.",
             "how": "Jaws of the Beast leaps you onto the target while healing you, your attacks deal bonus magic damage, Primal Howl reduces the damage you take then makes enemies flee."},
            {"name": "The capture", "when": "A carry is isolated.",
             "how": "Infinite Duress leaps in a direction (farther with bonus speed) and suppresses the first champion hit for 1.5 seconds."},
            {"name": "The hunt", "when": "An enemy is below 50% health.",
             "how": "Blood Hunt gives you movement and attack speed bonuses against them, tripled below 25%."},
        ],
        "mistakes": [
            "Forgetting your passive at low health: it is your heal.",
            "Casting the ultimate without having adjusted your bonus movement speed.",
            "Using Primal Howl when you do not need to flee.",
        ],
    },
    "Aurora": {
        "playstyle": (
            "Aurora is a mage-assassin of the spirit realms: her passive exorcises the spirits of the enemies she damages, and they follow and heal her. "
            "Twofold Hex curses and is recast to pull the hexes, Across the Veil makes her invisible, The Weirding slows before a hop backward, and Between Worlds creates a teleportation zone."
        ),
        "laning": (
            "Twofold Hex: recast it to pull the active hexes and damage along the way. "
            "The Weirding makes you hop backward to safety."
        ),
        "strengths": [
            "Heals from the exorcised spirits of the enemies she damages.",
            "Across the Veil makes her invisible and speeds her up for a brief moment.",
            "Between Worlds damages and slows, then creates a zone where she can teleport from edge to edge.",
        ],
        "weaknesses": [
            "The Weirding hops her backward: her final position is less aggressive.",
            "Twofold Hex needs a recast to be fully effective.",
            "Lots of long cooldowns: her combos are spaced out.",
        ],
        "teamfight": (
            "Aurora plays at range, places Twofold Hex on several targets, then recasts to pull the hexes. "
            "Her ultimate creates a slowing zone in which she teleports freely: she repositions within the fight without ever overexposing herself."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within range.",
             "how": "Twofold Hex curses the target, The Weirding deals damage and slows then puts you to safety, recast Twofold Hex to pull the active hexes."},
            {"name": "The engage", "when": "A carry is isolated.",
             "how": "Across the Veil makes you leap, makes you invisible and speeds you up; Between Worlds releases a shockwave and creates a zone that slows."},
            {"name": "The teleportation zone", "when": "You want to reposition.",
             "how": "Between Worlds creates a zone that lets you teleport from edge to edge."},
            {"name": "The area combo", "when": "A group of enemies approaches.",
             "how": "Between Worlds releases a shockwave and creates a zone that slows; Twofold Hex curses the enemies, The Weirding slows then puts you to safety, recast Twofold Hex to pull the active hexes."},
        ],
        "mistakes": [
            "Forgetting Twofold Hex's recast.",
            "Using Across the Veil with no target.",
            "Ignoring the exorcised spirits: they heal you.",
        ],
    },
    "Samira": {
        "playstyle": (
            "Samira is a marksman who combines melee and ranged: her combos build by chaining attacks or abilities different from the previous one. "
            "Wild Rush dashes her through an enemy and resets on a kill, Blade Whirl destroys enemy projectiles, and Inferno Trigger fires a rain of bullets on all enemies around her."
        ),
        "laning": (
            "Chain different actions to build your combo. "
            "In melee, your attacks deal bonus magic damage."
        ),
        "combos": [
            {"name": "The engage", "when": "An enemy is within dash range.",
             "how": "Wild Rush dashes you through an enemy while slashing and gives you attack speed; Flair cast during the dash hits every enemy along your path."},
            {"name": "The melee ultimate", "when": "You are surrounded by enemies.",
             "how": "Inferno Trigger fires a rain of bullets on all the enemies around you."},
            {"name": "Defense", "when": "Enemy projectiles are incoming.",
             "how": "Blade Whirl damages nearby enemies and destroys enemy projectiles."},
        ],
        "mistakes": [
            "Repeating the same action: you lose your combo.",
            "Casting the ultimate without being in contact with the enemies.",
            "Using Wild Rush with no target to dash through.",
        ],
    },
    "Akshan": {
        "playstyle": (
            "Akshan is a mobile marksman: every third hit, he deals bonus damage and gains a shield on a champion. "
            "Avengerang throws a boomerang that gains range with each hit, Going Rogue camouflages him and revives his allies by killing a Scoundrel, and Heroic Swing swings him from terrain."
        ),
        "laning": (
            "Your attacks are doubled by a weaker extra attack: cancel it to gain movement speed. "
            "Avengerang gains range with each enemy hit."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within range.",
             "how": "Avengerang deals damage on the way out and back, its range increases with each hit; the third action triggers your passive's damage and shield."},
            {"name": "The ambush", "when": "A Scoundrel is spotted.",
             "how": "Going Rogue camouflages you and speeds you toward Scoundrels; Heroic Swing swings you and fires repeatedly at the nearest enemy."},
            {"name": "The precision ultimate", "when": "An enemy champion is visible.",
             "how": "Comeuppance locks onto a champion, stores bullets then fires them all; the damage depends on the missing health of the first champion, minion or structure hit."},
        ],
        "mistakes": [
            "Casting the ultimate without checking who will be hit first.",
            "Staying visible away from tall grass or terrain features while camouflaged.",
            "Forgetting the cancelable extra attack.",
        ],
    },
    "Briar": {
        "playstyle": (
            "Briar is a frenzied jungler: her attacks and abilities deal a stacking bleed that heals her, and she lacks natural regeneration but her healing increases when she is low on health. "
            "Head Rush stuns and breaks armor, Blood Frenzy makes her chase the nearest enemy, Chilling Scream frees her from the frenzy, and Certain Death flies her to her prey."
        ),
        "laning": (
            "Do not count on your regeneration: make trades that heal you through the bleed. "
            "Head Rush stuns and breaks armor."
        ),
        "combos": [
            {"name": "The engage", "when": "An enemy is within leap range.",
             "how": "Head Rush leaps onto a unit, stuns and breaks armor; Blood Frenzy gives speeds and area damage around the target; recast it for a Snack Attack."},
            {"name": "Leaving the frenzy", "when": "You need to regain control.",
             "how": "Chilling Scream frees you from Blood Frenzy, reduces the damage you take while charging and heals you; a fully charged scream knocks back and stuns against a wall."},
            {"name": "The prey ultimate", "when": "A carry is visible on the map.",
             "how": "Certain Death marks the first champion hit as your prey and flies you to them while terrifying nearby enemies; you gain armor, magic resistance, life steal and speed."},
        ],
        "mistakes": [
            "Staying in the frenzy with no control: you chase the nearest enemy.",
            "Forgetting Blood Frenzy's recast.",
            "Casting the ultimate on a prey who can flee.",
        ],
    },
    "Zac": {
        "playstyle": (
            "Zac is an elastic tank: every ability that hits makes him lose a bit of himself that he absorbs to heal, and on death he splits into 4 blobs that try to recombine. "
            "Stretching Strikes grabs and slams two targets, Unstable Matter damages based on max health, Elastic Slingshot launches him, and Let's Bounce! bounces four times while knocking up."
        ),
        "laning": (
            "Pick up your bits to heal. "
            "Stretching Strikes grabs an enemy then, if you attack another one, sends the two targets into each other."
        ),
        "combos": [
            {"name": "The engage", "when": "An enemy carry is within range.",
             "how": "Elastic Slingshot launches you forward, Stretching Strikes grabs, Unstable Matter deals damage based on max health, Let's Bounce! knocks up and slows."},
            {"name": "The trade", "when": "Two enemies are close to each other.",
             "how": "Stretching Strikes grabs an enemy then, if you attack another one, sends the two targets into each other."},
            {"name": "The second life", "when": "You take lethal damage.",
             "how": "Cell Division splits you into 4 blobs that try to recombine; if any remain, you come back to life. This ability has a 5-minute cooldown."},
        ],
        "mistakes": [
            "Leaving the bits on the ground: they are your healing.",
            "Forgetting that the second life is available every 5 minutes.",
            "Using Elastic Slingshot with no direction: it is a movement ability.",
        ],
    },
    "Kassadin": {
        "playstyle": (
            "Kassadin is an assassin-mage who takes less magic damage and passes through units. "
            "Null Sphere interrupts channels, Nether Blade empowers his attacks, Force Pulse uses the energy of spells cast near him, and Riftwalk teleports him: each use in quick succession increases cost and damage."
        ),
        "laning": (
            "Keep Null Sphere to interrupt a channel or gain a shield against magic. "
            "The active Nether Blade restores mana and deals heavy damage."
        ),
        "combos": [
            {"name": "The trade", "when": "An enemy is within range.",
             "how": "Null Sphere deals damage and protects you from magic, Nether Blade empowers your attack and restores mana, Force Pulse damages and slows in a cone after absorbing enough energy."},
            {"name": "The engage", "when": "A carry is far away.",
             "how": "Riftwalk teleports you while damaging nearby enemies; each use in a short period increases the mana cost and the damage of the next."},
            {"name": "Anti-magic", "when": "An enemy mage casts abilities around you.",
             "how": "Force Pulse draws energy from spells cast near you; your passive reduces the magic damage you take."},
        ],
        "mistakes": [
            "Chaining Riftwalks without mana.",
            "Using Force Pulse without enough energy.",
            "Engaging with no exit: your Riftwalks cost more and more.",
        ],
    },
    "Tryndamere": {
        "playstyle": (
            "Tryndamere is a Fury fighter: every attack, critical strike and killing blow gives him some, which raises his critical strike chance. "
            "Bloodlust consumes Fury to heal him, Mocking Shout reduces the attack damage of nearby enemies, Spinning Slash dashes him, and Undying Rage stops him from dying for its duration."
        ),
        "laning": (
            "Generate Fury by attacking, then use Bloodlust to heal. "
            "Mocking Shout reduces the attack damage of nearby champions and the movement of those with their back to you."
        ),
        "combos": [
            {"name": "The trade", "when": "An enemy is within range.",
             "how": "Spinning Slash dashes you and damages enemies on your path, your attacks generate Fury, Bloodlust heals you."},
            {"name": "Defense", "when": "You are fighting high-attack enemies.",
             "how": "Mocking Shout reduces the attack damage of nearby champions; those who flee are slowed."},
            {"name": "The survival ultimate", "when": "You are at low health.",
             "how": "Undying Rage stops you from dying whatever the wounds: keep fighting."},
        ],
        "mistakes": [
            "Casting Undying Rage too early: it has a limited duration.",
            "Consuming your Fury with no attacks to make.",
            "Forgetting Mocking Shout against high-attack enemies.",
        ],
    },
}
