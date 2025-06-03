# Enhanced Pre-commit Configuration

## Current Configuration Analysis

Your basic hook is solid, but here are some improvements to consider:

```yaml
# Current (works but static)
repos:
  - repo: local
    hooks:
      - id: shacl-validate
        name: SHACL Validation
        entry: python validate.py --data your-artifacts.ttl
        language: system
        files: \.ttl$
        pass_filenames: false
```

## Enhanced Multi-Hook Configuration

### **Option 1: Dynamic File Detection**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      # Validate individual changed TTL files
      - id: shacl-validate-files
        name: SHACL Validation (Changed Files)
        entry: bash -c 'for file in "$@"; do echo "Validating $file..."; python validate.py --data "$file" || exit 1; done' --
        language: system
        files: \.ttl$
        pass_filenames: true
        
      # Validate complete artifact collection
      - id: shacl-validate-complete
        name: SHACL Validation (Complete Collection)
        entry: python validate.py --data artifacts/
        language: system
        files: \.ttl$
        pass_filenames: false
        stages: [commit, push]
```

### **Option 2: Smart Validation with File Detection**
```yaml
repos:
  - repo: local
    hooks:
      - id: shacl-validate
        name: SHACL Validation
        entry: python
        args: [-c, "
import sys, subprocess
from pathlib import Path

# Find all TTL files in common locations
ttl_files = []
for pattern in ['*.ttl', 'artifacts/*.ttl', 'data/*.ttl', '**/*.ttl']:
    ttl_files.extend(Path('.').glob(pattern))

# Skip shape files
data_files = [f for f in ttl_files if not ('shape' in f.name or f.name.startswith('validation-'))]

if not data_files:
    print('No TTL data files found to validate')
    sys.exit(0)

for ttl_file in data_files:
    print(f'Validating {ttl_file}...')
    result = subprocess.run(['python', 'validate.py', '--data', str(ttl_file)], 
                          capture_output=True, text=True)
    if result.returncode != 0:
        print(f'❌ Validation failed for {ttl_file}')
        print(result.stdout)
        sys.exit(1)
        
print(f'✅ Validated {len(data_files)} files successfully')
"]
        language: system
        files: \.ttl$
        pass_filenames: false
```

### **Option 3: Wrapper Script Approach (Recommended)**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: shacl-validate
        name: SHACL Validation
        entry: ./scripts/validate-hook.sh
        language: system
        files: \.ttl$
        pass_filenames: false
```

```bash
#!/bin/bash
# scripts/validate-hook.sh
set -e

echo "🔍 Running SHACL validation..."

# Find TTL files to validate (exclude shapes)
TTL_FILES=$(find . -name "*.ttl" -not -path "./validation-shapes.ttl" -not -name "*shapes*.ttl")

if [ -z "$TTL_FILES" ]; then
    echo "ℹ️  No TTL data files found to validate"
    exit 0
fi

VALIDATION_FAILED=false

for file in $TTL_FILES; do
    echo "Validating $file..."
    if ! python validate.py --data "$file" 2>/dev/null; then
        echo "❌ Validation failed for $file"
        VALIDATION_FAILED=true
    else
        echo "✅ $file is valid"
    fi
done

if [ "$VALIDATION_FAILED" = true ]; then
    echo ""
    echo "💥 SHACL validation failed. Please fix violations before committing."
    echo "Run 'python validate.py --data <file>' for detailed error reports."
    exit 1
fi

echo "🎉 All SHACL validations passed!"
```

## Configuration for Different Project Structures

### **For Ontology Framework Projects**
```yaml
repos:
  - repo: local
    hooks:
      - id: ontology-validate
        name: Ontology Framework Validation
        entry: python validate.py --data
        language: system
        files: ^(artifacts|data|ontology)/.*\.ttl$
        args: [artifacts/]
        pass_filenames: false
        
      - id: shapes-validate
        name: Validate SHACL Shapes
        entry: python -c "
from pyshacl import validate
import sys
# Validate the shapes themselves against SHACL meta-model
conforms, _, report = validate(
    shacl_graph='validation-shapes.ttl',
    meta_shacl=True
)
if not conforms:
    print('❌ SHACL shapes are invalid!')
    print(report)
    sys.exit(1)
print('✅ SHACL shapes are valid')
"
        language: system
        files: ^validation-shapes\.ttl$
        pass_filenames: false
```

### **For Multi-Project Repositories**
```yaml
repos:
  - repo: local
    hooks:
      - id: shacl-validate-project
        name: SHACL Validation (Per Project)
        entry: bash -c '
for project_dir in */; do
    if [ -f "$project_dir/artifacts.ttl" ]; then
        echo "Validating project: $project_dir"
        python validate.py --data "$project_dir/artifacts.ttl" || exit 1
    fi
done
'
        language: system
        files: \.ttl$
        pass_filenames: false
```

## Advanced Hooks with Conditional Logic

### **Performance-Optimized Hook**
```yaml
repos:
  - repo: local
    hooks:
      - id: shacl-validate-smart
        name: Smart SHACL Validation
        entry: python
        args: [-c, "
import subprocess
import sys
from pathlib import Path

# Only validate if shapes or data files changed
changed_files = sys.argv[1:] if len(sys.argv) > 1 else []
shapes_changed = any('shape' in f for f in changed_files)
data_changed = any(f.endswith('.ttl') and 'shape' not in f for f in changed_files)

if not (shapes_changed or data_changed):
    print('ℹ️  No relevant TTL files changed, skipping validation')
    sys.exit(0)

if shapes_changed:
    print('🔄 SHACL shapes changed, running full validation...')
else:
    print('📝 Data files changed, validating...')

# Run validation
result = subprocess.run(['python', 'validate.py', '--data', 'artifacts/'])
sys.exit(result.returncode)
"]
        language: system
        files: \.ttl$
        pass_filenames: true
```

## Installation and Setup

```bash
# Install pre-commit
pip install pre-commit

# Install the hooks
pre-commit install

# Test the hooks
pre-commit run --all-files

# Run only SHACL validation
pre-commit run shacl-validate
```

## Integration with Your Current Setup

Your current configuration works perfectly for a simple, single-file setup. To enhance it for real-world usage, I'd recommend the **wrapper script approach** (Option 3) because it:

- ✅ **Handles multiple files automatically**
- ✅ **Provides clear success/failure feedback** 
- ✅ **Excludes shape files from validation**
- ✅ **Gives helpful error messages**
- ✅ **Easy to customize for your project structure**

The wrapper script makes your validation robust while keeping the pre-commit configuration clean and simple!