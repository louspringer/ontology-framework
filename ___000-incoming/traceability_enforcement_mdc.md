---
applies_to: "**/*.{py,toml,ttl,md}"
activation: auto_attached
priority: critical
enforcement_level: halt_on_violation
---

# Traceability Enforcement Rule

## Core Constraint
**EVERY artifact must have complete traceability to ontological justification.**

## Behavioral Requirements

### **Pre-Generation Protocol**
Before creating or modifying ANY file:

1. **Verify Ontological Justification**
   - Must identify the `guidance:Requirement` driving this change
   - Must link to existing session event or create new one
   - Must validate against existing behavioral rules

2. **Twin Artifact Coordination** 
   - Python files (`.py`) MUST have corresponding manifest (`.manifest.toml`)
   - Both must share identical `trace:hasJustification`
   - Both must be in same `lifecycle:LifecyclePhase`

3. **Session Event Documentation**
   - Every modification must create/update session event
   - Must include timestamp, affected artifacts, and justification
   - Must respect lifecycle phase constraints

### **Validation Gates**

#### **For Python Modules**
```python
# REQUIRED: Every .py file must include traceability header
"""
Ontological Justification: <requirement-uri>
Session Event: <session-event-uri>  
Lifecycle Phase: <current-phase>
Twin Artifact: <manifest-file-path>
Semantic Purpose: <purpose-description>
"""
```

#### **For Manifest Documents**
```toml
[trace]
justification = "<requirement-uri>"
session_event = "<session-event-uri>"
lifecycle_phase = "<current-phase>"
twin_artifact = "<python-file-path>"
semantic_purpose = "<purpose-description>"
```

#### **For RDF/TTL Files**
```turtle
@prefix trace: <./trace#> .

<artifact-uri> a artifact:Artifact ;
    trace:hasJustification <requirement-uri> ;
    trace:hasSessionEvent <session-event-uri> ;
    lifecycle:hasLifecyclePhase <phase-uri> ;
    artifact:hasSemanticPurpose "<purpose>" .
```

### **Enforcement Actions**

#### **HALT CONDITIONS** 🛑
The AI must STOP and request clarification when:

- No ontological justification can be identified for requested action
- Attempting to modify artifact without updating twin
- Session event documentation is missing or incomplete
- SHACL validation fails for traceability constraints
- Lifecycle phase transition is not permitted

#### **VALIDATION REQUIREMENTS** ✅
Before proceeding with any action:

1. Run SHACL validation against `validation-shapes.ttl`
2. Verify twin artifact synchronization
3. Check lifecycle phase consistency
4. Validate complete traceability chain
5. Confirm session event documentation

#### **REMEDIATION PROTOCOL** 🔧
When violations are detected:

1. **Stop current operation immediately**
2. **Identify specific violation type**
3. **Request explicit ontological justification**
4. **Guide user through proper traceability setup**
5. **Re-validate before proceeding**

### **Session Event Requirements**

Every session must maintain:

```turtle
<session-event-uri> a session:Event ;
    session:timestamp "2025-05-26T10:30:00Z"^^xsd:dateTime ;
    session:eventType session:ArtifactModification ;
    session:affectsArtifact <artifact-uri> ;
    session:justifiedBy <requirement-uri> ;
    session:performedBy agent:ClaudeReflector ;
    session:description "Brief description of change and rationale" .
```

### **Twin Artifact Synchronization**

When modifying Python modules:
1. **Always update the corresponding manifest**
2. **Ensure identical traceability metadata**
3. **Synchronize lifecycle phases**
4. **Update session events for both artifacts**

When modifying manifests:
1. **Verify consistency with Python twin**
2. **Update traceability if changed**
3. **Maintain semantic purpose alignment**
4. **Document changes in session events**

### **Lifecycle Phase Enforcement**

#### **Valid Transitions Only**
```sparql
# Must validate before any phase transition
PREFIX lifecycle: <./lifecycle#>
ASK WHERE {
    ?fromPhase lifecycle:allowsTransitionTo ?toPhase .
}
```

#### **Phase-Specific Constraints**
- **Planning**: Focus on requirements and design
- **Implementation**: Generate twin artifacts with full traceability
- **Validation**: Run comprehensive SHACL validation
- **Production**: Read-only except for justified evolution

### **Error Messages and Guidance**

#### **Missing Justification**
```
❌ TRACEABILITY VIOLATION: No ontological justification provided

Required: Please specify which guidance requirement drives this change.
Example: "This implements requirement REQ-001 for semantic validation"

Cannot proceed without explicit justification linking to ontology.
```

#### **Twin Desynchronization**
```
❌ TWIN ARTIFACT VIOLATION: Python module and manifest out of sync

Issue: Different lifecycle phases or justifications detected
Required: Twin artifacts must share identical traceability metadata

Please synchronize before proceeding.
```

#### **Invalid Lifecycle Transition**
```
❌ LIFECYCLE VIOLATION: Invalid phase transition attempted

Current: lifecycle:Implementation
Requested: lifecycle:Production  
Issue: Must pass through lifecycle:Validation first

Valid next phases: [lifecycle:Validation, lifecycle:Refinement]
```

### **Integration Commands**

#### **Pre-Action Validation**
```bash
# Must run before any artifact modification
python validate.py --data artifacts/ --severity Violation
```

#### **Traceability Check**
```sparql
# Verify complete traceability chain exists
SELECT ?artifact WHERE {
    ?artifact a artifact:Artifact .
    ?artifact trace:hasJustification ?justification .
    ?justification trace:derivedFrom ?requirement .
    ?requirement a guidance:Requirement .
}
```

#### **Twin Synchronization Check**
```bash
# Verify twin artifacts are synchronized
python validate.py --data artifacts/ --shapes validation-shapes.ttl --focus TwinPhaseAlignmentShape
```

## ClaudeReflector Behavior Profile

This rule implements the `behavior:ClaudeReflector` constraints:

- ✅ **PDCA Protocol**: Plan (justify) → Do (generate) → Check (validate) → Act (remediate)
- ✅ **Semantic First Principle**: Meaning and justification drive implementation
- ✅ **No Assumptions Rule**: Explicit clarification required for ontological justification
- ✅ **Halt on Missing Guidance**: Stop rather than guess when requirements are unclear
- ✅ **Traceability Enforcement**: Every artifact traces to ontological foundation

**This rule transforms ad-hoc development into disciplined, semantically-grounded artifact generation.** 🎯