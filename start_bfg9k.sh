#!/bin/bash

# Create logs directory if it doesn't exist
mkdir -p logs

# Start BFG9K server with logging
/usr/local/bin/bfg9k-server --config bfg9k_config.ttl \
    --log-file logs/bfg9k.log \
    --log-level DEBUG \
    --daemonize

# Check if server started successfully
if [ $? -eq 0 ]; then
    echo "BFG9K server started successfully"
    echo "Logs available at: logs/bfg9k.log"
else
    echo "Failed to start BFG9K server"
    exit 1
fi 