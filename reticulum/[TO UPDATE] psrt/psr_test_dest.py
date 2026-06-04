##########################################################
# This RNS script enables packet success rate to be      #
# tested when the packet is sent at fixed intervals,     #
# across a link between a client and a server            #
##########################################################


import os
import sys
import time
import argparse
import RNS
import json
import csv
import random
from google.protobuf.json_format import ParseDict
import bridpacket_ts_pb2

# Let's define an app name. We'll use this for all
# destinations we create. Since this echo example
# is part of a range of example utilities, we'll put
# them all within the app namespace "example_utilities"
APP_NAME = "reticulum_test"
with open('bridpackets_ts.json', 'r') as f:
    PAYLOAD_DATA_NO_TS_ID = json.load(f)
FIELDNAMES = [
    "packet_id",
    "rssi_dbm",
    "snr_db",
    "tx_time",
    "rx_time",
]


##########################################################
#### Server Part #########################################
##########################################################


# The CSV file and writer that will be used for data collection
csv_file_path = None
csv_file = None
writer = None

  
# This initialisation is executed when the users chooses
# to run as a server
def server(configpath):
    # We must first initialise Reticulum
    reticulum = RNS.Reticulum(configpath)
  
    # Use a pre-generated identity
    server_identity = RNS.Identity.from_file("serverIdentity")
  
    # We create a destination that clients can connect to. We
    # want clients to create links to this destination, so we
    # need to create a "single" destination type.
    # 'linkexample' is a 'sub-channel' of APP_NAME. Changing this would change the destination hash.
    server_destination = RNS.Destination(
        server_identity,
        RNS.Destination.IN,
        RNS.Destination.SINGLE,
        APP_NAME,
        "multinode_test"
    )
    
    # Open CSV file once
    global csv_file; global csv_file_path; global writer
    csv_file = open(csv_file_path, "a", newline="")
    writer = csv.DictWriter(csv_file, fieldnames=FIELDNAMES)
    if csv_file.tell() == 0:
        writer.writeheader()
    RNS.log(f"File {csv_file_path} opened. Listening for packets (Ctrl+C to quit)")

    # We configure a function that will get called every time
    # a new client creates a link to this destination.
    server_destination.set_packet_callback(server_packet_received)
    
    # Everything's ready!
    # Let's Wait for client requests or user input
    server_loop(server_destination)
  
  
def server_loop(destination):
    # Let the user know that everything is ready
    RNS.log(
        "Link example "+
        RNS.prettyhexrep(destination.hash)+
        " running, waiting for a connection."
    )

    RNS.log("Hit enter to manually send an announce (Ctrl-C to quit)")

    # We enter a loop that runs until the users exits.
    # If the user hits enter, we will announce our server
    # destination on the network, which will let clients
    # know how to create messages directed towards it.
    while True:
        entered = input()
        if entered == "":
            destination.announce()
            RNS.log("Sent announce from "+RNS.prettyhexrep(destination.hash))


def server_packet_received(message, packet):
    global csv_file; global writer
    rx_time = time.time()
    try: 
        packet_pb = bridpacket_ts_pb2.Packet()
        packet_pb.ParseFromString(message)  
    except:
        return
    log_packet(packet_pb, packet, rx_time, csv_file, writer)
    print(f"[INFO] BRID packet received and logged to CSV file")


def log_packet(brid_packet, reticulum_packet, rx_time, csv_file, writer):
    # Extract useful data for analysis
    row = {
        "packet_id": brid_packet.packet_id,
        "rssi_dbm": reticulum_packet.get_rssi(),
        "snr_db": reticulum_packet.get_snr(),
        "tx_time": brid_packet.timestamp,
        "rx_time":rx_time,
    }
    writer.writerow(row)
    csv_file.flush() 


##########################################################
#### Client Part #########################################
##########################################################


# This initialisation is executed when the users chooses
# to run as a client
def client(destination_hexhash, configpath, interval):
    # We need a binary representation of the destination
    # hash that was entered on the command line
    try:
        dest_len = (RNS.Reticulum.TRUNCATED_HASHLENGTH//8)*2
        if len(destination_hexhash) != dest_len:
            raise ValueError(
                "Destination length is invalid, must be {hex} hexadecimal characters ({byte} bytes).".format(hex=dest_len, byte=dest_len//2)
            )
            
        destination_hash = bytes.fromhex(destination_hexhash)
    except:
        RNS.log("Invalid destination entered. Check your input!\n")
        sys.exit(0)

    # We must first initialise Reticulum
    reticulum = RNS.Reticulum(configpath)

    # Check if we know a path to the destination
    if not RNS.Transport.has_path(destination_hash):
        RNS.log("Destination is not yet known. Requesting path and waiting for announce to arrive...")
        RNS.Transport.request_path(destination_hash)
        while not RNS.Transport.has_path(destination_hash):
            time.sleep(0.1)

    # Recall the server identity
    server_identity = RNS.Identity.recall(destination_hash)

    # Inform the user that we'll begin connecting
    RNS.log("Initiating connection with server...")

    # When the server identity is known, we set
    # up a destination
    server_destination = RNS.Destination(
        server_identity,
        RNS.Destination.OUT,
        RNS.Destination.SINGLE,
        APP_NAME,
        "multinode_test"
    )

    # Everything is set up, so let's enter a loop
    # for the user to interact with the example
    client_loop(server_destination, interval)


def client_loop(destination, interval):

    RNS.log(f"Starting transmission of BRID packets at {interval}s intervals (Ctrl+C to quit)")
    packet_count = 1
    while True:
        try:
            RNS.Packet(destination, generate_brid_packet_ts(packet_count)).send()
            packet_count += 1
            time.sleep(interval)
        except KeyboardInterrupt:
            RNS.log("Closing interface.")


def generate_brid_packet_ts(packet_id: int) -> bytes:
    global PAYLOAD_DATA_NO_TS_ID
    packet_dict = random.choice(PAYLOAD_DATA_NO_TS_ID)
    packet_dict['packet_id'] = packet_id
    packet_dict['timestamp'] = time.time()
    packet_pb = bridpacket_ts_pb2.Packet()
    ParseDict(packet_dict, packet_pb)
    packet_bytes = packet_pb.SerializeToString()
    return packet_bytes


##########################################################
#### Program Startup #####################################
##########################################################


# This part of the program runs at startup,
# and parses input of from the user, and then
# starts up the desired program mode.
if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Simple link example")

        parser.add_argument(
            "-s",
            "--server",
            action="store_true",
            help="wait for incoming link requests from clients"
        )

        parser.add_argument(
            "--csv_file",
            action="store",
            default='brid_packets_reticulum.csv',
            help="CSV file to record packet data to",
            type=str
        )

        parser.add_argument(
            "--interval",
            action="store",
            default=1,
            help="Time between BRID packets in seconds",
            type=float
        )

        parser.add_argument(
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

        if args.config:
            configarg = args.config
        else:
            configarg = None

        if args.server:
            csv_file_path = args.csv_file
            server(configarg)
        else:
            if (args.destination == None):
                print("")
                parser.print_help()
                print("")
            else:
                client(args.destination, configarg, args.interval)

    except KeyboardInterrupt:
        print("")
        sys.exit(0)


