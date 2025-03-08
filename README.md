# Ontology Framework

A framework for managing and validating ontologies with support for both local and Oracle RDF storage.

## Features

- Consistent prefix and namespace management
- Local and Oracle RDF store support
- Pre-commit hooks for ontology validation
- SHACL validation support
- Automated testing infrastructure

## Requirements

### Python Dependencies

Install using conda (recommended):

```bash
conda env create -f environment.yml
conda activate ontology-framework
```

Or using pip:

```bash
pip install -r requirements.txt
```

### Oracle RDF Store Requirements

To use the Oracle RDF store functionality:

1. Oracle Database with RDF support
2. Java must be installed and configured in the Oracle database
3. Required environment variables:
   - `ORACLE_USER`: Database username
   - `ORACLE_PASSWORD`: Database password
   - `ORACLE_DSN`: Database connection string

To verify Oracle setup:

```bash
python -m scripts.verify_oracle_setup
```

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ontology-framework.git
   cd ontology-framework
   ```

2. Install pre-commit hooks:
   ```bash
   pip install pre-commit
   pre-commit install
   ```

3. Run tests:
   ```bash
   pytest tests/
   ```

## Ontology Development

### Prefix Management

The framework provides consistent prefix management through the `PrefixMap` class:

```python
from ontology_framework.prefix_map import default_prefix_map

# Get standard namespace
meta_ns = default_prefix_map.get_namespace("meta")

# Register custom prefix
default_prefix_map.register_prefix("custom", "./custom#", PrefixCategory.DOMAIN)

# Bind prefixes to graph
g = Graph()
default_prefix_map.bind_to_graph(g)
```

### Pre-commit Hooks

The following checks are run on commit:

1. Python code formatting (black)
2. Import sorting (isort)
3. Python code quality (flake8)
4. Ontology validation:
   - Required prefixes
   - Class property requirements
   - SHACL constraints

### Ontology Validation

Ontologies must follow these rules:

1. Use standard prefixes from `prefix_map.py`
2. Include required properties:
   - `rdfs:label`
   - `rdfs:comment`
   - `owl:versionInfo`
3. Pass SHACL validation if shapes are defined

## Contributing

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make changes and ensure all tests pass:
   ```bash
   pytest tests/
   ```

3. Commit with appropriate type and version:
   ```bash
   git commit -m "onto(scope): description

   Ontology-Version: X.Y.Z"
   ```

## License

[Your license here]
