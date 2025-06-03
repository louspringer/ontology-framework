# Test Violations Documentation

## Overview

The `test-violations.ttl` file contains **8 deliberately crafted violations** of the ontology framework's traceability governance rules. This serves as both a regression test for the validation system and educational material for developers learning the constraints.

## Violation Catalog

### **VIOLATION 1: Undocumented Artifact**
```turtle
artifact:OrphanedPythonModule a artifact:PythonModule ;
    rdfs:label "Orphaned Python Module" ;
    artifact:hasSemanticPurpose "Testing undocumented artifact detection" ;
    lifecycle:hasLifecyclePhase lifecycle:Implementation .
    # MISSING: trace:hasSessionEvent
    # MISSING: trace:hasJustification
```

**Rule Violated**: `rules:SessionDocumentation` + `rules:OntologicalJustification`  
**SHACL Shape**: `trace:SessionEventDocumentationShape` + `trace:OntologicalJustificationShape`  
**Detection Query**: Your original undocumented artifacts query  
**Severity**: Critical - artifacts without documentation break the entire traceability chain

**Expected Error Message**:
```
❌ Artifact lacks required session event documentation
❌ Artifact lacks required ontological justification
```

**Fix**: Add both `trace:hasSessionEvent` and `trace:hasJustification` properties.

---

### **VIOLATION 2: Missing Twin Artifact**
```turtle
artifact:LonelyPythonModule a artifact:PythonModule ;
    # Has proper traceability but missing twin
    trace:hasJustification guidance:TraceabilityEnforcementRequirement ;
    trace:hasSessionEvent session:TestEvent001 .
    # MISSING: artifact:hasTwin
```

**Rule Violated**: `rules:TwinSynchronization`  
**SHACL Shape**: `artifact:TwinSemanticConsistencyShape`  
**Severity**: High - breaks semantic twin guarantee  

**Expected Error Message**:
```
❌ Python module must have exactly one manifest twin
```

**Fix**: Create corresponding manifest document and link with `artifact:hasTwin`.

---

### **VIOLATION 3: Desynchronized Twin Artifacts**
```turtle
artifact:DesyncPythonModule 
    lifecycle:hasLifecyclePhase lifecycle:Implementation ;
    artifact:hasTwin artifact:DesyncManifest .

artifact:DesyncManifest 
    lifecycle:hasLifecyclePhase lifecycle:Validation .  # DIFFERENT PHASE!
```

**Rule Violated**: `rules:TwinSynchronization`  
**SHACL Shape**: `lifecycle:TwinPhaseAlignmentShape`  
**Severity**: High - semantic twins must evolve together

**Expected Error Message**:
```
❌ Twin artifact is in a different lifecycle phase
```

**Fix**: Synchronize lifecycle phases between twin artifacts.

---

### **VIOLATION 4: Invalid Lifecycle Transition**
```turtle
session:InvalidTransitionEvent 
    session:triggersTransition lifecycle:Production ;  # Can't skip Validation!
    session:affectsArtifact artifact:SkippingValidationModule .

artifact:SkippingValidationModule 
    lifecycle:hasLifecyclePhase lifecycle:Implementation .  # Current phase
```

**Rule Violated**: `rules:LifecycleCompliance`  
**SHACL Shape**: `lifecycle:ValidTransitionShape`  
**Severity**: Critical - lifecycle integrity must be maintained

**Expected Error Message**:
```
❌ Invalid lifecycle transition: not permitted from current phase
```

**Fix**: Follow proper lifecycle sequence: Implementation → Validation → Production.

---

### **VIOLATION 5: Broken Justification Chain**
```turtle
artifact:UnjustifiedModule 
    trace:hasJustification guidance:NonExistentRequirement ;  # BROKEN LINK!
```

**Rule Violated**: `rules:OntologicalJustification`  
**SHACL Shape**: `trace:OntologicalJustificationShape`  
**Severity**: Critical - justification must link to valid requirements

**Expected Error Message**:
```
❌ Artifact lacks required ontological justification for current lifecycle phase
```

**Fix**: Reference valid requirement (e.g., `guidance:TraceabilityEnforcementRequirement`).

---

### **VIOLATION 6: Session Event Without Justification**
```turtle
session:UnjustifiedEvent a session:Event ;
    session:affectsArtifact artifact:UnjustifiedEventModule .
    # MISSING: session:justifiedBy
```

**Rule Violated**: `rules:SessionDocumentation`  
**SHACL Shape**: `session:EventTraceabilityShape`  
**Severity**: High - all events must have ontological grounding

