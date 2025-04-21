from typing import Dict, Any
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, XSD

class RDFHandler:
    """Class for handling RDF conversion and serialization."""
    
    def __init__(self) -> None:
        """Initialize RDF handler with required namespaces."""
        self.graph = Graph()
        self._bind_namespaces()
        
    def _bind_namespaces(self) -> None:
        """Bind all required namespaces to the graph."""
        ERROR = Namespace("http://example.org/error#")
        PROCESS = Namespace("http://example.org/process#")
        VALIDATION = Namespace("http://example.org/validation#")
        METRICS = Namespace("http://example.org/metrics#")
        MODEL = Namespace("http://example.org/model#")
        COMPLIANCE = Namespace("http://example.org/compliance#")
        
        self.graph.bind("error", ERROR)
        self.graph.bind("process", PROCESS)
        self.graph.bind("validation", VALIDATION)
        self.graph.bind("metrics", METRICS)
        self.graph.bind("model", MODEL)
        self.graph.bind("compliance", COMPLIANCE)
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("xsd", XSD)

    def add_error(self, error: Dict[str, Any]) -> None:
        """Add error information to RDF graph."""
        ERROR = Namespace("http://example.org/error#")
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

    def serialize(self, format: str = "turtle") -> str:
        """Serialize RDF graph to specified format."""
        return self.graph.serialize(format=format) 