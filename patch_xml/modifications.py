#
# LICENSE
# https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2023 https://github.com/Oops19
#


import re
from typing import List, Dict
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from patch_xml.modinfo import ModInfo

from sims4communitylib.utils.common_log_registry import CommonLog


mod_name = ModInfo.get_identity().name
log: CommonLog = CommonLog(f"{ModInfo.get_identity().name}", ModInfo.get_identity().name, custom_file_path=None)
log.enable()


class Modification:
    """
    Class to modify XML elements.
    It allows to add, delete and modify elements.
    XPATH always defines the base.
    """

    @staticmethod
    def delete_element(root: Element, xpath: str, xml_elements: List[Dict] = None, match: str = '*'):
        elements = root.findall(xpath)
        log.debug(f"delete_element(xpath='{xpath}', xml_elements='{xml_elements}', match='{match}'; found_elements={len(elements)})")
        for element in elements:
            del_elements = element.findall(match)
            log.debug(f"'<{element.tag} {element.attrib}>...</{element.tag}>' contains '{len(del_elements)}' elements to delete.")
            if del_elements is None:
                continue
            for del_element in del_elements:
                log.debug(f"Checking element '<{del_element.tag} {del_element.attrib}>...</{del_element.tag}>' ...")
                if xml_elements is None:
                    element.remove(del_element)
                else:
                    for xml_element in xml_elements:
                        if xml_element.get('empty', False) is True:
                            if (not list(del_element)) and \
                                    (xml_element.get('tag', '&entity') == del_element.tag) and \
                                    (xml_element.get('attrib', None) is None or xml_element.get('attrib') == del_element.attrib) and \
                                    (xml_element.get('text', None) is None or xml_element.get('text') == del_element.text.strip()):
                                # Delete this empty tag
                                element.remove(del_element)
                                log.info(f"Element '<{del_element.tag}/>' deleted.")
                        elif (xml_element.get('tag', None) is None or xml_element.get('tag') == del_element.tag) and \
                                (xml_element.get('text', None) is None or xml_element.get('text') == del_element.text.strip()):
                            if not xml_element.get('attrib'):
                                element.remove(del_element)
                                log.info(f"Element '<{del_element.tag.strip()} {del_element.attrib}>...</{del_element.tag.strip()}>' deleted.")
                            else:
                                no_match = False
                                for k, v in xml_element.get('attrib').items():
                                    if not del_element.get(k).strip() == v:
                                        no_match = True
                                        break
                                if not no_match:
                                    element.remove(del_element)
                                    log.info(f"Element '<{del_element.tag.strip()} {del_element.attrib}>...</{del_element.tag.strip()}>' deleted.")

    @staticmethod
    def add_element(root: Element, xpath: str, xml_elements: List[Dict]):
        elements: List[ElementTree.Element] = root.findall(xpath)
        log.debug(f"add_element(xpath='{xpath}', xml_elements='{xml_elements}'; found_elements={len(elements)})")
        for element in elements:
            for xml_element in xml_elements:
                log.debug(f"Adding '{xml_element}' to '<{element.tag}>{element.text}</{element.tag}>'.")
                if xml_element.get('tag'):
                    new_tag = ElementTree.SubElement(element, f"{xml_element.get('tag')}")
                    if xml_element.get('text'):
                        new_tag.text = f"{xml_element.get('text')}"
                    if xml_element.get('attrib'):
                        for k, v in xml_element.get('attrib').items():
                            new_tag.set(f"{k}", f"{v}")
                    if xml_element.get('comment'):
                        element.append(ElementTree.Comment(f"{xml_element.get('comment')}"))

    @staticmethod
    def modify_element(root: Element, xpath: str, text: str = None, attributes: Dict = None):
        elements: List[ElementTree.Element] = root.findall(xpath)
        log.debug(f"modify_element(xpath='{xpath}', text='{text}', attributes='{attributes }'; found_elements={len(elements)})")
        for element in elements:
            if attributes:
                for k, v in attributes.items():
                    element.set(k, v)
            if text:
                rv = re.match(r'^(add|sub|x_sub|mul|div|x_div|pow|x_pow)\((-?[0-9]+(?:\.[0-9]*)?) *, *(\d) *\)$', text)
                if rv:
                    value = float(element.text.strip())
                    _rv = float(rv[2])
                    if rv[1] == 'mul':
                        value = value * _rv
                    elif rv[1] == 'div':
                        value = value / _rv
                    elif rv[1] == 'x_div':
                        value = _rv / value
                    elif rv[1] == 'add':
                        value = value + _rv
                    elif rv[1] == 'sub':
                        value = value - _rv
                    elif rv[1] == 'x_sub':
                        value = _rv - value
                    elif rv[1] == 'pow':
                        value = value ** _rv
                    elif rv[1] == 'x_pow':
                        value = _rv ** value
                    element.text = f"{value:0.{int(rv[3])}f}"
                else:
                    element.text = text
