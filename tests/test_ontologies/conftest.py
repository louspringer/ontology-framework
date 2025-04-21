import pytest
from pathlib import Path
import sys

# Add the src directory to the Python path
src_dir = Path(__file__).parent.parent.parent / "src"
sys.path.append(str(src_dir))

@pytest.fixture
def ontology_dir():
    """Return the path to the ontologies directory."""
    return Path("src/ontology_framework/ontologies")

@pytest.fixture
def error_ontology(ontology_dir):
    """Return the path to the error handling ontology."""
    return ontology_dir / "error_handling.ttl" 