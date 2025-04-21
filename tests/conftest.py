#!/usr/bin/env python3
"""
Shared test fixtures and configurations for the ontology framework tests.
Following the standards defined in guidance.ttl.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Generator, Iterator
from datetime import datetime

# Add the src directory to the Python path
src_dir = Path(__file__).parent.parent / "src"
sys.path.append(str(src_dir))

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

import pytest
from ontology_framework.modules.patch_management import PatchManager
from ontology_framework.meta import OntologyPatch, PatchType, PatchStatus
from tests.utils.test_monitoring import TestMonitor
from tests.utils.mock_graphdb import MockGraphDBServer

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

@pytest.fixture(scope="session")
def test_environment() -> dict[str, str]:
    """Set up test environment variables."""
    env = {
        "GRAPHDB_URL": "http://localhost:7200",
        "GRAPHDB_REPOSITORY": "test_repo",
        "GRAPHDB_USERNAME": "test_user",
        "GRAPHDB_PASSWORD": "test_pass",
        "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN", "test_token")
    }
    for key, value in env.items():
        os.environ[key] = value
    return env

@pytest.fixture(scope="session")
def mock_graphdb_server(test_environment: dict[str, str]) -> Generator[MockGraphDBServer, None, None]:
    """Create and start a mock GraphDB server."""
    server = MockGraphDBServer()
    server.start()
    yield server
    server.stop()

@pytest.fixture(scope="session")
def test_monitor(mock_graphdb_server: MockGraphDBServer) -> Generator[TestMonitor, None, None]:
    """Create a test monitor."""
    monitor = TestMonitor(mock_graphdb_server.url)
    yield monitor
    monitor.print_summary()

@pytest.fixture(autouse=True)
def monitor_test(request, test_monitor):
    """Monitor each test execution."""
    with test_monitor.monitor_test(request.node.name):
        yield 

@pytest.fixture
def ontology_dir():
    """Return the path to the ontologies directory."""
    return Path("src/ontology_framework/ontologies")

@pytest.fixture
def error_ontology(ontology_dir):
    """Return the path to the error handling ontology."""
    return ontology_dir / "error_handling.ttl"

@pytest.fixture(scope="function")
def temp_ttl_file() -> Generator[Path, None, None]:
    """Create a temporary TTL file with test data."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / "test.ttl"
        test_data = """
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
        @prefix ex: <http://example.org/> .

        ex:TestClass a rdfs:Class ;
            rdfs:label "Test Class" ;
            rdfs:comment "A test class for testing" .

        ex:TestInstance a ex:TestClass ;
            rdfs:label "Test Instance" ;
            rdfs:comment "A test instance for testing" .
        """
        test_file.write_text(test_data)
        yield test_file

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
def empty_graph() -> Graph:
    """Create an empty RDF graph."""
    return Graph()

@pytest.fixture(scope="session")
def test_namespaces() -> dict[str, Namespace]:
    """Create test namespaces."""
    return {
        "rdf": Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
        "rdfs": Namespace("http://www.w3.org/2000/01/rdf-schema#"),
        "ex": Namespace("http://example.org/")
    } 