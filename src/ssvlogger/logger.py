#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""A simple python string to parse SSV node logs and make them legible"""

# pylint: disable=C0103, C0301, W0718, R1702
# pylint: disable=too-many-locals,too-many-branches,too-many-statements


import sys
import json
import colorama

def extract_time_and_stat(log, DOCKER_MODE):
    """Extracts time and status from a log"""
    time = log[0].split(': ', maxsplit=1)[1] if not DOCKER_MODE else log[0]
    time = time.replace('T', ' ').split('.', maxsplit=1)[0]
    time = colorama.Fore.CYAN + time + colorama.Fore.RESET

    stat = log[1]

    if stat == "DEBUG":
        stat = colorama.Fore.BLUE + stat + colorama.Fore.RESET
    elif stat == "WARN":
        stat = colorama.Fore.YELLOW + stat + colorama.Fore.RESET
    elif stat == "ERROR":
        stat = colorama.Fore.LIGHTRED_EX + stat + colorama.Fore.RESET
    elif stat == "FATAL":
        stat = colorama.Fore.RED + stat + colorama.Fore.RESET

    return time, stat

def seconds_to_ms_or_s(from_log: str):
    """Converts seconds to milliseconds or seconds"""

    try:
        if float(from_log) < 1.5:
            return f"{float(from_log)*1000:.2f} ms"
        return f"{float(from_log):.2f} s"
    except ValueError:
        return f"{from_log}s"

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

MATCHES = {
    "AGGREGATOR_RUNNER": "Aggregator / Attester",
    "VALIDATOR_REGISTRATION_RUNNER": "Validator registration",
    "VALIDATOR_REGISTRATION": "Validator registration",
    "AGGREGATOR": "Aggregator",
    "ATTESTER": "Attester",
    "PROPOSER": "Proposer",
    "SYNC_COMMITTEE": "Sync committee",
    "CLUSTER": "Cluster",
    "VOLUNTARY_EXIT": "Voluntary exit",
    "COMMITTEE_RUNNER": "Committee"
}

