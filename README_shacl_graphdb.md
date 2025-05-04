# SHACL and GraphDB Management Tools

This package provides tools for managing SHACL constraints and GraphDB materialized inference, addressing common challenges when working with semantic web technologies.

## Key Tools

1. **`update_shacl_and_reload.py`**: Safely update SHACL constraints and reload data into GraphDB
2. **`manage_inference.py`**: Manage materialized inference in GraphDB repositories

## Common Challenges Addressed

These tools help solve the following common challenges:

1. **Materialized Inference Conflicts**: When GraphDB materializes inferences, SPARQL updates to the original triples may not affect inferred triples
2. **SHACL Validation Loops**: Circular dependencies between validation rules and the data they validate
3. **Clean Repository Management**: Managing explicit vs. inferred statements separately

## Using `update_shacl_and_reload.py`

This script provides a clean workflow for updating SHACL constraints:

```bash
# Basic usage - update ontology with new shapes
python update_shacl_and_reload.py --ontology guidance.ttl --shapes shacl_shapes.ttl

# Save to a different output file
python update_shacl_and_reload.py --ontology guidance.ttl --shapes shacl_shapes.ttl --output updated_guidance.ttl

# Specify a different GraphDB server or repository
python update_shacl_and_reload.py --ontology guidance.ttl --shapes shacl_shapes.ttl \
  --graphdb-url http://graphdb.example.com:7200 --repository my-repo

# Skip the GraphDB reload step
python update_shacl_and_reload.py --ontology guidance.ttl --shapes shacl_shapes.ttl --no-reload

# Use a specific named graph (context)
python update_shacl_and_reload.py --ontology guidance.ttl --shapes shacl_shapes.ttl \
  --graph-uri http://example.org/shapes
```

### Key Features

- **Local Validation**: Validates SHACL constraints locally before applying
- **Staging Repository**: Tests changes in a staging repository before affecting the main one
- **Clean Shape Updates**: Properly removes old shapes before adding new ones
- **Safe GraphDB Reload**: Handles GraphDB clearing and reloading correctly

## Using `manage_inference.py`

This script helps manage materialized inference in GraphDB:

```bash
# Disable inference for a repository
python manage_inference.py --repository my-repo disable

# Enable inference with a specific ruleset
python manage_inference.py --repository my-repo enable --ruleset owl-horst-optimized

# Clear only inferred statements (keeps explicit statements)
python manage_inference.py --repository my-repo clear-inferred

# Get counts of explicit vs. inferred statements
python manage_inference.py --repository my-repo count

# Export repository data without inferences
python manage_inference.py --repository my-repo export --output data_no_inference.ttl
```

### Key Features

- **Ruleset Management**: Temporarily disable/enable inference
- **Smart Clearing**: Remove only inferred statements while preserving explicit triples
- **Statement Analysis**: Separate and count explicit vs. inferred statements
- **Clean Export**: Export data without materialized inferences

## Workflow for Updating SHACL Shapes

For the most reliable updates when working with SHACL shapes and GraphDB:

1. **Count statements** to understand your data:
   ```bash
   python manage_inference.py count
   ```

2. **Clear inferred statements** to start clean:
   ```bash
   python manage_inference.py clear-inferred
   ```

3. **Update SHACL constraints** in a safe way:
   ```bash
   python update_shacl_and_reload.py --ontology your_ontology.ttl --shapes your_shapes.ttl
   ```

4. **Re-enable inference** if needed:
   ```bash
   python manage_inference.py enable
   ```

## Handling Large Ontologies

For very large ontologies, additional strategies are implemented:

1. **Context-Based Loading**: Use named graphs for better separation
2. **Temporary Disable Inference**: Speeds up loading and updates
3. **Incremental Updates**: Process changes in smaller batches

## Common Issues

### Stale Inferences

If you see stale or inconsistent inferences:

```bash
# Clear only inferred statements
python manage_inference.py clear-inferred

# Then reload with inference enabled
python update_shacl_and_reload.py --ontology your_ontology.ttl --shapes your_shapes.ttl
```

### SHACL Validation Errors

If you're getting SHACL validation errors:

1. **Validate locally** first to debug:
   ```bash
   python update_shacl_and_reload.py --ontology your_ontology.ttl --shapes your_shapes.ttl --no-reload
   ```

2. **Check for circular dependencies** in your shapes

3. **Inspect the log** for detailed validation messages

## Requirements

- Python 3.8+
- RDFLib
- PySHACL
- Requests

## See Also

- [GraphDB Documentation](http://graphdb.ontotext.com/documentation/)
- [SHACL W3C Specification](https://www.w3.org/TR/shacl/)
- [RDFLib Documentation](https://rdflib.readthedocs.io/) 