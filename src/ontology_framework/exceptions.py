"""
Custom exceptions for the ontology framework.
"""

class OntologyFrameworkError(Exception):
    """Base exception for all ontology framework errors."""
    pass

class ValidationError(OntologyFrameworkError):
    """Raised when validation fails."""
    pass

class ConfigurationError(OntologyFrameworkError):
    """Raised when configuration is invalid."""
    pass

class DependencyError(OntologyFrameworkError):
    """Raised when a dependency is missing or invalid."""
    pass

class ReasonerError(OntologyFrameworkError):
    """Raised when reasoning fails."""
    pass

class ConformanceError(OntologyFrameworkError):
    """Raised when conformance checks fail."""
    pass

class ConcurrentModificationError(OntologyFrameworkError):
    """Raised when concurrent modifications are detected."""
    pass

class SporeIntegrationError(OntologyFrameworkError):
    """Raised when SPORE integration fails."""
    pass

class BoldoAPIError(OntologyFrameworkError):
    """Base exception for Boldo API errors."""
    pass

class AuthenticationError(BoldoAPIError):
    """Exception raised when authentication fails."""
    pass

class APIRequestError(BoldoAPIError):
    """Exception raised when an API request fails."""
    def __init__(self, message: str, status_code: int | None = None):
        self.status_code = status_code
        super().__init__(message)

class PatchNotFoundError(OntologyFrameworkError):
    """Raised when a patch cannot be found."""
    pass

class PatchApplicationError(OntologyFrameworkError):
    """Raised when a patch cannot be applied."""
    pass

class ResourceNotFoundError(BoldoAPIError):
    """Exception raised when a requested resource is not found."""
    pass

class ModelQualityError(OntologyFrameworkError):
    """Exception raised when model quality checks fail."""
    pass

class ModelProjectionError(OntologyFrameworkError):
    """Exception raised when model projection operations fail."""
    pass

class RegistrationError(OntologyFrameworkError):
    """Exception raised when ontology registration fails."""
    pass

class GuidanceError(OntologyFrameworkError):
    """Exception raised when guidance operations fail."""
    pass

class GraphDBError(OntologyFrameworkError):
    """Exception raised when GraphDB operations fail."""
    pass

class GitHubError(OntologyFrameworkError):
    """Exception raised when GitHub operations fail."""
    pass

__all__ = [
    'OntologyFrameworkError',
    'ValidationError',
    'ConfigurationError',
    'DependencyError',
    'ReasonerError',
    'ConformanceError',
    'ConcurrentModificationError',
    'SporeIntegrationError',
    'BoldoAPIError',
    'AuthenticationError',
    'APIRequestError',
    'PatchNotFoundError',
    'PatchApplicationError',
    'ResourceNotFoundError',
    'ModelQualityError',
    'ModelProjectionError',
    'RegistrationError',
    'GuidanceError',
    'GraphDBError',
    'GitHubError'
] 