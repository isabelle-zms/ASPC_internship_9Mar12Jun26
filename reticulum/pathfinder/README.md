# RNS Pathfinder

This guide covers how run the pathfinder module to obtain the path of packets in a network, provided the user has access to all the nodes involved

## Contents
The contents of this folder are as follows:
```text
pathfinder/
├── README.md
├── main-v2.2.py
├── endIdentity
├── startIdentity
│
├── v2-identities/
│   ├── set1/
│   │   ├── identity
│   │   └── transport_identity
│   ├── set2/
│   │   ├── identity
│   │   └── transport_identity
│   ├── ... (more sets)
│      
└── packages/
    ├── requirements.txt
    ├── package1/
    │   ├── README.txt
    │   ├── main-v2.2.py
    │   ├── id.txt
    │   ├── identity
    │   └── startIdentity
    ├── ... (more packages)    

```
`pathfinder/`: to be downloaded on start and end node

`pathfinder/main-v2.2.py`: to be ran by start and end node

`endIdentity`, `startIdentity`: Identities of start and end nodes

`v2-identities/`: Collection of identity and transport identities of intermediate nodes

`packages/`: Collection of directories to be downloaded on each intermediate node (i.e., 1 node 1 package)

---

## Requirements
- python
- RNS

---

## How It Works
This script implements an active path tracing tool for Reticulum networks. It discovers and logs the sequence of transport nodes between a start node and a designated end node, measuring traversal time along the way.

### Architecture
The script operates across three distinct node roles, each run as a separate instance:

#### Start node (-s)
Initiates the trace. It resolves the target destination hash via Transport.request_path, identifies the first next hop from the local path table, then sends a path-query packet to that hop's destination. As responses return, it appends each hop's ID to a running path list and dispatches the next query, continuing until the target hash is reached. Results are printed with total elapsed time.

#### Intermediate/transport node (-t)
Listens on a fixed identity and destination. On receiving a query packet, it performs its own has_path lookup for the target, reads the next hop from its local path table, and sends a response packet back to the start node containing its node ID and the next hop's identity hash. This repeats at every transport node along the path.

#### End node (-e)
A passive listener that simply logs received packets. Its destination hash is the target the start node is tracing toward.

### Key Details

- Identity mapping: The start node maintains a directory of transport node identities, mapping each node's transport identity hash to its corresponding destination identity file. This is used to address query packets to the correct next hop.
- Reliability: Packets are sent with configurable retransmission attempts and receipt-acknowledgement timeouts (PROVE_ALL proof strategy).
- Path queries are application-layer: The trace logic is entirely above the RNS transport layer — transport nodes participate by running this script, not by virtue of their routing role alone.

---

## Usage

End node (run first, note the destination hash)
```bash
python pathfinder.py -e -c /path/to/rns/config
```

Intermediate nodes (one per transport hop)
```bash
python pathfinder.py -t -c /path/to/rns/config
```

Start node
```bash
python pathfinder.py -s -c /path/to/rns/config -i /path/to/identities/ -d <target_hex_hash>
```
---

## Troubleshooting



