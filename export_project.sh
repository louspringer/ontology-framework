#!/bin/bash

# Create a temporary directory for the export
EXPORT_DIR="ontology-framework-export"
mkdir -p "$EXPORT_DIR"

# Copy Python source files
cp -r src "$EXPORT_DIR/"
cp -r tests "$EXPORT_DIR/"
cp -r scripts "$EXPORT_DIR/"

# Copy configuration files
cp pyproject.toml "$EXPORT_DIR/"
cp requirements.txt "$EXPORT_DIR/"
cp requirements-test.txt "$EXPORT_DIR/"
cp pytest.ini "$EXPORT_DIR/"
cp setup.py "$EXPORT_DIR/"

# Copy ontology files
cp *.ttl "$EXPORT_DIR/" 2>/dev/null || true

# Copy documentation
cp *.md "$EXPORT_DIR/" 2>/dev/null || true

# Create a clean archive
tar -czf ontology-framework.tar.gz "$EXPORT_DIR"

# Clean up
rm -rf "$EXPORT_DIR"

echo "Project exported to ontology-framework.tar.gz"
echo "To import on the new machine:"
echo "1. Copy ontology-framework.tar.gz to the new machine"
echo "2. Extract: tar -xzf ontology-framework.tar.gz"
echo "3. Create a new virtual environment: python -m venv venv"
echo "4. Activate the environment: source venv/bin/activate"
echo "5. Install dependencies: pip install -r requirements.txt"
echo "6. Install test dependencies: pip install -r requirements-test.txt" 