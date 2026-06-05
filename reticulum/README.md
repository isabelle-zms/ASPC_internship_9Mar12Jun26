# Reticulum

## Getting Started

### Software

1. Create a virutal environment (optional)
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install RNS
```bash
pip install RNS
```

### Hardware

Refer to §7.2.2 of the [Reticulum Manual](https://reticulum.network/manual/Reticulum%20Manual.pdf) for the list of supported LoRa boards

3. Set the LoRa board into boot mode
(description)

4. Flash the RNode firmware onto the LoRa board via Terminal
```bash
rnodeconf --autoinstall
```
Select the desired options when prompted.

Something that worked for us is manually resetting the node only when the **first** 'Waiting for ESP32 reset' line shows on the terminal. This should result in the OLED screen lighting up and displaying 'missing config'. For subsequent processes, do not manually reset the node as it will do so automatically.

Once successful, the OLED screen should display 'TX ready'



