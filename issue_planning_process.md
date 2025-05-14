# Issue Planning Process

## Overview
A systematic approach to analyze GitHub issues and create structured plans with ontological foundations.

## Process Steps

### 1. Issue Analysis 🔍
**Produces**: Issue Inventory

- List all existing GitHub issues
- Categorize by type and scope
- Extract key requirements and constraints
- Identify common patterns
- Document issue metadata

### 2. Ontology Mapping 🗺️
**Requires**: Issue Inventory
**Produces**: Ontology Map

- Map issues to existing ontology concepts
- Identify gaps in ontology coverage
- Create new ontology terms as needed
- Document semantic relationships
- Validate mappings for consistency

### 3. Plan Creation 📝
**Requires**: Ontology Map
**Produces**: Issue Plans

- Create TTL representation for each issue
- Generate markdown documentation
- Define success criteria
- Outline implementation steps
- Add validation requirements (must be derived from the central validation pipeline and guidance.ttl; see validation/fix tool documentation for authoritative requirements and traceability)

### 4. Dependency Analysis 🔗
**Requires**: Issue Plans
**Produces**: Dependency Graph

- Identify dependencies between issues
- Create dependency visualization
- Document blocking relationships
- Identify parallel work opportunities
- Flag critical path items

### 5. Priority Assignment ⭐
**Requires**: Dependency Graph
**Produces**: Prioritized Plans

- Assign priority levels
- Create implementation timeline
- Balance resource constraints
- Document rationale for priorities
- Set milestone targets

## Artifacts

### Issue Inventory

- Complete list of issues
- Categorization scheme
- Initial metadata analysis
- Pattern documentation

### Ontology Map

- Issue-to-concept mappings
- New ontology terms
- Relationship definitions
- Validation rules

### Issue Plans

- TTL representations
- Markdown documentation
- Implementation steps
- Success criteria

### Dependency Graph

- Visual dependency map
- Critical path analysis
- Parallel work options
- Blocking relationships

### Prioritized Plans

- Priority assignments
- Implementation timeline
- Resource allocations
- Milestone definitions

## Success Criteria

- ✓ All issues mapped to ontology concepts
- ✓ Each issue has TTL and MD plans
- ✓ Dependencies clearly documented
- ✓ Priorities assigned with rationale
- ✓ Implementation timeline established 

## Validation Requirements Traceability

All validation requirements for issue plans must be:
- Derived from the central validation pipeline and `guidance.ttl`
- Documented in both the TTL and markdown representations
- Linked to the validation/fix tools as the source of truth
- Versioned and traceable for audit and compliance

See [Validation Procedures](docs/validation_procedures.md) and the CLI/MCP tool documentation for details. 