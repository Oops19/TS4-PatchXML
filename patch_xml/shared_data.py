#
# LICENSE
# https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2024 https://github.com/Oops19
#


import os
import re
import shutil
from typing import Dict, Union
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from patch_xml.modinfo import ModInfo
from ts4lib.libraries.ts4folders import TS4Folders
from ts4lib.utils.singleton import Singleton

from sims4communitylib.utils.common_log_registry import CommonLog, CommonLogRegistry

log: CommonLog = CommonLogRegistry.get().register_log(ModInfo.get_identity(), ModInfo.get_identity().name)
log.enable()


class SharedData(metaclass=Singleton):
    r"""
    Global definitions.
    Directory structure:
    dir_tunings = mod_data/patch_xml/tunings/ - tuning files in */*.xml
    dir_mod_data_gv = mod_data/patch_xml/1.0.111.111/ - directory for the current game version
    dir_ts4_mods_gv = mod_data/patch_xml/2.0.222.222/ - directory for a new game version
    file_cache_index = mod_data/patch_xml/2.0.222.444/cache_index.txt - file with links to all already patched tuning files
    """
    def __init__(self):
        log.debug(f"SharedData().init()")
        self._initialized = False
        self.ts4f = TS4Folders(ModInfo.get_identity().base_namespace)

        self.file_ts4_mods_gv = os.path.join(self.ts4f.ts4_folder_mods, 'GameVersion.txt')
        self.file_mod_data_gv = os.path.join(self.ts4f.data_folder, 'GameVersion.txt')
        ts4_mods_gv = self._get_version(self.file_ts4_mods_gv)
        mod_data_gv = self._get_version(self.file_mod_data_gv)

        self.dir_tunings = os.path.join(self.ts4f.data_folder, 'tunings')
        self.dir_mod_data_gv = os.path.join(self.ts4f.data_folder, mod_data_gv)  # mod_data/patch_xml/1.0.111.111/
        self.dir_ts4_mods_gv = os.path.join(self.ts4f.data_folder, ts4_mods_gv)  # mod_data/patch_xml/2.0.222.222/
        os.makedirs(self.dir_tunings, exist_ok=True)
        os.makedirs(self.dir_mod_data_gv, exist_ok=True)
        os.makedirs(self.dir_ts4_mods_gv, exist_ok=True)

        self.file_cache_index = os.path.join(self.dir_ts4_mods_gv, 'cache_index.txt')

        if ts4_mods_gv == mod_data_gv and mod_data_gv != 0 and os.path.exists(self.file_cache_index):
            self._game_updated = False
        else:
            self._game_updated = True

        self.file_patch = os.path.join(self.ts4f.data_folder, 'patch.ETreeTuningLoader.txt')
        self.file_no_patch = os.path.join(self.ts4f.data_folder, 'no-patch.ETreeClassCreator.txt')

        self.patched_tunings_cache: Union[None, Dict[str, Union[Element, ElementTree]]] = None  # Cache to read from  {id: xml, ...}
        self.patch_tuning_files: Union[None, Dict[str, str]] = None   # Add new tunings, save to cache later  {id: filename, ...}

    def initialize_cache_directory(self):
        for directory in [self.dir_ts4_mods_gv, self.dir_mod_data_gv]:
            try:
                shutil.rmtree(directory)
            except:
                pass
        os.makedirs(self.dir_mod_data_gv, exist_ok=True)

        old = [os.path.join(self.ts4f.data_folder, 'patch.txt'), os.path.join(self.ts4f.data_folder, 'nopatch.txt'), ]  # TODO remove me one day
        for file in [self.file_patch, self.file_no_patch, *old, ]:
            try:
                os.unlink(file)
            except:
                pass

    @property
    def game_updated(self) -> bool:
        return self._game_updated

    @property
    def initialized(self) -> bool:
        return self._initialized

    @initialized.setter
    def initialized(self, is_ready: bool):
        self._initialized = is_ready

    def copy_version(self):
        # Mark the current TS4 version as the current version for PatchXML.
        # This allows to use the cache.
        shutil.copyfile(self.file_ts4_mods_gv, self.file_mod_data_gv, follow_symlinks=False)

    @staticmethod
    def _get_version(filename: str) -> str:
        game_version = '0.0'
        try:
            with open(filename, 'rb') as fp:
                game_version = fp.read().decode(errors='ignore')  # convert b to str and ignore errors
                game_version = re.sub(r'[^0-9.]', '', game_version)  # in case of UTF-8 characters which survived 'ignore': replace everything with '' except of '0-9' and '.'
        except:
            pass
        return game_version