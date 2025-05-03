#!/bin/bash

# Set executable permissions on the Python script
chmod +x visualize_ontology.py

# Run the visualization script with enhanced visualization settings
./visualize_ontology.py guidance.ttl \
  --output ontology_relationships.svg \
  --show-labels \
  --relation-types subClassOf imports domain range type seeAlso \
  --layout hierarchical 