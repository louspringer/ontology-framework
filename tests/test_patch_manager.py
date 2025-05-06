"""Test module for the PatchManager class."""

import pytest
from pathlib import Path
import shutil
from datetime import datetime
from rdflib import Graph, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, RDFS, OWL, DCTERMS, XSD
from ontology_framework.modules.patch_management import PatchManager, PatchNotFoundError
from ontology_framework.meta import PatchType, OntologyPatch, PatchStatus, MetaOntology

PATCH = Namespace("http://example.org/ontology/")

@pytest.fixture
def patch_manager():
    """Create a PatchManager instance for testing."""
    meta_ontology = MetaOntology()
    return PatchManager(meta_ontology=meta_ontology)

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

def test_create_patch(patch_manager):
    """Test creating a new patch."""
    patch = patch_manager.create_patch(
        patch_id="test-patch-1",
        description="Test patch",
        patch_type=PatchType.ADD,
        target_ontology="test.ttl",
        content="@prefix : <http://example.org/test#> .\n@prefix owl: <http://www.w3.org/2002/07/owl#> .\n:TestClass a owl:Class ."
    )
    
    assert patch is not None
    assert isinstance(patch, Graph)
    
    # Check patch metadata
    patch_uri = next(patch.subjects(RDF.type, PATCH.Patch))
    assert patch.value(patch_uri, RDFS.label) == Literal("Test patch")
    assert patch.value(patch_uri, PATCH.createdAt) is not None
    assert patch.value(patch_uri, PATCH.patchType) == Literal(PatchType.ADD.name)
    assert patch.value(patch_uri, OWL.imports) == Literal("test.ttl")
    assert patch.value(patch_uri, RDFS.comment) is not None

def test_get_patch(patch_manager):
    """Test retrieving a patch."""
    # First create a patch
    patch = patch_manager.create_patch(
        patch_id="test-patch-1",
        description="Test patch",
        patch_type=PatchType.ADD,
        target_ontology="test.ttl",
        content="@prefix : <http://example.org/test#> .\n@prefix owl: <http://www.w3.org/2002/07/owl#> .\n:TestClass a owl:Class ."
    )
    
    # Get the patch
    retrieved_patch = patch_manager.get_patch("test-patch-1")
    assert retrieved_patch is not None
    assert isinstance(retrieved_patch, Graph)
    
    # Check patch metadata
    patch_uri = next(retrieved_patch.subjects(RDF.type, PATCH.Patch))
    assert retrieved_patch.value(patch_uri, RDFS.label) == Literal("Test patch")

def test_get_nonexistent_patch(patch_manager):
    """Test retrieving a non-existent patch."""
    with pytest.raises(PatchNotFoundError):
        patch_manager.get_patch("nonexistent-patch")

def test_list_patches(patch_manager):
    """Test listing patches."""
    # Create some patches
    patch_manager.create_patch(
        patch_id="patch-1",
        description="First patch",
        patch_type=PatchType.ADD,
        target_ontology="test.ttl",
        content="@prefix : <http://example.org/test#> .\n@prefix owl: <http://www.w3.org/2002/07/owl#> .\n:TestClass1 a owl:Class ."
    )
    patch_manager.create_patch(
        patch_id="patch-2",
        description="Second patch",
        patch_type=PatchType.ADD,
        target_ontology="test.ttl",
        content="@prefix : <http://example.org/test#> .\n@prefix owl: <http://www.w3.org/2002/07/owl#> .\n:TestClass2 a owl:Class ."
    )
    
    # List patches
    patches = patch_manager.list_patches()
    assert len(patches) == 2
    assert "patch-1" in patches
    assert "patch-2" in patches

def test_apply_patch(patch_manager):
    """Test applying a patch."""
    # Create a patch with content
    patch = patch_manager.create_patch(
        patch_id="test-patch-1",
        description="Test patch",
        patch_type=PatchType.ADD,
        target_ontology="test.ttl",
        content="@prefix : <http://example.org/test#> .\n@prefix owl: <http://www.w3.org/2002/07/owl#> .\n:TestClass a owl:Class ."
    )
    
    # Create a target graph
    target_graph = Graph()
    
    # Apply the patch
    patch_manager.apply_patch("test-patch-1", target_graph)
    
    # Check that the patch was applied
    assert len(target_graph) > 0
    assert (URIRef("http://example.org/test#TestClass"), RDF.type, OWL.Class) in target_graph

def test_validate_patch(patch_manager):
    """Test validating a patch."""
    # Create a patch with all required properties
    patch = patch_manager.create_patch(
        patch_id="test-patch-1",
        description="Test patch",
        patch_type=PatchType.ADD,
        target_ontology="test.ttl",
        content="@prefix : <http://example.org/test#> .\n@prefix owl: <http://www.w3.org/2002/07/owl#> .\n:TestClass a owl:Class ."
    )
    
    # Validate the patch
    assert patch_manager.validate_patch("test-patch-1") is True

def test_validate_nonexistent_patch(patch_manager):
    """Test validating a non-existent patch."""
    assert patch_manager.validate_patch("nonexistent-patch") is False

