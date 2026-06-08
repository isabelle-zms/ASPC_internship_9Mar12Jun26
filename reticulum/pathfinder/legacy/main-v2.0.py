import RNS
import time
import json
import sys
import argparse
import os

# identity vs transport identity vs destination hash
# challenge: recalling an identity from a hash (transport identity does not work)


APP_NAME = "pathfinder"
WORKING_DIR = ""
pathfinder_responses = []


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
  
    start_dest.set_packet_callback(packet_handler)
  
    # Optional: Obtain net hop to target. Will return Transport identity or target destination hash
    if find_path_has_path(target_hash):
      RNS.log(f"Next hop is {RNS.Transport.next_hop(target_hash).hex()}")
  
    # Send path table query to all nodes in the network
    send_remote_queries(start_dest, identitiespath, target_hash)
  
    # Send announces manually
    while True:
        entered = input()
        if entered == "":
            start_dest.announce()
            RNS.log(f"Sent announce from {RNS.prettyhexrep(start_dest.hash)}")


def send_remote_queries(start_dest, identitiespath, target_hash):
    payload = {
        "sender_hash": start_dest.hash.hex(),
        "target_dest_hexhash": target_hash.hex(),
    }
  
    for i_set in os.listdir(identitiespath):
        # Register a Destination for the transport node identity
        remote_identity = RNS.Identity.from_file(os.path.join(identitiespath, i_set, "identity"))
        remote_dest = RNS.Destination(
            remote_identity,
            RNS.Destination.OUT,
            RNS.Destination.SINGLE,
            APP_NAME,
        )
       
        if find_path_has_path(remote_dest.hash):
          RNS.Packet(remote_dest, json.dumps(payload).encode('utf-8')).send()
          RNS.log(f"Path query sent to {RNS.prettyhexrep(remote_dest.hash)}")
        else:
          RNS.log(f"{RNS.prettyhexrep(remote_dest.hash)} cannot be reached")
  
        time.sleep(5)


def packet_handler(message, packet):
    try:
        pathfinder_response = json.loads(message.decode('utf-8'))
    except:
        RNS.log(f"Ignored packet: {message.decode('utf-8')}")
        return
    with open('pathfinder.json', 'a') as f:
        RNS.log(f"Logging pathfinder response to pathfinder.json")
        json.dump(pathfinder_response, f)
        f.write("\n")
    return


###########################################
#### INTERMEDIATE (TRANSPORT) #############
###########################################

# Must have fixed identity

def intermediate_node(configpath):
    global identity
    reticulum = RNS.Reticulum(configpath)
    identity = RNS.Identity.from_file("v2-identities/set1/identity")
  
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
        RNS.log(f"Received a path query packet from {payload['sender_hash']} to {payload['target_dest_hexhash']}")
        target_hash = bytes.fromhex(payload["target_dest_hexhash"])
       
        if find_path_has_path(target_hash):
            next_hop_hash = RNS.Transport.next_hop(target_hash)
            return_payload = {
                "node_id": "abc",
                "node_transport_hexhash": RNS.Transport.identity.hash.hex(),
                "next_hop_hexhash": next_hop_hash.hex(),
            }
            sender_identity = RNS.Identity.from_file("identity2")
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
    RNS.log(f"START node {target_destination.hash.hex()} running.")
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
  
  