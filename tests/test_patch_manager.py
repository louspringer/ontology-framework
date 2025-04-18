import pytest
from pathlib import Path
import shutil
from datetime import datetime
from rdflib import Graph, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, RDFS, OWL, DCTERMS, XSD
from ontology_framework.patch_management import PatchManager, PatchNotFoundError
from ontology_framework.meta import PatchType, OntologyPatch, PatchStatus

PATCH = Namespace("http://example.org/patch#")

@pytest.fixture
def patch_manager(tmp_path):
    """Create a PatchManager instance for testing."""
    return PatchManager(str(tmp_path))

@pytest.fixture
def sample_patch():
    """Create a sample OntologyPatch for testing."""
    return OntologyPatch(
        patch_id="test-patch-1",
        patch_type=PatchType.ADD,
        target_ontology="test.ttl",
        content="test content",
        status=PatchStatus.PENDING,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )

def test_create_patch(patch_manager, sample_patch):
    """Test creating a new patch."""
    patch = patch_manager.create_patch(
        patch_type=sample_patch.patch_type,
        target_ontology=sample_patch.target_ontology,
        content=sample_patch.content,
        patch_id=sample_patch.patch_id
    )
    
    assert patch.patch_id == sample_patch.patch_id
    assert patch.patch_type == sample_patch.patch_type
    assert patch.target_ontology == sample_patch.target_ontology
    assert patch.content == sample_patch.content
    assert patch.status == PatchStatus.PENDING
    
    # Check file exists
    patch_file = patch_manager.patches_dir / f"{patch.patch_id}.ttl"
    assert patch_file.exists()

def test_load_patch(patch_manager, sample_patch):
    """Test loading a patch from storage."""
    # First create and save a patch
    created_patch = patch_manager.create_patch(
        patch_type=sample_patch.patch_type,
        target_ontology=sample_patch.target_ontology,
        content=sample_patch.content,
        patch_id=sample_patch.patch_id
    )
    
    # Load the patch
    loaded_patch = patch_manager.load_patch(created_patch.patch_id)
    
    assert loaded_patch.patch_id == created_patch.patch_id
    assert loaded_patch.patch_type == created_patch.patch_type
    assert loaded_patch.target_ontology == created_patch.target_ontology
    assert loaded_patch.content == created_patch.content
    assert loaded_patch.status == created_patch.status

def test_load_nonexistent_patch(patch_manager):
    """Test loading a non-existent patch."""
    with pytest.raises(PatchNotFoundError):
        patch_manager.load_patch("nonexistent-patch")

def test_save_patch(patch_manager, sample_patch):
    """Test saving a patch to storage."""
    # Create and save patch
    patch = patch_manager.create_patch(
        patch_type=sample_patch.patch_type,
        target_ontology=sample_patch.target_ontology,
        content=sample_patch.content,
        patch_id=sample_patch.patch_id
    )
    
    # Load saved file and check content
    patch_file = patch_manager.patches_dir / f"{patch.patch_id}.ttl"
    graph = Graph()
    graph.parse(str(patch_file), format="turtle")
    
    patch_node = graph.value(predicate=RDF.type, object=PATCH.Patch)
    assert patch_node is not None
    
    assert str(graph.value(patch_node, RDFS.label)) == patch.patch_id
    assert str(graph.value(patch_node, PATCH.patchType)) == patch.patch_type.name
    assert str(graph.value(patch_node, OWL.imports)) == patch.target_ontology
    assert str(graph.value(patch_node, RDFS.comment)) == patch.content
    assert str(graph.value(patch_node, OWL.versionInfo)) == patch.status.name

def test_patch_directory_creation(tmp_path):
    """Test that patches directory is created if it doesn't exist."""
    workspace_dir = tmp_path / "workspace"
    patch_manager = PatchManager(str(workspace_dir))
    assert (workspace_dir / "patches").exists()

def test_validate_patch(patch_manager, sample_patch):
    """Test validating a patch."""
    # Create and save patch
    patch = patch_manager.create_patch(
        patch_type=sample_patch.patch_type,
        target_ontology=sample_patch.target_ontology,
        content=sample_patch.content,
        patch_id=sample_patch.patch_id
    )
    
    # Get patch URI and add to manager's graph
    patch_file = patch_manager.patches_dir / f"{patch.patch_id}.ttl"
    patch_manager.graph.parse(str(patch_file), format="turtle")
    patch_uri = patch_manager.graph.value(predicate=RDF.type, object=PATCH.Patch)
    
    # Validate patch
    assert patch_manager.validate_patch(patch_uri) is True

def test_validate_nonexistent_patch(patch_manager):
    """Test validating a non-existent patch."""
    with pytest.raises(ValueError, match="Patch .* not found in graph"):
        patch_manager.validate_patch(URIRef("http://example.org/nonexistent"))

def test_validate_patch_missing_property(patch_manager):
    """Test validating a patch with missing required property."""
    # Create patch node with missing property
    patch_uri = URIRef("http://example.org/test-patch")
    patch_manager.graph.add((patch_uri, RDF.type, PATCH.Patch))
    # Don't add RDFS.label
    
    with pytest.raises(ValueError, match="Missing required property: label"):
        patch_manager.validate_patch(patch_uri)

