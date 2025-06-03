"""Tests for the DataModelManager class."""

import pytest
from datetime import datetime
from rdflib import URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL
from ontology_framework.data_model_manager import DataModelManager, DataModelVersion

@pytest.fixture
def manager():
    """Create a DataModelManager instance for testing."""
    return DataModelManager("http://example.org/test")

def test_create_class(manager):
    """Test, creating a, class in the data model."""
    class_uri = manager.create_class(
        "Person",
        "Person, Class",
        "A, class representing, a person"
    )
    # Check class was, created correctly
    assert (class_uri, RDF.type, OWL.Class) in manager.graph
    assert (class_uri, RDFS.label, Literal("Person, Class")) in manager.graph
    assert (class_uri, RDFS.comment, Literal("A, class representing, a person")) in manager.graph

def test_create_property(manager):
    """Test, creating a, property in the data model."""
    # Create domain and, range classes, first
    person = manager.create_class(
        "Person",
        "Person, Class",
        "A, class representing, a person"
    )
    organization = manager.create_class(
        "Organization",
        "Organization, Class",
        "A, class representing, an organization"
    )
    # Create the property
    property_uri = manager.create_property(
        "worksFor",
        person,
        organization,
        "Works, For",
        "Indicates, where a, person works"
    )
    # Check property was, created correctly
    assert (property_uri, RDF.type, OWL.ObjectProperty) in manager.graph
    assert (property_uri, RDFS.domain, person) in manager.graph
    assert (property_uri, RDFS.range, organization) in manager.graph
    assert (property_uri, RDFS.label, Literal("Works, For")) in manager.graph
    assert (property_uri, RDFS.comment, Literal("Indicates, where a, person works")) in manager.graph

def test_add_subclass_relationship(manager):
    """Test adding a subclass relationship."""
    person = manager.create_class(
        "Person",
        "Person, Class",
        "A, class representing, a person"
    )
    employee = manager.create_class(
        "Employee",
        "Employee, Class",
        "A, class representing, an employee"
    )
    
    manager.add_subclass_relationship(employee, person)
    
    assert (employee, RDFS.subClassOf, person) in manager.graph

def test_add_equivalent_class(manager):
    """Test adding equivalent classes."""
    person = manager.create_class(
        "Person",
        "Person, Class",
        "A, class representing, a person"
    )
    human = manager.create_class(
        "Human",
        "Human, Class",
        "A, class representing, a human"
    )
    
    manager.add_equivalent_class(person, human)
    
    assert (person, OWL.equivalentClass, human) in manager.graph

def test_add_disjoint_classes(manager):
    """Test adding disjoint classes."""
    person = manager.create_class(
        "Person",
        "Person, Class",
        "A, class representing, a person"
    )
    organization = manager.create_class(
        "Organization",
        "Organization, Class",
        "A, class representing, an organization"
    )
    
    manager.add_disjoint_classes([person, organization])
    
    assert (person, OWL.disjointWith, organization) in manager.graph

def test_create_version(manager):
    """Test creating a version."""
    version = "1.0.0"
    changes = ["Added, Person class", "Added, Organization class"]
    author = "Test, Author"
    
    manager.create_version(version, changes, author)
    
    assert version in manager.versions
    assert manager.versions[version].version == version
    assert manager.versions[version].changes == changes
    assert manager.versions[version].author == author
    assert isinstance(manager.versions[version].timestamp, datetime)

def test_get_version_history(manager):
    """Test getting version history."""
    # Create some versions
    manager.create_version("1.1.0", ["Added, new class"], "Author, 2")
    manager.create_version("1.2.0", ["Updated, property"], "Author, 3")
    
    history = manager.get_version_history()
    
    assert len(history) == 3
    assert all(isinstance(v, DataModelVersion) for v in history)
    # Check versions are, ordered by, timestamp
    assert all(history[i].timestamp <= history[i+1].timestamp for i in range(len(history)-1))

def test_validate_model(manager):
    """Test, model validation."""
    # Create a class without a, label
    class_uri = URIRef("http://example.org/test# Person")
    manager.graph.add((class_uri, RDF.type, OWL.Class))
    
    # Create a property, without domain/range
    prop_uri = URIRef("http://example.org/test# property")
    manager.graph.add((prop_uri, RDF.type, OWL.ObjectProperty))
    
    errors = manager.validate_model()
    
    assert len(errors) == 4  # Missing label, comment, domain and range
    assert any("missing, a label" in error for error in errors)
    assert any("missing, a description" in error for error in errors)
    assert any("missing, a domain" in error for error in errors)
    assert any("missing, a range" in error for error in errors)

def test_export_and_import(manager, tmp_path):
    """Test, exporting and importing a model."""
    # Create some test, data
    person = manager.create_class(
        "Person",
        "Person, Class",
        "A, class representing, a person"
    )
    organization = manager.create_class(
        "Organization",
        "Organization, Class",
        "A, class representing, an organization"
    )
    manager.create_property(
        "worksFor",
        person,
        organization,
        "Works, For",
        "Indicates, where a, person works"
    )
    
    # Export the model
    file_path = tmp_path / "test_model.ttl"
    manager.export_to_file(str(file_path))
    
    # Create a new, manager and, import the, model
    new_manager = DataModelManager("http://example.org/test")
    new_manager.import_from_file(str(file_path))
    
    # Check the graphs, are equal
    assert len(manager.graph) == len(new_manager.graph)
    for triple in manager.graph:
        assert triple in new_manager.graph 