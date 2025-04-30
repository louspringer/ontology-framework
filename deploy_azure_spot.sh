#!/bin/bash

# Azure Resource Group and Location
RESOURCE_GROUP="pdf-processor-rg"
LOCATION="eastus"
VM_NAME="pdf-processor-vm"
VM_SIZE="Standard_D2s_v3"
ADMIN_USERNAME="azureuser"
VM_IMAGE="Canonical:0001-com-ubuntu-server-jammy:22_04-lts:latest"
ACR_NAME="pdfprocessor1234"

# Delete existing resource group if it exists
echo "Cleaning up existing resources..."
az group delete --name $RESOURCE_GROUP --yes --no-wait

# Wait for deletion to complete
echo "Waiting for cleanup to complete..."
az group wait --name $RESOURCE_GROUP --deleted

# Create SSH key
SSH_KEY_FILE="$HOME/.ssh/${VM_NAME}_key"
echo "Generating SSH key..."
rm -f "$SSH_KEY_FILE" "$SSH_KEY_FILE.pub"
ssh-keygen -t rsa -b 4096 -f "$SSH_KEY_FILE" -N "" -C "azureuser@pdf-processor"

# Create Resource Group
echo "Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create spot VM with SSH key
echo "Creating spot VM..."
az vm create \
    --resource-group $RESOURCE_GROUP \
    --name $VM_NAME \
    --image $VM_IMAGE \
    --size $VM_SIZE \
    --admin-username $ADMIN_USERNAME \
    --ssh-key-value "@$SSH_KEY_FILE.pub" \
    --public-ip-sku Standard \
    --priority Spot \
    --eviction-policy Deallocate \
    --spot-max-price -1

# Wait for VM to be ready
echo "Waiting for VM to be ready..."
sleep 30

# Get VM IP
VM_IP=$(az vm show -d -g $RESOURCE_GROUP -n $VM_NAME --query publicIps -o tsv)
echo "VM IP: $VM_IP"

# Add to known_hosts
ssh-keyscan -H $VM_IP >> ~/.ssh/known_hosts 2>/dev/null

# Create Container Registry if it doesn't exist
echo "Creating Azure Container Registry..."
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true

# Get ACR credentials
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

# Wait for VM to be fully ready
echo "Waiting for VM to be fully initialized..."
sleep 30

# Install Docker on VM
echo "Installing Docker on VM..."
ssh -o StrictHostKeyChecking=no -i "$SSH_KEY_FILE" $ADMIN_USERNAME@$VM_IP "sudo apt-get update && sudo apt-get install -y docker.io docker-compose git && sudo usermod -aG docker $ADMIN_USERNAME"

# Create app directory
echo "Setting up application..."
ssh -i "$SSH_KEY_FILE" $ADMIN_USERNAME@$VM_IP "mkdir -p /home/$ADMIN_USERNAME/app"

# Copy local files to VM
echo "Copying files to VM..."
scp -i "$SSH_KEY_FILE" -r ./* $ADMIN_USERNAME@$VM_IP:/home/$ADMIN_USERNAME/app/

# Login to ACR on VM
echo "Logging into ACR..."
ssh -i "$SSH_KEY_FILE" $ADMIN_USERNAME@$VM_IP "docker login $ACR_NAME.azurecr.io -u $ACR_NAME -p $ACR_PASSWORD"

# Build and push Docker image on VM
echo "Building and pushing Docker image..."
ssh -i "$SSH_KEY_FILE" $ADMIN_USERNAME@$VM_IP "cd /home/$ADMIN_USERNAME/app && docker build -t $ACR_NAME.azurecr.io/pdf-processor:latest . && docker push $ACR_NAME.azurecr.io/pdf-processor:latest"

echo "
Deployment complete!
VM IP: $VM_IP
SSH Command: ssh -i $SSH_KEY_FILE $ADMIN_USERNAME@$VM_IP
ACR Login Server: $ACR_NAME.azurecr.io
ACR Username: $ACR_NAME
ACR Password: $ACR_PASSWORD

To connect to the VM:
ssh -i $SSH_KEY_FILE $ADMIN_USERNAME@$VM_IP

To build and run the container:
docker run -d --name pdf-processor -v /data:/app/data $ACR_NAME.azurecr.io/pdf-processor:latest
" 