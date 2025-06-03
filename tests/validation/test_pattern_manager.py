import pytest
from pathlib import Path
from ontology_framework.validation.pattern_manager import PatternManager
import tempfile
import os

@pytest.fixture
def temp_patterns_file():
    with tempfile.NamedTemporaryFile(suffix='.ttl', delete=False) as f:
        f.write(b"""
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix vp: <http://example.org/validation-patterns#> .

vp:TestPattern a vp:ValidationPattern ;
    vp:pattern "test.*" ;
    vp:category vp:TestCategory ;
    vp:version "1.0.0" ;
    rdfs:label "Test Pattern"@en ;
    rdfs:comment "A test pattern"@en .
""")
        yield f.name
    os.unlink(f.name)

@pytest.fixture
def pattern_manager(temp_patterns_file):
    return PatternManager(temp_patterns_file)

def test_load_patterns(pattern_manager):
    """Test loading patterns from file."""
    pattern = pattern_manager.get_pattern("TestPattern")
    assert pattern is not None
    assert pattern["pattern"] == "test.*"
    assert pattern["version"] == "1.0.0"

def test_add_pattern(pattern_manager):
    """Test adding a new pattern."""
    pattern_manager.add_pattern(
        "NewPattern",
        r"\d{3}-\d{2}-\d{4}",
        "TestCategory",
        version="1.0.0",
        label="New Pattern",
        comment="A new test pattern"
    )
    
    pattern = pattern_manager.get_pattern("NewPattern")
    assert pattern is not None
    assert pattern["pattern"] == r"\d{3}-\d{2}-\d{4}"
    assert pattern["version"] == "1.0.0"

def test_update_pattern(pattern_manager):
    """Test updating an existing pattern."""
    pattern_manager.update_pattern(
        "TestPattern",
        pattern="updated.*",
        version="1.1.0"
    )
    
    pattern = pattern_manager.get_pattern("TestPattern")
    assert pattern is not None
    assert pattern["pattern"] == "updated.*"
    assert pattern["version"] == "1.1.0"

def test_get_patterns_by_category(pattern_manager):
    """Test getting patterns by category."""
    patterns = pattern_manager.get_patterns_by_category("TestCategory")
    assert len(patterns) == 1
    assert patterns[0]["id"] == "TestPattern"

def test_validate_pattern(pattern_manager):
    """Test pattern validation."""
    assert pattern_manager.validate_pattern(r"\d+")  # Valid pattern
    assert not pattern_manager.validate_pattern(r"[")  # Invalid pattern

def test_version_validation(pattern_manager):
    """Test version validation."""
    with pytest.raises(ValueError):
        pattern_manager.add_pattern(
            "InvalidVersion",
            "test",
            "TestCategory",
            version="invalid"
        )

def test_pattern_history(pattern_manager):
    """Test getting pattern version history."""
    # Add multiple versions
    pattern_manager.add_pattern(
        "VersionedPattern",
        "test",
        "TestCategory",
        version="1.0.0"
    )
    pattern_manager.update_pattern(
        "VersionedPattern",
        pattern="test2",
        version="1.1.0"
    )
    
    history = pattern_manager.get_pattern_history("VersionedPattern")
    assert len(history) == 2
    assert history[0]["version"] == "1.1.0"
    assert history[1]["version"] == "1.0.0"
