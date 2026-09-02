from typing import Optional


class OpenApiError(Exception):
    """Obecná chyba při komunikaci se Škoda API."""
    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class OpenApiAuthenticationError(OpenApiError):
    """Error 401 - Invalid or Expired X-API-Key."""
    def __init__(self, message: str = "Invalid or expired X-API-Key.") -> None:
        super().__init__(message, status_code=401)


class OpenApiForbiddenError(OpenApiError):
    """Error 403 - Forbidden access to the requested resource."""
    def __init__(self, message: str = "Access to the requested resource is forbidden.") -> None:
        super().__init__(message, status_code=403)


class OpenApiVehicleNotFoundError(OpenApiError):
    """Error 404 - Vehicle with this VIN does not exist."""
    def __init__(self, message: str = "Vehicle with this VIN does not exist.") -> None:
        super().__init__(message, status_code=404)

class OpenApiUnsupportedError(OpenApiError):
    """Error 422 - Unsupported operation."""
    def __init__(self, message: str = "Vehicle does not support this operation") -> None:
        super().__init__(message, status_code=422)

class OpenApiRateLimitError(OpenApiError):
    """Error 429 - Rate limit exceeded or weak 12V battery."""
    def __init__(self, message: str = "Rate limit exceeded or weak 12V battery.") -> None:
        super().__init__(message, status_code=429)

class OpenApiServerError(OpenApiError):
    """Error 500 - Server error or timeout."""
    def __init__(self, message: str, status_code: int = 500) -> None:
        super().__init__(message, status_code=status_code)
