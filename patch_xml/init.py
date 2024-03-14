#
# LICENSE
# https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2024 https://github.com/Oops19
#


import os
import shutil
from typing import Tuple, Dict

from patch_xml.modinfo import ModInfo
from patch_xml.patch import Patch
from patch_xml.user_config import UserConfig
from patch_xml.vanilla_tunings import VanillaTunings

from ts4lib.libraries.ts4folders import TS4Folders
from ts4lib.utils.singleton import Singleton
from sims4communitylib.utils.common_log_registry import CommonLog


mod_name = ModInfo.get_identity().name
log: CommonLog = CommonLog(f"{ModInfo.get_identity().name}", ModInfo.get_identity().name, custom_file_path=None)
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
                    d1 = fp.read()
                with open(mod_gv, 'rb') as fp:
                    d2 = fp.read()
                if d1 == d2:
                    self.game_updated = False
                else:
                    os.unlink(mod_gv)
                    for f in {'patch.txt', 'patch.txt'}:
                        file = os.path.join(self.ts4f.data_folder, f)
                        if os.path.exists(file):
                            os.unlink(file)

            VanillaTunings().init(write_all_tunings=False, dump_xml=False, xml_comments=True, pretty_xml=True, force_refresh=self.game_updated)

            user_provided_patches: Dict = self.uc.merge_configuration_files()
            parsed_patches: Tuple = self.uc.join_configuration(user_provided_patches)
            self.patch.init(parsed_patches)

            shutil.copyfile(ts4_gv, mod_gv, follow_symlinks=False)
        except:
            log.error(f"Could not initialize Patch XML!", throw=True)
        log.debug(f"Init completed")


Init()
