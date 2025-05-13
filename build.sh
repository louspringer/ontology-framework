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
        echo "Build successful. Updating latest tag..."
        
        # Get all images tagged as latest
        echo "Finding all images tagged as latest..."
        LATEST_DIGESTS=$(az acr repository show-tags --name $ACR_NAME --repository bfg9k-mcp-sse --orderby time_desc --query "[?contains(tags, 'latest')].digest" -o tsv)
        
        # Remove all existing latest tags
        for digest in $LATEST_DIGESTS; do
            echo "Removing latest tag from digest: $digest"
            az acr repository untag --name $ACR_NAME --image bfg9k-mcp-sse@$digest
        done
        
        # Create new latest tag
        echo "Creating new latest tag..."
        az acr repository update \
            --name $ACR_NAME \
            --image bfg9k-mcp-sse:latest \
            --tag bfg9k-mcp-sse:$TAG
            
        echo "Image available at: $ACR_NAME.azurecr.io/bfg9k-mcp-sse:$TAG"
        echo "Latest tag updated to: $ACR_NAME.azurecr.io/bfg9k-mcp-sse:latest"
    else
        echo "Build failed. Check ACR build logs for details."
        exit 1
    fi
fi 