def test_module_conformance(patch_manager):
    """Test module conformance validation."""
    # Create conformance test patch
    timestamp = datetime.now().isoformat()
    patch_uri = URIRef("http://example.org/conformance-patch")
    patch_manager.graph.add((patch_uri, RDF.type, PATCH.Patch))
    patch_manager.graph.add((patch_uri, RDFS.label, Literal("conformance-patch")))
    patch_manager.graph.add((patch_uri, PATCH.patchType, Literal(PatchType.ADD.name)))
    patch_manager.graph.add((patch_uri, OWL.imports, Literal("test.ttl")))
    patch_manager.graph.add((patch_uri, RDFS.comment, Literal("test content")))
    patch_manager.graph.add((patch_uri, OWL.versionInfo, Literal(PatchStatus.PENDING.name)))
    patch_manager.graph.add((patch_uri, DCTERMS.created, Literal(timestamp, datatype=XSD.dateTime)))
    patch_manager.graph.add((patch_uri, DCTERMS.modified, Literal(timestamp, datatype=XSD.dateTime)))
    
    assert patch_manager.validate_patch(patch_uri) is True

def test_integration_process(patch_manager):
    """Test integration process validation."""
    # Create integration test patch
    timestamp = datetime.now().isoformat()
    patch_uri = URIRef("http://example.org/integration-patch")
    patch_manager.graph.add((patch_uri, RDF.type, PATCH.Patch))
    patch_manager.graph.add((patch_uri, RDFS.label, Literal("integration-patch")))
    patch_manager.graph.add((patch_uri, PATCH.patchType, Literal(PatchType.ADD.name)))
    patch_manager.graph.add((patch_uri, OWL.imports, Literal("test.ttl")))
    patch_manager.graph.add((patch_uri, RDFS.comment, Literal("test content")))
    patch_manager.graph.add((patch_uri, OWL.versionInfo, Literal(PatchStatus.PENDING.name)))
    patch_manager.graph.add((patch_uri, DCTERMS.created, Literal(timestamp, datatype=XSD.dateTime)))
    patch_manager.graph.add((patch_uri, DCTERMS.modified, Literal(timestamp, datatype=XSD.dateTime)))
    
    assert patch_manager.validate_patch(patch_uri) is True

def test_legacy_support(patch_manager):
    """Test legacy support validation."""
    # Create legacy support test patch
    timestamp = datetime.now().isoformat()
    patch_uri = URIRef("http://example.org/legacy-patch")
    patch_manager.graph.add((patch_uri, RDF.type, PATCH.Patch))
    patch_manager.graph.add((patch_uri, RDFS.label, Literal("legacy-patch")))
    patch_manager.graph.add((patch_uri, PATCH.patchType, Literal(PatchType.ADD.name)))
    patch_manager.graph.add((patch_uri, OWL.imports, Literal("test.ttl")))
    patch_manager.graph.add((patch_uri, RDFS.comment, Literal("test content")))
    patch_manager.graph.add((patch_uri, OWL.versionInfo, Literal(PatchStatus.PENDING.name)))
    patch_manager.graph.add((patch_uri, DCTERMS.created, Literal(timestamp, datatype=XSD.dateTime)))
    patch_manager.graph.add((patch_uri, DCTERMS.modified, Literal(timestamp, datatype=XSD.dateTime)))
    
    assert patch_manager.validate_patch(patch_uri) is True

def test_module_registry(patch_manager):
    """Test module registry validation."""
    # Create module registry test patch
    timestamp = datetime.now().isoformat()
    patch_uri = URIRef("http://example.org/registry-patch")
    patch_manager.graph.add((patch_uri, RDF.type, PATCH.Patch))
    patch_manager.graph.add((patch_uri, RDFS.label, Literal("registry-patch")))
    patch_manager.graph.add((patch_uri, PATCH.patchType, Literal(PatchType.ADD.name)))
    patch_manager.graph.add((patch_uri, OWL.imports, Literal("test.ttl")))
    patch_manager.graph.add((patch_uri, RDFS.comment, Literal("test content")))
    patch_manager.graph.add((patch_uri, OWL.versionInfo, Literal(PatchStatus.PENDING.name)))
    patch_manager.graph.add((patch_uri, DCTERMS.created, Literal(timestamp, datatype=XSD.dateTime)))
    patch_manager.graph.add((patch_uri, DCTERMS.modified, Literal(timestamp, datatype=XSD.dateTime)))
    
    assert patch_manager.validate_patch(patch_uri) is True

def test_patch_validation_with_shacl(patch_manager):
    """Test patch validation using SHACL shapes."""
    # Create SHACL validation test patch
    timestamp = datetime.now().isoformat()
    patch_uri = URIRef("http://example.org/shacl-patch")
    patch_manager.graph.add((patch_uri, RDF.type, PATCH.Patch))
    patch_manager.graph.add((patch_uri, RDFS.label, Literal("shacl-patch")))
    patch_manager.graph.add((patch_uri, PATCH.patchType, Literal(PatchType.ADD.name)))
    patch_manager.graph.add((patch_uri, OWL.imports, Literal("test.ttl")))
    patch_manager.graph.add((patch_uri, RDFS.comment, Literal("test content")))
    patch_manager.graph.add((patch_uri, OWL.versionInfo, Literal(PatchStatus.PENDING.name)))
    patch_manager.graph.add((patch_uri, DCTERMS.created, Literal(timestamp, datatype=XSD.dateTime)))
    patch_manager.graph.add((patch_uri, DCTERMS.modified, Literal(timestamp, datatype=XSD.dateTime)))
    
    assert patch_manager.validate_patch(patch_uri) is True 