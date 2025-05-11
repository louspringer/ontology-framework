#!/bin/bash

# Default values
BUILD_TYPE=${1:-"local"}
PLATFORM=${2:-"linux/amd64"}

# ACR configuration
ACR_NAME="ontologyframework"
IMAGE_NAME="ontology-framework"
TAG=$(date +%Y%m%d_%H%M%S)

echo "Building with ACR Build service..."
echo "Build type: $BUILD_TYPE"
echo "Platform: $PLATFORM"
echo "Image: $ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG"

# Build and push using ACR Build
az acr build \
    --registry $ACR_NAME \
    --image $IMAGE_NAME:$TAG \
    --platform $PLATFORM \
    --file Dockerfile \
    --build-arg BUILDPLATFORM=$PLATFORM \
    --build-arg TARGETPLATFORM=$PLATFORM \
    .

# Tag as latest if build succeeds
if [ $? -eq 0 ]; then
    echo "Build successful. Tagging as latest..."
    az acr repository show-tags --name $ACR_NAME --repository $IMAGE_NAME --orderby time_desc --output tsv | head -n1 | xargs -I {} az acr repository untag --name $ACR_NAME --image $IMAGE_NAME:latest || true
    az acr repository tag --name $ACR_NAME --image $IMAGE_NAME:$TAG --tag latest
    echo "Image available at: $ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG"
    echo "Latest tag updated to: $ACR_NAME.azurecr.io/$IMAGE_NAME:latest"
else
    echo "Build failed. Check ACR build logs for details."
    exit 1
fi 