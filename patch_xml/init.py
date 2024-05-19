#
# LICENSE
# https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2024 https://github.com/Oops19
#


import os
import re
import shutil
from typing import Tuple, Dict, Set, List

from patch_xml.modinfo import ModInfo
from patch_xml.patch import Patch
from patch_xml.user_config import UserConfig
from patch_xml.vanilla_tunings import VanillaTunings
from sims4communitylib.utils.common_log_utils import CommonLogUtils

from ts4lib.libraries.ts4folders import TS4Folders
from ts4lib.utils.singleton import Singleton
from sims4communitylib.utils.common_log_registry import CommonLog


mod_name = ModInfo.get_identity().name
log: CommonLog = CommonLog(ModInfo.get_identity(), ModInfo.get_identity().name, custom_file_path=None)
log.enable()
log.info(f"Thank you for using Patch XML!")


class Init(object, metaclass=Singleton):
    def __init__(self):
        try:
            self.ts4f = TS4Folders(ModInfo.get_identity().base_namespace)
            self.tunings_folder = os.path.join(self.ts4f.data_folder, 'tunings')
            self.uc = UserConfig()
            self.patch = Patch()

            self.game_updated = True
            os.makedirs(self.tunings_folder, exist_ok=True)
            ts4_gv = os.path.join(self.ts4f.ts4_folder_mods, 'GameVersion.txt')
            mod_gv = os.path.join(self.ts4f.data_folder, 'GameVersion.txt')
            if os.path.exists(ts4_gv) and os.path.exists(mod_gv):
                with open(ts4_gv, 'rb') as fp:
                    b_new_gv = fp.read()
                with open(mod_gv, 'rb') as fp:
                    b_cur_gv = fp.read()
                if b_new_gv == b_cur_gv:
                    # Don't patch a thing, read from cache
                    self.game_updated = False
                else:
                    self.game_updated = True

            if self.game_updated:
                try:
                    # Clear cache
                    with open(mod_gv, 'rb') as fp:
                        cur_gv = fp.read().decode(errors='ignore')  # convert b to str and ignore errors
                        cur_gv = re.sub(r'[^0-9.]', '', cur_gv)  # in case of UTF-8 characters which survived 'ignore': replace everything with '' except of '0-9' and '.'
                        shutil.rmtree(os.path.join(self.ts4f.data_folder, cur_gv))
                except:
                    pass
                try:
                    # Prepare new cache
                    with open(ts4_gv, 'rb') as fp:
                        new_gv = fp.read().decode(errors='ignore')  # convert b to str and ignore errors
                        new_gv = re.sub(r'[^0-9.]', '', new_gv)  # in case of UTF-8 characters which survived 'ignore': replace everything with '' except of '0-9' and '.'
                        os.makedirs((os.path.join(self.ts4f.data_folder, new_gv)), exist_ok=True)
                except:
                    pass

                for f in {'patch.txt', 'nopatch.txt'}:
                    file = os.path.join(self.ts4f.data_folder, f)
                    if os.path.exists(file):
                        os.unlink(file)

            # Add code to actually read the cache if available
            VanillaTunings().init(write_all_tunings=False, dump_xml=False, xml_comments=True, pretty_xml=True, force_refresh=self.game_updated)

            user_provided_patches: Dict = self.uc.merge_configuration_files()
            parsed_patches: Tuple[Set, Set, Set, Set, Set, Set, Set, List] = self.uc.join_configuration(user_provided_patches)
            self.patch.init(parsed_patches)

            # Copy the current version over the new one
            shutil.copyfile(ts4_gv, mod_gv, follow_symlinks=False)
        except:
            log.error(f"Could not initialize Patch XML!", throw=True)
        log.debug(f"Init completed")


Init()
