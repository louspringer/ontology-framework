#!/bin/bash

# Azure resource variables
APIM_NAME=${APIM_NAME:-baldo-apim}
RESOURCE_GROUP=${RESOURCE_GROUP:-BALDO-DEVBOX-RG}
LOCATION=${LOCATION:-westus}
PUBLISHER_EMAIL=${PUBLISHER_EMAIL:-you@example.com}
PUBLISHER_NAME=${PUBLISHER_NAME:-"Your Name"}
GRAPHDB_API_NAME=${GRAPHDB_API_NAME:-graphdb}
GRAPHDB_API_SUFFIX=${GRAPHDB_API_SUFFIX:-graphdb}
GRAPHDB_BACKEND_URL=${GRAPHDB_BACKEND_URL:-http://10.0.2.6:7200}
CLIENT_CERT_PATH=${CLIENT_CERT_PATH:-./client-cert.pem}

# Deploy APIM (Consumption tier)
deploy_apim() {
  echo "[INFO] Creating APIM instance ($APIM_NAME) in $RESOURCE_GROUP..."
  az apim create \
    --name $APIM_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --publisher-email $PUBLISHER_EMAIL \
    --publisher-name "$PUBLISHER_NAME" \
    --sku-name Consumption
}

# Import GraphDB API
deploy_api() {
  echo "[INFO] Importing GraphDB API..."
  az apim api create \
    --resource-group $RESOURCE_GROUP \
    --service-name $APIM_NAME \
    --api-id $GRAPHDB_API_NAME \
    --path $GRAPHDB_API_SUFFIX \
    --display-name "GraphDB" \
    --protocols https \
    --service-url $GRAPHDB_BACKEND_URL
}

# Upload client certificate
deploy_cert() {
  echo "[INFO] Uploading client certificate..."
  az apim certificate create \
    --resource-group $RESOURCE_GROUP \
    --service-name $APIM_NAME \
    --data "$(base64 < $CLIENT_CERT_PATH)" \
    --name client-cert
}

# Add client cert validation policy
deploy_policy() {
  echo "[INFO] Adding client certificate validation policy..."
  POLICY_FILE=policy.xml
  cat > $POLICY_FILE <<EOF
<policies>
  <inbound>
    <base />
    <validate-client-certificate />
  </inbound>
  <backend>
    <base />
  </backend>
  <outbound>
    <base />
  </outbound>
  <on-error>
    <base />
  </on-error>
</policies>
EOF
  az apim api policy create \
    --resource-group $RESOURCE_GROUP \
    --service-name $APIM_NAME \
    --api-id $GRAPHDB_API_NAME \
    --xml-content @$POLICY_FILE
  rm $POLICY_FILE
}

# Undeploy (delete APIM instance)
undeploy_apim() {
  echo "[INFO] Deleting APIM instance ($APIM_NAME)..."
  az apim delete --name $APIM_NAME --resource-group $RESOURCE_GROUP --yes
}

# Usage
usage() {
  echo "Usage: $0 [deploy|undeploy]"
  exit 1
}

# Main
case "$1" in
  deploy)
    deploy_apim
    deploy_api
    deploy_cert
    deploy_policy
    ;;
  undeploy)
    undeploy_apim
    ;;
  *)
    usage
    ;;
esac 