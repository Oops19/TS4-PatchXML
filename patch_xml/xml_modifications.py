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


try:
    from sims4communitylib.utils.common_log_registry import CommonLog, CommonLogRegistry
    log: CommonLog = CommonLogRegistry.get().register_log(ModInfo.get_identity(), ModInfo.get_identity().name)
except:
    from ts4lib.utils.un_common_log import UnCommonLog
    log: UnCommonLog = UnCommonLog(ModInfo.get_identity().name, ModInfo.get_identity().name)

log.enable()


class XmlModification:
    """
    Class to modify XML elements.
    It allows to add, delete and modify elements.
    XPATH always defines the base.
    """

    @staticmethod
    def as_str(e: Element) -> str:
        s = ElementTree.tostring(e, encoding='UTF-8').decode('UTF-8').replace('\n', '')
        s = re.sub(r'> *<', '><', s).strip()
        return s

    @staticmethod
    def remove_nodes(elements: List[Element], xpath: str,  root: Element):
        log.debug(f"remove_nodes(xpath='{xpath}', found_elements={len(elements)})")
        if '/' not in xpath:
            for element in elements:
                root.remove(element)
                log.info(f"\tNode '<{element.tag} {element.attrib}/>' removed.")
            return

        xpath, _, child_xpath = xpath.rpartition('/')
        log.debug(f"\txpath = {xpath}; child_xpath = {child_xpath}")

        parents = root.findall(xpath)
        for parent in parents:
            # log.debug(f"\tparent = {XmlModification.as_str(parent)}")  # TODO

            if child_xpath[0] == '[':
                _del_elements = parent.findall(child_xpath[1])
                _filter = re.sub(r"\[.=['\"](.*)['\"]\]", r"\g<1>", child_xpath)
            else:
                _del_elements = parent.findall(child_xpath)
                _filter = None

            if not _del_elements:
                log.info(f"\tNo elements found for '{child_xpath}'")
            else:
                for _del_element in _del_elements:
                    if _filter is None or _filter == _del_element.text:
                        log.info(f"\tDeleting: {XmlModification.as_str(_del_element)}")
                        parent.remove(_del_element)

        r"""
        parents = root.findall(xpath)
        for parent in parents:
            log.debug(f"parent = {XmlModification.as_str(parent)}")  # TODO
            elements = parent.findall(child_xpath)
            for element in elements:
                parent.remove(element)
                log.info(f"Node '<{element.tag} {element.attrib}/>' removed.")
        """


    @staticmethod
    def delete_element(elements: List[Element], xpath: str, xml_elements: List[Dict] = None, match: str = '*'):
        log.debug(f"delete_element(xpath='{xpath}', xml_elements='{xml_elements}', match='{match}'; found_elements={len(elements)})")
        for element in elements:
            log.debug(f"Element: {ElementTree.tostring(element, encoding='UTF-8').decode('UTF-8')}")
            del_elements = element.findall(match)
            log.debug(f"'<{element.tag} {element.attrib}>...</{element.tag}>' contains '{len(del_elements)}' elements to delete.")
            if del_elements is None:
                continue
            for del_element in del_elements:
                log.debug(f"Checking element '<{del_element.tag} {del_element.attrib}>...</{del_element.tag}>' ...")
                if xml_elements is None:
                    element.remove(del_element)
                    log.info(f"Element '<{del_element.tag}/>' deleted.")
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
                        elif ((xml_element.get('tag', None) is None or xml_element.get('tag') == del_element.tag)) and \
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
    def add_element(elements: List[Element], xpath: str, xml_elements: List[Dict], add_comments: bool = False):
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
                    # This may cause issues for TS4
                    if add_comments and xml_element.get('comment'):
                        log.warn(f"Adding comment {xml_element.get('comment')} which might cause issues.")
                        element.append(ElementTree.Comment(f"{xml_element.get('comment')}"))
                elif xml_element.get('_xml'):
                    new_node = ElementTree.XML(f"{xml_element.get('_xml')}")
                    element.append(new_node)

    @staticmethod
    def update_element(elements: List[Element], xpath: str, xml_elements: List[Dict]):
        print(f"update_element(xpath='{xpath}', xml_elements='{xml_elements}'; found_elements={len(elements)})")
        for element in elements:
            for xml_element in xml_elements:
                if xml_element.get('text'):
                    element.text = f"{xml_element.get('text')}"

    @staticmethod
    def modify_element(elements: List[Element], xpath: str, text: str = None, attributes: Dict = None, comment: str = None):
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
            if comment:
                log.warn(f"Adding comment {comment} which might cause issues")
                element.append(ElementTree.Comment(f" {comment} "))
