# Enhanced Validation Toolkit

## Current Implementation Analysis

Your toolkit provides a solid foundation:

✅ **Clean CLI Interface**: Simple `--data` and `--shapes` arguments  
✅ **SHACL Standards Compliance**: Uses `pyshacl` with full feature set  
✅ **Exit Code Integration**: Returns non-zero on validation failures for CI/CD  
✅ **Core Validation Rules**: Lifecycle transitions and twin artifact alignment

## Enhanced `validate.py` Extensions

### **1. Rich Error Reporting**
```python
import sys
import json
from pyshacl import validate
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

def format_violation_report(report_graph, format_type: str = "human") -> str:
    """Format SHACL validation report for different audiences."""
    if format_type == "json":
        # Parse RDF report into structured JSON
        violations = []
        # Implementation to extract sh:ValidationResult instances
        return json.dumps(violations, indent=2)
    
    elif format_type == "markdown":
        # Generate markdown report for documentation
        return f"""# Validation Report - {datetime.now().isoformat()}

## Summary
- **Status**: FAILED
- **Violations Found**: {violation_count}

## Violations
{formatted_violations}
"""
    
    return report_text  # Default human-readable format

def run_validation(
    data_file: Path, 
    shacl_file: Path, 
    output_format: str = "human",
    severity_filter: Optional[str] = None
) -> Dict[str, Any]:
    """Enhanced validation with filtering and formatting options."""
    
    conforms, report_graph, report_text = validate(
        data_graph=str(data_file),
        shacl_graph=str(shacl_file),
        inference='rdfs',
        abort_on_first=False,
        meta_shacl=True,
        advanced=True,
        serialize_report_graph=True
    )
    
    # Extract structured violation data
    violations = extract_violations(report_graph)
    
    # Apply severity filtering if specified
    if severity_filter:
        violations = [v for v in violations if v.get('severity') == severity_filter]
    
    result = {
        'conforms': conforms,
        'violation_count': len(violations),
        'violations': violations,
        'report_text': format_violation_report(report_graph, output_format)
    }
    
    print(result['report_text'])
    
    if not conforms and violations:  # Only fail if filtered violations exist
        sys.exit(1)
    
    return result
```

### **2. Configuration File Support**
```python
# validation.toml
[validation]
default_shapes = "validation-shapes.ttl"
output_format = "human"
severity_levels = ["Violation", "Warning", "Info"]

[validation.ci]
fail_on = ["Violation"]
report_format = "json"
output_file = "validation-report.json"

[validation.shapes]
lifecycle = "shapes/lifecycle-shapes.ttl"
artifacts = "shapes/artifact-shapes.ttl"
behavioral = "shapes/behavioral-shapes.ttl"
```

### **3. Multi-File Validation**
```python
def validate_directory(data_dir: Path, shapes_file: Path) -> Dict[str, Any]:
    """Validate all .ttl files in a directory."""
    results = {}
    
    for ttl_file in data_dir.glob("**/*.ttl"):
        if ttl_file.name.startswith("shapes-") or ttl_file.name.endswith("-shapes.ttl"):
            continue  # Skip shape files
            
        print(f"Validating {ttl_file.relative_to(data_dir)}...")
        results[str(ttl_file)] = run_validation(ttl_file, shapes_file)
    
    return results
```

## Complete SHACL Shapes Bundle

