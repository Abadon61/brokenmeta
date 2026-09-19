"""English guides, batch 7 (Gangplank includes the extras: strengths / weaknesses / teamfight, and its 4th combo)."""

EN = {
    "Olaf": {
        "playstyle": (
            "Olaf is a fighter who gets more dangerous as he loses health: his passive gives him attack speed and life steal based on his missing health. "
            "Undertow throws his axe to damage and reduce armor and movement speed, Reckless Swing deals true damage (including to himself), and Ragnarok makes him immune to crowd control as long as he keeps attacking."
        ),
        "laning": (
            "Pick up your axe after Undertow: it reduces its cooldown. "
            "Reckless Swing costs you health but refunds it if it kills its target."
        ),
        "combos": [
            {"name": "The trade", "when": "An enemy is within axe range.",
             "how": "Undertow damages and reduces armor and speed, pick up the axe to reduce its cooldown, Reckless Swing deals true damage and Tough It Out gives attack speed and a shield."},
            {"name": "The team engage", "when": "A fight begins.",
             "how": "Ragnarok makes you immune to crowd control as long as you attack; follow with Undertow and Tough It Out."},
            {"name": "The exit from a fight", "when": "A control threatens you.",
             "how": "Ragnarok cancels crowd control if you keep attacking, and Tough It Out gives you a shield."},
        ],
        "mistakes": [
            "Not picking up the axe after Undertow.",
            "Casting Reckless Swing at low health with no guarantee of a kill.",
            "Stopping your attacks during Ragnarok: the immunity depends on your attacks.",
        ],
    },
    "Zoe": {
        "playstyle": (
            "Zoe is a burst mage who plays with distance: Paddle Star!'s damage increases with the distance traveled in a straight line, and Sleepy Trouble Bubble puts the target to sleep. "
            "Her passive adds damage after each ability, Spell Thief lets her pick up the enemy's summoner spells and item actives, and Portal Jump briefly teleports her before bringing her back."
        ),
        "laning": (
            "Fire Paddle Star! from afar and redirect it in flight: the farther it travels, the more it hurts. "
            "Chain ability then attack to benefit from your passive."
        ),
        "combos": [
            {"name": "The basic burst", "when": "An enemy is within Bubble range.",
             "how": "Sleepy Trouble Bubble puts the target to sleep and reduces their magic resistance; damage that wakes them is doubled (up to a maximum): hit with Paddle Star! then a passive attack."},
            {"name": "Spell theft", "when": "An enemy has just used a summoner spell.",
             "how": "Spell Thief picks up the remnants of the enemy's summoner spells and item actives so you can use them yourself; when you use a summoner spell, you fire three projectiles at the nearest enemy."},
            {"name": "The positioning ultimate", "when": "You want to strike safely.",
             "how": "Portal Jump teleports you to a nearby spot for 1 second before bringing you back to your starting point: cast your abilities from the advanced position."},
        ],
        "mistakes": [
            "Casting Paddle Star! point-blank: it loses most of its damage.",
            "Waking the target with a small hit: damage that wakes them is doubled, so save the big one for that.",
            "Forgetting that Portal Jump brings you back to your starting point.",
        ],
    },
    "Milio": {
        "playstyle": (
            "Milio is a mage-support who enchants his allies: his abilities give the allies they hit bonus damage and a burn on their next attack. "
            "Warm Hugs gives a shield and speed (2 charges), Cozy Campfire heals and increases attack range, and his ultimate heals and removes crowd control."
        ),
        "laning": (
            "Ultra Mega Fire Kick pushes an enemy back then lands in an arc to slow. "
            "Warm Hugs has two charges: use one for your carry and keep the other for yourself."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within range.",
             "how": "The fireball pushes back then lands to damage and slow; Warm Hugs on your carry enchants their next attacks."},
            {"name": "Support", "when": "Your team is fighting around a point.",
             "how": "Cozy Campfire heals the allies who enter it and raises their attack range; the zone follows the ally closest to the starting point."},
            {"name": "The healing ultimate", "when": "Your team is under crowd control.",
             "how": "Breath of Life heals allies in range and removes the crowd control affecting them."},
        ],
        "mistakes": [
            "Using both charges of Warm Hugs at once.",
            "Casting Cozy Campfire far from your allies.",
            "Holding the ultimate too long when your team is already under control.",
        ],
    },
    "Shen": {
        "playstyle": (
            "Shen is a long-range support tank: his passive gives him a shield after each ability, and his ultimate gives a shield to an ally before teleporting you to them. "
            "Spirit's Refuge blocks attacks targeting his allies or himself near his blade, and Shadow Dash taunts enemies."
        ),
        "laning": (
            "Twilight Assault deals damage based on the target's max health: use it to harass. "
            "Place your spirit blade so that Spirit's Refuge protects when you are close."
        ),
        "combos": [
            {"name": "The engage", "when": "An enemy is within taunt range.",
             "how": "Shadow Dash dashes you and taunts the enemies you cross; Twilight Assault recalls your blade for damage based on max health; Spirit's Refuge blocks targeted attacks."},
            {"name": "The rescue ultimate", "when": "An ally is in danger far from you.",
             "how": "Stand United gives an absorbing shield to an allied champion then teleports you to them: keep it for an ally under threat."},
            {"name": "Harassment", "when": "An enemy is far from their allies.",
             "how": "The blade slows the enemies it hits when they move away from you; attacks are greatly empowered if it hits a champion."},
        ],
        "mistakes": [
            "Using the ultimate with no ally to protect.",
            "Forgetting your passive: every ability gives you a shield.",
            "Placing Spirit's Refuge far from your blade.",
        ],
    },
    "Renekton": {
        "playstyle": (
            "Renekton is a melee fighter whose attacks generate Fury, more so when he is low on health. "
            "Above 50 Fury, each ability is empowered: Cull the Meek heals more, Ruthless Predator strikes three times and destroys shields, Slice and Dice reduces armor. Dominus makes him sturdier."
        ),
        "laning": (
            "Attack to generate Fury, and keep 50 points to empower your abilities before a trade. "
            "Ruthless Predator stuns for 0.75 seconds (1.5 s when empowered)."
        ),
        "combos": [
            {"name": "The empowered trade", "when": "You have more than 50 Fury.",
             "how": "Ruthless Predator strikes three times, destroys shields and stuns for 1.5 seconds; Cull the Meek and Slice and Dice are empowered."},
            {"name": "The engage", "when": "An enemy is far away.",
             "how": "Slice and Dice charges and damages every unit in the way; follow with the stun then the circular attack."},
            {"name": "Tyrant form", "when": "A team fight begins.",
             "how": "Dominus gives you bonus health, damages the enemies around you and periodically grants you Fury."},
        ],
        "mistakes": [
            "Spending your abilities before 50 Fury.",
            "Using Slice and Dice with no exit plan.",
            "Casting Ruthless Predator on an unshielded target when you could keep the empowered version for a shielded one.",
        ],
    },
    "Kalista": {
        "playstyle": (
            "Kalista is a marksman who hops while moving during her attacks: give a move command during the animation of her attack or Pierce to advance slightly. "
            "Her attacks stick spears into targets, which she rips out to slow and deal increased damage. Her ultimate teleports her oathsworn ally to her."
        ),
        "laning": (
            "Attack and hop at the same time: it is the basis of your mobility. "
            "Rend has no cooldown: use it when the stuck spears are enough to kill or to slow."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within range.",
             "how": "Your attacks stick spears, Pierce passes through the enemies it kills, then Rend rips out the spears to slow and deal increased damage."},
            {"name": "Scouting", "when": "You want vision.",
             "how": "Sentinel sends a soul patrolling along a route, revealing the area ahead of it; it also deals bonus damage when you and your oathsworn hit the same target."},
            {"name": "The ultimate", "when": "Your oathsworn is in danger or must engage.",
             "how": "Fate's Call teleports your oathsworn to you; they can then charge to knock back nearby enemy champions."},
        ],
        "mistakes": [
            "Attacking without hopping: you lose your mobility.",
            "Using the ultimate without coordinating with your oathsworn.",
            "Ripping out the spears with no decisive effect.",
        ],
    },
    "Gangplank": {
        "playstyle": (
            "Gangplank is a fighter whose attacks set the target on fire every few seconds. "
            "Parrrley earns him gold if it kills, Remove Scurvy removes crowd control and heals him, Powder Keg extends the damage of his attacks over the area and slows, and Cannon Barrage bombards an area."
        ),
        "laning": (
            "Attack a keg to extend your damage and slow the enemies around it. "
            "Take last hits with Parrrley to earn extra gold."
        ),
        "strengths": [
            "Kegs extend the damage of his attacks and slow the enemies around them.",
            "Remove Scurvy removes crowd control effects and heals him.",
            "Cannon Barrage bombards a long-range area, slowing and damaging.",
        ],
        "weaknesses": [
            "His power depends on placing and detonating kegs at the right time.",
            "Remove Scurvy has a long cooldown (14 to 22 s).",
            "Little mobility to get away when his kegs are destroyed.",
        ],
        "teamfight": (
            "Gangplank sets up the terrain with kegs, uses Cannon Barrage to slow and damage a whole area, "
            "then detonates the kegs around the enemies. He uses Remove Scurvy to survive a decisive control."
        ),
        "combos": [
            {"name": "The keg", "when": "An enemy is near a keg.",
             "how": "Powder Keg explodes when you attack it, extends the damage over the area and slows; Parrrley finishes."},
            {"name": "The cleanse", "when": "You are under crowd control.",
             "how": "Remove Scurvy removes the crowd control effects affecting you and restores health."},
            {"name": "The area ultimate", "when": "A fight is underway at range.",
             "how": "Cannon Barrage bombards an area, slowing and damaging enemies; combine it with kegs to trap them."},
            {"name": "The keg under the barrage", "when": "Enemies are in a narrow area.",
             "how": "Place a keg, Cannon Barrage slows and damages the area, an attack on the keg extends the damage and slows, Parrrley finishes for gold."},
        ],
        "mistakes": [
            "Placing kegs with no plan to detonate them.",
            "Using Remove Scurvy with no crowd control to remove.",
            "Casting the ultimate without calling out the area to your allies.",
        ],
    },
    "Nidalee": {
        "playstyle": (
            "Nidalee alternates between human form (Javelin Toss, Bushwhack, Primal Surge) and Cougar form (Takedown, Pounce, Swipe). "
            "In tall grass her movement speed increases, and hitting champions with Javelin Toss or Bushwhack puts her on their hunt: true vision and empowered Pounce/Takedown."
        ),
        "laning": (
            "The Javelin deals more damage the farther it travels: it is your harassment ability. "
            "Bushwhack places a trap that damages and reveals: use it to mark and hunt."
        ),
        "combos": [
            {"name": "The hunt", "when": "You have hit with Javelin Toss or Bushwhack.",
             "how": "After hitting with the Javelin, switch to Cougar with Aspect Of The Cougar: Pounce lands you in an area (empowered against the hunted target), Takedown cuts deep (more damage if the target has lost health), Swipe claws."},
            {"name": "Human-form harassment", "when": "An enemy is within Javelin range.",
             "how": "Bushwhack marks and reveals, the Javelin deals more damage with distance, Primal Surge heals allies and gives them attack speed."},
            {"name": "The chase", "when": "An enemy is fleeing.",
             "how": "In Cougar form, Pounce propels you and deals area damage on landing."},
        ],
        "mistakes": [
            "Throwing the Javelin at short range: it deals less damage.",
            "Changing form without having marked: you lose the hunt.",
            "Ignoring tall grass: it raises your speed.",
        ],
    },
    "Naafiri": {
        "playstyle": (
            "Naafiri is an assassin who fights with her pack: pack members appear and attack the targets of her attacks and abilities. "
            "Darkin Daggers applies bleeds, The Call of the Pack makes her untargetable and summons extra members, Eviscerate recalls and heals the pack, and Hounds' Pursuit strikes a champion with the whole pack."
        ),
        "laning": (
            "Your pack attacks with you: stay close to your opponent so it deals its damage. "
            "The daggers apply a bleed; the second deals bonus damage if the target is already bleeding."
        ),
        "combos": [
            {"name": "The trade", "when": "An enemy is within dagger range.",
             "how": "Two Darkin Daggers apply a bleed then bonus damage; the pack leaps onto the first champion hit; Eviscerate dashes you and deals damage around you."},
            {"name": "The execution", "when": "A champion is low.",
             "how": "Hounds' Pursuit sends you and your pack dashing onto a champion; you reveal nearby enemies and can recast if you score a takedown (without a shield the second time)."},
            {"name": "The empowered pack", "when": "A fight begins.",
             "how": "The Call of the Pack makes you untargetable, summons extra members and gives you speed and attack damage; Eviscerate recalls and fully heals the pack."},
        ],
        "mistakes": [
            "Engaging alone: your power depends on your pack.",
            "Using Eviscerate without looking at the state of your pack.",
            "Recasting the ultimate without a takedown.",
        ],
    },
    "Sona": {
        "playstyle": (
            "Sona is an enchanter whose every ability has a direct effect and an aura for the allies it hits: Hymn of Valor damages and gives bonus damage, Aria of Perseverance heals and protects, Song of Celerity speeds up. "
            "Her passive reduces her cooldowns when she uses her abilities well, and her ultimate stuns and forces enemies to dance."
        ),
        "laning": (
            "Chain abilities to benefit from your passive's ability haste. "
            "Your next attack after a few abilities deals bonus damage and an effect depending on the last ability cast."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is close to you and your carry.",
             "how": "Hymn of Valor deals damage to two enemies and gives an aura to your allies; chain to trigger the Power Chord on your attack."},
            {"name": "Protection", "when": "An ally is under threat.",
             "how": "Aria of Perseverance heals you and a nearby wounded ally, with a shield for the allies hit by the aura; Song of Celerity speeds up your team."},
            {"name": "The engage ultimate", "when": "Your team is ready to engage.",
             "how": "Crescendo stuns enemy champions, forces them to dance and deals magic damage to them."},
        ],
        "mistakes": [
            "Casting the ultimate with no ally ready.",
            "Not using your abilities when you can: your passive reduces cooldowns.",
            "Neglecting mana: every ability costs some.",
        ],
    },
}
