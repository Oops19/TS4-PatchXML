import os
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from patch_xml.xml_patcher import XmlPatcher
from ts4lib.libraries import ET


class PatchOffline:
    def __init__(self):

        actions = {
            'add_mixers': {
                'xpath': "/I/U[@n='game_effect_modifier']/L[@n='_game_effect_modifiers']/V[@t='autonomy_modifier']/U[@n='autonomy_modifier']/V[@n='provided_affordance_compatibility']/U[@n='literal']/V[@n='default_inclusion']/U[@n='exclude_all']/L[@n='include_affordances']",
                'add': [{'tag': 'T', 'text': '12148471909530941517'}, ],  # o19_si_sim_remove_shoes based on sim_WakeUp
            },
        }

        src_tuning = os.path.join(os.path.dirname(__file__), './.src.xml')
        dst_file = os.path.join(os.path.dirname(__file__), './.dst.xml')

        fp = open(src_tuning, 'rt', encoding='UTF-8')
        tuning = fp.read()
        tuning = tuning.strip()
        if not isinstance(tuning, str):
            return
        xml: Element = ElementTree.XML(tuning)

        xml_patcher = XmlPatcher()
        new_xml = xml_patcher.patch(xml, actions)
        ET.indent(new_xml)

        fp = open(dst_file, 'wt', encoding='UTF-8', newline='')
        fp.write(f"{ElementTree.tostring(new_xml, encoding='UTF-8').decode('UTF-8')}")


if __name__ == '__main__':
    PatchOffline()