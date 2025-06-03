# Generated following ontology framework rules and ClaudeReflector constraints
# Ontology-Version: [current version from guidance.ttl]
# Behavioral-Profile: ClaudeReflector

from typing import Dict, Any
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, XSD

class RDFHandler:
    """Class for handling RDF operations in error handling."""
    
    def __init__(self) -> None:
        """Initialize RDF handler."""
        self.graph = Graph()
        self._setup_namespaces()
        
    def _setup_namespaces(self) -> None:
        """Set up common namespaces used in the RDF graph."""
        self.graph.bind("rdf", RDF)
        self.graph.bind("xsd", XSD)
        self.graph.bind("error", "http://example.org/error# ")

    def add_error(self, error: Dict[str, Any]) -> None:
        """Add error information to RDF graph."""
        ERROR = Namespace("http://example.org/error# ")
        error_id = URIRef(f"http://example.org/error/{error['type']}_{error['timestamp']}")
        
        self.graph.add((error_id, RDF.type, ERROR.Error))
        self.graph.add((error_id, ERROR.type, Literal(error['type'])))
        self.graph.add((error_id, ERROR.message, Literal(error['message'])))
        self.graph.add((error_id, ERROR.severity, Literal(error['severity'])))
        self.graph.add((error_id, ERROR.timestamp, Literal(error['timestamp'], datatype=XSD.dateTime)))
        
        if error.get('context'):
            self.graph.add((error_id, ERROR.context, Literal(error['context'])))
            
        if error.get('documentation'):
            self.graph.add((error_id, ERROR.documentation, Literal(error['documentation'])))
            
        # Add validation results if present
        if 'validation_results' in error:
            for result in error['validation_results']:
                result_id = URIRef(f"http://example.org/validation/{result['id']}")
                self.graph.add((result_id, RDF.type, ERROR.ValidationResult))
                self.graph.add((result_id, ERROR.result, Literal(result['result'])))
                self.graph.add((error_id, ERROR.hasValidationResult, result_id))

    def get_error_graph(self) -> Graph:
        """Get the RDF graph containing error information."""
        return self.graph

    def clear_graph(self) -> None:
        """Clear the RDF graph."""
        self.graph = Graph()
        self._setup_namespaces()

    def serialize(self, format: str = "turtle") -> str:
        """Serialize RDF graph to specified format."""
        return self.graph.serialize(format=format) 