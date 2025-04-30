# Validation Patterns Convention

## Overview

The validation patterns system provides a flexible and extensible way to define, manage, and apply validation rules across the ontology framework. Patterns are stored in RDF format using the Turtle syntax and can be easily extended or modified.

## Pattern Structure

Each validation pattern is defined with the following properties:

```turtle
vp:ExamplePattern a vp:ValidationPattern ;
    vp:pattern "pattern_string" ;
    vp:category vp:PatternCategory ;
    vp:version "1.0.0" ;
    rdfs:label "Pattern Name"@en ;
    rdfs:comment "Pattern Description"@en .
```

### Required Properties

- `vp:pattern`: The actual pattern string (regex or SPARQL query)
- `vp:category`: The category this pattern belongs to
- `vp:version`: Version number in semver format
- `rdfs:label`: Human-readable name
- `rdfs:comment`: Description of what the pattern detects

## Pattern Categories

The framework includes several predefined pattern categories:

1. **Sensitive Data** (`vp:SensitiveData`)
   - Passwords
   - Social Security Numbers
   - Credit Card Numbers
   - API Keys

2. **Security Risk** (`vp:SecurityRisk`)
   - SQL Injection
   - XSS Attempts
   - Command Injection

3. **Data Quality** (`vp:DataQuality`)
   - Email Addresses
   - URLs
   - Date Formats

## Usage

### Loading Patterns

```python
from ontology_framework.validation.pattern_manager import PatternManager

# Initialize with default patterns
manager = PatternManager()

# Or with custom patterns file
manager = PatternManager("path/to/patterns.ttl")
```

### Adding New Patterns

```python
manager.add_pattern(
    "CustomPattern",
    r"pattern\d+",
    "SensitiveData",
    version="1.0.0",
    label="Custom Pattern",
    comment="Detects custom sensitive data"
)
```

### Updating Patterns

```python
manager.update_pattern(
    "CustomPattern",
    pattern=r"updated\d+",
    version="1.1.0"
)
```

### Using Patterns in Validation

```python
from ontology_framework.validation.validation_handler import ValidationHandler

handler = ValidationHandler()

# Configure validation rule
rule = {
    "type": ValidationRuleType.SENSITIVE_DATA,
    "patterns": ["PasswordPattern", "SSNPattern"],
    "severity": ErrorSeverity.HIGH
}

# Register and execute rule
handler.register_rule("sensitive_data_check", rule)
result = handler.validate_graph(graph)
```

## Pattern Versioning

Patterns follow semantic versioning (MAJOR.MINOR.PATCH):

- MAJOR: Breaking changes to pattern behavior
- MINOR: New features in backward-compatible manner
- PATCH: Backward-compatible bug fixes

Example version history:
```turtle
vp:PasswordPattern vp:version "1.0.0" . # Initial version
vp:PasswordPattern vp:version "1.1.0" . # Added support for new formats
vp:PasswordPattern vp:version "2.0.0" . # Changed matching behavior
```

## Best Practices

1. **Pattern Naming**
   - Use CamelCase for pattern IDs
   - Include the type of check in the name
   - Be specific about what is being detected

2. **Pattern Design**
   - Make patterns as specific as possible
   - Avoid overly broad matches
   - Document false positive/negative scenarios
   - Include examples in comments

3. **Testing**
   - Test patterns with both valid and invalid data
   - Include edge cases
   - Document test cases in comments

4. **Maintenance**
   - Review and update patterns regularly
   - Track pattern effectiveness
   - Version patterns appropriately

## Example Patterns

### Sensitive Data Detection

```turtle
vp:PasswordPattern a vp:ValidationPattern ;
    vp:pattern "(?i)(password|pwd|secret|key|token|credential|api[_-]?key)" ;
    vp:category vp:SensitiveData ;
    vp:version "1.0.0" ;
    rdfs:label "Password Pattern"@en ;
    rdfs:comment "Detects password-related fields"@en .

vp:SSNPattern a vp:ValidationPattern ;
    vp:pattern "\\d{3}-\\d{2}-\\d{4}" ;
    vp:category vp:SensitiveData ;
    vp:version "1.0.0" ;
    rdfs:label "SSN Pattern"@en ;
    rdfs:comment "Detects Social Security Numbers"@en .
```

### Security Risk Detection

```turtle
vp:SQLInjectionPattern a vp:ValidationPattern ;
    vp:pattern "(?i)(\\b(select|insert|update|delete|drop|union|exec)\\b)" ;
    vp:category vp:SecurityRisk ;
    vp:version "1.0.0" ;
    rdfs:label "SQL Injection Pattern"@en ;
    rdfs:comment "Detects potential SQL injection attempts"@en .
```

## Error Handling

The pattern management system includes robust error handling:

1. **Pattern Validation**
   - Validates regex patterns before adding
   - Checks version format
   - Ensures required properties

2. **Loading Errors**
   - Graceful handling of missing files
   - Clear error messages
   - Fallback to default patterns

3. **Runtime Errors**
   - Safe SPARQL result handling
   - Proper error propagation
   - Detailed error messages 