def main_function():
    """Main function"""

    colorama.init()
    NOSPAM = False
    FULLERRORS = False
    DOCKER_MODE = True

    if "--no-spam" in sys.argv or "-n" in sys.argv:
        NOSPAM = True

    if "--traceback" in sys.argv or "-t" in sys.argv:
        FULLERRORS = True

    if "--journal" in sys.argv or "-j" in sys.argv:
        DOCKER_MODE = False

    additional_logs = []

    for line in sys.stdin:
        log = line.strip().replace("        ", "\t").split("\t")

        if "systemd[1]" in line: # Ignore systemd messages
            continue

        if len(log) < 2:         # Ignore any non standard messages
            continue

        # Time and information recovery

        time, stat = extract_time_and_stat(log, DOCKER_MODE)

        if "DEBUG" in stat and NOSPAM:
            continue

        try:
            # P2P network

            if (log[2] == "P2PNetwork.ConnHandler") and log[3] == "Verified handshake nodeinfo":
                if NOSPAM:
                    continue
                data = json.loads(log[4])
                if "conn_dir" not in data.keys():
                    print(data)
                direction = data["conn_dir"]
                ip = data["remote_addr"]
                ip = (ip[1:]).split("/")
                ip = f"{ip[1]}:{ip[3]}"
                addr = data["peer_id"][:16] + "..."
                tolog = f"Processing {colorama.Fore.LIGHTMAGENTA_EX}" + \
                    f"{direction}{colorama.Fore.RESET}" + \
                    f" connection from {colorama.Fore.GREEN}{addr}@{ip}{colorama.Fore.RESET}"

            elif (log[2] == "P2PNetwork") and log[3] == "Verified handshake nodeinfo":
                continue

            elif (log[2] == "P2PNetwork") and (log[3] == "starting" or log[3] == "starting p2p"):
                tolog = "Starting P2P networking"

            elif (log[2] == "P2PNetwork") and log[3] == "configuring":
                tolog = "Configuring P2P networking"

            elif (log[2] == "P2PNetwork") and log[3] == "services configured":
                data = json.loads(log[4])
                tolog = f"Configured P2P networking. Node id: {colorama.Fore.LIGHTMAGENTA_EX}" + \
                    f"{data['selfPeer'][:16]}...{colorama.Fore.RESET}"

            elif (log[2] == "P2PNetwork") and log[3] == "discovery: using discv5":
                data = json.loads(log[4])
                tolog = f"Using discv5 for discovery. Using {colorama.Fore.LIGHTMAGENTA_EX}" + \
                    f"{len(data['bootnodes'])}{colorama.Fore.RESET} bootnodes."

            elif (log[2] == "P2PNetwork" and log[3] == "proposed discovered peers"):
                if NOSPAM:
                    continue
                data = json.loads(log[4])
                tolog = f"Discovered {colorama.Fore.LIGHTMAGENTA_EX}" + \
                    f"{data['count']}{colorama.Fore.RESET} new nodes."

            # Execution Client

            elif log[2] == "execution_client" and log[3] == "fetched registry events":
                if NOSPAM:
                    continue
                data = json.loads(log[4])
                tolog = f"Processed {colorama.Fore.LIGHTMAGENTA_EX}{data['events']}" + \
                    f" {colorama.Fore.RESET}registry events ({data['progress']} complete)"

            elif log[2] == "execution_client" and log[3] == "connected to execution client":
                data = json.loads(log[4])
                tolog = f"Connected to execution client at {colorama.Fore.LIGHTMAGENTA_EX}" + \
                    f"{data['address']}{colorama.Fore.RESET} in {data['took']}"

            elif log[2] == "execution_client" and log[3] == "reconnecting":
                data = json.loads(log[4])
                tolog = f"Reconnecting to execution client at {colorama.Fore.LIGHTMAGENTA_EX}" + \
                    f"{data['address']}{colorama.Fore.RESET}"

            elif log[2] == "execution_client" and log[3] == "could not reconnect, still trying":
                data = json.loads(log[4])
                tolog = f"Reconnecting to execution client at {colorama.Fore.LIGHTMAGENTA_EX}" + \
                    f"{data['address']}{colorama.Fore.RESET} ({data['error']})"

            # EventSyncer

            elif log[2] == "EventSyncer" and log[3] == "subscribing to ongoing registry events":
                data = json.loads(log[4])
                tolog = "Subscribing to registry contract events after block " + \
                    f"{colorama.Fore.LIGHTMAGENTA_EX}{data['from_block']}{colorama.Fore.RESET}"

            elif log[2] == "EventSyncer" and log[3] == "finished syncing historical events":
                data = json.loads(log[4])
                tolog = f"Processing registry events from block {colorama.Fore.LIGHTMAGENTA_EX}" + \
                    f"{data['from_block']}{colorama.Fore.RESET} to {colorama.Fore.LIGHTMAGENTA_EX}" + \
                    f"{data['last_processed_block']}{colorama.Fore.RESET}"

            # DutyScheduler

            elif log[2] == "DutyScheduler" and log[3] == "duty scheduler started":
                tolog = "Started Duty Scheduler"

            elif log[2] == "DutyScheduler" and log[3] == "starting duty handler":
                data = json.loads(log[4])
                tolog = f"Started {colorama.Fore.GREEN}{data['handler'].replace('_', ' ').lower()}" + \
                    f"{colorama.Fore.RESET} duty scheduler"

            elif log[2] == "DutyScheduler" and log[3] == "failed to submit beacon committee subscription":
                data = json.loads(log[4])
                tolog = f"Failed to submit {colorama.Fore.CYAN}{data['handler']}{colorama.Fore.RESET} job.\n"
                tolog += "Error: " + data['error'].replace('\\"', '"')

            elif log[2] == "DutyScheduler" and log[3] == "could not find validator":
                data = json.loads(log[4])
                tolog = f"Failed to submit {colorama.Fore.CYAN}{data['handler']}{colorama.Fore.RESET} job " + \
                    f"for validator {data['pubkey'][:8]} due to non-existant validator."

            elif log[2] == "DutyScheduler" and log[3].startswith("malformed event"):
                data = json.loads(log[4])
                tolog = f"Malformed Event: {log[3].split(':')[1].strip()}. Transaction hash: {data['tx_hash']}"

            elif log[2] == "DutyScheduler" and "indices change received" in log[3]:
                data = json.loads(log[4])
                if NOSPAM:
                    continue
                tolog = f"Received indices change {data['handler']}"

            elif (log[2] == "DutyScheduler" or log[2] == "Operator.DutyScheduler") and "✅ successfully submitted attestations" in log[3]:
                data = json.loads(log[4])
                commitee = data['committee_id'][:12] + "..."
                tolog = f"{colorama.Fore.GREEN}Successfully submitted attestations{colorama.Fore.RESET} for slot {colorama.Fore.LIGHTMAGENTA_EX}{data['slot']}" + \
                    f"{colorama.Fore.RESET} for committee {colorama.Fore.LIGHTMAGENTA_EX}{commitee}{colorama.Fore.RESET}" + \
                    f" in {seconds_to_ms_or_s(data['consensus_time'])}"

            elif log[2] == "DutyScheduler" and "starting duty processing" in log[3]:
                data = json.loads(log[4])
                commitee = data['committee_id'][:12] + "..."
                tolog = f"Running duty for slot {colorama.Fore.LIGHTMAGENTA_EX}{data['slot']}" + \
                    f"{colorama.Fore.RESET} for committee {colorama.Fore.LIGHTMAGENTA_EX}{commitee}{colorama.Fore.RESET}"

            elif log[2] == "DutyScheduler" and "❗no committee runner found for slot" in log[3]:
                data = json.loads(log[4])
                tolog = f"No committee runner found for slot {colorama.Fore.LIGHTMAGENTA_EX}{data['slot']}" + \
                    f"{colorama.Fore.RESET} for committee {colorama.Fore.LIGHTMAGENTA_EX}{data['committee_id'][:12]}..."

            elif log[2] == "Operator.DutyScheduler" and "received head event." in log[3]:
                data = json.loads(log[4])
                tolog = f"Processesing new block {colorama.Fore.LIGHTMAGENTA_EX}{data['slot']}{colorama.Fore.RESET}"

            # consensus_client

            elif log[2] == "consensus_client" and "block root to slot cache updated" in log[3]:
                if NOSPAM:
                    continue
                data = json.loads(log[4])
                tolog = f"Updated slot cache to block root {colorama.Fore.LIGHTMAGENTA_EX}{data['block_root']}{colorama.Fore.RESET}"

            elif log[2] == "consensus_client" and "event broadcasted" in log[3]:
                if NOSPAM:
                    continue
                data = json.loads(log[4])
                tolog = f"Sent new event to conensus client topic: {colorama.Fore.LIGHTMAGENTA_EX}{data['topic']}{colorama.Fore.RESET} identifier: {colorama.Fore.LIGHTMAGENTA_EX}{data['subscriber_identifier']}{colorama.Fore.RESET}"

            elif log[2] == "consensus_client" and "consensus client synced" in log[3]:
                data = json.loads(log[4])
                tolog = f"Consensus client synced at {colorama.Fore.LIGHTMAGENTA_EX}{data['address']}{colorama.Fore.RESET}"

            elif log[2] == "consensus_client" and "consensus client connected" in log[3]:
                data = json.loads(log[4])
                tolog = f"Consensus client connected at {colorama.Fore.LIGHTMAGENTA_EX}{data['address']} ({data['version']}){colorama.Fore.RESET}"

            elif log[2] == "consensus_client" and "retrieved fork epochs" in log[3]:
                data = json.loads(log[4])
                tolog = "Retrieved fork epochs from consensus client. "
                for key, value in data.items():
                    if key in ["node_addr", "current_data_version"]:
                        continue
                    tolog += f"{key}: {colorama.Fore.CYAN}{value}{colorama.Fore.RESET} "

            elif log[2] == "consensus_client" and "submitted batched validator registrations" in log[3]:
                data = json.loads(log[4])
                tolog = f"Submitted {colorama.Fore.LIGHTMAGENTA_EX}{data['count']}{colorama.Fore.RESET} validator registrations at slot {colorama.Fore.CYAN}{data['slot']}{colorama.Fore.RESET}"

            elif log[2] == "consensus_client" and "going to submit batch validator registrations" in log[3]:
                data = json.loads(log[4])
                tolog = f"Going to submit {colorama.Fore.LIGHTMAGENTA_EX}{data['count']}{colorama.Fore.RESET} validator registrations at slot {colorama.Fore.CYAN}{data['slot']}{colorama.Fore.RESET}"


            # Controller

            elif log[2] == "Controller.Validator" and "starting duty processing" in log[3]:
                data = json.loads(log[4])
                role = data["beacon_role"] if "beacon_role" in data else data["role"]
                role = MATCHES[role] if role in MATCHES else role
                slot = data["slot"]
                validator = data["pubkey"][:6] + "..."
                tolog = f"Processing {colorama.Fore.LIGHTMAGENTA_EX}{role}{colorama.Fore.RESET}" + \
                    f" duty at slot {colorama.Fore.LIGHTMAGENTA_EX}{slot}{colorama.Fore.RESET}" + \
                    f" for validator {colorama.Fore.LIGHTMAGENTA_EX}{validator}{colorama.Fore.RESET}"

            elif log[2] == "Controller.Validator" and "successfully submitted attestation" in log[3]:
                data = json.loads(log[4])
                role = data["beacon_role"] if "beacon_role" in data else data["role"]
                slot = data["slot"]
                validator = data["pubkey"][:6] + "..."
                tolog = "Sucessfully submitted attestation at slot " + \
                    f"{colorama.Fore.LIGHTMAGENTA_EX}{slot}{colorama.Fore.RESET}" + \
                    f" for validator {colorama.Fore.LIGHTMAGENTA_EX}{validator}{colorama.Fore.RESET}"

            elif log[2] == "Controller.Validator" and "successfully submitted sync committee" in log[3]:
                data = json.loads(log[4])
                validator = data["pubkey"][:6] + "..."
                tolog = "Sucessfully submitted sync committee message for validator " + \
                    f"{colorama.Fore.LIGHTMAGENTA_EX}{validator}{colorama.Fore.RESET}"

            elif log[2] == "Controller.Validator" and "got beacon block proposal" in log[3]:
                data = json.loads(log[4])
                role = data["beacon_role"] if "beacon_role" in data else data["role"]
                slot = data["slot"]
                validator = data["pubkey"][:6] + "..."
                tolog = f"Processing {colorama.Fore.LIGHTMAGENTA_EX}{role}{colorama.Fore.RESET}" + \
                    f" duty at slot {colorama.Fore.LIGHTMAGENTA_EX}{slot}{colorama.Fore.RESET}" + \
                    f" for validator {colorama.Fore.LIGHTMAGENTA_EX}{validator}{colorama.Fore.RESET}"

            elif log[2] == "Controller.TaskExecutor" and "removed validator" in log[3]:
                data = json.loads(log[4])
                tolog = f"Removing validator {colorama.Fore.RED}{data['pubkey'][:8]}{colorama.Fore.RESET}"

            elif log[2] == "Controller" and log[3] == "starting validators setup...":
                data = json.loads(log[4])
                tolog = f"Configuring {colorama.Fore.YELLOW}{data['shares count']}" + \
                    f"{colorama.Fore.RESET} validators."

            elif log[2] == "Controller" and log[3] == "skipping validator until it becomes active":
                data = json.loads(log[4])
                tolog = f"Skipping setup for validator {colorama.Fore.RED}{data['pubkey'][:8]}" + \
                    f"{colorama.Fore.RESET} until it becomes active on beacon chain."

            elif log[2] == "Controller" and log[3] == "recording validator status":
                data = json.loads(log[4])
                tolog = f"Validators currently {colorama.Fore.CYAN}{data['status']}{colorama.Fore.RESET}: {colorama.Fore.LIGHTMAGENTA_EX}{data['count']}{colorama.Fore.RESET}"

            elif log[2] == "Controller" and log[3] == "setup validators done":
                data = json.loads(log[4])
                tolog = f"Completed configuration for {colorama.Fore.MAGENTA}{data['shares']}" + \
                    f"{colorama.Fore.RESET} validators."

                additional_logs.append(f"Successfully configured and started {colorama.Fore.GREEN}" + \
                    f"{data['started']}{colorama.Fore.RESET} validators")

                additional_logs.append(f"Failed to configure {colorama.Fore.RED}{data['failures']}" + \
                    f"{colorama.Fore.RESET} validator{'s' if data['failures'] != 1 else ''}")

            elif log[2] == "Controller" and log[3] == "init validators done":
                data = json.loads(log[4])
                tolog = f"Completed initialization for {colorama.Fore.MAGENTA}{data['shares']}" + \
                    f"{colorama.Fore.RESET} validators."

                additional_logs.append(f"Unable to initialize {colorama.Fore.RED}" + \
                    f"{data['missing_metadata']}{colorama.Fore.RESET} validator" + \
                    f"{'s' if data['missing_metadata'] != 1 else ''}" + \
                    " due to missing metadata or non-active status on beacon chain.")

                additional_logs.append(f"Failed to initialize {colorama.Fore.RED}{data['failures']}" + \
                    f"{colorama.Fore.RESET} validator{'s' if data['failures'] != 1 else ''}")

            elif log[2] == "Controller" and log[3] == "failed to update validators metadata":
                data = json.loads(log[4])
                tolog = "Failed to update validator metadata"

            elif log[2] == "Controller" and "dropping message because the queue is full" in log[3]:
                data = json.loads(log[4])
                tolog = f"Dropping {data['msg_type']} message because the queue is full."

            elif log[2] == "Controller" and "starting new validator" in log[3]:
                data = json.loads(log[4])
                tolog = f"Starting new validator {colorama.Fore.MAGENTA}0x{data['pubkey'][:8]}{colorama.Fore.RESET}"

            # EventHandler

            elif log[2] == "EventHandler" and log[3] == "unknown event name":
                data = json.loads(log[4])
                tolog = f"Ignoring unknown event {colorama.Fore.RED}{data['name']}{colorama.Fore.RESET}"

            elif log[2] == "EventHandler" and "malformed event: " in log[3]:
                data = json.loads(log[4])
                tolog = f"Malformed Event: {log[3].split(':')[1].strip()}. Transaction hash: {data['tx_hash']}"

            elif log[2] == "EventHandler" and "could not parse event" in log[3]:
                data = json.loads(log[4])
                tolog = f"Failed to parse event {data['event']}"

            # Operator

            elif log[2] == "Operator.DutyScheduler" and log[3] == "ℹ️ starting duty processing":
                data = json.loads(log[4])
                tolog = f"Running {MATCHES[data['role']]} duty for slot {colorama.Fore.LIGHTMAGENTA_EX}{data['slot']}" + \
                    f"{colorama.Fore.RESET} in committee {colorama.Fore.LIGHTMAGENTA_EX}{data['committee_id'][:12]}..."

            elif log[2] == "Operator.DutyScheduler" and log[3] == "failed to submit beacon committee subscription":
                data = json.loads(log[4])
                err = data['error'].replace('\\"', '\"').replace('\\n', '\n')
                tolog = f"Failed to submit beacon commitee subscribtion for role {MATCHES[data['handler']]}." + \
                    f" Error: {colorama.Fore.LIGHTRED_EX}{err}{colorama.Fore.RESET}"

            elif log[2] == "Operator.DutyScheduler" and log[3] == "failed to submit beacon committee subscription":
                data = json.loads(log[4])
                tolog = f"{data}"

            elif log[2] == "Operator.DutyScheduler" and log[3] == "🔁 indices change received":
                if NOSPAM:
                    continue
                data = json.loads(log[4])
                tolog = f"Received indices change for {colorama.Fore.LIGHTMAGENTA_EX}{MATCHES[data['handler']]}{colorama.Fore.RESET} duty"

            elif log[2] == "Operator.DutyScheduler" and log[3] == "could not execute committee duty":
                data = json.loads(log[4])
                err = data['error'].replace('\\"', '\"').replace('\\n', '\n')
                tolog = f"Failed to execute committee duty for {MATCHES[data['handler']]} duty at {colorama.Fore.CYAN}slot {data['slot']}{colorama.Fore.RESET}." + \
                    f"Error {colorama.Fore.LIGHTRED_EX}{err}{colorama.Fore.RESET}"

            elif log[2] == "Operator.DutyScheduler" and log[3] == "starting duty handler":
                data = json.loads(log[4])
                tolog = f"Starting {MATCHES[data['handler']]} duty handler"

            # Miscellaneous log handling

            elif log[2] == "increasing MaxPeers to match the operator's subscribed subnets":
                data = json.loads(log[3])
                tolog = f"Increasing MaxPeers to {colorama.Fore.MAGENTA}{data['new_max_peers']}{colorama.Fore.RESET} to match the operator's subscribed subnets (from {colorama.Fore.MAGENTA}{data['old_max_peers']}{colorama.Fore.RESET})."

            elif log[2] == "setting ssv network":
                data = json.loads(log[3])
                print(data)
                tolog = f"Configuring SSV node for running on {colorama.Fore.MAGENTA}" + \
                    f"{data['network']}{colorama.Fore.RESET}"

            elif log[2] == "applying migrations":
                data = json.loads(log[3])
                tolog = f"Applying {colorama.Fore.LIGHTBLUE_EX}{data['count']}" + \
                    f"{colorama.Fore.RESET} migrations"

            elif log[2] == "applied migrations successfully":
                tolog = "Applied migrations sucessfully"

            elif log[2] == "successfully setup operator keys":
                data = json.loads(log[3])
                tolog = f"Set up operator key ({colorama.Fore.MAGENTA}{data['pubkey'][16:]}" + \
                    f"{colorama.Fore.RESET})"

            elif log[2] == "successfully loaded operator keys":
                data = json.loads(log[3])
                tolog = f"Loaded operator key ({colorama.Fore.MAGENTA}{data['pubkey'][16:]}" + \
                    f"{colorama.Fore.RESET})"

            elif log[2] == "consensus client: connecting":
                data = json.loads(log[3])
                tolog = f"Connecting to consensus client at {colorama.Fore.MAGENTA}" + \
                    f"{data['address']}{colorama.Fore.RESET}"

            elif log[2] == "consensus client connected":
                data = json.loads(log[3])
                tolog = f"Connecting to consensus client at {colorama.Fore.MAGENTA}" + \
                    f"{data['version']}{colorama.Fore.RESET}"

            elif log[2] == "waiting until nodes are healthy":
                tolog = "Waiting until all clients are synced and healthy"

            elif log[2] == "ethereum node(s) are healthy":
                tolog = "All clients are synced and healthy"

            elif log[2] == "historical registry sync stats":
                data = json.loads(log[3])
                tolog = "Network statistics: "
                additional_logs.append(f"Operator ID           : {data['my_operator_id']}")
                additional_logs.append(f"Operators on network  : {data['operators']}")
                additional_logs.append(f"Validators on network : {data['validators']}")
                additional_logs.append(f"Liquidated Validators : {data['liquidated_validators']}")
                additional_logs.append(f"Validators managed    : {data['my_validators']}")

            elif log[2] == "All required services are ready. " + \
                    "OPERATOR SUCCESSFULLY CONFIGURED AND NOW RUNNING!" or \
                    log[3] == "All required services are ready. " + \
                    "OPERATOR SUCCESSFULLY CONFIGURED AND NOW RUNNING!":  
                tolog = "Operator configured sucessfully"

                additional_logs.append(f"{colorama.Fore.GREEN}" + \
                    f"╔═╗╔╦╗╔═╗╦═╗╔╦╗╦ ╦╔═╗  ╔═╗╦ ╦╔═╗╔═╗╔═╗╔═╗╔═╗{colorama.Fore.RESET}")
                additional_logs.append(f"{colorama.Fore.GREEN}" + \
                    f"╚═╗ ║ ╠═╣╠╦╝ ║ ║ ║╠═╝  ╚═╗║ ║║  ║  ║╣ ╚═╗╚═╗{colorama.Fore.RESET}")
                additional_logs.append(f"{colorama.Fore.GREEN}" + \
                    f"╚═╝ ╩ ╩ ╩╩╚═ ╩ ╚═╝╩    ╚═╝╚═╝╚═╝╚═╝╚═╝╚═╝╚═╝{colorama.Fore.RESET}")

            elif log[2] == "going to submit batch validator registrations":
                data = json.loads(log[3])
                tolog = f"Planning to submit {colorama.Fore.MAGENTA}{data['count']}" + \
                    f"{colorama.Fore.RESET} validator registrations"

            elif log[2] == "submitted batched validator registrations":
                data = json.loads(log[3])
                tolog = f"Submitted {colorama.Fore.MAGENTA}{data['count']}{colorama.Fore.RESET}" + \
                    " validator registrations"

            elif log[2] == "could not submit proposal preparation batch":
                data = json.loads(log[3])
                tolog = "Failed to submit proposal preparation batch.\n"
                tolog += "Error: " + data['error'].replace('\\"', '"')

            # Metrics

            elif log[2] == "MetricsHandler" and log[3] == "setup collection":
                data = json.loads(log[4])
                tolog = f"Setting up metrics collection on address {colorama.Fore.LIGHTBLUE_EX}" + \
                    f"{data['address']}{colorama.Fore.RESET}"


            # Specific Error Handling

            elif "node is not healthy" in log[2]:
                data = json.loads(log[3])
                node = data["node"]
                error = data["error"].replace('\\"', '"')
                tolog = f"Issue with {node}. {error}"
                if FULLERRORS:
                    verbose = data["errorVerbose"].replace('\\"', '"').replace('\\n', '\n') \
                        .replace('\\r', '\r').replace('\\t', '\t')
                    tolog+= f"\nFull Traceback:\n{verbose}"

            # Generic Error handling and fallback
            else:
                if "ERROR" in stat or "FATAL" in stat:
                    try:
                        data = json.loads(log[3])
                        tolog = f"{log[2]} - {data['error']}"
                        if FULLERRORS and "errorVerbose" in data.keys():
                            verbose = data["errorVerbose"].replace('\\"', '"').replace('\\n', '\n') \
                                .replace('\\r', '\r').replace('\\t', '\t')
                            tolog+= f"\nFull Traceback:\n{verbose}"
                    except IndexError:
                        tolog = f"{log[2]}"
                    except json.decoder.JSONDecodeError:
                        tolog = f"{log[2]} - {log[3]}"
                else:
                    tolog = "        ".join(log[2:])

        except json.decoder.JSONDecodeError:
            tolog = "        ".join(log[2:])
        except IndexError:
            tolog = "        ".join(log[2:])

        # Print log to stdout

        print(f"{time} {stat}: {tolog}")

        # Print and reset additional logs

        for i in additional_logs:
            print(f"{time} {stat}: {i}")

        additional_logs = []

if __name__ == "__main__":
    main()
