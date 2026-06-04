import RNS
import time
import json
import sys
import argparse
import os

# add prove packet
# make package for transport node


APP_NAME = "pathfinder"
WORKING_DIR = ""


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

###########################################
#### START ################################
###########################################


def start_node(configpath, identitiespath, target_hash):
    reticulum = RNS.Reticulum(configpath)
    start_identity = RNS.Identity.from_file("identity2")
  
    start_dest = RNS.Destination(
        start_identity,
        RNS.Destination.IN,
        RNS.Destination.SINGLE,
        APP_NAME,
    )
  
    RNS.log(f"START node {start_dest.hash.hex()} running.")
    print("")
    
    path = ["START", ]
    transport_hex_to_identity = map_transport_hexhashes_to_identities(identitiespath)


    def packet_handler(message, packet):
        try:
            pathfinder_response = json.loads(message.decode('utf-8'))
        except:
            RNS.log(f"Ignored packet: {message.decode('utf-8')}")
            return
        
        path.append(pathfinder_response["id"])
        next_hop = bytes.fromhex(pathfinder_response["nh_ihh"])
        if next_hop == target_hash:
            RNS.log("Pathfinder successful! Printing results... (Ctrl+C to quit)")
            pathfinder_end_results(path)
            return
        else:
            RNS.log(f"Received pathfinder packet from {pathfinder_response['id']}, querying next hop ({next_hop.hex()})...")
            query_next_hop(start_dest, transport_hex_to_identity[next_hop.hex()])
            return


    start_dest.set_packet_callback(packet_handler)

    RNS.log("Starting pathfinder.")
    if find_path_has_path(target_hash):
        next_hop = RNS.Transport.next_hop(target_hash)
        if next_hop == target_hash:
            RNS.log("Pathfinder successful! Printing results... (Ctrl+C to quit)")
            pathfinder_end_results(path)
        else:
            RNS.log(f"Querying next hop ({next_hop.hex()})...")
            query_next_hop(start_dest, transport_hex_to_identity[next_hop.hex()])
    else:
        RNS.log("Pathfinder unsuccessful. Try again. (Ctrl+C to exit)")
  
    # Send announces manually
    while True:
        entered = input()
        if entered == "":
            start_dest.announce()
            RNS.log(f"Sent announce from {RNS.prettyhexrep(start_dest.hash)}")


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

    if find_path_has_path(remote_dest.hash):
        RNS.Packet(remote_dest, json.dumps(payload).encode('utf-8')).send()
        RNS.log(f"Path query sent to {remote_dest.hash.hex()}")
    else:
        RNS.log(f"{remote_dest.hash.hex()} cannot be reached")


def map_transport_hexhashes_to_identities(identitiespath):
    """Map each transport hexhash to path of identity file (relative to CWD)"""
    transport_to_identity = {}
    for i_set in os.listdir(identitiespath):
        transport_hexhash = RNS.Identity.from_file(os.path.join(identitiespath, i_set, "transport_identity")).hash.hex()
        transport_to_identity.update({transport_hexhash: os.path.join(identitiespath, i_set, "identity")})
    return transport_to_identity


def pathfinder_end_results(path):
    path.append("END")
    print(f"""
*****************************
{" -> ".join(path)}
*****************************
    """)

# Utility for testing
def send_hello_to_dest(dest_h):
    dest = RNS.Destination(
        RNS.Identity.recall(dest_h),
        RNS.Destination.OUT,
        RNS.Destination.SINGLE,
        APP_NAME,
    )
    RNS.Packet(dest, "hello".encode('utf-8')).send()


###########################################
#### INTERMEDIATE (TRANSPORT) #############
###########################################

# Must have fixed identity

def intermediate_node(configpath):
    global identity
    reticulum = RNS.Reticulum(configpath)
    identity = RNS.Identity.from_file("identity")
  
    transport_destination = RNS.Destination(
        identity,
        RNS.Destination.IN,
        RNS.Destination.SINGLE,
        APP_NAME
    )
    
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
            node_id = next(open("id.txt")).strip()
            return_payload = {
                "id": node_id,
                "nh_ihh": next_hop.hex(),
            }
            # recalling identity doesn't seem to work
            sender_identity = RNS.Identity.from_file("../identity2")
            sender_dest = RNS.Destination(
                sender_identity,
                RNS.Destination.OUT,
                RNS.Destination.SINGLE,
                APP_NAME,
            )
            RNS.Packet(sender_dest, json.dumps(return_payload).encode('utf-8')).send()
            RNS.log("Sent path query response to sender.")
            return
        else:
            RNS.log("Path lookup to target failed.")
            return


###########################################
#### END ##################################
###########################################


def end_node(configpath):
    reticulum = RNS.Reticulum(configpath)
    target_identity = RNS.Identity.from_file("identity1")
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
  
  