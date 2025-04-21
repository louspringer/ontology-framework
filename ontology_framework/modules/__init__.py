"""
Ontology Framework modules package.
"""

from .error_handling import ErrorHandler, ErrorType, ValidationRule, ErrorResult
from .patch_management import PatchManager
from .turtle_syntax import fix_turtle_syntax, validate_turtle, validate_shacl, load_and_fix_turtle
from .ontology_analyzer import OntologyAnalyzer
from .create_error_ontology import create_error_ontology
from .update_error_ontology import update_error_ontology

__all__ = [
    'ErrorHandler',
    'ErrorType',
    'ValidationRule',
    'ErrorResult',
    'PatchManager',
    'fix_turtle_syntax',
    'validate_turtle',
    'validate_shacl',
    'load_and_fix_turtle',
    'OntologyAnalyzer',
    'create_error_ontology',
    'update_error_ontology'
] 