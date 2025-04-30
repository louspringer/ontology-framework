"""
Common types and enums for the ontology framework.
"""

from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from enum import Enum, auto

class ValidationRuleType(str, Enum):
    """Validation rule types."""
    SHACL = "shacl"
    SEMANTIC = "semantic"
    SYNTAX = "syntax"
    SPORE = "spore"
    RISK = "risk"
    SECURITY = "security"
    INDIVIDUAL_TYPE = "individual_type"
    MATRIX = "matrix"
    COMPLIANCE = "compliance"
    PERFORMANCE = "performance"
    RELIABILITY = "reliability"
    AVAILABILITY = "availability"
    SCALABILITY = "scalability"
    MAINTAINABILITY = "maintainability"
    SEVERITY = "severity"
    STEP_ORDER = "step_order"
    BFG9K = "bfg9k"
    SENSITIVE_DATA = "sensitive_data"

class PatchType(Enum):
    """Types of patches that can be applied."""
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"
    SECURITY = "security"
    DEPENDENCY = "dependency"
    DOCUMENTATION = "documentation"
    TEST = "test"
    REFACTOR = "refactor"
    PERFORMANCE = "performance"
    FEATURE = "feature"
    BUGFIX = "bugfix"
    ENHANCEMENT = "enhancement"
    MAINTENANCE = "maintenance"
    COMPLIANCE = "compliance"
    SECURITY_PATCH = "security_patch"
    DEPENDENCY_UPDATE = "dependency_update"
    DOCUMENTATION_UPDATE = "documentation_update"
    TEST_UPDATE = "test_update"
    REFACTORING = "refactoring"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    FEATURE_ADDITION = "feature_addition"
    BUG_FIX = "bug_fix"
    ENHANCEMENT_UPDATE = "enhancement_update"
    MAINTENANCE_UPDATE = "maintenance_update"
    COMPLIANCE_UPDATE = "compliance_update"

class PatchStatus(Enum):
    """Status of a patch."""
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"
    MERGED = "merged"
    DEPLOYED = "deployed"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"
    UNBLOCKED = "unblocked"
    SCHEDULED = "scheduled"
    UNSCHEDULED = "unscheduled"
    PRIORITIZED = "prioritized"
    DEPRIORITIZED = "deprioritized"
    ARCHIVED = "archived"
    RESTORED = "restored"

class ErrorSeverity(Enum):
    """Enum for error severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    FATAL = "fatal"
    DEBUG = "debug"
    TRACE = "trace"
    NOTICE = "notice"
    ALERT = "alert"
    EMERGENCY = "emergency"

class ErrorType(Enum):
    """Types of errors that can occur."""
    VALIDATION = "Validation Error"
    RUNTIME = "runtime"
    CONFIGURATION = "configuration"
    NETWORK = "network"
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    MEMORY = "memory"
    CPU = "cpu"
    DISK = "disk"
    API = "api"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    COMPLIANCE = "compliance"
    MATRIX = "matrix"
    PERFORMANCE = "performance"
    SCALABILITY = "scalability"
    AVAILABILITY = "availability"
    RELIABILITY = "reliability"
    MAINTAINABILITY = "maintainability"
    DATA_LOSS = "data_loss"
    IO = "io"
    TEST = "test"

class ErrorStep(Enum):
    """Steps in the error handling process."""
    IDENTIFICATION = "identification"
    ANALYSIS = "analysis"
    RECOVERY = "recovery"
    PREVENTION = "prevention"
    SETUP = "setup"
    EXECUTION = "execution"
    VALIDATION = "validation"
    CLEANUP = "cleanup"
    MONITORING = "monitoring"
    REPORTING = "reporting"
    DOCUMENTATION = "documentation"
    REVIEW = "review"
    APPROVAL = "approval"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    VERIFICATION = "verification"
    CLOSURE = "closure"

class ErrorResult:
    """Class for representing error results."""
    def __init__(
        self,
        error_type: ErrorType,
        message: str,
        severity: ErrorSeverity,
        step: ErrorStep,
        timestamp: datetime = datetime.now(),
        details: Optional[Dict[str, Any]] = None,
        validation_details: Optional[Dict[str, Any]] = None,
        prevention_measures: Optional[Dict[str, bool]] = None,
        recovery_strategies: Optional[Dict[str, bool]] = None
    ):
        self.error_type = error_type
        self.message = message
        self.severity = severity
        self.step = step
        self.timestamp = timestamp
        self.details = details or {}
        self.validation_details = validation_details or {}
        self.prevention_measures = prevention_measures or {}
        self.recovery_strategies = recovery_strategies or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert the error result to a dictionary."""
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
        """Return a string representation of the error result."""
        return f"{self.error_type.value}: {self.message} (Severity: {self.severity.value}, Step: {self.step.value})"

