import RNS
import time
import json
import sys
import argparse


# If End disconnects, will resume usually operations upon connection. However if Start disconnects, requires resetting the node and rerunning the Python script.


# Path table:


# path_table = {
#     b'\xf5f\x06\x19\xd7\xf4\r-\x86dj/\xce\x05\xfe\xb1': [
#         1779110776.028899,
#         b'\xf5f\x06\x19\xd7\xf4\r-\x86dj/\xce\x05\xfe\xb1',
#         1,
#         1779715576.028899,
#         [b'\x1e_ B\x9f\x00j\x0b\x13w'],
#         <RNS.Interfaces.RNodeInterface.RNodeInterface object at 0x10183f2f0>, 
#         b'\xcaU\xe5V\xc1\x13\xb5\xcf\x12\x90j\x85y\x96\x16\x19\xb4D\xb5\xc2\xb6\x8b\xef\x19X_L\xfe\x17\xd7YM'
#     ]
#}
 #  --- Protocol Specifications ---
APP_NAME = "packet_tracer"
 
 
class HopByHopTracer(RNS.Reticulum):
    def __init__(self, config, node_name="whattoput"):
        self.node_name = node_name
        self.rns = RNS.Reticulum(config)
        self.identity = RNS.Identity()
        self.neighbours = {}
        # Set up the node's own destination and add packet handler
        self.dest = RNS.Destination(
            self.identity,
            RNS.Destination.IN,
            RNS.Destination.SINGLE,
            APP_NAME,
        )
        self.dest.set_proof_strategy(RNS.Destination.PROVE_ALL)
        self.dest_hash = self.dest.hash
        self.dest.set_packet_callback(self._on_packet_receive)
 
        print(f"[INIT] Node online: {self.node_name} | Addr: {RNS.prettyhexrep(self.dest_hash)}")

    # Clears current path table and requests a new path to the target
    def next_hop_destination(self, target_hexhash):
        target_hash = bytes.fromhex(target_hexhash)
       
        with RNS.Transport.path_table_lock:
            if target_hash in RNS.Transport.path_table:
                del RNS.Transport.path_table[target_hash]
        RNS.log("Refreshing path to target...")
        RNS.Transport.request_path(target_hash)
        while not RNS.Transport.has_path(target_hash):
            time.sleep(0.1)

        # Obtain destination hash and hexhash of next hop
        next_hop_hash = RNS.Transport.next_hop(target_hash)
        next_hop_hexhash = next_hop_hash.hex()

        # Return Destination of next hop
        if next_hop_hexhash in self.neighbours:
            return self.neighbours.get(next_hop_hexhash)
        else:
            next_hop_identity = RNS.Identity.recall(next_hop_hash)
            print(next_hop_identity)
            next_hop_destination = RNS.Destination(
                next_hop_identity,
                RNS.Destination.OUT,
                RNS.Destination.SINGLE,
                APP_NAME,
            )
            self.neighbours.update({next_hop_hexhash: next_hop_destination})
            return next_hop_destination
       
    # Initiation
    def start_trace(self, target_hash):
        payload = {
            "app_name": APP_NAME,
            "target": target_hash,
            "path": [self.node_name],
            "origin": self.node_name,
            "ts": 0,
        }

        print("")
        RNS.log(f"TRACE START: {self.dest_hash.hex()} -> {target_hash}")

        while True:
            print("")
            next_hop_dest = self.next_hop_destination(target_hash)
            payload['ts'] = time.time()
            # Use PacketReceipt to confirm delivery
            receipt = RNS.Packet(next_hop_dest, json.dumps(payload).encode("utf-8")).send()
            self.handle_receipt(receipt, target_hash)
            RNS.log(f"Traceroute packet sent to {RNS.prettyhexrep(next_hop_dest.hash)}")
            time.sleep(10)
   
    # Not exactly necessary, but useful for validating that the packet has been sent out.
    def handle_receipt(self, receipt, target_hash):
        def _on_packet_delivered(r):
            RNS.log("Packet delivered.")
        def _on_packet_timeout(r):
            RNS.log("Transmission failed. Next trace attempt in 5 seconds.")
 
        receipt.set_timeout(5)
        receipt.set_delivery_callback(_on_packet_delivered)
        receipt.set_timeout_callback(_on_packet_timeout)

    # Relay processing
    def _on_packet_receive(self, message, packet):
        try:
            payload = json.loads(message.decode("utf-8"))
        except:
            return
      
        if payload.get("app_name", None) == APP_NAME:
            target_hash = payload["target"]
            payload["path"].append(self.node_name)
 
 
            if bytes.fromhex(target_hash) == self.dest_hash:
                print(f"""
===============================================
TRACEROUTE from {payload["origin"]} to {self.node_name}
PATH: {" -> ".join(payload["path"])}
TIME TAKEN: {time.time() - payload['ts']}s
===============================================
""")
            else:
                print("I'm a transport node finally transporting")
                RNS.Packet(self.next_hop_destination(target_hash), json.dumps(payload).encode("utf-8")).send()

            
if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Reticulum packet tracer")
        parser.add_argument(
            "-s",
            "--server",
            action="store_true",
            help="wait for incoming packets from start node"
        )

        parser.add_argument(
            "-n",
            "--node_name",
            action='store',
            default="???",
            help="Identifier for node, useful for detailing node placements",
            type=str,
        )
 
        parser.add_argument(
            "-c",
            "--config",
            action="store",
            default=None,
            help="path to alternative Reticulum config directory",
            type=str
        )
 
        parser.add_argument(
            "destination",
            nargs="?",
            default=None,
            help="hexadecimal hash of the server destination",
            type=str
        )

        args = parser.parse_args()
        node = HopByHopTracer(args.config, args.node_name)
        if args.server:
            print("\n--- NODE ACTIVE (Listening/Relay Mode) ---")
        if not args.server:
            node.start_trace(args.destination)
 
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("")
        sys.exit(0)



