#!/usr/bin/env python3
"""Tests for Python code validator."""

import pytest
from pathlib import Path
from src.ontology_framework.python_validator import PythonValidator

@pytest.fixture
def validator():
    """Create a validator instance."""
    return PythonValidator()

@pytest.fixture
def test_files(tmp_path):
    """Create test Python files."""
    # Valid Python file
    valid_file = tmp_path / "valid.py"
    valid_file.write_text('''#!/usr/bin/env python3
"""Valid Python module."""

from typing import List, Optional

class ValidClass:
    """A valid Python class."""
    
    def __init__(self, name: str):
        """Initialize the class.
        
        Args:
            name: The name
        """
        self.name = name
    
    def get_name(self) -> str:
        """Get the name.
        
        Returns:
            The name
        """
        return self.name
''')
    
    # Invalid Python file (bad indentation)
    invalid_indent = tmp_path / "invalid_indent.py"
    invalid_indent.write_text('''#!/usr/bin/env python3
"""Invalid Python module."""

class InvalidClass:
   """Bad indentation."""
   
   def __init__(self):
       pass
''')
    
    # Invalid Python file (missing type hints)
    invalid_types = tmp_path / "invalid_types.py"
    invalid_types.write_text('''#!/usr/bin/env python3
"""Invalid Python module."""

class InvalidClass:
    """Missing type hints."""
    
    def __init__(self, name):
        self.name = name
    
    def get_name(self):
        return self.name
''')
    
    return tmp_path

def test_validate_valid_file(validator, test_files):
    """Test validation of a valid Python file."""
    valid_file = test_files / "valid.py"
    errors = validator.validate_file(valid_file)
    assert not errors, f"Unexpected errors: {errors}"

def test_validate_invalid_indentation(validator, test_files):
    """Test validation of a file with incorrect indentation."""
    invalid_file = test_files / "invalid_indent.py"
    errors = validator.validate_file(invalid_file)
    assert any("indentation" in error.lower() for error in errors)

def test_validate_missing_type_hints(validator, test_files):
    """Test validation of a file with missing type hints."""
    invalid_file = test_files / "invalid_types.py"
    errors = validator.validate_file(invalid_file)
    assert any("type hints" in error.lower() for error in errors) 