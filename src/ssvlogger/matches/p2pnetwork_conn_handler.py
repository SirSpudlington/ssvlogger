# pylint: disable=C0116, C0114, missing-module-docstring

import json
import colorama


def verified_handshake_nodeinfo(log: list[str]) -> tuple[str, list[str]] | None:
    data = json.loads(log[4])
    return (
        f"Completed {colorama.Fore.LIGHTCYAN_EX}{data['conn_dir']}"
        + f"{colorama.Fore.RESET} handshake with {colorama.Fore.LIGHTMAGENTA_EX}"
        + f"{data['remote_addr']}{colorama.Fore.RESET}"
    ), []


P2PNetwork_ConnHandler = {
    # SSV log entry: (function, silent)
    "Verified handshake nodeinfo": (verified_handshake_nodeinfo, True)
}
