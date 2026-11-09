from collections.abc import Mapping
from typing import Any

from pydantic import ValidationError

from ..models.problem_details import ProblemDetails


def _header_int_value(headers: Mapping[str, str], name: str) -> int | None:
    """Return the integer value of a response header, or None if absent or not a number."""
    value = headers.get(name)
    if value is None:
        return None
    value = value.strip()
    return int(value) if value.isdigit() else None


#: Members that identify a body as a problem object (RFC 9457).
_PROBLEM_MEMBERS = ("type", "title", "status", "detail", "instance")


def _parse_problem(body: Any) -> ProblemDetails | None:
    """Read the problem details out of an error response body, if it carries any.

    A body only counts as a problem when it holds at least one of the RFC 9457
    members, so an unrelated JSON object is not mistaken for an empty problem.
    Never raises: an unreadable body must not mask the HTTP error it belongs to,
    and is still available as ``error.body``.
    """
    if not isinstance(body, dict) or not (_PROBLEM_MEMBERS & body.keys()):
        return None
    try:
        return ProblemDetails.model_validate(body)
    except ValidationError:
        return None


class OpenApiError(Exception):
    """General error when communicating with the Škoda API.

    When the API answered, the response is attached to the error:

    * ``headers``: the response headers, with lower-case names.
    * ``body``: the parsed ``application/problem+json`` object, or the raw text
      when the body was not JSON. ``None`` when there was no body.
    * ``problem``: the same body as :class:`ProblemDetails`, or ``None`` when it
      was absent or not a JSON object.

    All of them are empty for errors that never saw a response, such as
    :class:`OpenApiTimeoutError`.
    """

    default_message: str = "Error when communicating with the Škoda API."
    default_status_code: int | None = None

    def __init__(
        self,
        message: str | None = None,
        status_code: int | None = None,
        headers: Mapping[str, str] | None = None,
        body: Any = None,
    ) -> None:
        super().__init__(message if message is not None else self.default_message)
        self.status_code = (
            status_code if status_code is not None else self.default_status_code
        )
        # Header names are normalised so callers do not depend on how the server
        # or any proxy in between capitalised them.
        self.headers: Mapping[str, str] = {
            key.lower(): value for key, value in (headers or {}).items()
        }
        self.body: Any = body
        self.problem: ProblemDetails | None = _parse_problem(body)

    @property
    def retry_after(self) -> int | None:
        """Seconds from the ``Retry-After`` response header, if it held a number."""
        return _header_int_value(self.headers, "retry-after")

    @property
    def rate_limit_remaining(self) -> int | None:
        """Requests left in the current window, from ``RateLimit-Remaining``."""
        return _header_int_value(self.headers, "ratelimit-remaining")

    @property
    def rate_limit_reset(self) -> int | None:
        """Seconds until the quota window resets, from ``RateLimit-Reset``."""
        return _header_int_value(self.headers, "ratelimit-reset")

    @property
    def api_key_expires_at(self) -> str | None:
        """Expiration timestamp of the API key, from ``X-API-Key-Expires-At``."""
        return self.headers.get("x-api-key-expires-at")

    @property
    def problem_type(self) -> str | None:
        """Problem name from the type URI, e.g. ``rate-limit-exceeded``.

        ``None`` when the response carried no problem object or only the
        ``about:blank`` type, which says nothing beyond the status code.
        """
        return self.problem.slug if self.problem else None

    @property
    def problem_type_uri(self) -> str | None:
        """Full problem type URI, which doubles as a link to its documentation."""
        return self.problem.type if self.problem else None

    @property
    def detail(self) -> str | None:
        """Human-readable ``detail`` member of the problem, if the API sent one."""
        return self.problem.detail if self.problem else None


class OpenApiAuthenticationError(OpenApiError):
    """Error 401 - Invalid or Expired X-API-Key."""

    default_message = "Invalid or expired X-API-Key."
    default_status_code = 401


class OpenApiForbiddenError(OpenApiError):
    """Error 403 - the key or the user is not allowed to execute the operation.

    The API distinguishes ``api-key-not-authorized`` from ``operation-not-authorized``;
    read ``problem_type`` to tell them apart.
    """

    default_message = "Access forbidden. User not allowed to execute operation."
    default_status_code = 403


class OpenApiVehicleNotFoundError(OpenApiError):
    """Error 404 - Vehicle with this VIN does not exist."""

    default_message = "Vehicle with this VIN does not exist."
    default_status_code = 404


class OpenApiUnsupportedError(OpenApiError):
    """Error 422 - Unsupported operation."""

    default_message = "Vehicle does not support this operation"
    default_status_code = 422


class OpenApiRateLimitError(OpenApiError):
    """Error 429 - Rate limit exceeded, or the vehicle declined the operation.

    Both conditions share the status code; tell them apart by ``problem_type``
    (``rate-limit-exceeded`` for the key quota, ``vehicle-not-accepting-requests``
    when the vehicle itself declined).
    """

    default_message = "Rate limit exceeded or insufficient battery level."
    default_status_code = 429


class OpenApiServerError(OpenApiError):
    """Error 500 - Server error or timeout."""

    default_message = "An unexpected error occurred while processing the request."
    default_status_code = 500


class OpenApiTimeoutError(OpenApiError):
    """The request did not complete before the client-side timeout elapsed."""

    default_message = "The request to the Škoda API timed out."


class OpenApiResponseValidationError(OpenApiError):
    """The API response could not be parsed into the expected model."""

    default_message = "The API response could not be parsed into the expected model."
