Follow the instructions below to set up a RNS Transport node for the pathfinder utility.

Note: To replace <num> and <user> with appropriate values


(1) Setup system files

sudo mv /home/<user>/rns_pathfinder /opt/
sudo chown -R $USER:$USER /opt/rns_pathfinder

/opt/
|-rns_pathfinder/
| |-.venv/ (see step 2)
| |-package<num>/
|   |-main-v2.2.py
|   |-.reticulum_transportInstance/
|   |-identity
|   |-id.txt
|   |-startIdentity
|   |-README.txt
|-...

(2) Create virtual environment

cd /opt/rns_pathfinder
python3 -m venv .venv
source .venv/bin/activate
pip3 install RNS

(3) Edit main-v2.2.py to include absolute path

e.g.,
"identity" --> "/opt/rns_pathfinder/package<num>/identity"

(4) Initialise systemd service

sudo nano /etc/systemd/system/rns_pathfinder.service

===================================================
[Unit]
Description=Reticulum Transport Node

Requires=dev-ttyACM0.device
After=dev-ttyACM0.device

[Service]
Type=simple
User=<user>
WorkingDirectory=/opt/rns_pathfinder/package<num>
ExecStart=/opt/rns_pathfinder/.venv/bin/python3 /opt/rns_pathfinder/package<num>/main-v2.2.py -t -c /opt/rns_pathfinder/package<num>/.reticulum_transportInstance
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
===================================================

^O, Enter, ^X

sudo systemctl daemon-reload
sudo systemctl enable rns_pathfinder.service
sudo systemctl start rns_pathfinder.service

To check the status of the service:
systemctl status rns_pathfinder.service

To boot into console instead of desktop for headless RPi:
sudo raspi-config
1 System Options > S5 Boot / Auto Login > B1 Console / B2 Console Autologin

(5) Disabling the service

sudo systemctl stop rns_pathfinder.service
sudo systemctl disable rns_pathfinder.service
sudo rm /etc/systemd/system/rns_pathfinder.service
sudo systemctl daemon-reload
(optional) sudo systemctl reset-failed

To verify that the service has been disabled:
systemctl status rns_pathfinder.service


