"""English guides, batch 16 (includes the extras for Bel'Veth, Trundle, Annie, Amumu)."""

EN = {
    "Nunu": {
        "playstyle": (
            "Nunu & Willump are a tank-mage duo: Nunu raises the attack and movement speed of Willump and a nearby ally, and Willump's attacks hurt the enemies near the target. "
            "Consume heals, Biggest Snowball Ever! grows as it rolls and knocks up, Snowball Barrage roots those it hits, and Absolute Zero creates a blizzard."
        ),
        "laning": (
            "Consume bites a minion, a monster or a champion and heals you. "
            "Biggest Snowball Ever! grows and speeds up: the longer it rolls, the more effective it is."
        ),
        "combos": [
            {"name": "The engage", "when": "An enemy is far away.",
             "how": "Biggest Snowball Ever! damages and knocks up, Snowball Barrage damages and Willump roots the champions hit, Consume bites while healing you."},
            {"name": "The area ultimate", "when": "Enemies are grouped.",
             "how": "Absolute Zero creates a blizzard that slows and deals heavy damage at the end of the spell: stay in place to channel it."},
            {"name": "Sustain", "when": "You are in the jungle.",
             "how": "Consume deals heavy damage and restores your health as it bites."},
        ],
        "mistakes": [
            "Casting the ultimate with no protection during its duration.",
            "Not letting the snowball roll long enough.",
            "Forgetting your ally: Nunu raises their speeds.",
        ],
    },
    "Belveth": {
        "playstyle": (
            "Bel'Veth is an attack-speed jungler: her passive gives her permanent bonuses after killing large monsters, large minions and champions, and a temporary bonus after each ability. "
            "Void Surge dashes her, Above and Below knocks up and slows, Royal Maelstrom channels strikes on the enemy with the lowest health, and Endless Banquet turns her into her true form."
        ),
        "laning": (
            "Kill large monsters and large minions to stack permanent attack speed bonuses. "
            "Void Surge damages every enemy crossed."
        ),
        "strengths": [
            "Her attack speed increases permanently with large monsters, large minions and champions killed.",
            "Royal Maelstrom gives her life steal and damage reduction while striking the enemy with the lowest health.",
            "Her final form (Endless Banquet) increases her max health, range and attack speed.",
        ],
        "weaknesses": [
            "Royal Maelstrom roots her in place while channeling.",
            "Her power depends on good jungle progression.",
            "Her ultimate depends on Void Coral to collect.",
        ],
        "teamfight": (
            "Bel'Veth enters combat with Void Surge, knocks up with Above and Below, then channels Royal Maelstrom in the middle of the enemies to benefit from the life steal and damage reduction. "
            "She is most dangerous once she has taken her final form."
        ),
        "combos": [
            {"name": "The trade", "when": "An enemy is within range.",
             "how": "Void Surge dashes you while damaging; each ability gives you a temporary attack speed bonus; Above and Below knocks up and slows."},
            {"name": "The storm", "when": "Enemies are close.",
             "how": "Royal Maelstrom roots you and channels a storm of strikes that targets the enemy with the lowest health, with life steal and damage reduction."},
            {"name": "The final form", "when": "You have Void Coral.",
             "how": "Endless Banquet consumes Void Coral: max health, attack range and attack speed increase; the coral from an epic Void monster lets you summon Void Remoras."},
            {"name": "Entering the fight", "when": "Enemies are grouped.",
             "how": "Void Surge dashes you, damaging every enemy crossed, Above and Below knocks up and slows, Royal Maelstrom channels a storm of strikes around you."},
        ],
        "mistakes": [
            "Neglecting large monsters: they give permanent bonuses.",
            "Casting Royal Maelstrom with no protection: you are rooted.",
            "Not collecting Void Coral.",
        ],
    },
    "Skarner": {
        "playstyle": (
            "Skarner is a tectonic jungler-tank: his attacks, Shattered Earth, Upheaval and Impale apply stacks of Threads of Vibration, and at max stacks the enemies take magic damage based on their max health. "
            "Seismic Bastion gives a shield and slows, Ixtal's Impact slams into a wall, and Impale suppresses then drags enemies."
        ),
        "laning": (
            "Pull up a boulder with Shattered Earth to empower your attacks, then throw it with Upheaval. "
            "Stack Threads of Vibration to trigger the max-health damage."
        ),
        "combos": [
            {"name": "The trade", "when": "An enemy is within range.",
             "how": "Shattered Earth empowers your attacks, Upheaval throws the boulder, Seismic Bastion gives you a shield and slows with a shockwave."},
            {"name": "The slam", "when": "An enemy is near a wall.",
             "how": "Ixtal's Impact charges through obstacles; if it hits a champion, it slams them into the next wall, dealing damage and stunning them."},
            {"name": "The capture ultimate", "when": "A carry is visible.",
             "how": "Impale suppresses the enemy champions hit by your tails and lets you move while dragging them: bring them to your team."},
        ],
        "mistakes": [
            "Dragging the enemies toward their allies.",
            "Forgetting Threads of Vibration: it is your source of max-health damage.",
            "Casting Ixtal's Impact with no wall.",
        ],
    },
    "Azir": {
        "playstyle": (
            "Azir is a sand-soldier mage: Arise! summons a soldier that attacks in his place, and the soldier's attacks deal magic damage along a line. "
            "Conquering Sands sends all the soldiers, Shifting Sands dashes him to a soldier, and Emperor's Divide pushes enemies back. His passive lets him summon the Sun Disc from the ruins of turrets."
        ),
        "laning": (
            "Place your soldiers so they hit your target; they replace your attack against targets in their range. "
            "Shifting Sands dashes you to a soldier."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within range.",
             "how": "Arise! summons a soldier that attacks in your place; Conquering Sands sends all the soldiers over an area: they damage and slow for 1 second."},
            {"name": "The engage", "when": "A carry is within range.",
             "how": "Shifting Sands gives you a shield and dashes you to a soldier; if it hits a champion, a new soldier is prepared and the dash stops; Emperor's Divide pushes back."},
            {"name": "Defense", "when": "An enemy dives.",
             "how": "Emperor's Divide summons a wall of soldiers that charge forward, pushing back and damaging the enemies."},
        ],
        "mistakes": [
            "Not placing soldiers before attacking.",
            "Casting Shifting Sands with no soldier nearby.",
            "Using the ultimate with no direction.",
        ],
    },
    "Ivern": {
        "playstyle": (
            "Ivern is an enchanter jungler-support: he cannot attack or be attacked by non-epic monsters, and creates magic groves that, once grown, release the monsters for gold and experience. "
            "Rootcaller roots, Brushmaker creates tall grass, Triggerseed protects, and Daisy! summons a sentinel."
        ),
        "laning": (
            "Grow your groves, then release the monsters for gold and experience. "
            "Your allies can dash to the target rooted by Rootcaller."
        ),
        "combos": [
            {"name": "The pick", "when": "An enemy is within Rootcaller range.",
             "how": "Rootcaller roots the target and your allies can dash onto them; Triggerseed gives a shield to an ally that explodes and slows."},
            {"name": "The grass zone", "when": "A fight is approaching.",
             "how": "Brushmaker creates a patch of tall grass where your attacks and those of your nearby allies deal bonus magic damage."},
            {"name": "The companion", "when": "A team fight begins.",
             "how": "Daisy! summons a sentinel that fights by your side; recast the ability to order her to attack or move."},
        ],
        "mistakes": [
            "Neglecting your groves.",
            "Using Triggerseed on an ally with no enemy nearby: the shield resets.",
            "Not controlling Daisy.",
        ],
    },
    "Kled": {
        "playstyle": (
            "Kled is a mounted fighter: Skaarl takes the damage in his place, and when his health drops to zero, Kled is dismounted with modified abilities and less damage to champions. "
            "He restores Skaarl's courage by fighting, and Bear Trap on a Rope hooks and pulls enemies toward him."
        ),
        "laning": (
            "Protect Skaarl: as long as he is mounted, you deal more damage. "
            "Dismounted, fight to restore courage and get back in the saddle."
        ),
        "combos": [
            {"name": "The hook", "when": "An enemy is within trap range.",
             "how": "Bear Trap on a Rope hooks a champion; if they stay hooked, they take bonus damage and are pulled toward you; Jousting dashes you in."},
            {"name": "The speed fight", "when": "You are in melee.",
             "how": "Violent Tendencies greatly raises your attack speed for four attacks; the fourth deals more damage."},
            {"name": "The team charge", "when": "Your team engages.",
             "how": "Chaaaaaaaarge!!! makes you charge with a shield and leaves a trail that raises your allies' speed; Skaarl dashes onto the first enemy champion he meets."},
        ],
        "mistakes": [
            "Letting Skaarl drop to zero for no reason.",
            "Forgetting that dismounted you have different abilities.",
            "Using Jousting without the recast when it is useful.",
        ],
    },
    "Trundle": {
        "playstyle": (
            "Trundle is a duel fighter: when an enemy unit dies near him, he recovers a percentage of their max health. "
            "Chomp slows and drains attack damage, Frozen Domain raises his speeds and healing, Pillar of Ice blocks the path, and Subjugate steals health, armor and magic resistance."
        ),
        "laning": (
            "Chomp reduces your opponent's attack damage: use it at the start of a trade. "
            "Fight inside your Frozen Domain to benefit from bonuses."
        ),
        "strengths": [
            "Recovers health when an enemy dies near him, and heals a lot in his Frozen Domain.",
            "Chomp slows and drains the target's attack damage: very effective against a melee carry.",
            "Subjugate instantly steals health, armor and magic resistance, then doubles the amount over 4 seconds.",
        ],
        "weaknesses": [
            "Depends on staying in his Frozen Domain for his bonuses.",
            "Little engage at range: he has to reach his target.",
            "Pillar of Ice only helps if the terrain suits it.",
        ],
        "teamfight": (
            "Trundle picks a target, neutralizes them with Chomp and Subjugate, and uses Pillar of Ice to block a path or split the enemies. "
            "He fights better inside his Frozen Domain, where his speeds and healing increase."
        ),
        "combos": [
            {"name": "The trade", "when": "An enemy is within range.",
             "how": "Frozen Domain raises speeds and healing, Chomp deals damage, slows and drains their attack damage, Pillar of Ice blocks the path."},
            {"name": "The duel", "when": "A carry is isolated.",
             "how": "Subjugate instantly steals a percentage of the target's health, armor and magic resistance, then the amount doubles over 4 seconds."},
            {"name": "The trap", "when": "An enemy is chasing you.",
             "how": "Pillar of Ice blocks the path and slows nearby enemies."},
            {"name": "The attrition duel", "when": "A melee carry is within range.",
             "how": "Frozen Domain raises your speeds and healing, Chomp drains their attack damage, Subjugate steals part of their health, armor and magic resistance, doubled over 4 seconds."},
        ],
        "mistakes": [
            "Using Subjugate on a carry who is too weak: it steals a percentage of the stats.",
            "Fighting outside your Frozen Domain.",
            "Forgetting to drain the damage with Chomp.",
        ],
    },
    "Sejuani": {
        "playstyle": (
            "Sejuani is an ice jungler-tank: out of combat she gains Frost Armor (armor, magic resistance, immunity to slows), and she can shatter a stunned enemy for huge magic damage. "
            "Arctic Assault knocks up, Winter's Wrath applies Frost stacks, Permafrost stuns a champion at max Frost, and Glacial Prison freezes the first champion hit."
        ),
        "laning": (
            "Stack Frost with Winter's Wrath then freeze with Permafrost. "
            "Take advantage of Frost Armor out of combat to engage."
        ),
        "combos": [
            {"name": "The engage", "when": "An enemy is within range.",
             "how": "Arctic Assault knocks up and stops on a champion; Winter's Wrath damages, slows and applies Frost; Permafrost stuns a champion at max stacks; your attack shatters the stunned enemy."},
            {"name": "The capture ultimate", "when": "A carry is visible.",
             "how": "Glacial Prison freezes and stuns the first champion hit with bolas and creates an ice storm that slows the other enemies."},
            {"name": "The approach", "when": "You want to open a fight.",
             "how": "Arctic Assault knocks enemies into the air, Winter's Wrath slows them with two mace strikes."},
        ],
        "mistakes": [
            "Using Permafrost without max Frost.",
            "Casting the ultimate with no ally to take advantage of the freeze.",
            "Forgetting to shatter the stunned enemy.",
        ],
    },
    "Rammus": {
        "playstyle": (
            "Rammus is a jungler-tank who gains attack damage based on his armor and magic resistance. "
            "Powerball rolls over enemies, Defensive Ball Curl raises his defenses and reflects damage, Frenzying Taunt forces an enemy to attack him, and Soaring Slam leaps and lands with damage and a slow."
        ),
        "laning": (
            "Taunt the enemy carry to force them to attack you. "
            "Defensive Ball Curl makes you very tough and reflects damage to attackers."
        ),
        "combos": [
            {"name": "The engage", "when": "An enemy is within roll range.",
             "how": "Powerball rolls toward enemies, dealing damage and slowing; Frenzying Taunt forces the target to attack you; Soaring Slam lands in an area."},
            {"name": "Defense", "when": "A carry is attacking your team.",
             "how": "Defensive Ball Curl greatly raises armor and magic resistance and reflects damage; Frenzying Taunt forces a champion to fixate on you."},
            {"name": "The knock-up combo", "when": "Several enemies are grouped.",
             "how": "If Soaring Slam is cast during Powerball, the enemies near the center are knocked into the air."},
        ],
        "mistakes": [
            "Casting Defensive Ball Curl on an enemy who is not attacking with physical damage.",
            "Using Soaring Slam without Powerball active when you can combine them.",
            "Taunting the wrong champion.",
        ],
    },
    "RekSai": {
        "playstyle": (
            "Rek'Sai is a two-mode jungler: on the surface, she generates Fury with her attacks and abilities, and burrowed she consumes Fury to heal. "
            "Burrow gives her new abilities (Un-burrow, Tunnel), and Void Rush marks then lets her leap onto a marked target."
        ),
        "laning": (
            "Generate Fury to heal while burrowed and to empower Furious Bite. "
            "Burrowed, you can no longer attack and your vision is reduced."
        ),
        "combos": [
            {"name": "The trade", "when": "An enemy is within range.",
             "how": "Queen's Wrath empowers your next 3 attacks; Furious Bite deals bonus true damage if your Fury gauge is full."},
            {"name": "The underground ambush", "when": "An enemy is isolated.",
             "how": "Burrow gives you speed; Un-burrow, while burrowed, knocks up and damages nearby enemies; Tunnel creates a reusable passage."},
            {"name": "The hunting ultimate", "when": "An enemy is marked.",
             "how": "Void Rush passively marks your targets; activate it to become untargetable and leap onto a marked target with heavy damage based on their max health."},
        ],
        "mistakes": [
            "Staying burrowed against an enemy who destroys your tunnel.",
            "Not using your Fury to heal.",
            "Leaping without having marked.",
        ],
    },
    "Annie": {
        "playstyle": (
            "Annie is a burst mage: after 4 abilities used, her next offensive ability stuns its target, and she starts the game and respawns with Pyromania available. "
            "Disintegrate refunds its mana if it kills, Incinerate deals damage in a cone, Molten Shield protects, and Summon: Tibbers brings her bear to life."
        ),
        "laning": (
            "Use your abilities to charge your passive: 4 abilities then a stun. "
            "Disintegrate refunds its mana if it kills the target."
        ),
        "strengths": [
            "Stuns after 4 abilities used, and begins every life with her passive ready.",
            "Tibbers deals area damage and keeps burning nearby enemies.",
            "Molten Shield protects an ally and damages those who attack them.",
        ],
        "weaknesses": [
            "Has to cast 4 abilities to make the stun available.",
            "Short range on most of her abilities: she has to get close.",
            "Tibbers is her ultimate: without it, the burst decreases.",
        ],
        "teamfight": (
            "Annie prepares her stun with 4 abilities before the fight, then casts Tibbers on the enemy group so it is followed by a stun. "
            "She also protects her carry with Molten Shield, which damages attackers."
        ),
        "combos": [
            {"name": "The stun", "when": "An enemy is within range.",
             "how": "Chain four abilities; your next offensive ability stuns your target: cast Tibbers, which deals area damage and burns nearby enemies."},
            {"name": "The team engage", "when": "A fight begins.",
             "how": "Molten Shield gives movement speed and a shield (damaging attackers); Tibbers attacks and burns nearby enemies."},
            {"name": "Farming", "when": "You are in lane.",
             "how": "Disintegrate kills the target and refunds its mana cost."},
            {"name": "The team-fight opener", "when": "Your passive is ready (4 abilities already used).",
             "how": "Molten Shield protects you, Incinerate damages in a cone, Tibbers (with the stun from your passive) lands on the group, Disintegrate finishes."},
        ],
        "mistakes": [
            "Wasting your passive before the engage.",
            "Casting Tibbers without the stun ready.",
            "Neglecting Molten Shield for an ally.",
        ],
    },
    "Amumu": {
        "playstyle": (
            "Amumu is a control jungler-tank: his attacks curse enemies, who take bonus true damage each time they take magic damage. "
            "Bandage Toss stuns, Despair removes a percentage of max health every second, Tantrum reduces physical damage and hurts, and Curse of the Sad Mummy entangles and stuns nearby enemies."
        ),
        "laning": (
            "Bandage Toss has a very short cooldown: use it to approach and stun. "
            "Despair consumes mana every second: do not leave it on with no target."
        ),
        "strengths": [
            "Curse of the Sad Mummy stuns every nearby enemy and applies his passive.",
            "Despair reduces the max health of all the enemies around him every second.",
            "Bandage Toss has a very short cooldown to close the distance.",
        ],
        "weaknesses": [
            "Despair consumes mana as long as it is active.",
            "Needs an ally to convert his stuns into takedowns.",
            "Little damage outside his area effects.",
        ],
        "teamfight": (
            "Amumu is an area engage: Curse of the Sad Mummy stuns every nearby enemy, then Despair removes a percentage of their max health every second while his allies attack. "
            "His passive makes cursed enemies take bonus true damage on every magic damage instance."
        ),
        "combos": [
            {"name": "The engage", "when": "Several enemies are grouped.",
             "how": "Bandage Toss stuns and brings you closer, Curse of the Sad Mummy entangles and stuns nearby enemies, Despair removes a percentage of their max health every second."},
            {"name": "The prolonged fight", "when": "You are in the middle of the enemies.",
             "how": "Your passive curses; Tantrum reduces the physical damage you take and hurts; its cooldown decreases every time you are hit."},
            {"name": "The pick", "when": "An enemy is isolated.",
             "how": "Bandage Toss stuns and damages as you approach, then attack to apply the curse."},
            {"name": "The area engage", "when": "Several enemies are grouped.",
             "how": "Bandage Toss stuns and brings you closer, Curse of the Sad Mummy entangles nearby enemies, Despair removes a percentage of their max health, Tantrum reduces the physical damage you take."},
        ],
        "mistakes": [
            "Casting the ultimate on a single enemy.",
            "Leaving Despair on with no target.",
            "Forgetting your curse: magic damage becomes stronger against the cursed.",
        ],
    },
}
