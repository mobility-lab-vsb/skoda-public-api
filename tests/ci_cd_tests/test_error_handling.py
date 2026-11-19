"""The response (headers, body) of a failed request is attached to the raised error."""

import json
from typing import Any
from unittest.mock import MagicMock

import aiohttp
import pytest

from skoda_public_api.api_layer.const import TEST_BASE_URL
from skoda_public_api.api_layer.exceptions import (
    OpenApiAuthenticationError,
    OpenApiError,
    OpenApiForbiddenError,
    OpenApiRateLimitError,
    OpenApiServerError,
    OpenApiTimeoutError,
    OpenApiUnsupportedError,
    OpenApiVehicleNotFoundError,
)
from skoda_public_api.api_layer.open_api_client import OpenAPIClient
from skoda_public_api.api_layer.rest_api import SkodaRestAPI
from skoda_public_api.models.problem_details import ABOUT_BLANK_TYPE, ProblemDetails

VIN = "TMBJW0NZ8SC006012"
UNKNOWN_VIN = "TMBJW0NZ8SC999999"
TEST_HOST = "public.test-api.connect.skoda-auto.cz"
PREFIX = "https://public.api.connect.skoda-auto.cz/problems/"
VEHICLE_URL = f"/api/v1/vehicles/{VIN}"
UNKNOWN_VEHICLE_URL = f"/api/v1/vehicles/{UNKNOWN_VIN}"
START_URL = f"/api/v1/vehicles/{VIN}/charging/start"

QUOTA_HEADERS = {
    "Retry-After": "1834",
    "RateLimit-Limit": "20",
    "RateLimit-Remaining": "0",
    "RateLimit-Reset": "1834",
    "X-API-Key-Expires-At": "2026-12-31T23:00:00.000Z",
}

# Marks a body that is no problem object at all, unlike an unnamed problem.
NOT_A_PROBLEM = object()


def _problem_body(problem_type: str | None = None, **members: Any) -> str:
    """An ``application/problem+json`` body of one published problem type.

    On the wire there is only the ``type`` URI; the short name a client reads back
    is derived from its last segment. Without a type the body says ``about:blank``.
    """
    body: dict[str, Any] = {
        "type": ABOUT_BLANK_TYPE if problem_type is None else f"{PREFIX}{problem_type}",
        **{name: value for name, value in members.items() if value is not None},
    }
    return json.dumps(body)


def _serve(
    aresponses,
    method: str,
    path: str,
    status: int,
    body: Any = None,
    headers: dict[str, str] | None = None,
) -> None:
    """Answer one request with `status`, an optional problem+json body and headers."""
    payload: dict[str, Any] = {"headers": headers}
    if body is not None:
        payload["text"] = body if isinstance(body, str) else json.dumps(body)
        payload["content_type"] = "application/problem+json"
    aresponses.add(
        TEST_HOST, path, method, aresponses.Response(status=status, **payload)
    )


def _client(session: aiohttp.ClientSession) -> OpenAPIClient:
    return OpenAPIClient(api_key="fake", session=session, base_url=TEST_BASE_URL)


