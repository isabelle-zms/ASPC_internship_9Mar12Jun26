import meshtastic
import meshtastic.serial_interface
from pubsub import pub
from threading import Event
import random
import time

ifaceTX = meshtastic.serial_interface.SerialInterface('/dev/ttyACM1')
print('ifaceTX connected!')

rcved_ack = Event()
rcved_num_packets_rx = Event()
num_packets_rx = None


def check_whether_acknoledged(packet, interface):
    if packet.get('decoded', None) != None:
        if packet['decoded']['text'] == 'ACK. Start sending.':
            rcved_ack.set()
            print(f"ACK received from {packet['fromId']}. Initiating BRID packet test in 3 seconds.")


def obtain_num_packets_rx(packet, interface):
    if packet.get('decoded', None) != None:
        if packet['decoded']['text'][:22] == "Received BRID packets:":
            global num_packets_rx
            num_packets_rx = int(packet['decoded']['text'][23:])
            rcved_num_packets_rx.set()


def send_brid_packets(rx_nodeid, interval, num_packets, packet_list):
    pub.subscribe(check_whether_acknoledged, 'meshtastic.receive.text')
    ifaceTX.sendText('Want to start BRID packet test. Awaiting acknoledgement.', rx_nodeid)
    print('Text sent')
    if rcved_ack.wait(timeout=100):
        pub.unsubscribe(check_whether_acknoledged, 'meshtastic.receive.text')
        time.sleep(3)
        for _ in range(num_packets):
            ifaceTX.sendData(random.choice(packet_list), rx_nodeid)
            time.sleep(interval)
        print(f'Finished sending {num_packets} BRID packets. Awaiting test results.')
        
        pub.subscribe(obtain_num_packets_rx, 'meshtastic.receive.text')
        ifaceTX.sendText(f'Sent BRID packets: {num_packets}', rx_nodeid)
        if rcved_num_packets_rx.wait(timeout=30):
            pub.unsubscribe(obtain_num_packets_rx,'meshtastic.receive.text')
            print(f"""
                  ----------------------------------------
                  Test Summary
                  Packets sent: {num_packets}
                  Packets received: {num_packets_rx}
                  Success rate: {(num_packets_rx/num_packets) * 100}%
                  ----------------------------------------
                  """)
            ifaceTX.sendText(f'Test Summary\nPackets sent: {num_packets}\nPackets received: {num_packets_rx}\nSuccess rate: {(num_packets_rx/num_packets) * 100}%', rx_nodeid)
        else:
            print(f"Is {rx_nodeid} still alive?")
    else:
        print(f"""
              Did not receieve ACK from {rx_nodeid}. Check 
              (1) Are the modem presets of the node the same?
              (2) Are the nodes too far?
              (3) Are the nodes both positoned in the same orientation?
              """)
        
send_brid_packets('!435a7004', 3, 20, [b'\n\x03BLE\x12\x1170:04:1D:34:1A:62\x18\xb3\xff\xff\xff\xff\xff\xff\xff\xff\x01 \xff\xff\xff\xff\xff\xff\xff\xff\xff\x01(\xf0\xc2\xc5:0\x01B]\n\x12\x18\x01"\x0e18099470000022\n\x02\x08\x01\x12+\x11F\xce\xc2\x9ev\xb8\xf5?\x19b\xbe\xbc\x00\xfb\xffY@%\x00\x008A-\x00\x00\x04B5\x00\x00\x00\xbfM\x00\x00\xd4BU3\xc3\xd6D\x1a\x14\r\xac\xc5\xa7:%\x00\x00z\xc4-\x00\x00z\xc45\x00\x00z\xc4"\x00'])
