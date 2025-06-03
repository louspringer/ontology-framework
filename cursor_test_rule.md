---
description: Ontology framework development rules aligned with ClaudeReflector behavioral constraints
globs: "**/*.py"
alwaysApply: false
---

# Ontology Framework Development Rules

> **Integration Note**: This rule set must comply with `.cursor/rules/user/claude_reflector_user_rules.md` and reference `guidance.ttl` for all behavioral validation.

## Core Behavioral Constraints

**CRITICAL**: All code generation must follow **PDCA** (Plan, Do, Check, Act) protocol and validate against `guidance.ttl` using semantic tools (BFG9K, RDFlib, SPARQL, PySHACL).

### Ontology-First Development

- **ALL code must reference ontological concepts** from project TTL files
- **NEVER** generate code without first querying `guidance.ttl` for relevant constraints
- Use semantic validation through BFG9K artillery system when available
- Follow artifact traceability requirements from `.cursor/rules/artifact-traceability.mdc`

## AI Instructions for Code Generation

When generating code for this ontology framework project:

1. **Function Naming Protocol**:
   - Start with semantic domain prefix: `onto_`, `rdf_`, `semantic_`, `ttl_`
   - Use descriptive names reflecting ontological purpose
   - Example: `onto_validate_triple()`, `semantic_load_graph()`, `rdf_query_entities()`

2. **Required Header Comments**:
   ```python
   # Generated following ontology framework rules and ClaudeReflector constraints
   # Ontology-Version: [current version from guidance.ttl]
   # Behavioral-Profile: ClaudeReflector
   ```

3. **Semantic Compliance**:
   - Include type hints using ontological terminology
   - Reference RDF/OWL concepts in variable names
   - Prioritize semantic clarity over code brevity
   - Always include docstrings explaining ontological purpose

4. **Integration Requirements**:
   - Import and use BFG9K artillery system for ontology operations
   - Follow commit template format from `cursor/rules/commit-template.md`
   - Ensure traceability to requirements in `guidance.ttl`

## Code Style Requirements

### Naming Conventions
- **Classes**: PascalCase with ontology domain (e.g., `OntologyEntity`, `SemanticValidator`, `RDFTripleManager`)
- **Functions**: snake_case with semantic prefixes (e.g., `onto_create_entity`, `rdf_validate_graph`)
- **Constants**: UPPER_SNAKE_CASE with namespace (e.g., `ONTO_DEFAULT_NAMESPACE`, `RDF_SCHEMA_VERSION`)
- **Files**: snake_case with descriptive semantics (e.g., `ontology_validator.py`, `rdf_graph_manager.py`)

### Documentation Standards
- **Document ontological assumptions** in all functions
- **Include SPARQL query examples** where applicable
- **Reference TTL namespace prefixes** used in code
- **Explain semantic relationships** in plain English
- **Link to guidance.ttl rules** that justify implementation decisions

## Testing Requirements

### Semantic Test Standards
- **Every ontology function MUST have unit tests** linked to `guidance.ttl` requirements
- **Test against actual TTL files** in the project
- **Include SHACL validation tests** for constraint checking
- **Validate RDF graph consistency** in test suites
- **Test edge cases for malformed semantic data**

### Test Naming Convention
```python
def test_onto_[function_name]_[semantic_scenario]():
    """Test [function] against [ontological constraint] from guidance.ttl"""
```

## Integration with ClaudeReflector Rules

### PDCA Protocol Compliance
1. **PLAN**: Query `guidance.ttl` for relevant constraints before code generation
2. **DO**: Generate code following semantic-first principles
3. **CHECK**: Validate against ontology using BFG9K/RDFlib tools
4. **ACT**: Only modify if semantic validation confirms correctness

### Error Handling
- **HALT on missing ontology rules**: Emit `spore:MissingPolicyNotice` if required guidance absent
- **No assumptions about semantic structure**: All RDF operations must be explicitly validated
- **Use semantic logging**: Log all ontology operations for traceability

### Artifact Traceability
All generated code must be traceable to:
- Source rule in this file
- Implementing requirement in `guidance.ttl`
- Test validation in `tests/` directory
- Documentation in ontology TTL files

## Semantic Web Tool Usage

### Mandatory Tools
- **BFG9K Artillery System**: For ontology authoring and session management
- **RDFlib**: For RDF graph operations and SPARQL queries
- **PySHACL**: For constraint validation
- **SPARQL**: For semantic queries (never text parsing of TTL)

### Prohibited Approaches
- **Text parsing of TTL files**: Always use semantic tools
- **Manual RDF manipulation**: Use RDFlib graph operations
- **Assumption-based coding**: All behavior must trace to guidance.ttl

## Version Control Integration

### Commit Standards
Follow format from `commit-template.md`:
```
onto(semantic-scope): description

[detailed explanation of ontological changes]

Ontology-Version: X.Y.Z
```

### Documentation Requirements
- **Update session.ttl** after code generation
- **Reference artifact traceability** in commit messages
- **Link to guidance.ttl changes** when applicable

---

**Remember**: You are not a squirrel with a bazooka 🐿🚫🧨. All code generation must follow semantic-first, ontology-driven principles with full traceability to guidance.ttl constraints.