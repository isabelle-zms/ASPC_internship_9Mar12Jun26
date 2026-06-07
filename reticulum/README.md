# Reticulum
The Reticulum Networking Stack (RNS) is a hardware agnostic cryptography-based network stack designed to build networks that support a large range of data rates (from as low as 5bps). It operates on top of the physical and data link layer, enabling it to work across various transport mediums.

## Purpose
This folder contains scripts, setup notes, and experiments related to using Reticulum for packet communication and LoRa-based networking.

Refer to our [Google Docs](https://docs.google.com/document/d/1JltWomsxRBIPiLrJyV6v5tv5WKGQFqe1Y2CG1Pps34o/edit?usp=sharing) for more detailed information regarding Reticulum, setup, and troubleshooting.

## Contents

- psrt
- pathfinder
- instance_identity_generator.py
- docs
- sandbox

## Tested Environment

The setup and scripts in this folder were tested using:
- OS: Ubuntu 22.04.5 (Linux)
- Python: 3.10.12

## Getting Started

### Software

1. Create a virtual environment (recommended)
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install the Reticulum Python Library
```bash
pip install RNS
```
Refer to the [RNS GitHub Repository](https://github.com/markqvist/Reticulum/tree/master) for more information about the library

### Hardware

Refer to §7.2.2 of the [Reticulum Manual](https://reticulum.network/manual/Reticulum%20Manual.pdf) for the list of supported LoRa boards

3. Set the LoRa board into boot mode
(description)

4. Flash the RNode firmware onto the LoRa board via Terminal
```bash
rnodeconf --autoinstall
```
Select the desired options when prompted.

Something that worked for us is manually resetting the node only when the **first** 'Waiting for ESP32 reset' line shows on the terminal. This should cause the OLED screen to light up and display 'missing config'. Do **not** manually reset the node during subsequent reset prompts, as the process should continue automatically.

Once successful, the OLED screen should display 'TX ready'

## Basic Packet Transceiving
There are several ways to interface with the device:
- MeshChat (locally hosted on PC/laptop) - Not recommended due to usability issues during testing
- NomadNet (locally hosted on PC/laptop terminal)
- Sideband (Android-only app) - Not tested due to lack of Android device
- RNS Python Library

### MeshChat
(description)

### NomadNet
(description)

### RNS Python Library

Refer to the [RNS API documentation](https://reticulum.network/manual/understanding.html) for more functions
(description)



