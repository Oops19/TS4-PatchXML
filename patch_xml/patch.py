#
# LICENSE
# https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2023 https://github.com/Oops19
#


import os
from typing import List, Tuple, Set, Any, Union
from xml.etree.ElementTree import Element

from patch_xml.modinfo import ModInfo
from patch_xml.tuning_tools import TuningTools
from patch_xml.vanilla_tunings import VanillaTunings
from patch_xml.xml_patcher import XmlPatcher
from sims4.tuning.merged_tuning_manager import UnavailablePackSafeResourceError

from sims4.tuning.serialization import ETreeTuningLoader, ETreeClassCreator  # patch serialization.py#88: raise ValueError(f"Trailing comma on tunable '{_}'") to remove the error
from sims4communitylib.events.event_handling.common_event_registry import CommonEventRegistry
from sims4communitylib.events.zone_spin.events.zone_late_load import S4CLZoneLateLoadEvent
from sims4communitylib.utils.common_injection_utils import CommonInjectionUtils
from ts4lib.libraries.ts4folders import TS4Folders
from ts4lib.utils.singleton import Singleton
from sims4communitylib.utils.common_log_registry import CommonLog, CommonLogRegistry

log: CommonLog = CommonLogRegistry.get().register_log(ModInfo.get_identity(), ModInfo.get_identity().name)
log.enable()


class Patch(object, metaclass=Singleton):

    logged_errors: Set[str] = set()

    def __init__(self):
        self.ts4f = TS4Folders(ModInfo.get_identity().base_namespace)
        self.tt = TuningTools()
        self.px = XmlPatcher()
        self.used_tags = self.used_instances = self.used_tuning_ids = None
        self.match_string_equal = None
        self.match_string_starts = None
        self.match_string_ends = None
        self.match_string_contains = None
        self.secret_combinations = None

        self.patch_file = os.path.join(self.ts4f.data_folder, 'patch.txt')
        if os.path.exists(self.patch_file):
            self.patch_file_data = None
        else:
            self.patch_file_data = dict()
        self.nopatch_file = os.path.join(self.ts4f.data_folder, 'nopatch.txt')
        if os.path.exists(self.nopatch_file):
            self.nopatch_file_data = None
        else:
            self.nopatch_file_data = dict()

    def init(self, parsed_patches: Tuple[Set, Set, Set, Set, Set, Set, Set, List]):
        self.used_tags, self.used_instances, self.used_tuning_ids,\
            self.match_string_equal, self.match_string_starts,\
            self.match_string_ends, self.match_string_contains, self.secret_combinations = parsed_patches

    def nopatch(self, _self: Union[ETreeTuningLoader, ETreeClassCreator], node: Any, caller: str = None) -> Element:
        if self.nopatch_file_data is not None:
            try:
                if isinstance(node, Element):
                    n = node.attrib.get('n')
                    s = node.attrib.get('s')
                else:
                    # assume isinstance(node, _tuning.BinaryTuningElement)
                    n = node.get('n')
                    s = node.get('s')
                self.nopatch_file_data.update({s: n})
            except Exception as e:
                log.error(f"{e}", throw=True)
        return node

    def patch(self, _self: Union[ETreeTuningLoader, ETreeClassCreator], node: Union[Element, Any], caller: str = None, verbose: bool = False) -> Element:
        tag = ''
        i = ''
        n = ''
        s = ''
        try:
            if isinstance(node, Element):
                tag = node.tag
                i = node.attrib.get('i')
                n = node.attrib.get('n')
                s = node.attrib.get('s')
            else:
                # assume isinstance(node, _tuning.BinaryTuningElement)
                tag = node.tag
                i = node.get('i')
                n = node.get('n')
                s = node.get('s')

            if self.patch_file_data is not None:
                self.patch_file_data.update({s: n})

            # This would log every tuning
            if verbose:
                log.debug(f"Checking({caller}): {tag} {i} '{n}' ({s})")
                log.debug(f"used_tags: {self.used_tags}")
                log.debug(f"used_instances: {self.used_instances}")
                log.debug(f"match_string_equal: {self.match_string_equal}")
                log.debug(f"match_string_starts: {self.match_string_starts}")
                log.debug(f"match_string_ends: {self.match_string_ends}")
                log.debug(f"match_string_contains: {self.match_string_contains}")

            val_s = int(s)
            if val_s not in self.used_tuning_ids:
                # Make sure that 'tag', 'i' and 'n' match
                if tag and tag not in self.used_tags:
                    return node
                if i and i not in self.used_instances:
                    return node
                n_matches = False
                n_lower = n.lower()
                if n_lower in self.match_string_equal:
                    n_matches = True
                else:
                    for match_string in self.match_string_starts:
                        if n_lower.startswith(match_string):
                            n_matches = True
                            break
                    if not n_matches:
                        for match_string in self.match_string_ends:
                            if n_lower.endswith(match_string):
                                n_matches = True
                                break
                    if not n_matches:
                        for match_string in self.match_string_contains:
                            if match_string in n_lower:
                                n_matches = True
                                break
                if not n_matches:
                    return node

            log.debug(f"Processing({caller}): {tag} {i} '{n}' ({s})")
            node = VanillaTunings().get_tuning(s)

            for secret_combination in self.secret_combinations:
                if val_s in secret_combination[3]:
                    log.debug(f"Tuning {n} ({s}) matches 'tuning_id'")
                    node = self.px.patch(node, secret_combination[4])
                    VanillaTunings().write_tuning(node, 'patched.xml')
                    return node

            for secret_combination in self.secret_combinations:
                if tag in secret_combination[0] and i in secret_combination[1]:
                    tuning_id, tuning_search_name = self.tt.is_in(n, s, secret_combination[2])
                    if tuning_id:
                        log.debug(f"Tuning {n} ({tuning_id}) matches '{tuning_search_name}'")
                        node = self.px.patch(node, secret_combination[4])
                        VanillaTunings().write_tuning(node, 'patched.xml')
                        return node

        except Exception as e:
            self.handle_exception(_self, node, caller, e)
            # raise e
        return node

    @staticmethod
    @CommonEventRegistry.handle_events(ModInfo.get_identity())
    def save_data(event_data: S4CLZoneLateLoadEvent):
        if Patch().nopatch_file_data is not None:
            with open(Patch().nopatch_file, 'wt', encoding='UTF-8', newline='\n') as fp:
                fp.write(f"s: n\n")
                for s, n in dict(sorted(Patch().nopatch_file_data.items())).items():
                    fp.write(f"{s}: {n}\n")
            Patch().nopatch_file_data = None
        if Patch().patch_file_data is not None:
            with open(Patch().patch_file, 'wt', encoding='UTF-8', newline='\n') as fp:
                fp.write(f"s: n\n")
                for s, n in dict(sorted(Patch().patch_file_data.items())).items():
                    fp.write(f"{s}: {n}\n")
            Patch().patch_file_data = None

    @staticmethod
    def handle_exception(_self: Union[ETreeTuningLoader, ETreeClassCreator, None], node: Union[Element, Any], caller: str, e: Exception = None):
        source = ''
        tag = ''
        i = ''
        n = ''
        s = ''
        try:
            source = _self.source
        except:
            pass
        try:
            if isinstance(node, Element):
                tag = node.tag
                i = node.attrib.get('i')
                n = node.attrib.get('n')
                s = node.attrib.get('s')
            else:
                # assume isinstance(node, _tuning.BinaryTuningElement)
                tag = node.tag
                i = node.get('i')
                n = node.get('n')
                s = node.get('s')
        except:
            pass
        log.error(f"{caller}: source='{source}'; tag='{tag}', n='{n}', s='{s}', i='{i}'; err='{e}'", throw=False)


