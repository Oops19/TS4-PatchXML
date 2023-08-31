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
        return '1.0.0'


"""
TODO:
    Save tunings to patched/ and load them from there
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
"""