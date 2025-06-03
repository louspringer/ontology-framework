---
description: Enforce artifact traceability requirements across all project files
globs: "**/*"
alwaysApply: true
---

# Artifact Traceability Enforcement

> **Critical Function**: This rule enforces the artifact traceability standards defined in `cursor/rules/artifact-traceability.md` by ensuring every project artifact maintains proper ontological justification and session tracking.

## Core Traceability Principles

**FUNDAMENTAL**: Every artifact in the ontology framework project MUST be traceable to:
1. **Ontological justification** in guidance.ttl or domain ontologies
2. **Session documentation** in session.ttl
3. **Behavioral rules** that governed its creation
4. **Requirements** that necessitated its existence

### Universal Traceability Requirements

When creating, modifying, or referencing ANY project artifact, Cursor MUST:

1. **Identify ontological justification** from guidance.ttl
2. **Document creation/modification** in session.ttl
3. **Reference applicable behavioral rules** 
4. **Establish requirement linkage**
5. **Maintain traceability chain integrity**

## Artifact Classification and Traceability

### Code Artifacts
**Python Files (*.py)**:
```python
# Required traceability header
"""
Ontological Justification: guidance.ttl::SomeRequirement
Session Reference: session.ttl::CreationEvent_YYYYMMDD_HHMMSS
Behavioral Rules: [ClaudeReflector rules applied]
Artifact Type: PythonModule
"""
```

**Manifest Files (*.manifest.toml)**:
```toml
[requirements_traceability]
implements_requirements = ["guidance.ttl::SpecificRequirement"]
satisfies_constraints = ["guidance.ttl::BehavioralConstraint"]
artifact_type = "PythonModuleManifest"
justification_chain = "guidance.ttl::Requirement → session.ttl::Event → this.manifest"
```

### Configuration Artifacts
**Cursor Rules (*.mdc)**:
```yaml
---
description: Rule description with ontological purpose
ontological_justification: "guidance.ttl::RuleRequirement"
session_reference: "session.ttl::RuleCreationEvent"
enforces_constraints: ["guidance.ttl::BehavioralRule"]
---
```

**Environment Configs (*.json, *.yml)**:
```json
{
  "_traceability": {
    "ontological_justification": "guidance.ttl::EnvironmentRequirement",
    "session_reference": "session.ttl::ConfigCreationEvent",
    "behavioral_compliance": ["ClaudeReflector::EnvironmentControl"]
  }
}
```

### Documentation Artifacts
**Markdown Files (*.md)**:
```markdown
<!-- Traceability Metadata
Ontological Justification: guidance.ttl::DocumentationRequirement
Session Reference: session.ttl::DocCreationEvent
Behavioral Rules: [Applicable ClaudeReflector constraints]
-->
```

### Ontology Artifacts
**Turtle Files (*.ttl)**:
```turtle
# Traceability annotations
@prefix trace: <./traceability#> .

ex:ThisOntology a owl:Ontology ;
    trace:justifiedBy guidance:OntologyRequirement ;
    trace:sessionEvent session:OntologyCreationEvent ;
    trace:behavioralCompliance guidance:SemanticFirstPrinciple ;
    owl:versionInfo "0.1.0" .
```

## Session.ttl Integration Requirements

### Creation Event Documentation
Every artifact creation MUST generate a session entry:

```turtle
session:ArtifactCreation_YYYYMMDD_HHMMSS a trace:CreationEvent ;
    trace:createdArtifact artifact:SpecificArtifact ;
    trace:justifiedBy guidance:SomeRequirement ;
    trace:appliedRules (
        rules:OntologyFrameworkDevelopment
        rules:ClaudeReflectorConstraints
    ) ;
    trace:userRequest "Original user prompt" ;
    trace:timestamp "YYYY-MM-DDTHH:MM:SSZ" ;
    trace:pdcaPhase "DO" .

artifact:SpecificArtifact a trace:ProjectArtifact ;
    trace:artifactType "PythonModule" ;
    trace:filePath "./path/to/artifact" ;
    trace:ontologicalPurpose "Specific semantic function" ;
    trace:behavioralProfile "ClaudeReflector" .
```

### Modification Event Documentation
Every artifact modification MUST update session.ttl:

```turtle
session:ArtifactModification_YYYYMMDD_HHMMSS a trace:ModificationEvent ;
    trace:modifiedArtifact artifact:ExistingArtifact ;
    trace:previousVersion artifact:ExistingArtifact_v1 ;
    trace:justifiedBy guidance:ChangeRequirement ;
    trace:changeReason "Specific ontological necessity" ;
    trace:maintainsTraceability true .
```

## Traceability Validation Protocol

### Ontological Justification Validation
For every artifact, Cursor MUST verify:

