#!/usr/bin/env bash

# monitor_vm_scheduled_events.sh
# Requires: azure-cli, jq
# Polls Azure Instance Metadata Service for scheduled events on this VM
# and deallocates the VM if a pending poweroff event is detected

set -euo pipefail

# Configuration
RESOURCE_GROUP="CURSOR-IDE-VM-RG"
VM_NAME="cursor-ide-vm"
IMDS_URL="http://169.254.169.254/metadata/scheduledevents?api-version=2020-07-01"
METADATA_HEADER="Metadata:true"
POLL_INTERVAL=30  # seconds

# Logging helper function
echo_ts() {
  echo "$(date -u +'%Y-%m-%dT%H:%M:%SZ') - $*"
}

echo_ts "Starting monitor for scheduled events on VM: $VM_NAME (resource group: $RESOURCE_GROUP)"

while true; do
  # Fetch scheduled events
  payload=$(curl -s -H "$METADATA_HEADER" "$IMDS_URL")
  # Filter for events with status 'Scheduled'
  events=$(echo "$payload" | jq -c '.Events[]? | select(.EventStatus=="Scheduled")')
  if [ -n "$events" ]; then
    echo_ts "Detected scheduled events:"
    echo "$events" | jq
    echo_ts "Mitigating by deallocating VM via Azure CLI"
    az vm deallocate --resource-group "$RESOURCE_GROUP" --name "$VM_NAME"
    echo_ts "Mitigation command issued. Exiting monitor."
    exit 0
  fi
  echo_ts "No pending events. Sleeping for $POLL_INTERVAL seconds."
  sleep "$POLL_INTERVAL"
done
