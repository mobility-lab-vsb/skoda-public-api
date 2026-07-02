import logging
from typing import Any, Optional, List
from aiohttp import ClientSession
from .rest_api import SkodaRestAPI
from models.vehicle import VehicleResponse
from models.vehicle_status import VehicleStatus

class OpenAPIClient:
    """Client for interacting with rest API and used in HomeAssistant."""

    def __init__(self, api_key: str, session: ClientSession) -> None:
       self.rest_api = SkodaRestAPI(api_key=api_key, session=session)

    async def get_vehicle(self, vin: str, include: Optional[List[str]] = None) -> VehicleResponse:
        """Get the actual vehicle data and return the parsed Pydantic model."""
        endpoint_result = await self.rest_api.get_vehicle(vin, include=include)
        return endpoint_result.result
    
    async def get_vehicle_status(self, vin: str, include: Optional[List[str]] = None) -> VehicleStatus:
        """Get the actual vehicle status and return the parsed Pydantic model."""
        endpoint_result = await self.rest_api.get_vehicle_status(vin, include=include)
        return endpoint_result.result

    async def connect(self):
        """TODO: Implementation of connect mechanism."""
        pass
    
    async def disconnect(self) -> None:
        """TODO: Implementation of disconnect mechanism."""
        pass
    
    async def verify_spin(self, spin: str) -> bool:
        """TODO: Implementation of SPIN verification."""
        pass

    # TODO: Add more methods for other endpoints as needed
