# Project Structure

## Root Directory Organization

### Core Configuration
- `pyproject.toml` - Python project configuration and dependencies
- `requirements.txt` - pip dependencies
- `environment.yml` - Conda environment specification
- `setup.py` - Package setup and entry points
- `pytest.ini` - Test configuration with coverage settings
- `.pre-commit-config.yaml` - Code quality and validation hooks

### Docker & Deployment
- `Dockerfile*` - Multiple Dockerfiles for different services
- `docker-compose.yml` - Multi-service orchestration
- `build.sh` - Container build script with ACR support
- `deploy-*.sh` - Azure deployment scripts

### Documentation
- `README.md` - Main project documentation
- `SPORE_CONCEPT.md` - Core concept explanation
- `docs/` - Detailed documentation and architecture diagrams
- `*.md` files - Various domain-specific documentation

## Source Code Structure (`src/ontology_framework/`)

### Core Modules
- `__init__.py` - Package initialization
- `cli.py` - Command-line interface
- `prefix_map.py` - Namespace and prefix management
- `ontology_validator.py` - Core validation logic
- `spore_validation.py` - Spore governance validation

### Specialized Directories
- `ai_assistant/` - AI-powered development tools (chat, SPARQL generation, pattern recognition)
- `api/` - REST API components
- `apps/` - Application-specific modules
- `cli/` - Command-line interface components
- `collaboration/` - Team collaboration tools (reviews, change impact, conflict resolution)
- `config/` - Configuration management
- `developer_experience/` - Developer tools (code generation, templates, migration)
- `integration/` - CI/CD pipelines, deployment, and monitoring
- `mcp/` - Model Context Protocol implementation (basic and enhanced servers)
- `model/` - Data models and schemas
- `modules/` - Modular ontology components
- `tools/` - Utility scripts and tools
- `validation/` - Validation frameworks and rules (basic and advanced)
- `visualization/` - Diagram and visualization tools

### Data Storage
- `ontologies/` - Ontology definitions (.ttl files)
- `tests/` - Test suites and fixtures
- `examples/` - Usage examples and templates

## File Naming Conventions

### Python Files
- `snake_case.py` - Standard Python naming
- `test_*.py` - Test files (pytest discovery)
- `*_validator.py` - Validation modules
- `*_client.py` - Client/interface modules

### Ontology Files
- `*.ttl` - Turtle RDF format (preferred)
- `*.rdf` - RDF/XML format
- `*.owl` - OWL ontologies
- Descriptive names reflecting domain/purpose

### Configuration Files
- `*.yml`/`*.yaml` - YAML configuration
- `*.json` - JSON configuration
- `*.toml` - TOML configuration (Python projects)

## Key Directories

### `/scripts/` - Utility Scripts
- Standalone Python scripts for maintenance tasks
- Database setup and migration scripts
- Validation and testing utilities

### `/infrastructure/` - Deployment Code
- `azure/` - Azure-specific deployment
- `graphdb/` - GraphDB configuration
- `oracle/` - Oracle RDF setup

### `/models/` - Domain Models
- Ontology models organized by domain
- Recovery and maintenance plans
- Validation patterns

### `/guidance/` - Framework Guidance
- Modular guidance components
- Framework-specific rules and patterns

## Import Patterns
- Use relative imports within the package
- Absolute imports from `src/ontology_framework`
- CLI entry points defined in `pyproject.toml`

## Testing Structure
- Tests mirror source structure in `tests/`
- Integration tests in `tests/integration/`
- Unit tests alongside modules
- Fixtures in `tests/fixtures/`