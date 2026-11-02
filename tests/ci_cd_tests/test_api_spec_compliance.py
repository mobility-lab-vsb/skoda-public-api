"""Tests that responses and requests follow the Škoda public API specification."""

from unittest.mock import AsyncMock, MagicMock

import aiohttp
from aiohttp import web
from pydantic import ValidationError
import pytest

from skoda_public_api.api_layer.const import TEST_BASE_URL
from skoda_public_api.api_layer.exceptions import (
    OpenApiError,
    OpenApiServerError,
    OpenApiUnsupportedError,
)
from skoda_public_api.api_layer.open_api_client import OpenAPIClient
from skoda_public_api.api_layer.rest_api import PostEndpointResult, SkodaRestAPI
from skoda_public_api.models.enums import (
    AuxiliaryHeatingState,
    ChargingState,
    LockState,
    MovementState,
    PlugConnectionState,
    VehicleErrorState,
    VehicleOperationName,
)
from skoda_public_api.models.vehicle import VehicleResponse

VIN = "TMBJW0NZ8SC006012"
TEST_HOST = "public.test-api.connect.skoda-auto.cz"


def _response(vehicle: dict, errors: list | None = None) -> VehicleResponse:
    """Validate a raw API response the same way the REST layer does."""
    return VehicleResponse.model_validate(
        {"vehicle": {"vin": VIN, **vehicle}, "errors": errors or []}
    )


def test_auxiliary_heating_preheating_state() -> None:
    """PREHEATING is a documented auxiliary heating state and must not fail validation."""
    response = _response({"auxiliaryHeating": {"state": "PREHEATING"}})

    assert response.vehicle.auxiliary_heating.state is AuxiliaryHeatingState.PREHEATING


def test_unknown_enum_values_fall_back_to_unknown() -> None:
    """Values added to the API later must not fail validation of the whole response."""
    response = _response(
        {
            "charging": {
                "isVehicleInSavedLocation": False,
                "status": {"state": "WAITING_FOR_TIMER"},
            },
            "parkingPosition": {"state": "TOWED"},
            "odometer": {"mileageInKm": 80421},
        },
    )

    assert response.vehicle.charging.status.state is ChargingState.UNKNOWN
    assert response.vehicle.parking_position.state is MovementState.UNKNOWN
    assert response.vehicle.odometer.mileage_in_km == 80421


def test_unknown_fallback_only_for_strings() -> None:
    """Only unrecognized strings fall back to UNKNOWN, other types still fail validation."""
    with pytest.raises(ValidationError):
        _response(
            {
                "charging": {
                    "isVehicleInSavedLocation": False,
                    "status": {"state": 5},
                }
            }
        )


def test_error_without_description() -> None:
    """The error description is optional in the specification."""
    response = _response({}, errors=[{"type": "CHARGING_UNAVAILABLE"}])

    assert response.errors[0].type is VehicleErrorState.CHARGING_UNAVAILABLE
    assert response.errors[0].description is None


def test_fuel_status_numbers() -> None:
    """Fractional numbers are accepted, whole numbers stay int."""
    response = _response(
        {
            "fuelStatus": {
                "carType": "HYBRID",
                "totalRangeInKm": 197,
                "primaryEngineRange": {
                    "engineType": "GASOLINE",
                    "currentFuelLevelInPercent": 87.5,
                    "remainingRangeInKm": 170,
                },
                "secondaryEngineRange": {
                    "engineType": "ELECTRIC",
                    "currentSoCInPercent": 39,
                    "remainingRangeInKm": 27.4,
                },
            }
        }
    )
    fuel_status = response.vehicle.fuel_status

    assert fuel_status.total_range_in_km == 197
    assert isinstance(fuel_status.total_range_in_km, int)
    assert fuel_status.primary_engine_range.current_fuel_level_in_percent == 87.5
    assert fuel_status.secondary_engine_range.remaining_range_in_km == 27.4
    assert fuel_status.secondary_engine_range.current_soc_in_percent == 39


def test_plug_state() -> None:
    """Plug connection and lock state are parsed from the charging status."""
    response = _response(
        {
            "charging": {
                "isVehicleInSavedLocation": True,
                "status": {
                    "state": "CONNECT_CABLE",
                    "plugConnectionState": "DISCONNECTED",
                    "plugLockState": "UNLOCKED",
                },
            }
        }
    )
    status = response.vehicle.charging.status

    assert status.plug_connection_state is PlugConnectionState.DISCONNECTED
    assert status.plug_lock_state is LockState.UNLOCKED


