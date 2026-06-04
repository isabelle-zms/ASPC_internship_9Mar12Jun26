import json
from google.protobuf.json_format import ParseDict
import bridpacket_pb2

with open('BRID_protobuf/bridpackets.json', 'r') as f:
   bridpacket_dict = json.load(f)

# protobuf - 148 bytes

msg_pb = bridpacket_pb2.Packet()    
ParseDict(bridpacket_dict, msg_pb)

msg_bytes = msg_pb.SerializeToString()
print("Protobuf:", len(msg_bytes), "bytes")
print(msg_bytes)

# JSON - 683 bytes

bridpacket_json_bytes = json.dumps(bridpacket_dict).encode('utf-8')
print("JSON:", len(bridpacket_json_bytes), "bytes")