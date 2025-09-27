# pylint: disable=C0116, C0114, missing-module-docstring

import json
import colorama

from ssvlogger.matches.controller_commitee import submitted_attestations

MATCHES = {
    "AGGREGATOR_RUNNER": "Aggregator / Attester",
    "PROPOSER_RUNNER": "Proposer",
    "VALIDATOR_REGISTRATION_RUNNER": "Validator registration",
    "VALIDATOR_REGISTRATION": "Validator registration",
    "AGGREGATOR": "Aggregator",
    "ATTESTER": "Attester",
    "PROPOSER": "Proposer",
    "SYNC_COMMITTEE": "Sync committee",
    "CLUSTER": "Cluster",
    "VOLUNTARY_EXIT": "Voluntary exit",
    "COMMITTEE_RUNNER": "Committee",
}


def received_head_event(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    return (
        f"Updated to new chain head {colorama.Fore.LIGHTCYAN_EX}"
        + f"{data['slot']}{colorama.Fore.RESET} at root {colorama.Fore.LIGHTMAGENTA_EX}"
        + f"0x{data['block_root'][0:4]}..{data['block_root'][-4:]}{colorama.Fore.RESET}"
    ), []


def ticker_event(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    return (
        (
            "Checking for "
            + f"{colorama.Fore.GREEN}"
            + (MATCHES.get(data['handler'])
                or data['handler'].replace('_', ' ').lower())
            + f"{colorama.Fore.RESET} duties"
        ),
        [],
    )


def no_duties(_log: list[str]) -> tuple[str, list[str]] | None:
    return "No attester or sync-committee duties to execute", []


def duty_scheduler_started(_log: list[str]) -> tuple[str, list[str]] | None:
    return "Started Duty Scheduler", []


def starting_duty_handler(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    duty = MATCHES.get(data['handler']) or data['handler'].replace('_', ' ').lower()
    return (
        (
            f"Started {colorama.Fore.GREEN}{duty}"
            + f"{colorama.Fore.RESET} duty handler"
        ),
        [],
    )


def starting_duty_processing(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    duty = MATCHES.get(data['handler']) or data['handler'].replace('_', ' ').lower()
    return (
        (
            f"Started processing {colorama.Fore.GREEN}{duty}"
            + f"{colorama.Fore.RESET} duty at slot {colorama.Fore.CYAN}{data['slot']}"
            + f"{colorama.Fore.RESET}"
        ),
        [],
    )


def failed_to_submit_beacon(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    return (
        f"Failed to submit {colorama.Fore.CYAN}{data['handler']}{colorama.Fore.RESET} job.\n"
        + "Error: "
        + data["error"].replace('\\"', '"'),
        [],
    )


def failed_submit_attestations(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    commitee = data["committee_id"][:12] + "..."
    return (
        f"{colorama.Fore.RED}Failed to submit attestation{colorama.Fore.RESET}"
        + f" for slot {colorama.Fore.LIGHTMAGENTA_EX}{data['slot']}"
        + f"{colorama.Fore.RESET} in committee {colorama.Fore.LIGHTMAGENTA_EX}"
        + f"0x{commitee}{colorama.Fore.RESET}"
    ), []


def could_not_find_validator(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    return (
        f"Failed to submit {colorama.Fore.CYAN}{data['handler']}{colorama.Fore.RESET} job "
        + f"for validator {data['pubkey'][:8]} due to non-existant validator"
    ), []


def subscribing_to_head_events(_log: list[str]) -> tuple[str, list[str]] | None:
    return "Subscribing to head events", []


def failed_to_fetch(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    duty = MATCHES.get(data['handler']) or data['handler'].replace('_', ' ').lower()
    return (
        (
            f"Failed to fetch {colorama.Fore.CYAN}{duty}"
            + f"{colorama.Fore.RESET}"
            + f" duties for current epoch: {colorama.Fore.RED}"
            + f"{data['error']}{colorama.Fore.RESET}"
        ),
        [],
    )


DutyScheduler = {
    # SSV log entry: (function, silent)
    "received head event": (received_head_event, True),
    "ticker event": (ticker_event, True),
    "no attester or sync-committee duties to execute": (no_duties, True),
    "duty scheduler started": (duty_scheduler_started, True),
    "starting duty handler": (starting_duty_handler, False),
    "failed to submit beacon committee subscription": (failed_to_submit_beacon, False),
    "could not find validator": (could_not_find_validator, False),
    "subscribing to head events": (subscribing_to_head_events, True),
    "starting duty processing": (starting_duty_processing, False),
    "successfully submitted attestations": (submitted_attestations, False),
    "failed to submit attestation": (failed_submit_attestations, False),
    "failed to fetch duties for current epoch": (failed_to_fetch, False),
}
