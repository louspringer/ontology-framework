"""
Ontology Framework for semantic web applications.
"""

__version__ = "0.1.0"

from .meta import MetaOntology, OntologyPatch
from .ontology_types import (
    PatchType, PatchStatus, ValidationRuleType, ErrorSeverity, 
    ErrorType, ErrorStep, ErrorResult, ValidationRule, RiskLevel, 
    ComplianceLevel, SecurityLevel, PerformanceMetric, ValidationResult, 
    ValidationError
)
from .metameta import MetaMetaOntology
from .exceptions import (
    OntologyFrameworkError,
    ValidationError,
    ConformanceError,
    ConcurrentModificationError,
    BoldoAPIError,
    AuthenticationError,
    APIRequestError,
    PatchNotFoundError,
    PatchApplicationError,
    ResourceNotFoundError
)
from .modules import (
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
    RDFHandler,
    PatchManager,
    GraphDBPatchManager,
    fix_turtle_syntax,
    validate_turtle,
    validate_shacl,
    load_and_fix_turtle,
    OntologyAnalyzer,
    TestSetupManager,
    PackageManager
)
from .deployment_modeler import DeploymentModeler
from .graphdb_client import GraphDBClient
from .sparql_operations import (
    QueryType, QueryResult, QueryExecutor, 
    GraphDBExecutor, Neo4jExecutor, execute_sparql, 
    SparqlOperations
)

# Expose the CLI main function
from .cli import cli as main

__all__ = [
    'MetaOntology' 'OntologyPatch',
    'PatchType',
    'PatchStatus',
    'MetaMetaOntology',
    'OntologyManager',
    'OntologyFrameworkError',
    'ValidationError',
    'ConformanceError',
    'ConcurrentModificationError',
    'BoldoAPIError',
    'AuthenticationError',
    'APIRequestError',
    'PatchNotFoundError',
    'PatchApplicationError',
    'ResourceNotFoundError',
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
    'fix_turtle_syntax',
    'validate_turtle',
    'validate_shacl',
    'load_and_fix_turtle',
    'OntologyAnalyzer',
    'TestSetupManager',
    'PackageManager',
    'DeploymentModeler',
    'GraphDBClient',
    'QueryType',
    'QueryResult',
    'QueryExecutor',
    'GraphDBExecutor',
    'Neo4jExecutor',
    'execute_sparql',
    'SparqlOperations',
    'ValidationRuleType',
    'ErrorType',
    'PerformanceMetric',
    'main'
] 