class ValidationRule(Enum):
    """Types of validation rules."""
    RISK = "risk"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    PERFORMANCE = "performance"
    SENSITIVE_DATA = "sensitive_data"
    RELIABILITY = "reliability"
    AVAILABILITY = "availability"
    SCALABILITY = "scalability"
    MAINTAINABILITY = "maintainability"
    SEVERITY = "severity"
    STEP_ORDER = "step_order"
    SPORE = "spore"
    SEMANTIC = "semantic"
    SYNTAX = "syntax"
    MATRIX = "matrix"
    BFG9K = "bfg9k"

    @property
    def message(self) -> str:
        """Get the validation message for this rule."""
        messages = {
            ValidationRule.RISK: "Risk validation failed",
            ValidationRule.SECURITY: "Security validation failed",
            ValidationRule.COMPLIANCE: "Compliance validation failed",
            ValidationRule.PERFORMANCE: "Performance validation failed",
            ValidationRule.SENSITIVE_DATA: "Sensitive data validation failed",
            ValidationRule.RELIABILITY: "Reliability validation failed",
            ValidationRule.AVAILABILITY: "Availability validation failed",
            ValidationRule.SCALABILITY: "Scalability validation failed",
            ValidationRule.MAINTAINABILITY: "Maintainability validation failed",
            ValidationRule.SEVERITY: "Severity validation failed",
            ValidationRule.STEP_ORDER: "Step order validation failed",
            ValidationRule.SPORE: "SPORE validation failed",
            ValidationRule.SEMANTIC: "Semantic validation failed",
            ValidationRule.SYNTAX: "Syntax validation failed",
            ValidationRule.MATRIX: "Matrix validation failed",
            ValidationRule.BFG9K: "BFG9K pattern validation failed"
        }
        return messages.get(self, "Validation failed")

    @property
    def priority(self) -> str:
        """Get the priority level for this rule."""
        priorities = {
            ValidationRule.RISK: "HIGH",
            ValidationRule.SECURITY: "HIGH",
            ValidationRule.COMPLIANCE: "HIGH",
            ValidationRule.PERFORMANCE: "MEDIUM",
            ValidationRule.SENSITIVE_DATA: "HIGH",
            ValidationRule.RELIABILITY: "HIGH",
            ValidationRule.AVAILABILITY: "HIGH",
            ValidationRule.SCALABILITY: "MEDIUM",
            ValidationRule.MAINTAINABILITY: "MEDIUM",
            ValidationRule.SEVERITY: "HIGH",
            ValidationRule.STEP_ORDER: "HIGH",
            ValidationRule.SPORE: "HIGH",
            ValidationRule.SEMANTIC: "MEDIUM",
            ValidationRule.SYNTAX: "LOW",
            ValidationRule.MATRIX: "HIGH",
            ValidationRule.BFG9K: "HIGH"
        }
        return priorities.get(self, "MEDIUM")

    @property
    def target(self) -> str:
        """Get the target of this validation rule."""
        targets = {
            ValidationRule.RISK: "data",
            ValidationRule.SECURITY: "data",
            ValidationRule.COMPLIANCE: "data",
            ValidationRule.PERFORMANCE: "data",
            ValidationRule.SENSITIVE_DATA: "data",
            ValidationRule.RELIABILITY: "data",
            ValidationRule.AVAILABILITY: "data",
            ValidationRule.SCALABILITY: "data",
            ValidationRule.MAINTAINABILITY: "data",
            ValidationRule.SEVERITY: "data",
            ValidationRule.STEP_ORDER: "data",
            ValidationRule.SPORE: "data",
            ValidationRule.SEMANTIC: "data",
            ValidationRule.SYNTAX: "data",
            ValidationRule.MATRIX: "data",
            ValidationRule.BFG9K: "pattern"
        }
        return targets.get(self, "data")

    @property
    def validator(self) -> str:
        """Get the validator for this rule."""
        validators = {
            ValidationRule.RISK: "risk_validator",
            ValidationRule.SECURITY: "security_validator",
            ValidationRule.COMPLIANCE: "compliance_validator",
            ValidationRule.PERFORMANCE: "performance_validator",
            ValidationRule.SENSITIVE_DATA: "sensitive_data_validator",
            ValidationRule.RELIABILITY: "reliability_validator",
            ValidationRule.AVAILABILITY: "availability_validator",
            ValidationRule.SCALABILITY: "scalability_validator",
            ValidationRule.MAINTAINABILITY: "maintainability_validator",
            ValidationRule.SEVERITY: "severity_validator",
            ValidationRule.STEP_ORDER: "step_order_validator",
            ValidationRule.SPORE: "spore_validator",
            ValidationRule.SEMANTIC: "semantic_validator",
            ValidationRule.SYNTAX: "syntax_validator",
            ValidationRule.MATRIX: "matrix_validator",
            ValidationRule.BFG9K: "bfg9k_validator"
        }
        return validators.get(self, "unknown_validator")

