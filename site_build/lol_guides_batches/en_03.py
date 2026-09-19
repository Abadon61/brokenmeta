"""English guides, batch 3."""

EN = {
    "Camille": {
        "playstyle": (
            "Camille is a mobile fighter who gains a shield when attacking champions, adapted to the enemy's damage type (physical or magic). "
            "Hookshot lets her leap off a wall and knock champions up on landing, and her ultimate locks a target in an area where her attacks deal bonus magic damage."
        ),
        "laning": (
            "Precision Protocol deals much more damage if you wait between the two activations: do not recast it too quickly. "
            "Your passive protects you according to your opponent's damage type, which makes close-range trades favorable."
        ),
        "combos": [
            {"name": "The lane trade", "when": "An enemy is within attack range.",
             "how": "Precision Protocol empowers your next attack and gives you speed; recast it after a short wait to deal much more damage. Tactical Sweep hits with the outer half of the cone to slow and heal you."},
            {"name": "The Hookshot engage", "when": "A wall is close to the target.",
             "how": "Hookshot launches you toward a wall and then leaps you off it; enemy champions hit on landing are knocked into the air. Chain your abilities while they are vulnerable."},
            {"name": "The area execution", "when": "A carry is isolated.",
             "how": "The Hextech Ultimatum sends you onto a champion and locks them in an area; take advantage of the bonus magic damage of your basic attacks on them."},
        ],
        "mistakes": [
            "Recasting Precision Protocol too quickly: the wait between the two attacks greatly increases the damage.",
            "Casting Tactical Sweep aiming at the inner half of the cone: it is the outer half that slows and heals you.",
            "Using Hookshot with no wall nearby: it needs one to launch itself.",
        ],
    },
    "Ekko": {
        "playstyle": (
            "Ekko is an assassin-mage who manipulates time. His passive deals bonus magic damage every third attack or ability on the same target. "
            "Timewinder slows and damages twice, Parallel Convergence creates an anomaly that slows then stuns, and his ultimate makes him untargetable by returning him to where he was a few seconds ago."
        ),
        "laning": (
            "Use Timewinder at range: the grenade returns to you and damages on its way. "
            "Do not hold Chronobreak for nothing: his ultimate is as much a survival tool as an engage."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within range of the grenade.",
             "how": "Timewinder deals damage and slows, Phase Dive teleports you next to the target with bonus damage, then your attacks trigger the passive every third hit."},
            {"name": "The stun", "when": "Enemies are grouping.",
             "how": "After a few seconds, Parallel Convergence creates an anomaly that slows; if you enter it, you gain a shield and stun those inside. Place it where they are going."},
            {"name": "The emergency ultimate", "when": "You are in danger or want to damage several enemies.",
             "how": "Chronobreak makes you untargetable and returns you to where you were a few seconds earlier, recovering a percentage of the health you lost; enemies near your arrival take heavy damage."},
        ],
        "mistakes": [
            "Using the ultimate without remembering you go back to where you were a few seconds ago: assess that spot first.",
            "Placing Parallel Convergence at random: it has a delay before it creates the anomaly.",
            "Wasting Phase Dive: it is your dodge, and its next attack teleports you next to the target.",
        ],
    },
    "Seraphine": {
        "playstyle": (
            "Seraphine is a support mage whose passive makes her cast the chosen basic ability twice every three basic abilities. "
            "She protects and heals with Surround Sound, deals area damage with High Note and Beat Drop, and her ultimate charms the enemies it hits with a range that extends with each champion hit."
        ),
        "laning": (
            "Cast abilities near your allies: your next basic attack gains range and magic damage. "
            "High Note is your main harassment tool, and Beat Drop restricts movement in a line."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within area range.",
             "how": "High Note deals area damage, Beat Drop hits in a line and restricts their movement, then your attack benefits from the bonus range of your passive."},
            {"name": "Protection", "when": "Your allies are under threat.",
             "how": "Surround Sound gives haste and a shield to nearby allies; if you already have a shield, it also heals allies. Place it in the middle of the fight."},
            {"name": "The chain ultimate", "when": "Enemies and allies are lined up.",
             "how": "Encore deals damage and charms the enemies hit; its range extends with each champion hit, ally or enemy. Aim to hit as many as possible."},
        ],
        "mistakes": [
            "Casting the ultimate with no ally or enemy to extend its range.",
            "Neglecting the passive: the ability cast twice is your best damage opportunity.",
            "Using Surround Sound too early: its cooldown is long.",
        ],
    },
    "Akali": {
        "playstyle": (
            "Akali is an energy assassin who plays with the energy ring created around the damaged target: leaving it empowers her next attack with range and damage. "
            "Twilight Shroud makes her invisible and untargetable, Shuriken Flip dashes her onto a marked target, and her ultimate can execute the enemies it hits on the recast."
        ),
        "laning": (
            "Five Point Strike slows and hits at short range: chain it with your passive by leaving the ring to empower your attack. "
            "Twilight Shroud protects you briefly but you are revealed if you attack or use abilities."
        ),
        "combos": [
            {"name": "The trade", "when": "An enemy is within kunai range.",
             "how": "Five Point Strike damages and slows, and creates the energy ring; leave the ring to empower your attack, then Shuriken Flip."},
            {"name": "The full engage", "when": "A carry is within engage range.",
             "how": "Shuriken Flip marks the first enemy or cloud hit; recast it to dash onto the marked target. Perfect Execution leaps you in, and on the recast executes every enemy you hit."},
            {"name": "The escape", "when": "You need to get away.",
             "how": "Twilight Shroud gives you movement speed and makes you invisible; Shuriken Flip on a smoke cloud you hit lets you dash onto it."},
        ],
        "mistakes": [
            "Casting the ultimate with no target in range: it is your main execution tool.",
            "Attacking from the Shroud while forgetting it briefly reveals you.",
            "Spending too much energy on minions: every ability costs some.",
        ],
    },
    "Nami": {
        "playstyle": (
            "Nami is a water enchanter: Aqua Prison stuns, Ebb and Flow heals allies and damages enemies as it bounces, and Tidecaller's Blessing empowers an ally's attacks (magic damage and slow). "
            "Her abilities on allies give them movement speed, and her ultimate knocks the enemies it hits into the air."
        ),
        "laning": (
            "Aqua Prison is your engage: its bubble stuns on impact, so aim well. "
            "Tidecaller's Blessing on your carry gives them a slow and bonus damage: it is the core of your harassment."
        ),
        "combos": [
            {"name": "The lane engage", "when": "Your carry is ready to strike.",
             "how": "Aqua Prison stuns on impact, Tidecaller's Blessing empowers your ally, Ebb and Flow heals your team and damages the target as it bounces."},
            {"name": "Protection", "when": "An ally is in trouble.",
             "how": "Ebb and Flow bounces between allied and enemy champions: it heals allies and damages enemies. Tidecaller's Blessing slows the aggressors."},
            {"name": "The engage ultimate", "when": "A team fight starts.",
             "how": "Tidal Wave knocks the enemies it hits into the air, slows and damages them; your allies it hits gain double the effect of Surging Tides."},
        ],
        "mistakes": [
            "Casting Aqua Prison without accounting for the bubble's travel time: it stuns on impact, so plan its trajectory.",
            "Forgetting to heal: Ebb and Flow is also your sustain tool.",
            "Using the ultimate with no ally nearby: its speed effect benefits your team.",
        ],
    },
    "Graves": {
        "playstyle": (
            "Graves is a marksman-jungler with a unique shotgun: each attack fires four pellets that do not pass through units, and he has to reload when out of ammo. "
            "Quickdraw gives him armor and magic resistance, Smoke Screen reduces enemy vision, and Collateral Damage deals heavy damage to the first champion hit."
        ),
        "laning": (
            "Your pellets do not pass through units: stand at short range to hit with all of them. "
            "Quickdraw recharges when you hit with your basic attacks and gives you a defensive bonus."
        ),
        "combos": [
            {"name": "The melee combo", "when": "An enemy is close.",
             "how": "Quickdraw brings you closer and gives you armor; your attacks reduce its cooldown, End of the Line explodes after 1 second or on contact with an obstacle."},
            {"name": "The control zone", "when": "You want to reduce the enemy's vision.",
             "how": "Smoke Screen damages and briefly slows and reduces the field of vision; follow with End of the Line and Quickdraw."},
            {"name": "The cone ultimate", "when": "Enemies are in a line.",
             "how": "Collateral Damage deals heavy damage to the first champion hit then explodes in a cone: aim at a front-line enemy with others behind."},
        ],
        "mistakes": [
            "Attacking from far away: your pellets do not all hit at long range.",
            "Ignoring your magazine: reloading at the wrong time costs you damage.",
            "Casting the ultimate without looking at what the cone will hit.",
        ],
    },
    "Ambessa": {
        "playstyle": (
            "Ambessa is an energy fighter whose passive triggers a short dash after an ability cast while moving or attacking, with bonus range, damage and attack speed on the next attack. "
            "Her twin drakehounds give her ability variants, and her ultimate teleports her onto the farthest enemy to stun them."
        ),
        "laning": (
            "Cast an ability while moving or attacking to trigger your dash: it is the basis of your chain. "
            "Repudiation gives you a shield and deals bonus damage if you block damage from units other than minions."
        ),
        "combos": [
            {"name": "The trade", "when": "An enemy is within range.",
             "how": "Cunning Sweep deals bonus damage, and if it hits, the next cast becomes a Sundering Slam in a straight line. Lacerate slows and damages."},
            {"name": "The Lacerate dash", "when": "You want to amplify your dash.",
             "how": "Using Drakehound's Step out of Lacerate triggers an extra strike at the end. Repudiation protects you during the chain."},
            {"name": "The execution", "when": "An isolated carry is in a straight line.",
             "how": "Public Execution teleports you onto the farthest enemy on a line, neutralizes them, then slams them to the ground for damage and a stun."},
        ],
        "mistakes": [
            "Casting the ultimate without checking who the farthest enemy on the line is.",
            "Not triggering your dash: it accounts for a large part of your damage.",
            "Using Repudiation with nothing to block: its bonus damage depends on what you block.",
        ],
    },
    "Talon": {
        "playstyle": (
            "Talon is a mobile assassin: his abilities wound champions and large monsters (up to 3 stacks), and an attack on a champion with 3 wounds makes them bleed for heavy damage over time. "
            "Assassin's Path lets him jump over walls, and Shadow Assault makes him invisible with a speed bonus."
        ),
        "laning": (
            "Stack 3 wounds with Noxian Diplomacy and Rake, then attack to trigger the bleed. "
            "Assassin's Path has a short cooldown but the terrain crossed has a long one: do not overuse it."
        ),
        "combos": [
            {"name": "The trade", "when": "An enemy is within blade range.",
             "how": "Rake damages on the way out and back and slows, Noxian Diplomacy stabs (critical strike in melee) and stacks, your attack triggers the bleed at 3 stacks."},
            {"name": "The assassination", "when": "A carry is isolated behind a wall.",
             "how": "Assassin's Path crosses the terrain, Noxian Diplomacy leaps onto the target from range, then Shadow Assault makes you invisible and damages the enemies hit by the blades."},
            {"name": "The escape", "when": "You need to get away.",
             "how": "Shadow Assault makes you invisible with a movement speed bonus; Assassin's Path crosses a wall to cut off the chase."},
        ],
        "mistakes": [
            "Attacking without the 3 wounds: the bleed depends on the stacks.",
            "Using Assassin's Path without thinking: the terrain crossed has a long cooldown.",
            "Casting the ultimate too early: the blades return to you when you become visible again.",
        ],
    },
    "Bard": {
        "playstyle": (
            "Bard is a wandering support who collects chimes to gain experience, mana and out-of-combat movement speed. "
            "His Meeps add damage to his attacks and, with enough chimes, deal area damage and slow. Cosmic Binding slows and can stun, Magical Journey opens a portal, and his ultimate places all units and turrets in stasis."
        ),
        "laning": (
            "Collect chimes to stay ahead in experience and mana. "
            "Cosmic Binding stuns if it hits a wall or a second enemy: position yourself for that."
        ),
        "combos": [
            {"name": "The stun", "when": "An enemy is near a wall or another enemy.",
             "how": "Cosmic Binding slows the first enemy hit; if it hits a wall it stuns the initial target, and a second enemy stuns both. Your Meeps add their damage to your attacks."},
            {"name": "The rescue", "when": "An ally is low or needs speed.",
             "how": "Caretaker's Shrine reveals a sanctuary that heals and speeds up the first ally to touch it. Magical Journey creates a one-way portal usable by everyone, allies and enemies."},
            {"name": "The control ultimate", "when": "A fight is underway.",
             "how": "Tempered Fate briefly places all units and turrets in stasis: use it to save an ally, stop a chase or make an engage pointless."},
        ],
        "mistakes": [
            "Neglecting chimes: they give you experience, mana and speed.",
            "Using the ultimate without thinking: it also puts your allies and turrets in stasis.",
            "Opening Magical Journey without thinking: enemies can use it too.",
        ],
    },
    "Viego": {
        "playstyle": (
            "Viego is a jungler whose passive turns enemies who die in front of him into spectres: he takes control of them by attacking them, recovers a percentage of their health and gains access to their basic abilities and items. "
            "He does not get their ultimate but can cast his own for free. His blade deals a percentage of current health as bonus damage."
        ),
        "laning": (
            "Your blade deals a percentage of the target's current health: it is effective against high-health targets. "
            "Harrowed Path lets you hide in the Black Mist as a spectre: camouflage yourself and gain speed."
        ),
        "combos": [
            {"name": "The basic combo", "when": "An enemy is within charge range.",
             "how": "Spectral Maw charges then dashes you forward with an orb that stuns the first enemy hit; Blade of the Ruined King hits twice the enemies recently hit and heals you."},
            {"name": "The execution", "when": "A carry is weakened.",
             "how": "Heartbreaker teleports you next to a champion and executes them on arrival, knocking back their nearby allies. Keep it for a low-health enemy."},
            {"name": "The possession cycle", "when": "An enemy dies in front of you.",
             "how": "Attack the spectre to take control of the dead enemy's body: you recover health and have access to their basic abilities and items, and you can cast your ultimate for free."},
        ],
        "mistakes": [
            "Not taking advantage of spectres: your passive is your best source of power.",
            "Casting Heartbreaker on a full-health enemy.",
            "Hiding in the Mist without a plan: coming out in the middle of the enemies is dangerous.",
        ],
    },
}
