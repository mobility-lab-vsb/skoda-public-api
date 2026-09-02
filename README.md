# skoda-public-api

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)

Asynchronous Python library for the Škoda public API, developed by [Mobility Lab @ VSB](https://github.com/mobility-lab-vsb) — Technical University of Ostrava. It provides typed access to connected-vehicle data (status, odometer, charging, climate, fuel, parking position) and remote vehicle control (climate, charging, ventilation) for Škoda vehicles.

It is built on [`aiohttp`](https://docs.aiohttp.org/) and [`pydantic`](https://docs.pydantic.dev/), and ships both as a library and as a standalone CLI (`skodactl`).

This version targets **API v1** of the [Škoda public API](https://public.api.connect.skoda-auto.cz/docs).

## Installation

```sh
pip install skoda-public-api
```

## As a library

```python
import asyncio

from aiohttp import ClientSession

from skoda_public_api.api_layer.open_api_client import OpenAPIClient


async def main() -> None:
    async with ClientSession() as session:
        client = OpenAPIClient(api_key="XXX", session=session)

        vehicle = await client.get_vehicle("TMBJX7NY4PM054321")
        print(vehicle.vehicle.name)

        charging = await client.get_charging("TMBJX7NY4PM054321")
        print(charging.status.battery.state_of_charge_in_percent)


asyncio.run(main())
```

Every response is a typed `pydantic` model — see [`src/skoda_public_api/models`](src/skoda_public_api/models) for the full data model, and [`src/skoda_public_api/api_layer/open_api_client.py`](src/skoda_public_api/api_layer/open_api_client.py) for the full list of available reads (vehicle status, odometer, charging, air conditioning, auxiliary heating, active ventilation, fuel status, parking position, charging profiles) and remote actions (start/stop charging, climate, auxiliary heating, active ventilation, window heating, charge limit, target temperature).

## As CLI

The library ships with a command line interface called `skodactl`, which is useful for manually
testing the API endpoints. Install it together with the CLI dependencies:

```sh
pip install "skoda-public-api[cli]"
```

You authenticate with your API key, either via the `--api-key` option or the `SKODA_API_KEY`
environment variable, and address a vehicle by its VIN:

```sh
skodactl --api-key XXX get-vehicle TMBJX7NY4PM054321
```

By default, the CLI talks to the production endpoint. Point it at the public test endpoint with
`--endpoint test`, switch to YAML output with `--format yaml`, or log HTTP requests and responses
with `--trace`:

```sh
skodactl --api-key XXX --endpoint test get-vehicle-status TMBJX7NY4PM054321
SKODA_API_KEY=XXX skodactl --format yaml --trace get-charging TMBJX7NY4PM054321
```

Remote operations can be started as well:

```sh
skodactl --api-key XXX start-air-conditioning TMBJX7NY4PM054321 --temperature 21
```

Run `skodactl --help` for the full list of commands and options.

## Development

Clone the repository and install it in editable mode together with the test dependencies:

```sh
pip install -e ".[test,cli]"
pytest
```

## License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for details.
