import time
import json

# Intitialise class Packettracer so that it can be easily plug in into automated script
import time
import json

class PacketTracer:
    def __init__(self, log_name="results.csv"):
        self.ledger = {}
        self.log_name = log_name
        # Create a CSV file with headers
        with open(self.log_name, "w") as f:
            f.write("seq_id,status,latency_ms,rssi,snr\n")

    def create_packet(self, seq_id):
        # return time in milliseconds
        tx_time = int(time.time() * 1000)

        # Store locally
        self.ledger[seq_id] = {"tx_time": tx_time, "status": "SENT"}

        # Return the JSON string to be sent over the radio
        return json.dumps({"seq": seq_id, "ts": tx_time})

    def log_arrival(self, seq_id, tx_time_from_packet, rssi=0, snr=0):
        #Calculate current time in milliseconds
        rx_time = int(time.time() * 1000)

        # Calculate Latency using the timestamp sent inside the packet
        # This ensures it works across two different computers
        latency = rx_time - tx_time_from_packet

        # Save the data to the CSV file
        with open(self.log_name, "a") as f:
            f.write(f"{seq_id},ARRIVED,{latency},{rssi},{snr}\n")

        print(f"SUCCESS: Packet {seq_id} arrived in {latency}ms")