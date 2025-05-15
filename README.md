# Spore Validation Framework

> **Note:** For a detailed explanation of the "spore" concept, its purpose, and its role in ontology governance, see [SPORE_CONCEPT.md](./SPORE_CONCEPT.md).

## 📚 Documentation Index

- [DRY Scientific Overview](docs/architecture/BFG9K_DRY_OVERVIEW.md)
- [Spore Concept & Governance](SPORE_CONCEPT.md)
- [MCP & BFG9K Architecture](docs/architecture/bfg9k_mcp_architecture.md)
- [MCP Validator Structure](docs/architecture/mcp_validator_structure.md)
- [Cursor IDE, LLM, and BFG9K_MCP Integration](docs/architecture/CURSOR_BFG9K_INTEGRATION.md)
- [Navigation Diagram (with links)](docs/architecture/BFG9K_DOC_NAVIGATION.md)

This framework provides tools for validating spore instances against governance rules and transformation patterns, ensuring compliance with the Spore Governance Discipline.

## Overview

The validation framework implements the Spore Governance Discipline by checking spore instances for:
- Pattern registration via `meta:TransformationPattern`
- SHACL validation support
- Runtime feedback through `meta:distributesPatch`
- Conformance tracking via `meta:confirmedViolation`
- Propagation and reintegration of corrections via `meta:ConceptPatch`

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
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

For more details or to suggest improvements, see the `CONTRIBUTING.md` or open an issue.
