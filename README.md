# Internship @ ASPC
By: Amanda, Isabelle

Internship period: 9 March 2026 - 12 June 2026

## Overview

A collection of scripts used in the comparative study of **Meshtastic** and **Reticulum** as data communication frameworks, as well as audio data samples for ML-based acoustic drone detection. 

## Contents

```text
ASPC_intership_9Mar12Jun26/
├── README.md
├── meshtastic/       # Experiments, configs, and results for Meshtastic
├── reticulum/        # Experiments, configs, and results for Reticulum
├── audio-ml/         # Data and scripts for Audio ML
├── sandbox/          # Exploratory scripts and misc testing
└── .gitignore
```

## Evaluation of LoRa for Data Transmission

Given the congestion of 2.4G and 5G RF bands, we set out to investigate the use of LoRa for data communication. We conducted our evaluation of LoRa using 2 open sourced projects: Meshtastic and Reticulum. The goal was to evaluate both platforms across key criteria, e.g. range, reliability, ease of deployment, throughput to inform a recommendation for data transmission.

A potential application is integration with current (B-RID) drone detectors to pipe data back to C3.

### Hardware Obtained

| Item | Quantity |
|---|---|
|LilyGo T-Beam Supreme</br>- LoRa Board</br>- Antenna|10|
|18650 battery|10|
|Heltec V4</br>- LoRa Board</br>- PL103665 LiPo Battery</br>- Antenna</br>- Casing|10|

### Documentation
The full comparative analysis, methodology, and results are documented in our [internship report](https://docs.google.com/document/d/1Z2ekmuAbnOseC_cCQgHusvXq2A4mMfuY6v65CTh2FUU/edit?usp=sharing). Other resources can be found in our [Google Drive folder](https://drive.google.com/drive/folders/1LHXuSWY_SENn9mCLYkU4nrk7pCBYPJd9?usp=share_link)

## Audio Data Collection for Acoustic Drone Detection
Collection of scripts and samples for the future development of an acoustics based drone detector.

## Other Tasks
Not included in this repo. Can be found in our [Google Drive folder](https://drive.google.com/drive/folders/1LHXuSWY_SENn9mCLYkU4nrk7pCBYPJd9?usp=share_link).

### Vector Network Analyser (VNA)
Explored the use of a VNA. Picked up related concepts such as impedance, S parameters, VSWR. Used the LiteVNA-64 to measure the S11, SWR and impedance of various antennas around the office. Measurements can be found [here](https://docs.google.com/spreadsheets/d/103Whadzx_50aWbKvtKXVo7ni8isa0EALrPEQ06344X8/edit?usp=sharing).

### Research on Evolution of Drone Technology and Interceptor Drones
Conducted brief research on the improvements of drone technology over the years. Additionally, summarised the recent interceptor drone models, generalising the prominent form factors and potential developments. Slides can be found [here](https://drive.google.com/drive/folders/161BoR6qGMTu0a-nFHKk7SIjMiQSpGYZg?usp=drive_link).