**Expected Error Message**:
```
❌ Session event lacks required ontological justification
```

**Fix**: Add `session:justifiedBy` property linking to valid requirement.

---

### **VIOLATION 7: Twin Artifacts with Different Justifications**
```turtle
artifact:MismatchedJustificationPython 
    trace:hasJustification guidance:TraceabilityEnforcementRequirement .

artifact:MismatchedJustificationManifest 
    trace:hasJustification guidance:DifferentRequirement .  # DIFFERENT!
```

**Rule Violated**: `rules:TwinSynchronization`  
**SHACL Shape**: `artifact:TwinSemanticConsistencyShape`  
**Severity**: High - twins must share semantic purpose

**Expected Error Message**:
```
❌ Twin artifacts must share semantic purpose
```

**Fix**: Ensure both twins reference the same justification requirement.

---

### **VIOLATION 8: Temporal Inconsistency**
```turtle
session:TemporalInconsistentEvent 
    session:timestamp "2025-05-26T10:00:00Z"^^xsd:dateTime .

artifact:TemporalInconsistentModule 
    trace:lastModified "2025-05-26T11:00:00Z"^^xsd:dateTime ;  # AFTER session!
    trace:hasSessionEvent session:TemporalInconsistentEvent .
```

**Rule Violated**: `rules:SessionDocumentation`  
**SHACL Shape**: `session:EventTraceabilityShape`  
**Severity**: Medium - temporal consistency required for audit trails

**Expected Error Message**:
```
❌ Artifact has been modified after last documented session event
```

**Fix**: Create new session event for the modification or correct timestamps.

## Testing Workflow

### **Manual Testing**
```bash
# Test violation detection (should fail)
python validate.py --data test-violations.ttl

# Expected exit code: 1 (failure)
# Expected output: List of all 8 violations with descriptions
```

### **Automated Testing**
```bash
#!/bin/bash
# test-validation-suite.sh

echo "🧪 Testing validation framework..."

# Test 1: Violations should be detected
echo "Testing violation detection..."
if python validate.py --data test-violations.ttl >/dev/null 2>&1; then
    echo "❌ FAIL: Violations not detected!"
    exit 1
else
    echo "✅ PASS: Violations correctly detected"
fi

# Test 2: Count expected violations
VIOLATION_COUNT=$(python validate.py --data test-violations.ttl 2>&1 | grep -c "❌")
if [ "$VIOLATION_COUNT" -eq 8 ]; then
    echo "✅ PASS: All 8 violations detected"
else
    echo "❌ FAIL: Expected 8 violations, found $VIOLATION_COUNT"
    exit 1
fi

echo "🎉 All validation tests passed!"
```

### **CI/CD Integration**
```yaml
# .github/workflows/test-governance.yml
name: Test Governance Framework
on: [push, pull_request]

jobs:
  test-violations:
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
        if python validate.py --data test-violations.ttl; then
          echo "ERROR: Validation should have failed"
          exit 1
        fi
        
    - name: Verify violation count
      run: |
        # Should detect exactly 8 violations
        VIOLATIONS=$(python validate.py --data test-violations.ttl 2>&1 | grep -c "❌" || true)
        if [ "$VIOLATIONS" -ne 8 ]; then
          echo "ERROR: Expected 8 violations, found $VIOLATIONS"
          exit 1
        fi
        echo "✅ All 8 violations correctly detected"
```

## Educational Use Cases

### **Developer Training**
- **New team members** can study each violation to understand governance constraints
- **Code reviews** can reference specific violation types by number
- **Documentation** provides clear examples of what not to do

### **Framework Development**
- **Regression testing** ensures validation rules continue working as framework evolves
- **Rule refinement** can test edge cases and corner conditions
- **Tool validation** proves SHACL shapes and Python scripts work correctly

### **Compliance Auditing**
- **Audit trails** can verify the governance system detects violations
- **Compliance reports** can reference test results as evidence
- **Risk assessment** can quantify potential governance gaps

## Extending the Test Suite

### **Adding New Violations**
When adding new governance rules:

1. Create corresponding violation in `test-violations.ttl`
2. Update this documentation with violation details
3. Update automated tests to expect additional violations
4. Verify new SHACL shapes detect the violation

### **Performance Testing**
```turtle
# For large-scale testing, multiply violations:
artifact:Violation001 a artifact:PythonModule ; # Missing session event
artifact:Violation002 a artifact:PythonModule ; # Missing session event
# ... repeat for performance testing
```

This test suite ensures your governance framework is **robust, reliable, and ready for production use**! 🧪✨