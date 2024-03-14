#
# LICENSE
# https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2024 https://github.com/Oops19
#


import ast
import gzip
import os
import pickle
import sys
import time
from typing import List, Tuple, Dict

from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from patch_xml import ET
from patch_xml.modinfo import ModInfo
from patch_xml.tuning_tools import TuningTools

from sims4.tuning.merged_tuning_manager import get_manager
from ts4lib.libraries.ts4folders import TS4Folders
from ts4lib.utils.singleton import Singleton
from sims4communitylib.utils.common_log_registry import CommonLog


mod_name = ModInfo.get_identity().name
log: CommonLog = CommonLog(f"{ModInfo.get_identity().name}", ModInfo.get_identity().name, custom_file_path=None)
log.enable()


class VanillaTunings(object, metaclass=Singleton):
    PICKLE_PROTOCOL = 4  # currently pickle.HIGHEST_PROTOCOL
    xml_lookup_table_g: Dict = {}  # {'x': b'<xml...>', ...}
    xml_lookup_table_r: Dict = {}  # {'s': b'<xml...>', ...}
    xml_lookup_table_rs: Dict = {}  # {'s': [b'<xml...>', ], ...}  # 10 elements
    comments: Dict = {}  # {'s': 'n', ...}

    node_lookup_table_r: Dict = {}  # {'s': expandedElementTree, ...}
    node_lookup_table_rs: Dict = {}  # {'s': [expandedElementTree, ...], ...}

    def __init__(self):
        self.ts4f = TS4Folders(ModInfo.get_identity().base_namespace)
        self.tunings_folder = os.path.join(self.ts4f.data_folder, 'tunings')
        self.tt = TuningTools()
        self._write_all_tunings = False
        self._dump_xml = False
        self._xml_comments = False
        self._pretty_xml = False
        self._force_refresh = False

    def init(self, write_all_tunings: bool = True, dump_xml: bool = False, xml_comments: bool = True, pretty_xml: bool = True, force_refresh: bool = False):
        log.debug('VanillaTunings - START')
        self._write_all_tunings = write_all_tunings
        self._dump_xml = dump_xml
        self._xml_comments = xml_comments
        self._pretty_xml = pretty_xml
        self._force_refresh = force_refresh

        try:
            os.makedirs(self.tunings_folder, exist_ok=True)
            ready = False
            if (self._force_refresh is False) and (self._dump_xml is False):
                try:
                    self.load_lookups()
                    ready = True
                except Exception as e:
                    log.error(f"Could not read cached data ({e})", throw=False)
            if ready is False:
                self.process_xml_list()
                self.save_lookups()

            if self._write_all_tunings is True:
                self.write_all_tunings()

        except Exception as e:
            log.error(f"{e}", throw=True)
        log.debug('VanillaTunings - END')

    def process_xml_list(self):
        merged_tuning_manager = get_manager()
        xml_list: List = merged_tuning_manager.binxml_list
        log.debug(f"Processing '{len(xml_list)}' items")
        idx = num_elements_g = num_elements_r = 0

        for xml_element in xml_list:
            idx += 1
            log.debug(f"Processing item {idx} ...")
            root = xml_element.root
            node = self.tt.clone(root)

            if self._dump_xml is True:
                # Log the XML nodes
                with open(os.path.join(self.tunings_folder, f"{idx}.xml"), 'wt', encoding='UTF-8') as fp:
                    fp.write(f"{ElementTree.tostring(node, encoding='UTF-8').decode('UTF-8')}")

            elements_g, elements_r = self.process_xml_element(node)
            num_elements_g += elements_g
            num_elements_r += elements_r

        log.debug(f"Elements (g) in cache: {len(VanillaTunings.xml_lookup_table_g)}/{num_elements_g}")
        log.debug(f"Elements (r) in cache: {len(VanillaTunings.xml_lookup_table_r)}/{num_elements_r}")
        log.debug(f"Elements (rs) in cache: {len(VanillaTunings.xml_lookup_table_rs)}")

        try:
            with open(os.path.join(self.tunings_folder, 'comments.txt'), 'rt', encoding='UTF-8') as fp:
                comments = ast.literal_eval(fp.read())
                comments = {**VanillaTunings.comments, **comments}
                VanillaTunings.comments = comments
        except:
            pass
        with open(os.path.join(self.tunings_folder, 'comments.txt'), 'wt', encoding='UTF-8') as fp:
            fp.write(f"{VanillaTunings.comments}")
        log.debug(f"Comments in cache: {len(VanillaTunings.comments)}")

    def process_xml_element(self, root: ElementTree) -> Tuple[int, int]:
        elements_g = root.findall('g/*[@x]')
        log.debug(f"Processing (g) '{len(elements_g)}' elements ...")

        for element in elements_g:
            x = element.get('x', 0)  # '123', not 123
            if VanillaTunings.xml_lookup_table_g.get(x, None) is None:
                # VanillaTunings.xml_lookup_table_g.update({x_value: copy.deepcopy(element)})
                VanillaTunings.xml_lookup_table_g.update({x: ElementTree.tostring(element, encoding='UTF-8')})  # store byte-string
            else:
                log.warn(f"Replacing (g) '{ElementTree.tostring(element, encoding='UTF-8').decode('UTF-8')}'.")

        elements_r = root.findall('R/*')
        log.debug(f"Processing (r) '{len(elements_r)}' elements ...")
        for element in elements_r:
            s = element.get('s', 0)
            n = element.get('n', '')
            VanillaTunings.comments.update({s: n})

            elem = ElementTree.tostring(element, encoding='UTF-8')
            if VanillaTunings.xml_lookup_table_r.get(s, None) is None:
                VanillaTunings.xml_lookup_table_r.update({s: elem})
            else:
                VanillaTunings.xml_lookup_table_r.update({s: None})
                current_elements = VanillaTunings.xml_lookup_table_rs.get(s, [])
                current_elements.append(elem)
                VanillaTunings.xml_lookup_table_rs.update({s: current_elements})  # ~10 s values are not unique !
        return len(elements_g), len(elements_r)

    def _join(self, node: Element) -> ElementTree:
        tag = node.tag
        # attrib = node.items()  # bin
        attrib = node.attrib  # ET
        text = node.text
        # noinspection PyTypeChecker  # bin
        root = Element(tag, attrib)
        if text:
            text = text.strip()
            root.text = text
        for child in node:
            ref_value = child.attrib.get('x')
            if ref_value and child.tag == 'r':
                # attrib = node.items()  # bin
                attrib = child.attrib  # ET
                child = ElementTree.fromstring(VanillaTunings.xml_lookup_table_g.get(ref_value))
                if child is None:
                    pass
                    log.warn("\t\tlookup is None")
                else:
                    attrib.update(child.attrib)
                    del attrib['x']
                    child.attrib = attrib
            e = self._join(child)
            if e is not None:
                root.append(e)
        return root

    def write_all_tunings(self):
        recursion_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(5000)
        log.debug(f"Expanding (rs) with {len(VanillaTunings.xml_lookup_table_rs)} elements.")
        t = 30 + time.time()
        idx = 0
        for s, xmls in VanillaTunings.xml_lookup_table_rs.items():
            for xml in xmls:
                if time.time() > t:
                    log.debug(f"    Expanded {idx} elements.")
                    t = 30 + time.time()
                idx += 1
                node = ElementTree.fromstring(xml)
                new_node = self._join(node)
                current_nodes = VanillaTunings.node_lookup_table_rs.get(s, [])
                current_nodes.append(new_node)
                VanillaTunings.node_lookup_table_rs.update({s: current_nodes})

        log.debug(f"Expanding (r) with {len(VanillaTunings.xml_lookup_table_r)} elements.")
        t = 30 + time.time()
        idx = 0
        for s, element in VanillaTunings.xml_lookup_table_r.items():
            if time.time() > t:
                log.debug(f"    Expanded {idx} elements.")
                t = 30 + time.time()
            idx += 1
            node = ElementTree.fromstring(element)
            new_node = self._join(node)
            VanillaTunings.node_lookup_table_r.update({s: new_node})

        sys.setrecursionlimit(recursion_limit)

        log.debug(f"Writing {len(VanillaTunings.xml_lookup_table_r)} tuning files.")
        t = 30 + time.time()
        idx = 0
        for element in VanillaTunings.xml_lookup_table_r:
            if time.time() > t:
                log.debug(f"    Wrote {idx} files.")
                t = 30 + time.time()
            idx += 1

            self.write_tuning(element)
        log.debug(f"Writing completed")

    def write_tuning(self, element: ElementTree, file_suffix: str = 'xml'):
        if self._xml_comments:
            t_elements = element.findall('.//T')
            for t_element in t_elements:
                try:
                    txt = VanillaTunings.comments.get(t_element.text)
                    if txt:
                        t_element.append(ElementTree.Comment(f"{txt}"))
                except:
                    pass

        if self._pretty_xml:
            ET.indent(element)

        # Write the file
        i = element.get('i', 'i')
        s = element.get('s', '0')
        n = element.get('n', 'n')
        os.makedirs(os.path.join(self.tunings_folder, i), exist_ok=True)
        log.debug(f'Writing {os.path.join(self.tunings_folder, i, f"{s}.{n}.{file_suffix}")}')
        with open(os.path.join(self.tunings_folder, i, f"{s}.{n}.{file_suffix}"), 'wt', encoding='UTF-8') as fp:
            fp.write(f"{ElementTree.tostring(element, encoding='UTF-8').decode('UTF-8')}")

    def get_tuning(self, tuning_id: str, tuning_class: str = None) -> ElementTree:
        """
        @param tuning_id The ID of the tuning to retrieve
        @param tuning_class Optional parameter, only used if the tuning_id is not unique
        """
        log.debug(f"get_tuning({tuning_id}, {tuning_class})")

        b_xml = VanillaTunings.xml_lookup_table_r.get(tuning_id)
        root = ElementTree.fromstring('<I/>')
        if b_xml is not None:
            root = ElementTree.fromstring(b_xml)
        else:
            b_xmls = VanillaTunings.xml_lookup_table_rs.get(tuning_id)
            if b_xmls:
                for b_xml in b_xmls:
                    root = ElementTree.fromstring(b_xml)
                    if tuning_class == root.get('c', ''):
                        break
        tuning_class = root.get('c', '')
        tuning_name = root.get('n', '')
        file = os.path.join(self.tunings_folder, tuning_class, f"{tuning_id}.{tuning_name}.xml")
        if os.path.exists(file):
            with open(file, 'rt', encoding='UTF-8') as fp:
                xml = fp.read()
                root = ElementTree.fromstring(xml)
        else:
            root = self._get_tuning(root)
        log.debug(f"get_tuning({tuning_id}, {tuning_class}) -> {root}")  # log only Element
        return root

    def _get_tuning(self, root: ElementTree) -> ElementTree:
        """
        Expand the tuning
        """
        recursion_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(5000)
        element = self._join(root)
        sys.setrecursionlimit(recursion_limit)

        self.write_tuning(element)
        return element

    def save_lookups(self):
        for f in ['xml_lookup_table_g', 'xml_lookup_table_r', 'xml_lookup_table_rs', 'comments']:
            file = os.path.join(self.tunings_folder, f"{f}.zip")
            data = getattr(VanillaTunings, f)
            with gzip.open(file, mode='wb') as fp:
                pickle.dump(data, fp, protocol=VanillaTunings.PICKLE_PROTOCOL)
                log.debug(f"Saved {len(data)} {f} elements")

    def load_lookups(self):
        for f in ['xml_lookup_table_g', 'xml_lookup_table_r', 'xml_lookup_table_rs', 'comments']:
            file = os.path.join(self.tunings_folder, f"{f}.zip")
            with gzip.open(file, mode='rb') as fp:
                data = pickle.load(fp)
                setattr(VanillaTunings, f, data)
                log.debug(f"Loaded {len(data)} {f} elements")
