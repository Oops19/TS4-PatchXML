import os
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from patch_xml.xml_patcher import XmlPatcher
from ts4lib.libraries import ET


class PatchOffline:
    def __init__(self):
        # Add the patch actions here, just the actions:
        #   <L n="test_globals">
        #     <V t="sim_info">
        #       <U n="sim_info">
        #         <V n="ages" t="specified">
        #           <L n="specified">

        actions = {
            'allow_for_everyone': {
                'xpath': "/I/L[@n='tests']/L",
                'delete': [{'tag': 'V', 'attrib': {'t': 'test_set_reference'}}, ],
            },
            'deny_for_everyone': {
                'xpath': ".",
                'add': [
                    {'tag': 'T', 'attrib': {'n': 'allow_user_directed'}, 'text': 'False'},
                    {'tag': 'T', 'attrib': {'n': 'allow_autonomous'}, 'text': 'False'},
                ],
            },
        }
        actions = {
            'filter': {
                'xpath': "/I/L[@n='test']",
                'delete': [{'tag': 'L', }, ],
                'add': [
                    {'_xml': '<L><V t="trait"><U n="trait"><L n="whitelist_traits"><T>274985</T></L></U></V></L>'}
                ],

                # 'add': [
                #                     {'_xml': '<L><V t="sim_info"><U n="sim_info"><V n="ages" t="specified"><L n="specified"><E>TEEN</E><E>YOUNGADULT</E><E>ADULT</E><E>ELDER</E></L></V></U></V><V t="sim_info"><U n="sim_info"><V n="ages" t="specified"><L n="specified"><E>TEEN</E><E>YOUNGADULT</E><E>ADULT</E><E>ELDER</E></L></V><E n="who">OtherSimsInCurrentGame</E></U></V></L>'},
                #                 ],
            },
        }

        # <T n="allow_user_directed">False</T>
        #   <T n="allow_autonomous">True</T>

        # {'tag': 'T', 'attrib': {'n': 'maximum_auto_satisfy_time'}, 'text': '0', },
        # {'tag': 'L', 'sim_age_test': ({'CHILD', 'TEEN', 'YOUNGADULT', 'ADULT', 'ELDER'}, None)}
        # {'tag': 'L', 'sim_age_test': ({, 'TEEN', 'YOUNGADULT', 'ADULT', 'ELDER'}, None)}

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