# class ETreeTuningLoader:
#     def  _load_node(self, node, tunable_class):
@CommonInjectionUtils.inject_safely_into(ModInfo.get_identity(), ETreeTuningLoader, ETreeTuningLoader._load_node.__name__, handle_exceptions=False)
def patch_xml_tuning_loader_load_node(original, self: ETreeTuningLoader, node: Any, tunable_class, *args, **kwargs):
    root = Patch().patch(self, node, 'ETreeTuningLoader')
    try:
        return original(self, root, tunable_class, *args, **kwargs)
    except (ModuleNotFoundError, UnavailablePackSafeResourceError) as e:
        _e = f'{e}'
        if _e not in Patch.logged_errors:
            Patch.logged_errors.add(_e)
            log.warn(_e)
    except Exception as e:
        Patch().handle_exception(self, root, 'ETreeTuningLoader', e)
        # raise e


# called before ETreeTuningLoader
# class ETreeClassCreator:
#     def _load_node(self, node, tunable_class):
@CommonInjectionUtils.inject_safely_into(ModInfo.get_identity(), ETreeClassCreator, ETreeClassCreator._load_node.__name__, handle_exceptions=False)
def patch_xml_class_creator_load_node(original, self: ETreeClassCreator, node: Element, tunable_class, *args, **kwargs):
    root = Patch().nopatch(self, node, 'ETreeClassCreator')
    try:
        return original(self, root, tunable_class, *args, **kwargs)
    except (ModuleNotFoundError, UnavailablePackSafeResourceError) as e:
        _e = f'{e}'
        if _e not in Patch.logged_errors:
            Patch.logged_errors.add(_e)
            log.warn(_e)
    except Exception as e:
        Patch().handle_exception(self, root, 'ETreeClassCreator', e)
        raise e
# (NameError, TypeError)