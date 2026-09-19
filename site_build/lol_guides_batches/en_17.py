"""English guides, batch 17 (last one; includes the extras for Taric, Heimerdinger, Nilah)."""

EN = {
    "Illaoi": {
        "playstyle": (
            "Illaoi is a tentacle fighter: she and the vessels she creates make tentacles appear on nearby impassable terrain; they deal physical damage and heal her if they hurt a champion. "
            "Test of Spirit rips out an enemy's spirit and turns them into a vessel, and Leap of Faith summons one tentacle per champion hit."
        ),
        "laning": (
            "Play near terrain features: that is where your tentacles appear. "
            "Tentacle Smash increases the tentacles' damage and makes one slam down when activated."
        ),
        "combos": [
            {"name": "The trade", "when": "An enemy is near terrain features.",
             "how": "Test of Spirit rips out the enemy's spirit: if they move too far away or the spirit is destroyed, they become a vessel and make tentacles appear; Harsh Lesson leaps you in and pushes the nearby tentacles to strike the target."},
            {"name": "The area ultimate", "when": "Several enemies are close.",
             "how": "Leap of Faith slams your idol, deals physical damage and summons a tentacle per enemy champion hit."},
            {"name": "Harassment", "when": "An enemy is in lane.",
             "how": "Tentacle Smash deals physical damage and amplifies the tentacles; they heal you if they hurt a champion."},
        ],
        "mistakes": [
            "Fighting far from impassable terrain features.",
            "Casting the ultimate without several targets.",
            "Forgetting that the spirit passes part of the damage to the original target.",
        ],
    },
    "Evelynn": {
        "playstyle": (
            "Evelynn is a shadow jungler-assassin: out of combat she is cloaked in Demon Shade, which heals her at low health and camouflages her from level 6. "
            "Hate Spike strikes then fires spikes, Allure charms her target, Whiplash moves her forward, and Last Caress makes her untargetable before teleporting her backward."
        ),
        "laning": (
            "Stay hidden: camouflage arrives at level 6. "
            "Allure curses the target: your next attack or spell charms them and reduces their magic resistance."
        ),
        "combos": [
            {"name": "The assassination combo", "when": "A carry is within range.",
             "how": "Allure curses the target, your next attack or spell charms them and reduces their magic resistance; Hate Spike and Whiplash deal damage; Last Caress ravages the area then teleports you backward."},
            {"name": "The approach", "when": "An enemy is far away.",
             "how": "Hate Spike hits the first unit hit then fires a line of spikes at nearby enemies several times; Whiplash raises your movement speed."},
            {"name": "The exit", "when": "You are in danger.",
             "how": "Last Caress makes you untargetable, damages in front of you and teleports you far backward."},
        ],
        "mistakes": [
            "Getting seen before you charm.",
            "Using the ultimate with no plan: it teleports you backward.",
            "Neglecting Demon Shade: it heals you at low health.",
        ],
    },
    "Taric": {
        "playstyle": (
            "Taric is a protection support-tank: his passive empowers his next 2 attacks after an ability (magic damage, reduced cooldowns, rapid attacks). "
            "Starlight's Touch heals nearby allies based on its charges, Bastion gives a shield and armor, Dazzle stuns, and Cosmic Radiance makes allies invulnerable."
        ),
        "laning": (
            "Chain ability then attacks to make the most of Bravado: each empowered attack gives a charge of Starlight's Touch. "
            "Bastion: your abilities are also cast from the affected ally."
        ),
        "strengths": [
            "Starlight's Touch heals his allies based on the number of stored charges.",
            "Bastion gives armor and lets him cast his abilities from the affected ally.",
            "Cosmic Radiance makes nearby allies invulnerable for a short time.",
        ],
        "weaknesses": [
            "Cosmic Radiance has a delay before it activates: you have to anticipate it.",
            "Dazzle takes time to take effect.",
            "His damage stays low without his empowered attacks.",
        ],
        "teamfight": (
            "Taric triggers Cosmic Radiance at the right moment to make his team invulnerable during the enemy engage, then chains Dazzle and empowered attacks. "
            "He mostly protects a specific ally thanks to Bastion."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within range.",
             "how": "Dazzle prepares a beam that stuns after a short delay; your empowered attacks deal bonus magic damage and charge Starlight's Touch."},
            {"name": "Protection", "when": "Your carry is under threat.",
             "how": "Bastion gives the ally a shield and armor as long as they stay near you; Starlight's Touch heals based on your charges."},
            {"name": "The team ultimate", "when": "A decisive fight begins.",
             "how": "After a delay, Cosmic Radiance bathes nearby allies in cosmic energy and makes them invulnerable for a short time: plan for the delay."},
            {"name": "The invulnerability window", "when": "An enemy engage is predictable.",
             "how": "Cosmic Radiance triggers after a delay: cast it before the damage peak; Dazzle stuns after a short delay, your empowered attacks charge Starlight's Touch."},
        ],
        "mistakes": [
            "Triggering the ultimate too late: it has a delay.",
            "Forgetting your passive's empowered attacks.",
            "Placing Dazzle without anticipating the delay.",
        ],
    },
    "Heimerdinger": {
        "playstyle": (
            "Heimerdinger is a turret mage: his passive gives him speed near allied or deployed turrets. "
            "H-28G Evolution Turret places a turret with a piercing laser, Hextech Micro-Rockets converge toward his cursor, CH-2 Electron Storm Grenade stuns and slows, and UPGRADE!!! boosts the effects of his next spell."
        ),
        "laning": (
            "Deploy turrets to control the lane. "
            "The turret deals 50% damage to enemy turrets."
        ),
        "strengths": [
            "His turrets deal continuous damage and help control an area or a lane.",
            "CH-2 Electron Storm Grenade stuns the units hit directly and slows nearby ones.",
            "UPGRADE!!! boosts the effects of his next spell.",
        ],
        "weaknesses": [
            "His power depends on his turrets: far from them, he is vulnerable.",
            "Not very mobile outside his speed near turrets.",
            "The Grenade and Micro-Rockets have long cooldowns.",
        ],
        "teamfight": (
            "Heimerdinger turns a corridor or an objective into a defended zone: turrets placed in advance, the Electron Storm Grenade to stun, Micro-Rockets for range. "
            "UPGRADE!!! on the right ability often decides the fight."
        ),
        "combos": [
            {"name": "The siege", "when": "You want to push or defend.",
             "how": "H-28G Evolution Turret deploys a turret with a piercing laser; the Micro-Rockets converge toward your cursor at long range."},
            {"name": "The stun", "when": "An enemy approaches your turrets.",
             "how": "CH-2 Electron Storm Grenade stuns the units hit directly and slows nearby ones; your turrets deal damage."},
            {"name": "The upgraded ability", "when": "A decisive fight begins.",
             "how": "UPGRADE!!! gives boosted effects on your next spell: choose it according to the situation."},
            {"name": "Objective defense", "when": "Your team is defending a point.",
             "how": "Deploy two turrets, UPGRADE!!! empowers your next ability, the Electron Storm Grenade stuns and slows, the Micro-Rockets converge toward your cursor."},
        ],
        "mistakes": [
            "Fighting far from your turrets.",
            "Casting the upgrade with no clear spell to boost.",
            "Placing turrets with no protection.",
        ],
    },
    "Nilah": {
        "playstyle": (
            "Nilah is a support fighter-marksman: her passive gives her more experience on minions and strengthens and shares nearby allies' healing and shields. "
            "Formless Blade increases her attack range, Jubilant Veil makes her dodge attacks, Slipstream dashes her, and Apotheosis deals damage and pulls enemies in."
        ),
        "laning": (
            "Take minions to gain more experience. "
            "Formless Blade increases your attack range for a short time."
        ),
        "strengths": [
            "Gains more experience on minions (passive) and shares nearby allies' healing and shields.",
            "Jubilant Veil makes her dodge every attack and gives the same effect to the allies she touches.",
            "Apotheosis gathers enemies around her, which helps her team's area damage.",
        ],
        "weaknesses": [
            "Has to be in contact to express her power: Formless Blade only extends her range briefly.",
            "Jubilant Veil has a long cooldown (22 to 26 s): it cannot be used on a loop.",
            "Depends on allies who heal or protect to benefit from her passive.",
        ],
        "teamfight": (
            "Nilah is a melee marksman: she joins the fight with Slipstream, places Jubilant Veil to make her team immune to attacks while the mist lasts, "
            "then Apotheosis pulls the enemies toward her. She is better when her allies heal or protect her, since she strengthens and shares those effects."
        ),
        "combos": [
            {"name": "The trade", "when": "An enemy is within range.",
             "how": "Formless Blade deals damage in a straight line and increases your attack range; Slipstream dashes you in enthusiastically and damages along your path."},
            {"name": "Team protection", "when": "Your team is engaged.",
             "how": "Jubilant Veil raises your movement speed and makes you dodge every attack; any ally you touch during the mist gains this effect too."},
            {"name": "The gathering ultimate", "when": "The enemies are around you.",
             "how": "Apotheosis whirls your whip-blade, deals damage to the enemies around you then pulls them toward you."},
            {"name": "The engage with the veil", "when": "Your team engages against enemy basic attacks.",
             "how": "Jubilant Veil raises your movement speed and lets you avoid every attack; Slipstream dashes you onto the target, damaging along your path; Formless Blade increases your attack range."},
        ],
        "mistakes": [
            "Casting the ultimate without being in contact.",
            "Using Jubilant Veil with no ally to touch.",
            "Neglecting your allies' healing and shields.",
        ],
    },
}
