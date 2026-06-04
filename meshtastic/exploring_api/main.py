import meshtastic
import meshtastic.serial_interface
import meshtastic.ble_interface
import meshtastic.protobuf.mesh_pb2
from pubsub import pub
from datetime import datetime
import exploring_api.data_processor as data_processor
import exploring_api.listen_to_channels as listen_to_channels
import exploring_api.config as config
import json
import time

data_200_byte = b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMN'
data_150_byte = b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
data_100_byte = b'012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789ABCDEFGHIJ'

# INTERFACING - To try BLE

ifaceCKT2 = meshtastic.serial_interface.SerialInterface()
print("ifaceCKT2 connected!")
# ifaceCKT1 = meshtastic.serial_interface.SerialInterface('/dev/ttyACM1')
# print("ifaceCKT1 connected!")
# ifaceCKT1 = meshtastic.ble_interface.BLEInterface(address='48:CA:43:5C:45:89', timeout=15)
# print("ifaceCKT1 connected!\n-------------------------------------------")

packets_log = []

# CONFIG SETTINGS - SEE config.py FILE

config.localConfig_lora_working['region'] = 'US'
config.localConfig_lora_working['modem_preset'] = 8
config.config_lora(ifaceCKT2, '!435a0bf4', config.localConfig_lora_working)
time.sleep(23)

ifaceCKT2 = meshtastic.serial_interface.SerialInterface('/dev/ttyACM0')    # reconnect after rebooting
print("ifaceCKT2 connected!")
# ifaceCKT1 = meshtastic.serial_interface.SerialInterface('/dev/ttyACM1')
# print("ifaceCKT1 connected!")

# DATA RATE TESTING (DRT) - Used PRIVATE_APP. Latency as time-base

def drt_receiver(packet, interface):
    global sender_userid; global drt_rx_time
    drt_rx_time_temp = time.perf_counter()                                                  # Record time upon receiving packet
    if packet['fromId'] == sender_userid and packet['decoded']['portnum'] == 'PRIVATE_APP': # Verify identity of packet before confirming rx time
        drt_rx_time = drt_rx_time_temp

def drt_local_test(sender_iface, receiver_iface, drt_data):
    global sender_userid; global drt_tx_time; global drt_rx_time
    sender_userid = sender_iface.getMyUser()['id']
    receiver_userid = receiver_iface.getMyUser()['id']
    pub.subscribe(drt_receiver, 'meshtastic.receive.data')
    drt_tx_time = time.perf_counter()                         # Record time of sending packet
    sender_iface.sendData(drt_data, receiver_userid)
    time.sleep(5)                                             # Allow for latency
    pub.unsubscribe(drt_receiver, 'meshtastic.receive.data')  # Cleanup
    print(f"""
          ------------------------------------
          Latency: {(drt_rx_time - drt_tx_time) * 1000}ms
          Goodput: {(len(drt_data) * 8) / (drt_rx_time - drt_tx_time)}bps
          ------------------------------------
          """)


# Print raw unparsed log line from radio
pub.subscribe(listen_to_channels.log_line, "meshtastic.log.line")
# drt_local_test(ifaceCKT2, ifaceCKT1, data_100_byte)


# PRINTING/DISPLAYING PACKETS

# pub.subscribe(listen_to_channels.display_packet, "meshtastic.receive")
for _ in range(0, 200):
    ifaceCKT2.sendData(data_100_byte, '!435a7004')
    time.sleep(8)

time.sleep(3)
ifaceCKT2.close()
# ifaceCKT1.close()
print("iface closed!")

# 5 Collating packets 

# print(type(packets_log))
# with open('packets.json', 'w') as f:
#     json.dumps(packets_log,f, indent=2, default=str)