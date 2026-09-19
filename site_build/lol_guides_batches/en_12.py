"""English guides, batch 12."""

EN = {
    "Gwen": {
        "playstyle": (
            "Gwen is a fighter whose attacks deal bonus magic damage based on the target's health, and who heals for part of the damage dealt to champions. "
            "Snip Snip! cuts up to 6 times, Hallowed Mist protects her from enemies outside the area, Skip 'n Slash dashes her with bonuses, and Needlework slows and can be recast twice."
        ),
        "laning": (
            "Snip Snip! deals true damage at the center of the area and applies your passive on every cut: aim with the center. "
            "Hallowed Mist makes you untouchable to enemies outside the mist."
        ),
        "combos": [
            {"name": "The trade", "when": "An enemy is within range.",
             "how": "Skip 'n Slash dashes you then gives attack speed, range and magic damage; Snip Snip! applies your passive on every snip of the scissors."},
            {"name": "The duel", "when": "You are fighting an enemy who has ranged allies.",
             "how": "Hallowed Mist protects you from enemies outside the area: only those who enter can target you. Fight inside."},
            {"name": "The three-part ultimate", "when": "A carry is isolated.",
             "how": "Needlework slows, deals magic damage and applies A Thousand Cuts; it can be activated two more times with more needles and damage."},
        ],
        "mistakes": [
            "Casting Snip Snip! aiming at the edges: the true damage is at the center.",
            "Using Hallowed Mist without fighting inside it.",
            "Forgetting the ultimate's recasts.",
        ],
    },
    "Zyra": {
        "playstyle": (
            "Zyra is an area mage who fights with plants: seeds appear regularly, and casting Deadly Spines or Grasping Roots near them turns them into plants that fight for her. "
            "Grasping Roots roots, and Stranglethorns knocks up and enrages the plants."
        ),
        "laning": (
            "Plant seeds with Rampant Growth: they last up to 60 seconds and can be stored. "
            "Cast your abilities near seeds to grow plants."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within range of a seed.",
             "how": "Plant a seed then Deadly Spines near it: a Thorn Spitter grows and fires from afar; Grasping Roots near a seed grows a Vine Lasher that slows."},
            {"name": "The root", "when": "An enemy is isolated.",
             "how": "Grasping Roots roots the target; Deadly Spines deals damage in an explosion, Stranglethorns knocks up."},
            {"name": "The team fight", "when": "A fight begins at a prepared spot.",
             "how": "Stranglethorns damages as it spreads then knocks up the enemies; the plants inside the thorns become enraged."},
        ],
        "mistakes": [
            "Casting your abilities far from your seeds: you lose the plants.",
            "Forgetting that seeds last 60 seconds.",
            "Using the ultimate with no plants to enrage.",
        ],
    },
    "Malzahar": {
        "playstyle": (
            "Malzahar is a control mage: Call of the Void silences, Malefic Visions deals damage over time and spreads on death, and Nether Grasp suppresses a champion. "
            "His passive gives him a huge damage reduction and immunity to crowd control if he takes nothing for a while."
        ),
        "laning": (
            "Take advantage of your passive: take no damage to gain immunity to crowd control. "
            "Malefic Visions is refreshed by your other spells on the target."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within range.",
             "how": "Malefic Visions deals damage over time and attracts the Voidlings, Call of the Void silences, Void Swarm adds attacks."},
            {"name": "The suppression", "when": "A carry is isolated.",
             "how": "Nether Grasp suppresses a champion in a zone of negative energy dealing damage: set it up with Malefic Visions."},
            {"name": "The spread", "when": "An affected enemy is about to die.",
             "how": "If the target dies under Malefic Visions, the visions pass to a nearby enemy unit and you regain mana."},
        ],
        "mistakes": [
            "Taking damage for no reason: you lose your passive's reduction.",
            "Casting Call of the Void without anticipating the portals' delay.",
            "Using the ultimate on a target who can break free.",
        ],
    },
    "Yuumi": {
        "playstyle": (
            "Yuumi is a support who attaches to her allies: You and Me! dashes her to an ally, and in that state only turrets can target her. "
            "Prowling Projectile slows (more if the projectile flies at least 1.35 seconds), Zoomies only benefits the ally when she is attached, and Final Chapter heals and damages."
        ),
        "laning": (
            "Attach to your carry to protect them. "
            "Your passive heals you and heals your next ally when you hit a champion."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within projectile range.",
             "how": "Prowling Projectile slows and damages (stronger if the projectile flew 1.35 s); while attached, you can steer it with your cursor; Zoomies gives your ally a shield and speeds."},
            {"name": "Protection", "when": "Your carry is threatened.",
             "how": "You and Me! puts you safely on your ally, Zoomies protects them, and Final Chapter heals your allies while channeling."},
            {"name": "The team fight", "when": "A fight begins.",
             "how": "Final Chapter channels five waves that damage enemies and heal allies; during it, you can move, attach and cast Zoomies."},
        ],
        "mistakes": [
            "Detaching in a dangerous area: you are vulnerable when not attached.",
            "Casting Prowling Projectile with no direction.",
            "Forgetting to strengthen the bond with your best friend.",
        ],
    },
    "Velkoz": {
        "playstyle": (
            "Vel'Koz is a long-range mage-support: his abilities apply Organic Deconstruction, and at 3 stacks the enemy takes an explosion of true damage. "
            "Plasma Fission splits, Void Rift explodes after a delay, Tectonic Disruption knocks up, and his ultimate follows the cursor, dealing true damage to test subjects."
        ),
        "laning": (
            "Apply three stacks to trigger the true-damage explosion. "
            "Plasma Fission splits in two on impact or on recast."
        ),
        "combos": [
            {"name": "The deconstruction explosion", "when": "An enemy is within range.",
             "how": "Each ability applies Organic Deconstruction: at 3 stacks, the enemy takes an explosion of true damage."},
            {"name": "The split projectile", "when": "An enemy is off to the side.",
             "how": "Plasma Fission splits in two on impact or on recast; slows and damages on impact."},
            {"name": "The true damage ultimate", "when": "A carry is marked.",
             "how": "Life Form Disintegration Ray fires a 2.5-second channeled beam that follows the cursor; test subjects take true damage."},
        ],
        "mistakes": [
            "Casting the ultimate with no test subject.",
            "Forgetting Plasma Fission's recast.",
            "Neglecting range: stay far away.",
        ],
    },
    "Corki": {
        "playstyle": (
            "Corki is a mixed-damage marksman-mage: his attacks deal bonus true damage. "
            "Phosphorus Bomb reveals, Valkyrie crosses a short distance while dropping bombs, Gatling Gun reduces armor and magic resistance, and Missile Barrage stores ammo of which every third shot is a big Bertha."
        ),
        "laning": (
            "Your passive converts part of your attack damage into true damage. "
            "Gatling Gun reduces the armor and magic resistance of enemies hit."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within range.",
             "how": "Phosphorus Bomb damages and reveals the area, Gatling Gun fires in a cone, reducing armor and magic resistance."},
            {"name": "Repositioning", "when": "You want to hit and move.",
             "how": "Valkyrie moves you a short distance while dropping bombs and a trail of fire, then Missile Barrage fires."},
            {"name": "The siege ultimate", "when": "Enemies are within barrage range.",
             "how": "Missile Barrage fires stored explosive missiles; one in 3 is a big Bertha dealing more damage."},
        ],
        "mistakes": [
            "Wasting your ultimate's missiles.",
            "Using Valkyrie without looking at its direction.",
            "Neglecting Gatling Gun: the resistance reduction is significant.",
        ],
    },
    "Sett": {
        "playstyle": (
            "Sett is a fighter who soaks up damage: his passive alternates his punches and increases his regeneration based on his missing health, and Haymaker converts damage taken into Grit for a shield and an area punch. "
            "Knuckle Down deals damage based on max health, Facebreaker pulls in from both sides, and The Show Stopper slams a champion."
        ),
        "laning": (
            "Knuckle Down empowers your next two attacks based on the target's max health. "
            "Do not waste Haymaker: the more damage you have taken, the more useful the shield."
        ),
        "combos": [
            {"name": "The trade", "when": "An enemy is within range.",
             "how": "Knuckle Down raises your speed toward enemies and your two attacks deal damage based on max health; Facebreaker stuns if there are enemies on both sides."},
            {"name": "Recovery", "when": "You have taken a lot of damage.",
             "how": "Haymaker spends all the stored Grit: a shield and an area punch, true damage at the center."},
            {"name": "The show-stopping ultimate", "when": "A carry is within range.",
             "how": "The Show Stopper lifts an enemy champion into the air before slamming them down, damaging and slowing all nearby enemies on landing."},
        ],
        "mistakes": [
            "Using Facebreaker with enemies on one side only: they are only slowed.",
            "Casting Haymaker with no stored Grit.",
            "Forgetting that you can place the ultimate to slam onto the enemy's allies.",
        ],
    },
    "Twitch": {
        "playstyle": (
            "Twitch is a venom marksman-assassin: his attacks infect the target and deal true damage every second. "
            "Ambush camouflages him with a speed bonus, Venom Cask slows and applies poison, Contaminate makes it worse, and Spray and Pray fires bolts that pierce all enemies."
        ),
        "laning": (
            "Poison your opponent with attacks then use Contaminate to make it worse. "
            "When you leave camouflage, your attack speed briefly rises."
        ),
        "combos": [
            {"name": "The ambush", "when": "A carry is within range.",
             "how": "Ambush camouflages you and raises your speed; on leaving it, your attack speed rises: strike then Contaminate worsens the poison."},
            {"name": "Harassment", "when": "An enemy is within range.",
             "how": "Venom Cask explodes in an area, slows and applies Deadly Venom; your attacks reinforce the poison."},
            {"name": "The line ultimate", "when": "Enemies are lined up.",
             "how": "Spray and Pray fires long-range bolts that pierce all enemies hit: line them up."},
        ],
        "mistakes": [
            "Using Contaminate with no poison.",
            "Casting the ultimate without lining up the enemies.",
            "Leaving camouflage with no target: you lose your window.",
        ],
    },
    "Zaahen": {
        "playstyle": (
            "Zaahen is a fighter who gains power with every hit: his attacks and abilities give Determination stacks with bonus attack damage, and at max he can come back to life. "
            "The Darkin Glaive slashes twice and can be recast to knock up, Dreaded Return pulls in, Aureate Rush dashes him with a slash, and Grim Deliverance brings him down in a dive."
        ),
        "laning": (
            "Hit champions to stack Determination. "
            "The Darkin Glaive heals you and can be recast to knock the target into the air."
        ),
        "combos": [
            {"name": "The trade", "when": "An enemy is within range.",
             "how": "The Darkin Glaive slashes twice with bonus damage and a heal; recast it to knock the target into the air."},
            {"name": "The engage", "when": "An enemy is far away.",
             "how": "Dreaded Return pulls enemies toward you, Aureate Rush dashes you with a slash around you."},
            {"name": "The ultimate", "when": "A group is close.",
             "how": "Grim Deliverance brings you down in a dive, damaging enemies and healing you for part of the damage dealt."},
        ],
        "mistakes": [
            "Using the ultimate without having stacked Determination.",
            "Casting Dreaded Return into nothing.",
            "Forgetting to recast The Darkin Glaive.",
        ],
    },
    "Ornn": {
        "playstyle": (
            "Ornn is a forge tank: he increases all his armor and magic resistance bonuses, and can forge non-consumable items anywhere on the map using gold. "
            "Volcanic Rupture slows, Bellows Breath makes enemies brittle, Searing Charge knocks up against terrain, and Call of the Forge God summons an elemental that charges toward him."
        ),
        "laning": (
            "Bellows Breath: the last flame makes enemies brittle. "
            "You can forge items without going back to base."
        ),
        "combos": [
            {"name": "Harassment", "when": "An enemy is within range.",
             "how": "Volcanic Rupture slows and forms a column of lava, Bellows Breath makes the enemies hit by the last flame brittle."},
            {"name": "The knock-up", "when": "An enemy is near a wall.",
             "how": "Searing Charge damages those you cross and creates a shockwave that knocks up if you hit terrain."},
            {"name": "The two-part ultimate", "when": "Several enemies are grouped.",
             "how": "Call of the Forge God summons an elemental that charges toward you; recast the ultimate to dash onto it and redirect it, knocking up the enemies hit."},
        ],
        "mistakes": [
            "Forgetting that you can forge items.",
            "Using the ultimate's recast without a clear direction.",
            "Casting Searing Charge with no wall.",
        ],
    },
}
