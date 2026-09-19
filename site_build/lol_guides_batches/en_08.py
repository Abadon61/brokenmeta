"""English guides, batch 8 (Wukong includes the extras: strengths / weaknesses / teamfight, and its 4th combo)."""

EN = {
    "Rengar": {
        "playstyle": (
            "Rengar is a jungle assassin who leaps onto his targets from tall grass. "
            "Every ability generates Ferocity, and at max the next ability is empowered. Thrill of the Hunt camouflages him, reveals the nearest enemy champion and reduces their armor."
        ),
        "laning": (
            "Leap from tall grass with your basic attack to open the trade. "
            "Save your Ferocity: at max, your next ability is empowered."
        ),
        "combos": [
            {"name": "The ambush", "when": "You are in tall grass near an enemy.",
             "how": "Your attack makes you leap, Savagery stabs for bonus damage, Bola Strike slows (roots with Ferocity), Battle Roar heals you."},
            {"name": "The hunting ultimate", "when": "You are tracking a carry.",
             "how": "Thrill of the Hunt camouflages you, reveals the nearest enemy champion from very far away, gives you speed, lets you leap without tall grass and reduces the target's armor."},
            {"name": "The exit", "when": "You are under control.",
             "how": "Battle Roar empowered by Ferocity breaks crowd control effects; Bola Strike roots the chasing target."},
        ],
        "mistakes": [
            "Spending your Ferocity too fast: at max, your abilities are empowered.",
            "Engaging without having positioned yourself in tall grass.",
            "Casting the ultimate with no priority target: it reveals the nearest champion.",
        ],
    },
    "Vi": {
        "playstyle": (
            "Vi is an engage fighter: Vault Breaker drags her forward while knocking back the enemies it hits, and her ultimate dashes onto an enemy while shoving aside those in her way. "
            "Her passive charges a shield that activates when she hits an enemy with an ability."
        ),
        "laning": (
            "Denting Blows breaks your opponent's armor and raises your attack speed: use your attacks to stack them. "
            "Relentless Force passes through the target and damages those behind."
        ),
        "combos": [
            {"name": "The engage", "when": "An enemy is within Vault Breaker range.",
             "how": "Vault Breaker propels you and knocks back the enemies it hits while applying Denting Blows; Relentless Force passes through the target."},
            {"name": "The capture", "when": "The enemy carry is isolated.",
             "how": "Cease and Desist dashes onto the enemy while shoving aside those in the way, then on arrival knocks them up, leaps over them and slams them back down."},
            {"name": "The shield", "when": "You enter melee.",
             "how": "Hitting with an ability activates the shield charged by your passive."},
        ],
        "mistakes": [
            "Using Vault Breaker with no target: it moves you forward.",
            "Casting the ultimate on an enemy out of your allies' reach.",
            "Forgetting to charge your shield before the engage.",
        ],
    },
    "Hwei": {
        "playstyle": (
            "Hwei is an artist-mage whose abilities are split into three subjects, each replacing his abilities: Disaster (damage: Devastating Fire, Molten Fissure, Cataclysm), Serenity (utility: Gentle Stream, Pool of Reflection, Starry Night) and Torment (control: Grim Visage, Gaze of the Abyss, Mind Maw). "
            "His passive completes a signature that explodes under an enemy hit by two damaging abilities."
        ),
        "laning": (
            "Hit an enemy with two damaging abilities to complete the signature: it explodes after a short delay. "
            "Choose your subject according to the situation: damage, support or control."
        ),
        "combos": [
            {"name": "The signature combo", "when": "An enemy is within range.",
             "how": "With Disaster, hit with two damaging abilities: the signature appears under the enemy and explodes after a short delay."},
            {"name": "Control", "when": "An enemy dives.",
             "how": "Torment replaces your abilities with crowd control: Grim Visage, Gaze of the Abyss or Mind Maw depending on the situation."},
            {"name": "The painting ultimate", "when": "A fight begins.",
             "how": "Spiraling Despair makes the first champion hit the center of a growing painting that slows and damages; it explodes at its size limit or when the affected champion dies."},
        ],
        "mistakes": [
            "Switching subject at the wrong time: each subject replaces your abilities.",
            "Forgetting the signature: two damaging abilities are needed.",
            "Casting Spiraling Despair on an enemy who can escape it.",
        ],
    },
    "Rakan": {
        "playstyle": (
            "Rakan is a mobile engage support: Grand Entrance dashes him in and knocks enemies up, Battle Dance flies him to an ally while giving them a shield, and his ultimate makes him faster and charms the enemies it hits. "
            "His passive periodically gives him a shield."
        ),
        "laning": (
            "Gleaming Quill heals your allies if it hits a champion or an epic monster. "
            "Battle Dance can be recast at no cost for a short time: chain it to reposition."
        ),
        "combos": [
            {"name": "The engage", "when": "An enemy carry is within range.",
             "how": "Grand Entrance dashes you in, knocking up nearby enemies, The Quickness raises your speed and charms the enemies it hits, Gleaming Quill damages."},
            {"name": "The rescue", "when": "An ally is in danger.",
             "how": "Battle Dance flies you to an allied champion, giving them a shield; recast it at no cost to extend the movement."},
            {"name": "Harassment", "when": "An enemy is within range.",
             "how": "Gleaming Quill deals magic damage and heals your allies if it hits a champion."},
        ],
        "mistakes": [
            "Engaging with no ally nearby to follow up.",
            "Wasting Grand Entrance with no target.",
            "Forgetting to recast Battle Dance.",
        ],
    },
    "KSante": {
        "playstyle": (
            "K'Sante is a two-phase tank-fighter: his abilities mark his targets and empower his next attack, and his ultimate makes him push an enemy through any wall before switching to All Out form. "
            "In All Out, he deals more damage and healing and his abilities are transformed, but his defenses drop."
        ),
        "laning": (
            "Ntofo Strikes pulls enemies at 2 stacks: place them to pull. "
            "Path Maker reduces the damage you take before dashing to knock back and stun."
        ),
        "combos": [
            {"name": "The trade", "when": "An enemy is at short range.",
             "how": "Two Ntofo Strikes make a shockwave that pulls enemies in, Footwork gives you a shield, your attack benefits from your passive's mark."},
            {"name": "The engage", "when": "An enemy is within dash range.",
             "how": "Path Maker charges your attack and protects you before dashing, knocking back and stunning the enemies."},
            {"name": "The ultimate at a wall", "when": "An enemy is near a wall.",
             "how": "All Out pushes the enemy through the wall then dashes you onto them: switch to All Out form for empowered damage and healing."},
        ],
        "mistakes": [
            "Staying in All Out form without taking advantage of the burst: your defenses are reduced.",
            "Casting the ultimate with no wall nearby.",
            "Ignoring your passive's mark.",
        ],
    },
    "Kayn": {
        "playstyle": (
            "Kayn is a jungler fighting Rhaast, the Darkin of his weapon: either Rhaast triumphs (healing based on the ability damage dealt to champions), or Kayn masters him and becomes the Shadow Assassin (bonus damage in the first seconds of a fight). "
            "Shadow Step lets him pass through terrain and his ultimate hides him inside an enemy to deal huge damage."
        ),
        "laning": (
            "Reaping Slash dashes you then strikes: both deal damage. "
            "Shadow Step lets you avoid obstacles and reposition."
        ),
        "combos": [
            {"name": "The trade", "when": "An enemy is within range.",
             "how": "Reaping Slash dashes you then strikes, Blade's Reach damages and slows along a line."},
            {"name": "The assassination", "when": "A carry is isolated behind a wall.",
             "how": "Shadow Step lets you pass through terrain, Umbral Trespass hides you inside the enemy then deals huge damage when you come out."},
            {"name": "The escape", "when": "You need to get away.",
             "how": "Shadow Step lets you pass through terrain to cut off the chase."},
        ],
        "mistakes": [
            "Using the ultimate on a target who cannot heal or flee.",
            "Not choosing your form according to your situation.",
            "Passing through terrain with no exit.",
        ],
    },
    "MonkeyKing": {
        "playstyle": (
            "Wukong is a combat jungler whose armor and regeneration increase in combat (stacking effect). "
            "Crushing Blow reduces armor, Warrior Trickster makes him invisible with a clone, Nimbus Strike dashes him onto a target with images that attack its neighbors, and Cyclone knocks enemies up."
        ),
        "laning": (
            "Crushing Blow has a longer range and reduces the target's armor: open the trade with it. "
            "Your passive gives you defense as the fight goes on."
        ),
        "strengths": [
            "Gains armor and regeneration in combat with champions or monsters.",
            "Warrior Trickster makes him invisible and leaves a clone that attacks in his place.",
            "Cyclone raises his movement speed and knocks the enemies it hits into the air.",
        ],
        "weaknesses": [
            "Has to get close: Nimbus Strike is his main engage.",
            "Warrior Trickster has a long cooldown (18 to 22 s).",
            "His ultimate only works if the enemies stay within reach of his staff.",
        ],
        "teamfight": (
            "Wukong enters a fight by surprise with Warrior Trickster (invisible, clone left behind), dashes with Nimbus Strike onto the target he has chosen and casts Cyclone to knock enemies up. "
            "He is especially effective at isolating a carry."
        ),
        "combos": [
            {"name": "The engage", "when": "An enemy is within Nimbus Strike range.",
             "how": "Nimbus Strike dashes you onto the enemy while sending images that attack nearby enemies, Crushing Blow reduces their armor, Warrior Trickster makes you invisible with a clone."},
            {"name": "The team fight", "when": "Several enemies are grouped.",
             "how": "Warrior Trickster hides you, Cyclone raises your speed and knocks up the enemies it hits."},
            {"name": "The exit", "when": "You are in danger.",
             "how": "Warrior Trickster makes you invisible and dashes you while leaving a clone."},
            {"name": "The invisible entry", "when": "A carry is in the enemy's brawl.",
             "how": "Warrior Trickster makes you invisible and leaves a clone, Nimbus Strike dashes you onto the target with images that attack its neighbors, Cyclone raises your speed and knocks up, Crushing Blow reduces armor."},
        ],
        "mistakes": [
            "Casting Cyclone with no grouped target.",
            "Forgetting the clone from Warrior Trickster.",
            "Using Nimbus Strike with no plan for what follows.",
        ],
    },
    "Nocturne": {
        "playstyle": (
            "Nocturne is a jungler whose attack regularly strikes in an area for bonus damage and a heal. "
            "Duskbringer leaves a Haunt that gives him speed, damage and pass-through of units, Shroud of Darkness blocks an ability, Unspeakable Horror terrifies and Paranoia reduces enemy vision before a leap."
        ),
        "laning": (
            "Your attacks reduce your passive's cooldown: attack often. "
            "Stay in the Haunt to benefit from the speed and damage bonus."
        ),
        "combos": [
            {"name": "The trade", "when": "An enemy is within range.",
             "how": "Duskbringer damages and leaves a Haunt; your attacks in the Haunt are empowered, Unspeakable Horror deals damage every second and terrifies if the target stays in range."},
            {"name": "Protection", "when": "An enemy casts an important ability.",
             "how": "Shroud of Darkness creates a barrier able to block an enemy ability and doubles the attack speed bonus on a block."},
            {"name": "The assassination", "when": "A carry is isolated.",
             "how": "Paranoia reduces the enemies' field of vision and removes their vision of allies; leap onto a nearby champion then chain."},
        ],
        "mistakes": [
            "Using Shroud of Darkness without anticipating the ability to block.",
            "Casting the ultimate with no nearby target.",
            "Leaving the Haunt: you lose your bonus.",
        ],
    },
    "Soraka": {
        "playstyle": (
            "Soraka is a healer: Astral Infusion sacrifices some of her health to heal an ally, Wish heals the whole team from afar, and her passive makes her run faster toward weakened allies. "
            "Starcall slows and heals her if it hits a champion, Equinox silences then roots those who remain."
        ),
        "laning": (
            "Starcall heals you when it hits a champion: harass with it. "
            "Astral Infusion has a short cooldown but costs you health: watch yours."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within range.",
             "how": "Starcall deals magic damage, slows and heals you if a champion is hit."},
            {"name": "Control", "when": "An enemy dives your carry.",
             "how": "Equinox creates a zone that silences all enemies, then roots those still in it when it disappears."},
            {"name": "The global rescue", "when": "Your team is low on health.",
             "how": "Astral Infusion heals an ally by sacrificing your health; Wish instantly restores health to all allies and yourself."},
        ],
        "mistakes": [
            "Spamming Astral Infusion at low health.",
            "Casting the ultimate too early: it heals at the moment of use.",
            "Placing Equinox where the enemies will not stay.",
        ],
    },
    "Fizz": {
        "playstyle": (
            "Fizz is a nimble assassin: he passes through units and benefits from a flat damage reduction against all sources. "
            "Urchin Strike makes him dash through his target, Seastone Trident adds a bleed, Playful / Trickster makes him untargetable, and Chum the Waters throws a fish that attracts a shark."
        ),
        "laning": (
            "Attack with Seastone Trident for the bleed and the empowered damage. "
            "Keep Playful / Trickster to avoid a decisive ability."
        ),
        "combos": [
            {"name": "The burst", "when": "A carry is within range.",
             "how": "Chum the Waters slows the target and makes a shark surge up, knocking them up and pushing nearby enemies back; follow with Seastone Trident, Urchin Strike and Playful / Trickster."},
            {"name": "The trade", "when": "An enemy is within range.",
             "how": "Seastone Trident makes them bleed and empowers your attacks; Urchin Strike makes you dash through the target while dealing magic damage."},
            {"name": "The dodge", "when": "An enemy casts a decisive ability.",
             "how": "Playful / Trickster makes you untargetable; from that position, you can slam the ground or leap again."},
        ],
        "mistakes": [
            "Casting the ultimate without checking the fish's trajectory.",
            "Using Playful / Trickster with no need: its cooldown is long early on.",
            "Not using the pass-through of units to reposition.",
        ],
    },
}
