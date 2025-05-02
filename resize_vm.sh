#!/bin/bash
# resize_vm.sh
# Safely deallocate, resize, and restart an Azure VM (Spot or regular)
# Usage: ./resize_vm.sh <resource-group> <vm-name> [<target-size>]
# Example: ./resize_vm.sh CURSOR-IDE-VM-RG cursor-ide-vm Standard_D4s_v3

set -e

RESOURCE_GROUP=${1:-CURSOR-IDE-VM-RG}
VM_NAME=${2:-cursor-ide-vm}
TARGET_SIZE=${3:-Standard_D4s_v3}

if ! command -v az &>/dev/null; then
  echo "Azure CLI (az) not found. Please install it first."
  exit 1
fi

# Check current size
CURRENT_SIZE=$(az vm show --resource-group "$RESOURCE_GROUP" --name "$VM_NAME" --query hardwareProfile.vmSize -o tsv)
echo "Current VM size: $CURRENT_SIZE"
if [ "$CURRENT_SIZE" == "$TARGET_SIZE" ]; then
  echo "VM is already at target size $TARGET_SIZE. Exiting."
  exit 0
fi

# Deallocate VM
az vm deallocate --resource-group "$RESOURCE_GROUP" --name "$VM_NAME"

# Resize VM
az vm resize --resource-group "$RESOURCE_GROUP" --name "$VM_NAME" --size "$TARGET_SIZE"

# Start VM
az vm start --resource-group "$RESOURCE_GROUP" --name "$VM_NAME"

echo "Resize complete. VM $VM_NAME is now running with size $TARGET_SIZE." 