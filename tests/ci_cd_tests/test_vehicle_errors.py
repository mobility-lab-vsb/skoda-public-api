"""Parsing of VehicleResponse.errors (issue #32)."""

from unittest.mock import AsyncMock, patch

import pytest

from skoda_public_api.api_layer.exceptions import (
    OpenApiError,
    OpenApiResponseValidationError,
)
from skoda_public_api.api_layer.rest_api import SkodaRestAPI
from skoda_public_api.models.enums import VehicleCapability, VehicleErrorState
from skoda_public_api.models.vehicle import VehicleResponse

VIN = "TMBJB9NY5RF999999"


def _payload(*error_types: str) -> dict:
    return {
        "vehicle": {"vin": VIN, "name": "x"},
        "errors": [{"type": t, "description": "d"} for t in error_types],
    }


@pytest.mark.parametrize(
    "error_type",
    [
        "RENDER_UNAVAILABLE",
        "CHARGING_PROFILES_UNSUPPORTED",
        "CHARGING_PROFILES_DISABLED",
        "CHARGING_PROFILES_UNAVAILABLE",
        "OPERATIONS_UNAVAILABLE",
    ],
)
def test_spec_error_types_parse_as_enum(error_type: str) -> None:
    """Every error type listed in the API spec maps to a VehicleErrorState member."""
    response = VehicleResponse.model_validate(_payload(error_type))

    assert response.errors[0].type is VehicleErrorState(error_type)


def test_unknown_error_type_falls_back_to_str() -> None:
    """An error type not (yet) known to the library must not fail the whole response."""
    response = VehicleResponse.model_validate(
        _payload("SOME_FUTURE_FEATURE_UNAVAILABLE", "CHARGING_UNAVAILABLE")
    )

    unknown, known = response.errors
    assert unknown.type == "SOME_FUTURE_FEATURE_UNAVAILABLE"
    assert not isinstance(unknown.type, VehicleErrorState)
    assert known.type is VehicleErrorState.CHARGING_UNAVAILABLE
    # Capability detection still works alongside an unknown error type.
    assert VehicleCapability.CHARGING in response.supported_capabilities()


def test_charging_profiles_unavailable_counts_as_supported() -> None:
    """A transient CHARGING_PROFILES_UNAVAILABLE error must not hide the capability."""
    response = VehicleResponse.model_validate(_payload("CHARGING_PROFILES_UNAVAILABLE"))

    caps = response.supported_capabilities()
    assert VehicleCapability.CHARGING_PROFILES in caps
    # The CHARGING prefix must not be confused with CHARGING_PROFILES.
    assert VehicleCapability.CHARGING not in caps


@pytest.mark.asyncio
async def test_invalid_response_raises_open_api_error() -> None:
    """A response that fails model validation surfaces as an OpenApiError subclass."""
    api = SkodaRestAPI(api_key="fake", session=AsyncMock())
    bad_json = {"vehicle": {"name": "missing vin"}}

    with patch.object(api, "_make_get_request", AsyncMock(return_value=(bad_json, {}))):
        with pytest.raises(OpenApiResponseValidationError) as exc_info:
            await api.get_vehicle(VIN)

    assert isinstance(exc_info.value, OpenApiError)
