#!/bin/bash
set -e

echo "Setting up Prompt Manager..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Ensure we're in the conda environment
eval "$(conda shell.bash hook)"
conda activate ontology-framework

# Start Docker services
docker-compose up -d

echo "Setup complete! Waiting for database to be ready..."
sleep 5

# Test the connection
python3 -c "from src.prompt_manager import PromptManager; PromptManager()"

echo "System is ready! Try adding your first prompt:"
echo "python -m src.prompt_cli add interpret-ontology interpret-ontology.prompt --category ontology --tags ontology analysis" 