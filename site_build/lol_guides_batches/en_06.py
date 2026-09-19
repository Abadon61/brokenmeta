"""English guides, batch 6."""

EN = {
    "Aatrox": {
        "playstyle": (
            "Aatrox is a melee fighter who wins long trades: his passive regularly lets him deal bonus magic damage and heal based on a percentage of the target's max health. "
            "The Darkin Blade hits up to three times with different areas, Infernal Chains drag back those who do not leave the area, and his ultimate increases his damage, healing and speed."
        ),
        "laning": (
            "The Darkin Blade has three strikes with different areas: vary your positioning to hit every time. "
            "Umbral Dash passively heals you when you damage champions and dashes you when activated."
        ),
        "combos": [
            {"name": "The lane trade", "when": "An enemy is within chain range.",
             "how": "Infernal Chains damages the first enemy hit and drags them back if they do not leave the area, The Darkin Blade strikes next, your attack benefits from your passive, Umbral Dash repositions you."},
            {"name": "The three strikes", "when": "The enemy is cornered.",
             "how": "Each hit of The Darkin Blade has a different area of effect: chain all three while moving to hit the target."},
            {"name": "The team fight", "when": "A fight begins.",
             "how": "World Ender gives you damage, healing and speed and terrifies nearby minions; its duration is extended if you take part in an enemy champion takedown."},
        ],
        "mistakes": [
            "Casting The Darkin Blade three times in the same place: each strike has a different area.",
            "Using Infernal Chains without giving the enemy time to stay in the area.",
            "Forgetting your passive: it triggers regularly and heals.",
        ],
    },
    "Galio": {
        "playstyle": (
            "Galio is a tank-mage who protects his allies from afar: his ultimate designates an ally's position, gives an anti-magic shield to every ally in the area, then slams down to knock enemies up. "
            "Shield of Durand taunts after a channel, Justice Punch knocks up the first champion hit, and Winds of War creates a tornado that deals damage over time."
        ),
        "laning": (
            "Your passive deals area magic damage every few seconds: time a basic attack on the minions and the champion. "
            "Shield of Durand slows you while channeling; only use it against magic damage."
        ),
        "combos": [
            {"name": "The trade", "when": "An enemy is within tornado range.",
             "how": "Winds of War fires two gusts that converge into a tornado, Justice Punch knocks up the first champion hit, and your passive deals area damage."},
            {"name": "The team engage", "when": "An ally is in danger far from you.",
             "how": "Hero's Entrance designates an ally's area, gives every ally an anti-magic shield, then Galio slams down after a delay, knocking up nearby enemies."},
            {"name": "The taunt", "when": "Enemies are targeting your team.",
             "how": "Shield of Durand is a channeled defensive stance; on release, you taunt and damage nearby enemies."},
        ],
        "mistakes": [
            "Casting Hero's Entrance without warning your ally: the delay is long.",
            "Using Shield of Durand against physical damage.",
            "Missing Justice Punch: it knocks up the first champion hit.",
        ],
    },
    "Blitzcrank": {
        "playstyle": (
            "Blitzcrank is a support-tank who wins by making picks: Rocket Grab catches an enemy and pulls them in, then Power Fist doubles the damage of his next attack and knocks the target up. "
            "His passive gives him a shield at low health based on his mana, Overdrive boosts his attack and movement speed, and his ultimate damages and silences."
        ),
        "laning": (
            "The grab is your lane ability: every hit decides the trade. "
            "Keep some mana: your Mana Barrier depends on it."
        ),
        "combos": [
            {"name": "The pick", "when": "An enemy is isolated on the trajectory.",
             "how": "Rocket Grab pulls them to you while damaging them, Power Fist doubles the damage of your attack and knocks them into the air."},
            {"name": "The chase", "when": "You need to catch up to a target.",
             "how": "Overdrive greatly boosts your attack and movement speed but slows you at the end: only use it if the chase is decisive."},
            {"name": "The area ultimate", "when": "Enemies are in melee range.",
             "how": "Static Field marks the enemies you attack (lightning after 1 second); activate it to destroy nearby shields, damage and silence."},
        ],
        "mistakes": [
            "Throwing the grab blind: its cooldown is long.",
            "Using Overdrive without being able to take advantage of the speed, since you are slowed afterward.",
            "Forgetting your barrier: keep some mana when you are at low health.",
        ],
    },
    "Khazix": {
        "playstyle": (
            "Kha'Zix is a jungle assassin who exploits isolated targets: they are marked, and his abilities benefit from interactions with them. "
            "He turns invisible with his ultimate, which triggers his passive (bonus magic damage and a slow), and his ultimate evolves his abilities with new effects."
        ),
        "laning": (
            "Look for isolated targets: Taste Their Fear deals more damage to them. "
            "Leap lets you engage or flee; some evolutions improve its range and cooldown."
        ),
        "combos": [
            {"name": "The isolated assassination", "when": "An enemy is isolated.",
             "how": "Void Assault makes you invisible and triggers Unseen Threat: your next attack deals bonus magic damage and slows; Taste Their Fear deals more damage to an isolated target."},
            {"name": "The leap engage", "when": "The target is far away.",
             "how": "Leap damages around the landing point; follow with Taste Their Fear and Void Spike, which heals you if you are within the explosion radius."},
            {"name": "The invisible escape", "when": "You need to get away.",
             "how": "Void Assault raises your movement speed and makes you invisible; the Adaptive Cloaking evolution extends the duration and allows one more use."},
        ],
        "mistakes": [
            "Engaging an enemy who is with others: your bonuses depend on isolation.",
            "Not choosing your evolutions according to the situation.",
            "Staying visible before the engage: you lose Unseen Threat.",
        ],
    },
    "TwistedFate": {
        "playstyle": (
            "Twisted Fate is a card mage: Wild Cards throws three cards that pierce, Pick a Card chooses a card with extra effects for the next attack, and Destiny reveals enemy champions and enables Gate to teleport. "
            "His passive gives him bonus gold on every kill."
        ),
        "laning": (
            "Pick a Card sets up your next attack: choose the card according to need (damage, control, mana). "
            "Stacked Deck gives attack speed and bonus damage every 4 attacks."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within range.",
             "how": "Pick a Card selects the card for your next attack, the attack benefits from the extra effect, then Wild Cards throws three piercing cards."},
            {"name": "The gate", "when": "A distant fight starts.",
             "how": "Destiny reveals enemy champions and enables Gate, which teleports you in 1.5 seconds to the chosen spot on the map."},
            {"name": "Farming", "when": "You want gold.",
             "how": "Loaded Dice gives 1 to 6 bonus gold for every unit killed; Stacked Deck deals bonus damage every 4 attacks."},
        ],
        "mistakes": [
            "Using Gate without looking at the enemies around your destination.",
            "Wasting Pick a Card with no target.",
            "Neglecting farm: your passive gives you gold.",
        ],
    },
    "Janna": {
        "playstyle": (
            "Janna is a control and protection enchanter: her allies gain speed when moving toward her, and Eye Of The Storm protects an ally or a turret while raising their attack damage. "
            "Howling Gale knocks up enemies, Zephyr reduces an enemy's speed, and Monsoon pushes enemies back then heals allies."
        ),
        "laning": (
            "Howling Gale can be charged to grow in size: recast it to release the tornado. "
            "Zephyr passively gives you movement speed and lets you pass through units."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within Zephyr range.",
             "how": "Zephyr deals damage and slows the enemy, your passive adds damage tied to your bonus movement speed, then recast Howling Gale."},
            {"name": "Protection", "when": "Your carry is under threat.",
             "how": "Eye Of The Storm protects an allied champion or a turret from damage and raises their attack damage."},
            {"name": "The defensive ultimate", "when": "Enemies dive your team.",
             "how": "Monsoon pushes enemies far away; the last breezes heal nearby allies as long as the ability is active."},
        ],
        "mistakes": [
            "Casting Howling Gale without charging it when you can.",
            "Using the ultimate too early: its healing depends on its duration.",
            "Placing Eye Of The Storm on a target who is not fighting.",
        ],
    },
    "Shaco": {
        "playstyle": (
            "Shaco is a trickery assassin: Deceive makes him invisible and teleports him, and his first attack while invisible deals bonus damage, with a critical strike if he hits from behind. "
            "Jack In The Box terrifies, Two-Shiv Poison slows, and his ultimate creates a clone that explodes into mini boxes."
        ),
        "laning": (
            "Strike from behind: your attacks and Two-Shiv Poison deal more damage. "
            "Place Jack In The Box in strategic spots: they terrify and then attack."
        ),
        "combos": [
            {"name": "The backstab assassination", "when": "A carry is isolated.",
             "how": "Deceive makes you invisible and teleports you; the first attack is empowered, a critical strike from behind. Two-Shiv Poison slows and the thrown dagger deals bonus damage under 30% health."},
            {"name": "The trap", "when": "An enemy is chasing you.",
             "how": "Jack In The Box terrifies then attacks nearby enemies when triggered; Two-Shiv Poison slows their chase."},
            {"name": "The duel with the clone", "when": "A close-quarters fight begins.",
             "how": "Hallucinate creates a clone that attacks (reduced damage to turrets); when it dies it explodes, spawning three mini boxes."},
        ],
        "mistakes": [
            "Attacking from the front: you lose your backstab bonuses.",
            "Placing boxes without thinking about their visibility.",
            "Using Deceive with no plan for what follows.",
        ],
    },
    "Ryze": {
        "playstyle": (
            "Ryze is a mage whose abilities deal extra damage based on his bonus mana. "
            "Spell Flux marks targets; Overload bounces between marked enemies, Rune Prison roots them, and Realm Warp transports your allies to a nearby spot."
        ),
        "laning": (
            "Chain abilities to charge runes: two charged runes give Overload a brief movement speed boost. "
            "Mark with Spell Flux before using your other abilities."
        ),
        "combos": [
            {"name": "The basic combo", "when": "An enemy is within range.",
             "how": "Spell Flux marks the target and nearby enemies, Overload deals bonus damage to a marked target and bounces, Rune Prison roots them instead of slowing."},
            {"name": "The area", "when": "Several enemies are grouped.",
             "how": "Flux marks the enemies near the target; Overload bounces toward them, and their damage benefits from the mark."},
            {"name": "The team portal", "when": "You want to reposition your team.",
             "how": "Realm Warp opens a portal to a nearby spot: a few seconds later, every ally near the portal is transported there."},
        ],
        "mistakes": [
            "Casting Rune Prison without a mark: the root depends on Flux.",
            "Neglecting your mana: your damage depends on it.",
            "Opening the portal without warning your team.",
        ],
    },
    "Garen": {
        "playstyle": (
            "Garen is a simple, sturdy fighter: he regenerates a percentage of his health if he has not taken damage recently, and gains armor and magic resistance by killing. "
            "Decisive Strike makes him faster and silences, Courage gives a shield and tenacity, Judgment deals area damage, and Demacian Justice tries to execute a champion."
        ),
        "laning": (
            "Decisive Strike removes slows and gives you speed: use it to open the trade. "
            "Your regeneration only triggers without damage: step out of range to heal."
        ),
        "combos": [
            {"name": "The trade", "when": "An enemy is within range.",
             "how": "Decisive Strike gives you speed, your next attack deals bonus damage and silences, Judgment spins around you."},
            {"name": "Defense", "when": "You are taking heavy damage.",
             "how": "Courage gives a shield and great tenacity for a brief moment, then a smaller damage reduction for longer."},
            {"name": "The execution", "when": "A champion is low.",
             "how": "Demacian Justice tries to execute an enemy champion: cast it when their health is low."},
        ],
        "mistakes": [
            "Casting the ultimate on a full-health enemy.",
            "Staying in lane without ever backing off: your regeneration needs a break.",
            "Forgetting Courage before you get caught in a control.",
        ],
    },
    "Leblanc": {
        "playstyle": (
            "LeBlanc is a burst and mobility assassin: Sigil of Malice marks the target and explodes when an ability damages it. "
            "Distortion makes her dash and return, Ethereal Chains roots after 1.5 seconds, and Mimic copies one of her basic abilities."
        ),
        "laning": (
            "Mark with Sigil of Malice then trigger the explosion with an ability within 3.5 seconds. "
            "If the sigil kills the target, you recover the mana cost and reduce its remaining cooldown."
        ),
        "combos": [
            {"name": "The burst", "when": "An enemy is within range.",
             "how": "Sigil of Malice marks the target, Mimic triggers the explosion again by copying your spell, Distortion dashes in while damaging nearby enemies, Ethereal Chains roots after 1.5 seconds."},
            {"name": "The engage and exit", "when": "You want to strike then flee.",
             "how": "Distortion makes you dash; within 4 seconds, recast it to return to your starting point."},
            {"name": "Safety", "when": "An enemy is chasing you.",
             "how": "Ethereal Chains throws a chain: if it stays attached for 1.5 seconds, the enemy is rooted. Your passive makes you invisible under 40% health."},
        ],
        "mistakes": [
            "Casting abilities before marking: the sigil has to explode.",
            "Forgetting that Distortion can be recast within 4 seconds.",
            "Using the ultimate on an ability whose cooldown is too long.",
        ],
    },
}
