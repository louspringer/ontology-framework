#!/bin/bash

# Azure Resource Group and Location
RESOURCE_GROUP="pdf-processor-rg"
LOCATION="eastus"  # Change to your preferred region

# VM Configuration
VM_NAME="pdf-processor-vm"
VM_SIZE="Standard_D2s_v3"
ADMIN_USERNAME="azureuser"
VM_IMAGE="Ubuntu2204"

# Container Registry
ACR_NAME="pdfprocessor1234"  # Must be globally unique

# Create Resource Group
echo "Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create VM
echo "Creating VM..."
az vm create \
    --resource-group $RESOURCE_GROUP \
    --name $VM_NAME \
    --image $VM_IMAGE \
    --size $VM_SIZE \
    --admin-username $ADMIN_USERNAME \
    --generate-ssh-keys \
    --public-ip-sku Standard

# Create Container Registry
echo "Creating Azure Container Registry..."
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true

# Get ACR credentials
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

# Install Docker and dependencies on VM
echo "Installing Docker on VM..."
az vm run-command invoke \
    --resource-group $RESOURCE_GROUP \
    --name $VM_NAME \
    --command-id RunShellScript \
    --scripts "sudo apt-get update && sudo apt-get install -y docker.io docker-compose && sudo usermod -aG docker $ADMIN_USERNAME"

# Create data directory
echo "Creating data directory..."
az vm run-command invoke \
    --resource-group $RESOURCE_GROUP \
    --name $VM_NAME \
    --command-id RunShellScript \
    --scripts "sudo mkdir -p /data && sudo chown $ADMIN_USERNAME:$ADMIN_USERNAME /data"

# Output connection information
echo "Deployment complete!"
echo "VM Public IP: $(az vm show -d -g $RESOURCE_GROUP -n $VM_NAME --query publicIps -o tsv)"
echo "ACR Login Server: $ACR_NAME.azurecr.io"
echo "ACR Username: $ACR_NAME"
echo "ACR Password: $ACR_PASSWORD"

# Instructions for next steps
echo "
Next steps:
1. SSH to the VM:
   ssh $ADMIN_USERNAME@$(az vm show -d -g $RESOURCE_GROUP -n $VM_NAME --query publicIps -o tsv)

2. Login to ACR:
   docker login $ACR_NAME.azurecr.io -u $ACR_NAME -p $ACR_PASSWORD

3. Build and push the image:
   docker build -t $ACR_NAME.azurecr.io/pdf-processor:latest .
   docker push $ACR_NAME.azurecr.io/pdf-processor:latest

4. Run the container:
   docker run -d --name pdf-processor -v /data:/app/data $ACR_NAME.azurecr.io/pdf-processor:latest
" 