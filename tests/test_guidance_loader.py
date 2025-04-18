import pytest
from pathlib import Path
from rdflib import Graph, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD
from ontology_framework.guidance_loader import GuidanceLoader
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture
def guidance_ttl(tmp_path):
    """Create a temporary guidance.ttl file with test data."""
    guidance_file = tmp_path / "guidance.ttl"
    content = """
    @prefix : <http://example.org/guidance#> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix owl: <http://www.w3.org/2002/07/owl#> .
    @prefix sh: <http://www.w3.org/ns/shacl#> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

    :TestProtocol a owl:Class ;
        rdfs:label "Test Protocol" ;
        rdfs:comment "A protocol for testing ontology components" .

    :TestPhase a owl:Class ;
        rdfs:label "Test Phase" ;
        rdfs:comment "A phase in the testing process" .

    :TestCoverage a owl:Class ;
        rdfs:label "Test Coverage" ;
        rdfs:comment "Coverage metrics for testing" .

    :ModelConformance a owl:Class ;
        rdfs:label "Model Conformance" ;
        rdfs:comment "Rules for ensuring model consistency" .

    :IntegrationProcess a owl:Class ;
        rdfs:label "Integration Process" ;
        rdfs:comment "Process for integrating model changes" .

    :SampleTestProtocol a :TestProtocol ;
        rdfs:label "Sample Test Protocol" ;
        rdfs:comment "A sample test protocol for unit testing" ;
        :conformanceLevel "STRICT" ;
        :requiresPrefixValidation "true"^^xsd:boolean ;
        :requiresNamespaceValidation "true"^^xsd:boolean .

    :Phase1 a :TestPhase ;
        rdfs:label "Phase 1" ;
        rdfs:comment "The first phase of testing" .

    :StandardCoverage a :TestCoverage ;
        rdfs:label "Standard Coverage" ;
        rdfs:comment "Standard test coverage requirements" .

    :ModelConformance1 a :ModelConformance ;
        rdfs:label "Strict Conformance" ;
        rdfs:comment "Strict model conformance rules" ;
        :conformanceLevel "STRICT" .

    :IntegrationStep1 a :IntegrationStep ;
        rdfs:label "Step 1" ;
        :stepOrder "1" ;
        :stepDescription "First integration step" .

    :TestShape a sh:NodeShape ;
        sh:targetClass :TestProtocol ;
        rdfs:label "Test Protocol Shape" ;
        rdfs:comment "SHACL shape for validating test protocols" ;
        sh:property [
            sh:path :hasTestPhase ;
            sh:minCount 1 ;
            sh:maxCount 5 ;
            sh:datatype xsd:string
        ] .

    :ModelConformanceShape a sh:NodeShape ;
        sh:targetClass :ModelConformance ;
        sh:property [
            sh:path :conformanceLevel ;
            sh:datatype xsd:string ;
            sh:in ("STRICT" "MODERATE" "RELAXED")
        ] .
    """
    guidance_file.write_text(content)
    return guidance_file

@pytest.fixture
def guidance_loader(guidance_ttl):
    """Create a GuidanceLoader instance with the sample guidance file."""
    return GuidanceLoader(guidance_ttl)

def test_get_section(guidance_loader):
    """Test retrieving a specific section from the guidance ontology."""
    results = guidance_loader.get_section("TestProtocol")
    assert len(results) > 0
    assert any(r["subject"].endswith("TestProtocol") for r in results)
    assert any(r["predicate"].endswith("type") for r in results)

def test_get_requirements(guidance_loader):
    """Test retrieving specific requirements from the guidance ontology."""
    results = guidance_loader.get_requirements("TestProtocol")
    assert len(results) > 0
    protocol = next(r for r in results if r["label"] == "Sample Test Protocol")
    assert protocol["comment"] == "A sample test protocol for unit testing"

def test_get_test_requirements(guidance_loader):
    """Test retrieving all test-related requirements."""
    requirements = guidance_loader.get_test_requirements()
    assert "protocols" in requirements
    assert "phases" in requirements
    assert "coverage" in requirements
    assert "shapes" in requirements
    
    # Verify protocols
    assert len(requirements["protocols"]) > 0
    assert any(p["label"] == "Sample Test Protocol" for p in requirements["protocols"])
    
    # Verify phases
    assert len(requirements["phases"]) > 0
    assert any(p["label"] == "Phase 1" for p in requirements["phases"])
    
    # Verify coverage
    assert len(requirements["coverage"]) > 0
    assert any(c["label"] == "Standard Coverage" for c in requirements["coverage"])

def test_get_shapes(guidance_loader):
    """Test retrieving SHACL shapes from the guidance ontology."""
    shapes = guidance_loader.get_shapes()
    assert len(shapes) > 0
    protocol_shape = next(s for s in shapes if s["targetClass"].endswith("TestProtocol"))
    assert protocol_shape["minCount"] == 1
    assert protocol_shape["maxCount"] == 5

def test_get_model_conformance(guidance_loader):
    """Test retrieving model conformance requirements."""
    conformance = guidance_loader.get_section("ModelConformance")
    assert len(conformance) > 0
    assert any(c["predicate"].endswith("conformanceLevel") for c in conformance)

def test_get_integration_process(guidance_loader):
    """Test retrieving integration process steps."""
    steps = guidance_loader.get_section("IntegrationStep")
    assert len(steps) > 0
    step1 = next(s for s in steps if s["subject"].endswith("IntegrationStep1"))
    assert step1["object"] == "1"  # stepOrder value

def test_validate_conformance_level(guidance_loader):
    """Test validation of conformance level values."""
    shapes = guidance_loader.get_shapes()
    conformance_shape = next(s for s in shapes if s["targetClass"].endswith("ModelConformance"))
    assert "allowedValues" in conformance_shape
    assert "STRICT" in conformance_shape["allowedValues"]
    assert "MODERATE" in conformance_shape["allowedValues"]
    assert "RELAXED" in conformance_shape["allowedValues"]

def test_invalid_section(guidance_loader):
    """Test retrieving a non-existent section."""
    results = guidance_loader.get_section("NonExistentSection")
    assert len(results) == 0

def test_invalid_requirement_type(guidance_loader):
    """Test retrieving requirements for a non-existent type."""
    results = guidance_loader.get_requirements("NonExistentType")
    assert len(results) == 0

def test_validate_test_protocol(guidance_loader):
    """Test validation of a test protocol against its SHACL shape."""
    protocol = guidance_loader.get_requirements("TestProtocol")[0]
    validation_result = guidance_loader.validate_against_shape(protocol, "TestShape")
    assert validation_result["isValid"]
    assert len(validation_result["violations"]) == 0 