def test_odometer_without_timestamp() -> None:
    """The odometer timestamp is optional in the specification."""
    response = _response({"odometer": {"mileageInKm": 80421}})

    assert response.vehicle.odometer.car_captured_timestamp is None


def test_supported_operations() -> None:
    """Known operations are returned, operations added to the API later are left out."""
    response = _response(
        {
            "operations": [
                {"name": "startCharging"},
                {"name": "stopCharging"},
                {"name": "startAirConditioning"},
                {"name": "someFutureOperation"},
            ]
        }
    )

    assert response.supported_operations() == {
        VehicleOperationName.START_CHARGING,
        VehicleOperationName.STOP_CHARGING,
        VehicleOperationName.START_AIR_CONDITIONING,
    }


def test_supported_operations_unknown_without_list() -> None:
    """Without an operations list the supported operations are unknown, not empty."""
    response = _response({}, errors=[{"type": "OPERATIONS_UNAVAILABLE"}])

    assert response.supported_operations() is None


@pytest.mark.asyncio
async def test_start_air_conditioning_without_temperature() -> None:
    """Without a temperature, no target temperature is sent and the vehicle keeps its own."""
    client = OpenAPIClient(api_key="fake", session=MagicMock())
    client.rest_api = AsyncMock(spec=SkodaRestAPI)

    await client.start_air_conditioning(VIN)

    config = client.rest_api.start_air_conditioning.await_args.args[1]
    assert config.model_dump(by_alias=True, exclude_none=True) == {
        "airConditioningWithoutExternalPower": True
    }


@pytest.mark.asyncio
async def test_start_air_conditioning_with_temperature() -> None:
    """A given temperature is sent as the target temperature."""
    client = OpenAPIClient(api_key="fake", session=MagicMock())
    client.rest_api = AsyncMock(spec=SkodaRestAPI)

    await client.start_air_conditioning(VIN, 21.5)

    config = client.rest_api.start_air_conditioning.await_args.args[1]
    assert config.model_dump(by_alias=True, exclude_none=True)["targetTemperature"] == {
        "value": 21.5,
        "unit": "CELSIUS",
    }


@pytest.mark.asyncio
async def test_set_charge_limit(aresponses) -> None:
    """The charge limit is sent as a PUT with the target state of charge."""
    received: dict = {}

    async def handler(request: web.Request) -> web.Response:
        received.update(await request.json())
        return aresponses.Response(status=202)

    aresponses.add(TEST_HOST, f"/api/v1/vehicles/{VIN}/charging/limit", "PUT", handler)

    async with aiohttp.ClientSession() as session:
        client = OpenAPIClient(api_key="fake", session=session, base_url=TEST_BASE_URL)
        result = await client.set_charge_limit(VIN, 80)

    assert isinstance(result, PostEndpointResult)
    assert result.status == 202
    assert received == {"targetStateOfChargeInPercent": 80}


@pytest.mark.asyncio
async def test_set_charge_limit_rejected(aresponses) -> None:
    """A rejected charge limit surfaces as the matching OpenApiError."""
    aresponses.add(
        TEST_HOST,
        f"/api/v1/vehicles/{VIN}/charging/limit",
        "PUT",
        aresponses.Response(status=422),
    )

    async with aiohttp.ClientSession() as session:
        client = OpenAPIClient(api_key="fake", session=session, base_url=TEST_BASE_URL)
        with pytest.raises(OpenApiUnsupportedError):
            await client.set_charge_limit(VIN, 80)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status", "error"),
    [(409, OpenApiError), (502, OpenApiServerError)],
)
async def test_unexpected_status_raises(aresponses, status: int, error: type) -> None:
    """Status codes not listed in the specification are not treated as success."""
    aresponses.add(
        TEST_HOST,
        f"/api/v1/vehicles/{VIN}/charging/start",
        "POST",
        aresponses.Response(status=status),
    )

    async with aiohttp.ClientSession() as session:
        client = OpenAPIClient(api_key="fake", session=session, base_url=TEST_BASE_URL)
        with pytest.raises(error) as exc_info:
            await client.start_charging(VIN)

    assert exc_info.value.status_code == status
