#
# LICENSE
# https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2024 https://github.com/Oops19
#


import ast
import os
import re
from typing import Tuple, Dict, Set, List, Union

from patch_xml.modinfo import ModInfo
from patch_xml.patch import Patch
from patch_xml.shared_data import SharedData
from patch_xml.user_config import UserConfig
from patch_xml.vanilla_tunings import VanillaTunings
from ts4lib.libraries.ts4folders import TS4Folders
from ts4lib.utils.singleton import Singleton
from sims4communitylib.utils.common_log_registry import CommonLog, CommonLogRegistry
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

log: CommonLog = CommonLogRegistry.get().register_log(ModInfo.get_identity(), ModInfo.get_identity().name)
log.enable()
log.info(f"Thank you for using Patch XML!")


class Init(object, metaclass=Singleton):

    def __init__(self):
        try:
            log.debug(f"Init().init()")
            self.ts4f = TS4Folders(ModInfo.get_identity().base_namespace)
            self.uc = UserConfig()
            self.sd = SharedData()

            self.tunings_folder = self.sd.dir_tunings
            os.makedirs(self.tunings_folder, exist_ok=True)

            patched_tunings_cache: Dict[int, Union[Element, ElementTree]] = {}
            if self.sd.game_updated:
                log.debug(f"Clearing data ...")
                self.sd.initialize_cache_directory()
            else:
                log.debug(f"Reading data from cache ...")
                cache_index = self.sd.file_cache_index
                missing_files = []
                xml_error_files = []
                with open(cache_index, 'rt', encoding='UTF-8') as fp:
                    cache_data_str = fp.read()
                    cache_data = ast.literal_eval(cache_data_str)
                    for instance_id, file_name in cache_data.items():
                        f = os.path.join(self.sd.dir_ts4_mods_gv, file_name)
                        if not os.path.exists(f):
                            missing_files.append(f"{file_name}")
                            continue
                        with open(f, 'rt', encoding='UTF-8') as fp_xml:
                            xml_str = fp_xml.read()
                            try:
                                xml = ElementTree.fromstring(xml_str)
                                patched_tunings_cache.update({instance_id: xml})
                            except:
                                xml_error_files.append(f"{file_name}")
                log.debug(f"Read {len(patched_tunings_cache)} files.")
                self.sd.patched_tunings_cache = patched_tunings_cache

                if missing_files:
                    log.warn(f"Didn't find all expected files: '{missing_files}'")
                    log.warn(f"These files will not be patched!")
                if xml_error_files:
                    log.warn(f"XML transformation failed for: '{xml_error_files}'")
                    log.warn(f"These files will not be patched!")
            self.sd.initialized = True

            self.patch = Patch()

            # Add code to actually read the cache if available
            VanillaTunings().init(write_all_tunings=False, dump_xml=False, xml_comments=True, pretty_xml=True, force_refresh=self.sd.game_updated)

            user_provided_patches: Dict = self.uc.merge_configuration_files()
            parsed_patches: Tuple[Set, Set, Set, Set, Set, Set, Set, List] = self.uc.join_configuration(user_provided_patches)
            self.patch.init(parsed_patches)

            # Copy the current version over the new one
            self.sd.copy_version()
        except:
            log.error(f"Could not initialize Patch XML!", throw=True)
        log.debug(f"Init completed")


Init()