### **Extended `validation-shapes.ttl`**
```turtle
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix lifecycle: <./lifecycle#> .
@prefix session: <./session#> .
@prefix artifact: <./artifact#> .
@prefix trace: <./trace#> .
@prefix behavior: <./behavior#> .
@prefix validation: <./validation#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# Your existing shapes...
lifecycle:ValidTransitionShape a sh:NodeShape ;
    sh:targetClass session:Event ;
    sh:property [
        sh:path session:triggersTransition ;
        sh:class lifecycle:LifecyclePhase ;
        sh:message "Triggered transition must be allowed from current artifact phase." ;
        sh:sparql [
            sh:message "Invalid lifecycle transition: not permitted from current phase." ;
            sh:select """SELECT $this
WHERE {
  $this session:triggersTransition ?toPhase ;
        session:affectsArtifact ?artifact .
  ?artifact lifecycle:hasLifecyclePhase ?fromPhase .
  FILTER NOT EXISTS {
    ?fromPhase lifecycle:allowsTransitionTo ?toPhase .
  }
}"""
        ]
    ] .

lifecycle:TwinPhaseAlignmentShape a sh:NodeShape ;
    sh:targetClass artifact:PythonModule ;
    sh:property [
        sh:path artifact:hasTwin ;
        sh:class artifact:ManifestDocument ;
        sh:message "Twin must be in same lifecycle phase." ;
        sh:sparql [
            sh:message "Twin artifact is in a different lifecycle phase." ;
            sh:select """SELECT $this
WHERE {
  $this lifecycle:hasLifecyclePhase ?phase1 .
  $this artifact:hasTwin ?twin .
  ?twin lifecycle:hasLifecyclePhase ?phase2 .
  FILTER(?phase1 != ?phase2)
}"""
        ]
    ] .

# Additional critical shapes
trace:OntologicalJustificationShape a sh:NodeShape ;
    sh:targetClass artifact:Artifact ;
    sh:property [
        sh:path trace:hasJustification ;
        sh:minCount 1 ;
        sh:message "Every artifact must have ontological justification." ;
        sh:sparql [
            sh:message "Artifact lacks required ontological justification." ;
            sh:select """SELECT $this
WHERE {
  $this a artifact:Artifact .
  FILTER NOT EXISTS {
    $this trace:hasJustification ?justification .
  }
}"""
        ]
    ] .

lifecycle:PhaseTemporalConsistencyShape a sh:NodeShape ;
    sh:targetClass lifecycle:LifecyclePhase ;
    sh:sparql [
        sh:message "Phase end time cannot be before start time." ;
        sh:select """SELECT $this
WHERE {
  $this lifecycle:phaseStart ?start ;
        lifecycle:phaseEnd ?end .
  FILTER(?end < ?start)
}"""
    ] .

artifact:TwinSemanticConsistencyShape a sh:NodeShape ;
    sh:targetClass artifact:PythonModule ;
    sh:property [
        sh:path artifact:hasTwin ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:class artifact:ManifestDocument ;
        sh:message "Python module must have exactly one manifest twin."
    ] ;
    sh:sparql [
        sh:message "Twin artifacts must share semantic purpose." ;
        sh:select """SELECT $this
WHERE {
  $this artifact:hasTwin ?twin ;
        artifact:hasSemanticPurpose ?purpose1 .
  ?twin artifact:hasSemanticPurpose ?purpose2 .
  FILTER(?purpose1 != ?purpose2)
}"""
    ] .
```

## Integration Examples

### **GitHub Actions Workflow**
```yaml
# .github/workflows/validate-ontology.yml
name: Ontology Validation
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        pip install pyshacl rdflib
    - name: Validate ontology artifacts
      run: |
        python validate.py --data artifacts/ --format json --output validation-report.json
    - name: Upload validation report
      uses: actions/upload-artifact@v3
      if: failure()
      with:
        name: validation-report
        path: validation-report.json
```

### **Pre-commit Hook**
```bash
#!/bin/sh
# .git/hooks/pre-commit
echo "Running ontology validation..."
python validate.py --data . --severity Violation
if [ $? -ne 0 ]; then
    echo "❌ Validation failed. Fix violations before committing."
    exit 1
fi
echo "✅ Validation passed."
```

### **Make Integration**
```makefile
# Makefile
.PHONY: validate validate-strict validate-all

validate:
	python validate.py --data artifacts.ttl

validate-strict:
	python validate.py --data artifacts.ttl --severity Violation --fail-on-warning

validate-all:
	python validate.py --data . --recursive --format markdown > validation-report.md

check: validate
	@echo "✅ All validations passed"
```

## Usage Examples

### **Basic Validation**
```bash
# Validate single file
python validate.py --data my-artifacts.ttl

# Use custom shapes
python validate.py --data my-artifacts.ttl --shapes custom-shapes.ttl

# Generate JSON report
python validate.py --data my-artifacts.ttl --format json > report.json
```

### **CI/CD Integration**
```bash
# Fail only on violations, allow warnings
python validate.py --data artifacts/ --severity Violation

# Generate markdown report for documentation
python validate.py --data artifacts/ --format markdown > validation-status.md
```

This enhanced toolkit transforms your validation from a simple check into a comprehensive **semantic governance system** for the ontology framework! 🎯✨