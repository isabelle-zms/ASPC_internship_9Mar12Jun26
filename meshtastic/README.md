# Meshtastic
Meshtastic is a 100% community driven, open source project that enables people to use inexpensive LoRa radios as a long range off-grid communication platform in areas without existing or reliable communications infrastructure.

## Purpose
This folder contains scripts, setup notes, and experiments related to using Meshtastic for packet communication and LoRa-based networking.

Refer to our [Google Docs](https://docs.google.com/document/d/1N2Y8lTuXaiwdwQeVuWp74Q3Yi5RGU71jlhOCv5_Ac9s/edit?usp=sharing) for more detailed information regarding Meshtastic, setup, and troubleshooting.

## Contents

```text
meshtastic/
├── README.md
├── psrt/       # Packet success rate test
├── docs/       # Infodump 
│   ├── other_method_info.txt      # Meshtastic Python API methods
│   ├── packets.txt                # Packet structures for various Meshtastic packets
│   └── our_nodes.txt              # (outdated) list of Meshtastic nodes
└── sandbox/    # Exploratory scripts and misc testing   
    ├── exploring-api/             # Random code that explores methods in the API
    └── minimal_client_server.py   # Minimal TX RX code used for troubleshooting

```

## Tested Environment

The setup and scripts in this folder were tested using:
- OS: Ubuntu 22.04.5 (Linux)
- Python 3.10.12
- Meshtastic Firmware ≥ 2.6.10 (Beta versions)

## Getting Started

### Software

1. Create a virtual environment (recommended)
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install the Meshtastic Python Library
```bash
pip install meshtastic
```
Refer to the [Meshtastic API Documentation](https://python.meshtastic.org/index.html) for more information about the library

### Hardware

LilyGo T-Beam Supreme boards should come pre-flashed with the firmware. Power on the node if unsure.

3. Set the LoRa board into boot mode

(description)

4. Flash the firmware onto the LoRa board via Meshtastic Web Flasher

Open the [Meshtastic Web Flasher](https://flasher.meshtastic.org/) in Chrome.

Select the desired options when prompted. 

If the device does not power on after 'Hard resetting via RTS pin' is shown, manually reset the node by pressing the RST button. Once successful, the OLED screen should display the Meshtastic UI.

### Interfacing
Methods to interface with the device:
- Meshtastic App (iOS/Android)
- Web Client (Desktop)
- Meshtastic Python API
- Meshtastic CLI



