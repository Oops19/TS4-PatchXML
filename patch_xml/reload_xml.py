import os
import re
from datetime import date
from typing import List, Any
import sims4
import services
from patch_xml.shared_data import SharedData
from sims4.resources import Types
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from create_enums.modinfo import ModInfo
from ts4lib.custom_enums.custom_resource_type import CustomResourceType
from ts4lib.custom_enums.enum_types.custom_enum import CustomEnum
from ts4lib.libraries.file_utils import FileUtils
from ts4lib.libraries.filename_helper import FilenameHelper

try:
    from sims4communitylib.utils.common_log_registry import CommonLog, CommonLogRegistry
    log: CommonLog = CommonLogRegistry.get().register_log(ModInfo.get_identity(), ModInfo.get_identity().name)
except:
    from ts4lib.utils.un_common_log import UnCommonLog

    log: UnCommonLog = UnCommonLog(ModInfo.get_identity().name, ModInfo.get_identity().name,  custom_file_path=None)
log.enable()


class ReloadXml:

    def __init__(self):
        pass

    def _get_instance_manager(self, file: str) -> Any:
        instance_manager = None
        manager_name = None
        fn = FilenameHelper(file)
        if fn.type == 0:
            # not a TS4_tttttttt_gggggggg_iiiiiiiiiiiiiiii.file.xml file
            with open(file, 'rt', encoding='UTF-8') as fp:
                line = fp.readline()
                line = f"{line}</I>"
                e: Element = ElementTree.XML(line)
                fn.instance = int(e.attrib.get('s'))
                fn.group = int(e.attrib.get('group'), 0)  # very likely not in the XML
                fn.type = int(e.attrib.get('type'), 0)  # very likely not in the XML
                if fn.type == 0:
                    manager_name = e.attrib.get('i')  # e.g. snippet, interaction

        if manager_name is None and fn.type:
            try:
                manager_name = CustomResourceType(fn.type).name
            except Exception as e:
                log.warn(f"Unknown type '{fn.type}' - can't get manager ({e})")
                return instance_manager

        try:
            instance_manager = services.get_instance_manager(sims4.resources.Types[manager_name.upper()])
        except Exception as e:
            log.warn(f"Unknown manager '{manager_name}' ({e})")
            return instance_manager

        return instance_manager

    def read_xml(self, filename_pattern: str, directory: str = None ):
        rv: List[str] = []
        if directory is None:
            directory = SharedData().dir_tunings
        fu = FileUtils(directory)
        files = fu.find_files(filename_pattern)
        for file in files:
            instance_manager = self._get_instance_manager(file)


        #         sims4.callback_utils.invoke_callbacks(sims4.callback_utils.CallbackEvent.TUNING_CODE_RELOAD)

source_dir = os.path.join('R:', 'xml',)
cws = ReloadXml()

r"""
<I c="GameObject" i="object" m="objects.game_object"
<I c="Recipe" i="recipe" m="crafting.recipe" n="recipe_Drink
<I c="Commodity" i="statistic" m="statistics.commodity" n="commodity
"""