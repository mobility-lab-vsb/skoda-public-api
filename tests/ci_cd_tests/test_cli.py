"""Tests for the CLI."""

import json
from unittest.mock import AsyncMock

import aresponses
import pytest
from asyncclick.testing import CliRunner
from pydantic import ValidationError

from myskoda_openapi.api_layer.exceptions import OpenApiAuthenticationError
from myskoda_openapi.api_layer.open_api_client import OpenAPIClient
from myskoda_openapi.api_layer.rest_api import PostEndpointResult
from myskoda_openapi.cli import cli
from myskoda_openapi.cli.operations import start_air_conditioning, start_auxiliary_heating
from myskoda_openapi.cli.utils import print_json, print_yaml
from myskoda_openapi.models.vehicle import Odometer

VIN = "DMBGF9NY3NF032963"

GET_COMMANDS = [
    ("get-vehicle-status", "get_vehicle_status"),
    ("get-air-conditioning", "get_air_conditioning"),
    ("get-parking-position", "get_parking_positions"),
    ("get-auxiliary-heating", "get_auxiliary_heating"),
    ("get-odometer", "get_odometer"),
    ("get-charging", "get_charging"),
    ("get-active-ventilation", "get_active_ventilation"),
    ("get-charging-profiles", "get_charging_profiles"),
    ("get-fuel-status", "get_fuel_status"),
]

SIMPLE_OPERATIONS = [
    ("stop-air-conditioning", "stop_air_conditioning"),
    ("stop-auxiliary-heating", "stop_auxiliary_heating"),
    ("start-active-ventilation", "start_active_ventilation"),
    ("stop-active-ventilation", "stop_active_ventilation"),
    ("start-charging", "start_charging"),
    ("stop-charging", "stop_charging"),
]


@pytest.mark.asyncio
async def test_cli_without_api_key_is_a_usage_error() -> None:
    """Invoking without --api-key (and without SKODA_API_KEY) fails before any network access."""
    runner = CliRunner()
    result = await runner.invoke(
        cli,
        ["--endpoint", "test", "get-vehicle", VIN],
        env={},
    )
    assert result.exit_code != 0
    assert "--api-key" in result.output


@pytest.mark.asyncio
async def test_cli_get_vehicle_test_endpoint(aresponses) -> None:
    """Full CLI invocation for get-vehicle against the test endpoint.

    The HTTP layer is mocked with aresponses: no real outgoing request is made.
    """
    aresponses.add(
        "public.test-api.connect.skoda-auto.cz",
        f"/api/v1/vehicles/{VIN}",
        "GET",
        aresponses.Response(
            text=json.dumps({"vehicle": {"vin": VIN}}),
            status=200,
            content_type="application/json",
        ),
    )
    runner = CliRunner()
    result = await runner.invoke(
        cli,
        ["--api-key", "dummy", "--endpoint", "test", "get-vehicle", VIN],
        env={},
    )
    assert result.exit_code == 0, result.output
    assert VIN in result.output


@pytest.mark.asyncio
async def test_cli_api_key_from_environment(aresponses) -> None:
    """The API key can also be provided via the SKODA_API_KEY environment variable."""
    aresponses.add(
        "public.test-api.connect.skoda-auto.cz",
        f"/api/v1/vehicles/{VIN}",
        "GET",
        aresponses.Response(
            text=json.dumps({"vehicle": {"vin": VIN}}),
            status=200,
            content_type="application/json",
        ),
    )
    runner = CliRunner()
    result = await runner.invoke(
        cli,
        ["--endpoint", "test", "get-vehicle", VIN],
        env={"SKODA_API_KEY": "dummy"},
    )
    assert result.exit_code == 0, result.output
    assert VIN in result.output


