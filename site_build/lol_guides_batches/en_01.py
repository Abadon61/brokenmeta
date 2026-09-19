"""English guides, batch 1 (translations of the French editorial, using the official English ability names)."""

EN = {
    "Ahri": {
        "playstyle": (
            "Ahri is a mobile mage who wins games by catching an isolated enemy with Charm and burning them down before they can react. "
            "Orb of Deception deals magic damage on the way out and true damage on the way back, which keeps it effective even against targets stacking magic resistance. "
            "Her ultimate gives her three dashes and can be recast when she takes part in a takedown: she is at her best when she chains kills, "
            "and at her worst when she engages badly, because without her ultimate her survivability is very limited."
        ),
        "laning": (
            "Early on, poke with Orb of Deception at maximum range and only spend Fox-Fire to finish a target or get out. "
            "The mana cost of Orb of Deception rises with each level, so check your mana bar before trading. "
            "Your passive heals you after 9 minion kills, so farming cleanly makes up for part of the enemy's harassment."
        ),
        "combos": [
            {"name": "The basic combo (pick)", "keys": ["E", "Q", "W"], "when": "An enemy is within Charm range and no minion blocks the path.",
             "how": "Cast Charm first: it interrupts the target's movement abilities and makes them walk toward you, which guarantees the rest lands. "
                    "Follow up with Orb of Deception, then Fox-Fire, whose fireballs lock on and attack nearby enemies while you reposition."},
            {"name": "The ultimate engage", "keys": ["R", "E", "Q", "W"], "when": "The target is too far for a direct Charm, or you want to close the distance at once.",
             "how": "Spirit Rush opens the way: it brings you closer, lets you land Charm, helps you hit twice with Orb of Deception "
                    "and puts you in range of Fox-Fire. Keep a recast in reserve, since the ultimate can be cast up to three times."},
            {"name": "The team-fight clean-up", "keys": ["E", "R", "R", "R"], "when": "The fight is going your way and you are chasing the last enemies.",
             "how": "Charm the first runner, then chain Spirit Rush recasts: Ahri gains more by taking part in enemy champion takedowns. "
                    "Keep the last one to get back to your team if the fight turns."},
        ],
        "mistakes": [
            "Casting Charm without checking the minions: the first enemy hit is the one charmed, and it is rarely the right one.",
            "Using the ultimate to open a fight without knowing whether you can recast it: without it, you have almost no survivability left.",
            "Forgetting that Orb of Deception also hits on the way back: position yourself so the target is on its path in both directions.",
        ],
    },
    "Jinx": {
        "playstyle": (
            "Jinx is a marksman who becomes dominant as soon as she is well protected. Her passive gives her a huge movement and attack speed bonus "
            "on every takedown, letting her chain kills in a fight that is already well engaged. She alternates between the minigun, which ramps up attack speed, "
            "and the rocket launcher, which hits in an area at longer range but costs mana. Her weakness is a lack of defense: if her chompers miss, she is vulnerable."
        ),
        "laning": (
            "Use rockets on minions to hit nearby enemy champions without drawing their attention, and switch to the minigun as soon as an enemy gets too close. "
            "Keep your Flame Chompers to defend yourself: their long cooldown makes them your main protection. "
            "Zap! slows and reveals the target at very long range, ideal to set up a trade."
        ),
        "combos": [
            {"name": "The fringe of the team fight", "keys": ["W", "AA", "AA"], "when": "A fight breaks out and your team is protecting you.",
             "how": "Stay on the edge of the fight, use Zap! then your rockets, and only pull out the minigun when it is safe. "
                    "Each takedown triggers your passive: the speed you gain lets you chain onto the next target."},
            {"name": "Defending against a diver", "keys": ["E", "W", "Q", "AA"], "when": "An enemy jumps on you.",
             "how": "Place Flame Chompers on their path: they root the enemy when stepped on. Slow them with Zap!, "
                    "then swap back to the minigun with Switcheroo! to finish them at close range."},
            {"name": "The ultimate to finish a target", "keys": ["R"], "when": "A weakened enemy is fleeing or standing far from you.",
             "how": "Super Mega Death Rocket crosses the map and its damage grows during its flight, based on the target's missing health: "
                    "the farther you are from the target, the harder the ultimate hits. Fire it from afar to secure a kill or a chase."},
        ],
        "mistakes": [
            "Spamming rockets when an enemy is next to you: the minigun takes time to ramp up its attack speed.",
            "Wasting your chompers at the start of a fight: without them, you have no defense.",
            "Using the ultimate up close: the closer the target, the less damage it deals.",
        ],
    },
    "Darius": {
        "playstyle": (
            "Darius is a fighter who gets stronger the longer a fight lasts. His attacks and abilities cause bleeding (Hemorrhage, up to 5 stacks); "
            "at five stacks he goes into a rage and gains a huge attack damage bonus. Decimate heals him based on the champions hit by the blade, "
            "and Apprehend pulls enemies toward him. His ability to escape is limited: he wants a prolonged close-range fight, not a chase."
        ),
        "laning": (
            "Hit with the blade of Decimate, on the outer edge of the axe, to get the most damage and healing while staying at the limit of your range. "
            "Stack Hemorrhage with your attacks between abilities. During the cooldown of Apprehend you are vulnerable to harassment: "
            "avoid exposing yourself when it is not available."
        ),
        "combos": [
            {"name": "The lane trade", "keys": ["Q", "AA", "W", "AA"], "when": "You want to trade without fully committing.",
             "how": "Decimate at the edge of its range so the blade connects, an attack to stack Hemorrhage, then Crippling Strike on the next attack: "
                    "the bleed slows the target and stops them from leaving."},
            {"name": "The full engage (kill)", "keys": ["E", "W", "AA", "Q", "AA", "R"], "when": "An enemy is within Apprehend range and you want the kill.",
             "how": "Apprehend pulls them in, Crippling Strike slows them, your attacks and Decimate stack Hemorrhage (up to 5 stacks) and heal you. "
                    "Finish with Noxian Guillotine: its true damage grows with the number of stacks on the target, so do not cast it too early."},
            {"name": "The team-fight chain", "keys": ["R", "R"], "when": "A weakened enemy is within Guillotine range in a team fight.",
             "how": "If Noxian Guillotine kills its target, its cooldown is reset for a short time: recast it right away on the next weakened enemy. "
                    "Keep a stacked target for the second cast."},
        ],
        "mistakes": [
            "Casting Noxian Guillotine without Hemorrhage stacks: its damage depends on them.",
            "Engaging without Apprehend when the opponent can harass you: you are fragile during its cooldown.",
            "Trying to chase: your ability to escape or catch up is limited, force a close-range fight instead.",
        ],
    },
    "Yone": {
        "playstyle": (
            "Yone is a fighter-assassin who alternates physical and magic hits: one attack out of two deals magic damage, which makes his damage hard to counter with a single type of resistance. "
            "He wins games by stacking Mortal Steel to knock enemies into the air, then closing the fight with Fate Sealed, which gathers the enemies it hits. "
            "Soul Unbound is the key to his kit: part of the damage dealt as a spirit is repeated when he returns to his body."
        ),
        "laning": (
            "Chain basic attacks and Mortal Steel to stack the Storm Surge effect; two stacks let you dash and knock the target up. "
            "Spirit Cleave gives you a shield proportional to the number of champions hit: save it for a trade, not for minions."
        ),
        "combos": [
            {"name": "The lane trade", "keys": ["Q", "AA", "Q", "W"], "when": "You want to trade without spending Soul Unbound.",
             "how": "Two Mortal Steels close together trigger the dash and the knock-up; slip an attack in between to benefit from his passive, then Spirit Cleave for the shield."},
            {"name": "The spirit engage", "keys": ["E", "Q", "AA", "W", "E"], "when": "An enemy is in range and you want to maximize the repeated damage.",
             "how": "Leave your body with Soul Unbound, deal as much damage as possible while you are a spirit, then recast it: part of that damage is repeated. "
                    "The combo has to fit within its limited duration, so start it in range."},
            {"name": "The team-fight combo", "keys": ["Q", "Q", "R", "Q", "W"], "when": "Several enemies are lined up.",
             "how": "Knock a target up with the tornado, then Fate Sealed teleports you behind the last champion hit on the line and pulls every enemy hit toward you. "
                    "Finish with Mortal Steel and Spirit Cleave to take advantage of the clumping."},
        ],
        "mistakes": [
            "Using Fate Sealed without an ally to follow up: the ultimate puts you in the middle of the enemy team.",
            "Casting Soul Unbound with nothing to hit: the repeated damage depends on what you deal during the spirit.",
            "Wasting Spirit Cleave on minions: its shield grows with the champions hit.",
        ],
    },
    "LeeSin": {
        "playstyle": (
            "Lee Sin is a jungler built on mobility and initiative. He chains two-part abilities (Sonic Wave / Resonating Strike, Safeguard / Iron Will, Tempest / Cripple) to chase, protect or escape. "
            "His passive speeds up his next two attacks after each ability, which rewards fast chains. His ultimate kicks the target backward and damages whoever it hits."
        ),
        "laning": (
            "In the jungle, keep some energy: each two-part ability costs some. Use Tempest to reveal enemies and Sonic Wave to engage. "
            "Safeguard lets you dash to an ally, which works as well to protect them as to join a fight."
        ),
        "combos": [
            {"name": "The classic pick", "keys": ["Q", "Q", "AA", "E", "AA"], "when": "An enemy is isolated within Sonic Wave range.",
             "how": "Sonic Wave connects, Resonating Strike carries you to the target (damage based on their missing health). "
                    "Follow with the fast attacks from your passive and Tempest to reveal and slow."},
            {"name": "The ultimate engage", "keys": ["Q", "Q", "R"], "when": "You want to remove a carry from their position.",
             "how": "After Resonating Strike, Dragon's Rage kicks the target backward: it damages the enemies it hits and knocks them up briefly. "
                    "Aim at a target that will cross their line."},
            {"name": "The escape or the reinforcement", "keys": ["W", "W", "E"], "when": "An ally is in danger or you need to get out.",
             "how": "Safeguard dashes you to an ally (who is also shielded if a champion), then Iron Will gives you omnivamp. "
                    "Tempest and Cripple slow whoever is chasing."},
        ],
        "mistakes": [
            "Recasting Resonating Strike too late: you have 3 seconds after Sonic Wave lands.",
            "Casting Sonic Wave without enough energy left for the second part.",
            "Using Dragon's Rage without looking behind the target: enemies it hits are damaged and knocked up, so aim at a target that crosses their line rather than yours.",
        ],
    },
    "Jhin": {
        "playstyle": (
            "Jhin is a precision marksman with a fixed rate of fire: he fires four shots before reloading, and the fourth always critically strikes and deals bonus damage. "
            "He plays around the root (Deadly Flourish) and Lotus Traps to lock down a target, before finishing them from very long range with his ultimate."
        ),
        "laning": (
            "Your fourth shot is the strongest: aim it at a champion. Dancing Grenade deals more damage after each kill, so take last hits on minions with it. "
            "Place Lotus Traps on common paths; they slow and damage an enemy that steps on them."
        ),
        "combos": [
            {"name": "Locking down the lane", "keys": ["E", "W", "Q", "AA"], "when": "An enemy is stuck behind their minions or has already been hit.",
             "how": "Lotus Trap to slow, then Deadly Flourish: if the target was recently damaged by you or an ally, they are rooted. "
                    "Dancing Grenade and the fourth shot finish."},
            {"name": "The team fight", "keys": ["W", "AA", "AA", "AA", "AA"], "when": "Your team engages and you are protected.",
             "how": "Root with Deadly Flourish after an ally's first hit, then chain your four shots: the last is a guaranteed critical strike. "
                    "Do not forget the movement speed gained on each crit."},
            {"name": "The long-range finish", "keys": ["R", "R", "R", "R"], "when": "A weakened enemy is in your line of fire.",
             "how": "Curtain Call gives you four very long-range shots that stop at the first champion hit and cripple them. "
                    "The fourth shot always critically strikes: keep it for the finish."},
        ],
        "mistakes": [
            "Reloading at the wrong time: reloading leaves you without damage for a moment, especially up close.",
            "Casting the ultimate without noticing the enemy in the way: the shot stops at the first champion hit.",
            "Placing Lotus Traps at random: they only trigger when an enemy walks on them, so place them on likely paths.",
        ],
    },
    "Sylas": {
        "playstyle": (
            "Sylas is a fighter-mage who wins long trades. After each ability, his passive stores a charge that makes his next attack faster and more dangerous. "
            "Kingslayer heals him against champions, and his ultimate lets him steal an enemy's ultimate ability: his potential depends as much on his targets as on himself."
        ),
        "laning": (
            "Cast Chain Lash across your opponent's path to slow them and make the chain intersection explode. "
            "Keep Kingslayer for a profitable trade, since it heals you when it hits a champion. Your passive makes every chain stronger: avoid casting a single isolated ability."
        ),
        "combos": [
            {"name": "The lane combo", "keys": ["Q", "AA", "W", "AA"], "when": "You want a short, profitable trade.",
             "how": "Chain Lash to slow, an attack with the passive charge, then Kingslayer to heal and deal damage."},
            {"name": "The chain engage", "keys": ["E", "E", "W", "Q", "AA"], "when": "The target is too far for Kingslayer.",
             "how": "Abscond dashes you in a direction; recast it to throw your chains and pull yourself toward the enemy hit. Follow with Kingslayer and Chain Lash."},
            {"name": "Stealing an ultimate", "keys": ["R"], "when": "An enemy has just used a useful ultimate, or one you can reuse.",
             "how": "Hijack lets you cast an enemy's ultimate freely. Pick the right moment: a stolen ultimate that hits no one is a free turn for the opponent."},
        ],
        "mistakes": [
            "Stealing an ultimate without knowing how it works: read it first, since every ultimate plays differently.",
            "Casting Chain Lash without letting the intersection explode: the second effect has a delay.",
            "Using Kingslayer without a champion target: the heal only applies against champions.",
        ],
    },
    "Yunara": {
        "playstyle": (
            "Yunara is a marksman whose critical strikes deal bonus magic damage. Cultivation of Spirit gives her attack speed and bonus on-hit damage and makes her attacks bounce onto nearby enemies, "
            "which makes her strong in team fights. Her Transcend improves her basic abilities and replaces some with more dangerous versions."
        ),
        "laning": (
            "Keep Kanmei's Steps to reposition or get out. Arc of Judgment slows at range: use it to chase or to keep an enemy at a good distance. "
            "Wait for your Transcend to engage fully: its upgraded versions change the nature of her abilities."
        ),
        "combos": [
            {"name": "The team fight", "keys": ["R", "Q", "W", "AA"], "when": "A team fight starts and you are protected.",
             "how": "Enter Transcend to upgrade your abilities, then cast Cultivation of Spirit: attack speed, bonus on-hit damage and bounces on nearby enemies. Slow with the Transcend beam."},
            {"name": "Harassment", "keys": ["W", "AA", "AA"], "when": "You want to slow and hit from range.",
             "how": "Arc of Judgment deals damage and slows; follow with basic attacks as long as the enemy stays in range."},
            {"name": "Getting out of danger", "keys": ["E", "W"], "when": "An enemy jumps on you.",
             "how": "Kanmei's Steps gives you movement speed and makes you ghostly; in Transcend it becomes a dash. Then slow the chaser with Arc of Judgment."},
        ],
        "mistakes": [
            "Triggering Transcend too early: it is your main power window, with a long cooldown.",
            "Using Kanmei's Steps out of reflex rather than for a precise position.",
            "Staying at close range: your advantage comes from distance and the slow.",
        ],
    },
    "Kaisa": {
        "playstyle": (
            "Kai'Sa is a marksman-mage who chains Plasma effects: each attack applies stacks, and her allies' immobilizing effects add some too. "
            "Her items upgrade her basic abilities (Living Weapon), which changes her playstyle depending on her build. Her ultimate dashes her to an enemy champion, ideal for an execution."
        ),
        "laning": (
            "Mark with Void Seeker at long range to stack Plasma, then attack to finish the stacks. Icathian Rain deals area damage around you: use it at point-blank range. "
            "Supercharge helps you reposition; upgraded, it gives you a brief invisibility."
        ),
        "combos": [
            {"name": "Lane harassment", "keys": ["W", "AA", "AA", "Q"], "when": "An enemy is within range of the beam.",
             "how": "Void Seeker marks with your passive, your basic attacks complete the stacks, then Icathian Rain deals its damage on nearby targets."},
            {"name": "The execution", "keys": ["R", "Q", "AA", "AA"], "when": "A carry is isolated or weakened.",
             "how": "Killer Instinct dashes you to an enemy champion; immediately follow with Icathian Rain and your attacks. Make sure you have a way out before diving."},
            {"name": "The team fight", "keys": ["E", "AA", "AA", "W"], "when": "Your team engages and you are at range.",
             "how": "Supercharge boosts your movement speed then attack speed. Stay on the edge and use Void Seeker to mark: your allies' immobilizing effects add Plasma."},
        ],
        "mistakes": [
            "Using the ultimate to open a fight without an exit: it puts you right next to the enemies.",
            "Ignoring how your items upgrade your abilities: the item you choose changes what each ability does.",
            "Casting Supercharge with no purpose: it is your repositioning tool, not a damage ability.",
        ],
    },
    "Yasuo": {
        "playstyle": (
            "Yasuo is a melee fighter with constant mobility. His passive gives him increased critical strike chance and a shield that fills as he moves. "
            "He stacks Steel Tempest to knock enemies into the air, which enables his ultimate, and Wind Wall blocks enemy projectiles, a decisive tool against marksmen and mages."
        ),
        "laning": (
            "Use Sweeping Blade on minions to close in on the enemy, and stack Steel Tempest to trigger the tornado. "
            "Keep Wind Wall to block an important ability rather than casting it out of habit: its cooldown is long."
        ),
        "combos": [
            {"name": "The tornado combo", "keys": ["E", "Q", "Q"], "when": "An enemy is within dash range.",
             "how": "Sweeping Blade dashes you through a target; Steel Tempest cast during the dash delivers a circular strike; two stacks of Gathering Storm then make a tornado that knocks the target up."},
            {"name": "The ultimate after a knock-up", "keys": ["Q", "Q", "R"], "when": "An enemy is knocked into the air.",
             "how": "Last Breath can only target a champion that is already airborne: cast it the moment the tornado connects, and benefit from the armor penetration bonus on your critical strikes."},
            {"name": "Protecting against marksmen", "keys": ["W"], "when": "The enemy marksmen are targeting your team.",
             "how": "Wind Wall blocks enemy projectiles for 4 seconds. Place it between your team and their ranged damage sources before they fire."},
        ],
        "mistakes": [
            "Using the ultimate without an airborne target: it cannot be cast on its own.",
            "Wasting Wind Wall outside important fights.",
            "Dashing onto minions that leave you under a tower or in the enemy's line of fire.",
        ],
    },
    "Ezreal": {
        "playstyle": (
            "Ezreal is a marksman who plays with his abilities more than his attacks. Every ability that hits gives him attack speed (up to 5 stacks), and Mystic Shot reduces his cooldowns when it lands. "
            "He harasses from range and repositions with Arcane Shift, never overexposing himself."
        ),
        "laning": (
            "Mystic Shot is your main tool: each hit reduces your cooldowns, so aim at real targets, champions or minions. "
            "Mark with Essence Flux to set up a trade: the orb detonates if you hit the marked target."
        ),
        "combos": [
            {"name": "Harassment", "keys": ["W", "Q", "AA"], "when": "An enemy is within range of Essence Flux.",
             "how": "Place the orb on the target, hit them with Mystic Shot or an attack to detonate it; each hit reduces your cooldowns and adds attack speed."},
            {"name": "Dodge and retaliate", "keys": ["E", "Q", "W"], "when": "An enemy jumps on you.",
             "how": "Arcane Shift teleports you and fires at the nearest enemy, prioritizing one marked by Essence Flux. Use the distance to retaliate with your other abilities."},
            {"name": "The ultimate in a fight", "keys": ["R"], "when": "A team fight starts and several enemies line up.",
             "how": "Trueshot Barrage crosses every unit on its line for heavy damage (reduced against minions and non-epic monsters). Cast it along a line of enemies."},
        ],
        "mistakes": [
            "Casting Arcane Shift without knowing where to stand: it is your escape, not your engage.",
            "Wasting Mystic Shot on nothing: each hit reduces your cooldowns.",
            "Forgetting that the ultimate crosses the whole map: check the lines before firing.",
        ],
    },
    "Nautilus": {
        "playstyle": (
            "Nautilus is a control tank who wins by catching an enemy: Dredge Line pulls both toward each other, then his attacks briefly root thanks to his passive. "
            "His ultimate chases a chosen enemy, knocks them up and stuns them, making it one of the best engage tools in the game."
        ),
        "laning": (
            "Only cast Dredge Line blind if the path is clear: it stops at the first enemy or obstacle hit. "
            "Titan's Wrath gives you a shield and makes your attacks deal damage over time: place it before a trade."
        ),
        "combos": [
            {"name": "The basic hook", "keys": ["Q", "AA", "E"], "when": "An enemy is within hook range.",
             "how": "Dredge Line pulls you together; your first attack deals bonus damage and briefly roots. Riptide slows and damages to finish."},
            {"name": "The team-fight engage", "keys": ["R", "W", "E"], "when": "The enemy carry is visible.",
             "how": "Depth Charge chases an enemy and knocks them up with a stun, letting your team attack them. Activate Titan's Wrath to withstand the enemy damage."},
            {"name": "Protecting an ally", "keys": ["Q", "W"], "when": "An enemy dives your carry.",
             "how": "Dredge Line catches the aggressor and cuts them off from their target; Titan's Wrath shields you and damages those who come close."},
        ],
        "mistakes": [
            "Casting Dredge Line without a clear path: a minion can stop it.",
            "Using the ultimate on a non-priority target: warn your team first.",
            "Forgetting the shield from Titan's Wrath before a trade.",
        ],
    },
    "Tristana": {
        "playstyle": (
            "Tristana is an execution marksman: her attack range grows with her levels, and Rocket Jump lets her dive or escape. "
            "Explosive Charge places a bomb on a target or explodes on every takedown, letting her chain kills in team fights. Her ultimate knocks the target back and doubles the charge's blast radius."
        ),
        "laning": (
            "Your range grows with your levels: play carefully early, then punish from a distance as soon as you outrange them. "
            "Keep Rocket Jump to escape or finish, since its cooldown is long."
        ),
        "combos": [
            {"name": "The execution", "keys": ["W", "E", "Q", "AA"], "when": "An enemy is isolated or weakened.",
             "how": "Rocket Jump brings you closer and slows, Explosive Charge places a bomb on the target, Rapid Fire boosts your attack speed to finish."},
            {"name": "The defensive ultimate", "keys": ["R"], "when": "An enemy dives you.",
             "how": "Buster Shot deals magic damage and knocks the target back; if they carry an Explosive Charge, the blast radius is doubled, which also hurts their nearby allies."},
            {"name": "The kill chain", "keys": ["E", "AA", "AA", "Q"], "when": "A team fight is underway.",
             "how": "Every takedown makes your projectiles explode around the victim: position yourself to hit several enemies at once."},
        ],
        "mistakes": [
            "Diving with Rocket Jump without an escape: its cooldown is long.",
            "Using the ultimate offensively when it knocks the target back: it is also a defensive tool.",
            "Forgetting that your range grows with levels: do not play like you are level 1.",
        ],
    },
}
