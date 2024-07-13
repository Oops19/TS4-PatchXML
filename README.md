# Patch XML

This mod is a poor man's clone of Live XML.

It allows to patch the tuning files while starting TS4 which might be much more convenient for many users.
It uses XML XPath syntax to locate the parts in the tuning and offers basic 'add', 'delete' and 'modify' operations.

As it is executed while the tuning files are loaded there might be a chicken-egg problem so for now configuration files instead of '.package' files are used to patch tunings.

### v1.2.0 CacheD
Version 1.2+ cache the patched tuning files in `mod_data/patch_xml/{game_version/`.
Whenever a new TS4 version gets released startup will take a while to extract comments and to create new patch files. 

The cached tunings are used to replace the original tunings.
It takes around 2 seconds to replace the tunings, so this version is much faster.

There's no need to update even though I highly recommend it.

## Mild Warning - Game mechanics changed
The `mod_data/patch_xml/cfg/*.txt` files modify tunings.
They change the game mechanics and checks in various ways (like an override.package does).
* Please review the files in `mod_data` and remove files which you do not want to use.
* Filtering of broadcasts affects multiple sims.
* Modified age/race/gender checks may allow sims and/or pets to execute tasks which were never planned to be available for them.
* Modified range checks may lower or increase the interaction range and/or privacy need of sims. 

The included files should not affect the game-play too much, but it's hard to test everything.

Modifications which I do not consider as strictly SFW have a 'nsfw_' prefix.

### Tuning Extractor
This mod can extract all tuning files with comments for referenced tunings, like 'TS4 XML Extractor' does. It doesn't add STBL comments for text references.

### Tuning Editor
This mod is for everyone who wants to modify tuning values without editing XML files. It is the superior alternative to overrides.

We often see xml tuning override mods which are 3 months old and when compared to the current XML it becomes obvious that EA added many new things to the XML files (fixes, buffs, traits, commodities, ...) which are missing in the mod.
They often break when EA releases a new TS4 version.
It is more easy to use than Live XML. Anyhow it has the limitation that the tunings can't be modified as soon as the game is running.

As a normal user you want to install this mod if another mod requires it.
The mod itself does not modify the game play at all.
Of course, you can install it and benefit (or suffer) from the game changes caused by the included sample configuration files if you fail to remove them.

## Real world example
How would we implement the simple requirement to disable autonomy for one interaction?

### Copy XML Tuning
**Don't do this!** There are many mods which have been created like this, unfortunately.

The simple way is to copy the tuning (eg 'stereo_Dance_LocalCultureSkill') and add a line `<T n="allow_autonomous">False</T>` to it.
Then add the XML to a new .package and it's done.
To do this for 10 similar tunings we copy all 10 files, edit them and add them to the .package.
And then we pray to EA that they never ever modify these tunings, even though we know that we did it wrong.

If you created your tunings mods like this you may consider to use this mod.
EA adds new lines to tuning files, sometimes 3, sometimes 100 and each '.package' file with copied tunings will contribute to game errors.
Don't be a fool and join the 'Broken/Updated Mods & CC' forum on forums.thesims.com.

### 'Patch while starting TS4' with 'Patch XML'
We need to gather the tunings, for this mod we need the name.
Wildcards are supported, so it is easy to match similar tunings (eg 'stereo_Dance_*').
As we work with XML we need to locate the proper place to insert `<T n='allow_autonomous'>False</T>`

With XPath `'xpath': "."` we'll locate the tuning root.

And with `'add': [{'tag': 'T', 'attrib': {'n': 'allow_autonomous'}, 'text': 'False', 'comment': " Rumbasim is Dead. "}]` we add the XML node.

That's it. Saved to a configuration file and when the game starts it's applied to the specified tunings.

To test this while the game is running we create a new configuration file `no_autonomous_rumbasim.txt` with the data from above.

With the cheat command `o19.tunings.patch no_autonomous_rumbasim.txt 175415` the tuning 175415(stereo_Dance_LocalCultureSkill) is loaded, the configuration will be applied and the patched file is saved. Review this file and if it looks good the configuration is good, hopefully.

## Security
This mod reads and parses configuration files with `literal_eval()` into  Python dict() elements.
The elements are hopefully processed properly as variables and should never be executed.
Please let me know if you can identify security issues, no one wants to run a mod with code injection or shell vulnerabilities.
For now I recommend that you review the files before you save them to `mod_data/patch_xml/`.

I consider this mod to be safe, otherwise I would not publish it.




## Cheat commands
* 'o19.tunings.patch file.txt n': Config file (in patch_xml/cfg/) and tuning_id to test. The modification can't be applied while testing.  If the patch looks fine restart the game to apply it.
* 'o19.tunings.pretty False': Disable formatting the XML.
* 'o19.tunings.comments False': Disable comments in XML.
* 'o19.tunings.write n': Write tuning for tuning_id n.
* 'o19.tunings.write 0': Write all tuning files. This takes 5..30 minutes depending on the installed DLCs and your CPU.

## Limitations
All tunings? No! Some indomitable tunings stop resisting the modifications.
Even though all tunings can be read and modified it is not always possible to apply the modifications.
* 'patch.txt' (created after starting TS4) should contain the tunings which can be patched.
* 'nopatch.txt' contains the tunings which might not be patched.  E.g. the 'satisfaction.satisfaction_tracker' tuning.

