from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, XSD, OWL, SH
import logging
from typing import List, Dict, Any, Optional
from .ontology_types import ErrorType, ValidationRule, ErrorStep, RiskLevel, ErrorSeverity

class OntologyManager:
    """Manages ontology operations using rdflib."""
    
    def __init__(self, ontology_path: str):
        """Initialize the ontology manager with a path to the ontology file."""
        self.graph = Graph()
        self.ontology_path = ontology_path
        self.logger = logging.getLogger(__name__)
        
        # Define namespaces
        self.ERROR = Namespace("http://example.org/error#")
        self.MODULE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/#")
        
        # Load existing ontology if it exists
        try:
            self.graph.parse(ontology_path, format="turtle")
        except Exception as e:
            self.logger.warning(f"Could not load existing ontology: {e}")
            self.graph = Graph()
            
        # Bind namespaces
        self.graph.bind("error", self.ERROR)
        self.graph.bind("module", self.MODULE)
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("xsd", XSD)
        self.graph.bind("owl", OWL)
        self.graph.bind("sh", SH)
    
    def add_error_type(self, error_type: ErrorType, label: str, comment: str) -> None:
        """Add a new error type to the ontology."""
        error_uri = self.ERROR[error_type.name]
        self.graph.add((error_uri, RDF.type, self.ERROR.ErrorType))
        self.graph.add((error_uri, RDFS.label, Literal(label)))
        self.graph.add((error_uri, RDFS.comment, Literal(comment)))
    
    def add_validation_rule(self, rule: ValidationRule, label: str, comment: str) -> None:
        """Add a new validation rule to the ontology."""
        rule_uri = self.ERROR[rule.name]
        self.graph.add((rule_uri, RDF.type, self.ERROR.ValidationRule))
        self.graph.add((rule_uri, RDFS.label, Literal(label)))
        self.graph.add((rule_uri, RDFS.comment, Literal(comment)))
    
    def add_handling_step(self, step: ErrorStep, label: str, comment: str, order: int) -> None:
        """Add a new error handling step to the ontology."""
        step_uri = self.ERROR[step.name]
        self.graph.add((step_uri, RDF.type, self.ERROR.HandlingStep))
        self.graph.add((step_uri, RDFS.label, Literal(label)))
        self.graph.add((step_uri, RDFS.comment, Literal(comment)))
        self.graph.add((step_uri, self.ERROR.stepOrder, Literal(order, datatype=XSD.integer)))
    
    def add_risk(self, risk_name: str, label: str, comment: str, severity: RiskLevel) -> None:
        """Add a new risk to the ontology."""
        risk_uri = self.ERROR[risk_name]
        self.graph.add((risk_uri, RDF.type, self.ERROR.Risk))
        self.graph.add((risk_uri, RDFS.label, Literal(label)))
        self.graph.add((risk_uri, RDFS.comment, Literal(comment)))
        self.graph.add((risk_uri, self.ERROR.hasSeverity, Literal(severity.value)))
    
    def add_shacl_shape(self, shape_name: str, target_class: URIRef, properties: List[Dict]) -> None:
        """Add a SHACL shape to the ontology."""
        shape_uri = self.ERROR[shape_name]
        self.graph.add((shape_uri, RDF.type, SH.NodeShape))
        self.graph.add((shape_uri, SH.targetClass, target_class))
        
        for prop in properties:
            prop_uri = self.graph.resource(shape_uri)
            prop_uri.add(SH.path, prop["path"])
            if "minCount" in prop:
                prop_uri.add(SH.minCount, Literal(prop["minCount"], datatype=XSD.integer))
            if "maxCount" in prop:
                prop_uri.add(SH.maxCount, Literal(prop["maxCount"], datatype=XSD.integer))
            if "datatype" in prop:
                prop_uri.add(SH.datatype, prop["datatype"])
            if "message" in prop:
                prop_uri.add(SH.message, Literal(prop["message"]))
    
    def save(self) -> None:
        """Save the ontology to the specified path."""
        self.graph.serialize(destination=self.ontology_path, format="turtle")
    
    def validate(self) -> bool:
        """Validate the ontology structure."""
        # TODO: Implement SHACL validation
        return True 