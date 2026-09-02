from datetime import datetime
from typing import List, Optional
from pydantic import Field

from .base_model import BaseModel

from .vehicle_status import VehicleStatus
from .common import VehicleError
from .parking_position import ParkingPosition
from .auxiliary_heating import AuxiliaryHeating
from .active_ventilation import ActiveVentilation
from .charging import Charging
from .driving_range import FuelStatus
from .air_conditioning import AirConditioning
from .charging_profiles import ChargingProfiles

class Odometer(BaseModel):
    """Odometer of the vehicle."""
    mileage_in_km: int
    car_captured_timestamp: Optional[str]

class VehicleObject(BaseModel):
    """Pack whole vehicle object into one object for the vehicle."""
    name: Optional[str] = None
    vin: str
    license_plate: Optional[str] = None
    render_url: Optional[str] = None
    odometer: Optional[Odometer] = None
    status: Optional[VehicleStatus] = None
    parking_position: Optional[ParkingPosition] = None 
    auxiliary_heating: Optional[AuxiliaryHeating] = None
    active_ventilation: Optional[ActiveVentilation] = None
    air_conditioning: Optional[AirConditioning] = None
    fuel_status: Optional[FuelStatus] = None
    charging: Optional[Charging] = None
    charging_profiles: Optional[ChargingProfiles] = None

class VehicleResponse(BaseModel):
    """Response object for vehicle data."""
    vehicle: VehicleObject
    errors: List[VehicleError] = Field(default_factory=list)

   