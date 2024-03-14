#
# LICENSE
# https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2023 https://github.com/Oops19
#
import ast
import os
from typing import Dict, Tuple
from xml.etree import ElementTree

from patch_xml.modinfo import ModInfo
from patch_xml.patch import Patch
from patch_xml.user_config import UserConfig
from patch_xml.vanilla_tunings import VanillaTunings

from sims4communitylib.services.commands.common_console_command import CommonConsoleCommand, CommonConsoleCommandArgument
from sims4communitylib.services.commands.common_console_command_output import CommonConsoleCommandOutput
from ts4lib.libraries.ts4folders import TS4Folders
from sims4communitylib.utils.common_log_registry import CommonLog


mod_name = ModInfo.get_identity().name
log: CommonLog = CommonLog(f"{ModInfo.get_identity().name}", ModInfo.get_identity().name, custom_file_path=None)
log.enable()

# o19.tunings.patch teens_fake_id.txt 129094
# o19.tunings.write 11780257369672543883
# o19.tunings.patch reward_costs.txt 11780257369672543883


@CommonConsoleCommand(
    ModInfo.get_identity(), 'o19.tunings.patch', 'Patch a tuning to test the outcome.',
    command_arguments=(
            CommonConsoleCommandArgument('config_file', 'str', "The name of the configuration file (in patch_xml/cfg/, e.g. 'foo.txt'", is_optional=False),
            CommonConsoleCommandArgument('tuning_id', 'int', "The tuning_id of the tuning to modify. 'filter' is ignored.", is_optional=False),
    )
)
def o19_tunings_patch(output: CommonConsoleCommandOutput, config_file: str, tuning_id: int):
    try:
        output(f"Processing '{config_file}'.")
        ts4f = TS4Folders(ModInfo.get_identity().base_namespace)
        uc = UserConfig()
        patch = Patch()
        vt = VanillaTunings()
        file = os.path.join(ts4f.data_folder, 'cfg', config_file)

        if not os.path.exists(file):
            output(f"File {file} not found.")
            return
        with open(file, 'rt', encoding='UTF-8') as fp:
            user_provided_patches: Dict = ast.literal_eval(fp.read())
            parsed_patches: Tuple = uc.join_configuration(user_provided_patches)
            patch.init(parsed_patches)
            node = vt.get_tuning(f"{tuning_id}")  # str ===????
            root = patch.patch(None, node, 'Console', verbose=True)
            file2 = os.path.join(ts4f.data_folder, f"{tuning_id}.patched.xml")
            with open(file2, 'wt', encoding='UTF-8') as fp2:
                fp2.write(f"{ElementTree.tostring(root, encoding='UTF-8').decode('UTF-8')}")
                output(f"Wrote patch to {file2}")
    except Exception as e:
        log.error(f"Oops: {e}", None, throw=True)
