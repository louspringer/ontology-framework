#!/bin/bash

# Usage:
#   ./build.sh [local|acr] [platform] [dockerfile] [image_name] [tag]
#
# Examples:
#   ./build.sh local linux/amd64 Dockerfile.bfg9k bfg9k-mcp-sse latest
#   ./build.sh acr linux/amd64 Dockerfile.bfg9k bfg9k-mcp-sse 20240514_120000

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    source .env
fi

# Defaults
BUILD_TYPE=${1:-"acr"}  # local or acr
PLATFORM=${2:-"linux/amd64"}
DOCKERFILE=${3:-"Dockerfile.bfg9k"}
IMAGE_NAME=${4:-"bfg9k-mcp"}
TAG=${5:-$(date +%Y%m%d_%H%M%S)}
ACR_NAME="${ACR_NAME:-ontologyframework}"
ACR_SERVER="${ACR_SERVER:-$ACR_NAME.azurecr.io}"

set -e

echo "Build type: $BUILD_TYPE"
echo "Platform: $PLATFORM"
echo "Dockerfile: $DOCKERFILE"
echo "Image: $ACR_SERVER/$IMAGE_NAME:$TAG"

echo "Logging in to Azure Container Registry..."
az acr login --name $ACR_NAME

if [ "$BUILD_TYPE" = "local" ]; then
    echo "Performing local Docker build..."
    docker build -f $DOCKERFILE -t $IMAGE_NAME:$TAG --build-arg BUILDPLATFORM=$PLATFORM --build-arg TARGETPLATFORM=$PLATFORM .
    docker tag $IMAGE_NAME:$TAG $ACR_SERVER/$IMAGE_NAME:$TAG
    docker push $ACR_SERVER/$IMAGE_NAME:$TAG
    # Always tag and push as latest
    docker tag $IMAGE_NAME:$TAG $ACR_SERVER/$IMAGE_NAME:latest
    docker push $ACR_SERVER/$IMAGE_NAME:latest
    echo "Local build and push successful: $IMAGE_NAME:$TAG and :latest"
else
    echo "Building with ACR Build service..."
    az acr build \
        --registry $ACR_NAME \
        --image $IMAGE_NAME:$TAG \
        --image $IMAGE_NAME:latest \
        --platform $PLATFORM \
        --file $DOCKERFILE \
        --build-arg BUILDPLATFORM=$PLATFORM \
        --build-arg TARGETPLATFORM=$PLATFORM \
        .
    echo "ACR build submitted for: $IMAGE_NAME:$TAG and :latest"
fi

echo "Build script completed." 