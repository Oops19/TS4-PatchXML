#
# LICENSE https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2023 https://github.com/Oops19
#


from sims4communitylib.mod_support.common_mod_info import CommonModInfo


class ModInfo(CommonModInfo):
    """ Mod info for the S4CL Sample Mod. """
    # To create a Mod Identity for this mod, simply do ModInfo.get_identity(). Please refrain from using the ModInfo of The Sims 4 Community Library in your own mod and instead use yours!
    _FILE_PATH: str = str(__file__)

    @property
    def _name(self) -> str:
        # This is the name that'll be used whenever a Messages.txt or Exceptions.txt file is created <_name>_Messages.txt and <_name>_Exceptions.txt.
        return 'PatchXML'

    @property
    def _author(self) -> str:
        # This is your name.
        return 'o19'

    @property
    def _base_namespace(self) -> str:
        # This is the name of the root package
        return 'patch_xml'

    @property
    def _file_path(self) -> str:
        # This is simply a file path that you do not need to change.
        return ModInfo._FILE_PATH

    @property
    def _version(self) -> str:
        return '1.2.3'


r'''
TODO:
    Cleanup of old delete code in SharedData().initialize_cache_directory()

v1.2.3
    Add XML with "_xml='<E>TEEN</E>'" to the selected (via xpath) node.
    Evaluate the xpath only one time. xpath with '/..' will no longer fail after deleting the child node.
    xpath compatibility: 'contains()' and 'text' support now single and double quotes:
    * E[contains(text(), "TEEN")] or E[contains(text(), 'TEEN')]
    * E[text="TEEN"] or E[text='TEEN']
    * [E="TEEN"] or [E='TEEN']
        * For 'match' [E="TEEN"] or [E='TEEN'] must be used, 'contains()' and 'text' are not supported.
v1.2.2
    No longer sort tunings, this fixes a memory issue.
v1.2.1
    Improved identification of bogus tunings.
    During 1st start and/or after a game update all tuning IDs are logged.
    The time stamps can be matched with Vanilla Logs.
    Vanilla Logs are needed as exceptions within TS4 are caught internally and Patch-XML doesn't receive them.
v1.2.0
    For example:
    2024-07-25 23:55:55.742631 DEBUG: [PatchXML]: Checking(ETreeTuningLoader): I buff 'buff_Alien_Empathy_Emotion_Playful' (103479)
    2024-07-25T23:55:55.724679 FATAL  None                 None       '[GSI_DUMP][cjiang] Error occurred within the tag named 'walkstyle' (value: V) (UnavailablePackSafeResourceError)
    S4S Shift+Ctr+C 'resource.find 103479' -> Shows only EA EP01/EP02 sources for me, strange!
    Add 103479 to S4S package and check all references, e.g. n="Mood_Playful" s="14642"
    S4S Shift+Ctr+C 'resource.find 14642' -> 'roBurky - EmotionalInertia-Complete.package' - This file must be updated or deleted to fix the error.
    Remove the cached Patch-XML data and start TS4 again to make sure it starts without errors.
    PS: This FATAL error is not really FATAL, TS4 starts anyway. 

v1.2.0
    Save tunings to mod_data/patch_xml/{game_version}/ and load them from there
v1.0.13
    Tested with TS4 v1.107
v1.0.12
    Improved logging
    Fixed a bug
v1.0.11
    Return XML without the 'n', 's' ad 'i' attributes 1:1, don't throw an exception
v1.0.10
    Basic support for http://xpather.com/ XPath syntax.
    Avoid to add spaces to the XPath expression around `@=,[]()"'` etc. as such strings can't be converted.
        Exception: 1-n spaces behind ',' are supported.
    '', '/I', -> '.'
    '/I/X/Y/Z' -> 'X/Y/Z'
    '/X[text()="Y"]' with '/[X="Y"]/X'
    '/X[contains(text(), "Y"]' with '/[X="Y"]/X'  # not correct, no longer a contains check!
    '/*' will be removed as it is not supported!
    
    A simple expression can be used 1:1, e.g.:
    * '/I/X[text()="Y"]/../Z' will be translated to '[X="Y"]/X/../Z'
    
    For '/[T="text"]' matches: 
        Remove all comments from xml before parsing. 'Y' does not match 'Y<-- Whatever -->'
v1.0.9
    Improved logging
v1.0.8
    Require XmlPatcher(add_comments=True) to add comments to generated files.
v1.0.7
    Modified log imports to use this mod without TS4.
    Allow to add a comment also while modifying XML.
    It is not recommended to add comments with config files during startup as this may cause issues for TS4.
v1.0.6
    Improve error logging
v1.0.5
    Updated README for new TS4 version
v1.0.4
    Small bugfix
v1.0.3
    Updated README for new TS4 version
v1.0.2
    Updated README for new TS4 version
v1.0.1
    Removed comments from patch files which TS4 can't handle properly
v1.0.0
    Update docs
v0.0.16
    Fix tag.strip() exception
v0.0.15
    Updated documentation and compile script
v0.0.14
    Fix logging problem
v0.0.13
    Save tunings as '.patched.xml'
v0.0.12
    'strip()' tag and text for proper matching and logging.
v0.0.11
    Updated README and compile script
v0.0.10
    Provided 'Tuning Inspector' as a standalone mod
    Updated README and compile
v0.0.9
    Add documentation.
v0.0.8
    Change logging to CommonLog
v0.0.7
    Minor code cleanup
v0.0.6
    Allow empty i/instance and tuning_ids to be specified. For the rare cases when it is necessary.
v0.0.5
    Add cheat commands:
    'o19.tunings.patch file.txt n': Config file (in patch_xml/cfg/) and tuning_id to test. The modification can't be applied while testing.
        If the patch looks fine restart the game to apply it. Or use Live XML to patch it.
    'o19.tunings.pretty False': Disable formatting the XML.
    'o19.tunings.comments False': Disable comments in XML.
    'o19.tunings.write n': Write tuning for tuning_id n.
    'o19.tunings.write 0': Write all tuning files. This takes 5..30 minutes depending on the used DLCs.
    
    Optimize startup and caching. The start times are usually below one second.
    The first startup time after installing or a game update will be 1..2 minutes to initialize the cache.
v0.0.4
    Read and combine configuration files
    Add some configuration files.
v0.0.3
    Create tuning.xml from memory
    Initialize VanillaTunings and use get_tuning() to retrieve individual tuning files. 
v0.0.2
    Read tuning.xml from disk
    Patch f(hard-coded configuration)
v0.0.1
    Initial version
    Extract and save tuning.xml files
'''
