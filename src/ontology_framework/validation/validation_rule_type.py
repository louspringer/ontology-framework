from enum import Enum

class ValidationRuleType(Enum):
    """Enum for different types of validation rules."""
    
    SHACL = "SHACL"
    SEMANTIC = "SEMANTIC"
    SYNTAX = "SYNTAX"
    PATTERN = "PATTERN"
    SENSITIVE_DATA = "SENSITIVE_DATA"
    INDIVIDUAL_TYPE = "INDIVIDUAL_TYPE"
    
    @classmethod
    def from_string(cls, value: str) -> "ValidationRuleType":
        """Convert a string to a ValidationRuleType.
        
        Args:
            value: String value to convert
            
        Returns:
            ValidationRuleType enum value
            
        Raises:
            ValueError: If string cannot be converted
        """
        try:
            return cls(value.upper())
        except (KeyError, ValueError):
            raise ValueError(f"Invalid validation rule type: {value}") 