#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up Ontology Framework...${NC}"

# Function to check if a command exists
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}Error: $1 is not installed${NC}"
        exit 1
    fi
}

# Check required commands
check_command conda
check_command python
check_command pip

# Create conda environment
echo "Creating conda environment..."
conda env create -f environment.yml

# Activate environment
echo "Activating environment..."
conda activate ontology-framework

# Install package in development mode
echo "Installing package in development mode..."
pip install -e .

# Create necessary directories
echo "Creating directory structure..."
mkdir -p src/ontologies/{base,domain,transform}
mkdir -p docs/{architecture,transformations,contributing}
mkdir -p tests
mkdir -p examples
mkdir -p .github/{workflows,templates}

# Initialize git if not already initialized
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
fi

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "Creating .gitignore..."
    cat > .gitignore << EOL
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment
.env
.venv
env/
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
logs/

# Data
data/

# Test files
test.ttl
test_checkin.py

# Config
boldo_config.ttl
EOL
fi

echo -e "${GREEN}Setup completed successfully!${NC}"
echo "To start using the framework:"
echo "1. Activate the conda environment: conda activate ontology-framework"
echo "2. Run the CLI: ontology --help"
echo "3. Run MCP: mcp --help" 