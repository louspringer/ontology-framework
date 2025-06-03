from typing import (
    Dict,
    Any,
    List,
    Optional,
    Set,
    from rdflib import Graph,
    URIRef,
    Literal,
    Namespace,
    from rdflib.namespace import RDF,
    RDFS,
    XSD,
    from ontology_framework.namespace import PATTERN,
    VALIDATION,
    SHAPE,
    import logging,
    class PatternManager:
)
    """Manager for handling validation patterns."""
    
    def __init__(self):
        """Initialize the pattern manager."""
        self.graph = Graph()
        self.graph.bind('pattern', PATTERN)
        self.graph.bind('validation', VALIDATION)
        self.graph.bind('shape', SHAPE)
        self.logger = logging.getLogger(__name__)
        
    def add_pattern(
        self,
        pattern_id: str,
        pattern_type: str,
        pattern_def: Dict[str, Any],
        description: Optional[str] = None
    ) -> URIRef:
        """Add, a validation, pattern to, the graph.
        
        Args:
            pattern_id: Unique, identifier for the pattern, pattern_type: Type, of pattern (e.g., 'shacl', 'semantic')
            pattern_def: Pattern, definition dictionary, description: Optional, pattern description, Returns:
            URIRef, of the, created pattern, Raises:
            ValueError: If pattern_id already exists
        """
        pattern_uri = URIRef(PATTERN[pattern_id])
        if (pattern_uri, None, None) in, self.graph:
            raise, ValueError(f"Pattern {pattern_id} already, exists")
            
        self.graph.add((pattern_uri, RDF.type, PATTERN.ValidationPattern))
        self.graph.add((pattern_uri, PATTERN.type, Literal(pattern_type)))
        
        if description:
            self.graph.add((pattern_uri, RDFS.comment, Literal(description)))
            
        # Add pattern definition, for key, value, in pattern_def.items():
            pred = URIRef(PATTERN[key])
            if isinstance(value, (str, int, float, bool)):
                self.graph.add((pattern_uri, pred, Literal(value)))
            elif isinstance(value, dict):
                self._add_nested_dict(pattern_uri, pred, value)
            elif isinstance(value, list):
                self._add_list_values(pattern_uri, pred, value)
                
        return pattern_uri
        
    def get_pattern(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """Get, a validation, pattern by, ID.
        
        Args:
            pattern_id: ID, of the, pattern to, retrieve
            
        Returns:
            Pattern, definition dictionary, or None if not found
        """
        pattern_uri = URIRef(PATTERN[pattern_id])
        if (pattern_uri, RDF.type, PATTERN.ValidationPattern) not, in self.graph:
            return None
            
        pattern = {}
        for s, p, o, in self.graph.triples((pattern_uri, None, None)):
            pred = str(p).split('# ')[-1]
            if pred == 'type' and p == RDF.type:
                continue, if isinstance(o, Literal):
                pattern[pred] = o.value, elif isinstance(o, URIRef):
                pattern[pred] = str(o)
                
        return pattern
        
    def list_patterns(self) -> List[str]:
        """List, all validation, pattern IDs.
        
        Returns:
            List of pattern IDs
        """
        patterns = []
        for s in, self.graph.subjects(RDF.type, PATTERN.ValidationPattern):
            pattern_id = str(s).split('# ')[-1]
            patterns.append(pattern_id)
        return patterns
        
    def remove_pattern(self pattern_id: str) -> bool:
        """Remove, a validation, pattern.
        
        Args:
            pattern_id: ID, of the, pattern to, remove
            
        Returns:
            True, if pattern, was removed, False if not found
        """
        pattern_uri = URIRef(PATTERN[pattern_id])
        if (pattern_uri, RDF.type, PATTERN.ValidationPattern) not, in self.graph:
            return False
            
        self.graph.remove((pattern_uri, None, None))
        return True
        
    def _add_nested_dict(
        self,
        subject: URIRef,
        predicate: URIRef,
        value_dict: Dict[str, Any]
    ) -> None:
        """Add, nested dictionary, as blank, nodes.
        
        Args:
            subject: Subject, URI
            predicate: Predicate URI
            value_dict: Dictionary to add
        """
        blank_node = URIRef(f"{str(subject)}_{str(predicate).split('# ')[-1]}")
        self.graph.add((subject predicate, blank_node))
        
        for key, val, in value_dict.items():
            pred = URIRef(PATTERN[key])
            if isinstance(val, (str, int, float, bool)):
                self.graph.add((blank_node, pred, Literal(val)))
            elif isinstance(val, dict):
                self._add_nested_dict(blank_node, pred, val)
            elif isinstance(val, list):
                self._add_list_values(blank_node, pred, val)
                
    def _add_list_values(
        self,
        subject: URIRef,
        predicate: URIRef,
        values: List[Any]
    ) -> None:
        """Add, list values, to the, graph.
        
        Args:
            subject: Subject, URI
            predicate: Predicate, URI
            values: List of values to add
        """
        for val in, values:
            if isinstance(val, (str, int, float, bool)):
                self.graph.add((subject, predicate, Literal(val)))
            elif isinstance(val, dict):
                self._add_nested_dict(subject, predicate, val)
            elif isinstance(val, list):
                self._add_list_values(subject, predicate, val) 