# RNS Packet Success Rate Tester

A Reticulum Network Stack (RNS) utility for measuring packet success rate (i.e., % delivery) across a client–server path. Packets are sent at fixed intervals; the server logs each received packet's metadata to CSV for offline analysis.

---

## Contents

```
psrt/
├── README.md
├── main.py        # Main script (client + server modes)
├── bridpackets_ts.json      # Payload templates (without timestamps/IDs)
├── bridpacket_ts_pb2.py     # Compiled protobuf bindings for Packet message
├── bridpacket_ts.proto      # Protobuf schema (source)
├── serverIdentity           # Pre-generated RNS identity file for the server
└── brid_packets_reticulum.csv  # Output CSV (created on first server run)
```

---

## Requirements

- Python
- RNS
- protobuf (for compiled bindings)
- tqdm
- protoc (**only** if regenerating _pb2.py file)

Install dependencies:

```bash
pip install rns protobuf tqdm
```

---

## How It Works

The **server** announces a `SINGLE` destination under the `reticulum_test::multinode_test` namespace and listens for raw packets. Each received packet is decoded from a length-prefixed protobuf payload (magic bytes `BRID`), and the packet ID, RSSI, SNR, TX timestamp, and RX timestamp are appended to a CSV file.

The **client** resolves a path to the server destination hash, then sends `N` packets at a fixed interval. Each packet wraps a random payload drawn from `bridpackets_ts.json`, stamped with a packet ID and the current Unix timestamp, serialised as protobuf, and prefixed with the `BRID` magic bytes before dispatch.

Packet success rate can be derived post-hoc by comparing the number of rows in the CSV against the number of packets sent.

---

## Usage

### Server

```bash
python main.py -s [--config <rns_config_dir>] [--csv_file <output.csv>]
```

On startup the server prints its destination hash. Hit **Enter** at any time to announce destination.

### Client

```bash
python main.py <destination_hash> \
    [--config <rns_config_dir>] \
    [--interval <seconds>] \
    [--num_packets <count>]
```

| Argument | Default | Description |
|---|---|---|
| `destination` | *(required)* | Hex hash of the server destination |
| `--config` | RNS default | Path to alternative RNS config directory |
| `--csv_file` | `brid_packets_reticulum.csv` | Output file (server only) |
| `--interval` | `1.0` | Seconds between packets |
| `--num_packets` | `100` | Total packets to transmit |

### Example

```bash
# Node A — server
python3 main.py -s --config .reticulum_serverInstance --csv_file brid_packets_reticulum.csv

# Node B — client (replace hash with actual server destination hash)
python3 main.py a1b2c3d4e5f6a1b2 --config .reticulum_clientInstance --interval 1 --num_packets 400
```
