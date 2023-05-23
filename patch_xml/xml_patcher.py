#
# LICENSE https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2023 https://github.com/Oops19
#


from typing import Dict
from xml.etree.ElementTree import Element

from patch_xml.modinfo import ModInfo
from patch_xml.modifications import Modification

from sims4communitylib.utils.common_log_registry import CommonLog


mod_name = ModInfo.get_identity().name
log: CommonLog = CommonLog(f"{ModInfo.get_identity().name}", ModInfo.get_identity().name, custom_file_path=None)
log.enable()


class XmlPatcher:
    def __init__(self):
        self.mod = Modification()

    def patch(self, root: Element, actions: Dict) -> Element:
        for description, action in actions.items():
            log.debug(f"Processing {description} ...")
            xpath = action.get('xpath', '.')
            attributes = action.get('attrib')
            text = action.get('text', '')
            delete_xml_elements = action.get('delete')
            match_xml_elements = action.get('match', '*')
            add_xml_elements = action.get('add')

            if delete_xml_elements:
                self.mod.delete_element(root, xpath, delete_xml_elements, match_xml_elements)

            if add_xml_elements:
                self.mod.add_element(root, xpath, add_xml_elements)

            if text or attributes:
                self.mod.modify_element(root, xpath, text, attributes)

        # log.debug(f"NODE: {ElementTree.tostring(root, encoding='UTF-8').decode('UTF-8')}")
        return root
