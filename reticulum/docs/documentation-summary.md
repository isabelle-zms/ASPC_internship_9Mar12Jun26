# Reticulum API Notes

This document contains brief notes and observations made while exploring the Reticulum (`RNS`) Python library. It is **not a complete API reference**, but rather a collection of functions that were **thought** to be useful during initial stages of exploration.

For official documentation, refer to the [Reticulum manual](https://reticulum.network/manual/Reticulum%20Manual.pdf) and [API documentation](https://reticulum.network/manual/understanding.html).

---

## Basic Setup

Refer to Reticulum's [code examples](https://reticulum.network/manual/examples.html) for more samples. A basic setup would look like:

```python
def program_setup(configpath):
    reticulum = RNS.Reticulum(configpath)
    identity = RNS.Identity()
    destination = RNS.Destination(
        identity,
        RNS.Destination.IN,
        RNS.Destination.SINGLE,
        APP_NAME,
        "minimalsample"
    )
    destination.set_proof_strategy(RNS.Destination.PROVE_ALL)
    runtimeLoop(destination)
```

`configpath`: Path to the Reticulum configuration file. Reticulum uses this file to determine the interfaces, transports, and networking behaviour etc.

## Printing Packet Metadata

```python
my_destination.set_packet_callback(on_rcv)
def on_rcv(message, packet):
    for attr in dir(packet):
      if not attr.startswith("_"):
        try:
          value = getattr(packet, attr)
          print(f"{attr}: {value}")
        except:
          continue
```

<details>
<summary>Full Packet Debug Dump</summary>

```text
ANNOUNCE: 1
CACHE_REQUEST: 8
CHANNEL: 14
COMMAND: 12
COMMAND_STATUS: 13
DATA: 0
ENCRYPTED_MDU: 383
FLAG_SET: 1
FLAG_UNSET: 0
HEADER_1: 0
HEADER_2: 1
HEADER_MAXSIZE: 35
KEEPALIVE: 250
LINKCLOSE: 252
LINKIDENTIFY: 251
LINKPROOF: 253
LINKREQUEST: 2
LRPROOF: 255
LRRTT: 254
MDU: 464
MTU: 500
NONE: 0
PATH_RESPONSE: 11
PLAIN_MDU: 464
PROOF: 3
REQUEST: 9
RESOURCE: 1
RESOURCE_ADV: 2
RESOURCE_HMU: 4
RESOURCE_ICL: 6
RESOURCE_PRF: 5
RESOURCE_RCL: 7
RESOURCE_REQ: 3
RESPONSE: 10
TIMEOUT_PER_HOP: 6
attached_interface: None
context: 0
context_flag: 0
create_receipt: False
data: b"\xae5!\x1d& Z\xb1g\x1e\x1c<go\xfc\xbe\t\xb4\x9bp8]\x15T/\xbe\x15\xd3\x0b\xb9=d\x96N:d\xc6\xc55G\x9e\x1dO\xdf\x81\xeeN\x18\xf7\x8ez\x10\x89\xb0}\xd8\x12\xab\x11\x1c\xea'p\x80\xfdG\xa5\xcc|\xdf\xbb\x8d9\x96\x8f\xdd\xc9~+\x18\x90&\xd0\xbao\x80,\x0e\x1aeN\x04u\xfa\x95M"
destination: <receipt_test.d7e22b752c12f624b3c3a9a1552069a9:015cfee41d8d5fe8c8e50348431d7629>
destination_hash: b'\x01\\\xfe\xe4\x1d\x8d_\xe8\xc8\xe5\x03HC\x1dv)'
destination_type: 0
flags: 0
fromPacked: True
generate_proof_destination: <bound method Packet.generate_proof_destination of <RNS.Packet.Packet object at 0x72346882dd80>>
getTruncatedHash: <bound method Packet.getTruncatedHash of <RNS.Packet.Packet object at 0x72346882dd80>>
get_hash: <bound method Packet.get_hash of <RNS.Packet.Packet object at 0x72346882dd80>>
get_hashable_part: <bound method Packet.get_hashable_part of <RNS.Packet.Packet object at 0x72346882dd80>>
get_packed_flags: <bound method Packet.get_packed_flags of <RNS.Packet.Packet object at 0x72346882dd80>>
get_q: <bound method Packet.get_q of <RNS.Packet.Packet object at 0x72346882dd80>>
get_rssi: <bound method Packet.get_rssi of <RNS.Packet.Packet object at 0x72346882dd80>>
get_snr: <bound method Packet.get_snr of <RNS.Packet.Packet object at 0x72346882dd80>>
header_type: 0
header_types: [0, 1]
hops: 1
pack: <bound method Packet.pack of <RNS.Packet.Packet object at 0x72346882dd80>>
packed: False
packet_hash: b'\x08\x17\xa7\xd4+v\xc1\x00\x8a\xa3\xed6r\xbch\x8f$\xd7Z\x12\x80~\x91t\xa8t\xcb\x1d1\xc1\xc6\x86'
packet_type: 0
prove: <bound method Packet.prove of <RNS.Packet.Packet object at 0x72346882dd80>>
q: 100.0
ratchet_id: None
raw: b"\x00\x00\x01\\\xfe\xe4\x1d\x8d_\xe8\xc8\xe5\x03HC\x1dv)\x00\xae5!\x1d& Z\xb1g\x1e\x1c<go\xfc\xbe\t\xb4\x9bp8]\x15T/\xbe\x15\xd3\x0b\xb9=d\x96N:d\xc6\xc55G\x9e\x1dO\xdf\x81\xeeN\x18\xf7\x8ez\x10\x89\xb0}\xd8\x12\xab\x11\x1c\xea'p\x80\xfdG\xa5\xcc|\xdf\xbb\x8d9\x96\x8f\xdd\xc9~+\x18\x90&\xd0\xbao\x80,\x0e\x1aeN\x04u\xfa\x95M"
receiving_interface: RNodeInterface[RNode LoRa Interface]
resend: <bound method Packet.resend of <RNS.Packet.Packet object at 0x72346882dd80>>
rssi: -64
send: <bound method Packet.send of <RNS.Packet.Packet object at 0x72346882dd80>>
sent_at: None
snr: 12.0
transport_id: None
transport_type: 0
types: [0, 1, 2, 3]
unpack: <bound method Packet.unpack of <RNS.Packet.Packet object at 0x72346882dd80>>
update_hash: <bound method Packet.update_hash of <RNS.Packet.Packet object at 0x72346882dd80>>
validate_proof: <bound method Packet.validate_proof of <RNS.Packet.Packet object at 0x72346882dd80>>
validate_proof_packet: <bound method Packet.validate_proof_packet of <RNS.Packet.Packet object at 0x72346882dd80>>

```
</details>

---

## `RNS.log()`

Used to print logs/messages to the console.

---

## `RNS.Destination`

Represents an endpoint capable of sending and receiving data.

### Common methods

`RNS.Destination.set_proof_strategy(RNS.Destination.PROVE_ALL)`: Sets proofs (similar to ACKs). `PROVE_ALL` requests delivery proofs whenever possible.
`RNS.Destination.set_packet_callback(callback)`: Sets callback when packet is received

---

## `RNS.Link`

Represents a secure connection between two destinations.

### Common methods

`RNS.Link(server_destination)`: Creates a link to a destination

`RNS.Link.set_link_closed_callback(callback)`: Triggers a callback when the link closes

`RNS.Link.get_channel().send(message)`: Sends a message through the link channel

`RNS.Link.teardown()`: Terminates the link

`RNS.Link.request(...)`: Used for request-response style communication.

---

## `RNS.MessageBase`

Parent class for custom message types.

Any message type intended for transmission should subclass `RNS.MessageBase`.

Requirements:

* subclasses must define `MSGTYPE`
* `MSGTYPE >= 0xf000`

---

## `RNS.Channel.Channel`

Handles message transport over a link.

### Common methods

`RNS.Channel.Channel.MDU()`: Returns the **Maximum Data Unit (MDU)**.

This is smaller than `RNS.Link.get_mdu()` which does not account for message headers

`RNS.Channel.Channel.register_message_type()`: Registers a message type so it can be sent over the link.

`RNS.Channel.Channel.add_message_handler()`: Adds callback handlers for incoming messages. Multiple handlers can be registered.

* returns `True` → message handled, processing stops
* returns `False` → message passed to next handler

`RNS.Channel.Channel.is_ready_to_send()`: Checks whether the channel is ready for transmission.

---



