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

# Function to create directory structure
create_directory_structure() {
    echo "Creating directory structure..."
    
    # Main directories
    mkdir -p src/ontologies/{base,domain,transform}
    mkdir -p docs/{architecture,transformations,contributing}
    mkdir -p tests
    mkdir -p examples
    mkdir -p .github/{workflows,templates}
}

# Function to create conda environment
create_conda_environment() {
    echo "Creating conda environment..."
    
    # Create environment from yml file
    cat > environment.yml << EOL
name: ontology-framework
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.11
  - pip
  - bzip2
  - ca-certificates
  - libexpat
  - libffi
  - libsqlite
  - libzlib
  - ncurses
  - openssl
  - readline
  - setuptools
  - tk
  - tzdata
  - wheel
  - xz
EOL

    # Create the conda environment
    conda env create -f environment.yml
}

# Function to initialize git repository
init_git_repository() {
    echo "Initializing git repository..."
    
    # Initialize git if not already initialized
    if [ ! -d ".git" ]; then
        git init
        
        # Create .gitignore
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
EOL
    fi
}

# Function to create initial documentation
create_documentation() {
    echo "Creating documentation..."
    
    # Create README.md
    cat > README.md << EOL
# Ontology Framework

A flexible ontology framework designed to leverage LLMs for semantic constraint enforcement and rich domain modeling capabilities, with lossless transformations between modeling formats.

## Overview

This framework provides:
- Semantic constraint enforcement for LLM responses
- Rich domain modeling with lossless transformations
- Tiered architecture promoting reuse
- Extensible model structures
- Multi-format projections (Turtle, UML, ERD, etc.)

## Installation

\`\`\`bash
# Create conda environment
conda env create -f environment.yml

# Activate environment
conda activate ontology-framework
\`\`\`

## License

MIT License - see LICENSE file for details.
EOL

    # Create LICENSE file
    cat > LICENSE << EOL
MIT License

Copyright (c) $(date +%Y)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOL
}

# Main execution
main() {
    # Check required commands
    check_command conda
    check_command git
    
    # Create directory structure
    create_directory_structure
    
    # Create conda environment
    create_conda_environment
    
    # Initialize git repository
    init_git_repository
    
    # Create documentation
    create_documentation
    
    echo -e "${GREEN}Setup complete!${NC}"
    echo "Next steps:"
    echo "1. Run: conda activate ontology-framework"
    echo "2. Review the created directory structure and documentation"
    echo "3. Begin adding your ontologies to src/ontologies/"
}

# Run main function
main 