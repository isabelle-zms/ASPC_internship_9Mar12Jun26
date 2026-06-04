import json
import protobuftest_pb2

drone_data_dict = {
    'id': 'abcd123',
    'lat_long': [1352123, 103819876],
    'battery_voltage': 3,
    'model': 'MODEL_DJI_MINI',
    }

# JSON - 100 bytes

drone_data_json = json.dumps(drone_data_dict).encode("utf-8")
print("JSON: ", len(drone_data_json), "bytes")

# JSON (compact) - 71 bytes

drone_data_compact_dict = {
    'id': 'abcd123',
    'll': [1352123, 103819876],
    'bv': 3,
    'm': 'DJI_MINI',
    }

drone_data_compact_json = json.dumps(drone_data_compact_dict).encode("utf-8")
print("JSON (compact): ", len(drone_data_compact_json), "bytes")

# protobuf - 20 bytes

drone_data_protobuf = protobuftest_pb2.DronePacket()

drone_data_protobuf.id = 'abcd123'
drone_data_protobuf.lat_long.extend([1352123, 103819876])
drone_data_protobuf.battery_voltage = 3
drone_data_protobuf.model = protobuftest_pb2.DronePacket.Model.MODEL_DJI_MINI

drone_data_protobuf_bytes = drone_data_protobuf.SerializeToString()
print("Protobuf:", len(drone_data_protobuf_bytes), "bytes")

# Reults - up to 5x savings!
    # JSON:  100 bytes
    # JSON (compact):  71 bytes
    # Protobuf: 20 bytes

# Whiteboard - Testing out methods

print(drone_data_protobuf.IsInitialized())

msg = protobuftest_pb2.DronePacket()
msg.ParseFromString(drone_data_protobuf_bytes)
print(msg)