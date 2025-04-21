from typing import Optional, List, Dict, Set, Union
from datetime import datetime
from rdflib import Graph, URIRef, Literal, Namespace, Node
from rdflib.namespace import RDFS, OWL

class ViolationDetails:
    """Details of a conformance violation."""
    
    def __init__(
        self,
        spore_id: URIRef,
        rule_id: URIRef,
        severity: str,
        message: str,
        timestamp: datetime
    ) -> None:
        """Initialize violation details.
        
        Args:
            spore_id: The spore that violated the rule
            rule_id: The rule that was violated
            severity: Severity level (ERROR, WARNING, INFO)
            message: Description of the violation
            timestamp: When the violation occurred
        """
        ...
    
    spore_id: URIRef
    rule_id: URIRef
    severity: str
    message: str
    timestamp: datetime

class ConformanceTracker:
    """Tracks conformance violations and validation results."""
    
    def __init__(
        self,
        ontology: Optional[Graph] = None,
        guidance_graph: Optional[Graph] = None
    ) -> None:
        """Initialize the ConformanceTracker.
        
        Args:
            ontology: The ontology graph to track
            guidance_graph: The guidance graph for validation
        """
        ...
    
    def add_violation(self, violation: ViolationDetails) -> None:
        """Add a violation to the tracker.
        
        Args:
            violation: The violation details
        """
        ...
    
    def get_violations(self) -> List[ViolationDetails]:
        """Get all tracked violations.
        
        Returns:
            List[ViolationDetails]: List of violations
        """
        ...
    
    def clear_violations(self) -> None:
        """Clear all tracked violations."""
        ...
    
    def validate_pattern_metadata(self, pattern: URIRef) -> bool:
        """Validate pattern metadata.
        
        Args:
            pattern: The pattern to validate
            
        Returns:
            bool: True if metadata is valid
        """
        ...
    
    def validate_pattern_guidance(self, pattern: URIRef) -> bool:
        """Validate pattern against guidance rules.
        
        Args:
            pattern: The pattern to validate
            
        Returns:
            bool: True if pattern conforms to guidance
        """
        ...
    
    def export_violations(self, file_path: str) -> None:
        """Export violations to a file.
        
        Args:
            file_path: Path to export file
        """
        ...
    
    def import_violations(self, file_path: str) -> None:
        """Import violations from a file.
        
        Args:
            file_path: Path to import file
        """
        ... 