@pytest.mark.asyncio
async def test_rate_limit_error_carries_headers_and_problem(aresponses) -> None:
    """A 429 stores rate limit info (headers) and the problem details (type)."""
    _serve(
        aresponses,
        "GET",
        VEHICLE_URL,
        429,
        _problem_body(
            "rate-limit-exceeded",
            title="Too Many Requests",
            status=429,
            detail="Rate limit exceeded. Retry after 1834 seconds.",
            instance=VEHICLE_URL,
            correlationId="c-123",
        ),
        headers=QUOTA_HEADERS,
    )

    async with aiohttp.ClientSession() as session:
        client = _client(session)
        with pytest.raises(OpenApiRateLimitError) as quota:
            await client.get_vehicle(VIN)

    error = quota.value
    assert error.status_code == 429
    assert error.retry_after == error.rate_limit_reset == 1834
    assert error.rate_limit_remaining == 0
    assert error.api_key_expires_at == "2026-12-31T23:00:00.000Z"
    assert error.problem_type == "rate-limit-exceeded"
    assert error.problem_type_uri == f"{PREFIX}rate-limit-exceeded"
    assert error.detail == "Rate limit exceeded. Retry after 1834 seconds."
    assert error.problem is not None
    assert error.problem.title == "Too Many Requests"
    assert error.problem.status == 429
    assert error.problem.instance == VEHICLE_URL
    # A member this library does not know yet is kept, and so is the whole body.
    assert error.problem.model_extra == {"correlationId": "c-123"}
    assert error.body["detail"] == error.detail
    # ``client.last_headers`` keeps its success-path meaning; a failure is read
    # from the error instead.
    assert client.last_headers == {}
    assert client.rate_limit_remaining is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status", "problem_type", "error"),
    [
        (401, "api-key-expired", OpenApiAuthenticationError),
        (403, "api-key-not-authorized", OpenApiForbiddenError),
        (403, "operation-not-authorized", OpenApiForbiddenError),
        (422, "operation-not-supported", OpenApiUnsupportedError),
        (422, "operation-disabled", OpenApiUnsupportedError),
        (429, "rate-limit-exceeded", OpenApiRateLimitError),
        (429, "vehicle-not-accepting-requests", OpenApiRateLimitError),
        (500, None, OpenApiServerError),
        (503, None, OpenApiServerError),
        (504, "vehicle-did-not-respond", OpenApiServerError),  # published later on
        (409, None, OpenApiError),  # a status the specification does not define
    ],
)
async def test_every_error_carries_headers_and_problem(
    aresponses, status, problem_type, error
) -> None:
    """Whatever a status raises, the retry timing and the problem reach the caller."""
    detail = f"{problem_type or 'unnamed'} detail"
    _serve(
        aresponses,
        "POST",
        START_URL,
        status,
        _problem_body(problem_type, status=status, detail=detail),
        headers=QUOTA_HEADERS,
    )

    async with aiohttp.ClientSession() as session:
        with pytest.raises(error) as exc_info:
            await _client(session).start_charging(VIN)

    error = exc_info.value
    assert error.status_code == status
    assert error.retry_after == error.rate_limit_reset == 1834
    assert error.rate_limit_remaining == 0
    assert error.api_key_expires_at == "2026-12-31T23:00:00.000Z"
    assert error.problem.status == status
    # The readable name comes out of the type URI the response carried.
    assert error.problem_type_uri == (
        ABOUT_BLANK_TYPE if problem_type is None else f"{PREFIX}{problem_type}"
    )
    assert error.problem_type == problem_type
    assert error.detail == detail


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("body", "problem_type"),
    [
        ({"type": f"{PREFIX}operation-disabled"}, "operation-disabled"),
        # One RFC 9457 member is enough to be a problem, though an unnamed one.
        ({"detail": "d"}, None),
        (["unexpected"], NOT_A_PROBLEM),  # JSON, but no object to read members from
        ({"message": "proxy failure"}, NOT_A_PROBLEM),  # no RFC 9457 member at all
        # A member of the wrong type is no valid problem, but never masks the status.
        (
            {"type": f"{PREFIX}operation-disabled", "status": {"nested": 1}},
            NOT_A_PROBLEM,
        ),
    ],
)
async def test_only_a_problem_body_becomes_a_problem_object(
    aresponses, body, problem_type
) -> None:
    """What is not problem+json is lost as a problem but not from the error."""
    _serve(aresponses, "POST", START_URL, 409, body)

    async with aiohttp.ClientSession() as session:
        with pytest.raises(OpenApiError) as exc_info:
            await _client(session).start_charging(VIN)

    error = exc_info.value
    assert error.status_code == 409
    assert error.body == body
    if problem_type is NOT_A_PROBLEM:
        assert error.problem is None
        assert error.problem_type is None
    else:
        assert error.problem_type == problem_type


@pytest.mark.asyncio
async def test_error_without_documented_headers_or_body(aresponses) -> None:
    """A bare error response yields None everywhere instead of a crash."""
    _serve(aresponses, "GET", UNKNOWN_VEHICLE_URL, 404)

    async with aiohttp.ClientSession() as session:
        with pytest.raises(OpenApiVehicleNotFoundError) as exc_info:
            await _client(session).get_vehicle(UNKNOWN_VIN)

    error = exc_info.value
    assert error.retry_after is None
    assert error.rate_limit_remaining is None
    assert error.rate_limit_reset is None
    assert error.api_key_expires_at is None
    assert error.problem is None
    assert error.body is None


@pytest.mark.asyncio
async def test_non_numeric_retry_after_is_not_guessed(aresponses) -> None:
    """An HTTP-date Retry-After is no delay in seconds; only the raw header remains."""
    _serve(
        aresponses,
        "GET",
        VEHICLE_URL,
        429,
        headers={"Retry-After": "Wed, 21 Oct 2026 07:28:00 GMT"},
    )

    async with aiohttp.ClientSession() as session:
        with pytest.raises(OpenApiRateLimitError) as exc_info:
            await _client(session).get_vehicle(VIN)

    assert exc_info.value.retry_after is None
    assert exc_info.value.headers["retry-after"].startswith("Wed")


@pytest.mark.asyncio
async def test_timeout_error_carries_no_response() -> None:
    """A client-side timeout never saw a response, so there is nothing to attach."""
    session = MagicMock()
    session.get = MagicMock(side_effect=TimeoutError("timed out"))

    with pytest.raises(OpenApiTimeoutError) as exc_info:
        await SkodaRestAPI(api_key="fake", session=session)._make_get_request(
            VEHICLE_URL
        )

    assert exc_info.value.headers == {}
    assert exc_info.value.body is None
    assert exc_info.value.problem is None


def test_the_problem_name_is_read_from_the_type_uri() -> None:
    """Only the type is required, and ``about:blank`` names nothing."""
    unnamed = ProblemDetails.model_validate({"type": ABOUT_BLANK_TYPE})
    assert unnamed.slug is None
    assert unnamed.detail is None

    named = ProblemDetails.model_validate({"type": f"{PREFIX}operation-disabled"})
    assert named.slug == "operation-disabled"
