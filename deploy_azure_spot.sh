#!/bin/bash

set -e  # Exit on any error

# Configuration
RESOURCE_GROUP="ontology-framework-rg"
LOCATION="southeastasia"  # Using southeastasia as it has good spot VM availability
VM_NAME="ontology-framework-vm"
VM_SIZE="Standard_D2s_v3"  # 2 vCPUs, 8GB RAM
ADMIN_USERNAME="azureuser"
VM_IMAGE="Canonical:0001-com-ubuntu-server-jammy:22_04-lts:latest"
ACR_NAME="ontologyframework$(date +%Y%m%d)"  # Unique name with date

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
if ! ssh-keygen -t rsa -b 4096 -f ~/.ssh/ontology-framework-vm_key -N ""; then
    echo "Error: Failed to generate SSH key"
    exit 1
fi

echo "Creating resource group..."
if ! az group create --name "$RESOURCE_GROUP" --location "$LOCATION"; then
    echo "Error: Failed to create resource group"
    exit 1
fi

echo "Creating virtual network..."
if ! az network vnet create \
    --resource-group "$RESOURCE_GROUP" \
    --name "${VM_NAME}VNET" \
    --address-prefix 10.0.0.0/16 \
    --subnet-name "${VM_NAME}Subnet" \
    --subnet-prefix 10.0.0.0/24; then
    echo "Error: Failed to create virtual network"
    exit 1
fi

echo "Creating network security group..."
if ! az network nsg create \
    --resource-group "$RESOURCE_GROUP" \
    --name "${VM_NAME}NSG"; then
    echo "Error: Failed to create network security group"
    exit 1
fi

echo "Adding security rules..."
# Allow SSH
if ! az network nsg rule create \
    --resource-group "$RESOURCE_GROUP" \
    --nsg-name "${VM_NAME}NSG" \
    --name "AllowSSH" \
    --protocol tcp \
    --priority 1000 \
    --destination-port-range 22 \
    --access allow; then
    echo "Error: Failed to create SSH rule"
    exit 1
fi

# Allow GraphDB port
if ! az network nsg rule create \
    --resource-group "$RESOURCE_GROUP" \
    --nsg-name "${VM_NAME}NSG" \
    --name "AllowGraphDB" \
    --protocol tcp \
    --priority 1001 \
    --destination-port-range 7200 \
    --access allow; then
    echo "Error: Failed to create GraphDB rule"
    exit 1
fi

# Allow Ontology Service port
if ! az network nsg rule create \
    --resource-group "$RESOURCE_GROUP" \
    --nsg-name "${VM_NAME}NSG" \
    --name "AllowOntologyService" \
    --protocol tcp \
    --priority 1002 \
    --destination-port-range 8000 \
    --access allow; then
    echo "Error: Failed to create Ontology Service rule"
    exit 1
fi

echo "Creating public IP..."
if ! az network public-ip create \
    --resource-group "$RESOURCE_GROUP" \
    --name "${VM_NAME}PublicIP" \
    --sku Standard \
    --version IPv4; then
    echo "Error: Failed to create public IP"
    exit 1
fi

echo "Creating spot VM..."
if ! az vm create \
    --resource-group "$RESOURCE_GROUP" \
    --name "$VM_NAME" \
    --image "$VM_IMAGE" \
    --size "$VM_SIZE" \
    --admin-username "$ADMIN_USERNAME" \
    --ssh-key-values ~/.ssh/ontology-framework-vm_key.pub \
    --priority Spot \
    --eviction-policy Deallocate \
    --public-ip-address "${VM_NAME}PublicIP" \
    --vnet-name "${VM_NAME}VNET" \
    --subnet "${VM_NAME}Subnet" \
    --nsg "${VM_NAME}NSG"; then
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

echo "Installing Docker and Docker Compose on VM..."
if ! ssh -i ~/.ssh/ontology-framework-vm_key "$ADMIN_USERNAME@$VM_IP" "sudo apt-get update && sudo apt-get install -y docker.io docker-compose && sudo usermod -aG docker $ADMIN_USERNAME"; then
    echo "Error: Failed to install Docker"
    exit 1
fi

echo "Creating data directory on VM..."
if ! ssh -i ~/.ssh/ontology-framework-vm_key "$ADMIN_USERNAME@$VM_IP" "sudo mkdir -p /data && sudo chown $ADMIN_USERNAME:$ADMIN_USERNAME /data"; then
    echo "Error: Failed to create data directory"
    exit 1
fi

echo "Copying files to VM..."
if ! scp -i ~/.ssh/ontology-framework-vm_key -r ./* "$ADMIN_USERNAME@$VM_IP:/app/"; then
    echo "Error: Failed to copy files"
    exit 1
fi

echo "Logging into ACR..."
if ! ssh -i ~/.ssh/ontology-framework-vm_key "$ADMIN_USERNAME@$VM_IP" "docker login $ACR_NAME.azurecr.io -u $ACR_USERNAME -p $ACR_PASSWORD"; then
    echo "Error: Failed to login to ACR"
    exit 1
fi

echo "Building and pushing Docker image..."
if ! ssh -i ~/.ssh/ontology-framework-vm_key "$ADMIN_USERNAME@$VM_IP" "cd /app && docker build -t $ACR_NAME.azurecr.io/ontology-framework:latest . && docker push $ACR_NAME.azurecr.io/ontology-framework:latest"; then
    echo "Error: Failed to build and push Docker image"
    exit 1
fi

echo "Starting GraphDB container..."
if ! ssh -i ~/.ssh/ontology-framework-vm_key "$ADMIN_USERNAME@$VM_IP" "docker run -d --name graphdb -p 7200:7200 -v /data:/data ontotext/graphdb:10.1.0"; then
    echo "Error: Failed to start GraphDB"
    exit 1
fi

echo "Starting Ontology Framework container..."
if ! ssh -i ~/.ssh/ontology-framework-vm_key "$ADMIN_USERNAME@$VM_IP" "docker run -d --name ontology-framework -p 8000:8000 -v /data:/app/data --link graphdb:graphdb $ACR_NAME.azurecr.io/ontology-framework:latest"; then
    echo "Error: Failed to start Ontology Framework"
    exit 1
fi

echo "Deployment completed successfully!"
echo "VM IP: $VM_IP"
echo "ACR Login Server: $ACR_NAME.azurecr.io"

echo "
Deployment complete!
VM IP: $VM_IP
SSH Command: ssh -i ~/.ssh/ontology-framework-vm_key $ADMIN_USERNAME@$VM_IP
ACR Login Server: $ACR_NAME.azurecr.io
ACR Username: $ACR_USERNAME
ACR Password: $ACR_PASSWORD

Services:
- GraphDB: http://$VM_IP:7200
- Ontology Framework: http://$VM_IP:8000

To connect to the VM:
ssh -i ~/.ssh/ontology-framework-vm_key $ADMIN_USERNAME@$VM_IP

To view logs:
docker logs ontology-framework
docker logs graphdb
" 