class RiskLevel(Enum):
    """Levels of risk."""
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()

class ComplianceLevel(Enum):
    """Levels of compliance."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PARTIAL = "partial"
    FULL = "full"
    VERIFIED = "verified"
    CERTIFIED = "certified"
    UNKNOWN = "unknown"
    NON_COMPLIANT = "non_compliant"
    COMPLIANT = "compliant"
    EXEMPT = "exempt"
    WAIVED = "waived"
    PENDING = "pending"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CRITICAL = "critical"

class SecurityLevel(Enum):
    """Levels of security."""
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    RESTRICTED = auto()
    CONFIDENTIAL = auto()

class PerformanceMetric(Enum):
    """Types of performance metrics."""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    BANDWIDTH = "bandwidth"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    NETWORK_USAGE = "network_usage"
    ERROR_RATE = "error_rate"
    SUCCESS_RATE = "success_rate"
    AVAILABILITY = "availability"
    RELIABILITY = "reliability"
    SCALABILITY = "scalability"
    MAINTAINABILITY = "maintainability"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    COST = "cost"
    EFFICIENCY = "efficiency"
    EFFECTIVENESS = "effectiveness"
    QUALITY = "quality"
    SATISFACTION = "satisfaction"
    USABILITY = "usability"
    ACCESSIBILITY = "accessibility"
    INTEROPERABILITY = "interoperability"
    PORTABILITY = "portability"
    REUSABILITY = "reusability"
    TESTABILITY = "testability"
    UNDERSTANDABILITY = "understandability"
    MODIFIABILITY = "modifiability"
    ANALYZABILITY = "analyzability"
    STABILITY = "stability"
    CHANGEABILITY = "changeability" 

class ValidationResult:
    def __init__(
        self,
        rule: ValidationRule,
        result: bool,
        timestamp: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.rule = rule
        self.result = result
        self.timestamp = timestamp
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            'rule': self.rule,
            'result': self.result,
            'timestamp': self.timestamp,
            'details': self.details
        }

class ValidationError(Exception):
    def __init__(self, message: str, rule: ValidationRule, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.rule = rule
        self.details = details or {}