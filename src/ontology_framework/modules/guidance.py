"""Module for managing the guidance ontology."""

from rdflib import Graph, URIRef, Literal, BNode, Namespace, XSD, RDF, RDFS, OWL, SH
from rdflib.namespace import RDF, RDFS, OWL, XSD
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, cast, Sequence, TypedDict, TypeGuard, Tuple
from rdflib.query import ResultRow, Result
from .ontology import Ontology
from .constants import CONFORMANCE_LEVELS
from rdflib.term import Node

# Define SHACL terms
SH_CLASS = URIRef("http://www.w3.org/ns/shacl#class")
SH_IN = URIRef("http://www.w3.org/ns/shacl#in")

# Type definitions
ClassDefinition = Tuple[URIRef, str, str]
PropertyDefinition = Tuple[URIRef, str, str, URIRef, Union[URIRef, XSD]]
ShapeProperty = Tuple[URIRef, Union[URIRef, XSD], int, Optional[int]]
ShapeDefinition = Tuple[URIRef, URIRef, List[ShapeProperty]]
IndividualProperty = Dict[URIRef, Union[str, bool]]
IndividualDefinition = Tuple[URIRef, URIRef, str, str, Dict[URIRef, Union[str, bool]]]

class GuidanceOntology(Ontology):
    """Class for managing the guidance ontology."""
    
    def __init__(self, base_uri: str = "http://example.org/guidance#", guidance_file: Optional[Union[str, Path]] = None) -> None:
        """Initialize the guidance ontology."""
        super().__init__(base_uri)
        self._initialize_uris()
        
        if guidance_file:
            self.load(guidance_file)
            self._normalize_uris()
        else:
            self._initialize_guidance_ontology()

    def _create_uri(self, local_name: str) -> URIRef:
        """Create a URI reference for a name.
        
        Args:
            name: Name to create URI for.
            
        Returns:
            URIRef for the name.
        """
        return URIRef(f"{self.base_uri}{local_name}")

    def _initialize_uris(self) -> None:
        """Initialize core URIs as class attributes."""
        self.ValidationProcess = self._create_uri("ValidationProcess")
        self.ValidationRule = self._create_uri("ValidationRule")
        self.ValidationRuleShape = self._create_uri("ValidationRuleShape")
        self.IntegrationProcess = self._create_uri("IntegrationProcess")
        self.TestPhase = self._create_uri("TestPhase")
        self.hasStringRepresentation = self._create_uri("hasStringRepresentation")

    def _normalize_uris(self) -> None:
        """Normalize URIs to use consistent base URI."""
        old_base = "https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#"
        new_base = str(self.base_uri)
        
        # Create a new graph with normalized URIs
        new_graph = Graph()
        new_graph.bind("guidance", URIRef(self.base_uri))
        
        # Copy all triples with normalized URIs
        for s, p, o in sorted(self.graph, key=lambda x: (str(x[0]), str(x[1]), str(x[2]))):
            new_s = URIRef(str(s).replace(old_base, new_base)) if isinstance(s, URIRef) else s
            new_p = URIRef(str(p).replace(old_base, new_base)) if isinstance(p, URIRef) else p
            new_o = URIRef(str(o).replace(old_base, new_base)) if isinstance(o, URIRef) else o
            new_graph.add((new_s, new_p, new_o))
            
        # Replace the old graph with the normalized one
        self.graph = new_graph

    def _initialize_guidance_ontology(self) -> None:
        """Initialize the guidance ontology with core classes and properties."""
        # Add metadata
        base_uri = URIRef(self.base_uri)
        self.graph.add((base_uri, RDF.type, OWL.Ontology))
        self.graph.add((base_uri, RDFS.label, Literal("Guidance Ontology")))
        self.graph.add((base_uri, RDFS.comment, Literal("Ontology for managing guidance and validation rules")))
        self.graph.add((base_uri, OWL.versionInfo, Literal("1.0.0")))

        # Define class hierarchy
        self.graph.add((self.ValidationProcess, RDF.type, OWL.Class))
        self.graph.add((self.ValidationProcess, RDFS.label, Literal("Validation Process")))
        
        # Add TestPhase class and properties
        self.graph.add((self.TestPhase, RDF.type, OWL.Class))
        self.graph.add((self.TestPhase, RDFS.label, Literal("Test Phase")))
        self.graph.add((self.TestPhase, RDFS.comment, Literal("A phase in the testing process")))
        self.graph.add((self.TestPhase, RDFS.subClassOf, self.ValidationProcess))
        
        # Add example test phase individuals
        unit_test = self._create_uri("UnitTestPhase")
        integration_test = self._create_uri("IntegrationTestPhase")
        
        self.graph.add((unit_test, RDF.type, self.TestPhase))
        self.graph.add((unit_test, RDFS.label, Literal("Unit Test Phase")))
        self.graph.add((unit_test, self.hasStringRepresentation, Literal("Unit testing phase of validation")))
        
        self.graph.add((integration_test, RDF.type, self.TestPhase))
        self.graph.add((integration_test, RDFS.label, Literal("Integration Test Phase")))
        self.graph.add((integration_test, self.hasStringRepresentation, Literal("Integration testing phase of validation")))
        
        # Add subclasses for better organization
        self.graph.add((self.IntegrationProcess, RDFS.subClassOf, self.ValidationProcess))
        
        self.graph.add((self.ValidationRule, RDF.type, OWL.Class))
        self.graph.add((self.ValidationRule, RDFS.label, Literal("Validation Rule")))
        
        # Add subclasses for validation rules
        self.SyntaxRule = self._create_uri("SyntaxRule")
        self.SemanticRule = self._create_uri("SemanticRule")
        self.ConsistencyRule = self._create_uri("ConsistencyRule")
        
        self.graph.add((self.SyntaxRule, RDFS.subClassOf, self.ValidationRule))
        self.graph.add((self.SemanticRule, RDFS.subClassOf, self.ValidationRule))
        self.graph.add((self.ConsistencyRule, RDFS.subClassOf, self.ValidationRule))
        
        # Add example individuals
        syntax_rule_1 = self._create_uri("TurtleSyntaxRule")
        self.graph.add((syntax_rule_1, RDF.type, self.SyntaxRule))
        self.graph.add((syntax_rule_1, RDFS.label, Literal("Turtle Syntax Validation")))
        self.graph.add((syntax_rule_1, self.hasStringRepresentation, Literal("Validate Turtle syntax")))
        
        semantic_rule_1 = self._create_uri("ClassHierarchyRule")
        self.graph.add((semantic_rule_1, RDF.type, self.SemanticRule))
        self.graph.add((semantic_rule_1, RDFS.label, Literal("Class Hierarchy Validation")))
        self.graph.add((semantic_rule_1, self.hasStringRepresentation, Literal("Validate class hierarchy consistency")))
        
        # Add SHACL shapes with enhanced constraints
        self.graph.add((self.ValidationRuleShape, RDF.type, SH.NodeShape))
        self.graph.add((self.ValidationRuleShape, SH.targetClass, self.ValidationRule))
        
        # Add property constraints
        label_constraint = BNode()
        self.graph.add((self.ValidationRuleShape, SH.property, label_constraint))
        self.graph.add((label_constraint, SH.path, RDFS.label))
        self.graph.add((label_constraint, SH.minCount, Literal(1)))
        self.graph.add((label_constraint, SH.datatype, XSD.string))
        
        representation_constraint = BNode()
        self.graph.add((self.ValidationRuleShape, SH.property, representation_constraint))
        self.graph.add((representation_constraint, SH.path, self.hasStringRepresentation))
        self.graph.add((representation_constraint, SH.minCount, Literal(1)))
        self.graph.add((representation_constraint, SH.maxCount, Literal(1)))

    def emit(self, output_path: Union[str, Path] = "guidance.ttl") -> None:
        """Emit the guidance ontology to a Turtle file.
        
        Args:
            output_path: Path where to save the guidance.ttl file
        """
        self.save(output_path)
        
    def get_conformance_levels(self) -> List[Dict[str, str]]:
        """Get all conformance levels and their properties.
        
        Returns:
            List of dictionaries containing conformance level details
        """
        query = """
        PREFIX : <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?level ?string_rep ?rules ?requirements ?metrics ?label ?comment
        WHERE {
            ?level rdf:type :ConformanceLevel ;
                   :hasStringRepresentation ?string_rep ;
                   :hasValidationRules ?rules ;
                   :hasMinimumRequirements ?requirements ;
                   :hasComplianceMetrics ?metrics ;
                   rdfs:label ?label ;
                   rdfs:comment ?comment .
        }
        """
        results = []
        for row in self.query(query):
            if isinstance(row, ResultRow):
                results.append({
                    'uri': str(row[0]),
                    'string_rep': str(row[1]),
                    'rules': str(row[2]),
                    'requirements': str(row[3]),
                    'metrics': str(row[4]),
                    'label': str(row[5]),
                    'comment': str(row[6])
                })
        return results
    
    def get_validation_rules(self) -> List[Dict[str, str]]:
        """Get all validation rules from the guidance ontology.
        
        Returns:
            List of dictionaries containing validation rule details
        """
        query = """
        PREFIX : <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#>
        SELECT ?pattern ?label ?description ?priority
        WHERE {
            ?rule rdf:type :ValidationRule ;
                  :hasPattern ?pattern ;
                  rdfs:label ?label ;
                  rdfs:comment ?description ;
                  :hasPriority ?priority .
        }
        """
        results = []
        for row in self.query(query):
            if isinstance(row, ResultRow):
                results.append({
                    'pattern': str(row[0]),
                    'label': str(row[1]),
                    'description': str(row[2]),
                    'priority': str(row[3])
                })
        return results

if __name__ == "__main__":
    # Generate guidance.ttl in the project root
    project_root = Path(__file__).parent.parent.parent
    output_path = project_root / "guidance.ttl"
    guidance = GuidanceOntology()
    guidance.emit(output_path) 