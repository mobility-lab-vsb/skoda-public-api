"""CLI to test all API functions and models.

Execute with:
skodactl
"""

from logging import DEBUG, INFO

import asyncclick as click
import coloredlogs
from aiohttp import ClientSession
from asyncclick.core import Context

from ..api_layer.const import ENDPOINT_URLS, Endpoints
from ..api_layer.open_api_client import OpenAPIClient
from .operations import (
    start_active_ventilation,
    start_air_conditioning,
    start_auxiliary_heating,
    start_charging,
    stop_active_ventilation,
    stop_air_conditioning,
    stop_auxiliary_heating,
    stop_charging,
)
from .requests import (
    get_active_ventilation,
    get_air_conditioning,
    get_auxiliary_heating,
    get_charging,
    get_charging_profiles,
    get_fuel_status,
    get_odometer,
    get_parking_position,
    get_vehicle,
    get_vehicle_status,
)
from .utils import TRACE_CONFIG, Format, StrEnumChoice, print_json, print_yaml


@click.group()
@click.option(
    "api_key",
    "--api-key",
    help="API key used to authenticate against the Skoda API.",
    required=True,
    envvar="SKODA_API_KEY",
)
@click.option(
    "endpoint",
    "--endpoint",
    help="Select the API endpoint to use.",
    type=StrEnumChoice(Endpoints),
    default=Endpoints.BETA,
)
@click.option(
    "output_format",
    "--format",
    help="Select the output format. JSON or YAML.",
    type=StrEnumChoice(Format),
    default=Format.JSON,
)
@click.option("verbose", "--verbose", help="Enable verbose logging.", is_flag=True)
@click.option("trace", "--trace", help="Enable tracing of HTTP requests.", is_flag=True)
@click.pass_context
async def cli(
    ctx: Context,
    api_key: str,
    endpoint: Endpoints,
    output_format: Format,
    verbose: bool,
    trace: bool,
) -> None:
    """Interact with the Skoda Open API."""
    coloredlogs.install(level=DEBUG if verbose or trace else INFO)
    ctx.ensure_object(dict)
    ctx.obj["api_key"] = api_key
    ctx.obj["endpoint"] = endpoint
    if output_format == Format.JSON:
        ctx.obj["print"] = print_json
    elif output_format == Format.YAML:
        ctx.obj["print"] = print_yaml

    trace_configs = [TRACE_CONFIG] if trace else []

    if ctx.resilient_parsing:
        return

    session = ClientSession(trace_configs=trace_configs)
    client = OpenAPIClient(
        api_key=api_key,
        session=session,
        base_url=ENDPOINT_URLS[endpoint],
    )
    ctx.obj["client"] = client
    ctx.obj["session"] = session

    async def _close() -> None:
        await session.close()

    ctx.call_on_close(_close)


cli.add_command(get_active_ventilation)
cli.add_command(get_air_conditioning)
cli.add_command(get_auxiliary_heating)
cli.add_command(get_charging)
cli.add_command(get_charging_profiles)
cli.add_command(get_fuel_status)
cli.add_command(get_odometer)
cli.add_command(get_parking_position)
cli.add_command(get_vehicle)
cli.add_command(get_vehicle_status)
cli.add_command(start_active_ventilation)
cli.add_command(start_air_conditioning)
cli.add_command(start_auxiliary_heating)
cli.add_command(start_charging)
cli.add_command(stop_active_ventilation)
cli.add_command(stop_air_conditioning)
cli.add_command(stop_auxiliary_heating)
cli.add_command(stop_charging)


if __name__ == "__main__":
    cli()
