#!/usr/bin/env python3
"""
Shared test fixtures and configurations for the ontology framework tests.
Following the standards defined in guidance.ttl.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# Add the src directory to the Python path
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Configure logging
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test fixtures
import pytest
from rdflib import Graph, Namespace
import tempfile
import shutil
from typing import Generator

import pytest
from ontology_framework.patch_management import PatchManager
from ontology_framework.meta import OntologyPatch, PatchType, PatchStatus
from tests.utils.test_monitoring import TestMonitor

# Test Configuration
TEST_CONFIG = {
    "environment": "development",
    "timeout": 300,
    "report_file": "tests/test_report.md",
    "report_format": "markdown"
}

@pytest.fixture
def test_namespace():
    """Fixture providing a test namespace."""
    return Namespace("http://example.org/test#")

@pytest.fixture
def empty_graph():
    """Fixture providing an empty RDF graph."""
    return Graph()

@pytest.fixture
def valid_model_graph(test_namespace):
    """Fixture providing a valid model graph."""
    graph = Graph()
    graph.add((test_namespace.ValidClass, RDF.type, OWL.Class))
    graph.add((test_namespace.ValidClass, RDFS.label, Literal("Valid Class")))
    graph.add((test_namespace.ValidClass, RDFS.comment, Literal("A valid class")))
    graph.add((test_namespace.ValidClass, OWL.versionInfo, Literal("1.0.0")))
    return graph

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)

@pytest.fixture
def patch_manager(temp_dir: Path) -> PatchManager:
    """Create a PatchManager instance with a temporary directory."""
    return PatchManager(str(temp_dir))

@pytest.fixture
def sample_patch() -> OntologyPatch:
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
def sample_patch_file(temp_dir: Path, sample_patch: OntologyPatch) -> Path:
    """Create a sample patch file for testing."""
    patch_file = temp_dir / f"{sample_patch.patch_id}.ttl"
    patch_file.write_text(str(sample_patch))
    return patch_file

def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers",
        "model_structure: mark test as validating model structure requirements"
    )
    config.addinivalue_line(
        "markers",
        "shacl_validation: mark test as validating SHACL patterns"
    )
    config.addinivalue_line(
        "markers",
        "functional: mark test as validating functional requirements"
    )

@pytest.fixture(scope="session", autouse=True)
def test_environment():
    """Setup test environment for the entire test session."""
    # Setup phase
    logger.info("Setting up test environment")
    os.environ["TEST_ENV"] = TEST_CONFIG["environment"]
    
    # Create report directory if it doesn't exist
    report_path = Path(TEST_CONFIG["report_file"]).parent
    report_path.mkdir(parents=True, exist_ok=True)
    
    yield
    
    # Cleanup phase
    logger.info("Cleaning up test environment")
    cleanup_test_artifacts()

def cleanup_test_artifacts():
    """Clean up test artifacts and cache directories."""
    cache_dirs = [".pytest_cache", "__pycache__", ".mypy_cache"]
    for cache_dir in cache_dirs:
        if Path(cache_dir).exists():
            logger.info(f"Removing {cache_dir}")
            os.system(f"rm -rf {cache_dir}")

@pytest.fixture
def test_report():
    """Fixture to handle test reporting."""
    def _generate_report(test_name: str, results: Dict[str, Any]) -> None:
        """Generate test report entry."""
        with open(str(TEST_CONFIG["report_file"]), "a") as f:
            f.write(f"\n### {test_name} - {datetime.now().isoformat()}\n")
            for key, value in results.items():
                f.write(f"- {key}: {value}\n")
            f.write("\n")
    
    return _generate_report

def pytest_sessionfinish(session, exitstatus):
    """Generate final test report after all tests complete."""
    logger.info(f"Test session completed with exit status: {exitstatus}")
    
    with open(TEST_CONFIG["report_file"], "a") as f:
        f.write(f"\n## Test Session Summary - {datetime.now().isoformat()}\n\n")
        f.write(f"- Total tests: {session.testscollected}\n")
        f.write(f"- Passed: {session.testscollected - session.testsfailed}\n")
        f.write(f"- Failed: {session.testsfailed}\n")
        f.write(f"- Exit status: {exitstatus}\n\n")
        
        # Add test categories summary
        categories = {
            "model_structure": "Model Structure Tests",
            "shacl_validation": "SHACL Validation Tests",
            "functional": "Functional Tests"
        }
        
        f.write("### Test Categories Summary\n")
        for marker, title in categories.items():
            count = len([item for item in session.items if item.get_closest_marker(marker)])
            f.write(f"- {title}: {count} tests\n")
        f.write("\n")

@pytest.fixture(scope="session")
def test_monitor():
    """Create a test monitor for the session."""
    log_dir = Path("logs") / "tests"
    monitor = TestMonitor(log_dir=log_dir)
    yield monitor
    # Print test summary at the end of the session
    summary = monitor.get_test_summary()
    print("\nTest Execution Summary:")
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Failed Tests: {summary['failed_tests']}")
    print(f"Slow Tests: {summary['slow_tests']}")
    print(f"Success Rate: {summary['success_rate']:.2%}")
    print(f"Average Duration: {summary['average_duration']:.2f}s")

@pytest.fixture(autouse=True)
def monitor_test(request, test_monitor):
    """Monitor each test execution."""
    with test_monitor.monitor_test(request.node.name):
        yield 