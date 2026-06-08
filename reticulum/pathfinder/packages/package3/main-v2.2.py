import RNS
import time
import json
import sys
import argparse
import os


APP_NAME = "pathfinder"
WORKING_DIR = ""
RETRANSMISSION_ATTEMPTS = 3
RECEIPT_TIMEOUT = 5


def find_path_has_path(dest_hash, timeout=5):
    # with RNS.Transport.path_table_lock:
    #     if dest_hash in RNS.Transport.path_table:
    #         del RNS.Transport.path_table[dest_hash]
    ts = time.time()
    RNS.Transport.request_path(dest_hash)
    while time.time() - ts < timeout and not RNS.Transport.has_path(dest_hash):
        time.sleep(0.1)
    if RNS.Transport.has_path(dest_hash):
       return True
    return False


def send_packet_with_retransmission(dest, payload, attempts=RETRANSMISSION_ATTEMPTS, timeout=RECEIPT_TIMEOUT):
    for _ in range(attempts):
        receipt = RNS.Packet(dest, payload).send()
        ts = time.time()
        while time.time() - ts < timeout:
            if receipt.get_status() == 1:
                return True
            time.sleep(0.1)
    return False


###########################################
#### START ################################
###########################################


def start_node(configpath, identitiespath, target_hash):
    reticulum = RNS.Reticulum(".reticulum_startInstance")
    start_identity = RNS.Identity.from_file("startIdentity")
    start_dest = RNS.Destination(
        start_identity,
        RNS.Destination.IN,
        RNS.Destination.SINGLE,
        APP_NAME,
    )
    start_dest.set_proof_strategy(RNS.Destination.PROVE_ALL)
    RNS.log(f"START node {start_dest.hash.hex()} | {RNS.Transport.identity.hash.hex()} running.")
    path = ["START", ]
    transport_hex_to_identity = map_transport_hexhashes_to_identities(identitiespath)
  
    def packet_handler(message, packet):
        print("")
        try:
            pathfinder_response = json.loads(message.decode('utf-8'))
        except:
            RNS.log(f"Ignored packet: {message.decode('utf-8')}")
            return
      
        path.append(pathfinder_response["id"])
        next_hop = bytes.fromhex(pathfinder_response["nh_ihh"])
        if next_hop == target_hash:
            RNS.log("Pathfinder successful! Printing results... (Ctrl+C to quit)")
            pathfinder_end_results(path, ts)
            return
        else:
            RNS.log(f"Received pathfinder packet from {pathfinder_response['id']}, querying next hop ({next_hop.hex()})...")
            query_next_hop(start_dest, transport_hex_to_identity[next_hop.hex()])
            return
  
    start_dest.set_packet_callback(packet_handler)
    
    print("")
    RNS.log("Starting pathfinder...")
    ts = time.time()
    if find_path_has_path(target_hash):
        next_hop = RNS.Transport.next_hop(target_hash)
        if next_hop == target_hash:
            RNS.log("Pathfinder successful, direct transmission! Printing results... (Ctrl+C to quit)")
            pathfinder_end_results(path, ts)
        else:
            RNS.log(f"Querying next hop ({next_hop.hex()})...")
            query_next_hop(start_dest, transport_hex_to_identity[next_hop.hex()])
    else:
        RNS.log("Pathfinder unsuccessful. Try again. (Ctrl+C to quit)")
     # Send announces manually
    while True:
        entered = input()
        if entered == "":
            start_dest.announce()
            RNS.log(f"Sent announce from {start_dest.hash.hex()}")


def query_next_hop(start_dest, nh_i):
    payload = {
        "s_hh": start_dest.hash.hex(),
        "t_hh": target_hash.hex(),
    }
  
    remote_identity = RNS.Identity.from_file(nh_i)
    remote_dest = RNS.Destination(
        remote_identity,
        RNS.Destination.OUT,
        RNS.Destination.SINGLE,
        APP_NAME,
    )
    
    print("")
    if find_path_has_path(remote_dest.hash):
        if send_packet_with_retransmission(remote_dest, json.dumps(payload).encode('utf-8')):
            RNS.log(f"Path query sent to {remote_dest.hash.hex()}")
        else:
            RNS.log(f"Path query to {remote_dest.hash.hex()} failed. Try again. (Ctrl+C to quit)")
    else:
        RNS.log(f"{remote_dest.hash.hex()} cannot be reached. Try again. (Ctrl+C to quit)")


