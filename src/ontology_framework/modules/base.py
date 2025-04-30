"""Base module class for the ontology framework."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from rdflib import Graph

class BaseModule(ABC):
    """Base class for all ontology framework modules."""
    
    def __init__(self, graph: Optional[Graph] = None):
        """Initialize the module with an optional graph."""
        self.graph = graph
        
    @abstractmethod
    def validate(self, graph: Optional[Graph] = None) -> Dict[str, Any]:
        """Validate the graph according to the module's rules.
        
        Args:
            graph: Optional graph to validate. If None, uses the module's graph.
            
        Returns:
            Dictionary containing validation results.
        """
        pass
    
    @abstractmethod
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