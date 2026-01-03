import os
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from patch_xml.xml_patcher import XmlPatcher
from ts4lib.libraries import ET


class PatchOffline:
    def __init__(self):

        actions = {
            'prom_duration': {
                'xpath': "/I/T[@n='duration']",
                'text': '360',  # 2 hours longer if it starts 2 hours earlier
            },
            'prom_max_participants': {
                'xpath': "/I/T[@n='max_participants']",
                'text': '30',  # invite 30 instead of 20 sims
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