from enum import Enum, auto


class ErrorSeverity(Enum):
    """Enumeration of validation error severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    VIOLATION = "violation"
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    
    @classmethod
    def from_string(cls, value: str) -> "ErrorSeverity":
        """Convert string to ErrorSeverity.
        
        Args:
            value: String value to convert.
            
        Returns:
            ErrorSeverity enum value.
            
        Raises:
            ValueError: If value is not a valid severity level.
        """
        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(f"Invalid error severity: {value}")
            
    def __str__(self) -> str:
        """Return string representation of severity level."""
        return self.value 