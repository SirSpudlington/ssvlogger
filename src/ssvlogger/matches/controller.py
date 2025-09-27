# pylint: disable=C0116, C0114, missing-module-docstring

import json
import colorama


def validator_status_recording(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    return (
        f"{colorama.Fore.LIGHTCYAN_EX}{data['count']}{colorama.Fore.RESET} validators "
        + f"{colorama.Fore.LIGHTMAGENTA_EX}{data['status']}{colorama.Fore.RESET}"
    ), []


def initializing_validators(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    return (
        f"Configuring {colorama.Fore.YELLOW}{data['shares count']}"
        + f"{colorama.Fore.RESET} validators"
    ), []


def skipping_validator(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    return (
        f"Skipping setup for validator {colorama.Fore.RED}0x{data['pubkey'][:8]}"
        + f"{colorama.Fore.RESET} until it becomes active on beacon chain"
    ), []


def init_validators(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    additional_logs = []

    additional_logs.append(
        f"Unable to initialize {colorama.Fore.RED}"
        + f"{data['missing_metadata']}{colorama.Fore.RESET} validator"
        + f"{'s' if data['missing_metadata'] != 1 else ''}"
        + " due to missing metadata or non-active status on beacon chain"
    )

    additional_logs.append(
        f"Failed to initialize {colorama.Fore.RED}{data['failures']}"
        + f"{colorama.Fore.RESET} validator{'s' if data['failures'] != 1 else ''}"
    )

    additional_logs.append(
        f"Initialized {colorama.Fore.GREEN}{data['initialized']}"
        + f"{colorama.Fore.RESET} validator{'s' if data['initialized'] != 1 else ''}"
    )

    return (
        f"Completed initialization for {colorama.Fore.MAGENTA}{data['shares']}"
        + f"{colorama.Fore.RESET} validators"
    ), additional_logs


def noop(_log):
    return None


Controller = {
    # SSV log entry: (function, silent)
    "recording validator status": (validator_status_recording, True),
    "initializing validators": (initializing_validators, False),
    "starting validators setup": (initializing_validators, False),
    "skipping validator until it becomes active": (skipping_validator, False),
    "validator initialization is done": (init_validators, False),
    "init validators done": (init_validators, False),
    "start validators done": (noop, False),
    "setup validators done": (noop, False),
}
