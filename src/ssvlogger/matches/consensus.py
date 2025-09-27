# pylint: disable=C0116, C0114, missing-module-docstring

import json
import colorama


def slot_cache_updated(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    return (
        f"Updated block root and slot cache to slot {colorama.Fore.LIGHTCYAN_EX}"
        + f"{data['slot']}{colorama.Fore.RESET} at {colorama.Fore.LIGHTMAGENTA_EX}"
        + f"0x{data['block_root'][0:4]}..{data['block_root'][-4:]}{colorama.Fore.RESET}"
    ), []


def event_received(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    return (
        f"Received {colorama.Fore.GREEN}"
        + f"{data['topic']}{colorama.Fore.RESET} event from CL"
    ), []


def event_broadcasted(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    return (
        f"Broadcasted {colorama.Fore.GREEN}"
        + f"{data['topic']}{colorama.Fore.RESET} event to "
        + f"{colorama.Fore.LIGHTCYAN_EX}{data['subscriber_identifier']}{colorama.Fore.RESET}"
    ), []


def submitted_registrations(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    return (
        f"Submitted {colorama.Fore.MAGENTA}{data['count']}{colorama.Fore.RESET}"
        + " validator registrations"
    ), []


def returned_error(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    return (
        "Unable to communicate with consensus client "
        + f"({data.get('address') or data.get('client_addr') or 'default'}): {colorama.Fore.RED}"
        + f"{data['error']}{colorama.Fore.RESET}"
    ), []


def disconnected(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    return (
        f"Consensus client {colorama.Fore.RED}"
        + f"{data['address']}{colorama.Fore.RESET} offline"
    ), []


def out_of_sync(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    return (
        f"Consensus client {colorama.Fore.RED}"
        + f"{data['address']}{colorama.Fore.RESET} out of sync with the main chain"
    ), []


def in_sync(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    return (
        f"Consensus client {colorama.Fore.GREEN}"
        + f"{data['address']}{colorama.Fore.RESET} resynced with the main chain"
    ), []


def connected(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    return (
        f"Connected to {colorama.Fore.LIGHTCYAN_EX}{data['client']}"
        + f"-{data['version']}{colorama.Fore.RESET} consensus client at {colorama.Fore.MAGENTA}"
        + f"{data['address']}{colorama.Fore.RESET}"
    ), []


def noop(_log: list[str]) -> tuple[str, list[str]] | None:
    return None


def subscribing(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    return (
        f"Subscribing to CL events {colorama.Fore.LIGHTCYAN_EX}"
        + f"{data['topics']}{colorama.Fore.RESET}"
    ), []


def adding_event_subscriber(log: list[str]) -> tuple[str, list[str]] | None:
    return log[3] + " to consensus client", []


def optimistic(_log: list[str]) -> tuple[str, list[str]] | None:
    return "Consensus client is in optimistic mode", []


def fork_epochs(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    out = []

    for name, epoch in data.items():
        if name in ["current_data_version", "node_addr", "L", "T", "N", "M"]:
            continue
        out.append(
            f" - {colorama.Fore.LIGHTCYAN_EX}{name}{colorama.Fore.RESET}"
            + f": {colorama.Fore.GREEN}{epoch}{colorama.Fore.RESET}"
        )

    return "Retrieved fork epochs from CL", out


def all_clients_failed_to_submit(_log: list[str]) -> tuple[str, list[str]] | None:
    return (
        f"{colorama.Fore.RED}All CL clients failed to submit block"
        + f"{colorama.Fore.RESET}",
        [],
    )


ConsensusClient = {
    # SSV log entry: (function, silent)
    "block root to slot cache updated": (slot_cache_updated, True),
    "event received": (event_received, True),
    "event broadcasted": (event_broadcasted, True),
    "submitted validator registrations": (submitted_registrations, True),
    "client returned an error": (returned_error, False),
    "consensus client disconnected": (disconnected, False),
    "consensus client desynced": (out_of_sync, False),
    "consensus client synced": (in_sync, False),
    "consensus client connected": (connected, False),
    "could not get extract parameter from beacon node response": (noop, False),
    "beacon config has been initialized": (noop, False),
    "subscribed to head events": (noop, False),
    "retrieved beacon config": (noop, False),
    "subscribing to events": (subscribing, False),
    "' event subscriber": (adding_event_subscriber, False),
    "Consensus client is in optimistic mode": (optimistic, False),
    "retrieved fork epochs": (fork_epochs, False),
    "all clients failed to submit": (all_clients_failed_to_submit, False),
}
