#
# LICENSE https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2023 https://github.com/Oops19
#
import re
from typing import Dict
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

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

            # Basic support for http://xpather.com/ XPath syntax.
            if xpath[0] == '/':
                xpath = re.sub(r'/\*', r'', xpath)  # remove '/*'
                xpath = re.sub(r'^/[a-zA-z](?:\[[^]]*])?$', r'.', xpath)  # replace '/I' or '/I[...]' with '.'
                xpath = re.sub(r'^/[a-zA-z](?:\[[^]]*])?/', r'', xpath)  # replace '/I/...' or '/I[...]/...' with '...'
                xpath = re.sub(r'/([A-Z])\[contains\(text\(\), *("[^"]*")\)]', r'/[\g<1>=\g<2>]/\g<1>', xpath)  # replace '/X[contains(text(), "Y"]' with '/[X="Y"]/X'
                xpath = re.sub(r'/([A-Z])\[text\(\)("[^"]*")]', r'/[\g<1>=\g<2>]/\g<1>', xpath)  # replace '/X[text="Y"]' with '/[X="Y"]/X'
            if xpath == '' or len(xpath) == 2:  # '/[a-zA-Z]', usually '/I':
                xpath = '.'
            if '/[' in xpath:
                # ElementTree doesn't support ElementTree.strip_tags(root, etree.Comment)
                # Convert to string and replace '<!--.*?-->' (shortest match) with ''
                # (?:...) - don't create a  match group
                # (...)* - match all occurrences
                # We do this that the string match can match the string exactly. '123<!-- Happy -->' ==> '123' which will match '123'
                xml = f"{ElementTree.tostring(root, encoding='UTF-8').decode('UTF-8')}"
                xml = re.sub(r'(?:<!--.*?-->)*', r'', xml)
                xml = re.sub(r'[\r\n]*', r'', xml)
                root = ElementTree.fromstring(xml)

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
