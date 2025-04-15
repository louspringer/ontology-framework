# Spore Validation Framework

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
