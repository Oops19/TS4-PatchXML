#
# LICENSE
# https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2023 https://github.com/Oops19
#


from typing import Set, Tuple
from xml.etree.ElementTree import Element

from patch_xml.modinfo import ModInfo

from xml.etree import ElementTree
from sims4communitylib.utils.common_log_registry import CommonLog


mod_name = ModInfo.get_identity().name
log: CommonLog = CommonLog(ModInfo.get_identity(), ModInfo.get_identity().name, custom_file_path=None)
log.enable()


class TuningTools:

    def is_in(self, tuning_name: str, tuning_id: str, tuning_search_names: Set[str]) -> Tuple[int, str]:
        """
        Compare lower case stings.
        @return a dict with {tuning_id: 'tuning_search_name'}. tuning_id is set to zero if nothing is found or an error occurs.
        """
        rv = (0, '')
        try:
            if tuning_id.startswith('0x'):
                tuning_id = int(tuning_id, 16)
            else:
                tuning_id = int(tuning_id)
        except:
            log.error(f"Could not parse '{tuning_name}' ({tuning_id}).", throw=False)
            return rv

        tuning_name = tuning_name.lower()
        for tuning_search_name in tuning_search_names:
            tuning_search_name = tuning_search_name.lower()
            if tuning_search_name == tuning_name:
                return tuning_id, tuning_search_name  # exact match
            elif tuning_search_name == '*':
                return tuning_id, tuning_search_name  # wildcard match
            elif tuning_search_name.startswith('*'):
                if tuning_search_name.endswith('*'):
                    _tuning_search_name = tuning_search_name[1:-1]
                    if _tuning_search_name in tuning_name:
                        return tuning_id, tuning_search_name  # contains match
                else:
                    _tuning_search_name = tuning_search_name[1:]
                    if tuning_name.endswith(_tuning_search_name):
                        return tuning_id, tuning_search_name  # end match
            elif tuning_search_name.endswith('*'):
                _tuning_search_name = tuning_search_name[:-1]
                if tuning_name.startswith(_tuning_search_name):
                    return tuning_id, tuning_search_name  # start match

        return rv

    def clone(self, node: Element) -> ElementTree:
        tag = node.tag
        attrib = node.items()  # bin
        # attrib = node.attrib  # ET
        text = node.text
        # noinspection PyTypeChecker
        root = Element(tag, attrib)
        if text:
            text = text.strip()
            root.text = text
        for child in node:
            e = self.clone(child)
            if e is not None:
                root.append(e)
        return root
