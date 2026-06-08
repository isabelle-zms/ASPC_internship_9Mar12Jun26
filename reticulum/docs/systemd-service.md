# Systemd Service Setup

This guide covers how to create and manage a `systemd` service that automatically starts on boot.

---

## 1. Create the Service File

Create and open a new `.service` file in `/etc/systemd/system/`:

```bash
sudo nano /etc/systemd/system/rns_pathfinder.service
```

Paste the following configuration, editing the fields marked with `< >` to match your setup:

```ini
[Unit]
Description=Reticulum Transport Node
Requires=dev-ttyACM0.device
After=dev-ttyACM0.device

[Service]
Type=simple
User=<user>
WorkingDirectory=/opt/rns_pathfinder/package<num>
ExecStart=/opt/rns_pathfinder/.venv/bin/python3 /opt/rns_pathfinder/package<num>/main-v2.2.py \
    -t -c /opt/rns_pathfinder/package<num>/.reticulum_transportInstance
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Save and exit: `Ctrl+O`, `Enter`, `Ctrl+X`

---

## 2. Enable and Start the Service

Reload systemd to register the new service, then enable and start it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable rns_pathfinder.service
sudo systemctl start rns_pathfinder.service
```

---

## 3. Check Service Status

```bash
systemctl status rns_pathfinder.service
```

---

## 4. (Optional) Configure Headless Boot on Raspberry Pi

To boot into the console instead of the desktop environment:

```bash
sudo raspi-config
```

Navigate to: **1 System Options → S5 Boot / Auto Login → B1 Console** (or **B2 Console Autologin**)

---

## Disabling and Removing the Service

To stop, disable, and remove the service entirely:

```bash
sudo systemctl stop rns_pathfinder.service
sudo systemctl disable rns_pathfinder.service
sudo rm /etc/systemd/system/rns_pathfinder.service
sudo systemctl daemon-reload
sudo systemctl reset-failed  # optional: clears any failed state
```

Verify the service has been removed:

```bash
systemctl status rns_pathfinder.service
```
