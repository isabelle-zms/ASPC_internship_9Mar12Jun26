# Packet Success Rate Test (PSRT) — Meshtastic

A tool for measuring packet delivery success rate between two Meshtastic nodes over LoRa. The transmitter (client) sends structured BRID packets serialised with Protocol Buffers; the receiver (server) identifies, parses, and logs them to CSV for analysis.

---

## Contents

| File | Description |
|---|---|
| `psrt_manual_auto.py` | Main script — runs as either client or server |
| `bridpacket_ts_pb2.py` | Generated protobuf module for the `Packet` message type |
| `bridpackets_ts.json` | Pool of pre-defined packet payload templates (without timestamps/IDs) |
| `brid_packets_meshtastic.csv` | Output CSV (created on first server run) |

---

## Requirements

**Hardware:**
- Two Meshtastic-compatible LoRa nodes connected over serial (e.g. `/dev/ttyACM0`, `/dev/ttyACM1`)
- Nodes configured on the same Meshtastic channel/modem preset

**Python dependencies:**

- meshtastic
- pypubsub
- tqdm
- protobuf


Install with:
```bash
pip install meshtastic pypubsub tqdm protobuf
```

---

## How It Works

Each BRID packet is a protobuf-serialised `Packet` message prefixed with the 4-byte magic `BRID`. The client selects a random payload template from `bridpackets_ts.json`, stamps it with a sequential `packet_id` and a Unix `timestamp`, serialises it, and transmits it via `sendData()` to the server node ID.

The server subscribes to incoming data packets. On receipt, it checks for the `BRID` magic prefix to filter out non-BRID traffic, parses the protobuf payload, and appends a row to the CSV with packet ID, SNR, transmit time, receive time, and hop count. This data can be used to calculate packet success rate, latency, and link quality offline.

---

## Usage

### Server
Start the receiver on the listening node. Logs incoming BRID packets to CSV. Press **Enter** to reset the running packet count; **Ctrl+C** to exit.

```bash
python3 main_v2.2.py -p /dev/ttyACM0 -f brid_packets_meshtastic.csv
```

Monitor the CSV live in a separate terminal:
```bash
tail -f brid_packets_meshtastic.csv
```

### Client — Auto mode
Send `n` packets to the server at a fixed interval.

```bash
python3 main_v2.2.py -c -p /dev/ttyACM1 -a -i <interval_s> -n <num_packets> <server_node_id>
```

Example — 400 packets, 1-second interval:
```bash
python3 main_v2.2.py -c -p /dev/ttyACM1 -a -i 1 -n 400 '!435a0bf4'
```

### Client — Manual mode
Send packets interactively. Press **Enter** to send one random BRID packet; type any text to send it as raw UTF-8; type `quit` to exit.

```bash
python3 main_v2.2.py -c -p /dev/ttyACM1 '!435a0bf4'
```

### Full argument reference

| Argument | Default | Description |
|---|---|---|
| `-p / --port` | *(required)* | Serial port of the Meshtastic device |
| `-c / --client` | off | Run as client (transmitter); omit to run as server |
| `-f / --csv_file` | `brid_packets_meshtastic.csv` | CSV output path (server only) |
| `-a / --auto` | off | Enable automatic transmission (client only) |
| `-i / --interval` | `5` | Seconds between packets in auto mode |
| `-n / --num_packets` | `100` | Number of packets to send in auto mode |
| `destination` | — | Server node ID, e.g. `!435a0bf4` (client only) |
