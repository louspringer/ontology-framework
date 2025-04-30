#!/usr/bin/env python3
"""Script to demonstrate Python validation on multiple files."""

from ontology_framework.validation.python_validator import PythonValidator

def validate_file(validator: PythonValidator, file_path: str) -> None:
    """Validate a file and print results."""
    print(f"\nValidating {file_path}:")
    print("=" * (11 + len(file_path)))
    
    results = validator.validate_file(file_path)
    
    # Debug output
    print("\nData Graph:")
    print("-----------")
    print(validator.data_graph.serialize(format='turtle'))
    
    print("\nValidation Results:")
    print("------------------")
    if results['conforms']:
        print("✅ All validations passed!")
    else:
        print("❌ Found validation issues:")
        for violation in results['results']:
            print(f"- {violation['message']} (Severity: {violation['severity']}")

def main():
    """Run validation on example files."""
    validator = PythonValidator()
    
    # Validate good example
    validate_file(validator, "tests/test_data/sample.py")
    
    print("\n" + "="*50 + "\n")
    
    # Validate bad example
    validate_file(validator, "tests/test_data/bad_example.py")

if __name__ == "__main__":
    main() 