"""
Ontology Framework package initialization.
"""

from .patch_management import PatchManager
from .spore_integration import SporeIntegrator
from .conformance_tracking import ConformanceTracker
from .spore_validation import SporeValidator
from .bow_tie_transformation import BowTieTransformation
from .manage_models import ModelManager, ModelQualityError, ModelProjectionError
from .register_ontology import register_ontology, load_ontology
from .oracle_rdf import OracleRDFStore
from .meta import (
    META, PatchModel, PatchOperation, AddOperation, RemoveOperation,
    hasOperation, hasSubject, hasPredicate, hasObject, hasTargetSpore, createdAt,
    OntologyPatch, PatchType, PatchStatus
)
from .config import load_environment, get_api_token

# Load environment variables
load_environment()

__all__ = [
    'PatchManager',
    'SporeIntegrator',
    'ConformanceTracker',
    'SporeValidator',
    'BowTieTransformation',
    'ModelManager',
    'ModelQualityError',
    'ModelProjectionError',
    'register_ontology',
    'load_ontology',
    'OracleRDFStore',
    'META',
    'PatchModel',
    'PatchOperation',
    'AddOperation',
    'RemoveOperation',
    'hasOperation',
    'hasSubject',
    'hasPredicate',
    'hasObject',
    'hasTargetSpore',
    'createdAt',
    'get_api_token',
    'OntologyPatch',
    'PatchType',
    'PatchStatus'
]

"""Ontology Framework CLI package."""

__version__ = "0.1.0" 