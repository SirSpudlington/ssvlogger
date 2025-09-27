# pylint: disable=C0116, C0114, missing-module-docstring

import json
import colorama

from ssvlogger.matches.duty_scheduler import MATCHES


def started_duty(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    validator = "0x" + data["pubkey"][:12] + "..."
    duty = data.get("runner_role") or data.get("role") or "unknown"
    duty = MATCHES.get(duty) or duty.replace("_", " ").lower()
    return (
        "Executing "
        + f"{colorama.Fore.LIGHTCYAN_EX}{duty}{colorama.Fore.RESET} duty"
        + " for validator "
        + f"{colorama.Fore.LIGHTMAGENTA_EX}{validator}{colorama.Fore.RESET}"
        + f" at slot {colorama.Fore.LIGHTMAGENTA_EX}{data['slot']}"
        + f"{colorama.Fore.RESET}"
    ), []


def beacon_block_proposal(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    validator = "0x" + data["pubkey"][:12] + "..."
    duty = data.get("runner_role") or data.get("role") or "unknown"
    duty = MATCHES.get(duty) or duty.replace("_", " ").lower()
    return (
        "Received"
        + (" blinded " if data["blinded"] else "")
        + "beacon block proposal for validator "
        + f"{colorama.Fore.LIGHTMAGENTA_EX}{validator}{colorama.Fore.RESET}"
        + f" at slot {colorama.Fore.LIGHTMAGENTA_EX}{data['slot']}"
        + f"{colorama.Fore.RESET} with block hash of "
        + f"{colorama.Fore.CYAN}{data['block_hash']}{colorama.Fore.RESET}"
    ), []


def could_not_submit_block(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    validator = "0x" + data["pubkey"][:12] + "..."
    duty = data.get("runner_role") or data.get("role") or "unknown"
    duty = MATCHES.get(duty) or duty.replace("_", " ").lower()
    return (
        f"{colorama.Fore.RED}Failed to submit{colorama.Fore.RESET}"
        + (" blinded " if data["blinded"] else "")
        + "beacon block proposal for validator "
        + f"{colorama.Fore.LIGHTMAGENTA_EX}{validator}{colorama.Fore.RESET}"
        + f" at slot {colorama.Fore.LIGHTMAGENTA_EX}{data['slot']}"
        + f"{colorama.Fore.RESET} with block hash of "
        + f"{colorama.Fore.CYAN}{data['block_hash']}{colorama.Fore.RESET}"
    ), []


Controller_Validator = {
    # SSV log entry: (function, silent)
    "arting duty process": (started_duty, False),
    "got beacon block proposal": (beacon_block_proposal, False),
    "could not submit": (could_not_submit_block, False),
}
