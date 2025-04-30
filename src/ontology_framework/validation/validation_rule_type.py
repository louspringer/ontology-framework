from enum import Enum

class ValidationRuleType(Enum):
    """Types of validation rules that can be applied to ontologies."""
    
    SEMANTIC = "SEMANTIC"
    """Semantic validation using SPARQL queries"""
    
    STRUCTURAL = "STRUCTURAL"
    """Structural validation using SHACL shapes"""
    
    PATTERN = "PATTERN"
    """Pattern-based validation using regular expressions"""
    
    SENSITIVE_DATA = "SENSITIVE_DATA"
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