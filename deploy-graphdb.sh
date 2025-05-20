#!/bin/bash

# Exit on error
set -e

# Configuration
RESOURCE_GROUP="graphdb-dev-rg"
LOCATION="westus"
CONTAINER_APP_NAME="graphdb-dev"
STORAGE_ACCOUNT_NAME="graphdbstore$(openssl rand -hex 4)"
FILE_SHARE_NAME="graphdbdata"
CONTAINER_APP_ENV="graphdb-env"
CONTAINER_APP_DNS="graphdb-dev.$(openssl rand -hex 4).westus.azurecontainerapps.io"

# Create resource group
echo "Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create storage account and file share
echo "Creating storage account and file share..."
az storage account create \
    --name $STORAGE_ACCOUNT_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku Standard_LRS \
    --kind StorageV2

# Get storage account key
STORAGE_KEY=$(az storage account keys list \
    --account-name $STORAGE_ACCOUNT_NAME \
    --resource-group $RESOURCE_GROUP \
    --query '[0].value' \
    --output tsv)

# Create file share
az storage share create \
    --name $FILE_SHARE_NAME \
    --account-name $STORAGE_ACCOUNT_NAME \
    --account-key $STORAGE_KEY

# Create Container Apps environment
echo "Creating Container Apps environment..."
az containerapp env create \
    --name $CONTAINER_APP_ENV \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION

# Create Container App
echo "Creating Container App..."
az containerapp create \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $CONTAINER_APP_ENV \
    --image ontotext/graphdb:10.4.1 \
    --target-port 7200 \
    --ingress external \
    --min-replicas 1 \
    --max-replicas 1 \
    --env-vars \
        GDB_HEAP_SIZE=2g \
        GDB_JAVA_OPTS="-Xms2g -Xmx2g" \
    --secrets "graphdb-password=graphdb-dev-password" \
    --registry-server docker.io \
    --volume-mount "/opt/graphdb/home=graphdb-data" \
    --volume "graphdb-data=azureFile:graphdbdata:$STORAGE_ACCOUNT_NAME" \
    --query properties.configuration.ingress.fqdn

echo "Deployment completed!"
echo "GraphDB will be available at: https://$CONTAINER_APP_DNS"
echo "Default credentials:"
echo "Username: admin"
echo "Password: graphdb-dev-password"
echo ""
echo "To test the connection, use:"
echo "curl -X GET https://$CONTAINER_APP_DNS/repositories -u admin:graphdb-dev-password" 