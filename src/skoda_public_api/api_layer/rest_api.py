import json
import logging
from typing import Any, Generic, TypeVar

from aiohttp import ClientResponse, ClientSession
from pydantic import ValidationError

from ..models.active_ventilation import ActiveVentilation
from ..models.air_conditioning import AirConditioning
from ..models.auxiliary_heating import AuxiliaryHeating
from ..models.charging import Charging
from ..models.charging_profiles import ChargingProfiles
from ..models.configurations import (
    ChargingLimitConfiguration,
    StartAirConditioningConfiguration,
    StartAuxiliaryHeatingConfiguration,
)
from ..models.driving_range import FuelStatus
from ..models.parking_position import ParkingPosition
from ..models.vehicle import Odometer, VehicleResponse
from ..models.vehicle_status import VehicleStatus
from .const import BETA_URL
from .exceptions import (
    OpenApiAuthenticationError,
    OpenApiError,
    OpenApiForbiddenError,
    OpenApiRateLimitError,
    OpenApiResponseValidationError,
    OpenApiServerError,
    OpenApiTimeoutError,
    OpenApiUnsupportedError,
    OpenApiVehicleNotFoundError,
)

T = TypeVar("T")
_LOGGER = logging.getLogger(__name__)


class GetEndpointResult(Generic[T]):
    """Wrapper for the result of a GET request to an endpoint, containing the URL, raw JSON data, and the parsed Pydantic model."""

    def __init__(
        self, url: str, raw_json: Any, result: T, headers: dict[str, Any] | None = None
    ) -> None:
        self.url = url
        self.raw_json = raw_json
        self.result = result
        self.headers = headers or {}


class PostEndpointResult:
    """Wrapper for the result of a POST request to an endpoint, containing the URL, status code, and headers."""

    def __init__(self, url: str, status: int, headers: dict) -> None:
        self.url = url
        self.status = status
        self.headers = headers  # Užitečné např. pro sledování RateLimit-Remaining nebo X-API-Key-Expires-At


async def _read_error_body(response: ClientResponse) -> Any:
    """Read the body of an error response without ever masking its status code.

    Returns the parsed JSON when the body is JSON, the raw text otherwise, and
    ``None`` when the body is empty or cannot be read at all.
    """
    try:
        text = await response.text()
    except Exception:  # a body that cannot be read must not hide the status code
        return None
    if not text:
        return None
    try:
        return json.loads(text)
    except ValueError:
        return text


async def _raise_for_status(response: ClientResponse) -> None:
    """Raise the matching OpenApiError for an error status code returned by the API.

    Records headers and the error response body.
    """
    if 200 <= response.status < 300:
        return

    status = response.status
    headers = dict(response.headers)
    body = await _read_error_body(response)

    match status:
        case 401:
            raise OpenApiAuthenticationError(headers=headers, body=body)
        case 403:
            raise OpenApiForbiddenError(headers=headers, body=body)
        case 404:
            raise OpenApiVehicleNotFoundError(headers=headers, body=body)
        case 422:
            raise OpenApiUnsupportedError(headers=headers, body=body)
        case 429:
            raise OpenApiRateLimitError(headers=headers, body=body)
        case 400:
            raise OpenApiError(
                "Bad request (e.g. validation or VIN issues).",
                headers=headers,
                body=body,
            )
        case 500:
            raise OpenApiServerError(headers=headers, body=body)
        case 503:
            raise OpenApiServerError(
                "API key validation is temporarily unavailable. Retry after 10 seconds.",
                503,
                headers,
                body,
            )
        case 504:
            raise OpenApiServerError(
                "The vehicle did not respond in time.", 504, headers, body
            )
        case _ if status >= 500:
            raise OpenApiServerError(
                f"Unexpected server error with status code {status}.",
                status,
                headers,
                body,
            )
        case _:
            raise OpenApiError(
                f"Unexpected status code {status} returned by the API.",
                status,
                headers,
                body,
            )


