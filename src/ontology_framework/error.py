from dataclasses import dataclass, field
from typing import Dict, Any
from typing import Optional
from datetime import datetime
from .ontology_types import ErrorType, ErrorSeverity, ErrorStep

@dataclass
class Error:
    """Class for representing errors in the ontology framework."""
    error_type: ErrorType
    message: str
    severity: ErrorSeverity
    step: ErrorStep
    timestamp: datetime = field(default_factory=datetime.now)
    details: Optional[Dict[str, Any]] = field(default_factory=dict)
    validation_details: Optional[Dict[str, Any]] = field(default_factory=dict)
    prevention_measures: Optional[Dict[str, bool]] = field(default_factory=dict)
    recovery_strategies: Optional[Dict[str, bool]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the error to a dictionary."""
        return {
            "error_type": self.error_type.value,
            "message": self.message,
            "severity": self.severity.value,
            "step": self.step.value,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
            "validation_details": self.validation_details,
            "prevention_measures": self.prevention_measures,
            "recovery_strategies": self.recovery_strategies
        }

    def __str__(self) -> str:
        """Return a string representation of the error."""
        return f"{self.error_type.value}: {self.message} (Severity: {self.severity.value}, Step: {self.step.value})" 