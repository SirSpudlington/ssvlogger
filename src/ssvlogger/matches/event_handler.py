# pylint: disable=C0116, C0114, missing-module-docstring

import json
import colorama


def malformed_event(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    return (
        f"Malformed Event: {log[3].split(':')[1].strip()}. Transaction hash: {data['tx_hash']}",
        [],
    )


def failed_to_find_event(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    return (
        f"Failed to find event by ID {colorama.Fore.LIGHTCYAN_EX}"
        + f"{data['hash']}{colorama.Fore.RESET}",
        [],
    )


def unknown_event_name(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    return (
        f"Ignoring unknown event {colorama.Fore.RED}{data['name']}{colorama.Fore.RESET}",
        [],
    )


EventHandler = {
    # SSV log entry: (function, silent)
    "malformed event": (malformed_event, False),
    "failed to find event by ID": (failed_to_find_event, False),
    "unknown event name": (unknown_event_name, False),
}
