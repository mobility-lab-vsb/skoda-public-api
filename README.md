# vsb-developer-api

VSB developer API is a Python library to interact with the new VSB API for connected-vehicle data and remote control of VSB vehicles.

## As CLI

The library ships with a command line interface called `skodactl`, which is useful for manually
testing the API endpoints. Install it together with the CLI dependencies:

```sh
pip install "myvsb-developer-api[cli]"
```

You authenticate with your API key, either via the `--api-key` option or the `SKODA_API_KEY`
environment variable, and address a vehicle by its VIN:

```sh
skodactl --api-key XXX get-vehicle DMBGF9NY3NF032963
```

By default, the CLI talks to the production endpoint. Point it at the public test endpoint with
`--endpoint test`, switch to YAML output with `--format yaml`, or log HTTP requests and responses
with `--trace`:

```sh
skodactl --api-key XXX --endpoint test get-vehicle-status DMBGF9NY3NF032963
SKODA_API_KEY=XXX skodactl --format yaml --trace get-charging DMBGF9NY3NF032963
```

Remote operations can be started as well:

```sh
skodactl --api-key XXX start-air-conditioning DMBGF9NY3NF032963 --temperature 21
```

Run `skodactl --help` for the full list of commands and options.
