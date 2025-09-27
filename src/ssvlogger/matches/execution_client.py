# pylint: disable=C0116, C0114, missing-module-docstring

import json
import colorama


def received_head_event(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    return (
        f"Processed {colorama.Fore.LIGHTMAGENTA_EX}{data['events']}"
        + f" {colorama.Fore.RESET}registry events ({data['progress']} complete)"
    ), []


def connecting(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    return (
        f"Connecting to execution client at {colorama.Fore.LIGHTMAGENTA_EX}"
        + f"{data['address']}{colorama.Fore.RESET}"
    ), []


def failed_to_stream(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    return (
        "Cannot get events from execution client "
        + f"{'at ' if data.get('address') is not None else ''}{colorama.Fore.LIGHTMAGENTA_EX}"
        + f"{data.get('address') or ''}{colorama.Fore.RESET}: {data['error']}"
    ), []


def connected(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    return (
        f"Connected to execution client at {colorama.Fore.LIGHTMAGENTA_EX}"
        + f"{data['address']}{colorama.Fore.RESET} in {data['took']}"
    ), []


def reconnecting(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    return (
        f"Reconnecting to execution client at {colorama.Fore.LIGHTMAGENTA_EX}"
        + f"{data['address']}{colorama.Fore.RESET}"
    ), []


def could_not_reconnect(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    return (
        f"Reconnecting to execution client at {colorama.Fore.LIGHTMAGENTA_EX}"
        + f"{data['address']}{colorama.Fore.RESET} ({data['error']})"
    ), []


def returned_error(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    return (
        f"Unable to communicate with execution client: {colorama.Fore.RED}"
        + f"{data['error']}{colorama.Fore.RESET}"
    ), []


ExecutionClient = {
    # SSV log entry: (function, silent)
    "fetched registry events": (received_head_event, True),
    "execution client: connecting": (connecting, False),
    "connected to execution client": (connected, False),
    "failed to stream registry events, reconnecting": (failed_to_stream, False),
    "reconnecting": (reconnecting, False),
    "could not reconnect, still trying": (could_not_reconnect, False),
    "Execution client returned an error": (returned_error, False),
}
