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



