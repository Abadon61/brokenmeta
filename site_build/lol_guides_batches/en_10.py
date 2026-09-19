"""English guides, batch 10."""

EN = {
    "Poppy": {
        "playstyle": (
            "Poppy is an anti-mobility tank: Steadfast Presence stops enemy dashes around her (the enemy is slowed and grounded), Heroic Charge knocks back and stuns against a wall, and Keeper's Verdict knocks enemies very far away. "
            "Her passive throws her shield, which she picks up for a temporary shield."
        ),
        "laning": (
            "Pick up your shield after your passive to get a temporary shield. "
            "Hammer Shock creates a zone that slows then explodes after a delay."
        ),
        "combos": [
            {"name": "The wall stun", "when": "An enemy is near a wall.",
             "how": "Heroic Charge knocks the target back; against a wall they are stunned. Hammer Shock slows then explodes."},
            {"name": "Anti-dive", "when": "An enemy dashes toward your carry.",
             "how": "Steadfast Presence stops dashes around you: the enemy is slowed and grounded. Keeper's Verdict then knocks the enemy very far away."},
            {"name": "Harassment", "when": "An enemy is in lane.",
             "how": "Hammer Shock deals damage and creates a zone that explodes; your attack then throws the shield."},
        ],
        "mistakes": [
            "Not picking up your shield.",
            "Using Steadfast Presence with no dash to stop.",
            "Casting Heroic Charge far from a wall when you could wait.",
        ],
    },
    "Karthus": {
        "playstyle": (
            "Karthus is an area mage who keeps casting spells while dying: his passive gives him a spirit form. "
            "Lay Waste explodes after a delay (stronger on an isolated target), Wall of Pain reduces speed and magic resistance, Defile restores his mana on kills, and Requiem deals damage to all enemy champions after 3 seconds."
        ),
        "laning": (
            "Lay Waste has no cooldown: cast it nonstop on minions and enemies. "
            "Defile restores your mana on every kill."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is isolated.",
             "how": "Lay Waste explodes on a delay with more damage on an isolated target; Wall of Pain reduces the speed and magic resistance of those who cross it."},
            {"name": "The long-range ultimate", "when": "Enemies are weakened everywhere.",
             "how": "Requiem channels for 3 seconds then deals damage to all enemy champions: use it to finish several targets from a distance."},
            {"name": "Spirit form", "when": "You die in the middle of a fight.",
             "how": "Death Defied gives you a spirit form that lets you keep casting spells: take advantage of it to cast Requiem or Lay Waste."},
        ],
        "mistakes": [
            "Casting Requiem when the enemies are not within killing range.",
            "Using Defile out of need: it costs a lot of mana.",
            "Forgetting your spirit form.",
        ],
    },
    "Gnar": {
        "playstyle": (
            "Gnar is a fighter who alternates between small and Mega Gnar: his Rage fills as he fights, and when it is full, his next ability transforms him into Mega Gnar with better defenses and new abilities. "
            "Small, he throws a boomerang and hops; as Mega, he throws boulders, stuns with Wallop and knocks back all enemies with GNAR!."
        ),
        "laning": (
            "Catch your boomerang to reduce its cooldown. "
            "Hyper gives you damage and speed as you attack and cast abilities."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within boomerang range.",
             "how": "Boomerang Throw damages and slows; catch it to reduce its cooldown; Hyper adds damage and speed; Hop repositions you."},
            {"name": "The transformation", "when": "Your Rage gauge is full.",
             "how": "Your next ability transforms you into Mega Gnar: Wallop stuns, Crunch deals area damage."},
            {"name": "The team engage", "when": "Enemies are near a wall.",
             "how": "GNAR! knocks all nearby enemies in the targeted direction with damage and a slow; if they hit a wall, they are stunned and take bonus damage."},
        ],
        "mistakes": [
            "Using GNAR! with no wall or allies behind.",
            "Forgetting to catch the boomerang or the boulder.",
            "Transforming at the wrong time: Rage is spent.",
        ],
    },
    "Taliyah": {
        "playstyle": (
            "Taliyah is a terrain mage: her passive raises her speed near walls, and Threaded Volley creates worked ground that she consumes to throw a stronger boulder that slows. "
            "Seismic Shove knocks enemies back, Unraveled Earth traps with mines that stun, and Weaver's Wall creates a very long wall she surfs on."
        ),
        "laning": (
            "Cast Threaded Volley while moving freely: the worked ground gives an empowered version. "
            "Use Unraveled Earth to trap dashes."
        ),
        "combos": [
            {"name": "The boulder combo", "when": "An enemy is within range.",
             "how": "Threaded Volley creates worked ground, the second one consumes it for a boulder that slows; Seismic Shove knocks the target toward your mines."},
            {"name": "The trap", "when": "An enemy might dash.",
             "how": "Unraveled Earth creates a slowing minefield; if an enemy dashes or is knocked over it, the mines explode and stun them."},
            {"name": "The wall ultimate", "when": "You want to block a path or move fast.",
             "how": "Weaver's Wall creates a very long wall and lets you surf on it."},
        ],
        "mistakes": [
            "Casting Seismic Shove with no useful direction.",
            "Using the ultimate without knowing what it blocks or traps.",
            "Neglecting walls: they raise your speed.",
        ],
    },
    "Vayne": {
        "playstyle": (
            "Vayne is a marksman-assassin: her third consecutive attack or ability on the same target deals a percentage of max health as true damage. "
            "Tumble repositions her with bonus damage, Condemn knocks back and impales against terrain, and Final Hour raises her damage and makes her invisible during Tumble."
        ),
        "laning": (
            "Tumble between your attacks to reposition and deal damage. "
            "Attack the same target to trigger Silver Bolts on the third."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within range.",
             "how": "Tumble repositions you with bonus damage, the third consecutive attack triggers Silver Bolts with true damage based on max health."},
            {"name": "The impale", "when": "An enemy is near a wall.",
             "how": "Condemn fires a giant bolt that knocks the target back; if they hit the terrain, they are impaled, take bonus damage and are stunned."},
            {"name": "The final hour", "when": "A team fight begins.",
             "how": "Final Hour raises your attack damage, makes you invisible during Tumble and reduces its cooldown."},
        ],
        "mistakes": [
            "Switching targets: you lose the Silver Bolts progress.",
            "Using Condemn with no wall behind the target when there is one.",
            "Tumbling toward the enemies with no plan.",
        ],
    },
    "Quinn": {
        "playstyle": (
            "Quinn is a marksman-assassin who fights alongside Valor, her eagle: Harrier periodically marks enemies, and her first attack on a marked target deals bonus damage. "
            "Blinding Assault limits vision, Vault knocks her back after an impact, and Behind Enemy Lines makes her fly at high speed with Valor."
        ),
        "laning": (
            "Attack the target marked by Harrier first: your first attack deals bonus damage. "
            "Heightened Senses gives you attack and movement speed after attacking a marked target."
        ),
        "combos": [
            {"name": "The trade", "when": "An enemy is marked by Harrier.",
             "how": "Blinding Assault marks and limits vision before damaging nearby enemies; your attack on a marked target deals bonus damage; Vault damages, slows and sends you back."},
            {"name": "Scouting", "when": "You want vision.",
             "how": "Activating Heightened Senses makes Valor reveal a large area."},
            {"name": "The mobility ultimate", "when": "You want to cross the map.",
             "how": "Behind Enemy Lines makes you and Valor fly at high speed; ending the ability launches Skystrike, which damages nearby enemies and marks champions with Harrier."},
        ],
        "mistakes": [
            "Forgetting the Harrier mark.",
            "Using Vault without planning where you will end up.",
            "Casting the ultimate while placing yourself in the middle of the enemies.",
        ],
    },
    "DrMundo": {
        "playstyle": (
            "Dr. Mundo is a tank who resists the first immobilizing effect, at the cost of health and a canister he picks up to heal. "
            "Infected Bonesaw damages based on current health, Heart Zapper stores damage and returns it as healing, Blunt Force Trauma deals damage based on his missing health, and Maximum Dosage heals him instantly."
        ),
        "laning": (
            "Infected Bonesaw deals damage based on the target's current health: use it often to harass. "
            "Your health regeneration is very high: play with it."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within range.",
             "how": "Infected Bonesaw slows and deals damage based on current health; Blunt Force Trauma hits with bonus damage based on your missing health."},
            {"name": "The prolonged fight", "when": "You are surrounded by enemies.",
             "how": "Heart Zapper deals continuous damage and stores part of the damage taken, then returns it as healing at the end or on recast."},
            {"name": "The survival ultimate", "when": "You are at low health.",
             "how": "Maximum Dosage instantly recovers a percentage of your missing health, gives you speed and regenerates over a long duration."},
        ],
        "mistakes": [
            "Not picking up your passive's canister.",
            "Using Maximum Dosage at full health.",
            "Forgetting that the first immobilizing effect costs you health.",
        ],
    },
    "Xayah": {
        "playstyle": (
            "Xayah is a feather marksman: her abilities leave feathers, and Bladecaller recalls them to deal damage and root. "
            "After an ability, her next attacks hit every target in their path and leave a feather. Featherstorm makes her untargetable."
        ),
        "laning": (
            "Chain ability then attack so your attacks hit everything in their path. "
            "Place feathers on the enemies for your root."
        ),
        "combos": [
            {"name": "The root", "when": "An enemy is within range.",
             "how": "Double Daggers leave feathers, your attacks leave some too, Bladecaller recalls all the feathers to damage and root."},
            {"name": "The team fight", "when": "A fight begins.",
             "how": "Deadly Plumage raises your attack speed and damage, and your movement speed if you attack a champion."},
            {"name": "The ultimate", "when": "You are under threat.",
             "how": "Featherstorm makes you leap into the air, untargetable, while throwing daggers that leave feathers; recall them afterward."},
        ],
        "mistakes": [
            "Recalling your feathers with no enemies to root.",
            "Using the ultimate without checking where you will land.",
            "Neglecting the range of your attacks: they hit everything in their path.",
        ],
    },
    "Draven": {
        "playstyle": (
            "Draven is a marksman who lives on style: catching the Spinning Axe, killing minions or destroying turrets gives him Adoration, which converts into bonus gold when he kills a champion. "
            "Blood Rush raises his speeds, Stand Aside knocks back and slows, and Whirling Death executes enemies whose health is below his Adoration."
        ),
        "laning": (
            "Catch your axes: they are your source of Adoration and damage. "
            "You can have two Spinning Axes at the same time."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within range.",
             "how": "Spinning Axe deals bonus damage and ricochets; catch it to prepare another; Blood Rush ends its cooldown when you catch."},
            {"name": "The separation", "when": "An enemy dives you.",
             "how": "Stand Aside knocks the targets hit to the side and slows them."},
            {"name": "The execution", "when": "An enemy is low.",
             "how": "Whirling Death executes enemies whose health is below your accumulated Adoration; recast it to make the axes return sooner."},
        ],
        "mistakes": [
            "Missing an axe: you lose Adoration and damage.",
            "Using the ultimate without recasting it when useful.",
            "Neglecting Adoration: it decides the execution.",
        ],
    },
    "Teemo": {
        "playstyle": (
            "Teemo is a harassment marksman-mage: his passive makes him invisible indefinitely if he stands still, and in tall grass he can move while staying invisible. "
            "Blinding Dart blinds, Move Quick speeds him up, Toxic Shot poisons for 4 seconds, and Noxious Trap places mushrooms that slow and damage."
        ),
        "laning": (
            "Blind with Blinding Dart to stop your opponent from attacking you. "
            "When you leave invisibility, your Element of Surprise raises your attack speed."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within range.",
             "how": "Blinding Dart deals damage and blinds; your attacks poison the target for 4 seconds."},
            {"name": "The ambush", "when": "You are coming out of tall grass.",
             "how": "Leave your invisibility to benefit from the Element of Surprise (attack speed raised for a few seconds), then blind and attack."},
            {"name": "Area control", "when": "Enemies are approaching a chokepoint.",
             "how": "Noxious Trap throws a mushroom: if an enemy steps on it, a poison cloud slows and damages them; thrown onto another mushroom, it bounces with more range."},
        ],
        "mistakes": [
            "Staying visible when you could hide.",
            "Placing mushrooms without hiding them.",
            "Ignoring the Element of Surprise: it is your damage window.",
        ],
    },
}
