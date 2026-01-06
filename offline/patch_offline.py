import os
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from patch_xml.xml_patcher import XmlPatcher
from ts4lib.libraries import ET


class PatchOffline:
    def __init__(self):

        actions = {
            'remove_teen': {
                'xpath': "/I/U[@n='value']/L[@n='cross_age_tuning']/U",
                'match': "U[E='ADULT']/../L[@n='target_age_to_multiplier']/U/E[n='TEEN']/../..",
                'delete': [{'tag': 'U', }, ],
            },
        }

        # <I c="CrossAgeTuning" i="snippet" m="snippets" n="crossAgeTuning_RomanceZero" s="338529"><!-- 0x0000000000052A61 -->
        #   <U n="value">
        #     <L n="cross_age_tuning">
        #       <U>
        #         <E n="subject_age">ADULT</E>

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