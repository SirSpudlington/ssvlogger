# pylint: disable=C0116, C0114, missing-module-docstring

import json
import colorama

from ssvlogger.common import seconds_to_ms_or_s


def submitted_attestations(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    commitee = data["committee_id"][:12] + "..."
    return (
        f"{colorama.Fore.GREEN}Successfully submitted attestations{colorama.Fore.RESET}"
        + f" for slot {colorama.Fore.LIGHTMAGENTA_EX}{data['slot']}"
        + f"{colorama.Fore.RESET} in committee {colorama.Fore.LIGHTMAGENTA_EX}"
        + f"0x{commitee}{colorama.Fore.RESET}"
        + f" in {seconds_to_ms_or_s(data['total_consensus_time'])}"
    ), []


def started_duty(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    commitee = data["committee_id"][:12] + "..."
    return (
        f"Executing duty at slot {colorama.Fore.LIGHTMAGENTA_EX}{data['slot']}"
        + f"{colorama.Fore.RESET} in committee {colorama.Fore.LIGHTMAGENTA_EX}"
        + f"0x{commitee}{colorama.Fore.RESET}"
    ), []


Controller_Committee = {
    # SSV log entry: (function, silent)
    "successfully submitted attestations": (submitted_attestations, False),
    "starting duty processing": (started_duty, True),
}
