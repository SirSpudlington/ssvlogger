#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0116, C0114, R0912, R0915, W0718, R1732, R0916, R0914

"""A simple python string to parse SSV node logs and make them legible"""

import sys
import json
import argparse
from typing import Any, Callable
import colorama

from ssvlogger import matches


def extract_time_and_stat(log, docker_mode):
    """Extracts time and status from a log"""
    time = log[0].split(": ", maxsplit=1)[1] if not docker_mode else log[0]
    time = time.replace("T", " ").split(".", maxsplit=1)[0]
    time = colorama.Fore.CYAN + time + colorama.Fore.RESET

    stat = log[1]

    if stat == "DEBUG":
        stat = colorama.Fore.BLUE + stat + colorama.Fore.RESET
    elif stat == "INFO":
        stat = colorama.Fore.GREEN + stat + colorama.Fore.RESET
    elif stat == "WARN":
        stat = colorama.Fore.YELLOW + stat + colorama.Fore.RESET
    elif stat == "ERROR":
        stat = colorama.Fore.LIGHTRED_EX + stat + colorama.Fore.RESET
    elif stat == "FATAL":
        stat = colorama.Fore.RED + stat + colorama.Fore.RESET

    return time, stat


def parse_args() -> Any:
    parser = argparse.ArgumentParser(
        prog="ssvlogger",
        description="A simple script to parse operational SSV operator logs.",
    )

    parser.add_argument(
        "log_file",
        type=str,
        nargs="?",
        help="An optional log file to get logs from",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        default=False,
        help="Whether to print non-formatted debug logs",
        action="store_true",
    )

    parser.add_argument(
        "-j",
        "--journal",
        default=False,
        help="Enforce compatibility with `journalctl -f | "
        + "ssvlogger -j`, do not use this if using docker or `journalctl -f --output cat`",
        action="store_true",
    )

    parser.add_argument(
        "-t",
        "--traceback",
        default=False,
        help="Allow dumping full tracelogs to the console",
        action="store_true",
    )

    parser.add_argument(
        "-s",
        "--silent",
        default=False,
        help="Ignore running logs such as peer counts",
        action="store_true",
    )

    args = parser.parse_args()

    return args


def cleanup_log(line: str) -> list[str] | None:
    log = line.strip().replace("        ", "\t").split("\t")

    if "systemd[1]" in line:  # Ignore systemd messages
        return None

    if len(log) < 2:  # Ignore any non standard messages
        return None

    return log


def process_log(line: str, args: Any):
    log = cleanup_log(line)
    if log is None:
        return

    # Time and information recovery
    time, stat = extract_time_and_stat(log, not args.journal)

    if "DEBUG" in stat and args.verbose:
        tolog = tolog = "        ".join(log[2:])
        print(f"{time} {stat}: {tolog[2:]}")
    elif "DEBUG" in stat:
        return

    additional_logs = []
    tolog = ""

    try:
        x = switch_log(log, stat, args)
        if x is None:
            return
        (tolog, additional_logs) = x
    except json.decoder.JSONDecodeError:
        tolog = "        ".join(log[2:])
    except IndexError:
        tolog = "        ".join(log[2:])
    except KeyError:
        tolog = "        ".join(log[2:])

    # Print log to stdout
    print(f"{time} {stat}: {tolog}")

    # Print and reset additional logs
    for i in additional_logs:
        print(f"{time} {stat}: {i}")


