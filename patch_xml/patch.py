#
# LICENSE
# https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2023 https://github.com/Oops19
#


import os
import time
from typing import List, Tuple, Set, Any, Union, Dict
from xml.etree.ElementTree import Element

from patch_xml.modinfo import ModInfo
from patch_xml.shared_data import SharedData
from patch_xml.tuning_tools import TuningTools
from patch_xml.vanilla_tunings import VanillaTunings
from patch_xml.xml_patcher import XmlPatcher
from sims4.tuning.merged_tuning_manager import UnavailablePackSafeResourceError

# patch serialization.py#88: raise ValueError(f"Trailing comma on tunable '{_}'") to remove the 'ETreeClassCreator' error, if any
from sims4.tuning.serialization import ETreeTuningLoader, ETreeClassCreator
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
    file_cache_index: str = ''
    patch_tuning_files: Union[None, Dict[str, str]] = {}
    t_start_class_creator = 0
    t_end_class_creator = 0
    t_duration_class_creator = 0
    t_start_tuning_loader = 0
    t_end_tuning_loader = 0
    t_duration_tuning_loader = 0

    def __init__(self):
        log.debug(f"Patch().init()")
        self.ts4f = TS4Folders(ModInfo.get_identity().base_namespace)
        self.sd = SharedData()
        Patch.file_cache_index = self.sd.file_cache_index

        self.tt = TuningTools()
        self.px = XmlPatcher()
        self.used_tags = self.used_instances = self.used_tuning_ids = None
        self.match_string_equal = None
        self.match_string_starts = None
        self.match_string_ends = None
        self.match_string_contains = None
        self.secret_combinations = None

        self.patch_file = self.sd.file_patch
        if os.path.exists(self.patch_file):
            self.patch_file_data = None
        else:
            self.patch_file_data = dict()
        self.nopatch_file = self.sd.file_no_patch
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
                log.error(f"nopatch({caller}) -> '{e}'", throw=False)
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

            # self.sd.patched_tunings_cache
            if self.sd.patched_tunings_cache:
                patched_node = self.sd.patched_tunings_cache.get(s, None)
                if patched_node:
                    return patched_node
                else:
                    return node

            if self.patch_file_data is not None:
                self.patch_file_data.update({s: n})

            # This logs every tuning. We do this as EA may catch exceptions and not log the tuning at all.
            # The log time stamp allows to match Vanilla logs '[GSI_DUMP][cjiang] Error ...' to a tuning.
            log.debug(f"Checking({caller}): {tag} {i} '{n}' ({s})")
            if verbose:
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
                    filename = VanillaTunings().write_tuning(node, 'patched.xml')
                    Patch.patch_tuning_files.update({s: filename})
                    return node

            for secret_combination in self.secret_combinations:
                if tag in secret_combination[0] and i in secret_combination[1]:
                    tuning_id, tuning_search_name = self.tt.is_in(n, s, secret_combination[2])
                    if tuning_id:
                        log.debug(f"Tuning {n} ({tuning_id}) matches '{tuning_search_name}'")
                        node = self.px.patch(node, secret_combination[4])
                        filename = VanillaTunings().write_tuning(node, 'patched.xml')
                        Patch.patch_tuning_files.update({s: filename})
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

        log.debug(f"Patch.file_cache_index = {Patch.file_cache_index}")
        log.debug(f"Patch.patch_tuning_files = {Patch.patch_tuning_files}")
        if Patch.patch_tuning_files:
            with open(Patch.file_cache_index, 'wt', encoding='UTF-8') as fp:
                fp.write(f"{Patch.patch_tuning_files}")
            Patch.patch_tuning_files = None

        log.info(f"Patch statistics: ETreeClassCreator || ETreeTuningLoader")
        log.info(f"Patch start: {time.strftime('%y-%m-%d %H:%M:%S', time.localtime(Patch.t_start_class_creator))} || {time.strftime('%y-%m-%d %H:%M:%S', time.localtime(Patch.t_start_tuning_loader))}")
        log.info(f"Patch end:   {time.strftime('%y-%m-%d %H:%M:%S', time.localtime(Patch.t_end_class_creator))} || {time.strftime('%y-%m-%d %H:%M:%S', time.localtime(Patch.t_end_tuning_loader))}")
        log.info(f"Patch duration: {Patch.t_duration_class_creator:0.3f}s (+ TS4 {Patch.t_end_class_creator - Patch.t_start_class_creator - Patch.t_duration_class_creator:0.3f}s) || {Patch.t_duration_tuning_loader:0.3f}s (+ TS4 {Patch.t_end_tuning_loader - Patch.t_start_tuning_loader - Patch.t_duration_tuning_loader:0.3f}s)")

    @staticmethod
    def handle_exception(_self: Union[ETreeTuningLoader, ETreeClassCreator, None], node: Union[Element, Any], caller: str, ex: Exception = None, as_error: bool = True):
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
        if as_error:
            log.error(f"{caller}: source='{source}'; tag='{tag}', n='{n}', s='{s}', i='{i}'; ex='{ex}'", throw=False)
        else:
            log.warn(f"{caller}: source='{source}'; tag='{tag}', n='{n}', s='{s}', i='{i}'; ex='{ex}'")


