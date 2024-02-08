# NSFW - Patches explained

These patches do not remove any underwear and/or censor from the sims.

They allow interactions and/or reactions which are not possible in the base game.

## nsfw_batuu_romance_for_npc.txt
* Allow romantic interactions with NPCs.

## nsfw_enable_ctyae_sit_on_ground.txt
* Allow all sims to sit on ground.
* The interaction itself might not check the outfit.

## nsfw_lower_privacy_radius.txt
* This patch reduces the privacy radius. Reducing or increasing the radius might be useful for many tunings.
* The default is 10 or something like this so it works best if one plays only with one sim.
* Reducing this limit to 2 with `div(5, 0)` allows the sims to behave differently.
* `inspect - suntan_BeachTowel_Nude test_globals.SimsInConstraintTests.constraints` will not drill down deep enough to display the new value. 

## nsfw_poligamies.txt
* Remove some checks and allow Propose more often.

## nsfw_suppress_nude_broadcaster.txt
* Suppress all inappropriate reactions of sims when they live in a nudist world.
* Not suitable for everyone.

## nsfw_teens_fake_id.txt
* Add teens to the global 'adult' test. 
* This will allow teens to access more interactions.
* `inspect SNIPPET testSetInstance_YoungAdultOrAbove_YAE` will list a frozenset with ages: YOUNG_ADULT, ADULT, ELDER.
* The patch will add 'TEEN' to the snippet.
* `inspect SNIPPET testSetInstance_YoungAdultOrAbove_YAE` will display `ages=frozenset({<Age.YOUNGADULT = 16>, <Age.TEEN = 8>, <Age.ADULT = 32>, <Age.ELDER = 64>})`.
* `inspect SNIPPET testSetInstance_YoungAdultOrAbove_YAE test.SimInfoTest.ages` to drill properly down.

