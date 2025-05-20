#!/bin/bash

# Install wasm-pack if not already installed
if ! command -v wasm-pack &> /dev/null; then
    curl https://rustwasm.github.io/wasm-pack/installer/init.sh -sSf | sh
fi

# Build the WASM module
cd "$(dirname "$0")"
wasm-pack build --target web

# Move the built files to the correct location
mkdir -p ../static/wasm
cp pkg/bfg9k_rdf_engine_bg.wasm ../static/wasm/bfg9k_rdf_engine.wasm
cp pkg/bfg9k_rdf_engine.js ../static/wasm/bfg9k_rdf_engine.js

echo "WASM module built successfully" 