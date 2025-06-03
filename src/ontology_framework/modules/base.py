# Generated following ontology framework rules and ClaudeReflector constraints
# Ontology-Version: [current version from guidance.ttl]
# Behavioral-Profile: ClaudeReflector

"""Base module for ontology framework."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from rdflib import Graph

class BaseModule(ABC):
    """Base class for ontology framework modules."""
    
    def __init__(self, graph: Optional[Graph] = None) -> None:
        """Initialize the base module.
        
        Args:
            graph: Optional RDF graph to use
        """
        self.graph = graph or Graph()
        
    @abstractmethod
    def validate(self) -> Dict[str, Any]:
        """Validate the module's state.
        
        Returns:
            Dictionary containing validation results
        """
        pass
        
    @abstractmethod
    def load(self) -> None:
        """Load module data."""
        pass
        
    @abstractmethod
    def save(self) -> None:
        """Save module data."""
        pass

    def get_requirements(self) -> Dict[str, Any]:
        """Get the module's requirements.
        
        Returns:
            Dictionary containing the module's requirements.
        """
        pass

    def set_graph(self, graph: Graph) -> None:
        """Set the graph for this module.
        
        Args:
            graph: The graph to set.
        """
        self.graph = graph 