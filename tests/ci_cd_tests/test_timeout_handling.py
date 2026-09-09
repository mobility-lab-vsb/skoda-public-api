from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from skoda_public_api.api_layer.rest_api import SkodaRestAPI
from skoda_public_api.api_layer.exceptions import OpenApiTimeoutError, OpenApiError


@pytest.mark.asyncio
async def test_get_request_timeout_raises_open_api_timeout_error():
    """A client-side timeout on a GET request must surface as OpenApiTimeoutError."""
    session = MagicMock()
    session.get = MagicMock(side_effect=TimeoutError("timed out"))

    api = SkodaRestAPI(api_key="fake", session=session)

    with pytest.raises(OpenApiTimeoutError):
        await api._make_get_request("/api/v1/vehicles/FAKEVIN")


@pytest.mark.asyncio
async def test_post_request_timeout_raises_open_api_timeout_error():
    """A client-side timeout on a POST request must surface as OpenApiTimeoutError."""
    session = MagicMock()
    session.post = MagicMock(side_effect=TimeoutError("timed out"))

    api = SkodaRestAPI(api_key="fake", session=session)

    with pytest.raises(OpenApiTimeoutError):
        await api._make_post_request("/api/v1/vehicles/FAKEVIN/charging/start")


@pytest.mark.asyncio
async def test_open_api_timeout_error_is_an_open_api_error():
    """OpenApiTimeoutError must remain catchable by callers that only expect OpenApiError."""
    assert issubclass(OpenApiTimeoutError, OpenApiError)
