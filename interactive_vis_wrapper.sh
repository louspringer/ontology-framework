#!/bin/bash

# Set executable permissions on the Python scripts
chmod +x interactive_ontology_vis.py
chmod +x auto_reload_server.py

# Run the interactive visualization script
python interactive_ontology_vis.py guidance.ttl \
  --output interactive_ontology.html \
  --height "800px" \
  --width "100%" \
  --relation-types subClassOf imports domain range type seeAlso

# Start the auto-reloading server on port 8000
# This will automatically refresh the page when the HTML file changes
python auto_reload_server.py --port 8000 --watch interactive_ontology.html

# The server will run in the foreground, so the script will pause here
# Press Ctrl+C to stop the server 