@pytest.mark.asyncio
@pytest.mark.parametrize(("command", "method"), GET_COMMANDS)
async def test_get_commands_call_client(command: str, method: str) -> None:
    """Every GET command calls the matching client method with the VIN."""
    mock = AsyncMock(spec=OpenAPIClient)
    getattr(mock, method).return_value = None
    runner = CliRunner()
    result = await runner.invoke(
        cli.commands[command],
        [VIN],
        obj={"client": mock, "print": print_json},
    )
    assert result.exit_code == 0, result.output
    assert '"status": "ok"' in result.output
    getattr(mock, method).assert_awaited_once_with(VIN)


@pytest.mark.asyncio
async def test_get_vehicle_without_include() -> None:
    mock = AsyncMock(spec=OpenAPIClient)
    mock.get_vehicle.return_value = None
    runner = CliRunner()
    result = await runner.invoke(
        cli.commands["get-vehicle"],
        [VIN],
        obj={"client": mock, "print": print_json},
    )
    assert result.exit_code == 0, result.output
    mock.get_vehicle.assert_awaited_once_with(VIN, None)


@pytest.mark.asyncio
async def test_get_vehicle_with_include() -> None:
    mock = AsyncMock(spec=OpenAPIClient)
    mock.get_vehicle.return_value = None
    runner = CliRunner()
    result = await runner.invoke(
        cli.commands["get-vehicle"],
        [VIN, "--include", "status", "--include", "charging"],
        obj={"client": mock, "print": print_json},
    )
    assert result.exit_code == 0, result.output
    mock.get_vehicle.assert_awaited_once_with(VIN, ["status", "charging"])


@pytest.mark.asyncio
async def test_get_command_prints_model_as_camel_case_json() -> None:
    mock = AsyncMock(spec=OpenAPIClient)
    mock.get_odometer.return_value = Odometer(
        mileage_in_km=12345,
        car_captured_timestamp=None,
    )
    runner = CliRunner()
    result = await runner.invoke(
        cli.commands["get-odometer"],
        [VIN],
        obj={"client": mock, "print": print_json},
    )
    assert result.exit_code == 0, result.output
    assert '"mileageInKm": 12345' in result.output


@pytest.mark.asyncio
@pytest.mark.parametrize(("command", "method"), SIMPLE_OPERATIONS)
async def test_simple_operations_call_client(command: str, method: str) -> None:
    """Every simple POST command calls the matching client method and prints the result."""
    mock = AsyncMock(spec=OpenAPIClient)
    getattr(mock, method).return_value = PostEndpointResult(
        url=f"/api/v1/vehicles/{VIN}",
        status=200,
        headers={},
    )
    runner = CliRunner()
    result = await runner.invoke(
        cli.commands[command],
        [VIN],
        obj={"client": mock, "print": print_json},
    )
    assert result.exit_code == 0, result.output
    assert '"status": 200' in result.output
    getattr(mock, method).assert_awaited_once_with(VIN)


@pytest.mark.asyncio
async def test_start_air_conditioning_defaults() -> None:
    mock = AsyncMock(spec=OpenAPIClient)
    mock.start_air_conditioning.return_value = PostEndpointResult(
        url=f"/api/v1/vehicles/{VIN}/air-conditioning/start",
        status=200,
        headers={},
    )
    runner = CliRunner()
    result = await runner.invoke(
        start_air_conditioning,
        [VIN, "--temperature", "21"],
        obj={"client": mock, "print": print_json},
    )
    assert result.exit_code == 0, result.output
    mock.start_air_conditioning.assert_awaited_once_with(VIN, 21.0, "CELSIUS", True)


@pytest.mark.asyncio
async def test_start_air_conditioning_with_options() -> None:
    mock = AsyncMock(spec=OpenAPIClient)
    mock.start_air_conditioning.return_value = PostEndpointResult(
        url=f"/api/v1/vehicles/{VIN}/air-conditioning/start",
        status=200,
        headers={},
    )
    runner = CliRunner()
    result = await runner.invoke(
        start_air_conditioning,
        [VIN, "--temperature", "21.5", "--unit", "FAHRENHEIT", "--with-external-power"],
        obj={"client": mock, "print": print_json},
    )
    assert result.exit_code == 0, result.output
    mock.start_air_conditioning.assert_awaited_once_with(VIN, 21.5, "FAHRENHEIT", False)


