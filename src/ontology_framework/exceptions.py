class ConcurrentModificationError(Exception):
    """Raised when a concurrent modification is detected."""
    pass

class ModelQualityError(Exception):
    """Raised when model quality checks fail."""
    pass

class ModelProjectionError(Exception):
    """Raised when model projection fails."""
    pass

class BoldoAPIError(Exception):
    """Raised when Boldo API operations fail."""
    pass 