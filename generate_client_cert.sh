#!/bin/bash

# Output file names
CERT_NAME=${CERT_NAME:-client-cert}
KEY_FILE=${KEY_FILE:-$CERT_NAME.key}
CERT_FILE=${CERT_FILE:-$CERT_NAME.crt}
PEM_FILE=${PEM_FILE:-$CERT_NAME.pem}

# Generate private key
echo "[INFO] Generating private key..."
openssl genrsa -out $KEY_FILE 2048

# Generate self-signed certificate
echo "[INFO] Generating self-signed certificate..."
openssl req -new -x509 -key $KEY_FILE -out $CERT_FILE -days 365 -subj "/CN=apim-client"

# Combine key and cert into PEM (for APIM upload and curl)
echo "[INFO] Creating PEM file..."
cat $KEY_FILE $CERT_FILE > $PEM_FILE

# Output summary
echo "[INFO] Certificate and key generated:"
echo "  Private key: $KEY_FILE"
echo "  Certificate: $CERT_FILE"
echo "  PEM bundle:  $PEM_FILE" 