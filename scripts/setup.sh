#!/bin/bash

# Exit on error
set -e

echo "Setting up ontology-framework development environment..."

# Create required directories
mkdir -p data/graphdb

# Install package in development mode
echo "Installing package in development mode..."
pip install -e .

# Install package with pipx for isolated environment
echo "Installing package with pipx..."
pipx install -e .

# Start required services
echo "Starting GraphDB service..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for GraphDB to be ready..."
until curl -s http://localhost:7200/rest/repositories > /dev/null; do
    echo "Waiting for GraphDB..."
    sleep 5
done

echo "GraphDB is ready!"

# Create test repository
echo "Creating test repository..."
curl -X POST -H "Content-Type: application/json" -d '{
  "id": "test",
  "type": "graphdb:FreeSailRepository",
  "title": "Test Repository",
  "params": {
    "ruleset": "rdfsplus-optimized",
    "query-timeout": 0,
    "query-limit-results": 0,
    "check-for-inconsistencies": false,
    "disable-sameAs": true,
    "enable-context-index": true,
    "enablePredicateList": true,
    "enable-fts-index": true,
    "fts-indexes": [
      {
        "predicates": [
          "http://www.w3.org/2000/01/rdf-schema#label",
          "http://www.w3.org/2004/02/skos/core#prefLabel",
          "http://www.w3.org/2004/02/skos/core#altLabel"
        ],
        "minWordLength": 3,
        "stopWords": [],
        "caseSensitive": false,
        "language": "en"
      }
    ]
  }
}' http://localhost:7200/rest/repositories

echo "Setup complete! You can now run the tests with:"
echo "python -m pytest tests/" 