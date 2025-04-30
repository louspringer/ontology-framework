"""Tests for test target inference module."""

import pytest
from pathlib import Path
from src.ontology_framework.modules.test_inference import TestTargetInferrer, infer_test_targets


def test_inferrer_initialization():
    """Test initialization of TestTargetInferrer."""
    test_file = Path("tests/test_module.py")
    src_path = Path("src")

    inferrer = TestTargetInferrer(test_file, src_path)

    assert inferrer.test_file == test_file
    assert inferrer.src_path == src_path
    assert inferrer.imports == {}
    assert inferrer.class_cache == {}
    assert inferrer.current_test == ""
    assert inferrer.test_functions == []
    assert inferrer.potential_targets == {}


def test_analyze_test_with_type_hints():
    """Test analysis of test file with type hints."""
    test_file = Path("tests/test_module.py")
    src_path = Path("src")

    # Create a test file with type hints
    test_content = """
from src.ontology_framework.test_module import TestComponent

def test_method1_with_type_hint(component: TestComponent):
    assert component.method1() == "test"
"""
    test_file.write_text(test_content)

    targets = infer_test_targets(test_file, src_path)

    assert "test_method1_with_type_hint" in targets
    assert "TestComponent" in targets["test_method1_with_type_hint"]
    assert (
        targets["test_method1_with_type_hint"]["TestComponent"] == 0.9
    )  # Very high confidence for type hints
    assert "TestComponent.method1" in targets["test_method1_with_type_hint"]
    assert (
        targets["test_method1_with_type_hint"]["TestComponent.method1"] == 0.7
    )  # Medium confidence for method calls


def test_analyze_test_with_imports():
    """Test analysis of test file with imports."""
    test_file = Path("tests/test_module.py")
    src_path = Path("src")

    # Create a test file with imports
    test_content = """
from src.ontology_framework.test_module import TestComponent

def test_method1_with_import():
    component = TestComponent()
    assert component.method1() == "test"
"""
    test_file.write_text(test_content)

    targets = infer_test_targets(test_file, src_path)

    assert "test_method1_with_import" in targets
    assert "TestComponent" in targets["test_method1_with_import"]
    assert (
        targets["test_method1_with_import"]["TestComponent"] == 0.6
    )  # Medium confidence for class usage
    assert "TestComponent.method1" in targets["test_method1_with_import"]
    assert (
        targets["test_method1_with_import"]["TestComponent.method1"] == 0.7
    )  # Medium confidence for method calls


def test_analyze_test_with_assertions():
    """Test analysis of test file with assertions."""
    test_file = Path("tests/test_module.py")
    src_path = Path("src")

    # Create a test file with assertions
    test_content = """
from src.ontology_framework.test_module import TestComponent

def test_method1_with_assertion():
    component = TestComponent()
    result = component.method1()
    assert result == "test"
"""
    test_file.write_text(test_content)

    targets = infer_test_targets(test_file, src_path)

    assert "test_method1_with_assertion" in targets
    assert "TestComponent" in targets["test_method1_with_assertion"]
    assert (
        targets["test_method1_with_assertion"]["TestComponent"] == 0.6
    )  # Medium confidence for class usage
    assert "TestComponent.method1" in targets["test_method1_with_assertion"]
    assert (
        targets["test_method1_with_assertion"]["TestComponent.method1"] == 0.7
    )  # Medium confidence for method calls


def test_analyze_test_with_multiple_targets():
    """Test analysis of test file with multiple targets."""
    test_file = Path("tests/test_module.py")
    src_path = Path("src")

    # Create a test file with multiple targets
    test_content = """
from src.ontology_framework.test_module import Component1, Component2

def test_components():
    comp1 = Component1()
    comp2 = Component2()
    result1 = comp1.method1()
    result2 = comp2.method2()
    assert result1 == "test1"
    assert result2 == "test2"
"""
    test_file.write_text(test_content)

    targets = infer_test_targets(test_file, src_path)

    assert "test_components" in targets
    assert "Component1" in targets["test_components"]
    assert "Component2" in targets["test_components"]
    assert targets["test_components"]["Component1"] == 0.6  # Medium confidence for class usage
    assert targets["test_components"]["Component2"] == 0.6  # Medium confidence for class usage
    assert "Component1.method1" in targets["test_components"]
    assert "Component2.method2" in targets["test_components"]
    assert (
        targets["test_components"]["Component1.method1"] == 0.7
    )  # Medium confidence for method calls
    assert (
        targets["test_components"]["Component2.method2"] == 0.7
    )  # Medium confidence for method calls