def test_load_patch(patch_manager):
    """Test loading a patch from storage."""
    # First create and save a patch
    patch_id = "test-patch-1"
    description = "Test patch"
    patch_type = PatchType.ADD
    target_ontology = "test.ttl"
    content = "@prefix : <http://example.org/test#> .\n@prefix owl: <http://www.w3.org/2002/07/owl#> .\n:TestClass a owl:Class ."
    
    patch_manager.create_patch(
        patch_id=patch_id,
        description=description,
        patch_type=patch_type,
        target_ontology=target_ontology,
        content=content
    )
    
    # Load the patch
    loaded_patch = patch_manager.load_patch(patch_id)
    
    assert loaded_patch.patch_id == patch_id
    assert loaded_patch.patch_type == patch_type
    assert loaded_patch.target_ontology == target_ontology
    assert loaded_patch.content == content
    assert loaded_patch.status == PatchStatus.PENDING

def test_save_patch(patch_manager):
    """Test saving a patch to storage."""
    # Create patch data
    patch_id = "test-patch-1"
    description = "Test patch"
    patch_type = PatchType.ADD
    target_ontology = "test.ttl"
    content = "@prefix : <http://example.org/test#> .\n@prefix owl: <http://www.w3.org/2002/07/owl#> .\n:TestClass a owl:Class ."
    
    # Create patch
    patch = OntologyPatch(
        patch_id=patch_id,
        patch_type=patch_type,
        target_ontology=target_ontology,
        content=content,
        status=PatchStatus.PENDING,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )
    
    # Save patch
    patch_manager.save_patch(patch)
    
    # Verify saved patch
    loaded_patch = patch_manager.load_patch(patch_id)
    assert loaded_patch.patch_id == patch_id
    assert loaded_patch.patch_type == patch_type
    assert loaded_patch.target_ontology == target_ontology
    assert loaded_patch.content == content
    assert loaded_patch.status == PatchStatus.PENDING

def test_patch_directory_creation(tmp_path):
    """Test that patches directory is created if it doesn't exist."""
    meta_ontology = MetaOntology()
    patch_manager = PatchManager(meta_ontology=meta_ontology)
    assert patch_manager.patches_dir.exists()

def test_validate_patch_missing_property(patch_manager):
    """Test validating a patch with missing required property."""
    # Create patch node with missing property
    patch_uri = URIRef("http://example.org/ontology/test-patch")
    patch_manager.graph.add((patch_uri, RDF.type, PATCH.Patch))
    # Don't add RDFS.label
    
    # Validate should return False for missing property
    assert patch_manager.validate_patch(patch_uri) is False

def test_module_conformance(patch_manager):
    """Test module conformance validation."""
    # Create conformance test patch
    patch = patch_manager.create_patch(
        patch_id="conformance-patch",
        description="Conformance test patch",
        patch_type=PatchType.ADD,
        target_ontology="test.ttl",
        content="@prefix : <http://example.org/test#> .\n@prefix owl: <http://www.w3.org/2002/07/owl#> .\n:TestClass a owl:Class ."
    )
    
    assert patch_manager.validate_patch("conformance-patch") is True

def test_integration_process(patch_manager):
    """Test integration process validation."""
    # Create integration test patch
    patch = patch_manager.create_patch(
        patch_id="integration-patch",
        description="Integration test patch",
        patch_type=PatchType.ADD,
        target_ontology="test.ttl",
        content="@prefix : <http://example.org/test#> .\n@prefix owl: <http://www.w3.org/2002/07/owl#> .\n:TestClass a owl:Class ."
    )
    
    assert patch_manager.validate_patch("integration-patch") is True

def test_legacy_support(patch_manager):
    """Test legacy support validation."""
    # Create legacy support test patch
    patch = patch_manager.create_patch(
        patch_id="legacy-patch",
        description="Legacy support test patch",
        patch_type=PatchType.ADD,
        target_ontology="test.ttl",
        content="@prefix : <http://example.org/test#> .\n@prefix owl: <http://www.w3.org/2002/07/owl#> .\n:TestClass a owl:Class ."
    )
    
    assert patch_manager.validate_patch("legacy-patch") is True

def test_module_registry(patch_manager):
    """Test module registry validation."""
    # Create module registry test patch
    patch = patch_manager.create_patch(
        patch_id="registry-patch",
        description="Module registry test patch",
        patch_type=PatchType.ADD,
        target_ontology="test.ttl",
        content="@prefix : <http://example.org/test#> .\n@prefix owl: <http://www.w3.org/2002/07/owl#> .\n:TestClass a owl:Class ."
    )
    
    assert patch_manager.validate_patch("registry-patch") is True

def test_patch_validation_with_shacl(patch_manager):
    """Test patch validation using SHACL shapes."""
    # Create SHACL validation test patch
    patch = patch_manager.create_patch(
        patch_id="shacl-patch",
        description="SHACL validation test patch",
        patch_type=PatchType.ADD,
        target_ontology="test.ttl",
        content="@prefix : <http://example.org/test#> .\n@prefix owl: <http://www.w3.org/2002/07/owl#> .\n:TestClass a owl:Class ."
    )
    
    assert patch_manager.validate_patch("shacl-patch") is True 