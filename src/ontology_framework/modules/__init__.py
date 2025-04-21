"""
Modules package for the ontology framework.
"""

from rdflib import Namespace

# Define SHACL namespace
SHACL = Namespace('http://www.w3.org/ns/shacl#')

from .error_handling import (
    ErrorHandler,
    ValidationRule,
    ErrorResult,
    ErrorStep,
    ErrorSeverity,
    SecurityLevel,
    ComplianceLevel,
    RiskLevel,
    ValidationHandler,
    MetricsHandler,
    ComplianceHandler,
    RDFHandler
)
from .patch_management import (
    PatchManager,
    GraphDBPatchManager,
    PatchNotFoundError,
    PatchApplicationError
)
from .turtle_syntax import fix_turtle_syntax, validate_turtle, validate_shacl, load_and_fix_turtle
from .ontology_analyzer import OntologyAnalyzer
from .test_setup_manager import TestSetupManager
from .package_manager import PackageManager

__all__ = [
    'ErrorHandler',
    'ValidationRule',
    'ErrorResult',
    'ErrorStep',
    'ErrorSeverity',
    'SecurityLevel',
    'ComplianceLevel',
    'RiskLevel',
    'ValidationHandler',
    'MetricsHandler',
    'ComplianceHandler',
    'RDFHandler',
    'PatchManager',
    'GraphDBPatchManager',
    'PatchNotFoundError',
    'PatchApplicationError',
    'fix_turtle_syntax',
    'validate_turtle',
    'validate_shacl',
    'load_and_fix_turtle',
    'OntologyAnalyzer',
    'TestSetupManager',
    'PackageManager'
]

"""
Ontology Framework Modules
""" 