1. **Guidance.ttl Reference Exists**:
   - Parse guidance.ttl using RDFlib
   - Query for the referenced requirement/constraint
   - Validate the justification is semantically valid

2. **Requirement Necessity**:
   - Confirm the ontological requirement necessitates this artifact
   - Check that the artifact serves the declared semantic purpose
   - Verify alignment with project's ontological goals

### Session Traceability Validation
For every artifact, Cursor MUST verify:

1. **Session Event Exists**:
   - Query session.ttl for the referenced creation/modification event
   - Validate timestamp consistency
   - Confirm event completeness

2. **Traceability Chain Integrity**:
   - Verify user request → requirement → artifact chain
   - Check behavioral rule application documentation
   - Ensure PDCA phase progression is logical

### Behavioral Rule Compliance
For every artifact, Cursor MUST verify:

1. **Applied Rules Documentation**:
   - Confirm all referenced behavioral rules exist in guidance.ttl
   - Validate rule application was appropriate for artifact type
   - Check compliance with ClaudeReflector constraints

2. **Ongoing Compliance**:
   - Verify artifact still complies with referenced rules
   - Check for behavioral drift since creation
   - Validate against current rule definitions

## Error Handling and Repair

### Missing Traceability Detection
When traceability validation fails, Cursor MUST:

1. **Categorize the Missing Traceability**:
   - `MISSING_ONTOLOGICAL_JUSTIFICATION`: No guidance.ttl reference
   - `BROKEN_SESSION_LINK`: session.ttl event missing or invalid
   - `UNDEFINED_BEHAVIORAL_RULES`: Referenced rules don't exist
   - `ORPHANED_ARTIFACT`: No clear purpose or requirement linkage

2. **Emit Structured Error**:
   ```turtle
   spore:TraceabilityViolation a spore:ValidationError ;
       spore:errorType "MISSING_ONTOLOGICAL_JUSTIFICATION" ;
       spore:affectedArtifact "path/to/artifact" ;
       spore:requiredAction "ESTABLISH_TRACEABILITY" ;
       spore:guidanceReference guidance:TraceabilityRequirement .
   ```

3. **Halt Processing**: Do not proceed until traceability established

### Automatic Traceability Repair
For certain violations, Cursor MAY attempt repair:

- **Generate missing session events** with appropriate metadata
- **Create traceability headers** in code files
- **Update manifest traceability sections** with current information
- **Establish guidance.ttl links** for clearly justified artifacts

### Manual Intervention Required
For critical violations, require explicit guidance:
- **Orphaned artifacts** with unclear ontological purpose
- **Conflicting justifications** between artifact and guidance.ttl
- **Missing requirements** that need guidance.ttl updates
- **Behavioral rule conflicts** requiring policy resolution

## Integration with Existing Rules

### ClaudeReflector Compliance
All traceability enforcement MUST follow:
- **PDCA Protocol**: Plan traceability → Document → Check integrity → Act on violations
- **Semantic-First Principle**: Use RDFlib/SPARQL for all ontology operations
- **No Assumptions Rule**: Halt on missing traceability rather than assume purpose
- **Halt on Missing Guidance**: Stop if traceability requirements are undefined

### Co-Artifact Synchronization
Traceability enforcement strengthens co-artifact relationships:
- **Twin artifacts** must reference same ontological justification
- **Shared session events** for co-generated artifacts
- **Synchronized traceability metadata** across artifact pairs
- **Consistent behavioral rule documentation**

## Artifact Lifecycle Traceability

### Creation Phase
1. **Identify ontological necessity** from guidance.ttl
2. **Create session event** documenting justification
3. **Generate artifact** with embedded traceability metadata
4. **Validate traceability chain** before completion

### Maintenance Phase
1. **Verify ongoing justification** for modifications
2. **Update session events** for changes
3. **Maintain traceability metadata** consistency
4. **Check for requirement evolution** in guidance.ttl

### Deprecation Phase
1. **Document deprecation justification** in session.ttl
2. **Update dependent artifacts** traceability chains
3. **Maintain historical traceability** for audit purposes
4. **Archive with full traceability metadata**

## Traceability Reporting

### Real-time Validation
Track and report:
- **Traceability compliance rates** across artifact types
- **Missing justification frequency** and resolution patterns
- **Session event completeness** metrics
- **Behavioral rule consistency** across artifacts

### Traceability Health Metrics
Monitor:
- **Orphaned artifact detection** rates
- **Traceability chain integrity** scores
- **Guidance.ttl reference validity** percentages
- **Session.ttl event completeness** ratios

---

**Remember**: Artifact traceability is not optional metadata - it is the foundation of ontology-driven development. Every artifact must justify its existence through traceable links to ontological requirements and behavioral constraints. Breaking traceability violates the fundamental semantic accountability of the framework. 🐿🔗📋