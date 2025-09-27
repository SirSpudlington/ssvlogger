# pylint: disable=C0116, C0114, missing-module-docstring

import json
import colorama


def subscribing(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    return (
        "Subscribing to registry contract events after block "
        + f"{colorama.Fore.LIGHTMAGENTA_EX}{data['from_block']}{colorama.Fore.RESET}"
    ), []


def finished_syncing(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    return (
        f"Processing registry events from block {colorama.Fore.LIGHTMAGENTA_EX}"
        + f"{data['from_block']}{colorama.Fore.RESET} to {colorama.Fore.LIGHTMAGENTA_EX}"
        + f"{data['last_processed_block']}{colorama.Fore.RESET}"
    ), []


EventSyncer = {
    # SSV log entry: (function, silent)
    "subscribing to ongoing registry events": (subscribing, True),
    "finished syncing historical events": (finished_syncing, True),
}
