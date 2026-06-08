import json
from google.protobuf.json_format import ParseDict
from google.protobuf.json_format import MessageToJson
import bridpacket_pb2

with open('bridpackets.json', 'r') as f:
   bridpacket_dict = json.load(f) # obtain dictionary containing data from the JSON file

# protobuf - 148 bytes
# Converted dictionary --> protobuf message --> bytes
# There are alternative methods to convert JSON --> protobuf message, though not demonstrated here

msg_pb = bridpacket_pb2.Packet()    
ParseDict(bridpacket_dict, msg_pb)

msg_bytes = msg_pb.SerializeToString()
print("Protobuf:", len(msg_bytes), "bytes")
print(msg_bytes)

# Converted bytes --> protobuf message --> JSON to verify the integrity of the data after conversion
msg_pb2 = bridpacket_pb2.Packet()
msg_pb2.ParseFromString(msg_bytes)
bridpacket_json = MessageToJson(msg_pb2)

# JSON - 683 bytes

bridpacket_json_bytes = json.dumps(bridpacket_dict).encode('utf-8')
print("JSON:", len(bridpacket_json_bytes), "bytes")