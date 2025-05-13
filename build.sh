#!/bin/bash

# Default values
BUILD_TYPE=${1:-"acr"}
PLATFORM=${2:-"linux/amd64"}
DOCKERFILE=${3:-"Dockerfile"}
IMAGE_NAME=${4:-"ontology-framework"}

# ACR configuration
ACR_NAME="ontologyframework"
TAG=$(date +%Y%m%d_%H%M%S)

echo "Build type: $BUILD_TYPE"
echo "Platform: $PLATFORM"
echo "Dockerfile: $DOCKERFILE"
echo "Image: $ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG"

if [ "$BUILD_TYPE" = "local" ]; then
    echo "Performing local Docker build..."
    docker build -f $DOCKERFILE -t $IMAGE_NAME:$TAG --build-arg BUILDPLATFORM=$PLATFORM --build-arg TARGETPLATFORM=$PLATFORM .
    if [ $? -eq 0 ]; then
        echo "Local build successful: $IMAGE_NAME:$TAG"
    else
        echo "Local build failed."
        exit 1
    fi
else
    echo "Building with ACR Build service..."
    az acr build \
        --registry $ACR_NAME \
        --image $IMAGE_NAME:$TAG \
        --platform $PLATFORM \
        --file $DOCKERFILE \
        --build-arg BUILDPLATFORM=$PLATFORM \
        --build-arg TARGETPLATFORM=$PLATFORM \
        .

    # Tag as latest if build succeeds
    if [ $? -eq 0 ]; then
        echo "Build successful. Tagging as latest..."
        az acr import --name $ACR_NAME \
            --source $ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG \
            --image $IMAGE_NAME:latest
        echo "Image available at: $ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG"
        echo "Latest tag updated to: $ACR_NAME.azurecr.io/$IMAGE_NAME:latest"
    else
        echo "Build failed. Check ACR build logs for details."
        exit 1
    fi
fi 