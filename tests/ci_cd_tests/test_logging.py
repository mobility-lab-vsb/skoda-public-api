"""Every response is logged at debug level with its rate limit headers, VIN masked."""

import logging

import aiohttp
import pytest

from skoda_public_api.api_layer.const import TEST_BASE_URL
from skoda_public_api.api_layer.exceptions import (
    OpenApiAuthenticationError,
    OpenApiRateLimitError,
)
from skoda_public_api.api_layer.open_api_client import OpenAPIClient

VIN = "TMBJW0NZ8SC006012"
TEST_HOST = "public.test-api.connect.skoda-auto.cz"
LOGGER = "skoda_public_api.api_layer.rest_api"

QUOTA_HEADERS = {
    "RateLimit-Limit": "20",
    "RateLimit-Remaining": "17",
    "RateLimit-Reset": "1834",
}


def _client(session: aiohttp.ClientSession) -> OpenAPIClient:
    return OpenAPIClient(api_key="fake", session=session, base_url=TEST_BASE_URL)


def _messages(caplog: pytest.LogCaptureFixture) -> list[str]:
    """Messages of this library only; the test server logs the full request path."""
    return [record.getMessage() for record in caplog.records if record.name == LOGGER]


@pytest.mark.asyncio
async def test_get_response_is_logged(aresponses, caplog) -> None:
    """A poll logs its path with the query, status and the rate limit headers."""
    aresponses.add(
        TEST_HOST,
        f"/api/v1/vehicles/{VIN}",
        "GET",
        aresponses.Response(
            text=f'{{"vehicle": {{"vin": "{VIN}"}}}}',
            content_type="application/json",
            headers=QUOTA_HEADERS,
        ),
    )
    caplog.set_level(logging.DEBUG, logger=LOGGER)

    async with aiohttp.ClientSession() as session:
        await _client(session).get_charging(VIN)

    assert (
        "GET /api/v1/vehicles/***6012?include=charging -> 200 "
        "(RateLimit-Remaining: 17/20, RateLimit-Reset: 1834)"
    ) in _messages(caplog)
    assert not any(VIN in message for message in _messages(caplog))


@pytest.mark.asyncio
async def test_failed_command_is_logged(aresponses, caplog) -> None:
    """A rejected command is logged before the error is raised."""
    aresponses.add(
        TEST_HOST,
        f"/api/v1/vehicles/{VIN}/charging/start",
        "POST",
        aresponses.Response(
            status=429, headers={**QUOTA_HEADERS, "RateLimit-Remaining": "0"}
        ),
    )
    caplog.set_level(logging.DEBUG, logger=LOGGER)

    async with aiohttp.ClientSession() as session:
        with pytest.raises(OpenApiRateLimitError):
            await _client(session).start_charging(VIN)

    assert (
        "POST /api/v1/vehicles/***6012/charging/start -> 429 "
        "(RateLimit-Remaining: 0/20, RateLimit-Reset: 1834)"
    ) in _messages(caplog)
    assert not any(VIN in message for message in _messages(caplog))


@pytest.mark.asyncio
async def test_response_without_rate_limit_headers(aresponses, caplog) -> None:
    """A rejected key gets no quota headers, so the line leaves them out."""
    aresponses.add(
        TEST_HOST,
        f"/api/v1/vehicles/{VIN}",
        "GET",
        aresponses.Response(status=401),
    )
    caplog.set_level(logging.DEBUG, logger=LOGGER)

    async with aiohttp.ClientSession() as session:
        with pytest.raises(OpenApiAuthenticationError):
            await _client(session).get_vehicle(VIN)

    assert "GET /api/v1/vehicles/***6012 -> 401" in _messages(caplog)


@pytest.mark.asyncio
async def test_partial_rate_limit_headers(aresponses, caplog) -> None:
    """When only some quota headers arrive, the missing ones show as None."""
    aresponses.add(
        TEST_HOST,
        f"/api/v1/vehicles/{VIN}/charging/stop",
        "POST",
        aresponses.Response(status=202, headers={"RateLimit-Remaining": "5"}),
    )
    caplog.set_level(logging.DEBUG, logger=LOGGER)

    async with aiohttp.ClientSession() as session:
        await _client(session).stop_charging(VIN)

    assert (
        "POST /api/v1/vehicles/***6012/charging/stop -> 202 "
        "(RateLimit-Remaining: 5/None, RateLimit-Reset: None)"
    ) in _messages(caplog)
