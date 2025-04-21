from typing import Dict, Any
from enum import Enum

class ValidationRule: ...
class ErrorResult: ...

class ErrorStep(Enum):
    IDENTIFICATION = "identification"
    ANALYSIS = "analysis"
    RECOVERY = "recovery"
    PREVENTION = "prevention"
    MONITORING = "monitoring"
    REPORTING = "reporting"
    DOCUMENTATION = "documentation"
    REVIEW = "review"
    CLOSURE = "closure"

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SecurityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ComplianceLevel(Enum):
    NOT_STARTED = "not_started"
    PARTIAL = "partial"
    FULL = "full"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
