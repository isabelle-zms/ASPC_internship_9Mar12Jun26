##########################################################
# This file helps to test the packet success rate from   #
# transmitter to receiver on Meshtastic, using data      #
# packets                                                #
##########################################################


import argparse
import time
import meshtastic
import meshtastic.serial_interface
from pubsub import pub
import random
import json
import csv
from google.protobuf.json_format import ParseDict
import bridpacket_ts_pb2


# define variables
with open('bridpackets_ts.json', 'r') as f:
    PAYLOAD_DATA_NO_TS_ID = json.load(f)
FIELDNAMES = [
    "packet_id",
    "snr_db",
    "tx_time",
    "rx_time",
    "hops_used",
]

##########################################################
#### Server Part #########################################
##########################################################


def server(csv_file):
    # Connect to interface
    ifaceServer = meshtastic.serial_interface.SerialInterface("/dev/ttyACM0")
    print(f"[INFO] Server interface connected with node ID {ifaceServer.getMyNodeInfo()['user']['id']}. Listening for packets ... Hit enter to reset packet count (Ctrl+C to quit)")

    # Open file once, and write a header if the file is empty
    f = open(csv_file, "a", newline="")
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    if f.tell() == 0:
        writer.writeheader()
    print(f"[INFO] File {csv_file} opened. Listening for packets (Ctrl+C to quit)")

    # Handles packet upon receiving
    def on_receive(packet, interface):
        rx_time = time.time()
        try: 
            packet_pb = bridpacket_ts_pb2.Packet()
            packet_pb.ParseFromString(packet['decoded']['payload'])  
        except:
            return
        log_packet(packet_pb, packet, rx_time, f, writer)
        print(f"[INFO] BRID packet received and logged to CSV file")

    # Start listening to packets
    pub.subscribe(on_receive, "meshtastic.receive.data")

    while True:
        time.sleep(5)    

# Write data to CSV file
def log_packet(brid_packet, meshtastic_packet, rx_time, csv_file, writer):
    # Extract useful data for analysis
    row = {
        "packet_id": brid_packet.packet_id,
        "snr_db": meshtastic_packet['rxSnr'],
        "tx_time": brid_packet.timestamp,
        "rx_time":rx_time,
        "hops_used": meshtastic_packet['hopStart'] - meshtastic_packet['hopLimit'],
    }

    writer.writerow(row)
    csv_file.flush() 
      

##########################################################
#### Client Part #########################################
##########################################################


def client(server_nodeid, interval=None):
    ifaceClient = meshtastic.serial_interface.SerialInterface("/dev/ttyACM1")
    pub.subscribe(log_line, "meshtastic.log.line")
    print(f"[INFO] Client interface connected.")
   
    print(f"[INFO] Starting transmission of BRID packets at {interval}s intervals (Ctrl+C to quit)")
    packet_count = 1
    while True:
        ifaceClient.sendData(generate_brid_packet_ts(packet_count), server_nodeid)
        print(f"[INFO] BRID packet sent to node {server_nodeid}")
        packet_count += 1
        time.sleep(interval)


def generate_brid_packet_ts(packet_id: int) -> bytes:
    packet_dict = random.choice(PAYLOAD_DATA_NO_TS_ID)
    packet_dict['packet_id'] = packet_id
    packet_dict['timestamp'] = time.time()
    packet_pb = bridpacket_ts_pb2.Packet()
    ParseDict(packet_dict, packet_pb)
    packet_bytes = packet_pb.SerializeToString()
    return packet_bytes


def log_line(line, interface):
    print(line)
      
##########################################################
#### Program Startup #####################################
##########################################################


if __name__ == "__main__":
   try:
       parser = argparse.ArgumentParser(description="Simple link example")


       parser.add_argument(
           "-c",
           "--client",
           action="store_true",
           help="Send packets to server"
       )

       parser.add_argument(
           "--interval",
           action="store",
           default=5,
           help="Interval between packets in seconds",
           type=float
       )

       parser.add_argument(
           "--csv_file",
           default='brid_packets_meshtastic.csv',
           help="CSV file to record packet data to",
           type=str
       )

       parser.add_argument(
           "destination",
           nargs="?",
           default=None, 
           help="Server node ID e.g. !435a0bf4", 
           type=str 
       )


       args = parser.parse_args()

       if args.client == True:
            server_nodeid = args.destination
            interval = args.interval
            client(server_nodeid, interval)
       else:
            server(args.csv_file)


   except KeyboardInterrupt:
       print("")
       exit()





