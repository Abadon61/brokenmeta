"""English guides, batch 15 (includes the extras for Fiddlesticks, Tahm Kench, Kennen, Neeko, Vex, Renata, Lillia)."""

EN = {
    "XinZhao": {
        "playstyle": (
            "Xin Zhao is a duel jungler: every 3 attacks he deals bonus damage and heals. "
            "Three Talon Strike knocks up on the 3rd attack, Wind Becomes Lightning slows and marks as challenged, Audacious Charge has more range against challenged enemies, and Crescent Guard protects him from champions outside the circle."
        ),
        "laning": (
            "Chain attacks in threes to benefit from your passive and Three Talon Strike. "
            "A challenged enemy is easier to reach with Audacious Charge."
        ),
        "combos": [
            {"name": "The trade", "when": "An enemy is within charge range.",
             "how": "Wind Becomes Lightning marks as challenged while slowing, Audacious Charge charges with more range, Three Talon Strike: the 3rd attack knocks up."},
            {"name": "The duel", "when": "You are fighting a single champion.",
             "how": "Crescent Guard deals damage based on the current health of nearby enemies, pushes back the non-challenged and makes you immune to damage from champions outside the circle."},
            {"name": "The chase", "when": "A challenged enemy is fleeing.",
             "how": "Audacious Charge has increased range against challenged enemies and raises your attack speed."},
        ],
        "mistakes": [
            "Using the ultimate in the middle of a team brawl: its defensive effects are against champions outside the circle.",
            "Not counting your attacks: your passive triggers every 3 hits.",
            "Charging without having marked with Wind Becomes Lightning.",
        ],
    },
    "Fiddlesticks": {
        "playstyle": (
            "Fiddlesticks is a terror jungler: Terrify makes an enemy flee if he damages them while not visible, Bountiful Harvest drains with bonus execute damage, Reap slows and silences at the center, and Crowstorm deals damage per second in the area. "
            "His passive replaces his trinket with Scarecrow Effigies."
        ),
        "laning": (
            "Hide before attacking: Terrify works if you damage while not visible. "
            "The Scarecrow Effigies let you appear by surprise."
        ),
        "strengths": [
            "Terrify makes an enemy flee when you damage them without being visible: a very surprising engage.",
            "Crowstorm deals damage per second to all enemy units in the area.",
            "Reap slows every enemy hit and silences those at the center.",
        ],
        "weaknesses": [
            "Depends on invisibility: an enemy who reveals your position makes you lose Terrify's effect.",
            "Bountiful Harvest and Crowstorm require staying in the area while they work.",
            "Little mobility once engaged: without surprise, you are exposed.",
        ],
        "teamfight": (
            "Fiddlesticks enters the fight by surprise, from a bush or a zone with no vision, then chains Terrify, Reap and Crowstorm in the middle of the enemies. "
            "His ultimate makes him a constant source of damage as long as he is not interrupted: his team has to protect his channel."
        ),
        "combos": [
            {"name": "The ambush", "when": "You are hidden near an enemy.",
             "how": "Terrify makes the enemy flee, Reap slows and silences the enemies at the center, Bountiful Harvest drains with execute damage."},
            {"name": "The area ultimate", "when": "Enemies are grouped.",
             "how": "Crowstorm whirls around you, dealing damage per second to all enemy units in the area."},
            {"name": "The drain", "when": "An enemy is isolated.",
             "how": "Bountiful Harvest drains the life essence and deals bonus execute damage at the end of the effect."},
            {"name": "The team-fight engage", "when": "Your team is ready and the enemies are grouped.",
             "how": "Crowstorm creates a zone of damage per second, Reap slows and silences at the center, Terrify and Bountiful Harvest add control and execute damage."},
        ],
        "mistakes": [
            "Showing yourself before Terrify.",
            "Casting the ultimate without preparation.",
            "Using Bountiful Harvest without being able to finish it.",
        ],
    },
    "TahmKench": {
        "playstyle": (
            "Tahm Kench is a support-tank whose damage increases with his total health. "
            "Tongue Lash slows and applies An Acquired Taste (at 3 stacks, it stuns and can be followed by Devour), Abyssal Dive knocks up, Thick Skin stores damage for a shield, and Devour swallows a champion: magic damage or a shield for an ally."
        ),
        "laning": (
            "Apply 3 stacks of An Acquired Taste to stun with Tongue Lash. "
            "Thick Skin: activate it to convert the stored damage into a temporary shield."
        ),
        "strengths": [
            "His damage increases with his total health, which makes him effective as a tank.",
            "Tongue Lash applies An Acquired Taste: at 3 stacks, it stuns.",
            "Devour protects an ally by taking them to safety or swallows an affected enemy.",
        ],
        "weaknesses": [
            "Devour requires 3 stacks of An Acquired Taste on an enemy.",
            "Little damage without health.",
            "Thick Skin only really protects with stored damage to consume.",
        ],
        "teamfight": (
            "Tahm Kench chooses between protecting and attacking: swallowing an ally takes them out of a control, swallowing an enemy separates them from their team. "
            "Abyssal Dive helps him join the brawl or leave it."
        ),
        "combos": [
            {"name": "The stun", "when": "An enemy is within range.",
             "how": "Tongue Lash applies a stack of An Acquired Taste; at 3 stacks, the champion is stunned and the stacks are consumed."},
            {"name": "The engage", "when": "An enemy is far away.",
             "how": "Abyssal Dive makes you dive then reappear at the targeted spot, damaging and knocking up enemies; Devour swallows an enemy champion (3 stacks required)."},
            {"name": "Protecting an ally", "when": "An ally is under threat.",
             "how": "Devour on an ally gives them a shield for a few seconds; Thick Skin protects you too."},
            {"name": "The ally rescue", "when": "An ally is targeted by an engage.",
             "how": "Abyssal Dive brings you to the ally, Devour gives them a shield for a few seconds, Thick Skin converts your stored damage into a temporary shield."},
        ],
        "mistakes": [
            "Using Devour on an enemy without having the 3 stacks.",
            "Not converting your stored damage into a shield.",
            "Using Abyssal Dive with no direction.",
        ],
    },
    "Kennen": {
        "playstyle": (
            "Kennen is an energy mage whose passive stuns enemies hit 3 times by his abilities. "
            "Thundering Shuriken adds a Mark of the Storm, Electrical Surge passively adds some, Lightning Rush turns him into a ball of electricity, and Slicing Maelstrom hits nearby enemy champions."
        ),
        "laning": (
            "Hit three times to stun: Shuriken, Electrical Surge, Lightning Rush apply marks. "
            "Your energy limits your abilities: do not overuse them."
        ),
        "strengths": [
            "Stuns enemies hit three times by his abilities (Mark of the Storm).",
            "Lightning Rush gives him speed and lets him pass through units while applying marks.",
            "Slicing Maelstrom hits all nearby enemy champions with magic damage.",
        ],
        "weaknesses": [
            "Limited by his energy: his abilities repeat less quickly than a mana mage's.",
            "Has to get close to use Slicing Maelstrom.",
            "Fragile when he has no stun ready.",
        ],
        "teamfight": (
            "Kennen enters with Lightning Rush to apply marks on several enemies at once, completes with Shuriken and Electrical Surge to trigger the stuns, "
            "then casts Maelstrom to finish. His role is to control several targets with a single series of marks."
        ),
        "combos": [
            {"name": "The stun", "when": "An enemy is within range.",
             "how": "Thundering Shuriken adds a mark, Electrical Surge another, Lightning Rush a third: at 3 marks, the enemy is stunned."},
            {"name": "The team engage", "when": "Several enemies are close.",
             "how": "Lightning Rush lets you pass through units while applying marks; Slicing Maelstrom summons a storm that hits nearby enemy champions."},
            {"name": "Harassment", "when": "An enemy is in lane.",
             "how": "Electrical Surge passively adds marks every few attacks."},
            {"name": "The series of marks", "when": "Several enemies are close.",
             "how": "Lightning Rush applies a mark to each enemy crossed, Electrical Surge and Thundering Shuriken add some: at three marks, they are stunned; Slicing Maelstrom then hits the nearby champions."},
        ],
        "mistakes": [
            "Using your abilities without counting the marks.",
            "Casting the ultimate without several enemies nearby.",
            "Neglecting your energy.",
        ],
    },
    "Urgot": {
        "playstyle": (
            "Urgot is a ranged-melee fighter: his attacks and Purge make jets of flame burst from his legs, dealing physical damage. "
            "Corrosive Charge slows, Purge prioritizes recently hit champions, Disdain dashes him with a shield, and Fear Beyond Death impales then executes below a certain health threshold."
        ),
        "laning": (
            "Purge prioritizes enemy champions you recently hit with other abilities. "
            "Corrosive Charge slows in the area."
        ),
        "combos": [
            {"name": "The trade", "when": "An enemy is within range.",
             "how": "Corrosive Charge slows, Purge unloads on the marked enemy, your attacks trigger Echoing Flames, Disdain gives you a shield."},
            {"name": "The execution", "when": "A champion is low.",
             "how": "Fear Beyond Death fires a drill that impales the first champion hit: below a certain health threshold, you can execute them."},
            {"name": "The charge", "when": "You want to close in.",
             "how": "Disdain dashes you while giving you a shield and tramples the enemies on your path (except champions); if it hits a champion, it knocks them out of your way."},
        ],
        "mistakes": [
            "Using the ultimate without the execution threshold reached.",
            "Casting Purge without a prior slow.",
            "Forgetting that Disdain stops on a champion.",
        ],
    },
    "Maokai": {
        "playstyle": (
            "Maokai is a control tank-support: his basic attack heals and deals bonus damage, with a cooldown reduced by every ability cast or taken. "
            "Bramble Smash pushes back and slows, Twisted Advance roots on arrival, Sapling Toss watches an area, and Nature's Grasp advances slowly while rooting."
        ),
        "laning": (
            "Cast abilities to recharge your passive. "
            "Sapling Toss is more effective in tall grass."
        ),
        "combos": [
            {"name": "The engage", "when": "A carry is within range.",
             "how": "Twisted Advance makes you untargetable and dashes you onto the target, whom it roots on arrival; Bramble Smash pushes back and slows."},
            {"name": "Area control", "when": "You are defending an objective.",
             "how": "Sapling Toss watches an area; Nature's Grasp summons a wall of thorns that advances slowly, damaging and rooting the enemies."},
            {"name": "Sustain", "when": "You are engaged.",
             "how": "Your passive restores health with your basic attack; each ability reduces its cooldown."},
        ],
        "mistakes": [
            "Casting the ultimate with no direction.",
            "Forgetting your passive's attack.",
            "Using Twisted Advance with no target.",
        ],
    },
    "Neeko": {
        "playstyle": (
            "Neeko is a chameleon mage-support: her passive lets her take on the appearance of an ally or a unit, until she is immobilized, casts an offensive ability or takes damage. "
            "Blooming Burst blooms twice, Shapesplitter sends a clone, Tangle-Barbs roots, and Pop Blossom knocks up then stuns."
        ),
        "laning": (
            "Disguised, you can surprise: the wind-up of your ultimate cannot be seen if you are disguised. "
            "Blooming Burst blooms again if it hits a champion or kills."
        ),
        "strengths": [
            "Her disguise lets her approach without being identified, and the wind-up of her ultimate is invisible while disguised.",
            "Tangle-Barbs roots several enemies and grows if it passes through a champion or kills.",
            "Pop Blossom knocks up then stuns every nearby enemy.",
        ],
        "weaknesses": [
            "The disguise breaks if she is immobilized, casts an offensive ability or takes enough damage.",
            "Her abilities have long cooldowns (Shapesplitter 16 s, Pop Blossom 120 s).",
            "Fragile: without her engage, she has no escape.",
        ],
        "teamfight": (
            "Neeko approaches disguised, casts her ultimate to knock up and stun every nearby enemy, then roots the runners with Tangle-Barbs. "
            "A single successful engage can decide the fight, but she gets no second chance if the ultimate is missed."
        ),
        "combos": [
            {"name": "The disguised ambush", "when": "You are disguised near the enemies.",
             "how": "Pop Blossom: the wind-up is invisible if you are disguised, you leap knocking up and on landing you damage and stun; Tangle-Barbs then roots."},
            {"name": "Harassment", "when": "An enemy is within range.",
             "how": "Blooming Burst damages and blooms a second time; every 3 attacks, Shapesplitter deals bonus damage and speeds you up."},
            {"name": "The root", "when": "An enemy is isolated.",
             "how": "Tangle-Barbs roots every enemy it crosses; if it kills or passes through a champion, it grows and the root lasts longer."},
            {"name": "The disguised trap", "when": "You are disguised as an ally and the enemies are grouped.",
             "how": "Pop Blossom: its wind-up cannot be seen when disguised; nearby enemies are knocked up then damaged and stunned on landing; follow with Tangle-Barbs and Blooming Burst."},
        ],
        "mistakes": [
            "Breaking your disguise before the engage.",
            "Casting Tangle-Barbs with no trajectory.",
            "Forgetting the clone's recast.",
        ],
    },
    "Vex": {
        "playstyle": (
            "Vex is a counter-mobility mage: her passive empowers her regularly so that her next basic ability terrifies and interrupts dashes. "
            "Every dash by a nearby enemy gives her a consumable mark for bonus damage and a reduced cooldown. Shadow Surge marks then makes her dash onto the enemy."
        ),
        "laning": (
            "Wait until your empowerment is ready to terrify. "
            "Looming Darkness slows and applies Despair."
        ),
        "strengths": [
            "Her passive terrifies and interrupts dashes: it is a direct answer to assassins and engages.",
            "Every enemy dash gives her a mark that deals bonus damage and reduces the cooldown of her empowerment.",
            "Shadow Surge marks from afar and can be recast to dash onto the target.",
        ],
        "weaknesses": [
            "Against champions with no dash, she benefits less from her marks.",
            "Her empowerment is periodic: wasting it has a cost.",
            "Fragile against quick bursts if her shield is not ready.",
        ],
        "teamfight": (
            "Vex protects her team from engages: her empowered ability terrifies the diving enemy, Personal Space gives her a shield, and Shadow Surge lets her finish a marked carry. "
            "She is very effective against compositions that rely on dashes."
        ),
        "combos": [
            {"name": "The anti-dash", "when": "An enemy dashes.",
             "how": "Your empowered ability terrifies and interrupts the dash; the applied mark deals bonus damage if consumed."},
            {"name": "The hunting ultimate", "when": "A carry is visible.",
             "how": "Shadow Surge marks a champion then is recast to dash onto them and deal damage."},
            {"name": "Defense", "when": "An enemy dives.",
             "how": "Personal Space gives you a shield and damages nearby enemies; Looming Darkness slows and applies Despair."},
            {"name": "The riposte to an engage", "when": "An enemy dives you or your carry.",
             "how": "Personal Space gives you a shield and damages nearby enemies, your empowered ability terrifies and interrupts the dash, Looming Darkness slows and applies Despair."},
        ],
        "mistakes": [
            "Wasting your passive empowerment.",
            "Casting the ultimate on a target who can flee.",
            "Neglecting the marks: they reduce the empowerment's cooldown.",
        ],
    },
    "Kayle": {
        "playstyle": (
            "Kayle is a fighter who scales: her wings ignite with her levels and skill points, giving her attack speed, movement speed, range and waves of fire. "
            "Radiant Blast passes through and reduces resistances, Celestial Blessing heals, Starfire Spellblade empowers her, and Divine Judgment makes an ally invulnerable."
        ),
        "laning": (
            "Survive the laning phase: your power comes from your levels. "
            "Starfire Spellblade deals bonus damage based on the target's missing health."
        ),
        "combos": [
            {"name": "The trade", "when": "An enemy is within range.",
             "how": "Radiant Blast slows, damages and reduces resistances; Starfire Spellblade unleashes celestial fire on your next attack."},
            {"name": "Protection", "when": "An ally is under threat.",
             "how": "Celestial Blessing heals you and the nearest ally with a speed bonus; Divine Judgment makes an ally invulnerable."},
            {"name": "The team fight", "when": "A decisive fight begins.",
             "how": "Divine Judgment drops a rain of purifying swords around its target while the ally is invulnerable."},
        ],
        "mistakes": [
            "Trying to kill before you have your key levels.",
            "Using the ultimate on an ally who is not the target.",
            "Neglecting Starfire Spellblade: it adds damage based on missing health.",
        ],
    },
    "Renata": {
        "playstyle": (
            "Renata Glasc is a control support: her attacks mark enemies, and her allies deal bonus damage to marked enemies. "
            "Handshake roots and throws, Bailout delays an ally's death, Loyalty Program protects and slows, and Hostile Takeover drives the enemies it hits into a frenzy."
        ),
        "laning": (
            "Mark the enemy with your attacks so your carry deals more damage. "
            "Handshake can be recast to throw the enemy."
        ),
        "strengths": [
            "Her attacks mark enemies and her allies deal bonus damage to them.",
            "Bailout delays an ally's death and lets them survive if they take part in a takedown.",
            "Hostile Takeover turns the enemies against each other.",
        ],
        "weaknesses": [
            "Depends on the presence of allies to benefit from her marks.",
            "Handshake has a long cooldown (16 s) and is cast blind.",
            "Bailout has a 24 to 28 s cooldown: choose the ally well.",
        ],
        "teamfight": (
            "Renata controls the engage: she roots an enemy or sends them toward her allies, protects her carry with Bailout and Loyalty Program, "
            "then triggers Hostile Takeover when the enemies are grouped. Her marks raise her allies' damage on the target."
        ),
        "combos": [
            {"name": "The pick", "when": "An enemy is isolated.",
             "how": "Handshake roots the first enemy hit; recast it to throw them in a direction; Loyalty Program slows and protects."},
            {"name": "Protection", "when": "An ally is about to die.",
             "how": "Bailout delays the ally's death and lets them survive if they take part in a champion takedown."},
            {"name": "The chaos ultimate", "when": "Enemies are grouped.",
             "how": "Hostile Takeover sends a cloud that drives every enemy it hits into a frenzy."},
            {"name": "The team fight", "when": "Enemies are grouping on your carry.",
             "how": "Hostile Takeover drives the enemies it hits into a frenzy, Loyalty Program protects and slows, Bailout extends the life of a key ally, Handshake roots a threat."},
        ],
        "mistakes": [
            "Using Bailout on an ally who cannot take part in the takedown.",
            "Casting the ultimate with no grouped targets.",
            "Forgetting to mark the enemies.",
        ],
    },
    "Lillia": {
        "playstyle": (
            "Lillia is a jungler who runs: hitting a champion or a monster with an ability deals damage over time based on their max health. "
            "Blooming Blows gives her stacking movement speed, Watch Out! Eep! hits hard at the center, Swirlseed slows, and Lilting Lullaby puts enemies affected by Dream Dust to sleep."
        ),
        "laning": (
            "Hit with your abilities to stack movement speed with Blooming Blows. "
            "Watch Out! Eep! deals heavy damage at the center of the area."
        ),
        "strengths": [
            "Her abilities deal damage over time based on the max health of the targets hit.",
            "Blooming Blows gives her stacking movement speed to chase or flee.",
            "Lilting Lullaby puts enemies affected by Dream Dust to sleep, with bonus damage if they are forcibly woken.",
        ],
        "weaknesses": [
            "Has to hit with her abilities to stack her speed and her Dream Dust.",
            "Watch Out! Eep! deals its big damage at the center: poor positioning reduces it.",
            "Her ultimate is useless without enemies affected by her passive.",
        ],
        "teamfight": (
            "Lillia enters a fight running, applies her Dream Dust with her abilities, then casts Lilting Lullaby to put every marked enemy to sleep. "
            "Her team should avoid waking the sleeping targets too early, except to take advantage of the bonus damage."
        ),
        "combos": [
            {"name": "The basic combo", "when": "An enemy is within range.",
             "how": "Swirlseed damages and slows, Watch Out! Eep! hits at the center, Blooming Blows deals area damage (true at the edge); your passive deals damage over time."},
            {"name": "The sleep ultimate", "when": "Several enemies are marked.",
             "how": "Lilting Lullaby causes drowsiness in all the enemies affected by Dream Dust, who eventually fall asleep; they take bonus damage if forcibly woken."},
            {"name": "The chase", "when": "You want to run toward a target.",
             "how": "Blooming Blows gives you stacking speed bonuses when your abilities hit."},
            {"name": "The area run", "when": "You want to run toward a group of enemies.",
             "how": "Blooming Blows stacks speed when your abilities hit, Swirlseed slows, Watch Out! Eep! hits at the center, then the active Blooming Blows deals area damage."},
        ],
        "mistakes": [
            "Casting the ultimate without having hit any Dream Dust.",
            "Not aiming at the center with Watch Out! Eep!",
            "Standing still: your strength comes from your speed.",
        ],
    },
}
