# Artifact Traceability Rules

## Core Traceability Principles

### **1. Complete Justification Chain**
Every artifact must trace back to an ontological requirement through an unbroken chain:

```
Guidance Requirement → Session Event → Behavioral Rule → Generated Artifact
```

**Rule**: No artifact exists without explicit semantic justification.

### **2. Twin Artifact Co-Traceability**
Python modules and manifest documents are semantic twins sharing identical traceability:

```turtle
?pythonModule artifact:hasTwin ?manifestDoc .
?pythonModule trace:hasJustification ?justification .
?manifestDoc trace:hasJustification ?justification .
```

**Rule**: Twin artifacts must share the same ontological justification.

### **3. Session Event Documentation**
All artifact changes must be documented in session events:

```turtle
?sessionEvent session:affectsArtifact ?artifact ;
              session:timestamp ?when ;
              session:justifiedBy ?requirement .
```

**Rule**: Every artifact modification traces to a documented session event.

### **4. Lifecycle Phase Justification**
Each lifecycle phase transition must be ontologically justified:

```turtle
?artifact lifecycle:hasLifecyclePhase ?phase .
?phase trace:justifiedBy ?requirement ;
       trace:triggeredBy ?sessionEvent .
```

**Rule**: Lifecycle transitions require explicit justification.

## Traceability Validation Rules

### **Orphaned Artifact Detection**
```sparql
SELECT ?artifact WHERE {
  ?artifact a artifact:Artifact .
  FILTER NOT EXISTS {
    ?artifact trace:hasJustification ?justification .
  }
}
```

### **Broken Traceability Chain**
```sparql
SELECT ?artifact ?justification WHERE {
  ?artifact trace:hasJustification ?justification .
  FILTER NOT EXISTS {
    ?justification trace:derivedFrom ?requirement .
    ?requirement a guidance:Requirement .
  }
}
```

### **Twin Traceability Mismatch**
```sparql
SELECT ?pythonModule ?manifestDoc WHERE {
  ?pythonModule artifact:hasTwin ?manifestDoc ;
                trace:hasJustification ?justification1 .
  ?manifestDoc trace:hasJustification ?justification2 .
  FILTER(?justification1 != ?justification2)
}
```

### **Undocumented Session Changes**
```sparql
SELECT ?artifact WHERE {
  ?artifact trace:lastModified ?timestamp .
  FILTER NOT EXISTS {
    ?sessionEvent session:affectsArtifact ?artifact ;
                  session:timestamp ?eventTime .
    FILTER(?eventTime >= ?timestamp)
  }
}
```

## Implementation Requirements

### **Mandatory Artifact Properties**
All artifacts must include:
- `trace:hasJustification` → Links to ontological requirement
- `trace:hasSessionEvent` → Links to creation/modification event  
- `trace:lastModified` → Timestamp of last change
- `artifact:hasSemanticPurpose` → Semantic meaning declaration

### **Session Event Properties**
All session events must include:
- `session:timestamp` → When the event occurred
- `session:affectsArtifact` → Which artifacts were modified
- `session:justifiedBy` → Ontological requirement driving the change
- `session:eventType` → Type of modification (create, update, delete, transition)

### **Behavioral Rule Constraints**
AI behavior must enforce:
- **No generation without justification** → ClaudeReflector halts if no requirement provided
- **Twin synchronization** → Python/manifest pairs generated from same semantic model
- **Session documentation** → Every change documented in session log
- **Validation before action** → SHACL validation must pass before artifact modification

## Traceability Enforcement Workflow

### **1. Pre-Generation Validation**
Before creating any artifact:
1. Verify ontological requirement exists
2. Check for conflicting existing artifacts
3. Validate against behavioral rules
4. Ensure session event is properly documented

### **2. During Generation**
While creating artifacts:
1. Embed traceability metadata in all generated files
2. Create session events documenting the generation process
3. Link twin artifacts through shared justification
4. Apply appropriate lifecycle phase

### **3. Post-Generation Verification**
After artifact creation:
1. Run SHACL validation to ensure compliance
2. Verify complete traceability chain
3. Check twin artifact synchronization
4. Validate lifecycle phase consistency

### **4. Continuous Monitoring**
Ongoing traceability maintenance:
1. Periodic validation of all artifacts
2. Detection of orphaned or unjustified artifacts
3. Monitoring for traceability chain breaks
4. Automated remediation of violations

## Error Handling and Remediation

### **Missing Justification**
**Detection**: Artifact exists without `trace:hasJustification`
**Remediation**: 
1. Halt all modifications to the artifact
2. Require explicit ontological requirement
3. Create proper justification chain
4. Re-validate against SHACL constraints

### **Twin Desynchronization**
**Detection**: Twin artifacts have different justifications or lifecycle phases
**Remediation**:
1. Identify the authoritative version
2. Regenerate the twin from shared semantic model
3. Synchronize lifecycle phases
4. Update session events

### **Broken Traceability Chain**
**Detection**: Justification doesn't link to valid requirement
**Remediation**:
1. Trace back to find the break point
2. Reconstruct missing links
3. Validate the complete chain
4. Update documentation

### **Undocumented Changes**
**Detection**: Artifact modified without session event
**Remediation**:
1. Create retrospective session event
2. Identify the source of the undocumented change
3. Strengthen validation procedures
4. Review access controls

## Integration with Development Tools

### **IDE Integration**
- **Real-time validation** of traceability as files are edited
- **Justification prompts** when creating new artifacts
- **Twin synchronization alerts** when one twin is modified

### **CI/CD Pipeline**
- **Pre-commit validation** of traceability chains
- **Automated session event generation** for tracked changes
- **Deployment blocking** if traceability violations exist

### **Documentation Generation**
- **Automatic traceability reports** showing justification chains
- **Audit trails** for compliance requirements
- **Visual dependency graphs** of artifact relationships

This traceability framework ensures that every artifact in the ontology framework has a clear, documented reason for existence and a complete history of how it came to be. 🔍✨