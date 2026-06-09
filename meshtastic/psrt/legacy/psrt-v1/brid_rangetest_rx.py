import meshtastic
import meshtastic.serial_interface
from pubsub import pub
from threading import Event
import bridpacket_pb2

ifaceRX = meshtastic.serial_interface.SerialInterface('/dev/ttyACM0')
print(f'ifaceRX connected!')

reply_ack = Event()
reply_num_packets_rx = Event()
num_packets_rx = 0
num_packets_sent = None


def check_rcv_packet(packet, interface):
    if packet.get('decoded', None) != None:
        try:
            packet_pb = bridpacket_pb2.Packet()
            packet_pb.ParseFromString(packet['decoded']['payload'])
        except:
            return
        global num_packets_rx
        num_packets_rx += 1
        print(f'Received 1 BRID packet (Total: {num_packets_rx})')
        # log the packet


def check_rcv_init(packet, interface):
    if packet.get('decoded', None) != None:
        if packet['decoded']['text'] == 'Want to start BRID packet test. Awaiting acknoledgement.':
            reply_ack.set()
            print(f"{packet['fromId']} wants to initialise BRID packet test. Sending ACK.")


def check_end_test(packet, interface):
    if packet.get('decoded', None) != None:
        if packet['decoded']['text'][:18] == "Sent BRID packets:":
            global num_packets_sent
            num_packets_sent = int(packet['decoded']['text'][19:])
            reply_num_packets_rx.set()
            print('Test ended. Awaiting test results.')


def rcv_brid_packets(tx_nodeid):
    pub.subscribe(check_rcv_init, 'meshtastic.receive.text')
    if reply_ack.wait(timeout=100):
        pub.unsubscribe(check_rcv_init, 'meshtastic.receive.text')
        pub.subscribe(check_rcv_packet, 'meshtastic.receive.data')
        pub.subscribe(check_end_test, 'meshtastic.receive.text')
        ifaceRX.sendText('ACK. Start sending.', tx_nodeid)
        if reply_num_packets_rx.wait(timeout=300):
            ifaceRX.sendText(f'Received BRID packets: {num_packets_rx}', tx_nodeid)
            print(f"""
                  ----------------------------------------
                  Test Summary
                  Packets sent: {num_packets_sent}
                  Packets received: {num_packets_rx}
                  Success rate: {(num_packets_rx/num_packets_sent) * 100}%
                  ----------------------------------------435a0bf4
                  """)
        else:
            print(f'Is {tx_nodeid} still alive?')
    else:
        print(f"""
              Did not receieve init from {tx_nodeid}. Check 
              (1) Are the modem presets of the node the same?
              (2) Are the nodes too far?
              (3) Are the nodes both positoned in the same orientation?
              """)
        
rcv_brid_packets('!435a0bf4')