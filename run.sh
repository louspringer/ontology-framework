#!/bin/bash

# Load .env if present
if [ -f .env ]; then
    set -o allexport
    source .env
    set +o allexport
else
    echo ".env file not found. Proceeding with defaults or environment variables."
fi

# Default values
RUN_TYPE=${1:-"local"}  # local or aci
IMAGE_NAME=${2:-"bfg9k-mcp-sse"}
TAG=${3:-"latest"}
PORT=${4:-8080}
ACI_NAME=${5:-"bfg9k-mcp"}
RESOURCE_GROUP=${6:-"ontology-platform-rg"}
CPU=${7:-1}
MEMORY=${8:-2}

# Use .env values if set, otherwise fallback
ACR_NAME="${ACR_NAME:-ontologyframework}"
ACR_SERVER="${ACR:-$ACR_NAME.azurecr.io}"
ACR_USERNAME="${ACR_USERNAME:-}"  # optional
ACR_PASSWORD="${ACR_PASSWORD:-}"  # optional

# Helper: parse .env for all variables (excluding comments/empty lines)
get_env_vars() {
    if [ -f .env ]; then
        grep -v '^#' .env | grep -v '^$' | sed 's/\r//' | awk -F= '{gsub(/\"/, "", $2); printf("%s=%s ", $1, $2)}'
    fi
}

echo "[DEBUG] IMAGE_NAME: $IMAGE_NAME"
echo "[DEBUG] Full image reference: $ACR_SERVER/$IMAGE_NAME:$TAG"

# (No changes needed to argument parsing if IMAGE_NAME is set as: IMAGE_NAME=${2:-"bfg9k-mcp-sse"})
# But double-check that $2 is not empty when provided.
if [ -z "$IMAGE_NAME" ]; then
    echo "[ERROR] IMAGE_NAME is not set. Please provide it as the second argument."
    exit 1
fi

# ---
# Subnet/VNet argument handling for Azure Container Instance
# Supports two patterns:
#   1. If both VNET_NAME and SUBNET_NAME are provided, use --vnet and --subnet
#   2. If a full subnet resource ID is provided, use --subnet only
#   3. If neither, deploy public (no subnet)
#
# Usage examples:
#   ./run.sh aci bfg9k-mcp-sse latest 8080 bfg9k-mcp-sse ontology-platform-rg 1 2 baldo-net-westus aci-subnet
#   ./run.sh aci bfg9k-mcp-sse latest 8080 bfg9k-mcp-sse ontology-platform-rg 1 2 /subscriptions/.../subnets/aci-subnet
# ---

# Parse VNet/Subnet arguments
VNET_OR_SUBNET_ARG=${9:-""}
SUBNET_NAME_ARG=${10:-""}
VNET_RESOURCE_GROUP=${11:-"BALDO-DEVBOX-RG"}

# Determine subnet CLI args
SUBNET_CLI_ARGS=""
USE_DNS_LABEL=1
if [[ "$VNET_OR_SUBNET_ARG" == "/subscriptions/"* ]]; then
    # Full subnet resource ID provided
    SUBNET_CLI_ARGS="--subnet $VNET_OR_SUBNET_ARG"
    USE_DNS_LABEL=0
    echo "[DEBUG] Using full subnet resource ID: $VNET_OR_SUBNET_ARG"
elif [[ -n "$VNET_OR_SUBNET_ARG" && -n "$SUBNET_NAME_ARG" ]]; then
    # VNet name and subnet name provided, resolve full subnet ID
    echo "[DEBUG] Resolving subnet ID for VNet: $VNET_OR_SUBNET_ARG, Subnet: $SUBNET_NAME_ARG, VNet RG: $VNET_RESOURCE_GROUP"
    SUBNET_ID=$(az network vnet subnet show --resource-group "$VNET_RESOURCE_GROUP" --vnet-name "$VNET_OR_SUBNET_ARG" --name "$SUBNET_NAME_ARG" --query id -o tsv)
    if [ -z "$SUBNET_ID" ]; then
        echo "[ERROR] Failed to resolve subnet ID. Check VNet and Subnet names and resource group."
        exit 1
    fi
    SUBNET_CLI_ARGS="--subnet $SUBNET_ID"
    USE_DNS_LABEL=0
    echo "[DEBUG] Resolved subnet ID: $SUBNET_ID"
