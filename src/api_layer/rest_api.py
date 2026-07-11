import asyncio
import logging
from typing import Generic, Optional, TypeVar, Any, List
from dataclasses import dataclass
from aiohttp import ClientResponseError, ClientSession
from .const import SANDBOX_BASE_URL, PRODUCTION_BASE_URL, TEST_BASE_URL
from models.vehicle import VehicleResponse
from models.vehicle_status import VehicleStatus
from .exceptions import (
    OpenApiError,
    OpenApiAuthenticationError,
    OpenApiForbiddenError,
    OpenApiVehicleNotFoundError,
    OpenApiRateLimitError,
)

T = TypeVar("T")
_LOGGER = logging.getLogger(__name__)

class GetEndpointResult(Generic[T]):
    """Wrapper for the result of a GET request to an endpoint, containing the URL, raw JSON data, and the parsed Pydantic model."""
    def __init__(self, url: str, raw_json: Any, result: T) -> None:
        self.url = url
        self.raw_json = raw_json          
        self.result = result    # Final Pydantic model after parsing raw Json.

class PostEndpointResult:
    """Wrapper for the result of a POST request to an endpoint, containing the URL, status code, and headers."""
    def __init__(self, url: str, status: int, headers: dict) -> None:
        self.url = url
        self.status = status
        self.headers = headers # Užitečné např. pro sledování RateLimit-Remaining nebo X-API-Key-Expires-At


class SkodaRestAPI:
    """Rest API client for interacting with the Škoda Open API."""

    def __init__(self, api_key: str, session: ClientSession) -> None:
        self._api_key = api_key
        self._session = session
        self._base_url = TEST_BASE_URL  # Default to TEST_BASE_URL; can be changed to SANDBOX_BASE_URL or PRODUCTION_BASE_URL as needed.
        #TODO will be exteded with methods for authorization, token management, and other endpoints as needed.

    async def _make_post_request(self, url: str, json_data: Optional[dict] = None) -> int:
        """Helper method to make POST requests to the Škoda API."""
        full_url = f"{self._base_url}{url}"
        headers = {
            "X-API-Key": self._api_key,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        
        try:
            async with self._session.post(full_url, headers=headers, json=json_data) as response:
                if response.status not in (200, 202):
                    match response.status:
                        case 401: raise OpenApiAuthenticationError("Invalid or expired X-API-Key.")
                        case 403: raise OpenApiForbiddenError("Access forbidden. User not allowed to execute operation.")
                        case 404: raise OpenApiVehicleNotFoundError("Vehicle with this VIN does not exist.")
                        case 429: raise OpenApiRateLimitError("Rate limit exceeded or insufficient battery level.")
                        case 400: raise OpenApiError("Bad request (e.g. validation or VIN issues).")
                
                return response.status
        except Exception as err:
            if isinstance(err, OpenApiError):
                raise
            raise OpenApiError(f"There has been an error when trying to make the POST request: {err}") from err

    async def _make_get_request(self, url: str, params: Optional[dict] = None) -> Any:
        """Helper method to make GET requests to the Škoda API."""
        full_url = f"{self._base_url}{url}"
        headers = {
            "X-API-Key": self._api_key,
            "Accept": "application/json",
        }
        
        try:
            async with self._session.get(full_url, headers=headers, params=params) as response:
                if response.status not in (200, 202):
                    match response.status:
                        case 401: raise OpenApiAuthenticationError("Invalid or expired X-API-Key.") 
                        case 403: raise OpenApiForbiddenError("Access to the requested resource is forbidden.") 
                        case 404: raise OpenApiVehicleNotFoundError("Vehicle with this VIN does not exist.") 
                        case 429: raise OpenApiRateLimitError("Rate limit exceeded or weak 12V battery.") 
                return await response.json()
        except Exception as err:
            raise OpenApiError(f"There has been an error when trying to make the request: {err}") from err

    # =========================================================================
    # ENDPOINT METHODS - GET
    # =========================================================================
    async def get_vehicle(self, vin: str, include: Optional[List[str]] = None) -> GetEndpointResult[VehicleResponse]:
        """Call the GET /api/v1/vehicles/{vin} endpoint to retrieve vehicle data for a given VIN."""
        url = f"/api/v1/vehicles/{vin}"
        params = {}
        if include:
            params["include"] = ",".join(include)

        raw_json = await self._make_get_request(url, params=params)
        
        # Deserializace raw_json into Pydantic model VehicleResponse
        full_response = VehicleResponse.model_validate(raw_json)
        
        # Pack and retunr the result in GetEndpointResult
        return GetEndpointResult(url=url, raw_json=raw_json, result=full_response)
    
    async def get_vehicle_status(self, vin: str) -> GetEndpointResult[Optional[VehicleStatus]]:
        """Retrieve ONLY the vehicle status by filtering via the 'include' parameter."""
        url = f"/api/v1/vehicles/{vin}"        
        # Set the 'include' parameter to 'status' to retrieve only the vehicle status
        params = {"include": "status"}

        raw_json = await self._make_get_request(url, params=params)
        # Parse whole response into VehicleResponse model
        full_response = VehicleResponse.model_validate(raw_json)
        status_model = full_response.vehicle.status
        
        return GetEndpointResult(url=url, raw_json=raw_json, result=status_model)
    
    # =========================================================================
    # ENDPOINT METHODS - POST
    # =========================================================================
    async def start_air_conditioning(self, vin: str, payload: dict) -> PostEndpointResult:
        """Starts the air conditioning for the vehicle with the given VIN. The payload should contain any necessary parameters for starting the air conditioning."""
        url = f"/api/v1/vehicles/{vin}/air-conditioning/start"
        
        status = await self._make_post_request(url, json_data=payload)
        return PostEndpointResult(url=url, status=status, headers={})
    
    async def stop_air_conditioning(self, vin: str) -> PostEndpointResult:
        """Stops the air_conditioning for the given VIN"""
        url = f"/api/v1/vehicles/{vin}/air-conditioning/stop"
        
        status = await self._make_post_request(url)
        return PostEndpointResult(url=url, status=status, headers={})
    
    async def start_auxiliary_heating(self, vin: str, payload: dict) -> PostEndpointResult:
        """Starts the auxiliary heating for the vehicle with the given VIN. The payload should contain any necessary parameters for starting the auxiliary heating."""
        url = f"/api/v1/vehicles/{vin}/auxiliary-heating/start"
        
        status = await self._make_post_request(url, json_data=payload)
        return PostEndpointResult(url=url, status=status, headers={})
    
    async def stop_auxiliary_heating(self, vin: str) -> PostEndpointResult:
        """Stops the auxiliary heating for the given VIN"""
        url = f"/api/v1/vehicles/{vin}/auxiliary-heating/stop"
        
        status = await self._make_post_request(url)
        return PostEndpointResult(url=url, status=status, headers={})
    
    async def start_active_ventilation(self, vin: str, payload: dict) -> PostEndpointResult:
        """Starts the active ventilation for the vehicle with the given VIN. The payload should contain any necessary parameters for starting the active ventilation."""
        url = f"/api/v1/vehicles/{vin}/active-ventilation/start"
        
        status = await self._make_post_request(url, json_data=payload)
        return PostEndpointResult(url=url, status=status, headers={})
    
    async def stop_active_ventilation(self, vin: str) -> PostEndpointResult:
        """Stops the active ventilation for the given VIN"""
        url = f"/api/v1/vehicles/{vin}/active-ventilation/stop"
        
        status = await self._make_post_request(url)
        return PostEndpointResult(url=url, status=status, headers={})
    
    #TODO rest of the methods