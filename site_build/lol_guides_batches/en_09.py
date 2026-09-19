"""English guides, batch 9."""

EN = {
    "Anivia": {
        "playstyle": (
            "Anivia is an area-control mage: Flash Frost freezes and damages everything in its path then stuns when it explodes, Crystallize creates an impassable wall of ice, and Glacial Storm damages and slows over an area. "
            "Her passive makes her be reborn as an egg with full health when she takes lethal damage."
        ),
        "laning": (
            "Frostbite deals double damage if the target was recently hit by Flash Frost or a fully grown Glacial Storm. "
            "Use Crystallize to block a path or protect an ally."
        ),
        "combos": [
            {"name": "The basic combo", "when": "An enemy is within Flash Frost range.",
             "how": "Flash Frost freezes and damages everything in its path, then explodes, stunning nearby enemies; Frostbite deals double damage to a recently hit target."},
            {"name": "Area control", "when": "Enemies are advancing on your team.",
             "how": "Crystallize blocks the path for a short time before melting; place Glacial Storm to damage and slow those waiting."},
            {"name": "The second life", "when": "You are at low health.",
             "how": "Rebirth turns you into an egg and brings you back to life with full health: the fight is not over."},
        ],
        "mistakes": [
            "Casting Frostbite without hitting first: you lose the double damage.",
            "Placing Crystallize too late: its duration is short.",
            "Leaving your egg unprotected: it can be destroyed.",
        ],
    },
    "MissFortune": {
        "playstyle": (
            "Miss Fortune is an area marksman: her passive deals bonus damage when she attacks a new target, Double Up hits two lined-up enemies, Make It Rain slows and damages in waves, and Bullet Time unleashes a barrage in a cone. "
            "Each wave of the ultimate can critically strike."
        ),
        "laning": (
            "Switch targets to trigger Love Tap every time. "
            "Double Up damages the target then the one behind: use a minion to hit a champion behind it."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is behind a minion.",
             "how": "Double Up fires at the minion to reach the champion behind it, both hits can apply Love Tap; Make It Rain slows."},
            {"name": "The team fight", "when": "Enemies are grouped in your line.",
             "how": "Make It Rain slows and damages in waves, Bullet Time deals heavy damage in a cone: position yourself so the cone covers several enemies."},
            {"name": "Mobility", "when": "You want to hit fast or flee.",
             "how": "Strut passively raises your speed when not attacking and gives attack speed when activated; Love Tap reduces its cooldown."},
        ],
        "mistakes": [
            "Casting the ultimate with no protection: it is a channel.",
            "Always attacking the same target: you lose Love Tap.",
            "Forgetting that Double Up passes through: position yourself to hit both.",
        ],
    },
    "Braum": {
        "playstyle": (
            "Braum is a support-tank whose attacks apply Concussive Blows: his allies' attacks apply them too, and at 4 stacks the target is stunned and takes magic damage. "
            "Unbreakable raises his shield to intercept projectiles, Stand Behind Me makes him leap to an ally, and his ultimate knocks up then slows along a line."
        ),
        "laning": (
            "Apply Concussive Blows with Winter's Bite and your attacks: your allies trigger the effect too, so coordinate with your carry. "
            "Point Unbreakable toward enemy projectiles."
        ),
        "combos": [
            {"name": "The stun", "when": "Your carry attacks the same target.",
             "how": "Winter's Bite applies a stack, each attack from Braum or an ally adds one; at 4 stacks, the target is stunned and takes magic damage."},
            {"name": "Protection", "when": "Your carry is threatened by projectiles.",
             "how": "Stand Behind Me leaps you to them to give armor and magic resistance to you both; Unbreakable intercepts projectiles and completely blocks the first attack."},
            {"name": "The engage ultimate", "when": "Enemies are grouping.",
             "how": "Glacial Fissure knocks up nearby enemies and those on the line, then the fissure slows them."},
        ],
        "mistakes": [
            "Forgetting that your allies also trigger Concussive Blows.",
            "Pointing Unbreakable the wrong way: it only protects in the chosen direction.",
            "Using the ultimate without coordinating your team.",
        ],
    },
    "Varus": {
        "playstyle": (
            "Varus is a ranged marksman-mage: his passive gives him attack damage and power after a kill or an assist, more on a champion. "
            "Piercing Arrow charges for more damage and range, Blighted Quiver applies Blight (damage based on max health), Hail of Arrows blights the ground, and Chain of Corruption roots and spreads."
        ),
        "laning": (
            "Your attacks apply Blight: your other abilities trigger it and deal damage based on the target's max health. "
            "Charge your Piercing Arrow for more range and damage."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within range.",
             "how": "Blighted Quiver empowers your next Piercing Arrow and your attacks apply Blight; abilities trigger Blight for damage based on max health."},
            {"name": "The blighted zone", "when": "Enemies are near a chokepoint.",
             "how": "Hail of Arrows deals physical damage and blights the ground: movement speed, healing and regeneration are reduced."},
            {"name": "The team engage", "when": "An enemy carry is visible.",
             "how": "Chain of Corruption damages and roots the first champion hit and spreads to nearby uninfected champions, rooting them too."},
        ],
        "mistakes": [
            "Releasing Piercing Arrow with no charge: damage and range increase with charge.",
            "Not using Blight: it makes up a large part of your damage.",
            "Casting the ultimate without its nearby targets being caught.",
        ],
    },
    "Diana": {
        "playstyle": (
            "Diana is a fighter-assassin whose passive strikes in an area every third hit and raises her attack speed for 5 seconds after each ability. "
            "Crescent Strike reveals with Moonlight, Lunar Rush has no cooldown on an affected enemy, and Moonfall pulls in all nearby enemies."
        ),
        "laning": (
            "Hit with Crescent Strike: Moonlight lets Lunar Rush reset. "
            "Pale Cascade gives you a shield; empowered if all three orbs explode."
        ),
        "combos": [
            {"name": "The basic combo", "when": "An enemy is within Crescent range.",
             "how": "Crescent Strike applies Moonlight, Lunar Rush dashes you onto the affected target with no delay, Pale Cascade gives damage and a shield, your attacks benefit from the attack speed."},
            {"name": "The team engage", "when": "Several enemies are grouped.",
             "how": "Moonfall reveals and pulls in nearby enemies then slows them; if you pull in a champion, the moonlight falls on you with damage increased per secondary target."},
            {"name": "The chase", "when": "You are chasing marked enemies.",
             "how": "Lunar Rush has no cooldown on an enemy affected by Moonlight; every other enemy loses the effect, even if not targeted."},
        ],
        "mistakes": [
            "Casting Lunar Rush on a target without Moonlight.",
            "Using the ultimate with no champion to pull in.",
            "Forgetting that Lunar Rush removes Moonlight from other enemies.",
        ],
    },
    "Swain": {
        "playstyle": (
            "Swain is a mage who grows: his ravens collect soul fragments that heal him and permanently increase his max health. "
            "Death's Hand deals more damage with the number of projectiles, Vision of Empire slows and reveals, Nevermove roots and pulls, and Demonic Ascension drains the health of nearby enemies."
        ),
        "laning": (
            "Vision of Empire damages, slows and gives a soul fragment if it hits a champion. "
            "Death's Hand passes through enemies: the more projectiles hit, the more the damage increases."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within range.",
             "how": "Vision of Empire damages, slows and reveals the champions hit (a soul fragment as a bonus), Death's Hand deals increasing damage."},
            {"name": "The capture", "when": "An enemy is isolated.",
             "how": "Nevermove fires a wave that returns and roots the enemies hit; recast it to pull every rooted champion toward you."},
            {"name": "Demon form", "when": "A team fight begins.",
             "how": "Demonic Ascension transforms you and drains the health of nearby enemies; Demonic Eruption decimates and slows, and the form lasts as long as you drain enemy champions."},
        ],
        "mistakes": [
            "Using Nevermove without knowing whom to pull in.",
            "Casting the ultimate outside the fight: it drains nearby enemies.",
            "Neglecting soul fragments: they increase your max health.",
        ],
    },
    "Cassiopeia": {
        "playstyle": (
            "Cassiopeia is a mage who benefits from movement speed, which is more effective on her. "
            "Noxious Blast damages, raises her speed and poisons, Miasma slows and grounds the enemies who cross it, Twin Fang deals more damage to poisoned targets and heals her, and Petrifying Gaze stuns those facing her."
        ),
        "laning": (
            "Poison with Noxious Blast then Twin Fang: it deals more damage and heals you. "
            "If Twin Fang kills its target, you regain mana."
        ),
        "combos": [
            {"name": "The poison combo", "when": "An enemy is within range.",
             "how": "Noxious Blast poisons after a short delay and speeds you up if it hits a champion, then Twin Fang deals more damage to poisoned targets."},
            {"name": "The facing ultimate", "when": "Several enemies are facing you.",
             "how": "Petrifying Gaze stuns those facing you and slows those turning their back: position yourself so they look toward you."},
            {"name": "Anti-mobility", "when": "An enemy uses movement abilities.",
             "how": "Miasma grounds those crossing the clouds: they cannot use movement abilities."},
        ],
        "mistakes": [
            "Casting the ultimate with your back to the enemies: they are only slowed.",
            "Using Twin Fang without poison.",
            "Placing Miasma without using its grounding effect.",
        ],
    },
    "Sivir": {
        "playstyle": (
            "Sivir is a bounce and tempo marksman: Boomerang Blade damages on the way out and back, Ricochet makes her attacks bounce with bonus attack speed, Spell Shield blocks an enemy ability and her ultimate speeds up her allies. "
            "Her attacks then reduce her cooldowns."
        ),
        "laning": (
            "Boomerang Blade hits on the way out and back: position yourself so both passes count. "
            "Spell Shield blocks an enemy ability and heals you if it is blocked."
        ),
        "combos": [
            {"name": "Harassment", "when": "Several targets are close.",
             "how": "Boomerang Blade deals damage on the way out and back, Ricochet gives attack speed and makes your attacks bounce (reduced damage on bounces)."},
            {"name": "Protection", "when": "An enemy is about to cast a decisive ability.",
             "how": "Spell Shield blocks an enemy ability, heals you and gives you a brief speed bonus if it is blocked."},
            {"name": "The team ultimate", "when": "Your team engages or chases.",
             "how": "On The Hunt temporarily raises your allies' speed and your attacks reduce your abilities' cooldowns."},
        ],
        "mistakes": [
            "Using Spell Shield too early: keep it for the right ability.",
            "Throwing Boomerang Blade without looking at its return.",
            "Bouncing attacks off minions when you can hit a champion.",
        ],
    },
    "Fiora": {
        "playstyle": (
            "Fiora is a duelist who reveals her opponents' weak points: hitting them heals her and gives her speed. "
            "Lunge dashes her in, Riposte parries all damage and crowd control targeting her before counterattacking, Bladework raises her attack speed with a critical strike, and Grand Challenge reveals all four weak points."
        ),
        "laning": (
            "Hit the revealed weak point to heal and gain speed. "
            "Keep Riposte to parry a decisive ability: it blocks all damage and crowd control."
        ),
        "combos": [
            {"name": "The trade", "when": "An enemy is within Lunge range.",
             "how": "Lunge dashes you onto the weak point, Bladework gives attack speed with a slow then a critical strike."},
            {"name": "The parry", "when": "An enemy casts a decisive ability.",
             "how": "Riposte parries all damage and crowd control targeting you, then thrusts to slow; it stuns if you parried an immobilizing effect."},
            {"name": "The duel", "when": "You are fighting a single champion.",
             "how": "Grand Challenge reveals all four weak points and speeds you up near them; if you hit all four or the opponent dies after you hit one, you and your allies in the area are healed."},
        ],
        "mistakes": [
            "Using Riposte without knowing which ability to parry.",
            "Ignoring the weak point: it is your source of healing.",
            "Casting Grand Challenge on an enemy accompanied by many allies.",
        ],
    },
    "MasterYi": {
        "playstyle": (
            "Master Yi is a melee jungler who wins through speed: Double Strike hits twice after several consecutive attacks, Alpha Strike makes him untargetable, Wuju Style adds true damage, and Highlander gives him speed and immunity to slows. "
            "Killing or assisting extends Highlander and reduces his abilities' cooldowns."
        ),
        "laning": (
            "Attack with Alpha Strike: basic attacks reduce its cooldown. "
            "Meditate heals you every second and stacks Double Strike."
        ),
        "combos": [
            {"name": "The engage", "when": "A carry is within range.",
             "how": "Highlander raises your movement and attack speed and makes you immune to slows; Alpha Strike makes you untargetable, Wuju Style adds true damage."},
            {"name": "The clean-up", "when": "Your team is winning the fight.",
             "how": "Every takedown or assist reduces your abilities' cooldowns and extends Highlander: chain Alpha Strike from target to target."},
            {"name": "Recovery", "when": "You are at low health.",
             "how": "Meditate regenerates your health every second, briefly reduces the damage you take and pauses the remaining duration of Wuju Style and Highlander."},
        ],
        "mistakes": [
            "Using Alpha Strike with no target or no exit plan.",
            "Casting Highlander too early: its duration is limited.",
            "Not chaining your attacks: Double Strike depends on them.",
        ],
    },
}
