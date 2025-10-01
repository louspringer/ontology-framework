# Technology Stack

## Core Technologies
- **Python 3.8+**: Primary development language
- **RDFLib**: Core RDF/OWL processing and manipulation
- **SHACL (pySHACL)**: Ontology validation and constraint checking
- **GraphDB**: Primary triple store (Ontotext GraphDB 10.4+)
- **Oracle RDF**: Alternative enterprise RDF backend
- **Docker & Docker Compose**: Containerization and orchestration

## Development Environment
- **Conda**: Recommended package manager (`environment.yml`)
- **pip**: Alternative package manager (`requirements.txt`)
- **Pre-commit**: Code quality and ontology validation hooks
- **pytest**: Testing framework with coverage reporting
- **Black**: Code formatting
- **isort**: Import sorting
- **MyPy**: Type checking

## Build System
- **setuptools**: Python package building
- **Azure Container Registry (ACR)**: Container image registry
- **Multi-platform builds**: Support for linux/amd64

## Common Commands

### Environment Setup
```bash
# Conda (recommended)
conda env create -f environment.yml
conda activate ontology-framework

# Or pip
pip install -r requirements.txt
```

### Development
```bash
# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/

# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/
```

### AI-Assisted Development
```bash
# Start enhanced MCP server
python -m ontology_framework.mcp.enhanced_server

# Generate ontology from description
python -c "from ontology_framework.ai_assistant.ontology_generator import OntologyGenerator; og = OntologyGenerator(); print(og.generate_from_description('A library system with books and authors'))"

# Generate Python classes from ontology
python -c "from ontology_framework.developer_experience.code_generator import CodeGenerator; cg = CodeGenerator(); cg.generate_python_classes('ontology.ttl')"
```

### Validation Workflow
```bash
# 1. Fix prefixes first (dry run)
fix_prefixes_tool <file.ttl>

# 2. Apply prefix fixes
fix_prefixes_tool --apply <file.ttl>

# 3. Full validation
validate_turtle_tool <file.ttl>

# 4. Advanced semantic validation
python -c "from ontology_framework.validation.advanced_validator import AdvancedValidator; av = AdvancedValidator(); print(av.semantic_consistency_check(graph))"
```

### CI/CD Operations
```bash
# Run full CI/CD pipeline
python -c "from ontology_framework.integration.ci_cd_pipeline import CICDPipeline; pipeline = CICDPipeline(); pipeline.run_pipeline(['ontology.ttl'])"

# Generate GitHub workflow
python -c "from ontology_framework.integration.ci_cd_pipeline import CICDPipeline; pipeline = CICDPipeline(); pipeline.generate_github_workflow('.')"

# Analyze change impact
python -c "from ontology_framework.collaboration.change_impact import ChangeImpactAnalyzer; cia = ChangeImpactAnalyzer(); cia.analyze_change_impact(old_graph, new_graph)"
```

### Docker Operations
```bash
# Start full stack
docker-compose up -d

# Build specific service
docker-compose build bfg9k-mcp

# View logs
docker-compose logs -f graphdb
```

### Container Builds
```bash
# Local build
./build.sh local linux/amd64 Dockerfile.bfg9k bfg9k-mcp latest

# ACR build
./build.sh acr linux/amd64 Dockerfile.bfg9k bfg9k-mcp
```

## Configuration Notes
- **Always use relative paths** in configuration files for portability
- **Run commands from project root** to ensure path resolution
- **Environment variables**: Use `.env` file for local configuration
- **Oracle setup**: Requires `ORACLE_USER`, `ORACLE_PASSWORD`, `ORACLE_DSN`