@pytest.mark.asyncio
async def test_start_auxiliary_heating_defaults() -> None:
    mock = AsyncMock(spec=OpenAPIClient)
    mock.start_auxiliary_heating.return_value = PostEndpointResult(
        url=f"/api/v1/vehicles/{VIN}/auxiliary-heating/start",
        status=200,
        headers={},
    )
    runner = CliRunner()
    result = await runner.invoke(
        start_auxiliary_heating,
        [VIN, "--spin", "1234"],
        obj={"client": mock, "print": print_json},
    )
    assert result.exit_code == 0, result.output
    mock.start_auxiliary_heating.assert_awaited_once_with(
        VIN, "1234", 120, "HEATING", None, "CELSIUS"
    )


@pytest.mark.asyncio
async def test_start_auxiliary_heating_with_options() -> None:
    mock = AsyncMock(spec=OpenAPIClient)
    mock.start_auxiliary_heating.return_value = PostEndpointResult(
        url=f"/api/v1/vehicles/{VIN}/auxiliary-heating/start",
        status=200,
        headers={},
    )
    runner = CliRunner()
    result = await runner.invoke(
        start_auxiliary_heating,
        [
            VIN,
            "--spin",
            "1234",
            "--duration",
            "60",
            "--start-mode",
            "VENTILATION",
            "--temperature",
            "21.5",
            "--unit",
            "FAHRENHEIT",
        ],
        obj={"client": mock, "print": print_json},
    )
    assert result.exit_code == 0, result.output
    mock.start_auxiliary_heating.assert_awaited_once_with(
        VIN, "1234", 60, "VENTILATION", 21.5, "FAHRENHEIT"
    )


@pytest.mark.asyncio
async def test_handle_request_prints_error_and_continues() -> None:
    """OpenApiError is printed as an error object and does not fail the command."""
    mock = AsyncMock(spec=OpenAPIClient)
    mock.get_vehicle_status.side_effect = OpenApiAuthenticationError()
    runner = CliRunner()
    result = await runner.invoke(
        cli.commands["get-vehicle-status"],
        [VIN],
        obj={"client": mock, "print": print_json},
    )
    assert result.exit_code == 0, result.output
    assert '"error": "OpenApiAuthenticationError"' in result.output
    assert '"status_code": 401' in result.output


@pytest.mark.asyncio
async def test_handle_request_prints_validation_error() -> None:
    """A pydantic ValidationError is printed as an error object instead of crashing."""
    mock = AsyncMock(spec=OpenAPIClient)
    mock.get_vehicle_status.side_effect = ValidationError.from_exception_data(
        "VehicleResponse",
        [
            {
                "type": "enum",
                "loc": ("errors", 0, "type"),
                "input": "FUEL_STATUS_DISABLED",
                "msg": "Input should be 'FOO' or 'BAR'",
                "ctx": {"expected": "'FOO' or 'BAR'"},
            }
        ],
    )
    runner = CliRunner()
    result = await runner.invoke(
        cli.commands["get-vehicle-status"],
        [VIN],
        obj={"client": mock, "print": print_json},
    )
    assert result.exit_code == 0, result.output
    assert '"error": "ValidationError"' in result.output
    assert '"status_code": null' in result.output


@pytest.mark.asyncio
async def test_yaml_output() -> None:
    mock = AsyncMock(spec=OpenAPIClient)
    mock.stop_charging.return_value = PostEndpointResult(
        url=f"/api/v1/vehicles/{VIN}/charging/stop",
        status=200,
        headers={},
    )
    runner = CliRunner()
    result = await runner.invoke(
        cli.commands["stop-charging"],
        [VIN],
        obj={"client": mock, "print": print_yaml},
    )
    assert result.exit_code == 0, result.output
    assert "status: 200" in result.output
