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
from tqdm import tqdm
import random


# Let's define an app name. We'll use this for all
# destinations we create. Since this echo example
# is part of a range of example utilities, we'll put
# them all within the app namespace "example_utilities"
APP_NAME = "example_utilities"
BRID_DATA = [b'\n\x03BLE\x12\x1170:04:1D:34:1A:62\x18\xb3\xff\xff\xff\xff\xff\xff\xff\xff\x01 \xff\xff\xff\xff\xff\xff\xff\xff\xff\x01(\xf0\xc2\xc5:0\x01B]\n\x12\x18\x01"\x0e18099470000022\n\x02\x08\x01\x12+\x11F\xce\xc2\x9ev\xb8\xf5?\x19b\xbe\xbc\x00\xfb\xffY@%\x00\x008A-\x00\x00\x04B5\x00\x00\x00\xbfM\x00\x00\xd4BU3\xc3\xd6D\x1a\x14\r\xac\xc5\xa7:%\x00\x00z\xc4-\x00\x00z\xc45\x00\x00z\xc4"\x00']
brid_count = 0


##########################################################
#### Server Part #########################################
##########################################################




# A reference to the latest client link that connected
latest_client_link = None



  
# This initialisation is executed when the users chooses
# to run as a server
def server(configpath):
    # We must first initialise Reticulum
    reticulum = RNS.Reticulum(configpath)
  
    # Use a pre-generated identity
    server_identity = RNS.Identity.from_file("./identity")
  
    # We create a destination that clients can connect to. We
    # want clients to create links to this destination, so we
    # need to create a "single" destination type.
    # 'linkexample' is a 'sub-channel' of APP_NAME. Changing this would change the destination hash.
    server_destination = RNS.Destination(
        server_identity,
        RNS.Destination.IN,
        RNS.Destination.SINGLE,
        APP_NAME,
        "psrtest"
    )
  
    # We configure a function that will get called every time
    # a new client creates a link to this destination.
    server_destination.set_link_established_callback(client_connected)
  
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

    RNS.log("Type 'announce' to manually send an announce, hit enter to reset BRID count. (Ctrl-C to quit)")

    # We enter a loop that runs until the users exits.
    # If the user hits enter, we will announce our server
    # destination on the network, which will let clients
    # know how to create messages directed towards it.
    while True:
        entered = input()
        if entered == "announce":
            destination.announce()
            RNS.log("Sent announce from "+RNS.prettyhexrep(destination.hash))
        elif entered == "":
            global brid_count
            brid_count = 0
            RNS.log("BRID count reset.")
        else:
            continue


# When a client establishes a link to our server
# destination, this function will be called with
# a reference to the link.
def client_connected(link):
    global latest_client_link
    global brid_count
    brid_count = 0
    RNS.log("Client connected")
    link.set_link_closed_callback(client_disconnected)
    link.set_packet_callback(server_packet_received)
    latest_client_link = link


def client_disconnected(link):
    RNS.log("Client disconnected")


def server_packet_received(message, packet):
    global brid_count
    # When data is received over any active link,
    # it will all be directed to the last client
    # that connected.
    if message in BRID_DATA:
        brid_count += 1
        RNS.log(f"Received BRID on the link (Count: {brid_count})")
    else:
        text = message.decode("utf-8")
        RNS.log("Received data on the link: "+text)


##########################################################
#### Client Part #########################################
##########################################################


# A reference to the server link
server_link = None


# This initialisation is executed when the users chooses
# to run as a client
def client(destination_hexhash, configpath, interval, num_packets):
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
    RNS.log("Establishing link with server...")

    # When the server identity is known, we set
    # up a destination
    server_destination = RNS.Destination(
        server_identity,
        RNS.Destination.OUT,
        RNS.Destination.SINGLE,
        APP_NAME,
        "psrtest"
    )

    # And create a link
    link = RNS.Link(server_destination)

    # We set a callback that will get executed
    # every time a packet is received over the
    # link
    link.set_packet_callback(client_packet_received)

    # We'll also set up functions to inform the
    # user when the link is established or closed
    link.set_link_established_callback(link_established)
    link.set_link_closed_callback(link_closed)

    # Everything is set up, so let's enter a loop
    # for the user to interact with the example
    client_loop(interval, num_packets)


def client_loop(interval, num_packets):
    global server_link

    # Wait for the link to become active
    while not server_link:
        time.sleep(0.1)

    should_quit = False
    while not should_quit:
        try:
            
            print("> ", end=" ")
            text = input()

            # Check if we should quit the example
            if text == "quit" or text == "q" or text == "exit":
                should_quit = True
                server_link.teardown()
    
            # or run another test
            elif text == "":
                RNS.log(f"Starting BRID test ({num_packets} at {interval}s intervals)")
                for i in tqdm(range(num_packets)):
                    RNS.Packet(server_link, random.choice(BRID_DATA), create_receipt=False).send()
                    time.sleep(interval)
                RNS.log(f"Finished sending {num_packets} packets (interval: {interval}). Hit enter to run another test, type to send data, or 'quit' to exit.")   

            # If not, send the entered text over the link
            else:
                data = text.encode("utf-8")
                if len(data) <= RNS.Link.MDU:
                    RNS.Packet(server_link, data, create_receipt=False).send()
                else:
                    RNS.log(
                        "Cannot send this packet, the data size of "+
                        str(len(data))+" bytes exceeds the link packet MDU of "+
                        str(RNS.Link.MDU)+" bytes",
                        RNS.LOG_ERROR
                    )

        except Exception as e:
            RNS.log("Error while sending data over the link: "+str(e))
            should_quit = True
            server_link.teardown()


# This function is called when a link
# has been established with the server
def link_established(link):
    # We store a reference to the link
    # instance for later use
    global server_link
    server_link = link

    # Inform the user that the server is
    # connected
    RNS.log("Link established with server. Hit enter to run BRID test, type to send data, or 'quit' to exit.\n")


# When a link is closed, we'll inform the
# user, and exit the program
def link_closed(link):
    if link.teardown_reason == RNS.Link.TIMEOUT:
        RNS.log("The link timed out, exiting now")
    elif link.teardown_reason == RNS.Link.DESTINATION_CLOSED:
        RNS.log("The link was closed by the server, exiting now")
    else:
        RNS.log("Link closed, exiting now")
    time.sleep(1.5)
    sys.exit(0)


# When a packet is received over the link, we
# simply print out the data.
def client_packet_received(message, packet):
    text = message.decode("utf-8")
    RNS.log("Received data on the link: "+text)
    print("> ", end=" ")
    sys.stdout.flush()


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
            "--interval",
            action="store",
            default=1,
            help="Time between BRID packets in seconds",
            type=float
        )

        parser.add_argument(
            "--packets",
            action="store",
            default=20,
            help="Number of BRID packets to send",
            type=int
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
            server(configarg)
        else:
            if (args.destination == None):
                print("")
                parser.print_help()
                print("")
            else:
                client(args.destination, configarg, args.interval, args.packets)

    except KeyboardInterrupt:
        print("")
        sys.exit(0)


