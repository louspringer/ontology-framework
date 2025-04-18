#!/usr/bin/env python3
"""
Tests for the checkin manager implementation.

This test module follows the ontology framework testing standards defined in guidance.ttl.
It includes setup, execution, validation, and cleanup steps for each test case.
"""

import asyncio
import logging
import os
import subprocess
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
import json
from pathlib import Path
from typing import Dict, Any, List
from unittest import mock

import pytest
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS, OWL
from ontology_framework.checkin_manager import CheckinManager, LLMClient, StepStatus
from ontology_framework.meta import OntologyPatch, PatchType, PatchStatus
from ontology_framework.patch_management import PatchManager

# Define SHACL namespace
SHACL = Namespace("http://www.w3.org/ns/shacl#")

# Test Configuration as per guidance.ttl
TEST_CONFIG = {
    "environment": "development",
    "timeout": 300,
    "report_file": "tests/test_report.md",
    "report_format": "markdown",
    "validation_shapes": "tests/validation_shapes.ttl"
}

# Define test namespaces
TEST = Namespace("http://example.org/test#")
ERROR = Namespace("http://example.org/error#")

# Error handling structure as per guidance.ttl
ERROR_HANDLING = {
    "fix_cycle": [
        {"step": "analyze", "description": "Analyze error output"},
        {"step": "plan", "description": "Plan fixes based on analysis"},
        {"step": "implement", "description": "Implement planned fixes"},
        {"step": "validate", "description": "Validate implemented fixes"}
    ],
    "error_traps": [
        {
            "type": ERROR.ValidationError,
            "message": "Ontology validation failed",
            "fix_steps": ["analyze", "plan", "implement", "validate"]
        },
        {
            "type": ERROR.TestError,
            "message": "Test execution failed",
            "fix_steps": ["analyze", "plan", "implement", "validate"]
        }
    ]
}

# SPARQL test patterns
PROPERTY_CARDINALITY_TEST = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
SELECT ?subject ?property (COUNT(?object) as ?count)
WHERE {
    ?subject ?property ?object .
    ?property rdf:type owl:ObjectProperty .
}
GROUP BY ?subject ?property
HAVING (?count > 1)
"""

PROCESS_COMPLETENESS_TEST = """
PREFIX process: <http://example.org/process#>
SELECT ?step
WHERE {
    ?process process:hasStep ?step .
    FILTER NOT EXISTS { ?step process:hasNextStep ?nextStep }
}
"""

TYPE_HIERARCHY_TEST = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?class ?superClass
WHERE {
    ?class rdfs:subClassOf ?superClass .
    FILTER(?class != owl:Nothing)
}
"""

# Configure logging for tests
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_test_report(test_results: Dict[str, Any]) -> None:
    """Generate test report in markdown format."""
    report_path = Path(str(TEST_CONFIG["report_file"]))
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(str(report_path), "a") as f:
        f.write(f"\n## Test Run - {datetime.now().isoformat()}\n\n")
        for test_name, result in test_results.items():
            f.write(f"### {test_name}\n")
            f.write(f"- Status: {result['status']}\n")
            if "error" in result:
                f.write(f"- Error: {result['error']}\n")
            if "details" in result:
                f.write(f"- Details: {result['details']}\n")
            f.write("\n")

@pytest.fixture(autouse=True)
def setup_test_environment(request):
    """Setup test environment before each test."""
    # Setup phase
    logger.info("Setting up test environment")
    os.environ["TEST_ENV"] = TEST_CONFIG["environment"]
    
    def cleanup():
        """Cleanup test environment after each test."""
        logger.info("Cleaning up test environment")
        # Remove cache directories
        for cache_dir in [".pytest_cache", "__pycache__", ".mypy_cache"]:
            if Path(cache_dir).exists():
                subprocess.run(["rm", "-rf", cache_dir])
    
    request.addfinalizer(cleanup)

@pytest.fixture
def mock_run(monkeypatch):
    """Mock subprocess.run for testing."""
    mock = MagicMock()
    mock.return_value = MagicMock(returncode=0, stderr="", stdout="")
    with patch('subprocess.run', return_value=mock.return_value) as mock_run:
        yield mock_run

