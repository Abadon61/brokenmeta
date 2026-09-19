"""English guides, batch 11."""

EN = {
    "Orianna": {
        "playstyle": (
            "Orianna is a mage who plays with her ball: every ability gives it an order (Attack, Dissonance, Protect, Shockwave), and the ball stays in the targeted area. "
            "Her passive deals increasing damage on the same target, and her ultimate pulls enemies toward the ball after a short delay."
        ),
        "laning": (
            "Command: Attack sends the ball to an area, hitting targets along the way. "
            "Position the ball: Dissonance and Shockwave come from it, not from you."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within range.",
             "how": "Command: Attack sends the ball, which stays in the area; Command: Dissonance deals damage around it and creates a zone that slows enemies and speeds up your allies; your attack benefits from your passive."},
            {"name": "Protection", "when": "Your carry is being dived.",
             "how": "Command: Protect attaches the ball to an ally: a shield, armor and magic resistance, and damage to enemies along its path."},
            {"name": "The gathering ultimate", "when": "Enemies are around the ball.",
             "how": "Shockwave pulls nearby enemies toward the ball after a short delay: place it in the middle of your team or on the target."},
        ],
        "mistakes": [
            "Forgetting where your ball is: your abilities come from it.",
            "Casting the ultimate without a well-placed ball.",
            "Using Protect on an ally who is not under threat.",
        ],
    },
    "Shyvana": {
        "playstyle": (
            "Shyvana is a jungler who gains defense by taking down champions, large minions and large monsters (Scalemail). "
            "Her ultimate turns her into a dragon, which empowers her abilities: Emberstrike gains a recast, Inferno Aegis heals her, and Molten Burst passes through enemies leaving a trail of fire."
        ),
        "laning": (
            "Emberstrike hits the target and the area around it; recast it. "
            "Inferno Aegis gives you a shield and speed before exploding."
        ),
        "combos": [
            {"name": "The trade", "when": "An enemy is within range.",
             "how": "Emberstrike hits the target and the area, recast it; Inferno Aegis protects you and explodes after a short delay."},
            {"name": "Dragon form", "when": "A fight begins.",
             "how": "Dragon's Descent turns you into a dragon and makes enemies flee in your path; Emberstrike gains a recast dealing huge damage to a single target, Molten Burst passes through leaving a trail of fire."},
            {"name": "The heal", "when": "You are hurt in dragon form.",
             "how": "In dragon form, the explosion of Inferno Aegis heals you if it hits an enemy champion."},
        ],
        "mistakes": [
            "Using the ultimate too early: dragon form is your window.",
            "Forgetting Emberstrike's recast.",
            "Neglecting Scalemail: it improves your resistances on takedowns.",
        ],
    },
    "Gragas": {
        "playstyle": (
            "Gragas is a fighter-mage who heals with every ability. "
            "Barrel Roll slows and explodes (manually or after 4 seconds, with more power over time), Body Slam stuns, Drunken Rage reduces the damage he takes, and Explosive Cask knocks enemies back."
        ),
        "laning": (
            "Every ability heals you thanks to your passive. "
            "Drunken Rage gives you damage reduction and an attack that damages all nearby enemies."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within barrel range.",
             "how": "Barrel Roll explodes on demand, its power increases over time and it slows; Drunken Rage sets up an area attack."},
            {"name": "The engage", "when": "Several enemies are grouped.",
             "how": "Body Slam charges and stuns every enemy near the first one hit; Explosive Cask knocks back the enemies hit by the explosion."},
            {"name": "Defense", "when": "You are being targeted.",
             "how": "Drunken Rage reduces the damage you take and deals damage to all nearby enemies with your next attack."},
        ],
        "mistakes": [
            "Detonating the barrel too early: its power grows with time.",
            "Casting the ultimate and knocking enemies back toward their allies.",
            "Using Body Slam with no plan for what follows.",
        ],
    },
    "Zilean": {
        "playstyle": (
            "Zilean is a time support-mage: Time Bomb sticks to a unit and explodes after 3 seconds, Rewind reduces his abilities' cooldowns, Time Warp slows an enemy or speeds up an ally, and Chronoshift sends an ally back in time if they take lethal damage. "
            "His passive stores experience he can give to an ally."
        ),
        "laning": (
            "Place bombs on enemies and minions: they stick to the first nearby unit, prioritizing champions. "
            "A bomb that explodes early because of another one stuns."
        ),
        "combos": [
            {"name": "The stun", "when": "An enemy is within bomb range.",
             "how": "Throw a bomb, then a second: if one bomb explodes early because of another, the enemies are stunned; Time Warp slows the target."},
            {"name": "Tempo", "when": "You want to recast your bombs fast.",
             "how": "Rewind reduces the cooldown of your other abilities: immediately recast Time Bomb."},
            {"name": "Protection", "when": "Your carry is about to die.",
             "how": "Chronoshift places a rune on an ally that sends them back in time if they take lethal damage; Time Warp speeds up your team."},
        ],
        "mistakes": [
            "Placing the ultimate on an ally too late: it has to be placed before the lethal damage.",
            "Placing a bomb with no target approaching.",
            "Forgetting your passive: give experience to an ally.",
        ],
    },
    "Aphelios": {
        "playstyle": (
            "Aphelios is a marksman with five Lunari weapons: he carries two at a time (main and secondary), and each weapon has a unique attack and ability. "
            "Attacks and abilities consume ammo; when out of ammo, the weapon is dropped and Alune summons the next one. Phase swaps the two weapons."
        ),
        "laning": (
            "Learn the weapon order: the third slot tells you which one is next. "
            "Each weapon has its own active ability: Calibrum marks, Severum runs while attacking, Gravitum roots, Infernum hits in a cone, Crescendum deploys a turret."
        ),
        "combos": [
            {"name": "Long-range harassment", "when": "Your main weapon is Calibrum.",
             "how": "Calibrum fires a long-range bullet that marks the target and allows a second attack at very long range; Phase swaps your weapons to chain."},
            {"name": "The team fight", "when": "A team fight is underway.",
             "how": "Choose the weapon whose ability serves best: Infernum hits in a cone with the secondary weapon, Crescendum deploys a turret that attacks, Gravitum roots the slowed enemies."},
            {"name": "The weapon ultimate", "when": "A group of enemies is lined up.",
             "how": "Moonlight Vigil fires a beam that explodes on contact with an enemy champion and applies the unique effect of your main weapon."},
        ],
        "mistakes": [
            "Not watching your ammo: a weapon with no ammo is dropped.",
            "Using the ultimate without looking at your main weapon: the effect depends on it.",
            "Forgetting Phase: swapping weapons changes your attack and ability.",
        ],
    },
    "Lissandra": {
        "playstyle": (
            "Lissandra is an ice and control mage: Ice Shard damages and slows, Ring of Frost roots nearby enemies, Glacial Path carries her to her claw, and her ultimate can freeze an enemy or entomb herself to heal. "
            "Her passive turns champions who die near her into Ice Minions that explode."
        ),
        "laning": (
            "Ice Shard passes through the target and damages the enemies behind: cast it along the axis. "
            "Glacial Path lets you reposition: recast it to teleport to your claw."
        ),
        "combos": [
            {"name": "The engage", "when": "An enemy is within claw range.",
             "how": "Glacial Path throws a claw and carries you to it; Ring of Frost freezes and roots nearby enemies; Ice Shard finishes."},
            {"name": "Control", "when": "A carry is isolated.",
             "how": "Frozen Tomb on an enemy champion freezes and stuns them; dark ice spreads from the target and slows nearby enemies."},
            {"name": "Survival", "when": "You are in danger.",
             "how": "Cast on yourself, Frozen Tomb entombs you in ice: you heal, become untargetable and immune to damage."},
        ],
        "mistakes": [
            "Casting Glacial Path into nothing.",
            "Using the ultimate on yourself too early: you cannot act during it.",
            "Forgetting Ice Minions: they slow and explode.",
        ],
    },
    "Veigar": {
        "playstyle": (
            "Veigar is a mage who gains permanent power: hitting a champion with an ability, killing a champion or assisting gives him power. "
            "Baleful Strike, on units it kills, gives some too. Event Horizon creates a cage that stuns, and Primordial Burst deals damage that increases with the target's missing health."
        ),
        "laning": (
            "Baleful Strike hits two enemies: kill minions with it to gain power. "
            "Dark Matter has its cooldown reduced by your power stacks."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within range.",
             "how": "Baleful Strike damages the first two enemies, Dark Matter drops dark matter for magic damage."},
            {"name": "The cage", "when": "An enemy is being chased.",
             "how": "Event Horizon creates a cage that stuns enemies crossing it: place it around an enemy or your team to engage."},
            {"name": "The execution", "when": "A champion is low.",
             "how": "Primordial Burst deals heavy damage that increases with the target's missing health: chain to finish."},
        ],
        "mistakes": [
            "Casting the ultimate on a full-health enemy.",
            "Neglecting farm with Baleful Strike: it is your power.",
            "Placing Event Horizon where the enemies will not pass.",
        ],
    },
    "Riven": {
        "playstyle": (
            "Riven is a burst fighter: her abilities charge her blade, which lets her basic attacks deal bonus damage by consuming charges. "
            "Broken Wings can be recast three times (the third hit knocks back), Ki Burst stuns, Valor moves her forward while blocking damage, and Blade of the Exile raises her damage and range with Wind Slash."
        ),
        "laning": (
            "Chain ability and attack to consume your blade's charges. "
            "Broken Wings can be recast twice within a short time."
        ),
        "combos": [
            {"name": "The burst", "when": "An enemy is within range.",
             "how": "Valor brings you closer while blocking damage, Ki Burst stuns nearby enemies, three Broken Wings with attacks in between, the third hit knocks back."},
            {"name": "The finishing ultimate", "when": "An enemy is low.",
             "how": "Blade of the Exile raises your attack damage and range; during the effect, you can use Wind Slash once, a powerful ranged attack."},
            {"name": "The exit", "when": "You need to get away.",
             "how": "Valor moves you and blocks damage, Broken Wings moves you forward again."},
        ],
        "mistakes": [
            "Wasting charges: chain attack and ability.",
            "Using Broken Wings three times with no target.",
            "Casting Wind Slash too early: it is a single use per ultimate.",
        ],
    },
    "Mel": {
        "playstyle": (
            "Mel is a mage who accumulates bonus projectiles (up to nine) with each ability for her next attack, and applies Overwhelm, which stacks infinitely. "
            "If there are enough stacks on a target, they are consumed to execute it. Golden Eclipse hits all marked enemies regardless of distance."
        ),
        "laning": (
            "Chain abilities to charge your next attack with bonus projectiles. "
            "Rebuttal reflects enemy projectiles back to the sender: keep it for a decisive ranged ability."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within range.",
             "how": "Radiant Volley deals repeated area damage, Solar Snare roots at the center and slows at the edge, your attack benefits from the bonus projectiles."},
            {"name": "Protection", "when": "An enemy fires projectiles.",
             "how": "Rebuttal creates a barrier that reflects enemy projectiles back to the sender, protects you and raises your movement speed."},
            {"name": "The execution", "when": "Several enemies are marked.",
             "how": "Golden Eclipse hits all enemies marked by Overwhelm regardless of distance, with bonus damage per stack."},
        ],
        "mistakes": [
            "Wasting Rebuttal on minions.",
            "Casting the ultimate without having stacked Overwhelm.",
            "Attacking without a previous ability: you lose your bonus projectiles.",
        ],
    },
    "Sion": {
        "playstyle": (
            "Sion is a tank who comes back to life after dying, with very fast attacks that heal him and deal damage based on the target's max health. "
            "Decimating Smash charges to knock up and stun, Soul Furnace gives a shield and max health on kills, and Unstoppable Onslaught charges while accelerating."
        ),
        "laning": (
            "Decimating Smash: charge it long enough to knock up and stun. "
            "Soul Furnace gives you a shield; killing enemies passively raises your max health."
        ),
        "combos": [
            {"name": "The stun", "when": "An enemy is within range.",
             "how": "A Decimating Smash charged long enough knocks up and stuns; Roar of the Slayer damages, slows and reduces armor."},
            {"name": "The engage ultimate", "when": "An enemy is far away.",
             "how": "Unstoppable Onslaught charges while accelerating and you can slightly change your path; the impact knocks up based on the distance traveled."},
            {"name": "The shield", "when": "You are engaged.",
             "how": "Soul Furnace surrounds you with a shield; recast it after 3 seconds to deal magic damage to nearby enemies."},
        ],
        "mistakes": [
            "Releasing Decimating Smash too early: it only knocks up after a long enough charge.",
            "Casting the ultimate with no direction: it accelerates and does not stop.",
            "Forgetting your passive: you come back temporarily to life.",
        ],
    },
}
