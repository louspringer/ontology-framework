# Test Violations Artifact

```turtle
# test-violations.ttl
# Intentionally non-conformant artifact for validation testing

@prefix artifact: <./artifact#> .
@prefix trace: <./trace#> .
@prefix session: <./session#> .
@prefix lifecycle: <./lifecycle#> .
@prefix guidance: <./guidance#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# VIOLATION 1: Undocumented Artifact (No session event)
artifact:OrphanedPythonModule a artifact:PythonModule ;
    rdfs:label "Orphaned Python Module" ;
    artifact:hasSemanticPurpose "Testing undocumented artifact detection" ;
    lifecycle:hasLifecyclePhase lifecycle:Implementation .
    # MISSING: trace:hasSessionEvent
    # MISSING: trace:hasJustification

# VIOLATION 2: Missing Twin Artifact
artifact:LonelyPythonModule a artifact:PythonModule ;
    rdfs:label "Lonely Python Module" ;
    artifact:hasSemanticPurpose "Testing missing twin detection" ;
    lifecycle:hasLifecyclePhase lifecycle:Implementation ;
    trace:hasJustification guidance:TraceabilityEnforcementRequirement ;
    trace:hasSessionEvent session:TestEvent001 .
    # MISSING: artifact:hasTwin

# VIOLATION 3: Desynchronized Twin Artifacts
artifact:DesyncPythonModule a artifact:PythonModule ;
    rdfs:label "Desynchronized Python Module" ;
    artifact:hasSemanticPurpose "Testing twin synchronization" ;
    lifecycle:hasLifecyclePhase lifecycle:Implementation ;
    artifact:hasTwin artifact:DesyncManifest ;
    trace:hasJustification guidance:TraceabilityEnforcementRequirement ;
    trace:hasSessionEvent session:TestEvent002 .

artifact:DesyncManifest a artifact:ManifestDocument ;
    rdfs:label "Desynchronized Manifest" ;
    artifact:hasSemanticPurpose "Testing twin synchronization" ;
    lifecycle:hasLifecyclePhase lifecycle:Validation ;  # DIFFERENT PHASE!
    trace:hasJustification guidance:TraceabilityEnforcementRequirement ;
    trace:hasSessionEvent session:TestEvent002 .

# VIOLATION 4: Invalid Lifecycle Transition
session:InvalidTransitionEvent a session:Event ;
    session:timestamp "2025-05-26T11:00:00Z"^^xsd:dateTime ;
    session:eventType session:LifecycleTransition ;
    session:triggersTransition lifecycle:Production ;  # INVALID: skips Validation
    session:affectsArtifact artifact:SkippingValidationModule ;
    session:justifiedBy guidance:TraceabilityEnforcementRequirement .

artifact:SkippingValidationModule a artifact:PythonModule ;
    rdfs:label "Skipping Validation Module" ;
    lifecycle:hasLifecyclePhase lifecycle:Implementation ;  # Can't go directly to Production
    artifact:hasSemanticPurpose "Testing invalid lifecycle transitions" ;
    trace:hasJustification guidance:TraceabilityEnforcementRequirement ;
    trace:hasSessionEvent session:InvalidTransitionEvent .

# VIOLATION 5: Broken Justification Chain
artifact:UnjustifiedModule a artifact:PythonModule ;
    rdfs:label "Unjustified Module" ;
    artifact:hasSemanticPurpose "Testing broken justification chain" ;
    lifecycle:hasLifecyclePhase lifecycle:Implementation ;
    trace:hasJustification guidance:NonExistentRequirement ;  # BROKEN LINK!
    trace:hasSessionEvent session:TestEvent003 .

# VIOLATION 6: Session Event Without Justification
session:UnjustifiedEvent a session:Event ;
    session:timestamp "2025-05-26T11:15:00Z"^^xsd:dateTime ;
    session:eventType session:ArtifactModification ;
    session:affectsArtifact artifact:UnjustifiedEventModule .
    # MISSING: session:justifiedBy

artifact:UnjustifiedEventModule a artifact:PythonModule ;
    rdfs:label "Unjustified Event Module" ;
    artifact:hasSemanticPurpose "Testing session events without justification" ;
    lifecycle:hasLifecyclePhase lifecycle:Implementation ;
    trace:hasJustification guidance:TraceabilityEnforcementRequirement ;
    trace:hasSessionEvent session:UnjustifiedEvent .

# VIOLATION 7: Twin Artifacts with Different Justifications
artifact:MismatchedJustificationPython a artifact:PythonModule ;
    rdfs:label "Mismatched Justification Python" ;
    artifact:hasSemanticPurpose "Testing twin justification mismatch" ;
    lifecycle:hasLifecyclePhase lifecycle:Implementation ;
    artifact:hasTwin artifact:MismatchedJustificationManifest ;
    trace:hasJustification guidance:TraceabilityEnforcementRequirement ;
    trace:hasSessionEvent session:TestEvent004 .

artifact:MismatchedJustificationManifest a artifact:ManifestDocument ;
    rdfs:label "Mismatched Justification Manifest" ;
    artifact:hasSemanticPurpose "Testing twin justification mismatch" ;
    lifecycle:hasLifecyclePhase lifecycle:Implementation ;
    trace:hasJustification guidance:DifferentRequirement ;  # DIFFERENT JUSTIFICATION!
    trace:hasSessionEvent session:TestEvent004 .

# VIOLATION 8: Temporal Inconsistency
session:TemporalInconsistentEvent a session:Event ;
    session:timestamp "2025-05-26T10:00:00Z"^^xsd:dateTime ;
    session:eventType session:ArtifactModification ;
    session:affectsArtifact artifact:TemporalInconsistentModule ;
    session:justifiedBy guidance:TraceabilityEnforcementRequirement .

artifact:TemporalInconsistentModule a artifact:PythonModule ;
    rdfs:label "Temporal Inconsistent Module" ;
    artifact:hasSemanticPurpose "Testing temporal consistency" ;
    lifecycle:hasLifecyclePhase lifecycle:Implementation ;
    trace:lastModified "2025-05-26T11:00:00Z"^^xsd:dateTime ;  # AFTER session event!
    trace:hasJustification guidance:TraceabilityEnforcementRequirement ;
    trace:hasSessionEvent session:TemporalInconsistentEvent .

# Supporting session events (valid ones for comparison)
session:TestEvent001 a session:Event ;
    session:timestamp "2025-05-26T10:30:00Z"^^xsd:dateTime ;
    session:eventType session:ArtifactCreation ;
    session:affectsArtifact artifact:LonelyPythonModule ;
    session:justifiedBy guidance:TraceabilityEnforcementRequirement .

session:TestEvent002 a session:Event ;
    session:timestamp "2025-05-26T10:45:00Z"^^xsd:dateTime ;
    session:eventType session:ArtifactCreation ;
    session:affectsArtifact artifact:DesyncPythonModule , artifact:DesyncManifest ;
    session:justifiedBy guidance:TraceabilityEnforcementRequirement .

session:TestEvent003 a session:Event ;
    session:timestamp "2025-05-26T11:10:00Z"^^xsd:dateTime ;
    session:eventType session:ArtifactCreation ;
    session:affectsArtifact artifact:UnjustifiedModule ;
    session:justifiedBy guidance:TraceabilityEnforcementRequirement .

session:TestEvent004 a session:Event ;
    session:timestamp "2025-05-26T11:20:00Z"^^xsd:dateTime ;
    session:eventType session:ArtifactCreation ;
    session:affectsArtifact artifact:MismatchedJustificationPython , artifact:MismatchedJustificationManifest ;
    session:justifiedBy guidance:TraceabilityEnforcementRequirement .
```