else
    echo "[DEBUG] No subnet/VNet specified, deploying with public IP."
    USE_DNS_LABEL=1
fi

if [ "$RUN_TYPE" = "local" ]; then
    # echo "Running locally with Docker..."
    echo "Removing local image $ACR_SERVER/$IMAGE_NAME:$TAG (if exists)..."
    docker rmi $ACR_SERVER/$IMAGE_NAME:$TAG 2>/dev/null || true
    echo "Pulling latest image from $ACR_SERVER..."
    docker pull $ACR_SERVER/$IMAGE_NAME:$TAG
    if [ -n "$ACR_USERNAME" ] && [ -n "$ACR_PASSWORD" ]; then
        echo "Logging in to Docker registry $ACR_SERVER as $ACR_USERNAME..."
        echo $ACR_PASSWORD | docker login $ACR_SERVER -u $ACR_USERNAME --password-stdin
    fi
    echo "Running $ACR_SERVER/$IMAGE_NAME:$TAG"
    # Pass all .env variables to Docker
    ENV_ARGS=""
    if [ -f .env ]; then
        while IFS= read -r line; do
            [[ "$line" =~ ^#.*$ || -z "$line" ]] && continue
            varname=$(echo "$line" | cut -d= -f1)
            ENV_ARGS+="--env $varname "
        done < .env
    fi
    echo "Running docker run -it --rm -p $PORT:8080 $ENV_ARGS $ACR_SERVER/$IMAGE_NAME:$TAG"
    docker run -it --rm -p $PORT:8080 $ENV_ARGS $ACR_SERVER/$IMAGE_NAME:$TAG
else
    echo "Running remotely via Azure Container Instance..."
    echo "Container group name: $ACI_NAME"
    echo "DNS name label: ${ACI_NAME,,}-$(date +%s)"
    echo "Image registry username: $ACR_USERNAME"
    echo "Image registry password: ${ACR_PASSWORD:0:4}... (hidden)"
    # Compose --environment-variables from .env
    ENV_ARGS=""
    if [ -f .env ]; then
        while IFS= read -r line; do
            [[ "$line" =~ ^#.*$ || -z "$line" ]] && continue
            varname=$(echo "$line" | cut -d= -f1)
            value=$(echo "$line" | cut -d= -f2- | sed 's/^"//;s/"$//')
            ENV_ARGS+="$varname=$value "
        done < .env
    fi
    REGISTRY_ARGS=""
    if [ -n "$ACR_USERNAME" ] && [ -n "$ACR_PASSWORD" ]; then
        REGISTRY_ARGS="--registry-username $ACR_USERNAME --registry-password $ACR_PASSWORD"
    fi
    DNS_LABEL="${ACI_NAME,,}-$(date +%s)"
    az container delete --resource-group $RESOURCE_GROUP --name $ACI_NAME --yes 2>/dev/null || true
    # Build az container create command, only add --dns-name-label if public
    AZ_DNS_LABEL_ARG=""
    if [ "$USE_DNS_LABEL" -eq 1 ]; then
        AZ_DNS_LABEL_ARG="--dns-name-label $DNS_LABEL"
    fi

    # Print the full az command for debug
    AZ_CMD="az container create \
        --resource-group $RESOURCE_GROUP \
        --name $ACI_NAME \
        --image $ACR_SERVER/$IMAGE_NAME:$TAG \
        --ports $PORT \
        $AZ_DNS_LABEL_ARG \
        --os-type Linux \
        --cpu $CPU \
        --memory $MEMORY \
        $REGISTRY_ARGS \
        --environment-variables $ENV_ARGS \
        --restart-policy OnFailure \
        $SUBNET_CLI_ARGS"
    echo "[DEBUG] AZ_CMD: $AZ_CMD"

    # Actually run the command
    $AZ_CMD
    if [ $? -eq 0 ]; then
        echo "ACI container group $ACI_NAME created successfully."
    else
        echo "Failed to create ACI container group $ACI_NAME. Check Azure CLI output for details."
        exit 1
    fi
fi 