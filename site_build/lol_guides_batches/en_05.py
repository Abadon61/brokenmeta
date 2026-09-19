"""English guides, batch 5."""

EN = {
    "Malphite": {
        "playstyle": (
            "Malphite is a tank-mage whose rock shield absorbs 10% of his max health and recharges if he is not hit for a few seconds. "
            "Seismic Shard steals movement speed from the enemy, Ground Slam deals magic damage based on his armor, and Unstoppable Force sends him charging at high speed and knocks enemies up: it is a team-fight engage."
        ),
        "laning": (
            "Seismic Shard brings you closer to your opponent by stealing their movement speed for 3 seconds. "
            "Your Ground Slam damage rises with your armor: stack armor to strengthen your defense as much as your damage."
        ),
        "combos": [
            {"name": "The lane trade", "when": "An enemy is within shard range.",
             "how": "Seismic Shard steals their speed for 3 seconds and brings you closer, Thunderclap makes your attacks produce shockwaves, Ground Slam reduces their attack speed."},
            {"name": "The team engage", "when": "Several enemies are grouped.",
             "how": "Unstoppable Force sends you charging at high speed, damaging the enemies and knocking them up; follow with Ground Slam and your empowered attacks."},
            {"name": "Harassment", "when": "You want to hinder a carry.",
             "how": "Seismic Shard slows by stealing speed; Ground Slam briefly reduces attack speed: you greatly reduce their effectiveness."},
        ],
        "mistakes": [
            "Casting Unstoppable Force with no target to hit in an area.",
            "Getting hit for nothing: your shield recharges if you take no damage.",
            "Neglecting armor: it strengthens your Ground Slam damage.",
        ],
    },
    "Katarina": {
        "playstyle": (
            "Katarina is a burst assassin whose cooldowns are greatly reduced when a champion she recently damaged dies. "
            "She picks up her daggers to damage all nearby enemies, teleports with Shunpo, and her ultimate hits the three nearest enemy champions while she channels."
        ),
        "laning": (
            "Bouncing Blade bounces between nearby enemies before landing on the ground: then pick up the dagger to deal area damage. "
            "Keep Shunpo to close in or flee."
        ),
        "combos": [
            {"name": "The basic combo", "when": "An enemy is within range.",
             "how": "Bouncing Blade throws a dagger, Shunpo teleports you next to the target, Preparation throws a dagger into the air and gives you speed; pick up the daggers to hit nearby enemies."},
            {"name": "The channeled ultimate", "when": "Several enemies are close.",
             "how": "Death Lotus throws knives at the three nearest enemy champions while you channel: position yourself with Shunpo, then cast it."},
            {"name": "The reset", "when": "A damaged champion is about to die.",
             "how": "When a champion you damaged dies, your cooldowns are greatly reduced: recast your abilities to chain into the next one."},
        ],
        "mistakes": [
            "Casting the ultimate and getting interrupted: it is a channel.",
            "Forgetting to pick up the daggers: your passive depends on them.",
            "Using Shunpo with no target or exit.",
        ],
    },
    "Rell": {
        "playstyle": (
            "Rell is an engage tank with two forms: mounted, she dives down knocking enemies up and gains a shield; on foot, she gains defenses, attack speed and range but is slowed. "
            "Her passive steals armor and magic resistance, and her ultimate violently pulls in nearby enemies."
        ),
        "laning": (
            "Shattering Strike breaks shields and stuns in a line. "
            "Your passive gives you bonus magic damage and steals resistances: fight up close."
        ),
        "combos": [
            {"name": "The classic engage", "when": "Your team is ready to follow up.",
             "how": "Ferromancy has you dismount, knocks nearby enemies up and gives you a shield; Shattering Strike stuns along the line."},
            {"name": "The joust with an ally", "when": "An ally is nearby.",
             "how": "Full Tilt gives Rell and the ally rising movement speed, doubled toward enemies; your next attack causes an explosion of magic damage."},
            {"name": "The team ultimate", "when": "Enemies are spread around you.",
             "how": "Magnet Storm violently pulls them toward you then keeps pulling them for a brief moment while damaging them: your team can then target them."},
        ],
        "mistakes": [
            "Staying on foot while forgetting you are slowed.",
            "Casting the ultimate with no ally to take advantage of the clumping.",
            "Using Shattering Strike without checking the line of fire.",
        ],
    },
    "Senna": {
        "playstyle": (
            "Senna is a ranged marksman-support: her passive lets her free the souls trapped in the Black Mist, which boosts her damage, range and critical strike chance. "
            "Piercing Darkness heals allies and damages enemies on its line, Last Embrace roots, and her ultimate has unlimited range with a shield for the allies it hits."
        ),
        "laning": (
            "Attack the souls freed when units die near you. "
            "Your cannon fires more slowly but deals extra damage and gives you part of the target's movement speed."
        ),
        "combos": [
            {"name": "Harassment", "when": "An ally is lined up with the enemy.",
             "how": "Piercing Darkness heals allies and damages the enemies it hits; your cannon attacks benefit from the movement speed bonus."},
            {"name": "The root", "when": "An enemy is within Mist range.",
             "how": "Last Embrace sends a wave of Mist: if it hits an enemy, they are rooted along with nearby enemies after a short delay."},
            {"name": "The global ultimate", "when": "Your allies are fighting far from you.",
             "how": "Dawning Shadow fires a beam with unlimited range: a shield for the allies hit, damage for the enemies in the center."},
        ],
        "mistakes": [
            "Not collecting the souls: they empower your cannon.",
            "Casting Last Embrace when your team cannot take advantage of the root.",
            "Using the ultimate without aiming for allies or the enemy center.",
        ],
    },
    "Hecarim": {
        "playstyle": (
            "Hecarim is a speed jungler: his attack damage rises by a percentage of his bonus movement speed. "
            "Rampage increases his damage and reduces its cooldown with each hit, Devastating Charge knocks back and deals damage based on the distance traveled, and Onslaught of Shadows charges in a line before terrifying on arrival."
        ),
        "laning": (
            "Rampage damages nearby enemies; if it hits at least one, the next ones become faster and stronger. "
            "Spirit of Dread heals you for a percentage of the damage taken by nearby enemies."
        ),
        "combos": [
            {"name": "The charge engage", "when": "An enemy is far away.",
             "how": "Devastating Charge increases your speed and lets you pass through units; your next attack knocks back and deals more damage the farther you have traveled."},
            {"name": "The team fight", "when": "Enemies are grouped.",
             "how": "Onslaught of Shadows charges in a line and terrifies nearby enemies on arrival; follow with Rampage and Spirit of Dread."},
            {"name": "The prolonged fight", "when": "You are in melee.",
             "how": "Rampage gets stronger with each hit; Spirit of Dread gives you armor, magic resistance and health."},
        ],
        "mistakes": [
            "Attacking without bonus movement speed: your damage depends on it.",
            "Using Devastating Charge at too short a distance: its damage depends on the distance traveled.",
            "Casting the ultimate while forgetting it charges in front of you.",
        ],
    },
    "Zeri": {
        "playstyle": (
            "Zeri is a marksman whose attacks deal magic damage and are treated as abilities. "
            "Moving and casting Burst Fire stores energy in her ionic pack; when fully charged, her next attack deals bonus damage. Her ultimate overcharges her: she gains attack speed and Burst Fire becomes a faster triple shot."
        ),
        "laning": (
            "Burst Fire has no cooldown: fire it often while moving to charge your pack. "
            "Ultrashock Laser slows and damages; if it hits a wall, it becomes a long-range laser."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within range.",
             "how": "Burst Fire fires 7 bullets that deal your attack damage to the first enemy hit; Ultrashock Laser slows, then fire Burst Fire again."},
            {"name": "The piercing dash", "when": "You want to engage or flee.",
             "how": "Spark Surge dashes you, empowers Burst Fire so it pierces, and makes you leap over obstacles."},
            {"name": "The overcharge", "when": "A team fight starts.",
             "how": "Lightning Crash triggers a nova and overcharges you: a stacking attack speed bonus on each champion hit and Burst Fire becomes a triple shot with a chain of lightning."},
        ],
        "mistakes": [
            "Not moving while you shoot: your pack charges while you move.",
            "Using the ultimate alone: you need to hit champions to stack attack speed.",
            "Casting Spark Surge with no exit plan.",
        ],
    },
    "Pyke": {
        "playstyle": (
            "Pyke is a support-assassin who regenerates recent damage when he is not seen, and whose extra health is converted into attack damage. "
            "Bone Skewer pulls an enemy in, Phantom Undertow stuns as it passes, Ghostwater Dive camouflages him, and his ultimate executes low-health enemies and grants bonus gold to the ally who assists."
        ),
        "laning": (
            "Bone Skewer can stab an enemy in front of you or pull them in: choose based on the distance. "
            "Stay out of sight to regenerate recent damage."
        ),
        "combos": [
            {"name": "The hook", "when": "An enemy is within harpoon range.",
             "how": "Bone Skewer pulls the enemy in, Phantom Undertow leaves a phantom that stuns champions in its path when it returns."},
            {"name": "The execution", "when": "Several enemies are low on health.",
             "how": "Death From Below dashes onto low-health enemies to execute them, which lets you recast the spell and grant bonus gold to an assisting ally."},
            {"name": "The stealthy approach", "when": "You want to surprise.",
             "how": "Ghostwater Dive camouflages you with a large speed bonus that fades: approach then hook."},
        ],
        "mistakes": [
            "Trying to increase your max health: it is converted into attack damage.",
            "Casting the ultimate on enemies with a lot of health.",
            "Using Bone Skewer without looking at the minions.",
        ],
    },
    "Ashe": {
        "playstyle": (
            "Ashe is a control marksman: her attacks slow their targets and deal bonus damage to affected targets, and her critical strikes apply a stronger slow. "
            "Hawkshot sends her hawk scouting anywhere on the map, and Enchanted Crystal Arrow stuns for a duration that grows with distance."
        ),
        "laning": (
            "Attack to generate Focus; at max, Ranger's Focus increases your attack speed. "
            "Volley deals more damage in a cone and applies Frost Shot."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within range.",
             "how": "Volley applies Frost Shot: your following attacks deal bonus damage to affected targets."},
            {"name": "The team fight", "when": "A team fight is underway.",
             "how": "Ranger's Focus consumes your stacks to temporarily raise your attack speed and turn your attacks into volleys of arrows."},
            {"name": "The long-range ultimate", "when": "An engage or a chase is underway.",
             "how": "Enchanted Crystal Arrow stuns the first champion hit: the farther it travels, the longer the stun, and nearby units take damage and are slowed."},
        ],
        "mistakes": [
            "Using the ultimate at too short a range: the stun is shorter.",
            "Forgetting Hawkshot: the vision it gives is its real value.",
            "Wasting Ranger's Focus before a fight.",
        ],
    },
    "Irelia": {
        "playstyle": (
            "Irelia is a mobile fighter whose abilities give her stacking attack speed. "
            "Bladesurge resets if it kills its target or hits a marked target, Flawless Duet damages, stuns and marks between two blades, and Vanguard's Edge creates a wall that damages and slows."
        ),
        "laning": (
            "Chain Bladesurge through minions to close in: its cooldown resets if it kills. "
            "Defiant Dance protects you from physical damage while charging."
        ),
        "combos": [
            {"name": "The engage combo", "when": "An enemy is within range.",
             "how": "Flawless Duet damages, stuns and marks; Bladesurge on a marked target resets its cooldown: you can chain and stack Ionian Fervor."},
            {"name": "The wall ultimate", "when": "A team fight starts.",
             "how": "Vanguard's Edge damages and marks the champions hit then forms a wall that slows; use the marks to recast Bladesurge."},
            {"name": "Physical defense", "when": "An enemy attacks with physical damage.",
             "how": "Defiant Dance charges an attack and makes you take less physical damage; the longer the charge, the more the damage increases."},
        ],
        "mistakes": [
            "Using Bladesurge with no minion or mark to come back from.",
            "Charging Defiant Dance with no protection against magic damage.",
            "Neglecting your passive's attack speed: it requires hitting with your abilities.",
        ],
    },
    "Xerath": {
        "playstyle": (
            "Xerath is a long-range mage: Arcanopulse, Eye of Destruction and Shocking Orb harass from very far away. "
            "His attacks restore mana and his ultimate roots him in place to fire several long-range barrages."
        ),
        "laning": (
            "Arcanopulse deals damage to every target hit: cast it to hit enemies and minions. "
            "Eye of Destruction slows in the area, with more effect in the center."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within range.",
             "how": "Arcanopulse deals damage in a line, Eye of Destruction slows (more in the center), Shocking Orb stuns and damages."},
            {"name": "The control stun", "when": "An enemy dives you.",
             "how": "Shocking Orb stuns first, then Eye of Destruction and Arcanopulse do the damage."},
            {"name": "The siege ultimate", "when": "Enemies are visible at long range.",
             "how": "Rite of the Arcane roots you to fire several barrages: cast it when you are protected."},
        ],
        "mistakes": [
            "Casting the ultimate with no protection: you are rooted while firing.",
            "Wasting Shocking Orb: it is your only stun.",
            "Neglecting mana: your attacks restore it regularly.",
        ],
    },
}
