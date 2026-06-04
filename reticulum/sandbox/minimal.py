import RNS
import time
import sys

APP_NAME = "receipt_test"


class Receiver:
    def __init__(self, config=None):
        self.rns = RNS.Reticulum(config)

        self.identity = RNS.Identity()

        self.destination = RNS.Destination(
            self.identity,
            RNS.Destination.IN,
            RNS.Destination.SINGLE,
            APP_NAME
        )

        # IMPORTANT
        self.destination.set_proof_strategy(
            RNS.Destination.PROVE_ALL
        )

        self.destination.set_packet_callback(
            self.packet_received
        )

        print("\nReceiver ready")
        print("Destination hash:")
        print(self.destination.hash.hex())

        while True:
            entered = input()
            self.destination.announce()
            RNS.log("Sent announce from "+RNS.prettyhexrep(self.destination.hash))

    def packet_received(self, message, packet):
        for attr in dir(packet):
            if not attr.startswith("_"):
                try:
                    value = getattr(packet, attr)
                    print(f"{attr}: {value}")
                except:
                    continue
        print(f"\nReceived: {message.decode('utf-8')}")

class Sender:
    def __init__(self, config=None):
        self.rns = RNS.Reticulum(config)
        self.identity = RNS.Identity()

    def send_packet(self, target_hexhash):
        target_hash = bytes.fromhex(target_hexhash)

        if not RNS.Transport.has_path(target_hash):
            RNS.log("Destination is not yet known. Requesting path and waiting for announce to arrive...")
            RNS.Transport.request_path(target_hash)
            while not RNS.Transport.has_path(target_hash):
                time.sleep(0.1)

        target_identity = RNS.Identity.recall(bytes.fromhex(target_hexhash))
        target_destination = RNS.Destination(
            target_identity,
            RNS.Destination.OUT,
            RNS.Destination.SINGLE,
            APP_NAME
        )
        while True:
            receipt = RNS.Packet(target_destination, "Hello".encode('utf-8')).send()
            receipt.set_timeout(10)
            receipt.set_delivery_callback(self.on_packet_delivered)
            receipt.set_timeout_callback(self.on_packet_timeout)

            time.sleep(20)
    
    def on_packet_delivered(self, r):
        print("Packet delivered")

    def on_packet_timeout(self, r):
        print("Delivery unsuccessful")

if __name__ == "__main__":
    config = sys.argv[1]
    if len(sys.argv) == 2:
        receiver = Receiver(config)
    elif len(sys.argv) == 3:
        sender = Sender(config)
        sender.send_packet(sys.argv[2])

    