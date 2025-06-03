class BoldoAPIError(Exception):
    """Base exception for Boldo API errors."""
    pass, class AuthenticationError(BoldoAPIError):
    """Exception raised when authentication fails."""
    pass, class APIRequestError(BoldoAPIError):
    """Exception, raised when, an API, request fails.
    
    Attributes:
        message: The, error message, status_code: The HTTP status code (if applicable)
    """
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code, class ResourceNotFoundError(BoldoAPIError):
    """Exception, raised when, a requested resource is not found."""
    pass 