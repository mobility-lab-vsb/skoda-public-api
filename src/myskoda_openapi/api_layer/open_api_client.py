import logging
from typing import Any, Optional, List
from aiohttp import ClientSession
from .rest_api import SkodaRestAPI
from models.vehicle import VehicleResponse, Odometer
from models.vehicle_status import VehicleStatus
from models.active_ventilation import ActiveVentilation
from models.air_conditioning import AirConditioning
from models.parking_position import ParkingPosition
from models.auxiliary_heating import AuxiliaryHeating
from models.charging import Charging

class OpenAPIClient:
    """Client for interacting with rest API and used in HomeAssistant."""

    def __init__(self, api_key: str, session: ClientSession) -> None:
       self.rest_api = SkodaRestAPI(api_key=api_key, session=session)

    async def get_vehicle(self, vin: str, include: Optional[List[str]] = None) -> VehicleResponse:
        """Get the actual vehicle data and return the parsed Pydantic model."""
        endpoint_result = await self.rest_api.get_vehicle(vin, include=include)
        return endpoint_result.result
    
    async def get_vehicle_status(self, vin: str) -> VehicleStatus:
        """Get the actual vehicle status and return the parsed Pydantic model."""
        endpoint_result = await self.rest_api.get_vehicle_status(vin)
        return endpoint_result.result
    
    async def get_air_conditioning(self, vin: str) -> AirConditioning:
        """Get the actual vehicle status and return the parsed Pydantic model."""
        endpoint_result = await self.rest_api.get_air_conditioning(vin)
        return endpoint_result.result
    
    async def get_parking_positions(self, vin: str) -> ParkingPosition:
        """Get the actual vehicle status and return the parsed Pydantic model."""
        endpoint_result = await self.rest_api.get_parking_positions(vin)
        return endpoint_result.result
    
    async def get_auxiliary_heating(self, vin: str) -> AuxiliaryHeating:
        """Get the actual vehicle status and return the parsed Pydantic model."""
        endpoint_result = await self.rest_api.get_auxiliary_heating(vin)
        return endpoint_result.result
    
    async def get_odometer(self, vin: str) -> Odometer:
        """Get the actual vehicle status and return the parsed Pydantic model."""
        endpoint_result = await self.rest_api.get_odometer(vin)
        return endpoint_result.result
    
    async def get_charging(self, vin: str) -> Charging:
        """Get the actual vehicle status and return the parsed Pydantic model."""
        endpoint_result = await self.rest_api.get_charging(vin)
        return endpoint_result.result
    
    async def get_active_ventilation(self, vin: str) -> ActiveVentilation:
        """Get the actual vehicle status and return the parsed Pydantic model."""
        endpoint_result = await self.rest_api.get_active_ventilation(vin)
        return endpoint_result.result
    
    async def start_air_conditioning(self, vin: str, temperature: float) -> None:
        """Starts the air conditioning for the vehicle with the given VIN."""
        payload = {"targetTemperature": temperature}
        await self.rest_api.start_air_conditioning(vin, payload=payload)
    
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

    async def start_charging(self, vin: str) -> None:
        """Starts the charging process for the vehicle with the given VIN."""
        await self.rest_api.start_charging(vin)

    async def stop_charging(self, vin: str) -> None:
        """Stops the charging process for the vehicle with the given VIN."""
        await self.rest_api.stop_charging(vin)

    async def connect(self):
        """TODO: Implementation of connect mechanism."""
        pass
    
    async def disconnect(self) -> None:
        """TODO: Implementation of disconnect mechanism."""
        pass
    
    async def verify_spin(self, spin: str) -> bool:
        """TODO: Implementation of SPIN verification."""
        pass

    """
    ======= NOT IMPLEMENTED FUNCTIONS - CAN BE USED SOMETIME IN THE FUTURE =======
    """
    async def refresh_auxiliary_heating(self, vin: str) -> None:
        """Refreshes the auxiliary heating status of the vehicle with the given VIN."""
        pass

    async def set_reduced_current_limit(self, vin: str) -> None:
        """Sets the charging current limit (e.g., to REDUCED or MAXIMUM) for the vehicle with the given VIN."""
        pass

    async def set_seats_heating(self, vin: str) -> None:
        """Configures the seats heating settings for the vehicle with the given VIN."""
        pass

    async def start_window_heating(self, vin: str) -> None:
        """Starts the electric window heating for the vehicle with the given VIN."""
        pass

    async def stop_window_heating(self, vin: str) -> None:
        """Stops the window heating of the vehicle and return None if it was succesfull else catch an exception in HomeAssistant."""
        pass

    async def set_windows_heating(self, vin: str) -> None:
        """Configures the front and rear windows heating settings for the vehicle with the given VIN."""
        pass

    async def set_auto_unlock_plug(self, vin: str) -> None:
        """Sets the automatic unlocking behavior of the charging plug (e.g., PERMANENT or OFF) for the vehicle with the given VIN."""
        pass
    async def set_charge_limit(self, vin: str, limit: int) -> None:
        """Sets the maximum charging limit in percent for the vehicle with the given VIN."""
        pass

    async def set_target_temperature(self, vin: str, temperature: float) -> None:
        """Sets the target temperature for AC or auxiliary heating for the vehicle with the given VIN."""
        pass
    # TODO: Add more methods for other endpoints as needed
