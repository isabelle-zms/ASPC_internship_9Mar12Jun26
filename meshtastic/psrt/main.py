"""
psrt_manual_auto.py — Packet Success Rate Test for Meshtastic

Tests the packet delivery success rate between a transmitter (client) and
receiver (server) over a Meshtastic LoRa mesh network using structured
BRID data packets serialised with Protocol Buffers.

Modes:
    Server: Listens on a serial-connected Meshtastic node, identifies BRID
            packets by magic prefix, parses them, and logs metadata to CSV.
    Client: Connects to a serial-connected Meshtastic node and sends BRID
            packets to the server either manually (one at a time) or
            automatically at a fixed interval.

Usage:
    Server: python3 psrt_manual_auto.py -p /dev/ttyACM0 -f brid_packets_meshtastic.csv
    Server (view CSV): tail -f brid_packets_meshtastic.csv
    Client (auto): python3 psrt_manual_auto.py -c -p /dev/ttyACM1 -a -i 3 -n 100 '!435a0bf4'
    Client (manual): python3 psrt_manual_auto.py -c -p /dev/ttyACM1 '!435a0bf4'

Dependencies:
    meshtastic, pubsub, tqdm, protobuf, bridpacket_ts_pb2, bridpackets_ts.json
"""


import argparse
import time
import meshtastic
import meshtastic.serial_interface
from pubsub import pub
import random
from tqdm import tqdm
import json
import csv
from google.protobuf.json_format import ParseDict
import bridpacket_ts_pb2

PAYLOAD_DATA_NO_TS_ID = json.load(open('bridpackets_ts.json', 'r')) # Pre-defined packet payloads (without timestamps/IDs)
FIELDNAMES = ["packet_id", "snr_db", "tx_time", "rx_time", "hops_used"] # CSV column schema
MAGIC = b'BRID' # 4-byte magic prefix used to identify BRID packets in the Meshtastic data stream


##########################################################
#### Server Part #########################################
##########################################################


def server(serial_path, csv_file):
    """
    Start the receiver node, listen for incoming BRID packets, and log them to CSV.

    Connects to a Meshtastic device over serial and subscribes to incoming data
    packets. Packets prefixed with the BRID magic bytes are parsed as protobuf
    Packet messages and their metadata is appended to the specified CSV file.
    Non-BRID packets are printed. Press Enter to reset the running
    packet count; Ctrl+C to shut down cleanly.

    Args:
        serial_path (str): Serial port path of the Meshtastic device, e.g. '/dev/ttyACM0'.
        csv_file (str): Path to the CSV file where received packet data will be logged.
    """
    brid_count = 0
    ifaceServer = meshtastic.serial_interface.SerialInterface(serial_path)
    print(f"[INFO] Server interface connected with node ID {ifaceServer.getMyNodeInfo()['user']['id']}.")
 
    def on_receive(packet, interface):
        nonlocal brid_count
        rx_time = time.time()
        if packet.get('decoded') is not None:
            packet_payload = packet['decoded']['payload']
            if packet_payload.startswith(MAGIC):
                brid_count += 1
                packet_pb = bridpacket_ts_pb2.Packet()
                try:
                    packet_pb.ParseFromString(packet['decoded']['payload'][len(MAGIC):])
                    log_packet(packet_pb, packet, rx_time, f, writer)
                    print(f"[INFO] BRID packet received and logged to CSV file. Total count: {brid_count}")
                except Exception as e:
                    print("Failed to parse protobuf:", e)
                return
            else:
                print(f"[INFO] Received data from {packet['fromId']}: {packet_payload.decode('utf-8')}")
    
    f = open(csv_file, "a", newline="") # Open CSV in append mode so previous runs are preserved
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    if f.tell() == 0: # Only write header if file is empty (new file)
        writer.writeheader()

    pub.subscribe(on_receive, "meshtastic.receive.data")
    print(f"[INFO] File {csv_file} opened. Listening for packets ... Hit enter to reset BRID count (Ctrl+C to quit)")

    try:
        while True:
            text = input()
            if text == '':
                brid_count = 0
                print(f"[INFO] Packet count reset.")
    except KeyboardInterrupt:
        print(f"[INFO] Closing interface and CSV file.")
        f.close()
        ifaceServer.close()


def log_packet(brid_packet, meshtastic_packet, rx_time, csv_file, writer):
    """
    Write a single received BRID packet's metadata to the open CSV file.

    Extracts packet ID, SNR, transmit timestamp, receive timestamp, and hop
    count, then writes them as one row and flushes the buffer so data is
    preserved even if the process is interrupted. csv_file and writer are captured from the enclosing server() scope.

    Args:
        brid_packet (bridpacket_ts_pb2.Packet): Parsed protobuf packet containing
            packet_id and timestamp (tx_time).
        meshtastic_packet (dict): Raw Meshtastic packet dict providing rxSnr,
            hopStart, and hopLimit fields.
        rx_time (float): Unix timestamp (seconds) recorded at the moment the
            packet was received.
        csv_file: Open file object used for flushing after each write.
        writer (csv.DictWriter): Writer bound to csv_file using FIELDNAMES schema.
    """
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


