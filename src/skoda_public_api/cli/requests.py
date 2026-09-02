"""Commands dealing with reading data from the Rest API."""

from typing import TYPE_CHECKING

import asyncclick as click
from asyncclick.core import Context

from .utils import handle_request

if TYPE_CHECKING:
    from ..api_layer.open_api_client import OpenAPIClient


@click.command()
@click.argument("vin")
@click.option(
    "include",
    "--include",
    help="Optional field to include in the response. Can be specified multiple times.",
    multiple=True,
)
@click.pass_context
async def get_vehicle(ctx: Context, vin: str, include: tuple[str, ...]) -> None:
    """Print info for the specified VIN."""
    client: OpenAPIClient = ctx.obj["client"]
    await handle_request(ctx, client.get_vehicle, vin, list(include) or None)


@click.command()
@click.argument("vin")
@click.pass_context
async def get_vehicle_status(ctx: Context, vin: str) -> None:
    """Print the current status for the specified VIN."""
    client: OpenAPIClient = ctx.obj["client"]
    await handle_request(ctx, client.get_vehicle_status, vin)


@click.command()
@click.argument("vin")
@click.pass_context
async def get_air_conditioning(ctx: Context, vin: str) -> None:
    """Print the current air conditioning status for the specified VIN."""
    client: OpenAPIClient = ctx.obj["client"]
    await handle_request(ctx, client.get_air_conditioning, vin)


@click.command()
@click.argument("vin")
@click.pass_context
async def get_parking_position(ctx: Context, vin: str) -> None:
    """Print the current parking position for the specified VIN."""
    client: OpenAPIClient = ctx.obj["client"]
    await handle_request(ctx, client.get_parking_positions, vin)


@click.command()
@click.argument("vin")
@click.pass_context
async def get_auxiliary_heating(ctx: Context, vin: str) -> None:
    """Print the current auxiliary heating status for the specified VIN."""
    client: OpenAPIClient = ctx.obj["client"]
    await handle_request(ctx, client.get_auxiliary_heating, vin)


@click.command()
@click.argument("vin")
@click.pass_context
async def get_odometer(ctx: Context, vin: str) -> None:
    """Print the current odometer for the specified VIN."""
    client: OpenAPIClient = ctx.obj["client"]
    await handle_request(ctx, client.get_odometer, vin)


@click.command()
@click.argument("vin")
@click.pass_context
async def get_charging(ctx: Context, vin: str) -> None:
    """Print the current charging status for the specified VIN."""
    client: OpenAPIClient = ctx.obj["client"]
    await handle_request(ctx, client.get_charging, vin)


@click.command()
@click.argument("vin")
@click.pass_context
async def get_active_ventilation(ctx: Context, vin: str) -> None:
    """Print the current active ventilation status for the specified VIN."""
    client: OpenAPIClient = ctx.obj["client"]
    await handle_request(ctx, client.get_active_ventilation, vin)


@click.command()
@click.argument("vin")
@click.pass_context
async def get_charging_profiles(ctx: Context, vin: str) -> None:
    """Print the charging profiles for the specified VIN."""
    client: OpenAPIClient = ctx.obj["client"]
    await handle_request(ctx, client.get_charging_profiles, vin)


@click.command()
@click.argument("vin")
@click.pass_context
async def get_fuel_status(ctx: Context, vin: str) -> None:
    """Print the fuel status for the specified VIN."""
    client: OpenAPIClient = ctx.obj["client"]
    await handle_request(ctx, client.get_fuel_status, vin)
