# Python Code Validation Framework

## Overview

The Python Code Validation Framework uses SHACL (Shapes Constraint Language) to enforce coding standards and best practices in Python code. It validates:

- Class and method naming conventions
- Documentation requirements
- Type annotations
- Code structure and inheritance

## SHACL Shapes

The framework uses the following SHACL shapes for validation:

### Class Shape
- Class names must be in PascalCase
- Classes must have docstrings
- Classes can have methods

### Method Shape
- Method names must be in snake_case
- Methods must have docstrings
- Methods must have return type annotations

### Parameter Shape
- Parameter names must be in snake_case
- Parameters must have type annotations

## Test Cases

### 1. Well-Formed Classes
Tests validation of properly structured classes:
- Correct naming (PascalCase)
- Complete docstrings
- Proper type annotations

Example:
```python
class Person:
    """A class representing a person."""
    
    def get_name(self) -> str:
        """Return the person's name."""
        return self.name
```

### 2. Naming Conventions
Tests enforcement of naming standards:
- Classes must use PascalCase
- Methods must use snake_case

Invalid example caught by validation:
```python
class badClass:  # ❌ Should be PascalCase
    def BadMethod(self):  # ❌ Should be snake_case
        pass
```

### 3. Documentation Requirements
Tests docstring validation:
- All classes must have docstrings
- All methods must have docstrings

Invalid example caught by validation:
```python
class UndocumentedClass:  # ❌ Missing docstring
    def undocumented_method(self):  # ❌ Missing docstring
        pass
```

### 4. Return Type Validation
Tests return type annotation requirements:
- Methods must specify return types
- Return types must be valid Python types

Example:
```python
def typed_method(self) -> str:  # ✓ Valid
    """A method with return type."""
    return "test"

def untyped_method(self):  # ❌ Missing return type
    """A method without return type."""
    return "test"
```

### 5. Inheritance Validation
Tests validation of inherited classes:
- Subclasses must follow the same rules as base classes
- Inherited methods must maintain type annotations

Example:
```python
class Employee(Person):
    """A class representing an employee."""
    
    def get_employee_id(self) -> str:
        """Return the employee's ID."""
        return self.employee_id
```

## Integration with Model Generator

The validation framework integrates with the model generator to:
1. Extract code structure into RDF graphs
2. Apply SHACL validation rules
3. Generate validation reports
4. Track validation results in the ontology

## Usage

```python
from ontology_framework.validation.python_validator import PythonValidator

# Create validator instance
validator = PythonValidator()

# Validate a file
results = validator.validate_file("path/to/python_file.py")

# Check results
for result in results:
    if result["conforms"]:
        print(f"✓ {result['node_name']} is valid")
    else:
        print(f"❌ {result['node_name']} has validation errors:")
        print(result["results_text"])
```

## Future Enhancements

1. Additional SHACL Shapes:
   - Complex type annotation validation
   - Function complexity metrics
   - Security pattern validation

2. Integration Features:
   - CI/CD pipeline integration
   - IDE plugin support
   - Automated fix suggestions

3. Reporting Improvements:
   - HTML validation reports
   - Trend analysis
   - Compliance dashboards 