def client(serial_path, server_nodeid, transmission_mode, interval, num_packets):
    """
    Start the transmitter node and send BRID packets to the server.

    Connects to a Meshtastic device over serial and sends packets to the
    specified destination node. Supports two transmission modes:

    - 'manual': Prompts for input in a loop. An empty Enter sends one random
      BRID packet; any other text is sent as raw UTF-8; 'quit' exits.
    - 'auto': Sends `num_packets` BRID packets spaced `interval` seconds apart,
      then closes the interface.

    Args:
        serial_path (str): Serial port path of the Meshtastic device, e.g. '/dev/ttyACM1'.
        server_nodeid (str): Destination node ID in Meshtastic format, e.g. '!435a0bf4'.
        transmission_mode (str): Either 'manual' or 'auto'.
        interval (float, optional): Seconds to wait between packets in auto mode.
        num_packets (int, optional): Total packets to send in auto mode.
    """
    ifaceClient = meshtastic.serial_interface.SerialInterface(serial_path)
    print(f"[INFO] Client interface connected on {serial_path}")
    
    if transmission_mode == 'manual':
        print(f"[INFO] Manual transmission mode selected. Hit enter to randomly send a BRID packet, or type some text to send. Enter 'quit' to stop.")
        should_quit = False
        while should_quit == False:
            print("> ", end=" ")
            text = input()
            if text == '':
                packet_with_magic = MAGIC + generate_brid_packet_ts(0) # add 4 byte magic prefix to serialised BRID packet
                ifaceClient.sendData(packet_with_magic, server_nodeid)
            elif text == 'quit':
                should_quit = True
                print(f"[INFO] Closing client interface.")
            else:
                ifaceClient.sendData(text.encode('utf-8'), server_nodeid)
        ifaceClient.close()
    
    elif transmission_mode == 'auto':
        print(f"[INFO] Auto transmission mode selected. Starting transmission.")
        for i in tqdm(range(num_packets)): # tqdm progress bar
            packet_with_magic = MAGIC + generate_brid_packet_ts(i+1) # packet_id is 1-indexed
            ifaceClient.sendData(packet_with_magic, server_nodeid)
            time.sleep(interval)
        print(f"[INFO] Finished sending {num_packets} packets. Closing interface.")
        ifaceClient.close()


def generate_brid_packet_ts(packet_id: int) -> bytes:
    """
    Build and serialise a BRID packet as raw protobuf bytes.

    Selects a random payload template from the pre-loaded JSON pool, stamps
    it with the given packet ID and the current Unix timestamp, parses it into
    a protobuf Packet message, and returns the serialised bytes (without the
    BRID magic prefix — the caller is responsible for prepending it).

    Args:
        packet_id (int): Sequential identifier for this packet (0 in manual mode,
                         1-based counter in auto mode).

    Returns:
        bytes: Serialised protobuf Packet payload, ready to be prefixed with MAGIC
               and passed to ifaceClient.sendData().
    """
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


if __name__ == "__main__":
   try:
       parser = argparse.ArgumentParser(
           prog="Packet Success Rate Test", 
           description="Enables client to send either BRID packets or other data to server manually, or BRID packets automatically. Server logs BRID packets to a CSV file."
       )

       parser.add_argument("-c", "--client", action="store_true", help="Send packets to server")
       parser.add_argument("-p", "--port", required=True, help="Serial port e.g. /dev/ttyACM1", type=str)
       parser.add_argument("-f", "--csv_file", default='brid_packets_meshtastic.csv', help="CSV file to record packet data to", type=str)
       parser.add_argument("-a", "--auto", action="store_true", default=False, help="Sends packets automatically")
       parser.add_argument("-i", "--interval", action="store", default=5, help="Interval between packets in seconds", type=float)
       parser.add_argument("-n", "--num_packets", action="store", default=100, help="Number of packets sent", type=int)
       parser.add_argument("destination", nargs="?", default=None, help="Server node ID e.g. !435a0bf4", type=str)

       args = parser.parse_args()

       port = args.port

       if args.client:
           server_nodeid = args.destination
           if args.auto:
               interval = args.interval
               num_packets = args.num_packets
               client(port, server_nodeid, 'auto', interval, num_packets)
           else:
               client(port, server_nodeid, 'manual')
       else:
           server(port, args.csv_file)


   except KeyboardInterrupt:
       print("")
       exit()





