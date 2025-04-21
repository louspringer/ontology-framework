"""Base ontology functionality."""

from pathlib import Path
from typing import Union, Optional
from rdflib import Graph, RDF, RDFS, OWL, URIRef, Literal, Namespace

class BaseOntology:
    """Base ontology class.
    
    This class provides common functionality for ontology operations.
    """
    
    def __init__(self, base_uri: str) -> None:
        """Initialize the ontology.
        
        Args:
            base_uri: Base URI for the ontology.
        """
        self.base_uri = base_uri
        self.base = Namespace(base_uri)
        self.graph = Graph()
        
        # Bind common prefixes
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("owl", OWL)
        self.graph.bind("", self.base)
        
    def load(self, file_path: Union[str, Path]) -> None:
        """Load an ontology from a file.
        
        Args:
            file_path: Path to the ontology file.
        """
        self.graph.parse(file_path, format="turtle")
        
    def save(self, file_path: Union[str, Path]) -> None:
        """Save the ontology to a file.
        
        Args:
            file_path: Path to save the ontology to.
        """
        self.graph.serialize(file_path, format="turtle")
        
    def query(self, query: str) -> list:
        """Execute a SPARQL query on the ontology.
        
        Args:
            query: SPARQL query string.
            
        Returns:
            List of query results.
        """
        return list(self.graph.query(query))
        
    def to_python(self, value: URIRef) -> Union[str, int, float, bool, None]:
        """Convert an RDF value to a Python type.
        
        Args:
            value: RDF value to convert.
            
        Returns:
            Python value.
        """
        if isinstance(value, Literal):
            return value.toPython()
        return str(value)
        
    def to_rdf(self, value: Union[str, int, float, bool, None]) -> Union[URIRef, Literal]:
        """Convert a Python value to an RDF type.
        
        Args:
            value: Python value to convert.
            
        Returns:
            RDF value.
        """
        if isinstance(value, (int, float, bool)):
            return Literal(value)
        elif value is None:
            return Literal("")
        return Literal(str(value)) 