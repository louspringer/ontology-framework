from enum import Enum
from rdflib import Namespace

GUIDANCE = Namespace('https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#')

class ValidationRuleType(Enum):
    """Types of validation rules that can be applied to ontologies."""
    
    SHACL = GUIDANCE.SHACL
    """SHACL-based validation using shapes"""
    
    SEMANTIC = GUIDANCE.SEMANTIC
    """Semantic validation using SPARQL queries"""
    
    SYNTAX = GUIDANCE.SYNTAX
    """Syntax validation using patterns"""
    
    STRUCTURAL = GUIDANCE.STRUCTURAL
    """Structural validation rules"""
    
    SENSITIVE_DATA = GUIDANCE.SENSITIVE_DATA
    """Validation for sensitive data patterns"""
    
    @classmethod
    def from_string(cls, value: str) -> 'ValidationRuleType':
        """Convert a string to a ValidationRuleType.
        
        Args:
            value: String representation of the rule type
            
        Returns:
            Corresponding ValidationRuleType enum value
            
        Raises:
            ValueError: If the string doesn't match any rule type
        """
        try:
            return cls[value.upper()]
        except KeyError:
            raise ValueError(f"Invalid validation rule type: {value}") 