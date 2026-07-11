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
    
    async def start_air_conditioning(self, vin: str, target_temperature: float, spin: Optional[str] = None, unit: str = "CELSIUS") -> None:
        """Start the air conditioning for the vehicle with the given VIN and target temperature."""
        pass #TODO implementation by the swagger
    
    async def stop_air_conditioning(self, vin: str) -> None:
        """Stops the air_conditioning of the vehicle and return None if it was succesfull else catch an exception in HomeAssistant"""
        await self.rest_api.stop_air_conditioning(vin)

    async def start_auxiliary_heating(self, vin: str, spin: str, duration_in_seconds: int = 120, start_mode: str = "HEATING", target_temperature: Optional[float] = None, unit: str = "CELSIUS") -> None:
        """Starts the auxiliary heating for the vehicle with the given VIN."""
        payload = {
            "spin": spin,
            "durationInSeconds": duration_in_seconds,
            "startMode": start_mode
        }
        # If there is target temperature, add it into the payload
        if target_temperature is not None:
            payload["targetTemperature"] = {
                "value": target_temperature,
                "unit": unit
            }
            
        await self.rest_api.start_auxiliary_heating(vin, payload=payload)

    async def stop_auxiliary_heating(self, vin: str) -> None:
        """Stops the auxiliary_heating of the vehicle and return None if it was succesfull else catch an exception in HomeAssistant"""
        await self.rest_api.stop_auxiliary_heating(vin)
    
    async def start_active_ventilation(self, vin: str) -> None:
        """Starts the active_ventilation for the vehicle with the given VIN."""
        await self.rest_api.start_active_ventilation(vin)

    async def stop_active_ventilation(self, vin: str) -> None:
        """Stops the active_ventilation of the vehicle and return None if it was succesfull else catch an exception in HomeAssistant"""
        await self.rest_api.stop_active_ventilation(vin)


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
