#
# LICENSE
# https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2023 https://github.com/Oops19
#


import ast
import os
from typing import Tuple, Dict, Set, List

from patch_xml.modinfo import ModInfo

from ts4lib.libraries.file_utils import FileUtils
from ts4lib.libraries.ts4folders import TS4Folders
from sims4communitylib.utils.common_log_registry import CommonLog


mod_name = ModInfo.get_identity().name
log: CommonLog = CommonLog(ModInfo.get_identity(), ModInfo.get_identity().name, custom_file_path=None)
log.enable()


class UserConfig:
    def __init__(self):
        self.ts4f = TS4Folders(ModInfo.get_identity().base_namespace)
        self.config_folder = os.path.join(self.ts4f.data_folder, 'cfg')
        self.fu = FileUtils(os.path.join(self.config_folder))

    def merge_configuration_files(self) -> Dict:
        rv: Dict = {}
        files = self.fu.find_files(r'^.*\.txt$')
        for file in files:
            try:
                with open(file, mode='rt', encoding='UTF-8') as fp:
                    data = ast.literal_eval(fp.read())
                    rv.update(data)
            except Exception as e:
                log.warn(f"Skipping file '{file}' with error '{e}'.")
        log.debug(f"merge_configuration_files() -> {rv}")
        return rv

    @staticmethod
    def join_configuration(config: Dict) -> Tuple[Set, Set, Set, Set, Set, Set, Set, List]:
        used_tags: Set[str] = set()  # {'I', 'M', ...}
        used_instances: Set[str] = set()  # {'broadcast', 'snippet', ...}
        used_tuning_ids: Set[int] = set()  # {123, 456, ...}
        match_string_equal: Set[str] = set()
        match_string_starts: Set[str] = set()
        match_string_ends: Set[str] = set()
        match_string_contains: Set[str] = set()
        secret_combinations: List[Tuple] = []  # keep the load order
        for author, data in config.items():
            tags = data.get('filter').get('loading_tags', {})
            instances = data.get('filter').get('instance', {})
            tunings = data.get('filter').get('tunings', {})
            tuning_ids = data.get('filter').get('tuning_ids', {})
            actions = data.get('actions', {})

            if tags is None or instances is None or tunings is None or actions is None:
                log.warn(f"None in tags({tags}) or instances({instances}) or tunings({tunings}) or actions({actions})")
                continue

            for tag in tags:
                used_tags.add(tag.replace('*', '').upper())
            for instance in instances:
                used_instances.add(instance.replace('*', '').lower())
            for tuning_id in tuning_ids:
                used_tuning_ids.add(tuning_id)
            for tuning in tunings:
                t = tuning.lower()
                if '*' in t:
                    if t[:1] == '*':
                        if t[-1:] == '*':
                            match_string_contains.add(t.replace('*', ''))
                        else:
                            match_string_ends.add(t.replace('*', ''))
                    else:
                        match_string_starts.add(t.replace('*', ''))
                else:
                    match_string_equal.add(t.replace('*', ''))
            actions_2 = {}
            for k, v in actions.items():
                actions_2.update({f"{author}:{k}": v})
            secret_combinations.append((tags, instances, tunings, tuning_ids, actions_2))

        # clear empty values, if any
        for var in used_tags, used_instances, match_string_equal, match_string_ends, match_string_starts, match_string_contains:
            var.add('')
            var.remove('')

        log.debug(f"used_tags = {used_tags}")
        log.debug(f"used_instances = {used_instances}")
        log.debug(f"used_tuning_ids = {used_tuning_ids}")
        log.debug(f"match_string_equal = {match_string_equal}")
        log.debug(f"match_string_starts = {match_string_starts}")
        log.debug(f"match_string_ends = {match_string_ends}")
        log.debug(f"match_string_contains = {match_string_contains}")
        log.debug(f"secret_combinations = {secret_combinations}")
        return used_tags, used_instances, used_tuning_ids, \
            match_string_equal, match_string_starts, match_string_ends, match_string_contains, \
            secret_combinations
