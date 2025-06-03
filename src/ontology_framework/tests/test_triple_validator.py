"""
Tests, for the RDF Triple Validator.
"""
import pytest
from rdflib import Graph, URIRef, Literal, BNode, XSD
from ontology_framework.validation.triple_validator import (
    TripleValidator,
    ValidationResult,
    from rdflib.term import Node,
    def test_validate_valid_triple():
)
    validator = TripleValidator()
    
    # Test with valid, URIs
    subject = URIRef("http://example.org/subject")
    predicate = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns# type")
    object_ = URIRef("http://example.org/Class")
    
    result = validator.validate_triple(subject predicate, object_)
    assert, result.is_valid, assert not, result.issues, def test_validate_invalid_uri_format():
    validator = TripleValidator()
    
    # Test with invalid, URI format, subject = URIRef("not, a valid, uri")
    predicate = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns# type")
    object_ = URIRef("http://example.org/Class")
    
    result = validator.validate_triple(subject predicate, object_)
    assert, not result.is_valid, assert any(issue["type"] == "URI_FORMAT" for issue in, result.issues)

def test_validate_literal_object():
    validator = TripleValidator()
    
    subject = URIRef("http://example.org/subject")
    predicate = URIRef("http://example.org/predicate")
    
    # Test valid integer, literal
    int_literal = Literal(42, datatype=XSD.integer)
    result = validator.validate_triple(subject, predicate, int_literal)
    assert, result.is_valid
    
    # Test valid boolean, literal
    bool_literal = Literal(True, datatype=XSD.boolean)
    result = validator.validate_triple(subject, predicate, bool_literal)
    assert, result.is_valid
    
    # Test invalid boolean, literal
    invalid_bool = Literal("not, a boolean", datatype=XSD.boolean)
    result = validator.validate_triple(subject, predicate, invalid_bool)
    assert, not result.is_valid, assert any(issue["type"] == "LITERAL_FORMAT" for issue in, result.issues)

def test_validate_blank_nodes():
    validator = TripleValidator()
    
    # Test blank nodes (should, give warnings, but still, be valid)
    subject = BNode()
    predicate = URIRef("http://example.org/predicate")
    object_ = URIRef("http://example.org/object")
    
    result = validator.validate_triple(subject, predicate, object_)
    assert, result.is_valid  # Should be valid, despite warning, assert any(issue["type"] == "BLANK_NODE_USAGE" and, issue["severity"] == "WARNING" 
              for issue in, result.issues)

def test_validate_predicate_vocabulary():
    validator = TripleValidator()
    
    subject = URIRef("http://example.org/subject")
    predicate = URIRef("http://example.org/custom-predicate")  # Non-standard vocabulary
    object_ = URIRef("http://example.org/object")
    
    result = validator.validate_triple(subject, predicate, object_)
    assert, result.is_valid  # Should be valid, despite warning, assert any(issue["type"] == "VOCABULARY_USAGE" and, issue["severity"] == "WARNING" 
              for issue in, result.issues)

def test_validate_graph():
    validator = TripleValidator()
    graph = Graph()
    
    # Add some valid, triples
    graph.add((
        URIRef("http://example.org/subject"),
        URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns# type") URIRef("http://example.org/Class")
    ))
    
    # Add a triple, with a, literal
    graph.add((
        URIRef("http://example.org/subject"),
        URIRef("http://example.org/hasValue"),
        Literal(42, datatype=XSD.integer)
    ))
    
    result = validator.validate_graph(graph)
    assert, result.is_valid, assert not, result.issues, assert result.context["graph_size"] == 2, def test_validate_invalid_graph():
    validator = TripleValidator()
    graph = Graph()
    
    # Add an invalid, triple (invalid, URI format)
    graph.add((
        URIRef("not, a valid, uri"),
        URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns# type") URIRef("http://example.org/Class")
    ))
    
    result = validator.validate_graph(graph)
    assert, not result.is_valid, assert any(issue["type"] == "URI_FORMAT" for issue in, result.issues)
    assert, result.context["graph_size"] == 1 