## Mod collision
If you are currently using Live XML consider to migrate the configurations to Patch XML. At least make sure that either Patch XML or Live XML modifies a tuning, this will improve performance.
It may make sense to keep Live XML installed to be able to inspect the tunings after they have been loaded.

## Merging
Most people do not merge script mods. This mod may be merged with a ZIP program with other mods. The file name may be renamed, it is not used to reference anything.

## Future
Fix bugs.
Add support to patch everything. 

# Creating custom files
The file 'cfg/sample.txt.ignore' contains some sample code with descriptions, like the supplied files.
In case you need to figure out which XPATH to use try to use a tool like https://www.freeformatter.com/xpath-tester.html.

Actually it is quite easy to follow the XML structure and use '/' before every child tag, ignore the 'I' as the XPath implementation is limited:
* `<I><U n="go"><T m="home"><E x="y"> ==> U/T/E`
* `<I><U n="go"><T m="home"><E x="y"> ==> U[n='go']/T[m='home']/E[x='y']` to be much more specific if the tuning has multiple U/T/E elements which different attributes.
The XPath may match 1-n elements and all elements will be processed.

Elements can be added or deleted, e.g. `<E>TEEN</E>` with `{'tag': 'E', 'text': 'TEEN'}`.
* `'delete': [{'tag': 'E', 'text': 'TEEN'}]`
* `'add': [{'tag': 'E', 'text': 'TEEN'}]`

To delete empty tags add `'empty': True, `.
This allows to remove empty (list) elements from the XML which can confuse TS4.
* `'delete': [{'tag': 'E', 'empty': True}}]`
* `'delete': [{'tag': 'E', 'attrib': {'n': 'go'}, 'empty': True}}]`

To delete possible empty tags use:
* `'delete`: [{'tag': 'U', 'empty': True}]` - A list with all elements removed must be cleaned up properly.

The element attributes and the element text can also be modified:
* `'attrib': {'n': 'something_else'}`
* `'text': 'NewText'`
* For numbers (int and float):
* `'text': 'div(2, 0)'` - Subtract '2' and round to '0' digits (int instead of float).
* Supported: operations: mul/div/add/sub/pow(number, digits) => 'text' */+-^ number; round to digits
* Supported: operations: x_div/x_sub/x_pow => number /-^ 'text'; round to digits



# Addendum

## Game compatibility
This mod has been tested with `The Sims 4` 1.107.151, S4CL 3.4, TS4Lib 0.3.20 (2024-05).
It is expected to be compatible with many upcoming releases of TS4, S4CL and TS4Lib.

## Dependencies
Download the ZIP file, not the sources.
* [This Mod](../../releases/latest)
* [TS4-Library](https://github.com/Oops19/TS4-Library/releases/latest)
* [S4CL](https://github.com/ColonolNutty/Sims4CommunityLibrary/releases/latest)
* [The Sims 4](https://www.ea.com/games/the-sims/the-sims-4)

If not installed download and install TS4 and these mods.
All are available for free.

## Installation
* Locate the localized `The Sims 4` folder which contains the `Mods` folder.
* Extract the ZIP file into this `The Sims 4` folder.
* It will create the directories/files `Mods/_o19_/$mod_name.ts4script`, `Mods/_o19_/$mod_name.package`, `mod_data/$mod_name/*` and/or `mod_documentation/$mod_name/*`
* `mod_logs/$mod_name.txt` will be created as soon as data is logged.

### Manual Installation
If you don't want to extract the ZIP file into `The Sims 4` folder you might want to read this. 
* The files in `ZIP-File/mod_data` are usually required and should be extracted to `The Sims 4/mod_data`.
* The files in `ZIP-File/mod_documentation` are for you to read it. They are not needed to use this mod.
* The `Mods/_o19_/*.ts4script` files can be stored in a random folder within `Mods` or directly in `Mods`. I highly recommend to store it in `_o19_` so you know who created it.

## Usage Tracking / Privacy
This mod does not send any data to tracking servers. The code is open source, not obfuscated, and can be reviewed.

Some log entries in the log file ('mod_logs' folder) may contain the local username, especially if files are not found (WARN, ERROR).

## External Links
[Sources](https://github.com/Oops19/)
[Support](https://discord.gg/d8X9aQ3jbm)
[Donations](https://www.patreon.com/o19)

## Copyright and License
* © 2024 [Oops19](https://github.com/Oops19)
* License for '.package' files: [Electronic Arts TOS for UGC](https://tos.ea.com/legalapp/WEBTERMS/US/en/PC/)  
* License for other media unless specified differently: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) unless the Electronic Arts TOS for UGC overrides it.
This allows you to use this mod and re-use the code even if you don't own The Sims 4.
Have fun extending this mod and/or integrating it with your mods.

Oops19 / o19 is not endorsed by or affiliated with Electronic Arts or its licensors.
Game content and materials copyright Electronic Arts Inc. and its licensors. 
Trademarks are the property of their respective owners.

### TOS
* Please don't put it behind a paywall.
* Please don't create mods which break with every TS4 update.
* For simple tuning modifications use [Patch-XML](https://github.com/Oops19/TS4-PatchXML) 
* or [LiveXML](https://github.com/Oops19/TS4-LiveXML).
* To check the XML structure of custom tunings use [VanillaLogs](https://github.com/Oops19/TS4-VanillaLogs).