## Expected Validation Results

When running `python validate.py --data test-violations.ttl`, you should see:

```
❌ SHACL Validation Failed - 8 violations found:

1. Undocumented Artifact: artifact:OrphanedPythonModule
   - Missing session event documentation
   - Missing ontological justification

2. Missing Twin Artifact: artifact:LonelyPythonModule  
   - Python module without corresponding manifest

3. Twin Phase Desynchronization: artifact:DesyncPythonModule ↔ artifact:DesyncManifest
   - Python module in Implementation phase
   - Manifest in Validation phase

4. Invalid Lifecycle Transition: session:InvalidTransitionEvent
   - Attempting Implementation → Production (skips Validation)

5. Broken Justification Chain: artifact:UnjustifiedModule
   - References non-existent requirement: guidance:NonExistentRequirement

6. Unjustified Session Event: session:UnjustifiedEvent
   - Session event without ontological justification

7. Twin Justification Mismatch: artifact:MismatchedJustificationPython ↔ artifact:MismatchedJustificationManifest
   - Different justification requirements

8. Temporal Inconsistency: artifact:TemporalInconsistentModule
   - Last modified after most recent session event
```

## Test Integration

### **Automated Testing Script**
```bash
#!/bin/bash
# test-validation.sh

echo "🧪 Testing validation framework with intentional violations..."

# Test 1: Should fail with violations
echo "Testing violation detection..."
if python validate.py --data test-violations.ttl; then
    echo "❌ ERROR: Validation should have failed but passed!"
    exit 1
else
    echo "✅ Violations correctly detected"
fi

# Test 2: Should pass with clean data
echo "Testing clean data validation..."
if python validate.py --data artifacts.ttl; then
    echo "✅ Clean data validation passed"
else
    echo "❌ ERROR: Clean data validation failed!"
    exit 1
fi

echo "🎉 All validation tests passed!"
```

### **CI/CD Integration**
```yaml
# .github/workflows/test-validation.yml
name: Test Validation Framework
on: [push, pull_request]

jobs:
  test-validation:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: pip install pyshacl rdflib
    - name: Test violation detection
      run: |
        # Should fail with violations
        ! python validate.py --data test-violations.ttl
    - name: Test clean validation
      run: |
        # Should pass with clean data  
        python validate.py --data artifacts.ttl
```

This test artifact **proves your governance framework works** by demonstrating that all constraint violations are properly detected! 🧪✨