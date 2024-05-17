#
# LICENSE https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2023 https://github.com/Oops19
#


from typing import Dict
from xml.etree.ElementTree import Element

from patch_xml.modinfo import ModInfo
from patch_xml.modifications import Modification

from patch_xml.modinfo import ModInfo
try:
    from sims4communitylib.utils.common_log_registry import CommonLog, CommonLogRegistry
    log: CommonLog = CommonLogRegistry.get().register_log(ModInfo.get_identity(), ModInfo.get_identity().name)
except:
    from ts4lib.utils.un_common_log import UnCommonLog
    log: UnCommonLog = UnCommonLog(f"{ModInfo.get_identity().name}", ModInfo.get_identity().name, custom_file_path=None)
log.enable()


class XmlPatcher:
    def __init__(self, add_comments: bool = False):
        self.add_comments = add_comments
        self.mod = Modification()

    def patch(self, root: Element, actions: Dict) -> Element:
        for description, action in actions.items():
            log.debug(f"Processing {description} ...")
            xpath = action.get('xpath', '.')  # AttributeError: 'str' object has no attribute 'get' / ETreeTuningLoader: source='Instance: 141926 (shower_TakeShower_SingInShower), Types.INTERACTION', n='shower_TakeShower_SingInShower', s='141926', i='interaction', tag='I', err=''str' object has no attribute 'get''
            attributes = action.get('attrib')
            text = action.get('text', '')
            comment = action.get('comment', '')
            if not self.add_comments:
                comment = ''
            delete_xml_elements = action.get('delete')
            match_xml_elements = action.get('match', '*')
            add_xml_elements = action.get('add')

            if delete_xml_elements:
                self.mod.delete_element(root, xpath, delete_xml_elements, match_xml_elements)

            if add_xml_elements:
                self.mod.add_element(root, xpath, add_xml_elements, add_comments=self.add_comments)

            if text or attributes:
                self.mod.modify_element(root, xpath, text, attributes, comment)

        # log.debug(f"NODE: {ElementTree.tostring(root, encoding='UTF-8').decode('UTF-8')}")
        return root
