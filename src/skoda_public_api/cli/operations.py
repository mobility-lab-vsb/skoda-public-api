"""Commands for the CLI for operations that can be performed."""

from typing import TYPE_CHECKING, TextIO

import asyncclick as click
from asyncclick.core import Context
from pydantic import ValidationError

from ..models.charging_profiles import ChargingProfile
from ..models.enums import ChargeMode, TemperatureUnit
from .utils import StrEnumChoice, handle_request

if TYPE_CHECKING:
    from ..api_layer.open_api_client import OpenAPIClient

TEMPERATURE_UNITS = [TemperatureUnit.CELSIUS, TemperatureUnit.FAHRENHEIT]
CHARGE_MODES = [mode for mode in ChargeMode if mode is not ChargeMode.UNKNOWN]


@click.command()
@click.argument("vin")
@click.option(
    "temperature",
    "--temperature",
    type=float,
    default=None,
    help="Target temperature for the air conditioning. Without it, the vehicle uses its last set temperature.",
)
@click.option(
    "unit",
    "--unit",
    type=StrEnumChoice(TEMPERATURE_UNITS),
    default=TemperatureUnit.CELSIUS,
    help="Temperature unit, CELSIUS or FAHRENHEIT.",
)
@click.option(
    "with_external_power",
    "--with-external-power",
    is_flag=True,
    help="Start the air conditioning with external power.",
)
@click.pass_context
async def start_air_conditioning(
    ctx: Context,
    vin: str,
    temperature: float | None,
    unit: TemperatureUnit,
    with_external_power: bool,
) -> None:
    """Start the air conditioning, optionally with a target temperature."""
    client: OpenAPIClient = ctx.obj["client"]
    await handle_request(
        ctx,
        client.start_air_conditioning,
        vin,
        temperature,
        unit.value,
        not with_external_power,
    )


@click.command()
@click.argument("vin")
@click.pass_context
async def stop_air_conditioning(ctx: Context, vin: str) -> None:
    """Stop the air conditioning for the specified VIN."""
    client: OpenAPIClient = ctx.obj["client"]
    await handle_request(ctx, client.stop_air_conditioning, vin)


@click.command()
@click.argument("vin")
@click.option("spin", "--spin", required=True, help="SPIN of the vehicle.")
@click.option(
    "duration",
    "--duration",
    type=int,
    default=120,
    help="Duration of heating in seconds.",
)
@click.option(
    "start_mode",
    "--start-mode",
    default="HEATING",
    help="Start mode, HEATING or VENTILATION.",
)
@click.option(
    "temperature",
    "--temperature",
    type=float,
    required=False,
    default=None,
    help="Optional target temperature.",
)
@click.option(
    "unit",
    "--unit",
    type=StrEnumChoice(TEMPERATURE_UNITS),
    default=TemperatureUnit.CELSIUS,
    help="Temperature unit, CELSIUS or FAHRENHEIT.",
)
@click.pass_context
async def start_auxiliary_heating(
    ctx: Context,
    vin: str,
    spin: str,
    duration: int,
    start_mode: str,
    temperature: float | None,
    unit: TemperatureUnit,
) -> None:
    """Start the auxiliary heating for the specified VIN."""
    client: OpenAPIClient = ctx.obj["client"]
    await handle_request(
        ctx,
        client.start_auxiliary_heating,
        vin,
        spin,
        duration,
        start_mode,
        temperature,
        unit.value,
    )


@click.command()
@click.argument("vin")
@click.pass_context
async def stop_auxiliary_heating(ctx: Context, vin: str) -> None:
    """Stop the auxiliary heating for the specified VIN."""
    client: OpenAPIClient = ctx.obj["client"]
    await handle_request(ctx, client.stop_auxiliary_heating, vin)


@click.command()
@click.argument("vin")
@click.pass_context
async def start_active_ventilation(ctx: Context, vin: str) -> None:
    """Start the active ventilation for the specified VIN."""
    client: OpenAPIClient = ctx.obj["client"]
    await handle_request(ctx, client.start_active_ventilation, vin)


@click.command()
@click.argument("vin")
@click.pass_context
async def stop_active_ventilation(ctx: Context, vin: str) -> None:
    """Stop the active ventilation for the specified VIN."""
    client: OpenAPIClient = ctx.obj["client"]
    await handle_request(ctx, client.stop_active_ventilation, vin)


@click.command()
@click.argument("vin")
@click.pass_context
async def start_charging(ctx: Context, vin: str) -> None:
    """Start charging for the specified VIN."""
    client: OpenAPIClient = ctx.obj["client"]
    await handle_request(ctx, client.start_charging, vin)


@click.command()
@click.argument("vin")
@click.pass_context
async def stop_charging(ctx: Context, vin: str) -> None:
    """Stop charging for the specified VIN."""
    client: OpenAPIClient = ctx.obj["client"]
    await handle_request(ctx, client.stop_charging, vin)


@click.command()
@click.argument("vin")
@click.argument("limit", type=click.IntRange(0, 100))
@click.pass_context
async def set_charge_limit(ctx: Context, vin: str, limit: int) -> None:
    """Set the charging limit in percent (typically 50 to 100 in steps of 10)."""
    client: OpenAPIClient = ctx.obj["client"]
    await handle_request(ctx, client.set_charge_limit, vin, limit)


@click.command()
@click.argument("vin")
@click.argument("mode", type=StrEnumChoice(CHARGE_MODES))
@click.pass_context
async def set_charge_mode(ctx: Context, vin: str, mode: ChargeMode) -> None:
    """Set the charge mode, e.g. MANUAL or TIMER."""
    client: OpenAPIClient = ctx.obj["client"]
    await handle_request(ctx, client.set_charge_mode, vin, mode)


@click.command()
@click.argument("vin")
@click.argument("profile_file", type=click.File("r", encoding="utf-8"))
@click.pass_context
async def update_charging_profile(ctx: Context, vin: str, profile_file: TextIO) -> None:
    """Update a charging profile from a JSON file ("-" reads standard input).

    The vehicle applies the profile as a whole: take one profile from the output
    of get-charging-profiles, change the fields you need and pass the complete
    profile.
    """
    try:
        profile = ChargingProfile.model_validate_json(profile_file.read())
    except ValidationError as err:
        raise click.BadParameter(str(err), param_hint="PROFILE_FILE") from err
    client: OpenAPIClient = ctx.obj["client"]
    await handle_request(ctx, client.update_charging_profile, vin, profile)
