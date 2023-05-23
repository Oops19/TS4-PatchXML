# Patches explained
If these patches are active, either by using this mod, Live XML or patched tuning files the first output will not match.

Each tuning modification alters the game play, in a desired or an unexpected way. Be careful of what you do 'cause the lie becomes the truth.

## no_autonomous_rumbasim.txt
* A very generic patch to disable autonomous interactions which could be applied to 100 other interactions.
* `inspect INTERACTION stereo_Dance_LocalCultureSkill` will show the normal tuning.
* The patch will add `<T n="allow_autonomous">False</T>` to the tuning.
* `inspect INTERACTION stereo_Dance_LocalCultureSkill` will display `allow_autonomous: <class 'str'> = False: <class 'bool'>`

## suppress_jealousy_broadcaster.txt
* A very generic patch to disable a broadcaster. It could be applied to many other broadcasters.
* Basically 'allow_sims' is set to 'False' so the broadcaster affects only objects.
* `inspect BROADCASTER broadcaster_Jealousy` will display `allow_sims: <class 'str'> = False: <class 'bool'>`.

## suppress_nude_broadcaster.txt
* Suppress all inappropriate reactions of sims when they live in a nudist world. Not suitable for everyone.
* Keep it playing on repeat. If you hate it - press delete.

## faster_gardening.txt
* One of my first Live XML tunings. Converted to Patch XML.
* It works exactly as Live XML, the min and max values are reduced and the loot gets adjusted.

## teens_fake_id.txt
* We'll add teens to the global 'adult' test. This will allow teens to access more interactions etc.
* `inspect SNIPPET testSetInstance_YoungAdultOrAbove_YAE` will list a frozenset with ages: YOUNG_ADULT, ADULT, ELDER.
* The patch will add 'TEEN' to the snippet.
* `inspect SNIPPET testSetInstance_YoungAdultOrAbove_YAE` will display `ages=frozenset({<Age.YOUNGADULT = 16>, <Age.TEEN = 8>, <Age.ADULT = 32>, <Age.ELDER = 64>})`.
* `inspect SNIPPET testSetInstance_YoungAdultOrAbove_YAE test.SimInfoTest.ages` to drill properly down.

## suntan_in_buildings.txt
* This patch`will remove a few tests from the tunings. Location, time and weather will no longer be checked. So one can also tan outside at night with freezing temperatures.
* `inspect INTERACTION suntan_BeachTowel test_globals.LocationTest` raises an error as there is no `LocationTest`any more.

## lower_privacy_radius.txt
* This patch reduces the privacy radius. Reducing or increasing the radius might be useful for many tunings.
* The default is 10 or something like this so it works best if one plays only with one sim.
* Reducing this limit to 2 with `div(5, 0)` allows the sims to behave differently.
* `inspect - suntan_BeachTowel_Nude test_globals.SimsInConstraintTests.constraints` will not drill down deep enough to display the new value. 

## immediate_instant_upgrade.txt
* This one is an easy patch, some min and max values are modified.
* The current values are deleted first and then new values are added.
* `inspect STATISTIC Commodity_Trait_TheKnack_UpgradeTimer` will show `max_value: <class 'str'> = 0.0: <class 'float'>` and `maximum_auto_satisfy_time: <class 'str'> = 0.0: <class 'float'>`.

## motives.txt
* Tuning: `<T n="decay_rate">0.1736</T>`
* `inspect STATISTIC motive_Bladder` will display `decay_rate: <class 'str'> = 0.1736: <class 'float'>`
* The patch looks for the 'decay_rate' and decreases it. Stupid, and unfortunately also simple.
* Then the loaded tuning will display `decay_rate: <class 'str'> = 0.0017: <class 'float'>`

# To be added
## faster_retail.txt
## neglect_toddlers_and_children.txt
* Actually to prevent that TS4 whisks them away without any reason. Only cruel people would neglect them.
## sing_longer_in_shower.txt


# Fails
Not everything is possible with Patch XML.
## bladdelhass.txt
* A tuning for the selfie camera inspired by a small camera company founded in Sweden.
* `inspect - photography_TakeSelfie_CellPhone basic_extras.photo_mode` will list:
* * `camera_quality: <class 'str'> = CameraQuality.CHEAP: <enum <class 'int'>: CameraQuality>`
* * `zoom_capability: <class 'str'> = ZoomCapability.NO_ZOOM: <enum <class 'int'>: ZoomCapability>`
* So far so good, but not visible in the tuning at all. Patching impossible.

## reward_costs.txt
* This patch doesn't work right now. Nothing will happen as the modification can't be applied properly.
* It would multiply the reward costs by 10 making it much harder to buy something.
* Only lame cheaters would replace 'mul' with 'div' - if this patch ever works I'll do it!