def switch_log(log: list[str], stat: Any, args: Any) -> tuple[str, list[str]] | None:
    # P2P network
    additional_logs = []
    tolog = ""

    if log[2].replace(".", "_") in dir(matches):

        module: dict[
            str, tuple[Callable[[list[str]]], tuple[str, list[str]] | None]
        ] = getattr(matches, log[2].replace(".", "_"))

        for k, (f, silent) in module.items():
            if k in log[3]:
                log = f(log)
                if (args.silent and silent) or (log is None):
                    return None
                tolog, additional_logs = log
                break

        if tolog == "":
            tolog = "        ".join(log[2:])

    # Edge case logs that don't belong to a specific module

    elif log[2] == "Observability" and log[3] == "global logger initialized":
        tolog = "SSV logger initialized"
    elif (
        log[2] == "Observability"
        or log[2] == "MetricsHandler"
        or log[2] == "Migrations"
        or log[2] == "starting event listener"
        or log[2] == "getting operator private key from keystore"
        or log[2] == "using badger db"
    ):
        return None

    elif len(log) == 4 and len(json.loads(log[3]).keys()) == 3:
        tolog = log[2]

    elif log[2] == "found network config by name":
        data = json.loads(log[3])
        tolog = (
            f"Loading {colorama.Fore.LIGHTMAGENTA_EX}"
            + f"{data['name']}{colorama.Fore.RESET} network config"
        )

    elif log[2] == "setting ssv network":
        data = json.loads(log[3])
        if (config := data.get("config")) is not None:
            name = json.loads(config)["name"]
        else:
            name = data.get("network") or "unknown"
        tolog = (
            f"Configuring SSV node for running on {colorama.Fore.MAGENTA}"
            + f"{name}{colorama.Fore.RESET}"
        )

    elif log[2] == "consensus client: connecting":
        data = json.loads(log[3])
        tolog = (
            f"Connecting to consensus clients {colorama.Fore.MAGENTA}"
            + f"{data['address']}{colorama.Fore.RESET}"
        )

    elif log[2] == "consensus client: connecting (multi client)":
        data = json.loads(log[3])
        tolog = "Connecting to the following consensus clients:"
        additional_logs = []
        for address in data["addresses"]:
            additional_logs.append(
                f" - {colorama.Fore.MAGENTA}" + f"{address}{colorama.Fore.RESET}"
            )

    elif log[2] == "applying migrations" or log[3] == "applying migrations":
        data = json.loads(log[4] or log[3])
        tolog = (
            f"Applying {colorama.Fore.LIGHTBLUE_EX}{data['count']}"
            + f"{colorama.Fore.RESET} migrations"
        )

    elif (
        log[2] == "applied migrations successfully"
        or log[3] == "applied migrations successfully"
    ):
        tolog = "Applied migrations sucessfully"

    elif log[2] == "successfully loaded operator keys":
        data = json.loads(log[3])
        tolog = (
            f"Loaded operator key ({colorama.Fore.MAGENTA}{data['pubkey'][16:]}"
            + f"{colorama.Fore.RESET})"
        )

    elif log[2] == "historical registry sync stats":
        data = json.loads(log[3])
        tolog = "Network statistics: "
        additional_logs.append(f"Operator ID           : {data['my_operator_id']}")
        additional_logs.append(f"Operators on network  : {data['operators']}")
        additional_logs.append(f"Validators on network : {data['validators']}")
        additional_logs.append(
            f"Liquidated Validators : {data['liquidated_validators']}"
        )
        additional_logs.append(f"Validators managed    : {data['my_validators']}")

    elif log[2] == "increasing MaxPeers to match the operator's subscribed subnets":
        data = json.loads(log[3])
        tolog = (
            f"Increasing max peers from {colorama.Fore.LIGHTCYAN_EX}{data['old_max_peers']}"
            + f"{colorama.Fore.RESET} to {colorama.Fore.LIGHTCYAN_EX}"
            + f"{data['new_max_peers']}{colorama.Fore.RESET}"
        )

    elif "OPERATOR SUCCESSFULLY CONFIGURED" in log[3]:
        tolog = "Operator configured sucessfully"

        additional_logs.append(
            f"{colorama.Fore.GREEN}"
            + f"╔═╗╔╦╗╔═╗╦═╗╔╦╗╦ ╦╔═╗  ╔═╗╦ ╦╔═╗╔═╗╔═╗╔═╗╔═╗{colorama.Fore.RESET}"
        )
        additional_logs.append(
            f"{colorama.Fore.GREEN}"
            + f"╚═╗ ║ ╠═╣╠╦╝ ║ ║ ║╠═╝  ╚═╗║ ║║  ║  ║╣ ╚═╗╚═╗{colorama.Fore.RESET}"
        )
        additional_logs.append(
            f"{colorama.Fore.GREEN}"
            + f"╚═╝ ╩ ╩ ╩╩╚═ ╩ ╚═╝╩    ╚═╝╚═╝╚═╝╚═╝╚═╝╚═╝╚═╝{colorama.Fore.RESET}"
        )

    # Specific Error Handling

    elif "node is not healthy" in log[2]:
        data = json.loads(log[3])
        node = data["node"]
        error = data["error"].replace('\\"', '"')
        tolog = f"Issue with {node} {colorama.Fore.RED}{error}"
        if args.traceback:
            verbose = (
                data["errorVerbose"]
                .replace('\\"', '"')
                .replace("\\n", "\n")
                .replace("\\r", "\r")
                .replace("\\t", "\t")
            )
            tolog += f"\nFull Traceback:\n{verbose}"
        tolog += colorama.Fore.RESET

    elif "not all nodes are healthy" in log[2]:
        tolog = "not all nodes are healthy"
    elif (
        "ethereum node(s) are either out of sync or down. Ensure the nodes are healthy to resume."
        in log[2]
    ):
        tolog = (
            "ethereum node(s) are either out "
            + "of sync or down. Ensure the nodes are healthy to resume."
        )

    # Generic Error handling and fallback
    else:
        if "ERROR" in stat or "FATAL" in stat:
            try:
                data = json.loads(log[3])
                tolog = f"{log[2]} - {data['error']}"
                if args.traceback and "errorVerbose" in data.keys():
                    verbose = (
                        data["errorVerbose"]
                        .replace('\\"', '"')
                        .replace("\\n", "\n")
                        .replace("\\r", "\r")
                        .replace("\\t", "\t")
                    )
                    tolog += f"\nFull Traceback:\n{verbose}"
            except IndexError:
                tolog = f"{log[2]}"
            except json.decoder.JSONDecodeError:
                tolog = f"{log[2]} - {log[3]}"
        else:
            tolog = "        ".join(log[2:])

    return tolog, additional_logs  # type: ignore


def main():
    """Error handling function and soft exit"""

    try:
        main_function()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    except Exception as error:
        print(f"{colorama.Fore.RED}SSVLogger Error: {error}{colorama.Fore.RESET}")
        sys.exit(1)


def main_function():
    """Main function"""

    colorama.init()
    args = parse_args()

    if args.log_file is not None:
        inp = open(args.log_file, "r", encoding="utf-8")
        while (line := inp.readline()) != "":
            line = json.loads(line)
            if "N" in line.keys():
                line = "        ".join(
                    [line["T"], line["L"], line["N"], line["M"], json.dumps(line)]
                )
            else:
                line = "        ".join(
                    [line["T"], line["L"], line["M"], json.dumps(line)]
                )

            process_log(line, args)

    else:
        for line in sys.stdin:
            process_log(line, args)


if __name__ == "__main__":
    main()
