#!/usr/bin/env python3
"""Validate all Python files in the codebase."""

import sys
from pathlib import Path
from ontology_framework.validation.python_validator import PythonValidator

def validate_all_files():
    """Validate all Python files and stop after 10 errors."""
    validator = PythonValidator()
    error_count = 0
    
    # Skip test files and __init__.py files initially
    skip_patterns = ["__init__.py", "test_", "tests/"]
    
    # First pass: Validate core implementation files
    for py_file in Path("src/ontology_framework").rglob("*.py"):
        if py_file.name == "__pycache__" or any(pattern in str(py_file) for pattern in skip_patterns):
            continue
            
        print(f"\nValidating {py_file}:")
        print("=" * (11 + len(str(py_file))))
        
        try:
            results = validator.validate_file(str(py_file))
            
            if not results['conforms']:
                for violation in results['results']:
                    error_count += 1
                    print(f"❌ Error {error_count} in {py_file.name}: {violation['message']}")
                    if error_count >= 10:
                        print("\nReached 10 errors, stopping validation.")
                        return error_count
            else:
                print("✅ File conforms to all rules")
        except Exception as e:
            error_count += 1
            print(f"❌ Error {error_count} in {py_file.name}: Failed to validate - {str(e)}")
            if error_count >= 10:
                print("\nReached 10 errors, stopping validation.")
                return error_count
    
    # Second pass: Validate test files if we haven't hit error limit
    if error_count < 10:
        print("\nValidating test files:")
        print("=" * 20)
        
        for py_file in Path("src/ontology_framework").rglob("*.py"):
            if py_file.name == "__pycache__":
                continue
            if not any(pattern in str(py_file) for pattern in skip_patterns):
                continue
                
            print(f"\nValidating {py_file}:")
            print("=" * (11 + len(str(py_file))))
            
            try:
                results = validator.validate_file(str(py_file))
                
                if not results['conforms']:
                    for violation in results['results']:
                        error_count += 1
                        print(f"❌ Error {error_count} in {py_file.name}: {violation['message']}")
                        if error_count >= 10:
                            print("\nReached 10 errors, stopping validation.")
                            return error_count
                else:
                    print("✅ File conforms to all rules")
            except Exception as e:
                error_count += 1
                print(f"❌ Error {error_count} in {py_file.name}: Failed to validate - {str(e)}")
                if error_count >= 10:
                    print("\nReached 10 errors, stopping validation.")
                    return error_count
    
    return error_count

if __name__ == "__main__":
    error_count = validate_all_files()
    print(f"\nValidation complete. Found {error_count} errors.")
    sys.exit(1 if error_count > 0 else 0) 