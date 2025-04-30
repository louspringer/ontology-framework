from typing import Dict, List, Optional, Union
from rdflib import Graph, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, SH
from .validation_rule_type import ValidationRuleType
from .conformance_level import ConformanceLevel

class ValidationRule:
    """Represents a validation rule with its properties and validation logic."""
    
    def __init__(self, rule_id: str, rule_data: Dict):
        """Initialize a validation rule.
        
        Args:
            rule_id: Unique identifier for the rule
            rule_data: Dictionary containing rule properties
        """
        self.rule_id = rule_id
        self.rule_type = ValidationRuleType[rule_data.get('type', 'SEMANTIC')]
        self.message = rule_data.get('message', f'Validation failed for rule {rule_id}')
        self.priority = int(rule_data.get('priority', 999))
        self.conformance_level = ConformanceLevel[rule_data.get('conformance_level', 'STRICT')]
        self.dependencies = rule_data.get('dependencies', [])
        self.validator = rule_data.get('validator')
        self.pattern = rule_data.get('pattern')
        self.target_class = rule_data.get('target_class')
        self.target_property = rule_data.get('target_property')
        
    def validate(self, graph: Graph) -> Dict[str, Union[bool, List[str]]]:
        """Validate a graph against this rule.
        
        Args:
            graph: The RDF graph to validate
            
        Returns:
            Dictionary containing validation results and messages
        """
        results = {
            "valid": True,
            "messages": []
        }
        
        try:
            if self.rule_type == ValidationRuleType.SEMANTIC:
                # Semantic validation using SPARQL
                if self.validator:
                    query_results = graph.query(self.validator)
                    if len(query_results) > 0:
                        results["valid"] = False
                        results["messages"].append(self.message)
                        
            elif self.rule_type == ValidationRuleType.STRUCTURAL:
                # Structural validation using SHACL
                if self.pattern:
                    shape = self._create_shacl_shape()
                    conforms, _, _ = validate(
                        graph,
                        shacl_graph=shape,
                        inference='none',
                        abort_on_first=False
                    )
                    if not conforms:
                        results["valid"] = False
                        results["messages"].append(self.message)
                        
            elif self.rule_type == ValidationRuleType.PATTERN:
                # Pattern-based validation
                if self.pattern and self.target_property:
                    for s, p, o in graph.triples((None, URIRef(self.target_property), None)):
                        if not self._matches_pattern(str(o)):
                            results["valid"] = False
                            results["messages"].append(f"{self.message}: {str(o)}")
                            
            elif self.rule_type == ValidationRuleType.SENSITIVE_DATA:
                # Sensitive data validation
                if self.pattern:
                    for s, p, o in graph.triples((None, None, None)):
                        if isinstance(o, Literal) and self._matches_pattern(str(o)):
                            results["valid"] = False
                            results["messages"].append(f"Sensitive data detected: {str(o)}")
                            
        except Exception as e:
            results["valid"] = False
            results["messages"].append(f"Error validating rule {self.rule_id}: {str(e)}")
            
        return results
        
    def _create_shacl_shape(self) -> Graph:
        """Create a SHACL shape graph for this rule.
        
        Returns:
            RDF graph containing the SHACL shape
        """
        shape_graph = Graph()
        shape_graph.bind('sh', SH)
        
        shape = BNode()
        shape_graph.add((shape, RDF.type, SH.NodeShape))
        
        if self.target_class:
            shape_graph.add((shape, SH.targetClass, URIRef(self.target_class)))
            
        if self.target_property:
            property_shape = BNode()
            shape_graph.add((shape, SH.property, property_shape))
            shape_graph.add((property_shape, SH.path, URIRef(self.target_property)))
            
            if self.pattern:
                shape_graph.add((property_shape, SH.pattern, Literal(self.pattern)))
                
        return shape_graph
        
    def _matches_pattern(self, value: str) -> bool:
        """Check if a value matches the rule's pattern.
        
        Args:
            value: The value to check
            
        Returns:
            True if the value matches the pattern, False otherwise
        """
        if not self.pattern:
            return True
            
        try:
            import re
            return bool(re.match(self.pattern, value))
        except Exception:
            return False
            
    def __eq__(self, other):
        if not isinstance(other, ValidationRule):
            return False
        return self.rule_id == other.rule_id
        
    def __hash__(self):
        return hash(self.rule_id)
        
    def __str__(self):
        return f"ValidationRule({self.rule_id}, type={self.rule_type}, priority={self.priority})" 