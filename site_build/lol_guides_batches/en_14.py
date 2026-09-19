"""English guides, batch 14 (Volibear includes the extras: strengths / weaknesses / teamfight, and its 4th combo)."""

EN = {
    "KogMaw": {
        "playstyle": (
            "Kog'Maw is a max-health damage marksman: Bio-Arcane Barrage increases his range and makes him deal magic damage equal to a percentage of the target's max health. "
            "Caustic Spittle corrodes armor and magic resistance, Void Ooze slows, and Living Artillery deals greatly increased damage against low-health enemies. His passive makes him explode 4 seconds after death."
        ),
        "laning": (
            "Caustic Spittle also gives you attack speed. "
            "Activate Bio-Arcane Barrage when you can attack safely: it increases your range."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within range.",
             "how": "Caustic Spittle corrodes armor and magic resistance and gives you attack speed; Bio-Arcane Barrage increases your range and your damage based on max health."},
            {"name": "Area control", "when": "An enemy approaches.",
             "how": "Void Ooze damages and leaves a trail that slows; Living Artillery fires at long range with greatly increased damage against low-health enemies."},
            {"name": "The explosive death", "when": "You are about to die.",
             "how": "Icathian Surprise makes you explode 4 seconds after your death, dealing true damage to nearby enemies: keep firing."},
        ],
        "mistakes": [
            "Spamming Living Artillery: the mana cost increases.",
            "Being within reach of melee with no defense plan.",
            "Forgetting your increased range with Bio-Arcane Barrage.",
        ],
    },
    "Smolder": {
        "playstyle": (
            "Smolder is a draconic marksman-mage: hitting champions with an ability and killing enemies with Super Scorcher Breath gives him Dragon Practice stacks that raise the damage of his basic abilities. "
            "Achooo! explodes on champions, Flap, Flap, Flap makes him fly while bombarding the enemy with the lowest health, and MMOOOMMMM! calls his mother for a slowing fire."
        ),
        "laning": (
            "Take kills with Super Scorcher Breath: they earn you stacks. "
            "Achooo! explodes if it hits enemy champions."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within range.",
             "how": "Super Scorcher Breath becomes more powerful with accumulated stacks; Achooo! explodes on the champions hit."},
            {"name": "The bombardment flight", "when": "You want to get past obstacles.",
             "how": "Flap, Flap, Flap makes you fly, ignoring obstacles, and bombard the enemy with the lowest health."},
            {"name": "The team ultimate", "when": "A fight begins.",
             "how": "MMOOOMMMM! makes his mother spit fire from the air: bonus damage and a slow at the center of the fire."},
        ],
        "mistakes": [
            "Neglecting kills: they grow your abilities.",
            "Using Flap, Flap, Flap without knowing who will be bombarded.",
            "Casting the ultimate on enemies who leave the area.",
        ],
    },
    "Elise": {
        "playstyle": (
            "Elise is a two-form jungler: in human form, her abilities generate dormant spiderlings and she stuns with Cocoon; in Spider Form, she gains movement speed and new abilities with a horde of spiders. "
            "Her attacks in Spider Form deal bonus magic damage and heal her."
        ),
        "laning": (
            "In human form, hit to generate spiderlings. "
            "Cocoon stuns the first unit hit and reveals it if it is not stealthed."
        ),
        "combos": [
            {"name": "The engage combo", "when": "An enemy is within Cocoon range.",
             "how": "Cocoon stuns, Neurotoxin (current health) and Volatile Spiderling damage, then Spider Form transforms you: Venomous Bite (missing health), Skittering Frenzy, Rappel."},
            {"name": "Human-form harassment", "when": "You want to harass in human form.",
             "how": "Neurotoxin deals damage based on current health; every ability that hits generates a dormant spiderling."},
            {"name": "The dive", "when": "A carry is far away.",
             "how": "Rappel suspends you in the air with your spiders then drops you onto the targeted enemy; after the fall, your passive's bonus damage and healing are increased."},
        ],
        "mistakes": [
            "Transforming without having hit with any ability in human form.",
            "Using Cocoon with no plan for Spider Form.",
            "Forgetting that your attack range is reduced as a spider.",
        ],
    },
    "Volibear": {
        "playstyle": (
            "Volibear is a fighter whose attacks and abilities raise his attack speed, with bonus magic damage to nearby enemies after a while. "
            "Thundering Smash stuns, Frenzied Maul marks and can be recast to heal, Sky Splitter slows and gives a shield, and Stormbringer leaps him in while disabling nearby turrets."
        ),
        "laning": (
            "Thundering Smash gives you speed toward enemies and stuns the first one attacked. "
            "Frenzied Maul recast on the same target deals more damage and heals you."
        ),
        "strengths": [
            "His attack speed rises with his attacks and abilities, with area magic damage after a while.",
            "Stormbringer temporarily disables nearby enemy turrets and gives him bonus health.",
            "Frenzied Maul can be recast to deal more damage and heal him.",
        ],
        "weaknesses": [
            "Has to get close to deal his damage.",
            "Stormbringer has a long cooldown (110 to 160 s).",
            "His engages can be controlled before he reaches his target.",
        ],
        "teamfight": (
            "Volibear leaps onto enemies with Stormbringer, gains bonus health and slows those under him, then strikes with Thundering Smash and Frenzied Maul. "
            "Near an enemy turret, the ultimate disables it, which allows you to dive."
        ),
        "combos": [
            {"name": "The trade", "when": "An enemy is within range.",
             "how": "Thundering Smash stuns, Frenzied Maul marks then is recast for damage and a heal, Sky Splitter slows and gives you a shield."},
            {"name": "The turret dive", "when": "An enemy is protected by a turret.",
             "how": "Stormbringer leaps you in while slowing and damaging the enemies under you; nearby enemy turrets are temporarily disabled."},
            {"name": "The team fight", "when": "A fight begins.",
             "how": "Your attacks stack attack speed and, after a while, deal bonus magic damage to nearby enemies."},
            {"name": "The dive under a turret", "when": "An enemy is protected by a turret.",
             "how": "Stormbringer temporarily disables the turrets near its landing point, slows and damages the enemies under you; Thundering Smash stuns, Frenzied Maul is recast to heal, Sky Splitter gives you a shield."},
        ],
        "mistakes": [
            "Casting Stormbringer without taking advantage of the disabled turret.",
            "Forgetting to recast Frenzied Maul.",
            "Using Sky Splitter out of range for the shield.",
        ],
    },
    "Ziggs": {
        "playstyle": (
            "Ziggs is a siege mage-marksman: his attacks regularly deal bonus magic damage, and his abilities reduce that delay. "
            "Bouncing Bomb damages, Satchel Charge knocks back (and destroys vulnerable turrets), Hexplosive Minefield slows, and Mega Inferno Bomb is thrown from very far away."
        ),
        "laning": (
            "Chain ability then attack to benefit from your passive. "
            "Satchel Charge knocks you back without damaging you: use it to reposition."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within range.",
             "how": "Bouncing Bomb deals damage, your attack benefits from the passive bonus, Hexplosive Minefield slows."},
            {"name": "The exit", "when": "An enemy dives you.",
             "how": "Satchel Charge knocks back the enemies and you (no damage to you); place mines behind you to slow."},
            {"name": "The siege ultimate", "when": "Enemies are grouped or a turret is vulnerable.",
             "how": "Mega Inferno Bomb is thrown from very far away: more damage in the main impact zone; use Satchel Charge to destroy vulnerable turrets."},
        ],
        "mistakes": [
            "Casting the ultimate without aiming at the main impact zone.",
            "Wasting Satchel Charge with no plan.",
            "Placing mines with no strategic placement.",
        ],
    },
    "AurelionSol": {
        "playstyle": (
            "Aurelion Sol is a mage who grows through stardust: his abilities that damage enemies give him some, which permanently upgrades each of his abilities. "
            "Breath of Light channels, Astral Flight makes him fly, Singularity pulls in and executes at the center, and Falling Star can become The Skies Descend with enough stardust."
        ),
        "laning": (
            "Hit champions with Breath of Light to collect stardust. "
            "Each second of channeling on an enemy adds damage."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within range.",
             "how": "Breath of Light channels and deals increasing damage; Astral Flight lifts you and Breath of Light has no cooldown or maximum channel duration."},
            {"name": "The execution zone", "when": "Several enemies are grouped.",
             "how": "Singularity slowly pulls enemies toward its center, which executes those under a certain percentage of max health; Falling Star stuns."},
            {"name": "The Skies Descend", "when": "You have enough stardust.",
             "how": "Collecting enough stardust turns the next Falling Star into The Skies Descend: a bigger zone, more damage, a knock-up and a shockwave."},
        ],
        "mistakes": [
            "Channeling without a target: Breath of Light only adds damage on an enemy.",
            "Neglecting stardust.",
            "Using Astral Flight without preparing your next ability.",
        ],
    },
    "Singed": {
        "playstyle": (
            "Singed is a tank-mage who leaves a poison trail behind him and gains speed when passing champions. "
            "Mega Adhesive slows and grounds, Fling knocks the enemy behind him (rooted if they land in the adhesive), and Insanity Potion improves his stats and makes his trail apply Grievous Wounds."
        ),
        "laning": (
            "Your poison trail damages the enemies who follow it. "
            "Fling on a target who lands in Mega Adhesive roots them."
        ),
        "combos": [
            {"name": "The capture", "when": "An enemy is within Fling range.",
             "how": "Mega Adhesive slows and grounds the enemies in the area; Fling knocks the enemy behind you: if they land in the adhesive, they are rooted."},
            {"name": "The chase", "when": "You are chasing a carry.",
             "how": "Insanity Potion improves your stats and your trail applies Grievous Wounds."},
            {"name": "The escape", "when": "An enemy is chasing you.",
             "how": "Your poison trail damages those following you and Mega Adhesive slows them."},
        ],
        "mistakes": [
            "Chasing without using your trail.",
            "Casting Mega Adhesive without an enemy trajectory.",
            "Using Insanity Potion too early: it has a limited duration.",
        ],
    },
    "Rumble": {
        "playstyle": (
            "Rumble is a fighter-mage running on Heat: every ability increases his Heat. At 50% he enters the Danger Zone (bonus effects), at 100% he overheats (bonus attack speed and damage but no abilities for a few seconds). "
            "Flamespitter ignites, Scrap Shield protects, Electro Harpoon slows and reduces magic resistance, and The Equalizer creates a wall of flames."
        ),
        "laning": (
            "Keep your Heat at the Danger Zone level without overheating. "
            "You can carry 2 harpoons at the same time."
        ),
        "combos": [
            {"name": "The Danger Zone trade", "when": "You have more than 50% Heat.",
             "how": "Electro Harpoon slows and reduces magic resistance, Flamespitter deals more damage in the Danger Zone, Scrap Shield protects you with more health."},
            {"name": "The area ultimate", "when": "Enemies are in a corridor.",
             "how": "The Equalizer fires a salvo of rockets that creates a wall of flames that damages and slows."},
            {"name": "The overheat", "when": "You want to finish by attacking.",
             "how": "At 100% Heat, you overheat: bonus attack speed and attack damage, but no abilities for a few seconds."},
        ],
        "mistakes": [
            "Overheating without having placed your decisive abilities.",
            "Not using both harpoons.",
            "Staying at low Heat: the Danger Zone empowers all your abilities.",
        ],
    },
    "Udyr": {
        "playstyle": (
            "Udyr is a stance jungler: four abilities he can activate to switch stances, and recast to renew their effects and add others. "
            "After an ability, his next two attacks gain attack speed. Wilding Claw strikes, Iron Mantle protects, Blazing Stampede stuns, Wingborne Storm slows."
        ),
        "laning": (
            "Choose your stance according to what you need: damage, defense, mobility or area. "
            "Recasting an ability renews its effects and adds some."
        ),
        "combos": [
            {"name": "The damage stance", "when": "You want to maximize your damage.",
             "how": "Wilding Claw gives attack speed and physical damage on your next two attacks; recast it so your attacks call down lightning."},
            {"name": "The tank stance", "when": "You are engaged.",
             "how": "Iron Mantle gives a shield and healing on your next two attacks; recast, a stronger shield and healing based on max health."},
            {"name": "The engage", "when": "An enemy is within range.",
             "how": "Blazing Stampede speeds you up and stuns with the first attack on each target; Wingborne Storm damages and slows nearby enemies."},
        ],
        "mistakes": [
            "Staying in a single stance when the situation changes.",
            "Forgetting the recasts.",
            "Using Blazing Stampede with no target to stun.",
        ],
    },
    "Kindred": {
        "playstyle": (
            "Kindred is a marksman-jungler who hunts: Mark of the Kindred marks targets, and every successful hunt permanently strengthens her basic abilities, with more range every 4 hunts. "
            "Dance of Arrows fires at three targets, Wolf's Frenzy attacks nearby enemies, Mounting Dread sends Wolf onto the target, and Lamb's Respite stops anyone from dying in the area."
        ),
        "laning": (
            "Mark and hunt to permanently strengthen your abilities. "
            "Lamb stacks effects by moving and attacking: at max, her next attack heals you."
        ),
        "combos": [
            {"name": "The hunt", "when": "A marked target is within range.",
             "how": "Dance of Arrows repositions you and fires at up to three nearby targets; Mounting Dread slows and, after two more attacks, the third sends Wolf for huge damage."},
            {"name": "The area fight", "when": "Several enemies are close.",
             "how": "Wolf's Frenzy makes Wolf attack around him; your attack, with maxed stacks, heals you."},
            {"name": "The life zone", "when": "A decisive fight around an objective.",
             "how": "Lamb's Respite offers a refuge from death to every creature in the area: no one can die there until the effect ends, then units are healed. It protects enemies too."},
        ],
        "mistakes": [
            "Using the ultimate without realizing it also protects enemies.",
            "Neglecting hunts: they strengthen your abilities.",
            "Casting Dance of Arrows without wanting to reposition.",
        ],
    },
    "Yorick": {
        "playstyle": (
            "Yorick is a fighter who summons: his passive lets him make Ghouls appear that attack nearby enemies, and his Last Rites create a grave on a champion, a large monster or a target that dies. "
            "Dark Procession creates a destructible wall, Mourning Mist marks and slows, and Eulogy of the Isles summons the Maiden of the Mist."
        ),
        "laning": (
            "Last Rites deals bonus damage and heals you: take last hits with it. "
            "Use the wall to isolate your target."
        ),
        "combos": [
            {"name": "The trade", "when": "An enemy is within range.",
             "how": "Last Rites deals bonus damage and heals you, creating a grave if it hits a champion; Mourning Mist reduces armor, damages, slows and marks."},
            {"name": "Isolation", "when": "A carry is close to their allies.",
             "how": "Dark Procession summons a destructible wall that blocks enemy movement and separates the target."},
            {"name": "The Maiden ultimate", "when": "A carry is identified.",
             "how": "Eulogy of the Isles summons the Maiden on the target: your attacks against them deal bonus damage; the Maiden turns the dead into Ghouls."},
        ],
        "mistakes": [
            "Not using the graves created by Last Rites.",
            "Placing the wall with no plan.",
            "Casting the ultimate on the wrong target: the Maiden follows her target.",
        ],
    },
}
