import os
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from patch_xml.xml_patcher import XmlPatcher
from ts4lib.libraries import ET


class PatchOffline:
    def __init__(self):

        actions = {
            'remove_teen': {
                'xpath': "/I/L[@n='test']",
                'match': "L/V[@t='sim_info']/U[@n='sim_info']/V[@n='ages']/L[@n='specified']/[E='TEEN']/../../../..",
                'delete': [{'tag': 'L', }, ],
            },
            'add_teen': {
                'xpath': "/I/L[@n='test']/L/V[@t='sim_info']/U[@n='sim_info']/V[@n='ages']/L[@n='specified']",
                'add': [
                    {'tag': 'E', 'text': 'TEEN'},
                ],
            },
        }

        # "L[@n='test']/L/V[@t='sim_info']/U[@n='sim_info']/V[@t='specified']
        #   <L n="test">
        #     <L>
        #       <V t="sim_info">
        #         <U n="sim_info">
        #           <V n="ages" t="specified">
        #             <L n="specified">
        #               <E>YOUNGADULT</E>

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