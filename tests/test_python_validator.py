#!/usr/bin/env python3
"""Tests for Python code validator."""

import unittest
from pathlib import Path
from rdflib import Graph, URIRef, Literal
from ontology_framework.validation.python_validator import PythonValidator

class TestPythonValidator(unittest.TestCase):
    """Test cases for PythonValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = PythonValidator()
        self.test_data_dir = Path(__file__).parent / "test_data"
        
    def test_validate_good_class(self):
        """Test validation of a well-formed class."""
        sample_file = self.test_data_dir / "sample.py"
        results = self.validator.validate_file(str(sample_file))
        
        # Check Person class validation
        person_result = next(r for r in results if r["node_name"] == "Person")
        self.assertTrue(person_result["conforms"], 
                       f"Person class validation failed: {person_result['results_text']}")
        
        # Check Employee class validation
        employee_result = next(r for r in results if r["node_name"] == "Employee")
        self.assertTrue(employee_result["conforms"],
                       f"Employee class validation failed: {employee_result['results_text']}")
        
    def test_validate_bad_naming(self):
        """Test validation of incorrectly named classes and methods."""
        with open(self.test_data_dir / "bad_naming.py", "w") as f:
            f.write('''
class badClass:  # Should start with uppercase
    """A badly named class."""
    
    def BadMethod(self):  # Should be snake_case
        """A badly named method."""
        pass
''')
        
        results = self.validator.validate_file(str(self.test_data_dir / "bad_naming.py"))
        class_result = next(r for r in results if r["node_name"] == "badClass")
        self.assertFalse(class_result["conforms"])
        self.assertIn("^[A-Z]", class_result["results_text"])  # Check for uppercase pattern
        
        method_result = next(r for r in results if r["node_name"] == "BadMethod")
        self.assertFalse(method_result["conforms"])
        self.assertIn("^[a-z]", method_result["results_text"])  # Check for lowercase pattern
        
    def test_validate_missing_docstring(self):
        """Test validation of missing docstrings."""
        with open(self.test_data_dir / "missing_docs.py", "w") as f:
            f.write('''
class UndocumentedClass:  # Missing docstring
    def undocumented_method(self):  # Missing docstring
        pass
''')
        
        results = self.validator.validate_file(str(self.test_data_dir / "missing_docs.py"))
        class_result = next(r for r in results if r["node_name"] == "UndocumentedClass")
        self.assertFalse(class_result["conforms"])
        self.assertIn("docstring", class_result["results_text"].lower())
        
    def test_validate_return_types(self):
        """Test validation of return type annotations."""
        with open(self.test_data_dir / "return_types.py", "w") as f:
            f.write('''
class TypedClass:
    """A class with type annotations."""
    
    def typed_method(self) -> str:
        """A method with return type."""
        return "test"
        
    def untyped_method(self):  # Missing return type
        """A method without return type."""
        return "test"
''')
        
        results = self.validator.validate_file(str(self.test_data_dir / "return_types.py"))
        typed_method = next(r for r in results if r["node_name"] == "typed_method")
        self.assertTrue(typed_method["conforms"])
        
        untyped_method = next(r for r in results if r["node_name"] == "untyped_method")
        self.assertFalse(untyped_method["conforms"])
        self.assertIn("returnType", untyped_method["results_text"])
        
    def test_validate_inheritance(self):
        """Test validation of inherited classes."""
        results = self.validator.validate_file(str(self.test_data_dir / "sample.py"))
        employee_result = next(r for r in results if r["node_name"] == "Employee")
        self.assertTrue(employee_result["conforms"],
                       f"Employee class validation failed: {employee_result['results_text']}")
        
    def tearDown(self):
        """Clean up test files."""
        test_files = ["bad_naming.py", "missing_docs.py", "return_types.py"]
        for file in test_files:
            test_file = self.test_data_dir / file
            if test_file.exists():
                test_file.unlink()

if __name__ == "__main__":
    unittest.main() 