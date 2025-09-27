# pylint: disable=C0116, C0114, missing-module-docstring

import json
import colorama


def verified_handshake_nodeinfo(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    if "conn_dir" not in data.keys():
        print(data)
    direction = data["conn_dir"]
    ip = data["remote_addr"]
    ip = (ip[1:]).split("/")
    ip = f"{ip[1]}:{ip[3]}"
    addr = data["peer_id"][:16] + "..."
    return (
        f"Processing {colorama.Fore.LIGHTMAGENTA_EX}"
        + f"{direction}{colorama.Fore.RESET}"
        + f" connection from {colorama.Fore.GREEN}{addr}@{ip}{colorama.Fore.RESET}",
        [],
    )


def starting(_log: list[str]) -> tuple[str, list[str]] | None:
    return "Starting P2P networking", []


def configuring(_log: list[str]) -> tuple[str, list[str]] | None:
    return "Configuring P2P networking", []


def services_configured(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    return (
        f"Configured P2P networking. Node id: {colorama.Fore.LIGHTMAGENTA_EX}"
        + f"{data['selfPeer'][:16]}...{colorama.Fore.RESET}"
    ), []


def discv5(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    return (
        f"Using discv5 for discovery. Using {colorama.Fore.LIGHTMAGENTA_EX}"
        + f"{len(data['bootnodes'])}{colorama.Fore.RESET} bootnodes"
    ), []


def selecting_discovered_peers(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    return (
        f"Selecting {colorama.Fore.LIGHTCYAN_EX}"
        + f"{data['pool_size']}{colorama.Fore.RESET} peers for p2p"
    ), []


def proposed_discovered_peers(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    return (
        f"Proposed {colorama.Fore.LIGHTCYAN_EX}"
        + f"{data['count']}{colorama.Fore.RESET} discovered peers"
    ), []


P2PNetwork = {
    # SSV log entry: (function, silent)
    "verified handshake nodeinfo": (verified_handshake_nodeinfo, True),
    "starting": (starting, False),
    "configuring": (configuring, False),
    "services configured": (services_configured, False),
    "using discv5": (discv5, False),
    "selecting discovered peers": (selecting_discovered_peers, True),
    "proposed discovered peers": (proposed_discovered_peers, True),
}
