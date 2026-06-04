import meshtastic
import meshtastic.serial_interface
import meshtastic.ble_interface
from pubsub import pub
import argparse
import time

def on_receive(packet, interface):
    decoded = packet.get("decoded")

    if not decoded:
        return

    payload = decoded.get("payload")
    if payload:
        print(f"[SERVER] Received raw bytes: {payload}")
        try:
            print(f"[SERVER] As string: {payload.decode('utf-8')}")
        except:
            print("[SERVER] Payload not UTF-8")

def log_line(line, interface):
    print(line)

def server():
    iface = meshtastic.serial_interface.SerialInterface("/dev/ttyACM0")

    print(iface.getMyNodeInfo()['user']['id'])
    print("[SERVER] Listening...")

    pub.subscribe(on_receive, "meshtastic.receive.text")

    while True:
        time.sleep(1)

def client():
    iface = meshtastic.serial_interface.SerialInterface("/dev/ttyACM1")
    pub.subscribe(log_line, "meshtastic.log.line")


    counter = 0

    print("[CLIENT] Sending Hello...")

    while True:
        # message = f"{counter}xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        time.sleep(15)  
        # iface.sendText(message, destinationId='!435a0bf4')
        # print(f"[CLIENT] Sent {message}")
        # counter += 1

if __name__ == "__main__":
    try:
       parser = argparse.ArgumentParser(description="Packet Success Rate test")

       parser.add_argument("-s", "--server", action="store_true", help="Receiving packets? (server role)")

       args = parser.parse_args()

       if args.server == True:
            server()
       else:
            client()

    except KeyboardInterrupt:
       print("")
       exit()