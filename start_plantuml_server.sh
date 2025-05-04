#!/bin/bash

# Simple script to start the PlantUML server directly
# This is useful for development or quick testing without Docker

# Check if PlantUML JAR is available
if [ ! -f "plantuml.jar" ]; then
    echo "PlantUML JAR not found. Downloading..."
    wget -O plantuml.jar https://github.com/plantuml/plantuml/releases/download/v1.2024.4/plantuml-1.2024.4.jar
fi

# Check if Java is available
if ! command -v java &> /dev/null; then
    echo "Java is required but not found. Please install Java 11 or higher."
    exit 1
fi

# Start the PlantUML server
echo "Starting PlantUML server on http://localhost:20075"
echo "Press Ctrl+C to stop the server"
java -jar plantuml.jar -picoweb:20075 