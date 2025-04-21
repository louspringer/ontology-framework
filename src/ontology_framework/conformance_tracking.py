"""
Module for tracking ontology conformance to guidance.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL

@dataclass
class ViolationDetails:
    """Details about a guidance violation."""
    rule_id: str
    severity: str
    message: str
    affected_elements: List[str]
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class ConformanceTracker:
    """Class for tracking ontology conformance to guidance."""
    
    def __init__(self, guidance_graph: Graph):
        """Initialize the tracker.
        
        Args:
            guidance_graph: The guidance ontology graph
        """
        self.guidance_graph = guidance_graph
        self.violations: Dict[str, List[ViolationDetails]] = {}
        
    def check_conformance(self, ontology_graph: Graph) -> List[ViolationDetails]:
        """Check an ontology's conformance to guidance.
        
        Args:
            ontology_graph: The ontology graph to check
            
        Returns:
            List of violations found
        """
        violations = []
        
        # Check class naming conventions
        violations.extend(self._check_class_naming(ontology_graph))
        
        # Check property naming conventions
        violations.extend(self._check_property_naming(ontology_graph))
        
        # Check documentation requirements
        violations.extend(self._check_documentation(ontology_graph))
        
        # Store violations
        timestamp = datetime.now().isoformat()
        self.violations[timestamp] = violations
        
        return violations
        
    def _check_class_naming(self, graph: Graph) -> List[ViolationDetails]:
        """Check class naming conventions.
        
        Args:
            graph: The ontology graph to check
            
        Returns:
            List of violations found
        """
        violations = []
        
        for cls in graph.subjects(RDF.type, OWL.Class):
            name = str(cls).split('#')[-1]
            
            # Classes should be in PascalCase
            if not name[0].isupper() or '_' in name:
                violations.append(ViolationDetails(
                    rule_id="CLASS_NAMING_001",
                    severity="ERROR",
                    message=f"Class name '{name}' should be in PascalCase",
                    affected_elements=[str(cls)]
                ))
                
        return violations
        
    def _check_property_naming(self, graph: Graph) -> List[ViolationDetails]:
        """Check property naming conventions.
        
        Args:
            graph: The ontology graph to check
            
        Returns:
            List of violations found
        """
        violations = []
        
        for prop in graph.subjects(RDF.type, OWL.ObjectProperty):
            name = str(prop).split('#')[-1]
            
            # Properties should be in camelCase
            if name[0].isupper() or '_' in name:
                violations.append(ViolationDetails(
                    rule_id="PROP_NAMING_001",
                    severity="ERROR",
                    message=f"Property name '{name}' should be in camelCase",
                    affected_elements=[str(prop)]
                ))
                
        return violations
        
    def _check_documentation(self, graph: Graph) -> List[ViolationDetails]:
        """Check documentation requirements.
        
        Args:
            graph: The ontology graph to check
            
        Returns:
            List of violations found
        """
        violations = []
        
        # Check classes have labels and comments
        for cls in graph.subjects(RDF.type, OWL.Class):
            if not any(graph.triples((cls, RDFS.label, None))):
                violations.append(ViolationDetails(
                    rule_id="DOC_001",
                    severity="ERROR",
                    message=f"Class {cls} is missing a label",
                    affected_elements=[str(cls)]
                ))
                
            if not any(graph.triples((cls, RDFS.comment, None))):
                violations.append(ViolationDetails(
                    rule_id="DOC_002",
                    severity="WARNING",
                    message=f"Class {cls} is missing a description",
                    affected_elements=[str(cls)]
                ))
                
        # Check properties have labels and comments
        for prop in graph.subjects(RDF.type, OWL.ObjectProperty):
            if not any(graph.triples((prop, RDFS.label, None))):
                violations.append(ViolationDetails(
                    rule_id="DOC_003",
                    severity="ERROR",
                    message=f"Property {prop} is missing a label",
                    affected_elements=[str(prop)]
                ))
                
            if not any(graph.triples((prop, RDFS.comment, None))):
                violations.append(ViolationDetails(
                    rule_id="DOC_004",
                    severity="WARNING",
                    message=f"Property {prop} is missing a description",
                    affected_elements=[str(prop)]
                ))
                
        return violations
        
    def get_violation_history(self) -> Dict[str, List[ViolationDetails]]:
        """Get the history of violations.
        
        Returns:
            Dictionary mapping timestamps to lists of violations
        """
        return self.violations
        
    def get_latest_violations(self) -> List[ViolationDetails]:
        """Get the most recent violations.
        
        Returns:
            List of most recent violations, or empty list if none
        """
        if not self.violations:
            return []
            
        latest_timestamp = max(self.violations.keys())
        return self.violations[latest_timestamp] 