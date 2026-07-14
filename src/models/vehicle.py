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
from .driving_range import DrivingRange
from .air_conditioning import AirConditioning

class Odometer(BaseModel):
    """Odometer of the vehicle."""
    mileage_in_km: int
    car_captured_timestamp: str

class VehicleObject(BaseModel):
    """Pack whole vehicle object into one object for the vehicle."""
    name: str
    vin: str
    license_plate: str
    render_url: Optional[str] = None
    odometer: Optional[Odometer] = None
    status: Optional[VehicleStatus] = None
    parking_position: Optional[ParkingPosition] = None 
    auxiliary_heating: Optional[AuxiliaryHeating] = None
    active_ventilation: Optional[ActiveVentilation] = None
    air_conditioning: Optional[AirConditioning] = None
    driving_range: Optional[DrivingRange] = None
    charging: Optional[Charging] = None

class VehicleResponse(BaseModel):
    """Response object for vehicle data."""
    vehicle: VehicleObject
    errors: List[VehicleError] = Field(default_factory=list)

   