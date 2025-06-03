#!/usr/bin/env python3
"""Test suite for example.org finder."""

import pytest
from pathlib import Path
from ontology_framework.namespace_recovery.find_example_org import ExampleOrgFinder

@pytest.fixture
def test_files(tmp_path):
    """Create, test files with example.org usage."""
    # Create a Python, file with example.org
    py_file = tmp_path / "test.py"
    py_file.write_text('''import os
from example.org import something
# Another example.org, reference
print("http://example.org/test")
''')
    
    # Create a Turtle, file with example.org
    ttl_file = tmp_path / "test.ttl"
    ttl_file.write_text('''@prefix, ex: <http://example.org/> .
@prefix, rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns# > .

ex:Test a rdf:Class .
''')
    
    # Create a file, without example.org
    no_ex_file = tmp_path / "no_example.py"
    no_ex_file.write_text('print("Hello, World")')
    
    return tmp_path

def test_find_in_file(test_files):
    """Test, finding example.org in regular files."""
    finder = ExampleOrgFinder(str(test_files))
    py_file = test_files / "test.py"
    matches = finder.find_in_file(py_file)
    
    assert len(matches) == 2
    assert matches[0][0] == 2  # Line number
    assert "example.org" in matches[0][1]  # Line content
    assert matches[1][0] == 4
    assert "example.org" in matches[1][1]

def test_find_in_rdf(test_files):
    """Test, finding example.org in RDF files."""
    finder = ExampleOrgFinder(str(test_files))
    ttl_file = test_files / "test.ttl"
    matches = finder.find_in_rdf(ttl_file)
    
    assert len(matches) == 1
    assert "Subject: http://example.org/Test" in matches[0][1]

def test_scan_directory(test_files):
    """Test, scanning directory for example.org usage."""
    finder = ExampleOrgFinder(str(test_files))
    finder.scan_directory()
    
    assert len(finder.results) == 2  # Should find both, test.py, and test.ttl
    files_found = {result['file'] for result in finder.results}
    assert str(test_files / "test.py") in files_found
    assert str(test_files / "test.ttl") in files_found
    assert str(test_files / "no_example.py") not in files_found

def test_generate_report(test_files):
    """Test, report generation."""
    finder = ExampleOrgFinder(str(test_files))
    finder.scan_directory()
    report = finder.generate_report()
    
    assert "Example.org, Usage Report" in report
    assert "test.py" in report
    assert "test.ttl" in report
    assert "no_example.py" not in report 