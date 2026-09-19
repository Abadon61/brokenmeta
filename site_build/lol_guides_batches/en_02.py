"""English guides, batch 2 (combo keys are copied from the French entry by the loader)."""

EN = {
    "Viktor": {
        "playstyle": (
            "Viktor is a mage who gets stronger as the game goes on: every takedown earns him Hex Fragments, and every 100 fragments he permanently upgrades an ability. "
            "Once all four basic abilities are upgraded, he can upgrade his ultimate. His strength is area control: slows, stuns from Gravity Field, and an Arcane Storm he can redirect."
        ),
        "laning": (
            "Siphon Power gives you a shield and empowers your next attack: use it to trade safely. "
            "Every takedown counts double for you, since it brings you closer to an upgrade: prioritize last hits."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within Hextech Ray range.",
             "how": "Siphon Power deals damage, shields you and empowers your attack; follow with the empowered attack, then Hextech Ray, which hits every enemy on its line."},
            {"name": "Area control", "when": "Enemies are grouping around an objective or a turret gate.",
             "how": "Place Gravity Field: enemies who stay in it too long are stunned. Hextech Ray and Siphon Power add damage while they try to leave."},
            {"name": "The ultimate in a team fight", "when": "A team fight is underway.",
             "how": "Arcane Storm deals periodic damage and interrupts enemy channels; you can redirect it to follow targets. If a champion dies after being damaged by it, it grows and lasts longer (upgraded version)."},
        ],
        "mistakes": [
            "Neglecting last hits: your Hex Fragments, and therefore your upgrades, depend on takedowns.",
            "Casting Arcane Storm without redirecting it: it can follow fleeing enemies.",
            "Placing Gravity Field without trapping anyone: it only pays off by keeping enemies inside its area.",
        ],
    },
    "Syndra": {
        "playstyle": (
            "Syndra is a burst mage who plays with her Dark Spheres: they last a few seconds and can be manipulated by her other abilities. "
            "Her passive collects Wrath Shards that upgrade her abilities in several tiers. She finishes targets by bombarding them with all her spheres."
        ),
        "laning": (
            "Place Dark Spheres to harass from a distance and keep some in reserve for your ultimate: the more you have, the harder it hits. "
            "Force of Will can throw a sphere or an enemy minion, and slows whoever it hits."
        ),
        "combos": [
            {"name": "The stun combo", "when": "An enemy is within range of a Dark Sphere.",
             "how": "Place a sphere, then Scatter the Weak pushes it and the enemies: those hit by spheres are stunned. Force of Will throws a sphere or a minion to add damage and a slow."},
            {"name": "The full burst", "when": "A carry is within range of all your spheres.",
             "how": "Build up Dark Spheres, stun with Scatter the Weak, then Unleashed Power bombards the champion with all your spheres. The more you have, the harder it hits."},
            {"name": "The clean-up", "when": "A weakened enemy champion tries to flee.",
             "how": "With your passive tiers unlocked, Unleashed Power executes targets with low health."},
        ],
        "mistakes": [
            "Casting the ultimate with few Dark Spheres: it is much stronger with a full stock.",
            "Using Scatter the Weak with no sphere to push: that is the core of the stun.",
            "Neglecting Wrath Shards: they upgrade your abilities in tiers, so play them to your advantage.",
        ],
    },
    "Caitlyn": {
        "playstyle": (
            "Caitlyn is a zone and range marksman: her traps root enemies and grant her an empowered Headshot, whose range is doubled against targets caught in a trap or net. "
            "She dominates her lane through distance and control, and her ultimate finishes a single target from very long range."
        ),
        "laning": (
            "Place Yordle Snap Traps behind you and on common paths: they reveal and root the champion who triggers them for 1.5 seconds. "
            "Chain the root with Piltover Peacemaker and an empowered Headshot for a very profitable trade."
        ),
        "combos": [
            {"name": "The trap and the shot", "when": "An enemy steps on your trap.",
             "how": "The trap roots, your next attack is an empowered Headshot (doubled range on a trapped target), then Piltover Peacemaker deals damage in a line."},
            {"name": "Defense", "when": "An enemy closes in on you.",
             "how": "90 Caliber Net slows the target and knocks you back to regain distance; place a trap where you land and finish with the piercing shot."},
            {"name": "The long-range execution", "when": "An enemy is very low and visible.",
             "how": "Ace in the Hole takes its time to deal heavy damage to a single target from very long range. Enemy champions can intercept the bullet in place of their ally: check that none is in the way."},
        ],
        "mistakes": [
            "Using the ultimate with an enemy near the target: they can intercept the bullet.",
            "Placing all your traps at once: they have a short cooldown, but good placement beats quantity.",
            "Forgetting that 90 Caliber Net knocks you back: do not use it with a wall behind you.",
        ],
    },
    "Lulu": {
        "playstyle": (
            "Lulu is an enchanter-mage who protects and controls. Pix, her companion, fires guided magic missiles when the champion he follows attacks. "
            "Her strength is turning an enemy into a harmless little creature with Whimsy, or empowering an ally with the same ability, then growing an ally with her ultimate."
        ),
        "laning": (
            "Glitterlance slows a lot: use it to control distance and harass. "
            "Help, Pix! lets you protect an ally by following them, or hurt an enemy and gain vision of them: place it well before the trade."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within Glitterlance range.",
             "how": "Glitterlance fires two projectiles that damage and slow. Help, Pix! on the enemy hurts them and gives you vision of them, then your attacks trigger Pix's shots."},
            {"name": "Protecting the carry", "when": "An enemy dives your carry.",
             "how": "Whimsy on the aggressor stops them from attacking and casting spells; on your ally, it raises their movement and attack speed. Wild Growth knocks up nearby enemies and gives the ally health."},
            {"name": "The team engage", "when": "Your team engages.",
             "how": "Slow with Glitterlance, neutralize the main threat with Whimsy, then grow your tank or carry with the ultimate: it then slows nearby enemies with its aura."},
        ],
        "mistakes": [
            "Using Whimsy on the wrong champion: its cooldown is long.",
            "Casting the ultimate without remembering it knocks up nearby enemies: time it to interrupt their dive.",
            "Neglecting Pix: his shots depend on the attacks of the ally he follows.",
        ],
    },
    "Jayce": {
        "playstyle": (
            "Jayce switches between two forms: Hammer (melee) and Cannon (ranged), gaining movement speed with each switch. "
            "Each form has its own abilities: in Hammer he leaps, damages and knocks back; in Cannon he fires a long-range orb and speeds up his attacks. "
            "His strength comes from mastering the weapon switch at the right time."
        ),
        "laning": (
            "The Cannon lets you harass safely with Shock Blast; switch to Hammer to dive with To the Skies! when the enemy is within burst range. "
            "Switching weapons gives a brief movement speed boost: use it to get away or close in."
        ),
        "combos": [
            {"name": "Harassment in Cannon form", "when": "You are at range and the enemy is in line.",
             "how": "The Acceleration Gate increases the speed, range and damage of a Shock Blast passing through it. Hyper Charge raises your attack speed to its maximum for several attacks."},
            {"name": "The Hammer dive", "when": "An enemy is within leap range.",
             "how": "After the ultimate, To the Skies! leaps you onto the enemy, damages and slows them; Lightning Field and Thundering Blow (magic damage, knockback) complete."},
            {"name": "Engage and retreat", "when": "An enemy is in range and you want to harass them and then get away.",
             "how": "The first switch to Cannon reduces the enemy's armor and magic resistance, the switch back to Hammer deals bonus magic damage: alternate to take advantage of these bonuses."},
        ],
        "mistakes": [
            "Staying too long in a single form: Jayce's strength comes from switching.",
            "Leaping in Hammer form without an exit: you end up in the middle of the enemies.",
            "Forgetting that the ultimate has a very short cooldown (6 s): switch weapons as soon as the moment is right.",
        ],
    },
    "Qiyana": {
        "playstyle": (
            "Qiyana is an elemental assassin: Terrashape enchants her weapon with an element, and her attacks and abilities deal bonus damage as long as she stays enchanted. "
            "Her passive gives bonus damage to the first ability or attack against an enemy. Her ultimate explodes when it hits terrain and stuns nearby enemies."
        ),
        "laning": (
            "Always prepare Terrashape before engaging, since the enchantment depends on the terrain you cross. "
            "Audacity lets you dash onto an enemy: use it wisely, as it is your main way to engage and to escape."
        ),
        "combos": [
            {"name": "The basic combo", "when": "An enemy is within Audacity range.",
             "how": "Terrashape enchants your weapon, Audacity dashes you onto the target (and triggers the bonus damage from your passive), Elemental Wrath applies the element's effect, then your enchanted attacks finish."},
            {"name": "The ultimate against a wall", "when": "An enemy is near a wall or terrain feature.",
             "how": "Supreme Display of Talent sends a shockwave that explodes when it hits terrain, stunning and damaging nearby enemies. Position the target against the terrain before casting."},
            {"name": "The exit", "when": "You need to get away.",
             "how": "Terrashape dashes you toward an area, then Audacity dashes you onto an enemy or a nearby target to extend your movement."},
        ],
        "mistakes": [
            "Casting the ultimate in the middle of open ground with no terrain nearby: it needs to explode.",
            "Engaging without Terrashape: your attacks do not deal the enchantment's bonus damage.",
            "Spending Audacity with no exit plan: it is your main mobility tool.",
        ],
    },
    "Thresh": {
        "playstyle": (
            "Thresh is an engage and protection support. Death Sentence pulls an enemy toward you (or you toward them), Dark Passage protects nearby allies with a lantern they can use to dash toward him, "
            "and The Box traps enemies with walls that slow and damage. His passive collects souls that permanently increase his armor and power."
        ),
        "laning": (
            "Death Sentence is your main ability: place it carefully, since it decides your lane. "
            "Drop the lantern between your carry and the danger, then use Flay to push an enemy away or bring them back under your turret."
        ),
        "combos": [
            {"name": "The hook and the flay", "when": "An enemy is hit by Death Sentence.",
             "how": "Death Sentence binds and pulls the enemy; Flay sends them in the direction of the hit (toward your allies or the turret). Your charged attacks deal more damage if you wait between them."},
            {"name": "The team-fight engage", "when": "The enemy carry is isolated.",
             "how": "A second activation of Death Sentence pulls you toward the enemy, which positions you to drop The Box around them and their allies. Its walls slow and damage those who break them."},
            {"name": "The rescue", "when": "Your carry is being dived.",
             "how": "Dark Passage shields nearby allies from damage, and they can click the lantern to dash to you; Flay pushes the aggressors away."},
        ],
        "mistakes": [
            "Using Death Sentence without checking the minions: they block the path.",
            "Dropping the lantern too far from your allies: they can only use it if they reach it.",
            "Casting The Box when your team is not ready to take advantage of it.",
        ],
    },
    "Locke": {
        "playstyle": (
            "Locke is an assassin-mage whose attacks deal bonus magic damage on hit, increased by the enemy's missing health. "
            "His Ritual Nails mark enemies, and he can consume those marks to deal bonus damage with his attacks. His ultimate executes the enemies it hits and empowers him by sealing champions."
        ),
        "laning": (
            "Mark with Ritual Nails then strike: the mark is what multiplies your attack damage. "
            "Soul Ignition makes you faster but hurts you: only activate it when you can win the trade, since you heal a portion of the damage taken at the end."
        ),
        "combos": [
            {"name": "The trade", "when": "An enemy is within range of the nails.",
             "how": "Ritual Nails mark the target, your attacks consume the marks for bonus damage, Soul Ignition raises your attack and movement speed."},
            {"name": "The chase engage", "when": "An enemy is out of range.",
             "how": "Ashen Pursuit teleports you and then dashes you onto the next target, damaging the enemies you cross. Mark and attack as soon as you arrive."},
            {"name": "The execution", "when": "An enemy is low.",
             "how": "Purgatory deals damage and can execute the enemies it hits; by sealing champions, Locke gains extra power."},
        ],
        "mistakes": [
            "Activating Soul Ignition with no target to hit: it damages you for nothing in return.",
            "Casting Purgatory on full-health enemies: it is mostly a finisher.",
            "Forgetting to consume your marks with attacks.",
        ],
    },
    "Lux": {
        "playstyle": (
            "Lux is a long-range mage who controls with Light Binding and Lucent Singularity, protects with Prismatic Barrier and finishes with Final Spark. "
            "Her abilities charge the target with energy, and her next attack ignites that energy for bonus magic damage."
        ),
        "laning": (
            "Light Binding roots up to two enemies: cast it from long range and follow up. "
            "Prismatic Barrier shields allies it touches on the way out and on the way back: place it to hit your carry."
        ),
        "combos": [
            {"name": "The root combo", "when": "An enemy is within range of the binding.",
             "how": "Light Binding roots and damages, Lucent Singularity slows then explodes, and your basic attack ignites the Illumination energy."},
            {"name": "The finishing ultimate", "when": "Enemies are lined up or weakened.",
             "how": "Final Spark fires a beam that deals damage in its area and triggers your passive: Illumination is refreshed on the targets hit. Finish with an attack."},
            {"name": "Protection", "when": "Your team is engaged.",
             "how": "Prismatic Barrier shields the allies it touches from damage, Lucent Singularity slows the chasers."},
        ],
        "mistakes": [
            "Casting Light Binding without checking the minions: it stops after two units.",
            "Triggering Lucent Singularity too early: the explosion deals the damage, so let it slow first.",
            "Using the ultimate without checking the trajectory.",
        ],
    },
    "Zed": {
        "playstyle": (
            "Zed is an energy assassin who plays with his shadows: Razor Shuriken and Shadow Slash are cast by him and his shadows at the same time. "
            "He regains energy when his shadows and he hit the same enemy with the same ability. His ultimate makes him untargetable, teleports him onto a champion and marks the target for a delayed explosion."
        ),
        "laning": (
            "Living Shadow lets you harass with two sources of damage: position the shadow before Razor Shuriken to hit twice. "
            "Energy is your resource: do not waste it, since every ability costs some."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within shuriken range.",
             "how": "Living Shadow sends the shadow forward, Razor Shuriken is thrown by you and your shadow, and your attacks use the bonus from your passive against low-health targets."},
            {"name": "The assassination burst", "when": "A carry is within range of the ultimate.",
             "how": "Death Mark makes you untargetable and teleports you; strike with your shadows and abilities. After 3 seconds the mark explodes and deals a percentage of all the damage you dealt during the mark."},
            {"name": "The escape", "when": "You need to get away.",
             "how": "Reactivating Living Shadow swaps your position with the shadow: place it far away first, then swap."},
        ],
        "mistakes": [
            "Attacking with the ultimate without finishing within 3 seconds: the mark explodes and its explosion depends on the damage you dealt.",
            "Spending all your energy without landing anything: your passive only refunds it if the ability hits.",
            "Using Living Shadow without planning the position swap.",
        ],
    },
}
