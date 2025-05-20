from typing import Union

class APIRequestError(BoldoAPIError):
    """Error raised when an API request fails."""
    def __init__(self, message: str, status_code: Union[int, None] = None):
        super().__init__(message)
        self.status_code = status_code 