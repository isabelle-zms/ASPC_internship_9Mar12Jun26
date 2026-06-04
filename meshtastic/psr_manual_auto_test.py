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
from tqdm import tqdm
import json


# define variables
PAYLOAD_DATA = [b'bkt', b'bcm', b'ckt']
brid_count = 0

##########################################################
#### Server Part #########################################
##########################################################


def server(serial_path):
   ifaceServer = meshtastic.serial_interface.SerialInterface(serial_path) # add safety net
   pub.subscribe(on_receive, "meshtastic.receive.data")
   print(f"[INFO] Server interface connected with node ID {ifaceServer.getMyNodeInfo()['user']['id']}. Listening for packets ... Hit enter to reset packet count (Ctrl+C to quit)")
   while True:
       text = input()
       if text == '':
           global brid_count
           brid_count = 0
           print(f"[INFO] Packet count reset.")


def on_receive(packet, interface):
   if packet.get('decoded', None) != None:
       packet_payload = packet['decoded']['payload']
       if packet_payload in PAYLOAD_DATA:
           global brid_count
           brid_count += 1
           print(f"[INFO] BRID packet received. Total count: {brid_count}. Hit enter to reset count.")
           return
       else:
           print(f"[INFO] Received data from {packet['fromId']}: {packet_payload.decode('utf-8')}")
      

##########################################################
#### Client Part #########################################
##########################################################


def client(serial_path, server_nodeid, transmission_mode, interval=None, num_packets=None):
   ifaceClient = meshtastic.serial_interface.SerialInterface(serial_path)
   print(f"[INFO] Client interface connected on {serial_path}")
   
   # Manual mode lets users send BRID or other data individually
   if transmission_mode == 'manual':
       print(f"[INFO] Manual transmission mode selected. Hit enter to randomly send a BRID packet, or type some text to send. Enter 'quit' to stop.")
       should_quit = False
       while should_quit == False:
           print("> ", end=" ")
           text = input()
           if text == '':
               ifaceClient.sendData(random.choice(PAYLOAD_DATA), server_nodeid)
           elif text == 'quit':
               should_quit = True
               print(f"[INFO] Closing client interface.")
           else:
               ifaceClient.sendData(text.encode('utf-8'), server_nodeid)
       ifaceClient.close()
   
   # Auto mode transmits BRID data packets at a specific interval
   elif transmission_mode == 'auto':
       print(f"[INFO] Auto transmission mode selected. Starting transmission.")
       for i in tqdm(range(num_packets)):
           ifaceClient.sendData(random.choice(PAYLOAD_DATA), server_nodeid)
           time.sleep(interval)
       print(f"[INFO] Finished sending {num_packets} packets. Closing interface.")
       ifaceClient.close()
      
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
           "--auto",
           action="store_true",
           default=False,
           help="Sends packets automatically"
       )


       parser.add_argument(
           "--interval",
           action="store",
           default=5,
           help="Interval between packets in seconds",
           type=float
       )
      
       parser.add_argument(
           "--num_packets",
           action="store",
           default=10,
           help="Number of packets sent",
           type=int
       )


       parser.add_argument(
           "--port",
           required=True,
           help="Serial port e.g. /dev/ttyACM1",
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

       port = args.port

       if args.client == True:
           server_nodeid = args.destination
           if args.auto == True:
               interval = args.interval
               num_packets = args.num_packets
               client(port, server_nodeid, 'auto', interval, num_packets)
           else:
               client(port, server_nodeid, 'manual')
       else:
           server(port)


   except KeyboardInterrupt:
       print("")
       exit()