# class ETreeTuningLoader:
#     def  _load_node(self, node, tunable_class):
@CommonInjectionUtils.inject_safely_into(ModInfo.get_identity(), ETreeTuningLoader, ETreeTuningLoader._load_node.__name__, handle_exceptions=False)
def patch_xml_tuning_loader_load_node(original, self: ETreeTuningLoader, node: Any, tunable_class, *args, **kwargs):
    t = time.time()
    root = Patch().patch(self, node, 'ETreeTuningLoader')
    Patch.t_duration_tuning_loader += time.time() - t
    if Patch.t_start_tuning_loader > 0:
        Patch.t_end_tuning_loader = time.time()
    else:
        Patch.t_start_tuning_loader = t
    try:
        return original(self, root, tunable_class, *args, **kwargs)
    except (ModuleNotFoundError, UnavailablePackSafeResourceError) as e:
        _e = f'{e}'
        if _e not in Patch.logged_errors and _e.startswith('No module named'):
            Patch.logged_errors.add(_e)
            Patch().handle_exception(self, root, 'ETreeTuningLoader', e, as_error=False)
    except Exception as e:
        Patch().handle_exception(self, root, 'ETreeTuningLoader', e)
        log.warn(f"ETreeTuningLoader: Dropping exception!")
        # raise e


# called before ETreeTuningLoader
# class ETreeClassCreator:
#     def _load_node(self, node, tunable_class):
@CommonInjectionUtils.inject_safely_into(ModInfo.get_identity(), ETreeClassCreator, ETreeClassCreator._load_node.__name__, handle_exceptions=False)
def patch_xml_class_creator_load_node(original, self: ETreeClassCreator, node: Element, tunable_class, *args, **kwargs):
    t = time.time()
    root = Patch().nopatch(self, node, 'ETreeClassCreator')
    Patch.t_duration_class_creator += time.time() - t
    if Patch.t_start_class_creator > 0:
        Patch.t_end_class_creator = time.time()
    else:
        Patch.t_start_class_creator = t
    try:
        return original(self, root, tunable_class, *args, **kwargs)
    except (ModuleNotFoundError, UnavailablePackSafeResourceError) as e:
        _e = f'{e}'
        if _e not in Patch.logged_errors and _e.startswith('No module named'):
            Patch.logged_errors.add(_e)
            Patch().handle_exception(self, root, 'ETreeClassCreator', e, as_error=False)
    except Exception as e:
        Patch().handle_exception(self, root, 'ETreeClassCreator', e)
        log.warn(f"ETreeClassCreator: Raising exception!")
        raise e
