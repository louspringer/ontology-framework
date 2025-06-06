# Spore Validation Framework

> **Note:** For a detailed explanation of the "spore" concept, its purpose, and its role in ontology governance, see [SPORE_CONCEPT.md](./SPORE_CONCEPT.md).

## 📚 Documentation Index

- [DRY Scientific Overview](docs/architecture/BFG9K_DRY_OVERVIEW.md)
- [Spore Concept & Governance](SPORE_CONCEPT.md)
- [MCP & BFG9K Architecture](docs/architecture/bfg9k_mcp_architecture.md)
- [MCP Validator Structure](docs/architecture/mcp_validator_structure.md)
- [Cursor IDE, LLM, and BFG9K_MCP Integration](docs/architecture/CURSOR_BFG9K_INTEGRATION.md)
- [Navigation Diagram (with links)](docs/architecture/BFG9K_DOC_NAVIGATION.md)

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

Install using conda:

```bash
conda env create -f environment.yml
conda activate ontology-framework
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

## ⚠️ Configuration Portability Note

- **Avoid absolute paths in configuration files.** Use relative paths (e.g., `./bfg9k_mcp.py`, `./src`) to ensure portability across different environments and operating systems.
- **Always run commands from the project root directory.** This ensures that all relative paths in configuration files resolve correctly.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ontology-framework.git
   cd ontology-framework
   ```

2. Install pre-commit hooks:
   ```bash
   conda install pre-commit
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

# Spore Validation Framework Overview

This framework provides tools for validating spore instances against governance rules and transformation patterns, ensuring compliance with the Spore Governance Discipline.

## Overview

The validation framework implements the Spore Governance Discipline by checking spore instances for:
- Pattern registration via `meta:TransformationPattern`
- SHACL validation support
- Runtime feedback through `meta:distributesPatch`
- Conformance tracking via `meta:confirmedViolation`
- Propagation and reintegration of corrections via `meta:ConceptPatch`

## Installation

1. Create and activate the conda environment:
```bash
conda env create -f environment.yml
conda activate ontology-framework
```

## Usage

### Basic Validation

```python
from spore_validation import SporeValidator

validator = SporeValidator()
spore_uri = "http://example.org/spores/example-spore"
results = validator.validate_spore(spore_uri)

print(results)
```

### Running Tests

```bash
python -m pytest test_spore_validation.py -v
```

## Validation Rules

The framework validates spore instances against the following governance rules:

1. **Pattern Registration**
   - Spore must be registered as a `meta:TransformationPattern`
   - Must have proper type assertions
   - Must be properly documented with labels and comments

2. **SHACL Validation**
   - Must have associated SHACL shapes
   - Shapes must target the spore class
   - Validation rules must be properly defined
   - Must support runtime validation

3. **Patch Support**
   - Must support patch distribution via `meta:distributesPatch`
   - Patches must be of type `meta:ConceptPatch`
   - Must support propagation and reintegration of corrections
   - Must maintain patch history and versioning

4. **Conformance Tracking**
   - Must track conformance violations via `meta:confirmedViolation`
   - Must support LLM or system-evaluated conformance
   - Must document remediation paths
   - Must maintain violation history

# Ontology Validation Workflow

## Recommended Validation Steps

To ensure robust and DRY ontology management, follow this two-step validation process:

### 1. Prefix Validation and Fixing
- **Tool:** `fix_prefixes_tool`
- **Purpose:** Ensures all prefixes are absolute IRIs and well-formed.
- **How to use:**
  - **Dry run:** Preview changes without modifying the file.
    ```bash
    # Example (dry run)
    fix_prefixes_tool <your_file.ttl>
    ```
  - **Apply fixes:**
    ```bash
    # Example (apply fixes)
    fix_prefixes_tool --apply <your_file.ttl>
    ```
- **Why:** Relative or malformed prefixes will cause errors in downstream validation and reasoning tools. Fixing them first prevents cascading issues.

### 2. Full Ontology Validation
- **Tool:** `validate_turtle_tool`
- **Purpose:** Checks Turtle syntax, semantic consistency, SHACL/OWL rules, and more.
- **How to use:**
    ```bash
    validate_turtle_tool <your_file.ttl>
    ```
- **Why:** Ensures your ontology is valid, consistent, and ready for use in the framework. This step assumes prefixes are already correct.

---

## Why This Order?
- **Prefix issues** are a common source of validation failure. Fixing them first makes the main validation step more reliable and actionable.
- **Iterative improvement:** This workflow is robust and can be automated in the future if needed, based on real-world usage and pain points.

---

## When to Revisit
- If prefix issues become a bottleneck or are frequently forgotten, consider integrating prefix fixing into the main validation tool or creating a wrapper script.
- For now, this two-step process is recommended for reliability and clarity.

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes with appropriate type and version:
   ```bash
   git commit -m "onto(scope): description
   
   Ontology-Version: X.Y.Z"
   ```
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

# GraphDB on Azure Container Apps

This repository contains deployment scripts for running Ontotext GraphDB on Azure Container Apps (ACA) in a development environment.

## Prerequisites

- Azure CLI installed and configured
- Azure subscription with permissions to create:
  - Resource Groups
  - Storage Accounts
  - Container Apps
  - Container Apps Environments

## Deployment Steps

1. Make the deployment script executable:
   ```bash
   chmod +x deploy-graphdb.sh
   ```

2. Run the deployment script:
   ```bash
   ./deploy-graphdb.sh
   ```

The script will:
- Create a resource group
- Set up Azure Files storage
- Create a Container Apps environment
- Deploy GraphDB with persistent storage
- Configure HTTPS ingress
- Set up basic authentication

## Configuration Details

### Storage
- Azure Files is mounted at `/opt/graphdb/home`
- Storage account uses Standard_LRS SKU
- File share name: `graphdbdata`

### Container App
- Image: ontotext/graphdb:10.4.1
- Port: 7200
- Memory: 2GB heap size
- Authentication: Basic auth
- Default credentials:
  - Username: admin
  - Password: graphdb-dev-password

### Network
- External HTTPS ingress enabled
- Custom domain name provided by Azure Container Apps
- No VNet integration required

## Accessing GraphDB

Once deployed, you can access GraphDB through:
1. Web interface: `https://<container-app-dns>`
2. REST API: `https://<container-app-dns>/repositories`

### Testing the Connection

```bash
curl -X GET https://<container-app-dns>/repositories -u admin:graphdb-dev-password
```

## Security Notes

- Basic authentication is enabled by default
- HTTPS is enforced
- Storage account uses Azure's built-in encryption
- Consider implementing IP restrictions if needed

## Cleanup

To remove all resources:
```bash
az group delete --name graphdb-dev-rg --yes
```

## Limitations

- This setup is for development purposes only
- Single instance deployment
- No high availability
- Basic authentication only
- No custom domain configuration

## Cost Optimization

- Uses Standard_LRS storage for cost efficiency
- Single instance deployment
- No additional services (API Gateway, etc.)
- Auto-scaling disabled
