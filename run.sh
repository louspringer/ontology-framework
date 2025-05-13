#!/bin/bash

# Load .env if present
if [ -f .env ]; then
    set -o allexport
    source .env
    set +o allexport
else
    echo ".env file not found. Proceeding with defaults or environment variables."
fi

MODE=${1:-"local"}  # local or aci
IMAGE_NAME=${2:-"bfg9k-mcp"}
TAG=${3:-"latest"}
PORT=${4:-8080}
ACI_NAME=${5:-"bfg9k-mcp"}
RESOURCE_GROUP=${6:-"ontology-platform-rg"}

# Use .env values if set, otherwise fallback
ACR_NAME="${ACR_NAME:-ontologyframework}"
ACR_SERVER="${ACR:-$ACR_NAME.azurecr.io}"
ACR_USERNAME="${ACR_USERNAME:-}"  # optional
ACR_PASSWORD="${ACR_PASSWORD:-}"  # optional

if [ "$MODE" = "local" ]; then
    echo "Running locally with Docker..."
    # Always remove local image to force pull from ACR
    echo "Removing local image $ACR_SERVER/$IMAGE_NAME:$TAG (if exists)..."
    docker rmi $ACR_SERVER/$IMAGE_NAME:$TAG 2>/dev/null || true
    echo "Pulling latest image from $ACR_SERVER..."
    docker pull $ACR_SERVER/$IMAGE_NAME:$TAG
    if [ -n "$ACR_USERNAME" ] && [ -n "$ACR_PASSWORD" ]; then
        echo "Logging in to Docker registry $ACR_SERVER as $ACR_USERNAME..."
        echo $ACR_PASSWORD | docker login $ACR_SERVER -u $ACR_USERNAME --password-stdin
    fi
    echo "running $ACR_SERVER/$IMAGE_NAME:$TAG"
    docker run -it --rm -p $PORT:8080 $ACR_SERVER/$IMAGE_NAME:$TAG
else
    echo "Running remotely via Azure Container Instance..."
    az container create \
        --resource-group $RESOURCE_GROUP \
        --name $ACI_NAME \
        --image $ACR_SERVER/$IMAGE_NAME:$TAG \
        --ports $PORT \
        --dns-name-label $ACI_NAME-$RANDOM \
        --environment-variables ACR_NAME=$ACR_NAME \
        --restart-policy OnFailure
fi 