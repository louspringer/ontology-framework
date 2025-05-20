#!/bin/bash

APIM_NAME=${APIM_NAME:-baldo-apim}
RESOURCE_GROUP=${RESOURCE_GROUP:-BALDO-DEVBOX-RG}
API_SUFFIX=${API_SUFFIX:-graphdb}

# Get the primary key for the built-in 'Unlimited' subscription
echo "[INFO] Retrieving APIM subscription key..."
KEY=$(az apim subscription show \
  --resource-group $RESOURCE_GROUP \
  --service-name $APIM_NAME \
  --sid 00000000000000000000000000000001 \
  --query primaryKey -o tsv)

if [ -z "$KEY" ]; then
  echo "[ERROR] Could not retrieve subscription key."
  exit 1
fi

echo "[INFO] Subscription key: $KEY"
echo ""
echo "[INFO] Sample curl command:"
echo "curl -H 'Ocp-Apim-Subscription-Key: $KEY' https://$APIM_NAME.azure-api.net/$API_SUFFIX" 