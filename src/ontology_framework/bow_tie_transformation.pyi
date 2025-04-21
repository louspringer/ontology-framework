from typing import Optional, List, Set, Union
from rdflib import Graph, URIRef, Literal, Namespace, Node
from rdflib.namespace import RDFS, OWL

class BowTieTransformation:
    """Class for managing bow-tie transformations in ontologies."""
    
    def __init__(self, graph: Graph) -> None:
        """Initialize the BowTieTransformation.
        
        Args:
            graph: The RDF graph to transform
        """
        ...
    
    def transform(self) -> Graph:
        """Transform the ontology using the bow-tie pattern.
        
        Returns:
            The transformed RDF graph
        """
        ...
    
    def validate(self) -> bool:
        """Check if the graph follows the bow-tie pattern.
        
        Returns:
            True if the graph follows the bow-tie pattern, False otherwise
        """
        ...
    
    def validate_chain(self, chain_id: str) -> bool:
        """Validate a transformation chain.
        
        Args:
            chain_id: The ID of the chain to validate
            
        Returns:
            bool: True if chain is valid
        """
        ...
    
    def add_transformation(self, pattern: URIRef, lossiness: float) -> bool:
        """Add a transformation pattern.
        
        Args:
            pattern: The pattern URI
            lossiness: The lossiness level (0.0 to 1.0)
            
        Returns:
            bool: True if pattern was added successfully
        """
        ...
    
    def get_transformations(self) -> List[URIRef]:
        """Get all transformation patterns.
        
        Returns:
            List[URIRef]: List of transformation pattern URIs
        """
        ...
    
    def get_lossiness(self, pattern: URIRef) -> Optional[float]:
        """Get the lossiness level for a pattern.
        
        Args:
            pattern: The pattern URI
            
        Returns:
            Optional[float]: The lossiness level if found
        """
        ... 