def map_transport_hexhashes_to_identities(identitiespath):
    """Map each transport hexhash to path of identity file (relative to CWD)"""
    transport_to_identity = {}
    for i_set in os.listdir(identitiespath):
        if i_set != ".DS_Store": # for Macbooks
            transport_hexhash = RNS.Identity.from_file(os.path.join(identitiespath, i_set, "transport_identity")).hash.hex()
            transport_to_identity.update({transport_hexhash: os.path.join(identitiespath, i_set, "identity")})
    return transport_to_identity


def pathfinder_end_results(path, ts):
    path.append("END")
    print(f"""
*****************************
{" -> ".join(path)}
Time taken: {time.time() - ts}
*****************************
""")


###########################################
#### INTERMEDIATE (TRANSPORT) #############
###########################################

# Must have fixed identity

def intermediate_node(configpath):
    global identity
    reticulum = RNS.Reticulum(configpath)
    identity = RNS.Identity.from_file("/opt/rns_pathfinder/package3/identity")
    transport_destination = RNS.Destination(
        identity,
        RNS.Destination.IN,
        RNS.Destination.SINGLE,
        APP_NAME
    )
    transport_destination.set_proof_strategy(RNS.Destination.PROVE_ALL)
     # 3 different hashes, destination, identity, and transport identity...
    RNS.log(f"TRANSPORT node {transport_destination.hash.hex()} | {identity.hash.hex()} | <{RNS.Transport.identity.hash.hex()}> running.")
    transport_destination.set_packet_callback(query_handler)
    while True:
        time.sleep(1)


def query_handler(message, packet):
    global identity
    payload = json.loads(message.decode('utf-8'))
    print("")
     # Identifies a path query packet by message type. Recommended to change...
    if isinstance(payload, dict):
        RNS.log(f"Received a path query packet from {payload['s_hh']} to {payload['t_hh']}")
        target_hash = bytes.fromhex(payload["t_hh"])
     
        if find_path_has_path(target_hash):
            next_hop = RNS.Transport.next_hop(target_hash)
            node_id = next(open("/opt/rns_pathfinder/package3/id.txt")).strip()
            return_payload = {
                "id": node_id,
                "nh_ihh": next_hop.hex(),
            }
            # recalling identity doesn't seem to work
            sender_identity = RNS.Identity.from_file("/opt/rns_pathfinder/package3/startIdentity")
            sender_dest = RNS.Destination(
                sender_identity,
                RNS.Destination.OUT,
                RNS.Destination.SINGLE,
                APP_NAME,
            )
            if send_packet_with_retransmission(sender_dest, json.dumps(return_payload).encode('utf-8')):
                RNS.log(f"Pathfinder response sent to {sender_dest.hash.hex()}")
            else:
                RNS.log(f"Pathfinder response to {sender_dest.hash.hex()} failed to deliver")
        else:
            RNS.log("Path lookup to target failed.")


###########################################
#### END ##################################
###########################################


def end_node(configpath):
    reticulum = RNS.Reticulum(".reticulum_endInstance")
    target_identity = RNS.Identity.from_file("endIdentity")
    target_destination = RNS.Destination(
        target_identity,
        RNS.Destination.IN,
        RNS.Destination.SINGLE,
        APP_NAME
    )
    RNS.log(f"TARGET node {target_destination.hash.hex()} running.")
    target_destination.set_packet_callback(server_packet_received)
    server_loop(target_destination)


def server_loop(destination):
    # Let the user know that everything is ready
    RNS.log("Hit enter to manually send an announce (Ctrl-C to quit)")
    while True:
        entered = input()
        if entered == "":
            destination.announce()
            RNS.log("Sent announce from "+RNS.prettyhexrep(destination.hash))


def server_packet_received(message, packet):
   RNS.log(f"Packet received: {message.decode('utf-8')}")


##########################################################
#### PROGRAMME STARTUP ###################################
##########################################################


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Packet tracer v2")
        parser.add_argument("-s", "--start", action="store_true", default=False, help="Start node")
        parser.add_argument("-t", "--transport", action="store_true", default=False, help="Transport/intermediate node")
        parser.add_argument("-e", "--end", action="store_true", default=False, help="End node")
        parser.add_argument("-c", "--config", action="store", default=None, help="path to alternative Reticulum config directory",type=str)
        parser.add_argument("-i", "--identities", action="store", default=None, help="path to transport/intermediate node identities", type=str)
        parser.add_argument("-d", "--destination", action="store", default=None, help="Hexhash of end node", type=str)
      
        args = parser.parse_args()
        if args.start:
            target_hash = bytes.fromhex(args.destination)
            start_node(args.config, args.identities, target_hash)
        elif args.transport:
            intermediate_node(args.config)
        elif args.end:
            end_node(args.config)
    except KeyboardInterrupt:
       print("")
       sys.exit(0)
