"""Commands for the CLI for operations that can be performed."""

from typing import TYPE_CHECKING, Optional

import asyncclick as click
from asyncclick.core import Context

from ..models.enums import TemperatureUnit
from .utils import StrEnumChoice, handle_request

if TYPE_CHECKING:
    from ..api_layer.open_api_client import OpenAPIClient

TEMPERATURE_UNITS = [TemperatureUnit.CELSIUS, TemperatureUnit.FAHRENHEIT]


@click.command()
@click.argument("vin")
@click.option(
    "temperature",
    "--temperature",
    type=float,
    required=True,
    help="Target temperature for the air conditioning.",
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
    temperature: float,
    unit: TemperatureUnit,
    with_external_power: bool,
) -> None:
    """Start the air conditioning with the provided target temperature."""
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
    temperature: Optional[float],
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
