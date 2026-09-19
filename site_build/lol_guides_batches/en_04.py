"""English guides, batch 4."""

EN = {
    "Alistar": {
        "playstyle": (
            "Alistar is an engage tank: Pulverize and Headbutt knock enemies up or down, Trample ignores unit collision and sets up a stun on his next attack, and his ultimate removes the crowd control on him while reducing the damage he takes. "
            "His passive charges a roar that heals the whole nearby team when he stuns or displaces enemies."
        ),
        "laning": (
            "Stunning or displacing enemies charges your roar: every control counts, even in lane. "
            "Trample stacks when it hurts a champion: at max stacks, your next attack stuns."
        ),
        "combos": [
            {"name": "The engage combo", "when": "An enemy is within Headbutt range.",
             "how": "Headbutt charges the target and knocks them back, Pulverize knocks nearby enemies into the air: the chain puts the whole enemy team under control."},
            {"name": "The Trample stun", "when": "An enemy is in melee range.",
             "how": "Trample several times to reach the maximum stacks; your next attack against a champion deals bonus magic damage and stuns them."},
            {"name": "The defensive ultimate", "when": "You are caught in crowd control.",
             "how": "Unbreakable Will removes all the crowd control affecting you and reduces the damage you take: engage during its duration without fearing controls."},
        ],
        "mistakes": [
            "Using Pulverize and Headbutt at the same time without coordination.",
            "Forgetting your roar: heal yourself and your team by chaining controls.",
            "Casting the ultimate too early: it is your best protection against a decisive control.",
        ],
    },
    "Nasus": {
        "playstyle": (
            "Nasus is a fighter who gains power through Siphoning Strike: every target killed increases the damage of his next strikes. "
            "Wither heavily slows a champion by reducing their attack and movement speed, Spirit Fire reduces armor, and Fury of the Sands gives him health, range and resistances."
        ),
        "laning": (
            "Take last hits with Siphoning Strike: it is your main source of power. "
            "Your passive gives you a life steal bonus against your opponent, which makes your lane more durable."
        ),
        "combos": [
            {"name": "The trade", "when": "An enemy is within range.",
             "how": "Wither slows the enemy (attack and movement speed), Spirit Fire reduces their armor, Siphoning Strike hits for heavy damage."},
            {"name": "The team fight", "when": "A team fight is underway.",
             "how": "Fury of the Sands gives you more health, attack range, armor and magic resistance and reduces the cooldown of Siphoning Strike: cast it before entering the brawl."},
            {"name": "Farming", "when": "You want to scale.",
             "how": "Siphoning Strike increases the power of your next strikes if it kills its target: take every minion with it."},
        ],
        "mistakes": [
            "Missing last hits with Siphoning Strike: it is your scaling.",
            "Forgetting Wither on the enemy carry.",
            "Entering a fight without your ultimate.",
        ],
    },
    "Pantheon": {
        "playstyle": (
            "Pantheon is an aggressive fighter-assassin: after several abilities or attacks, his next ability is empowered. "
            "Shield Vault stuns, Aegis Assault makes him invulnerable to the attacks he faces, and Grand Starfall lets him leap to a chosen spot and land with area damage."
        ),
        "laning": (
            "Build up your passive with attacks and abilities to get an empowered ability. "
            "Shield Vault stuns: place it for a trade, but keep Aegis Assault to block an important attack."
        ),
        "combos": [
            {"name": "The trade", "when": "An enemy is within range.",
             "how": "Shield Vault dashes you onto the target and stuns them, your attacks build up your passive, Comet Spear (thrust or throw) benefits from the empowered version."},
            {"name": "The block", "when": "An enemy is attacking in your direction.",
             "how": "Aegis Assault makes you invulnerable to the attacks you are facing while delivering rapid spear thrusts. Point the shield at the source."},
            {"name": "The engage ultimate", "when": "You want to surprise your target.",
             "how": "Grand Starfall makes you leap and then land at the chosen spot; follow with Shield Vault and Comet Spear on arrival."},
        ],
        "mistakes": [
            "Using Aegis Assault with no one attacking you head-on.",
            "Forgetting your passive's empowered ability.",
            "Casting Grand Starfall with no plan for what follows: you land in the middle of the enemies.",
        ],
    },
    "Lucian": {
        "playstyle": (
            "Lucian is a mobile marksman who chains abilities and attacks: each ability turns your next attack into a double shot. "
            "Relentless Pursuit dashes him a short distance (and Lightslinger reduces its cooldown), Ardent Blaze briefly marks and reveals enemies with a movement speed bonus when he attacks them, and his ultimate fires a hail of bullets."
        ),
        "laning": (
            "Always chain ability then attack to benefit from the double shot. "
            "When an ally heals or shields you, or an enemy is immobilized, your next 2 attacks deal bonus magic damage."
        ),
        "combos": [
            {"name": "The basic combo", "when": "An enemy is within range of Piercing Light.",
             "how": "Piercing Light pierces the target, your attack becomes a double shot, Relentless Pursuit repositions you (cooldown reduced by Lightslinger) and sets up the next attack."},
            {"name": "Area harassment", "when": "Several enemies are close.",
             "how": "Ardent Blaze explodes in a star shape and marks and reveals enemies; attack them to benefit from the bonus movement speed."},
            {"name": "The ultimate", "when": "An enemy is blocked or immobilized.",
             "how": "The Culling fires a hail of bullets with your weapons: fire it at an enemy controlled by your team to hit everything."},
        ],
        "mistakes": [
            "Attacking without a previous ability: you lose the double shot.",
            "Using Relentless Pursuit without looking at where you end up.",
            "Wasting the ultimate on a moving target with no control.",
        ],
    },
    "Karma": {
        "playstyle": (
            "Karma is a mage-support whose ultimate Mantra empowers her next ability: each one gets a bonus (a cataclysm, a strengthened tether that heals her, a shield extended to nearby allies). "
            "Her damaging abilities reduce Mantra's cooldown, which lets you use it often."
        ),
        "laning": (
            "Inner Flame harasses and reduces Mantra's cooldown by dealing damage. "
            "Focused Resolve reveals the enemy, roots them if they do not break the tether, then deals damage again."
        ),
        "combos": [
            {"name": "Mantra harassment", "when": "An enemy is within range.",
             "how": "Mantra empowers the next ability: Inner Flame also creates a cataclysm that deals damage after a short delay."},
            {"name": "The root", "when": "An enemy can be pinned down.",
             "how": "The empowered Focused Resolve heals Karma and extends the root: the tether roots the enemy if it is not broken."},
            {"name": "Protection", "when": "Your team engages.",
             "how": "Inspire gives a shield and movement speed to the ally; with Mantra, the energy spreads and extends Inspire to nearby allied champions."},
        ],
        "mistakes": [
            "Using Mantra without knowing which ability to empower.",
            "Not using your abilities to reduce its cooldown.",
            "Casting Focused Resolve and letting the tether be broken too easily.",
        ],
    },
    "Chogath": {
        "playstyle": (
            "Cho'Gath is a tank-mage who grows: he regains health and mana for each unit killed, and Feast makes him grow by increasing his max health if it kills its target. "
            "Rupture knocks enemies into the air, Feral Scream silences in a cone and Vorpal Spikes slow."
        ),
        "laning": (
            "Take kills to heal and regain mana. "
            "Rupture is your main control tool: place it where your enemy is going."
        ),
        "combos": [
            {"name": "The control combo", "when": "An enemy is within Rupture range.",
             "how": "Rupture knocks up and slows, Feral Scream silences in the cone, your attacks fire spikes that slow."},
            {"name": "The execution", "when": "An enemy is low.",
             "how": "Feast devours an enemy unit for heavy true damage; if the target is killed, you grow and gain max health."},
            {"name": "The control zone", "when": "Several enemies are in front of you.",
             "how": "Your attacks with Vorpal Spikes damage and slow every enemy in front of you."},
        ],
        "mistakes": [
            "Using Feast on a target you cannot kill: its bonus depends on the kill.",
            "Missing Rupture: it is your entry point.",
            "Neglecting farm: your power depends on kills.",
        ],
    },
    "Leona": {
        "playstyle": (
            "Leona is an engage tank: her spells mark enemies with Sunlight, which your allies pop for bonus magic damage. "
            "Shield of Daybreak stuns on your next attack, Zenith Blade roots the last champion hit and dashes you to them, and Solar Flare stuns in the center and slows on the edge."
        ),
        "laning": (
            "Shield of Daybreak has a short cooldown: use it to stun as soon as you can attack. "
            "Mark enemies so your team can pop Sunlight."
        ),
        "combos": [
            {"name": "The lane engage", "when": "An enemy is within Zenith Blade range.",
             "how": "Zenith Blade hits every enemy on a line, roots the last champion hit and dashes you to them; Shield of Daybreak stuns them on your attack."},
            {"name": "The team ultimate", "when": "Several enemies are grouping.",
             "how": "Solar Flare stuns those in the center and slows those on the edge: center the zone on the carries."},
            {"name": "Defense", "when": "You are in a forward position.",
             "how": "Eclipse raises armor and magic resistance and reduces the damage you take; at the end, it damages nearby enemies and the protection is extended."},
        ],
        "mistakes": [
            "Engaging with no ally to take advantage of Sunlight.",
            "Casting Solar Flare so that it only hits the edge.",
            "Using Eclipse too early: its protection is short.",
        ],
    },
    "Jax": {
        "playstyle": (
            "Jax is a fighter whose attack speed rises with successive attacks. "
            "Leap Strike lets him leap onto a unit, Counter Strike dodges every attack and then stuns nearby enemies, and Grandmaster-at-Arms adds magic damage every third consecutive attack."
        ),
        "laning": (
            "Leap onto minions or allies to reposition. "
            "Keep Counter Strike to dodge an important attack and stun nearby enemies."
        ),
        "combos": [
            {"name": "The basic combo", "when": "An enemy is within leap range.",
             "how": "Leap Strike hits the target, Empower charges your next attack for bonus damage, then your consecutive attacks raise your attack speed."},
            {"name": "The dodge and the stun", "when": "Several enemies attack together.",
             "how": "Counter Strike dodges every attack for a brief moment then stuns nearby enemies: cast it during their attacks, and recast it when the moment is right."},
            {"name": "The team fight", "when": "A team fight starts.",
             "how": "Grandmaster-at-Arms deals magic damage every third attack and can be activated for damage around you and extra resistances."},
        ],
        "mistakes": [
            "Using Counter Strike with no attack to dodge.",
            "Leaping into nothing with no target or exit.",
            "Interrupting your successive attacks: they raise your attack speed.",
        ],
    },
    "Vladimir": {
        "playstyle": (
            "Vladimir is a mage who draws his strength from health: he gains 1 point of power per 30 bonus health, and Transfusion steals the targeted enemy's health. "
            "Sanguine Pool makes him untargetable for 2 seconds, Tides of Blood spends his own health for area damage, and Hemoplague increases the damage infected enemies take before damaging them and healing him."
        ),
        "laning": (
            "Transfusion is your main source of damage and healing. When your gauge is full, its damage and healing increase a lot. "
            "Tides of Blood costs health: only use it if you can heal afterward."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within Transfusion range.",
             "how": "Transfusion steals health, Tides of Blood deals area damage (it can be blocked by enemy units), your attacks finish."},
            {"name": "The team-fight combo", "when": "Several enemies are grouped.",
             "how": "Hemoplague infects the area: enemies take more damage, then take magic damage and heal you for each champion hit. Sanguine Pool makes you untouchable for 2 seconds."},
            {"name": "The escape", "when": "Several enemies are engaging you.",
             "how": "Sanguine Pool makes you untargetable and slows the enemies in the pool; you can drain their life."},
        ],
        "mistakes": [
            "Casting Tides of Blood at low health: it costs you life.",
            "Using Sanguine Pool too early: its cooldown is long.",
            "Casting Hemoplague on enemies who can easily leave the area.",
        ],
    },
    "JarvanIV": {
        "playstyle": (
            "Jarvan IV is an engage fighter-tank: his first attack deals a percentage of the target's current health. "
            "Demacian Standard raises his attack speed and that of nearby allies, Dragon Strike reduces armor and can bring Jarvan back to his Standard while knocking enemies up, and Cataclysm creates an arena around him."
        ),
        "laning": (
            "Your first attack on an enemy deals a percentage of their current health: open the trade with it. "
            "Plant your Demacian Standard to set up your Dragon Strike and an engage."
        ),
        "combos": [
            {"name": "The engage combo", "when": "An enemy is within Dragon Strike range.",
             "how": "Demacian Standard plants a flag that deals magic damage; Dragon Strike brings you back to the standard while knocking up the enemies on the way, then your first attack deals the passive's damage."},
            {"name": "The arena", "when": "A carry is isolated.",
             "how": "Cataclysm leaps you onto a target while turning the area into an arena; follow with Dragon Strike and Golden Aegis to slow."},
            {"name": "Defense", "when": "You are in the middle of a fight.",
             "how": "Golden Aegis calls on the ancient kings to protect you and slow nearby enemies."},
        ],
        "mistakes": [
            "Casting Dragon Strike without the Standard: you lose the knock-up.",
            "Using Cataclysm with no ally to follow up.",
            "Attacking the same target several times: the passive only triggers once per period.",
        ],
    },
}
