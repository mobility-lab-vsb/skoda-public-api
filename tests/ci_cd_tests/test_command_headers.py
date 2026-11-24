"""Commands return their response headers and update the client's rate limit info."""

import aiohttp
import pytest

from skoda_public_api.api_layer.const import TEST_BASE_URL
from skoda_public_api.api_layer.exceptions import OpenApiRateLimitError
from skoda_public_api.api_layer.open_api_client import OpenAPIClient

VIN = "TMBJW0NZ8SC006012"
TEST_HOST = "public.test-api.connect.skoda-auto.cz"

QUOTA_HEADERS = {
    "RateLimit-Limit": "20",
    "RateLimit-Remaining": "11",
    "RateLimit-Reset": "2248",
}


def _client(session: aiohttp.ClientSession) -> OpenAPIClient:
    return OpenAPIClient(api_key="fake", session=session, base_url=TEST_BASE_URL)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("method", "path", "command", "args"),
    [
        pytest.param("POST", "charging/start", "start_charging", (), id="post"),
        pytest.param(
            "POST",
            "air-conditioning/start",
            "start_air_conditioning",
            (21.0,),
            id="post_with_payload",
        ),
        pytest.param("PUT", "charging/limit", "set_charge_limit", (80,), id="put"),
    ],
)
async def test_command_keeps_rate_limit_headers(
    aresponses, method: str, path: str, command: str, args: tuple
) -> None:
    """A successful command exposes its headers on the result and on the client."""
    aresponses.add(
        TEST_HOST,
        f"/api/v1/vehicles/{VIN}/{path}",
        method,
        aresponses.Response(status=202, headers=QUOTA_HEADERS),
    )

    async with aiohttp.ClientSession() as session:
        client = _client(session)
        result = await getattr(client, command)(VIN, *args)

    assert result.status == 202
    assert result.headers["ratelimit-remaining"] == "11"
    assert client.last_headers == result.headers
    assert client.rate_limit_remaining == 11
    assert client.rate_limit_reset == 2248


@pytest.mark.asyncio
async def test_failed_command_keeps_previous_headers(aresponses) -> None:
    """A failed command leaves ``last_headers`` alone; its headers are on the error."""
    aresponses.add(
        TEST_HOST,
        f"/api/v1/vehicles/{VIN}/charging/start",
        "POST",
        aresponses.Response(status=202, headers=QUOTA_HEADERS),
    )
    aresponses.add(
        TEST_HOST,
        f"/api/v1/vehicles/{VIN}/charging/start",
        "POST",
        aresponses.Response(
            status=429, headers={**QUOTA_HEADERS, "RateLimit-Remaining": "0"}
        ),
    )

    async with aiohttp.ClientSession() as session:
        client = _client(session)
        await client.start_charging(VIN)
        with pytest.raises(OpenApiRateLimitError) as exc_info:
            await client.start_charging(VIN)

    assert exc_info.value.rate_limit_remaining == 0
    assert client.rate_limit_remaining == 11