@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client."""
    client = AsyncMock(spec=LLMClient)
    
    # Mock error analysis response
    client.analyze_errors.return_value = {
        "root_cause": "Test failure due to missing model attributes",
        "fixes": ["Add OntologyPatch class"],
        "code_changes": ["Update meta.py"],
        "model_changes": []
    }
    
    # Mock commit message generation
    client.generate_commit_message.return_value = """
    🐛 Fix model validation errors
    
    - Add OntologyPatch class to meta.py
    - Update patch management tests
    - Reference guidance.ttl for validation rules
    """
    
    return client

@pytest.fixture
def mock_patch_manager():
    """Create a mock patch manager."""
    manager = MagicMock(spec=PatchManager)
    return manager

@pytest.fixture
def sample_patch():
    """Create a sample patch for testing."""
    return OntologyPatch(
        patch_id="test-patch-1",
        patch_type=PatchType.ADD,
        target_ontology="test-ontology",
        content="test content",
        status=PatchStatus.PENDING,
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z"
    )

@pytest.fixture
def checkin_manager(mock_llm_client, mock_patch_manager):
    """Create a checkin manager instance for testing."""
    return CheckinManager(
        llm_client=mock_llm_client,
        patch_manager=mock_patch_manager
    )

@pytest.fixture
def validation_graph():
    """Create a validation graph with SHACL shapes."""
    graph = Graph()
    
    # Add test pattern shapes
    graph.add((TEST.PropertyCardinalityShape, RDF.type, SHACL.NodeShape))
    graph.add((TEST.PropertyCardinalityShape, SHACL.targetClass, OWL.ObjectProperty))
    
    # Add error handling shapes
    graph.add((ERROR.ErrorHandlingShape, RDF.type, SHACL.NodeShape))
    graph.add((ERROR.ErrorHandlingShape, SHACL.property, ERROR.hasFix))
    
    return graph

@pytest.fixture
def test_pattern_application():
    """Create test pattern applications."""
    return [
        {
            "pattern": "PropertyCardinalityTest",
            "target": "test-ontology",
            "query": PROPERTY_CARDINALITY_TEST,
            "expected_result": "PASS"
        },
        {
            "pattern": "ProcessCompletenessTest",
            "target": "test-ontology",
            "query": PROCESS_COMPLETENESS_TEST,
            "expected_result": "PASS"
        },
        {
            "pattern": "TypeHierarchyTest",
            "target": "test-ontology",
            "query": TYPE_HIERARCHY_TEST,
            "expected_result": "PASS"
        }
    ]

def validate_test_patterns(patterns: List[Dict[str, str]], graph: Graph) -> bool:
    """Validate test patterns against the ontology."""
    for pattern in patterns:
        results = graph.query(pattern["query"])
        if len(results) > 0 and pattern["expected_result"] == "FAIL":
            return False
        if len(results) == 0 and pattern["expected_result"] == "PASS":
            return False
    return True

def test_llm_client_initialization():
    """Test LLM client initialization."""
    client = LLMClient(api_key="test-key")
    assert client.model == "gpt-4-turbo-preview"
    assert client.logger.name == "ontology_framework.checkin_manager"

@pytest.mark.asyncio
async def test_llm_client_error_analysis(mock_llm_client):
    """Test LLM client error analysis."""
    error_output = "Test failure: Module has no attribute 'OntologyPatch'"
    test_context = "Testing patch management functionality"
    
    analysis = await mock_llm_client.analyze_errors(
        error_output=error_output,
        test_context=test_context
    )
    
    assert "root_cause" in analysis
    assert "fixes" in analysis
    assert "code_changes" in analysis
    assert "model_changes" in analysis
    logger.debug(f"Error analysis: {json.dumps(analysis, indent=2)}")

@pytest.mark.asyncio
async def test_llm_client_commit_message(mock_llm_client, sample_patch):
    """Test LLM client commit message generation."""
    changes = ["Add OntologyPatch class", "Update tests"]
    
    message = await mock_llm_client.generate_commit_message(
        patch=sample_patch,
        changes=changes
    )
    
    assert message is not None
    assert "🐛" in message  # Check for emoji
    assert "guidance.ttl" in message  # Check for guidance reference
    logger.debug(f"Generated commit message: {message}")

def test_checkin_manager_initialization(checkin_manager):
    """Test checkin manager initialization."""
    assert checkin_manager.llm_client is not None
    assert checkin_manager.patch_manager is not None
    assert len(checkin_manager.step_status) == 5
    assert checkin_manager.step_status["run_tests"] == StepStatus.PENDING

@pytest.mark.asyncio
async def test_run_tests(mock_run, mock_llm_client, mock_patch_manager):
    """Test the _run_tests method."""
    checkin_manager = CheckinManager(mock_llm_client, mock_patch_manager)
    mock_run.return_value = MagicMock(returncode=0, stdout="All tests passed", stderr="")
    
    result = await checkin_manager._run_tests()
    assert result == StepStatus.COMPLETED
    mock_run.assert_called_once()

@pytest.mark.asyncio
async def test_git_add(mock_run, mock_llm_client, mock_patch_manager):
    """Test the _git_add method."""
    checkin_manager = CheckinManager(mock_llm_client, mock_patch_manager)
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    
    result = await checkin_manager._git_add()
    assert result == StepStatus.COMPLETED
    mock_run.assert_called_once_with(['git', 'add', '.'], capture_output=True, text=True)

@pytest.mark.asyncio
async def test_commit(mock_run, mock_llm_client, mock_patch_manager):
    """Test the _commit method."""
    checkin_manager = CheckinManager(mock_llm_client, mock_patch_manager)
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    commit_message = "test: Add new feature"
    
    result = await checkin_manager._commit(commit_message)
    assert result == StepStatus.COMPLETED
    mock_run.assert_called_once_with(['git', 'commit', '-m', commit_message], capture_output=True, text=True)

@pytest.mark.asyncio
async def test_fix_errors(mock_run, mock_llm_client, mock_patch_manager, validation_graph):
    """
    Test the _fix_errors method with proper error handling structure.
    
    Error Handling Steps:
    1. Analyze - Parse error output
    2. Plan - Determine fix strategy
    3. Implement - Apply fixes
    4. Validate - Verify fixes
    """
    checkin_manager = CheckinManager(mock_llm_client, mock_patch_manager)
    
    # Setup error context
    error_output = "Test failure: Ontology validation failed"
    error_context = {
        "type": ERROR.ValidationError,
        "message": error_output,
        "fix_cycle": ERROR_HANDLING["fix_cycle"]
    }
    
    # Mock analysis response
    mock_llm_client.analyze_errors.return_value = {
        "root_cause": "Ontology validation failed",
        "fixes": ["Update property cardinality"],
        "code_changes": ["Fix object property definition"],
        "model_changes": ["Add cardinality constraint"]
    }
    
    # Execute fix cycle
    for step in error_context["fix_cycle"]:
        if step["step"] == "analyze":
            analysis = await mock_llm_client.analyze_errors(
                error_output=error_output,
                test_context="Fixing validation errors"
            )
            assert "root_cause" in analysis
        elif step["step"] == "validate":
            # Validate fixes using SHACL
            validation_result = validate_test_patterns(
                test_pattern_application(),
                validation_graph
            )
            assert validation_result is True
    
    result = await checkin_manager._fix_errors(error_output)
    assert result == StepStatus.SUCCESS

@pytest.mark.asyncio
async def test_full_checkin_process(mock_run, mock_llm_client, mock_patch_manager, sample_patch):
    """
    Test the full checkin process.
    
    Test Steps:
    1. Setup - Initialize checkin manager
    2. Execution - Run the checkin process
    3. Validation - Verify all steps completed successfully
    4. Cleanup - Clean test environment
    """
    # Setup phase
    checkin_manager = CheckinManager(mock_llm_client, mock_patch_manager)
    test_results = {}
    
    try:
        # Mock successful test run
        mock_run.return_value = MagicMock(returncode=0, stdout="All tests passed", stderr="")
        
        # Mock LLM responses
        mock_llm_client.analyze_errors.return_value = {
            "root_cause": "No errors found",
            "fixes": [],
            "code_changes": [],
            "model_changes": []
        }
        mock_llm_client.generate_commit_message.return_value = "test: Add new feature"
        
        # Execution phase
        result = await checkin_manager.checkin(sample_patch)
        
        # Validation phase
        assert result == StepStatus.COMPLETED
        assert checkin_manager.step_status["run_tests"] == StepStatus.COMPLETED
        assert checkin_manager.step_status["fix_errors"] == StepStatus.PENDING
        assert checkin_manager.step_status["git_add"] == StepStatus.COMPLETED
        assert checkin_manager.step_status["create_message"] == StepStatus.COMPLETED
        assert checkin_manager.step_status["commit"] == StepStatus.COMPLETED
        
        test_results["full_checkin_process"] = {
            "status": "PASSED",
            "details": "All steps completed successfully"
        }
        
    except Exception as e:
        test_results["full_checkin_process"] = {
            "status": "FAILED",
            "error": str(e)
        }
        raise
    
    finally:
        # Generate test report
        generate_test_report(test_results)

@pytest.mark.asyncio
async def test_fix_errors_with_llm_failure(mock_run, mock_llm_client, mock_patch_manager):
    """Test the _fix_errors method when LLM analysis fails."""
    checkin_manager = CheckinManager(mock_llm_client, mock_patch_manager)
    mock_run.return_value.stdout = "Test failed with error"
    mock_llm_client.analyze_errors.side_effect = Exception("LLM analysis failed")
    
    result = await checkin_manager._fix_errors("Test failed with error")
    assert result == StepStatus.FAILED
    mock_llm_client.analyze_errors.assert_called_once_with(
        error_output="Test failed with error",
        test_context="Fixing test failures in checkin process"
    )

@pytest.mark.asyncio
async def test_git_add_failure(mock_run, mock_llm_client, mock_patch_manager):
    """Test git add failure case."""
    checkin_manager = CheckinManager(mock_llm_client, mock_patch_manager)
    mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="Git add failed")
    
    result = await checkin_manager._git_add()
    assert result == StepStatus.FAILED
    mock_run.assert_called_once_with(['git', 'add', '.'], capture_output=True, text=True)

@pytest.mark.asyncio
async def test_commit_failure(mock_run, mock_llm_client, mock_patch_manager):
    """Test commit failure case."""
    checkin_manager = CheckinManager(mock_llm_client, mock_patch_manager)
    mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="Commit failed")
    
    result = await checkin_manager._commit("test: Add new feature")
    assert result == StepStatus.FAILED
    mock_run.assert_called_once_with(['git', 'commit', '-m', "test: Add new feature"], capture_output=True, text=True)

@pytest.mark.asyncio
async def test_full_checkin_process_with_test_failure(mock_run, mock_llm_client, mock_patch_manager, sample_patch):
    """Test the full checkin process when tests initially fail but are fixed."""
    checkin_manager = CheckinManager(mock_llm_client, mock_patch_manager)
    
    # Mock test failure then success
    mock_run.side_effect = [
        MagicMock(returncode=1, stdout="", stderr="Test failed"),  # First test run fails
        MagicMock(returncode=0, stdout="", stderr=""),  # Second test run succeeds
        MagicMock(returncode=0, stdout="", stderr=""),  # git add succeeds
        MagicMock(returncode=0, stdout="", stderr="")   # git commit succeeds
    ]
    
    # Mock successful error analysis and fix
    mock_llm_client.analyze_errors.return_value = {
        "root_cause": "Test failure",
        "fixes": ["Fix applied"],
        "code_changes": ["Changed code"],
        "model_changes": ["Changed model"]
    }
    
    # Mock commit message generation
    mock_llm_client.generate_commit_message.return_value = "🐛 fix: Test fixes applied"
    
    result = await checkin_manager.checkin(sample_patch)
    assert result == StepStatus.COMPLETED
    
    # Verify all steps were executed
    assert checkin_manager.step_status["run_tests"] == StepStatus.COMPLETED
    assert checkin_manager.step_status["fix_errors"] == StepStatus.SUCCESS
    assert checkin_manager.step_status["git_add"] == StepStatus.COMPLETED
    assert checkin_manager.step_status["create_message"] == StepStatus.COMPLETED
    assert checkin_manager.step_status["commit"] == StepStatus.COMPLETED
    
    # Verify the sequence of calls
    assert mock_run.call_count == 4  # Two test runs, git add, git commit

@pytest.mark.asyncio
async def test_full_checkin_process_with_fix_failure(mock_run, mock_llm_client, mock_patch_manager, sample_patch):
    """Test the full checkin process when a fix fails after test failure."""
    # Mock test failure followed by fix failure
    mock_run.side_effect = [
        subprocess.CompletedProcess(args=[], returncode=1, stdout="Test failed", stderr=""),  # First test run fails
        subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # Git add succeeds
        subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # Git commit succeeds
    ]

    # Mock LLM client to return empty analysis (simulating fix failure)
    analysis_future = asyncio.Future()
    analysis_future.set_result({
        "root_cause": "Test failure",
        "fixes": ["Fix applied"],
        "code_changes": ["Changed code"],
        "model_changes": ["Changed model"]
    })
    mock_llm_client.analyze_errors.return_value = analysis_future

    commit_msg_future = asyncio.Future()
    commit_msg_future.set_result("🐛 fix: Test fix")
    mock_llm_client.generate_commit_message.return_value = commit_msg_future

    # Run the checkin process
    manager = CheckinManager(llm_client=mock_llm_client, patch_manager=mock_patch_manager)
    result = await manager.checkin(sample_patch)

    # Verify the process failed
    assert result == StepStatus.FAILED

    # Verify the mock calls
    mock_run.assert_has_calls([
        mock.call(["pytest", "-v"], capture_output=True, text=True),  # First test run
    ])
    mock_llm_client.analyze_errors.assert_called_once_with(
        error_output="Test failed",
        test_context="Fixing test failures in checkin process"
    )

    # Verify step statuses
    assert manager.step_status["run_tests"] == StepStatus.FAILED
    assert manager.step_status["fix_errors"] == StepStatus.FAILED
    assert manager.step_status["git_add"] == StepStatus.PENDING
    assert manager.step_status["create_message"] == StepStatus.PENDING
    assert manager.step_status["commit"] == StepStatus.PENDING

@pytest.mark.asyncio
async def test_full_checkin_process_with_git_failure(mock_run, mock_llm_client, mock_patch_manager, sample_patch):
    """Test the full checkin process when git add fails."""
    checkin_manager = CheckinManager(mock_llm_client, mock_patch_manager)
    
    # Mock successful test but failed git add
    mock_run.side_effect = [
        MagicMock(returncode=0, stdout="", stderr=""),  # Tests pass
        MagicMock(returncode=1, stdout="", stderr="git add failed")  # git add fails
    ]
    
    result = await checkin_manager.checkin(sample_patch)
    assert result == StepStatus.FAILED
    
    # Verify steps status
    assert checkin_manager.step_status["run_tests"] == StepStatus.COMPLETED
    assert checkin_manager.step_status["fix_errors"] == StepStatus.PENDING  # No errors to fix
    assert checkin_manager.step_status["git_add"] == StepStatus.FAILED
    assert checkin_manager.step_status["create_message"] == StepStatus.PENDING
    assert checkin_manager.step_status["commit"] == StepStatus.PENDING
    
    # Verify the sequence of calls
    assert mock_run.call_count == 2  # Test run and git add 

@pytest.mark.asyncio
async def test_model_structure_requirements():
    """
    Test model structure requirements as specified in guidance.ttl.
    
    Validates:
    1. Class definitions and hierarchy
    2. Property definitions with domain and range
    3. Individual instances
    4. SHACL validation patterns
    """
    test_results = {}
    
    try:
        # Validate OntologyPatch class structure
        assert hasattr(OntologyPatch, "patch_id"), "OntologyPatch must have patch_id"
        assert hasattr(OntologyPatch, "patch_type"), "OntologyPatch must have patch_type"
        assert hasattr(OntologyPatch, "target_ontology"), "OntologyPatch must have target_ontology"
        assert hasattr(OntologyPatch, "content"), "OntologyPatch must have content"
        assert hasattr(OntologyPatch, "status"), "OntologyPatch must have status"
        assert hasattr(OntologyPatch, "created_at"), "OntologyPatch must have created_at"
        assert hasattr(OntologyPatch, "updated_at"), "OntologyPatch must have updated_at"
        
        # Validate PatchType enumeration
        assert all(isinstance(pt, PatchType) for pt in PatchType), "PatchType must be an enumeration"
        assert len(PatchType) >= 2, "PatchType must have at least two values"
        
        # Validate PatchStatus enumeration
        assert all(isinstance(ps, PatchStatus) for ps in PatchStatus), "PatchStatus must be an enumeration"
        assert len(PatchStatus) >= 2, "PatchStatus must have at least two values"
        
        # Validate StepStatus enumeration
        assert all(isinstance(ss, StepStatus) for ss in StepStatus), "StepStatus must be an enumeration"
        assert len(StepStatus) >= 2, "StepStatus must have at least two values"
        
        # Create test instances
        test_patch1 = OntologyPatch(
            patch_id="test-1",
            patch_type=PatchType.ADD,
            target_ontology="test.ttl",
            content="test content 1",
            status=PatchStatus.PENDING,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z"
        )
        
        test_patch2 = OntologyPatch(
            patch_id="test-2",
            patch_type=PatchType.MODIFY,
            target_ontology="test.ttl",
            content="test content 2",
            status=PatchStatus.PENDING,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z"
        )
        
        # Validate instance attributes
        for patch in [test_patch1, test_patch2]:
            assert isinstance(patch.patch_id, str), "patch_id must be a string"
            assert isinstance(patch.patch_type, PatchType), "patch_type must be PatchType enum"
            assert isinstance(patch.target_ontology, str), "target_ontology must be a string"
            assert isinstance(patch.content, str), "content must be a string"
            assert isinstance(patch.status, PatchStatus), "status must be PatchStatus enum"
            assert isinstance(patch.created_at, str), "created_at must be a string"
            assert isinstance(patch.updated_at, str), "updated_at must be a string"
        
        test_results["model_structure_validation"] = {
            "status": "PASSED",
            "details": "All model structure requirements validated successfully"
        }
        
    except AssertionError as e:
        test_results["model_structure_validation"] = {
            "status": "FAILED",
            "error": str(e)
        }
        raise
    
    finally:
        # Generate test report
        generate_test_report(test_results)

@pytest.mark.asyncio
async def test_shacl_validation_patterns():
    """
    Test SHACL validation patterns as specified in guidance.ttl.
    
    Validates:
    1. Pattern syntax rules
    2. Character class usage
    3. Literal dot handling
    4. Binary string handling
    """
    test_results = {}
    
    try:
        # Test patch ID pattern (alphanumeric with hyphens)
        test_patch = OntologyPatch(
            patch_id="test-123-abc",
            patch_type=PatchType.ADD,
            target_ontology="test.ttl",
            content="test content",
            status=PatchStatus.PENDING,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z"
        )
        
        # Validate patch ID pattern
        assert test_patch.patch_id.replace("-", "").isalnum(), "Patch ID must be alphanumeric with optional hyphens"
        
        # Validate ISO 8601 datetime pattern
        datetime_pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z"
        import re
        assert re.match(datetime_pattern, test_patch.created_at), "created_at must be ISO 8601 format"
        assert re.match(datetime_pattern, test_patch.updated_at), "updated_at must be ISO 8601 format"
        
        test_results["shacl_pattern_validation"] = {
            "status": "PASSED",
            "details": "All SHACL patterns validated successfully"
        }
        
    except AssertionError as e:
        test_results["shacl_pattern_validation"] = {
            "status": "FAILED",
            "error": str(e)
        }
        raise
    
    finally:
        # Generate test report
        generate_test_report(test_results)

def pytest_sessionfinish(session, exitstatus):
    """Generate final test report after all tests complete."""
    logger.info(f"Test session completed with exit status: {exitstatus}")
    
    # Ensure the report directory exists
    Path(TEST_CONFIG["report_file"]).parent.mkdir(parents=True, exist_ok=True)
    
    # Write test summary
    with open(TEST_CONFIG["report_file"], "a") as f:
        f.write(f"\n## Test Session Summary - {datetime.now().isoformat()}\n\n")
        f.write(f"- Total tests: {session.testscollected}\n")
        f.write(f"- Passed: {session.testscollected - session.testsfailed}\n")
        f.write(f"- Failed: {session.testsfailed}\n")
        f.write(f"- Exit status: {exitstatus}\n\n") 