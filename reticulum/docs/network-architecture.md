# Network Architecture

## Instance, Identities, and Destinations

An instance is the ‘soul’ of the node. It stores Announces, routing tables, identities and other information about the node in that particular session. If the same instance file is used in the future, the session is continued.

There are 2 types of nodes: Instances and Transport nodes. Instances refer to any programme currently running reticulum. Every node runs on an Instance, but not every Instance is a transport node. Only transport nodes are able to route packets (i.e., nodes that are not transport nodes are mainly the sender/receiver nodes). 

An identity is a verifiable entity of a node, much like a person’s identification number. It holds the public and private keys required to encrypt, verify, and authenticate a transaction. Every identity is hence unique. For instance, the Reticulum Protocol is maintained by Mark Qvist, identified by the Reticulum Identity <bc7291552be7a58f361522990465165c>.

A Destination enables a node to send and receive data. There are 4 types of destinations: Plain, Single, Group, and Link. For secure communication between 2 nodes, the Single or Link Destination types are commonly used. More information can be found here.

## Routing

Announces are broadcasted from Destinations across the network using a managed flood routing mechanism. Each node stores a routing table in its cache. Upon receiving an Announce, it stores the Destination from which the Announce was broadcasted from, and the node which it received the Announce from. This enables the node to know its ‘next hop’ if it needs to send/relay a packet to that same Destination.

After these routing tables have been established, forwarding packets becomes efficient, with minimal overhead and packet duplication.

Announces are broadcasted from Destinations regularly, forming a self healing network, albeit with some downtime required to reconstruct outdated path tables.