class SkodaRestAPI:
    """Rest API client for interacting with the Škoda Open API."""

    def __init__(
        self, api_key: str, session: ClientSession, base_url: str = BETA_URL
    ) -> None:
        self._api_key = api_key
        self._session = session
        self._base_url = base_url  # Default to BETA_URL; can be changed to SANDBOX_BASE_URL or PRODUCTION_BASE_URL as needed.
        # TODO will be exteded with methods for authorization, token management, and other endpoints as needed.

    async def _make_command_request(
        self, method: str, url: str, json_data: dict | None = None
    ) -> int:
        """Helper method to make POST or PUT requests to the Škoda API returning the status code."""
        full_url = f"{self._base_url}{url}"
        headers = {
            "X-API-Key": self._api_key,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        try:
            async with self._session.request(
                method, full_url, headers=headers, json=json_data
            ) as response:
                await _raise_for_status(response)

                return response.status
        except TimeoutError as err:
            raise OpenApiTimeoutError(
                f"Timed out while trying to make the {method} request: {err}"
            ) from err
        except Exception as err:
            if isinstance(err, OpenApiError):
                raise
            raise OpenApiError(
                f"There has been an error when trying to make the {method} request: {err}"
            ) from err

    async def _make_get_request(
        self, url: str, params: dict | None = None
    ) -> tuple[Any, dict[str, Any]]:
        """Helper method to make GET requests to the Škoda API returning JSON and headers."""
        full_url = f"{self._base_url}{url}"
        headers = {
            "X-API-Key": self._api_key,
            "Accept": "application/json",
        }

        try:
            async with self._session.get(
                full_url, headers=headers, params=params
            ) as response:
                await _raise_for_status(response)

                json_data = await response.json()
                headers_dict = {k.lower(): v for k, v in response.headers.items()}
                return json_data, headers_dict
        except TimeoutError as err:
            raise OpenApiTimeoutError(
                f"Timed out while trying to make the request: {err}"
            ) from err
        except Exception as err:
            if isinstance(err, OpenApiError):
                raise
            raise OpenApiError(
                f"There has been an error when trying to make the request: {err}"
            ) from err

    @staticmethod
    def _parse_vehicle_response(raw_json: Any) -> VehicleResponse:
        """Parse a vehicle endpoint response, wrapping validation failures in an OpenApiError."""
        try:
            return VehicleResponse.model_validate(raw_json)
        except ValidationError as err:
            raise OpenApiResponseValidationError(
                f"Unexpected response from the vehicle endpoint: {err}"
            ) from err

    # =========================================================================
    # ENDPOINT METHODS - GET
    # =========================================================================
    async def get_vehicle(
        self, vin: str, include: list[str] | None = None
    ) -> GetEndpointResult[VehicleResponse]:
        """Call the GET /api/v1/vehicles/{vin} endpoint to retrieve vehicle data for a given VIN."""
        url = f"/api/v1/vehicles/{vin}"
        params = {}
        if include:
            params["include"] = ",".join(include)

        raw_json, resp_headers = await self._make_get_request(url, params=params)
        # Deserializace raw_json into Pydantic model VehicleResponse
        full_response = self._parse_vehicle_response(raw_json)

        # Pack and retunr the result in GetEndpointResult
        return GetEndpointResult(
            url=url, raw_json=raw_json, result=full_response, headers=resp_headers
        )

    async def get_vehicle_status(
        self, vin: str
    ) -> GetEndpointResult[VehicleStatus | None]:
        """Retrieve ONLY the vehicle status by filtering via the 'include' parameter."""
        url = f"/api/v1/vehicles/{vin}"
        # Set the 'include' parameter to 'status' to retrieve only the vehicle status
        params = {"include": "status"}

        raw_json, resp_headers = await self._make_get_request(url, params=params)
        # Parse whole response into VehicleResponse model
        full_response = self._parse_vehicle_response(raw_json)
        status_model = full_response.vehicle.status

        return GetEndpointResult(
            url=url, raw_json=raw_json, result=status_model, headers=resp_headers
        )

    async def get_air_conditioning(
        self, vin: str
    ) -> GetEndpointResult[AirConditioning | None]:
        """Retrieve ONLY the vehicles air conditioning object by filtering via the 'include' parameter."""
        url = f"/api/v1/vehicles/{vin}"
        params = {"include": "airConditioning"}

        raw_json, resp_headers = await self._make_get_request(url, params=params)

        full_response = self._parse_vehicle_response(raw_json)
        status_model = full_response.vehicle.air_conditioning

        return GetEndpointResult(
            url=url, raw_json=raw_json, result=status_model, headers=resp_headers
        )

    async def get_parking_positions(
        self, vin: str
    ) -> GetEndpointResult[ParkingPosition | None]:
        """Retrieve ONLY the vehicle parking positions object by filtering via the 'include' parameter."""
        url = f"/api/v1/vehicles/{vin}"
        params = {"include": "parkingPosition"}

        raw_json, resp_headers = await self._make_get_request(url, params=params)

        full_response = self._parse_vehicle_response(raw_json)
        status_model = full_response.vehicle.parking_position

        return GetEndpointResult(
            url=url, raw_json=raw_json, result=status_model, headers=resp_headers
        )

    async def get_auxiliary_heating(
        self, vin: str
    ) -> GetEndpointResult[AuxiliaryHeating | None]:
        """Retrieve ONLY the vehicle auxiliary heating by filtering via the 'include' parameter."""
        url = f"/api/v1/vehicles/{vin}"
        params = {"include": "auxiliaryHeating"}

        raw_json, resp_headers = await self._make_get_request(url, params=params)

        full_response = self._parse_vehicle_response(raw_json)
        status_model = full_response.vehicle.auxiliary_heating

        return GetEndpointResult(
            url=url, raw_json=raw_json, result=status_model, headers=resp_headers
        )

    async def get_odometer(self, vin: str) -> GetEndpointResult[Odometer | None]:
        """Retrieve ONLY the vehicle odometer object by filtering via the 'include' parameter."""
        url = f"/api/v1/vehicles/{vin}"
        params = {"include": "odometer"}

        raw_json, resp_headers = await self._make_get_request(url, params=params)

        full_response = self._parse_vehicle_response(raw_json)
        status_model = full_response.vehicle.odometer

        return GetEndpointResult(
            url=url, raw_json=raw_json, result=status_model, headers=resp_headers
        )

    async def get_charging(self, vin: str) -> GetEndpointResult[Charging | None]:
        """Retrieve ONLY the vehicle charging object by filtering via the 'include' parameter."""
        url = f"/api/v1/vehicles/{vin}"
        params = {"include": "charging"}

        raw_json, resp_headers = await self._make_get_request(url, params=params)

        full_response = self._parse_vehicle_response(raw_json)
        status_model = full_response.vehicle.charging

        return GetEndpointResult(
            url=url, raw_json=raw_json, result=status_model, headers=resp_headers
        )

    async def get_active_ventilation(
        self, vin: str
    ) -> GetEndpointResult[ActiveVentilation | None]:
        """Retrieve ONLY the vehicle active ventilation object by filtering via the 'include' parameter."""
        url = f"/api/v1/vehicles/{vin}"
        params = {"include": "activeVentilation"}

        raw_json, resp_headers = await self._make_get_request(url, params=params)

        full_response = self._parse_vehicle_response(raw_json)
        status_model = full_response.vehicle.active_ventilation

        return GetEndpointResult(
            url=url, raw_json=raw_json, result=status_model, headers=resp_headers
        )

    async def get_charging_profiles(
        self, vin: str
    ) -> GetEndpointResult[ChargingProfiles | None]:
        """Retrieve ONLY the vehicle charging profiles object by filtering via the 'include' parameter."""
        url = f"/api/v1/vehicles/{vin}"
        params = {"include": "chargingProfiles"}

        raw_json, resp_headers = await self._make_get_request(url, params=params)

        full_response = self._parse_vehicle_response(raw_json)
        status_model = full_response.vehicle.charging_profiles

        return GetEndpointResult(
            url=url, raw_json=raw_json, result=status_model, headers=resp_headers
        )

    async def get_fuel_status(self, vin: str) -> GetEndpointResult[FuelStatus | None]:
        """Retrieve ONLY the vehicle fuel status object by filtering via the 'include' parameter."""
        url = f"/api/v1/vehicles/{vin}"
        params = {"include": "fuelStatus"}

        raw_json, resp_headers = await self._make_get_request(url, params=params)

        full_response = self._parse_vehicle_response(raw_json)
        status_model = full_response.vehicle.fuel_status

        return GetEndpointResult(
            url=url, raw_json=raw_json, result=status_model, headers=resp_headers
        )

    # =========================================================================
    # ENDPOINT METHODS - POST
    # =========================================================================
    async def start_air_conditioning(
        self, vin: str, config: StartAirConditioningConfiguration
    ) -> PostEndpointResult:
        """Starts the air conditioning for the vehicle with the given VIN. The payload should contain any necessary parameters for starting the air conditioning."""
        url = f"/api/v1/vehicles/{vin}/air-conditioning/start"

        payload = config.model_dump(by_alias=True, exclude_none=True)
        status = await self._make_command_request("POST", url, json_data=payload)
        return PostEndpointResult(url=url, status=status, headers={})

    async def stop_air_conditioning(self, vin: str) -> PostEndpointResult:
        """Stops the air_conditioning for the given VIN"""
        url = f"/api/v1/vehicles/{vin}/air-conditioning/stop"

        status = await self._make_command_request("POST", url)
        return PostEndpointResult(url=url, status=status, headers={})

    async def start_auxiliary_heating(
        self, vin: str, config: StartAuxiliaryHeatingConfiguration
    ) -> PostEndpointResult:
        """Starts the auxiliary heating for the vehicle with the given VIN. The payload should contain any necessary parameters for starting the auxiliary heating."""
        url = f"/api/v1/vehicles/{vin}/auxiliary-heating/start"

        payload = config.model_dump(by_alias=True, exclude_none=True)
        status = await self._make_command_request("POST", url, json_data=payload)
        return PostEndpointResult(url=url, status=status, headers={})

    async def stop_auxiliary_heating(self, vin: str) -> PostEndpointResult:
        """Stops the auxiliary heating for the given VIN"""
        url = f"/api/v1/vehicles/{vin}/auxiliary-heating/stop"

        status = await self._make_command_request("POST", url)
        return PostEndpointResult(url=url, status=status, headers={})

    async def start_active_ventilation(self, vin: str) -> PostEndpointResult:
        """Starts the active ventilation for the vehicle with the given VIN. The payload should contain any necessary parameters for starting the active ventilation."""
        url = f"/api/v1/vehicles/{vin}/active-ventilation/start"

        status = await self._make_command_request("POST", url)
        return PostEndpointResult(url=url, status=status, headers={})

    async def stop_active_ventilation(self, vin: str) -> PostEndpointResult:
        """Stops the active ventilation for the given VIN"""
        url = f"/api/v1/vehicles/{vin}/active-ventilation/stop"

        status = await self._make_command_request("POST", url)
        return PostEndpointResult(url=url, status=status, headers={})

    async def start_charging(self, vin: str) -> PostEndpointResult:
        """Starts the charging process for the vehicle with the given VIN."""
        url = f"/api/v1/vehicles/{vin}/charging/start"

        status = await self._make_command_request("POST", url)
        return PostEndpointResult(url=url, status=status, headers={})

    async def stop_charging(self, vin: str) -> PostEndpointResult:
        """Stops the charging process for the given VIN"""
        url = f"/api/v1/vehicles/{vin}/charging/stop"

        status = await self._make_command_request("POST", url)
        return PostEndpointResult(url=url, status=status, headers={})

    # =========================================================================
    # ENDPOINT METHODS - PUT
    # =========================================================================
    async def set_charging_limit(
        self, vin: str, config: ChargingLimitConfiguration
    ) -> PostEndpointResult:
        """Sets the charging limit (target state of charge) for the vehicle with the given VIN."""
        url = f"/api/v1/vehicles/{vin}/charging/limit"

        payload = config.model_dump(by_alias=True)
        status = await self._make_command_request("PUT", url, json_data=payload)
        return PostEndpointResult(url=url, status=status, headers={})

    # TODO rest of the methods
