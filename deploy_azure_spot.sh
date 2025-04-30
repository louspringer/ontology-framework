#!/bin/bash

set -e  # Exit on any error

# Configuration
RESOURCE_GROUP="pdf-processor-rg"
LOCATION="southeastasia"
VM_NAME="pdf-processor-vm"
VM_SIZE="Standard_D2s_v3"
ADMIN_USERNAME="azureuser"
VM_IMAGE="Canonical:0001-com-ubuntu-server-jammy:22_04-lts:latest"
ACR_NAME="pdfprocessor1234"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for required commands
for cmd in az ssh-keygen ssh-keyscan scp; do
    if ! command_exists "$cmd"; then
        echo "Error: $cmd is required but not installed."
        exit 1
    fi
done

echo "Cleaning up existing resources..."
if az group exists --name "$RESOURCE_GROUP" --output tsv | grep -q "true"; then
    echo "Deleting existing resource group..."
    if ! az group delete --name "$RESOURCE_GROUP" --yes; then
        echo "Error: Failed to delete resource group"
        exit 1
    fi
    echo "Waiting for cleanup to complete..."
    sleep 30
fi

echo "Generating SSH key..."
if ! ssh-keygen -t rsa -b 4096 -f ~/.ssh/pdf-processor-vm_key -N ""; then
    echo "Error: Failed to generate SSH key"
    exit 1
fi

echo "Creating resource group..."
if ! az group create --name "$RESOURCE_GROUP" --location "$LOCATION"; then
    echo "Error: Failed to create resource group"
    exit 1
fi

echo "Creating spot VM..."
if ! az vm create \
    --resource-group "$RESOURCE_GROUP" \
    --name "$VM_NAME" \
    --image "$VM_IMAGE" \
    --size "$VM_SIZE" \
    --admin-username "$ADMIN_USERNAME" \
    --ssh-key-values ~/.ssh/pdf-processor-vm_key.pub \
    --priority Spot \
    --eviction-policy Deallocate; then
    echo "Error: Failed to create VM"
    exit 1
fi

echo "Waiting for VM to be ready..."
sleep 30

echo "Getting VM IP..."
VM_IP=$(az vm show -d -g "$RESOURCE_GROUP" -n "$VM_NAME" --query publicIps -o tsv)
if [ -z "$VM_IP" ]; then
    echo "Error: Failed to get VM IP"
    exit 1
fi

echo "Creating Azure Container Registry..."
if ! az acr create --resource-group "$RESOURCE_GROUP" --name "$ACR_NAME" --sku Basic; then
    echo "Error: Failed to create ACR"
    exit 1
fi

echo "Getting ACR credentials..."
ACR_USERNAME=$(az acr credential show --name "$ACR_NAME" --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name "$ACR_NAME" --query passwords[0].value -o tsv)
if [ -z "$ACR_USERNAME" ] || [ -z "$ACR_PASSWORD" ]; then
    echo "Error: Failed to get ACR credentials"
    exit 1
fi

echo "Installing Docker on VM..."
if ! ssh -i ~/.ssh/pdf-processor-vm_key "$ADMIN_USERNAME@$VM_IP" "sudo apt-get update && sudo apt-get install -y docker.io"; then
    echo "Error: Failed to install Docker"
    exit 1
fi

echo "Creating app directory on VM..."
if ! ssh -i ~/.ssh/pdf-processor-vm_key "$ADMIN_USERNAME@$VM_IP" "mkdir -p /app"; then
    echo "Error: Failed to create app directory"
    exit 1
fi

echo "Copying files to VM..."
if ! scp -i ~/.ssh/pdf-processor-vm_key -r ./* "$ADMIN_USERNAME@$VM_IP:/app/"; then
    echo "Error: Failed to copy files"
    exit 1
fi

echo "Logging into ACR..."
if ! ssh -i ~/.ssh/pdf-processor-vm_key "$ADMIN_USERNAME@$VM_IP" "docker login $ACR_NAME.azurecr.io -u $ACR_USERNAME -p $ACR_PASSWORD"; then
    echo "Error: Failed to login to ACR"
    exit 1
fi

echo "Building and pushing Docker image..."
if ! ssh -i ~/.ssh/pdf-processor-vm_key "$ADMIN_USERNAME@$VM_IP" "cd /app && docker build -t $ACR_NAME.azurecr.io/pdf-processor:latest . && docker push $ACR_NAME.azurecr.io/pdf-processor:latest"; then
    echo "Error: Failed to build and push Docker image"
    exit 1
fi

echo "Deployment completed successfully!"
echo "VM IP: $VM_IP"
echo "ACR Login Server: $ACR_NAME.azurecr.io"

echo "
Deployment complete!
VM IP: $VM_IP
SSH Command: ssh -i ~/.ssh/pdf-processor-vm_key $ADMIN_USERNAME@$VM_IP
ACR Login Server: $ACR_NAME.azurecr.io
ACR Username: $ACR_USERNAME
ACR Password: $ACR_PASSWORD

To connect to the VM:
ssh -i ~/.ssh/pdf-processor-vm_key $ADMIN_USERNAME@$VM_IP

To build and run the container:
docker run -d --name pdf-processor -v /data:/app/data $ACR_NAME.azurecr.io/pdf-processor:latest
" 