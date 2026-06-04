import meshtastic
import exploring_api.data_processor as data_processor
import time

# TOPIC: meshtastic.log.line
def log_line(line=None, interface=None):
    print(line)

# TOPIC: meshtastic.receive

def print_packet(packet, interface) -> None:
    """ Prints the raw form of the packet, including the __str__ representation of the protobuf object"""
    print("=" * 70)
    print(packet)
    print("=" * 70)


def display_packet(packet, interface) -> None:
    """Processes and prints packet details in a readable format"""
    rcv_time = time.time()

    # Sender & Receiver Info - Battery, Range etc
    sender = packet['fromId']
    receiver = packet['toId']

    # RSSI, SNR
    if packet.get('rxRssi', None) != None:
        # packets from the node itself will not have rssi and snr
        rssi, snr = packet['rxRssi'], packet['rxSnr']
    else:
        rssi, snr = '-', '-'

    # Encrypted or not?
    if packet.get('decoded', None) != None:
        
        packet_decoded = packet['decoded']
        payload_byte_size = len(packet_decoded['payload'])

        # Info based on commonly seen portnums
        if packet_decoded['portnum'] == 'TELEMETRY_APP':
            packet_type = 'TELEMETRY_APP'
            message_info = data_processor.remove_raw(packet_decoded['telemetry'])
        elif packet_decoded['portnum'] == 'ROUTING_APP':
            packet_type = 'ROUTING_APP'
            if packet_decoded['routing']['errorReason'] == 'NONE':
                message_info = 'Routing Successful'
            else:
                message_info = packet_decoded['routing']['errorReason']
        elif packet_decoded['portnum'] == 'POSITION_APP':
            packet_type = 'POSITION_APP'
            message_info = data_processor.remove_raw(packet_decoded['position'])
        elif packet_decoded['portnum'] == 'TEXT_MESSAGE_APP':
            packet_type = 'TEXT_MESSAGE_APP'
            message_info = packet_decoded['text']
        elif packet_decoded['portnum'] == 'PRIVATE_APP':
            packet_type = 'PRIVATE_APP'
            message_info = packet_decoded['payload']
        elif packet_decoded['portnum'] == 'RANGE_TEST_APP':
            packet_type = 'RANGE_TEST_APP'
            message_info = packet_decoded['payload']
        else:
            packet_type = packet_decoded['portnum']
            message_info = '(NEW PORTNUM, unable to process)'

        # Summary
        print(f"""
            -------------
            PACKET RECEIVED at {rcv_time}!
            Start & End: From {sender} to {receiver}
            RSSI: {rssi}dBm ({data_processor.rssi_level(rssi)})
            SNR: {snr}dB ({data_processor.snr_level(snr)})
            
            Packet type: {packet_type}
            Message info: {message_info}
            Payload bits: {payload_byte_size * 8} bits
            -------------

            """)
    
    else:
        print(f"""
            
            -------------
            PACKET RECEIVED at {rcv_time}!
            Start & End: From {sender} to {receiver}
            RSSI: {rssi}dBm ({data_processor.rssi_level(rssi)})
            SNR: {snr}dB ({data_processor.snr_level(snr)})
            
            (Encrypted message, unable to decrypt)
            -------------
            
            """)