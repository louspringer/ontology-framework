from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL
from pathlib import Path
from typing import Optional, Union
import logging

class OntologyManager:
    """Manages ontology operations using RDFlib for safe handling of Turtle files."""
    
    def __init__(self, base_uri: str = "http://example.org/ontology#"):
        self.graph = Graph()
        self.ns = Namespace(base_uri)
        self.graph.bind("onto", self.ns)
        self.graph.bind("owl", OWL)
        self.graph.bind("rdfs", RDFS)
        
    def load_ontology(self, file_path: Path) -> None:
        """Load an existing ontology file."""
        try:
            self.graph.parse(str(file_path), format="turtle")
            logging.info(f"Successfully loaded ontology from {file_path}")
        except Exception as e:
            logging.error(f"Failed to load ontology: {e}")
            raise
            
    def save_ontology(self, file_path: Path) -> None:
        """Save the ontology to a file in Turtle format."""
        try:
            self.graph.serialize(destination=str(file_path), format="turtle")
            logging.info(f"Successfully saved ontology to {file_path}")
        except Exception as e:
            logging.error(f"Failed to save ontology: {e}")
            raise
            
    def execute_sparql_query(self, query: str) -> Union[list, bool]:
        """Execute a SPARQL query on the ontology.
        
        Args:
            query: The SPARQL query string to execute.
            
        Returns:
            For SELECT queries: A list of query results.
            For ASK queries: A boolean indicating the query result.
            
        Raises:
            Exception: If the query execution fails.
        """
        try:
            results = self.graph.query(query)
            # Handle ASK queries by checking the query type
            if hasattr(results, 'type') and results.type == 'ASK':
                return bool(results.askAnswer)
            return list(results)
        except Exception as e:
            logging.error(f"SPARQL query failed: {e}")
            raise
            
    def add_class(self, class_name: str, label: str, comment: Optional[str] = None) -> URIRef:
        """Add a new class to the ontology with label and optional comment."""
        class_uri = self.ns[class_name]
        self.graph.add((class_uri, RDF.type, OWL.Class))
        self.graph.add((class_uri, RDFS.label, Literal(label)))
        if comment:
            self.graph.add((class_uri, RDFS.comment, Literal(comment)))
        return class_uri
        
    def add_property(self, prop_name: str, domain: URIRef, range_: URIRef, 
                    label: str, comment: Optional[str] = None) -> URIRef:
        """Add a new property to the ontology."""
        prop_uri = self.ns[prop_name]
        self.graph.add((prop_uri, RDF.type, OWL.ObjectProperty))
        self.graph.add((prop_uri, RDFS.domain, domain))
        self.graph.add((prop_uri, RDFS.range, range_))
        self.graph.add((prop_uri, RDFS.label, Literal(label)))
        if comment:
            self.graph.add((prop_uri, RDFS.comment, Literal(comment)))
        return prop_uri 