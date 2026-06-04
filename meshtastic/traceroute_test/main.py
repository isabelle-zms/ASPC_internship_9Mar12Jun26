import meshtastic.serial_interface
from pubsub import pub
import json
import time
from packettracer import PacketTracer

#Import PacketTracer Class before using this code.

#Initialise PacketTracer in meshtastic testing environment
tracer = PacketTracer("meshtastic_test.csv")

def onReceive(packet, interface):
    try:
        #Check if the radio signal actually contains text
        if 'decoded' in packet and packet['decoded']['portnum'] == 'TEXT_MESSAGE_APP':

            #Unpack information from the radio
            data = json.loads(packet['decoded']['text'])

            #Obtain info that we need i.e. sequence identifier and timestamp
            seq_id = data['seq']
            timestamp = data['ts']

            #Obtain signal strength (RSSI) and quality (SNR)
            rssi = packet.get('rssi', 0)
            snr = packet.get('snr', 0) # Added SNR since your class supports it

            #Log the arrival by collecting seq_id and the timestamp
            tracer.log_arrival(seq_id, timestamp, rssi, snr)

    except Exception as e:
        print(f"Error decoding: {e}")

#Pubsub runs when a radio packet is heard
interface = meshtastic.serial_interface.SerialInterface()
pub.subscribe(onReceive, "meshtastic.receive")

print("Meshtastic is listening... Press Ctrl+C to stop.")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Test stopped by user.")
    interface.close()