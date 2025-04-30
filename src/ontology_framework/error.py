from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime
from .ontology_types import ErrorType, ErrorSeverity, ErrorStep

@dataclass
class Error:
    """Class for representing errors in the ontology framework."""
    error_type: ErrorType
    message: str
    severity: ErrorSeverity
    step: ErrorStep
    timestamp: datetime = datetime.now()
    details: Optional[Dict[str, Any]] = None
    validation_details: Optional[Dict[str, Any]] = None
    prevention_measures: Optional[Dict[str, bool]] = None
    recovery_strategies: Optional[Dict[str, bool]] = None

    def __post_init__(self):
        """Initialize optional fields if they are None."""
        if self.details is None:
            self.details = {}
        if self.validation_details is None:
            self.validation_details = {}
        if self.prevention_measures is None:
            self.prevention_measures = {}
        if self.recovery_strategies is None:
            self.recovery_strategies = {}

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