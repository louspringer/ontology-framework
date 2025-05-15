#!/bin/bash

set -euo pipefail

# Check for required commands
for cmd in az jq curl; do
    if ! command -v "$cmd" &> /dev/null; then
        echo "Error: $cmd is required but not installed."
        exit 1
    fi
done

# Install script
echo "Installing VM monitor script..."
sudo cp monitor_vm_scheduled_events.sh /usr/local/bin/
sudo chmod +x /usr/local/bin/monitor_vm_scheduled_events.sh

# Install service
echo "Installing systemd service..."
sudo cp vm-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable vm-monitor.service
sudo systemctl start vm-monitor.service

echo "VM monitor service installed and started."
echo "Check status with: sudo systemctl status vm-monitor.service" 