from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Any, List, Optional, Union

class ValidationRuleType(Enum):
    """Validation rule types."""
    MATRIX = "matrix"
    ONTOLOGY = "ontology"
    PATTERN = "pattern"
    COMPLIANCE = "compliance"
    PERFORMANCE = "performance"
    SENSITIVE_DATA = "sensitive_data"
    RISK = "risk"
    SECURITY = "security"
    RELIABILITY = "reliability"
    AVAILABILITY = "availability"
    SCALABILITY = "scalability"
    MAINTAINABILITY = "maintainability"
    SEVERITY = "severity"
    STEP_ORDER = "step_order"
    ACCESS_CONTROL = "access_control"
    ENCRYPTION = "encryption"
    SPORE = "spore"
    SEMANTIC = "semantic"
    SYNTAX = "syntax"
    INDIVIDUAL_TYPE = "individual_type"
    BFG9K = "bfg9k"

@dataclass
class ValidationRule:
    """Class for validation rules."""
    description: str
    severity: str
    message_template: str
    rule_type: ValidationRuleType
    version: str = "1.0.0"
    conformance_level: str = "STRICT"

@dataclass
class ErrorResult:
    """Class for error results."""
    error_type: str
    message: str
    severity: str
    timestamp: str
    validation_details: Optional[Dict[str, Any]] = None

class ErrorType(Enum):
    """Error types."""
    RUNTIME = "runtime"
    MATRIX = "matrix"
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    COMPLIANCE = "compliance"
    PERFORMANCE = "performance"
    SYNTAX = "syntax"
    SEMANTIC = "semantic"
    INTEGRATION = "integration"
    CONFIGURATION = "configuration"
    DATA = "data"
    NETWORK = "network"
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    MEMORY = "memory"
    CPU = "cpu"
    DISK = "disk"
    API = "api"
    DATA_LOSS = "data_loss"
    PATTERN_MISMATCH = "pattern_mismatch"
    ONTOLOGY_ERROR = "ontology_error"
    SHACL_VALIDATION = "shacl_validation"

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
    IDENTIFICATION = "identification"
    PREVENTION = "prevention"
    BFG9K_VALIDATION = "bfg9k_validation"
    PATTERN_VALIDATION = "pattern_validation"
    SEMANTIC_VALIDATION = "semantic_validation"
    SYNTAX_VALIDATION = "syntax_validation"

class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    INFO = "info"
    DEBUG = "debug"
    TRACE = "trace"

class SecurityLevel(Enum):
    """Security levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    INTERNAL = "internal"
    PUBLIC = "public"

class ComplianceLevel(Enum):
    """Compliance levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    REGULATORY = "regulatory"
    POLICY = "policy"
    STANDARD = "standard"
    OPTIONAL = "optional"

class RiskLevel(Enum):
    """Risk levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    NONE = "none" 