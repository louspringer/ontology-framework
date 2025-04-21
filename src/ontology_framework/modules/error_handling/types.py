from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, List

class ValidationRuleType(Enum):
    """Enum for validation rule types."""
    SENSITIVE_DATA = "sensitive_data"
    RISK = "risk"
    MATRIX = "matrix"
    COMPLIANCE = "compliance"
    SECURITY = "security"
    PERFORMANCE = "performance"
    RELIABILITY = "reliability"
    AVAILABILITY = "availability"
    SCALABILITY = "scalability"
    MAINTAINABILITY = "maintainability"
    SEVERITY = "severity"
    STEP_ORDER = "step_order"

@dataclass
class ValidationRule:
    """Class for validation rules."""
    description: str
    severity: str
    message_template: str
    rule_type: ValidationRuleType
    version: str = "1.0.0"

@dataclass
class ErrorResult:
    """Class for error results."""
    error_type: str
    message: str
    severity: str
    timestamp: str

class ErrorType(Enum):
    """Enum for error types."""
    VALIDATION = "validation"
    SYNTAX = "syntax"
    SEMANTIC = "semantic"
    RUNTIME = "runtime"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    PERFORMANCE = "performance"
    INTEGRATION = "integration"
    CONFIGURATION = "configuration"
    DATA = "data"

class ErrorStep(Enum):
    """Enum for error handling steps."""
    INITIALIZATION = "initialization"
    VALIDATION = "validation"
    PREPROCESSING = "preprocessing"
    PROCESSING = "processing"
    POSTPROCESSING = "postprocessing"
    FINALIZATION = "finalization"
    ROLLBACK = "rollback"
    RECOVERY = "recovery"
    CLEANUP = "cleanup"
    LOGGING = "logging"
    NOTIFICATION = "notification"
    MONITORING = "monitoring"
    ANALYSIS = "analysis"
    REPORTING = "reporting"

class ErrorSeverity(Enum):
    """Enum for error severity levels."""
    CRITICAL = "critical"  # System crash, data loss
    SEVERE = "severe"     # Major functionality broken
    HIGH = "high"         # Important feature broken
    MEDIUM = "medium"     # Non-critical feature affected
    LOW = "low"          # Minor issue, cosmetic
    INFO = "info"        # Informational message
    DEBUG = "debug"      # Debug level message
    TRACE = "trace"      # Detailed tracing info

class SecurityLevel(Enum):
    """Enum for security levels."""
    CRITICAL = "critical"      # Severe security breach
    HIGH = "high"             # Potential data exposure
    MEDIUM = "medium"         # Security policy violation
    LOW = "low"              # Minor security concern
    CONFIDENTIAL = "confidential"  # Sensitive data handling
    RESTRICTED = "restricted"      # Limited access data
    INTERNAL = "internal"          # Internal use only
    PUBLIC = "public"              # Public information

class ComplianceLevel(Enum):
    """Enum for compliance levels."""
    CRITICAL = "critical"          # Severe compliance violation
    HIGH = "high"                 # Major compliance issue
    MEDIUM = "medium"             # Moderate compliance concern
    LOW = "low"                  # Minor compliance deviation
    REGULATORY = "regulatory"      # Regulatory requirement
    POLICY = "policy"             # Internal policy requirement
    STANDARD = "standard"         # Industry standard requirement
    GUIDELINE = "guideline"       # Best practice guideline
    OPTIONAL = "optional"         # Optional compliance measure

class RiskLevel(Enum):
    """Enum for risk levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical" 