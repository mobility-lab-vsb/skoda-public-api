import logging
from typing import Any, Optional, List
from aiohttp import ClientSession
from .const import BETA_URL
from .rest_api import PostEndpointResult, SkodaRestAPI
from ..models.vehicle import VehicleResponse, Odometer
from ..models.vehicle_status import VehicleStatus
from ..models.active_ventilation import ActiveVentilation
from ..models.air_conditioning import AirConditioning
from ..models.parking_position import ParkingPosition
from ..models.auxiliary_heating import AuxiliaryHeating
from ..models.charging import Charging
from ..models.driving_range import FuelStatus
from ..models.charging_profiles import ChargingProfiles
from ..models.configurations import StartAirConditioningConfiguration, StartAuxiliaryHeatingConfiguration, ConfigurationTargetTemperature

class OpenAPIClient:
    """Client for interacting with rest API and used in HomeAssistant."""

    def __init__(self, api_key: str, session: ClientSession, base_url: str = BETA_URL) -> None:
       self.rest_api = SkodaRestAPI(api_key=api_key, session=session, base_url=base_url)
       self.last_headers: dict[str, Any] = {}

    @property
    def api_key_expires_at(self) -> Optional[str]:
        """Return the expiration timestamp of the API key."""
        return self.last_headers.get("x-api-key-expires-at")

    @property
    def rate_limit_remaining(self) -> Optional[int]:
        """Return remaining requests quota."""
        val = self.last_headers.get("ratelimit-remaining")
        return int(val) if val is not None else None

    @property
    def rate_limit_reset(self) -> Optional[int]:
        """Return the time when the rate limit will be reset."""
        val = self.last_headers.get("ratelimit-reset")
        return int(val) if val is not None else None

    async def get_vehicle(self, vin: str, include: Optional[List[str]] = None) -> VehicleResponse:
        """Get the actual vehicle data and return the parsed Pydantic model."""
        endpoint_result = await self.rest_api.get_vehicle(vin, include=include)
        self.last_headers = endpoint_result.headers
        return endpoint_result.result
    
    async def get_vehicle_status(self, vin: str) -> Optional[VehicleStatus]:
        endpoint_result = await self.rest_api.get_vehicle_status(vin)
        self.last_headers = endpoint_result.headers
        return endpoint_result.result
    
    async def get_air_conditioning(self, vin: str) -> AirConditioning:
        """Get the actual vehicle status and return the parsed Pydantic model."""
        endpoint_result = await self.rest_api.get_air_conditioning(vin)
        self.last_headers = endpoint_result.headers
        return endpoint_result.result
    
    async def get_parking_positions(self, vin: str) -> ParkingPosition:
        """Get the actual vehicle status and return the parsed Pydantic model."""
        endpoint_result = await self.rest_api.get_parking_positions(vin)
        self.last_headers = endpoint_result.headers
        return endpoint_result.result
    
    async def get_auxiliary_heating(self, vin: str) -> AuxiliaryHeating:
        """Get the actual vehicle status and return the parsed Pydantic model."""
        endpoint_result = await self.rest_api.get_auxiliary_heating(vin)
        self.last_headers = endpoint_result.headers
        return endpoint_result.result
    
    async def get_odometer(self, vin: str) -> Odometer:
        """Get the actual vehicle status and return the parsed Pydantic model."""
        endpoint_result = await self.rest_api.get_odometer(vin)
        self.last_headers = endpoint_result.headers
        return endpoint_result.result
    
    async def get_charging(self, vin: str) -> Charging:
        """Get the actual vehicle status and return the parsed Pydantic model."""
        endpoint_result = await self.rest_api.get_charging(vin)
        self.last_headers = endpoint_result.headers
        return endpoint_result.result
    
    async def get_active_ventilation(self, vin: str) -> ActiveVentilation:
        """Get the actual active ventilation and return the parsed Pydantic model."""
        endpoint_result = await self.rest_api.get_active_ventilation(vin)
        self.last_headers = endpoint_result.headers
        return endpoint_result.result

    async def get_fuel_status(self, vin: str) -> FuelStatus:
        """Get the actual fuel status and return the parsed Pydantic model."""
        endpoint_result = await self.rest_api.get_fuel_status(vin)
        self.last_headers = endpoint_result.headers
        return endpoint_result.result

    async def get_charging_profiles(self, vin: str) -> ChargingProfiles:
        """Get the actual charging profiles and return the parsed Pydantic model."""
        endpoint_result = await self.rest_api.get_charging_profiles(vin)
        self.last_headers = endpoint_result.headers
        return endpoint_result.result
    
    
    async def start_air_conditioning(self, vin: str, temperature: float, unit: str = "CELSIUS", without_external_power: bool = True) -> PostEndpointResult:
        """Starts the air conditioning for the vehicle with the given VIN."""
        config = StartAirConditioningConfiguration(
            target_temperature=ConfigurationTargetTemperature(
                value=temperature,
                unit=unit,
            ),
            air_conditioning_without_external_power=without_external_power,
        )
        return await self.rest_api.start_air_conditioning(vin, config)
    
    async def stop_air_conditioning(self, vin: str) -> PostEndpointResult:
        """Stops the air_conditioning of the vehicle and return None if it was succesfull else catch an exception in HomeAssistant"""
        return await self.rest_api.stop_air_conditioning(vin)

    async def start_auxiliary_heating(self, vin: str, spin: str, duration_in_seconds: int = 120, start_mode: str = "HEATING", target_temperature: Optional[float] = None, unit: str = "CELSIUS") -> PostEndpointResult:
        """Starts the auxiliary heating for the vehicle with the given VIN."""
        temp_obj = None
        if target_temperature is not None:
            temp_obj = ConfigurationTargetTemperature(
                value=target_temperature,
                unit=unit,
            )

        config = StartAuxiliaryHeatingConfiguration(
            spin=spin,
            duration_in_seconds=duration_in_seconds,
            start_mode=start_mode,
            target_temperature=temp_obj,
        )
        return await self.rest_api.start_auxiliary_heating(vin, config)

    async def stop_auxiliary_heating(self, vin: str) -> PostEndpointResult:
        """Stops the auxiliary_heating of the vehicle and return None if it was succesfull else catch an exception in HomeAssistant"""
        return await self.rest_api.stop_auxiliary_heating(vin)
    
    async def start_active_ventilation(self, vin: str) -> PostEndpointResult:
        """Starts the active_ventilation for the vehicle with the given VIN."""
        return await self.rest_api.start_active_ventilation(vin)

    async def stop_active_ventilation(self, vin: str) -> PostEndpointResult:
        """Stops the active_ventilation of the vehicle and return None if it was succesfull else catch an exception in HomeAssistant"""
        return await self.rest_api.stop_active_ventilation(vin)

    async def start_charging(self, vin: str) -> PostEndpointResult:
        """Starts the charging process for the vehicle with the given VIN."""
        return await self.rest_api.start_charging(vin)

    async def stop_charging(self, vin: str) -> PostEndpointResult:
        """Stops the charging process for the vehicle with the given VIN."""
        return await self.rest_api.stop_charging(vin)

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
