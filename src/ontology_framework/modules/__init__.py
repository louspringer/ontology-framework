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
from .turtle_syntax import (
    fix_turtle_syntax,
    validate_turtle,
    validate_shacl,
    load_and_fix_turtle
)
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

"""Module registry for the ontology framework."""

from typing import Dict, Type
from ontology_framework.modules.base import BaseModule
from ontology_framework.modules.validation import ValidationModule
from ontology_framework.modules.consistency import ConsistencyModule
from ontology_framework.modules.semantic import SemanticModule
from ontology_framework.modules.syntax import SyntaxModule

# Registry of available modules
MODULE_REGISTRY: Dict[str, Type[BaseModule]] = {
    "validation": ValidationModule,
    "consistency": ConsistencyModule,
    "semantic": SemanticModule,
    "syntax": SyntaxModule,
}

def get_module(module_name: str) -> Type[BaseModule]:
    """Get a module class by name."""
    if module_name not in MODULE_REGISTRY:
        raise ValueError(f"Module {module_name} not found in registry")
    return MODULE_REGISTRY[module_name]

def list_modules() -> list[str]:
    """List all available modules."""
    return list(MODULE_REGISTRY.keys()) 