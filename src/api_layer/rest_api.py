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


class SkodaRestAPI:
    """Rest API client for interacting with the Škoda Open API."""

    def __init__(self, api_key: str, session: ClientSession) -> None:
        self._api_key = api_key
        self._session = session
        self._base_url = TEST_BASE_URL  # Default to TEST_BASE_URL; can be changed to SANDBOX_BASE_URL or PRODUCTION_BASE_URL as needed.

    async def _make_get_request(self, url: str, params: Optional[dict] = None) -> Any:
        """Helper method to make GET requests to the Škoda API."""
        full_url = f"{self._base_url}{url}"
        headers = {
            "X-API-Key": self._api_key,
            "Accept": "application/json",
        }
        
        try:
            async with self._session.get(full_url, headers=headers, params=params) as response:
                if response.status != 200:
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
