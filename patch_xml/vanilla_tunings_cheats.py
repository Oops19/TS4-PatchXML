#
# LICENSE
# https://creativecommons.org/licenses/by/4.0/ https://creativecommons.org/licenses/by/4.0/legalcode
# © 2023 https://github.com/Oops19
#


from patch_xml.modinfo import ModInfo
from patch_xml.vanilla_tunings import VanillaTunings

from sims4communitylib.services.commands.common_console_command import CommonConsoleCommand, CommonConsoleCommandArgument
from sims4communitylib.services.commands.common_console_command_output import CommonConsoleCommandOutput
from sims4communitylib.utils.common_log_registry import CommonLog, CommonLogRegistry


log: CommonLog = CommonLogRegistry.get().register_log(ModInfo.get_identity(), ModInfo.get_identity().name)
log.enable()


@CommonConsoleCommand(
    ModInfo.get_identity(), 'o19.tunings.write', 'Write tuning files.',
    command_arguments=(
            CommonConsoleCommandArgument('tuning_id', 'int', "Write a single tuning file. Use '0' to write all tuning files", is_optional=False),
    )
)
def o19_tunings_write_tunings(output: CommonConsoleCommandOutput, tuning_id: int):
    try:
        if tuning_id == 0:
            output(f"Writing all tuning files. This will take a while!")
            VanillaTunings().write_all_tunings()
        else:
            output(f"Writing tuning {tuning_id}.")
            VanillaTunings().get_tuning(f"{tuning_id}")
        output(f"Done")
    except Exception as e:
        log.error(f"Oops: {e}", None, throw=True)


@CommonConsoleCommand(
    ModInfo.get_identity(), 'o19.tunings.comments ', 'Add comments to XML',
    command_arguments=(
            CommonConsoleCommandArgument('enable', 'bool', 'Add comments (True/False).', is_optional=False),
    )
)
def o19_tunings_comments(output: CommonConsoleCommandOutput, enable: bool):
    try:
        output(f"Setting 'comments' to '{enable}'")
        VanillaTunings._xml_comments = enable
        output(f"Use 'o19.tunings.write 0' to write all XML.")
    except Exception as e:
        log.error(f"Oops: {e}", None, throw=True)


@CommonConsoleCommand(
    ModInfo.get_identity(), 'o19.tunings.pretty ', 'Write pretty XML',
    command_arguments=(
            CommonConsoleCommandArgument('enable', 'bool', 'Write pretty (True/False).', is_optional=False),
    )
)
def o19_tunings_pretty(output: CommonConsoleCommandOutput, enable: bool):
    try:
        output(f"Setting 'pretty' to '{enable}'")
        VanillaTunings._pretty_xml = enable
        output(f"Use 'o19.tunings.write 0' to write all XML.")
    except Exception as e:
        log.error(f"Oops: {e}", None, throw=True)
